import pytest

from fastdoctor.analyzer import postgres_inspector
from fastdoctor.analyzer.postgres_inspector import (
    PostgresInspectionError,
    PostgresColumnInfo,
    inspect_postgres_table,
    postgres_column_to_node,
)
from fastdoctor.analyzer.three_layer_mapping import map_three_layers
from fastdoctor.database import DatabaseConfig, MAX_CONNECT_TIMEOUT
from fastdoctor.evidence import IncidentEvidence
from fastdoctor.invariants.base import ContractNode
from fastdoctor.invariants.engine import InvariantEngine
from fastdoctor.runtime.failure_capture import capture_runtime_failure


class FakeCursor:
    def __init__(self, rows, connection):
        self.rows = rows
        self.connection = connection
        self.query = None
        self.parameters = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, parameters):
        self.connection.events.append(("query", query))
        self.query = query
        self.parameters = parameters

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows):
        self.rows = rows
        self.statements = []
        self.events = []
        self.fake_cursor = FakeCursor(rows, self)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, statement):
        self.statements.append(statement)
        self.events.append(("statement", statement))

    def cursor(self):
        return self.fake_cursor


def config(**overrides):
    values = {
        "host": "db.example.test",
        "port": 5544,
        "database": "fastdoctor_test",
        "user": "inspector",
        "password": "test-password",
        "schema": "app",
        "connect_timeout": 7,
    }
    values.update(overrides)
    return DatabaseConfig(**values)


def column_row(schema="app", table="orders"):
    return (schema, table, "id", "character varying", "NO", "varchar")


def test_postgres_column_to_node():

    column = PostgresColumnInfo(
        table_name="orders",
        column_name="id",
        data_type="character varying",
        is_nullable=False,
    )

    node = postgres_column_to_node(column)

    assert node.id == "postgres:orders.id"
    assert node.layer == "postgres"
    assert node.semantic_type == "STRING"

    assert node.metadata["table_name"] == "orders"
    assert node.metadata["column_name"] == "id"
    assert node.metadata["raw_type"] == "character varying"
    assert node.metadata["nullable"] is False


def test_inspector_passes_explicit_connection_configuration(monkeypatch):
    connection = FakeConnection([column_row()])
    received = {}

    def connect(**kwargs):
        received.update(kwargs)
        return connection

    monkeypatch.setattr(postgres_inspector.psycopg, "connect", connect)

    nodes = inspect_postgres_table("orders", database_config=config())

    assert received == {
        "host": "db.example.test",
        "port": 5544,
        "dbname": "fastdoctor_test",
        "user": "inspector",
        "password": "test-password",
        "connect_timeout": 7,
    }
    assert nodes[0].semantic_type == "STRING"


def test_database_config_bounds_timeout_and_does_not_show_password(monkeypatch):
    monkeypatch.setenv("PGHOST", "db.internal")
    monkeypatch.setenv("PGPORT", "5433")
    monkeypatch.setenv("PGDATABASE", "appdb")
    monkeypatch.setenv("PGUSER", "appuser")
    monkeypatch.setenv("PGPASSWORD", "test-password")
    monkeypatch.setenv("PGSCHEMA", "app")
    monkeypatch.setenv("PGCONNECT_TIMEOUT", "999")

    database_config = DatabaseConfig.from_env()

    assert database_config.host == "db.internal"
    assert database_config.port == 5433
    assert database_config.database == "appdb"
    assert database_config.user == "appuser"
    assert database_config.password == "test-password"
    assert database_config.schema == "app"
    assert database_config.connect_timeout == MAX_CONNECT_TIMEOUT
    assert "test-password" not in repr(database_config)


def test_inspector_passes_requested_schema_and_table_as_parameters(monkeypatch):
    connection = FakeConnection([column_row()])
    monkeypatch.setattr(
        postgres_inspector.psycopg,
        "connect",
        lambda **_: connection,
    )

    inspect_postgres_table("orders", "app", database_config=config())

    query = connection.fake_cursor.query
    assert "table_schema = %s" in query
    assert "table_name = %s" in query
    assert connection.fake_cursor.parameters == ("app", "orders")


def test_inspector_uses_read_only_transaction(monkeypatch):
    connection = FakeConnection([column_row()])
    monkeypatch.setattr(
        postgres_inspector.psycopg,
        "connect",
        lambda **_: connection,
    )

    inspect_postgres_table("orders", "app", database_config=config())

    assert connection.events == [
        ("statement", "SET TRANSACTION READ ONLY"),
        ("query", connection.fake_cursor.query),
    ]


def test_inspector_redacts_database_driver_errors(monkeypatch):
    secret_error = "could not connect using password=test-password host=db.internal"

    def connect(**_):
        raise postgres_inspector.psycopg.OperationalError(secret_error)

    monkeypatch.setattr(postgres_inspector.psycopg, "connect", connect)

    with pytest.raises(PostgresInspectionError) as raised:
        inspect_postgres_table("orders", "app", database_config=config())

    assert "database details were redacted" in str(raised.value)
    assert "test-password" not in str(raised.value)
    assert "db.internal" not in str(raised.value)

    runtime_failure = capture_runtime_failure(
        raised.value,
        endpoint="/inspect",
        method="GET",
    )
    incident = IncidentEvidence(
        incident_id="INC-TEST",
        runtime_failure=runtime_failure,
    )
    serialized_message = incident.to_dict()["runtime_failure"]["message"]
    assert "test-password" not in serialized_message
    assert "db.internal" not in serialized_message


def test_inspector_redacts_database_query_errors(monkeypatch):
    connection = FakeConnection([column_row()])

    def fail_query(*_):
        raise postgres_inspector.psycopg.OperationalError(
            "query failed with password=test-password"
        )

    connection.fake_cursor.execute = fail_query
    monkeypatch.setattr(
        postgres_inspector.psycopg,
        "connect",
        lambda **_: connection,
    )

    with pytest.raises(PostgresInspectionError) as raised:
        inspect_postgres_table("orders", "app", database_config=config())

    assert "test-password" not in str(raised.value)
    assert "database details were redacted" in str(raised.value)


def test_inspector_requires_schema_when_configuration_has_none(monkeypatch):
    def unexpected_connect(**_):
        pytest.fail("connection must not be opened without a schema")

    monkeypatch.setattr(postgres_inspector.psycopg, "connect", unexpected_connect)

    with pytest.raises(PostgresInspectionError, match="schema must be specified"):
        inspect_postgres_table("orders", database_config=config(schema=None))


def test_inspector_returns_no_nodes_for_missing_table(monkeypatch):
    connection = FakeConnection([])
    monkeypatch.setattr(
        postgres_inspector.psycopg,
        "connect",
        lambda **_: connection,
    )

    postgres_nodes = inspect_postgres_table(
        "missing", "app", database_config=config()
    )
    assert postgres_nodes == []

    pydantic = ContractNode(
        id="pydantic:OrderResponse.id",
        layer="pydantic",
        name="OrderResponse.id",
        semantic_type="STRING",
        metadata={"nullable": False},
    )
    sqlalchemy = ContractNode(
        id="sqlalchemy:Order.id",
        layer="sqlalchemy",
        name="Order.id",
        semantic_type="STRING",
        metadata={"nullable": False},
    )
    mappings = map_three_layers([pydantic], [sqlalchemy], postgres_nodes)

    assert [
        result.status for result in InvariantEngine().check(mappings[0])
    ] == ["UNVERIFIED", "UNVERIFIED"]
