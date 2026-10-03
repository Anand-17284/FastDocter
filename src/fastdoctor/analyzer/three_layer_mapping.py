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

    nodes_by_layer = {
        "pydantic": pydantic_nodes,
        "sqlalchemy": sqlalchemy_nodes,
        "postgres": postgres_nodes,
    }
    candidates_by_field: dict[str, dict[str, list[ContractNode]]] = {}

    # Preserve Pydantic field order, then append database-only fields in
    # their input order so missing contracts are still represented.
    for layer, nodes in nodes_by_layer.items():
        for node in nodes:
            field_name = node.name.split(".")[-1]
            field_candidates = candidates_by_field.setdefault(
                field_name,
                {name: [] for name in nodes_by_layer},
            )
            field_candidates[layer].append(node)

    mappings = []

    for field_name, field_candidates in candidates_by_field.items():
        selected = {
            layer: candidates[0] if len(candidates) == 1 else None
            for layer, candidates in field_candidates.items()
        }
        missing_layers = [
            layer
            for layer, candidates in field_candidates.items()
            if not candidates
        ]
        ambiguous_layers = [
            layer
            for layer, candidates in field_candidates.items()
            if len(candidates) > 1
        ]
        candidate_ids = {
            layer: [node.id for node in candidates]
            for layer, candidates in field_candidates.items()
        }

        evidence = [
            f"{layer} candidates for '{field_name}': "
            f"{', '.join(ids) if ids else 'none'}"
            for layer, ids in candidate_ids.items()
        ]
        evidence.extend(
            f"Field '{field_name}' is missing from {layer}"
            for layer in missing_layers
        )
        evidence.extend(
            f"Field '{field_name}' is ambiguous in {layer}: "
            f"{', '.join(candidate_ids[layer])}"
            for layer in ambiguous_layers
        )

        confidence = "UNKNOWN"
        relationship = "Insufficient evidence to establish a unique mapping"
        if not missing_layers and not ambiguous_layers:
            pydantic_node = selected["pydantic"]
            sqlalchemy_node = selected["sqlalchemy"]
            postgres_node = selected["postgres"]
            # All nodes are selected when each layer has exactly one candidate.
            assert pydantic_node is not None
            assert sqlalchemy_node is not None
            assert postgres_node is not None
            confidence, relationship = calculate_mapping_confidence(
                pydantic_node,
                sqlalchemy_node,
                postgres_node,
            )
            evidence.extend([
                f"Pydantic field: {pydantic_node.id}",
                f"SQLAlchemy field: {sqlalchemy_node.id}",
                f"PostgreSQL column: {postgres_node.id}",
                f"Mapping reason: {relationship}",
                f"SQLAlchemy table: {sqlalchemy_node.metadata.get('table_name', 'UNKNOWN')}",
                f"PostgreSQL table: {postgres_node.metadata.get('table_name', 'UNKNOWN')}",
                f"SQLAlchemy primary key: {sqlalchemy_node.metadata.get('primary_key', False)}",
            ])

        mappings.append(
            ThreeLayerMapping(
                field_name=field_name,
                pydantic=selected["pydantic"],
                sqlalchemy=selected["sqlalchemy"],
                postgres=selected["postgres"],
                relationship=relationship,
                evidence=evidence,
                confidence=confidence,
                missing_layers=missing_layers,
                ambiguous_layers=ambiguous_layers,
                candidate_ids=candidate_ids,
            )
        )

    return mappings
