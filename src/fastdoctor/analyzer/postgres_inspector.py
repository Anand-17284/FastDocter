import psycopg
from dataclasses import dataclass

from fastdoctor.analyzer.postgres import POSTGRES_TYPE_MAP
from fastdoctor.database import DatabaseConfig
from fastdoctor.invariants.base import ContractNode


class PostgresInspectionError(RuntimeError):
    """Safe-to-report error raised when PostgreSQL inspection fails."""

@dataclass
class PostgresColumnInfo:
    table_name: str
    column_name: str
    data_type: str
    is_nullable: bool
    udt_name: str | None = None

def postgres_column_to_node(
    column: PostgresColumnInfo,
) -> ContractNode:

    semantic_type = POSTGRES_TYPE_MAP.get(
        column.data_type.lower(),
    )

    if semantic_type is None and column.udt_name:
        semantic_type = POSTGRES_TYPE_MAP.get(
            column.udt_name.lower(),
            "UNKNOWN",
        )

    if semantic_type is None:
        semantic_type = "UNKNOWN"

    return ContractNode(
        id=f"postgres:{column.table_name}.{column.column_name}",
        layer="postgres",
        name=f"{column.table_name}.{column.column_name}",
        semantic_type=semantic_type,
        metadata={
            "table_name": column.table_name,
            "column_name": column.column_name,
            "raw_type": column.data_type,
            "udt_name": column.udt_name,
            "nullable": column.is_nullable,
        },
    )

def inspect_postgres_table(
    table_name: str,
    schema_name: str | None = None,
    *,
    database_config: DatabaseConfig | None = None,
) -> list[ContractNode]:
    config = database_config or DatabaseConfig.from_env()
    selected_schema = schema_name if schema_name is not None else config.schema
    if not selected_schema:
        raise PostgresInspectionError(
            "PostgreSQL schema must be specified with schema_name or PGSCHEMA"
        )

    try:
        with psycopg.connect(**config.psycopg_kwargs()) as connection:
            with connection.cursor() as cursor:
                # This is the first statement in the transaction, so the
                # server enforces that the inspection transaction is read-only.
                connection.execute("SET TRANSACTION READ ONLY")
                cursor.execute(
                    """
                    SELECT
                        table_schema,
                        table_name,
                        column_name,
                        data_type,
                        is_nullable,
                        udt_name
                    FROM information_schema.columns
                    WHERE table_schema = %s
                      AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (selected_schema, table_name),
                )
                rows = cursor.fetchall()
    except psycopg.Error:
        raise PostgresInspectionError(
            "PostgreSQL inspection failed; database details were redacted"
        ) from None

    if not rows:
        # An empty layer is retained as missing evidence so the mapping and
        # invariant layers can report UNVERIFIED instead of aborting analysis.
        return []

    nodes: list[ContractNode] = []
    for row in rows:
        column = PostgresColumnInfo(
            table_name=row[1],
            column_name=row[2],
            data_type=row[3],
            is_nullable=row[4] == "YES",
            udt_name=row[5],
        )
        nodes.append(postgres_column_to_node(column))

    return nodes
