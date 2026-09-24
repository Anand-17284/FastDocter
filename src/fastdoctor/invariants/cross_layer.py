from fastdoctor.invariants.base import (
    FieldMapping,
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