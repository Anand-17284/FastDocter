from fastdoctor.invariants.normalization import normalize_type

from fastdoctor.invariants.base import (
    FieldMapping,
    InvariantResult,
)

from fastdoctor.invariants.base import (
    ThreeLayerMapping,
    InvariantResult,
)

def check_mapped_field_type(
        
    mapping: FieldMapping,
) -> InvariantResult:

    source_type = mapping.source.semantic_type
    target_type = mapping.target.semantic_type

    passed = source_type == target_type

    failures = []

    if not passed:
        failures.append(
            f"Type mismatch: "
            f"{mapping.source.name}={source_type} "
            f"but "
            f"{mapping.target.name}={target_type}"
        )

    evidence = [
        mapping.source.id,
        mapping.target.id,
        mapping.relationship,
        *mapping.evidence,
    ]

    return InvariantResult(
        invariant_id="I-001",
        name="Mapped field semantic type consistency",
        passed=passed,
        expected=source_type,
        observed={
            mapping.source.id: source_type,
            mapping.target.id: target_type,
        },
        failures=failures,
        evidence=evidence,
    )

def check_three_layer_mapping(
    mapping: ThreeLayerMapping,
) -> InvariantResult:

    nodes = [
        node
        for node in (mapping.pydantic, mapping.sqlalchemy, mapping.postgres)
        if node is not None
    ]
    observed = {
        node.id: normalize_type(node.semantic_type)
        for node in nodes
    }

    insufficient_mapping = bool(
        mapping.missing_layers or mapping.ambiguous_layers
    ) or len(nodes) != 3

    unique_types = set(observed.values())

    if insufficient_mapping or "UNKNOWN" in unique_types:
        passed = None
    else:
        passed = len(unique_types) == 1

    failures = []

    if passed is False:
        failures.append(
            (
                "Semantic type mismatch across three layers "
                f"for field '{mapping.field_name}'"
            )
        )

    elif passed is None:
        details = []
        if mapping.missing_layers:
            details.append(
                "missing layers: " + ", ".join(mapping.missing_layers)
            )
        if mapping.ambiguous_layers:
            details.append(
                "ambiguous layers: " + ", ".join(mapping.ambiguous_layers)
            )
        reason = "; ".join(details) or "at least one layer is UNKNOWN"
        failures.append(
            (
                "Semantic type could not be verified because of "
                f"{reason} for field "
                f"'{mapping.field_name}'"
            )
        )

    pydantic_node = mapping.pydantic
    expected = (
        normalize_type(pydantic_node.semantic_type)
        if pydantic_node is not None
        else None
    )

    violated_layers = []

    if passed is False and expected is not None:
        for node_id, semantic_type in observed.items():
            if semantic_type != expected:
                violated_layers.append(node_id)

    evidence = [*mapping.evidence, f"field:{mapping.field_name}"]

    return InvariantResult(
    invariant_id="I-001",
    name="Three-layer semantic type consistency",
    passed=passed,
    expected=expected,
    observed=observed,
    failures=failures,
    evidence=evidence,
    field_name=mapping.field_name,
    violated_layers=violated_layers,
)
