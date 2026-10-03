from fastdoctor.invariants.base import ContractNode, InvariantResult


def check_three_layer_nullability(
    pydantic: ContractNode | None,
    sqlalchemy: ContractNode | None,
    postgres: ContractNode | None,
) -> InvariantResult:

    nodes = (pydantic, sqlalchemy, postgres)
    nullability_by_layer = {
        layer: node.metadata.get("nullable") if node is not None else None
        for layer, node in zip(("pydantic", "sqlalchemy", "postgres"), nodes)
    }
    observed = {
        node.id: str(nullability_by_layer[layer])
        for layer, node in zip(("pydantic", "sqlalchemy", "postgres"), nodes)
        if node is not None
    }

    values = set(nullability_by_layer.values())

    passed = None if None in values else len(values) == 1

    failures = []

    for layer, node in zip(("pydantic", "sqlalchemy", "postgres"), nodes):
        if node is None:
            failures.append(f"Missing {layer} field mapping")
        elif nullability_by_layer[layer] is None:
            failures.append(f"Missing {layer} nullability metadata: {node.id}")

    if passed is False:
        failures.append(
            "Nullability mismatch across Pydantic, "
            "SQLAlchemy, and PostgreSQL"
        )

    evidence = [
        node.id if node is not None else f"missing:{layer}"
        for layer, node in zip(("pydantic", "sqlalchemy", "postgres"), nodes)
    ]

    return InvariantResult(
        invariant_id="I-002",
        name="Three-layer nullability consistency",
        passed=passed,
        expected=(
            str(nullability_by_layer["pydantic"])
            if pydantic is not None
            else None
        ),
        observed=observed,
        failures=failures,
        evidence=evidence,
    )
