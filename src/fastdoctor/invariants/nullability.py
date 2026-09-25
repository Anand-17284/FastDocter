from fastdoctor.invariants.base import ContractNode, InvariantResult


def check_three_layer_nullability(
    pydantic: ContractNode,
    sqlalchemy: ContractNode,
    postgres: ContractNode,
) -> InvariantResult:

    pydantic_nullable = pydantic.metadata.get(
        "nullable",
        None,
    )

    sqlalchemy_nullable = sqlalchemy.metadata.get(
        "nullable",
        None,
    )

    postgres_nullable = postgres.metadata.get(
        "nullable",
        None,
    )

    observed = {
        pydantic.id: str(pydantic_nullable),
        sqlalchemy.id: str(sqlalchemy_nullable),
        postgres.id: str(postgres_nullable),
    }

    values = {
        pydantic_nullable,
        sqlalchemy_nullable,
        postgres_nullable,
    }

    passed = (
        None not in values
        and len(values) == 1
    )

    failures = []

    if pydantic_nullable is None:
        failures.append(
            f"Missing Pydantic nullability metadata: {pydantic.id}"
        )

    if sqlalchemy_nullable is None:
        failures.append(
            f"Missing SQLAlchemy nullability metadata: {sqlalchemy.id}"
        )

    if postgres_nullable is None:
        failures.append(
            f"Missing PostgreSQL nullability metadata: {postgres.id}"
        )

    if not passed and not failures:
        failures.append(
            "Nullability mismatch across Pydantic, "
            "SQLAlchemy, and PostgreSQL"
        )

    evidence = [
        pydantic.id,
        sqlalchemy.id,
        postgres.id,
    ]

    return InvariantResult(
        invariant_id="I-002",
        name="Three-layer nullability consistency",
        passed=passed,
        expected=str(pydantic_nullable),
        observed=observed,
        failures=failures,
        evidence=evidence,
    )