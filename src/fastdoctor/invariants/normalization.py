TYPE_ALIASES = {
    "uuid": "UUID",
    "UUID": "UUID",
    "uuid.UUID": "UUID",
    "UUID(as_uuid=True)": "UUID",

    "str": "STRING",
    "String": "VARCHAR",
    "VARCHAR": "VARCHAR",

    "int": "INTEGER",
    "Integer": "INTEGER",
    "INTEGER": "INTEGER",
}


def normalize_type(raw_type: str) -> str:
    return TYPE_ALIASES.get(raw_type, "UNKNOWN")