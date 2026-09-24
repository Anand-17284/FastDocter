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