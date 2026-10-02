from fastdoctor.invariants.base import ContractNode
from fastdoctor.invariants.normalization import normalize_type

POSTGRES_TYPE_MAP = {
    # UUID
    "uuid": "UUID",

    # String
    "character varying": "STRING",
    "varchar": "STRING",
    "text": "STRING",
    "char": "STRING",
    "bpchar": "STRING",

    # Integer
    "smallint": "INTEGER",
    "int2": "INTEGER",
    "integer": "INTEGER",
    "int4": "INTEGER",
    "bigint": "INTEGER",
    "int8": "INTEGER",
    "serial": "INTEGER",
    "bigserial": "INTEGER",

    # Floating point
    "real": "FLOAT",
    "float4": "FLOAT",
    "double precision": "FLOAT",
    "float8": "FLOAT",

    # Boolean
    "boolean": "BOOLEAN",
    "bool": "BOOLEAN",
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