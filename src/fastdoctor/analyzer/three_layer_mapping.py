from fastdoctor.invariants.base import (
    ContractNode,
    ThreeLayerMapping,
)

def calculate_mapping_confidence(
    pydantic_node: ContractNode,
    sqlalchemy_node: ContractNode,
    postgres_node: ContractNode,
) -> tuple[str, str]:

    pydantic_field = pydantic_node.name.split(".")[-1]
    sqlalchemy_field = sqlalchemy_node.name.split(".")[-1]
    postgres_field = postgres_node.name.split(".")[-1]

    name_match = (
        pydantic_field == sqlalchemy_field == postgres_field
    )

    sqlalchemy_table = sqlalchemy_node.metadata.get(
        "table_name"
    )

    postgres_table = postgres_node.metadata.get(
        "table_name"
    )

    table_match = (
        sqlalchemy_table is not None
        and postgres_table is not None
        and sqlalchemy_table == postgres_table
    )

    primary_key = sqlalchemy_node.metadata.get(
        "primary_key",
        False,
    )

    if name_match and table_match and primary_key:
        return (
            "HIGH",
            "Field names, database table, and primary-key evidence match",
        )

    if name_match and table_match:
        return (
            "HIGH",
            "Field names and database table evidence match",
        )

    if name_match:
        return (
            "MEDIUM",
            "All three field names match",
        )

    if (
        pydantic_field == sqlalchemy_field
        or sqlalchemy_field == postgres_field
        or pydantic_field == postgres_field
    ):
        return (
            "LOW",
            "Only two layers have matching field names",
        )

    return (
        "UNKNOWN",
        "No field-name relationship established",
    )

def map_three_layers(
    pydantic_nodes: list[ContractNode],
    sqlalchemy_nodes: list[ContractNode],
    postgres_nodes: list[ContractNode],
) -> list[ThreeLayerMapping]:

    mappings = []

    for pydantic_node in pydantic_nodes:

        pydantic_field = pydantic_node.name.split(".")[-1]

        sqlalchemy_match = next(
            (
                node
                for node in sqlalchemy_nodes
                if node.name.split(".")[-1] == pydantic_field
            ),
            None,
        )

        postgres_match = next(
            (
                node
                for node in postgres_nodes
                if node.name.split(".")[-1] == pydantic_field
            ),
            None,
        )

        if sqlalchemy_match is None:
            continue

        if postgres_match is None:
            continue

        confidence, confidence_reason = (
            calculate_mapping_confidence(
                pydantic_node,
                sqlalchemy_match,
                postgres_match,
            )
        )

        mappings.append(
            ThreeLayerMapping(
                field_name=pydantic_field,
                pydantic=pydantic_node,
                sqlalchemy=sqlalchemy_match,
                postgres=postgres_match,
                relationship=confidence_reason,
                evidence=[
                    f"Pydantic field: {pydantic_node.id}",
                    f"SQLAlchemy field: {sqlalchemy_match.id}",
                    f"PostgreSQL column: {postgres_match.id}",
                    f"Mapping reason: {confidence_reason}",
                    f"Field name matches across all layers: {pydantic_field == sqlalchemy_match.name.split('.')[-1] == postgres_match.name.split('.')[-1]}",
                    f"SQLAlchemy table: {sqlalchemy_match.metadata.get('table_name', 'UNKNOWN')}",
                    f"PostgreSQL table: {postgres_match.metadata.get('table_name', 'UNKNOWN')}",
                    f"SQLAlchemy primary key: {sqlalchemy_match.metadata.get('primary_key', False)}",
                    f"PostgreSQL column: {postgres_match.metadata.get('column_name', postgres_match.name.split('.')[-1])}",
                ],
                confidence=confidence,
            )
        )
        
    return mappings