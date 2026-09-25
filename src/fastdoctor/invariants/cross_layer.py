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

    observed = {
        mapping.pydantic.id: normalize_type(
            mapping.pydantic.semantic_type
        ),
        mapping.sqlalchemy.id: normalize_type(
            mapping.sqlalchemy.semantic_type
        ),
        mapping.postgres.id: normalize_type(
            mapping.postgres.semantic_type
        ),
    }

    unique_types = set(observed.values())

    passed = len(unique_types) == 1

    failures = []

    if not passed:
        failures.append(
            (
                "Semantic type mismatch across three layers "
                f"for field '{mapping.field_name}'"
            )
        )

    expected = (
        next(iter(unique_types))
        if len(unique_types) == 1
        else None
    )

    evidence = [
        *mapping.evidence,
        f"field:{mapping.field_name}",
    ]

    return InvariantResult(
        invariant_id="I-001",
        name="Three-layer semantic type consistency",
        passed=passed,
        expected=expected,
        observed=observed,
        failures=failures,
        evidence=evidence,
    )