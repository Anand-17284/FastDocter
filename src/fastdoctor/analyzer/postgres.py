from fastdoctor.invariants.base import ContractNode
from fastdoctor.invariants.normalization import normalize_type


POSTGRES_TYPE_MAP = {
    "uuid": "UUID",
    "character varying": "VARCHAR",
    "varchar": "VARCHAR",
    "text": "STRING",
    "integer": "INTEGER",
    "bigint": "INTEGER",
}


def analyze_postgres_column(
    table_name: str,
    column_name: str,
    postgres_type: str,
    nullable: bool,
) -> ContractNode:

    normalized_type = POSTGRES_TYPE_MAP.get(
        postgres_type.lower(),
        "UNKNOWN",
    )

    return ContractNode(
        id=f"postgres:{table_name}.{column_name}",
        layer="postgres",
        name=f"{table_name}.{column_name}",
        semantic_type=normalized_type,
        metadata={
            "nullable": nullable,
            "raw_type": postgres_type,
        },
    )