from fastdoctor.invariants.base import (
    ContractNode,
    InvariantResult,
)


def check_three_layer_type_consistency(
    pydantic_node: ContractNode,
    sqlalchemy_node: ContractNode,
    postgres_node: ContractNode,
) -> InvariantResult:

    observed = {
        pydantic_node.id: pydantic_node.semantic_type,
        sqlalchemy_node.id: sqlalchemy_node.semantic_type,
        postgres_node.id: postgres_node.semantic_type,
    }

    unique_types = set(observed.values())

    passed = len(unique_types) == 1

    failures = []

    if not passed:
        failures.append(
            "Semantic type mismatch across "
            "Pydantic, SQLAlchemy, and PostgreSQL"
        )

    expected = (
        next(iter(unique_types))
        if len(unique_types) == 1
        else None
    )

    evidence = [
        pydantic_node.id,
        sqlalchemy_node.id,
        postgres_node.id,
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