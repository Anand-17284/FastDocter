from fastdoctor.invariants.base import ContractNode, FieldMapping


def discover_field_mappings(
    source_nodes: list[ContractNode],
    target_nodes: list[ContractNode],
    relationship: str,
) -> list[FieldMapping]:

    mappings = []

    for source_node in source_nodes:

        source_field = source_node.name.split(".")[-1]

        for target_node in target_nodes:

            target_field = target_node.name.split(".")[-1]

            if source_field != target_field:
                continue

            mappings.append(
                FieldMapping(
                    source=source_node,
                    target=target_node,
                    relationship=relationship,
                    evidence=[
                        (
                            f"Field name '{source_field}' "
                            f"matches '{target_field}'"
                        )
                    ],
                    confidence="MEDIUM",
                )
            )

    return mappings