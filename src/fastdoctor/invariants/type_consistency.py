from .base import ContractNode, InvariantResult
from .normalization import normalize_type


def check_semantic_type_consistency(
    nodes: list[ContractNode],
) -> InvariantResult:

    observed = {
        node.id: normalize_type(node.semantic_type)
        for node in nodes
    }

    unique_types = set(observed.values())

    passed = len(unique_types) == 1

    failures = []

    if not passed:
        failures.append(
            "Semantic type mismatch across layers"
        )

    expected = (
        next(iter(unique_types))
        if len(unique_types) == 1
        else None
    )

    return InvariantResult(
        invariant_id="I-001",
        name="Cross-layer semantic type consistency",
        passed=passed,
        expected=expected,
        observed=observed,
        failures=failures,
    )