from fastdoctor.invariants.base import (
    ContractNode,
    ThreeLayerMapping,
)

def calculate_mapping_confidence(
    pydantic_field: str,
    sqlalchemy_field: str,
    postgres_field: str,
) -> tuple[str, str]:

    fields = [
        pydantic_field,
        sqlalchemy_field,
        postgres_field,
    ]

    if all(field == fields[0] for field in fields):
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
                pydantic_field,
                sqlalchemy_match.name.split(".")[-1],
                postgres_match.name.split(".")[-1],
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
                ],
                confidence=confidence,
            )
        )
        
    return mappings