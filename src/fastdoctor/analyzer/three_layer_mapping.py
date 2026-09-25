from fastdoctor.invariants.base import (
    ContractNode,
    ThreeLayerMapping,
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

        mappings.append(
            ThreeLayerMapping(
                field_name=pydantic_field,
                pydantic=pydantic_node,
                sqlalchemy=sqlalchemy_match,
                postgres=postgres_match,
                evidence=[
                    f"Pydantic field: {pydantic_node.id}",
                    f"SQLAlchemy field: {sqlalchemy_match.id}",
                    f"PostgreSQL column: {postgres_match.id}",
                ],
                confidence="MEDIUM",
            )
        )

    return mappings