TYPE_ALIASES = {
    # UUID
    "uuid": "UUID",
    "UUID": "UUID",
    "uuid.UUID": "UUID",
    "UUID(as_uuid=True)": "UUID",

    # String
    "str": "STRING",
    "STRING": "STRING",
    "String": "STRING",
    "VARCHAR": "STRING",
    "varchar": "STRING",
    "character varying": "STRING",
    "text": "STRING",
    "TEXT": "STRING",

    # Integer
    "int": "INTEGER",
    "Integer": "INTEGER",
    "INTEGER": "INTEGER",
    "integer": "INTEGER",
    "bigint": "INTEGER",

    # Float
    "float": "FLOAT",
    "Float": "FLOAT",
    "FLOAT": "FLOAT",

    # Boolean
    "bool": "BOOLEAN",
    "Boolean": "BOOLEAN",
    "BOOLEAN": "BOOLEAN",
    "boolean": "BOOLEAN",
}


def normalize_type(raw_type: str) -> str:
    return TYPE_ALIASES.get(raw_type, "UNKNOWN")