import psycopg
from dataclasses import dataclass

from fastdoctor.analyzer.postgres import POSTGRES_TYPE_MAP
from fastdoctor.invariants.base import ContractNode


@dataclass
class PostgresColumnInfo:
    table_name: str
    column_name: str
    data_type: str
    is_nullable: bool


def postgres_column_to_node(
    column: PostgresColumnInfo,
) -> ContractNode:

    semantic_type = POSTGRES_TYPE_MAP.get(
        column.data_type.lower(),
        "UNKNOWN",
    )

    return ContractNode(
        id=f"postgres:{column.table_name}.{column.column_name}",
        layer="postgres",
        name=f"{column.table_name}.{column.column_name}",
        semantic_type=semantic_type,
        metadata={
            "table_name": column.table_name,
            "column_name": column.column_name,
            "raw_type": column.data_type,
            "nullable": column.is_nullable,
        },
    )

def inspect_postgres_table(
    table_name: str,
) -> list[ContractNode]:

    with psycopg.connect() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    table_name,
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
                """,
                (table_name,),
            )

            rows = cursor.fetchall()

    nodes = []

    for row in rows:

        column = PostgresColumnInfo(
            table_name=row[0],
            column_name=row[1],
            data_type=row[2],
            is_nullable=row[3] == "YES",
        )

        nodes.append(
            postgres_column_to_node(column)
        )

    return nodes