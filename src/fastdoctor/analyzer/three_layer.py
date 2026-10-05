from fastdoctor.analyzer.pydantic import analyze_pydantic_model
from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model
from fastdoctor.analyzer.postgres_inspector import (
    PostgresInspectionError,
    inspect_postgres_table,
)
from fastdoctor.database import DatabaseConfig
from fastdoctor.invariants.base import ContractNode


def analyze_three_layers(
    pydantic_model,
    sqlalchemy_model,
    table_name: str,
    *,
    schema_name: str | None = None,
    database_config: DatabaseConfig | None = None,
) -> dict[str, list[ContractNode]]:

    pydantic_nodes = analyze_pydantic_model(
        pydantic_model
    )

    sqlalchemy_nodes = analyze_sqlalchemy_model(
        sqlalchemy_model
    )

    config = database_config or DatabaseConfig.from_env()
    selected_schema = schema_name if schema_name is not None else config.schema
    if not selected_schema:
        raise PostgresInspectionError(
            "PostgreSQL schema must be specified with schema_name or PGSCHEMA"
        )
    postgres_nodes = inspect_postgres_table(
        table_name,
        selected_schema,
        database_config=config,
    )

    return {
        "pydantic": pydantic_nodes,
        "sqlalchemy": sqlalchemy_nodes,
        "postgres": postgres_nodes,
    }
