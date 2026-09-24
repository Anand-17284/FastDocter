from fastdoctor.invariants.base import (
    ContractNode,
    FieldMapping,
)


def map_fields(
    pydantic_nodes: list[ContractNode],
    sqlalchemy_nodes: list[ContractNode],
) -> list[FieldMapping]:

    mappings = []

    for pydantic_node in pydantic_nodes:
        pydantic_field = pydantic_node.name.split(".")[-1]

        for sqlalchemy_node in sqlalchemy_nodes:
            sqlalchemy_field = sqlalchemy_node.name.split(".")[-1]

            if pydantic_field == sqlalchemy_field:

                mappings.append(
                    FieldMapping(
                        source=pydantic_node,
                        target=sqlalchemy_node,
                        relationship="field_name_match",
                        evidence=[
                            f"Field name '{pydantic_field}' matches"
                        ],
                        confidence="MEDIUM",
                    )
                )

    return mappings