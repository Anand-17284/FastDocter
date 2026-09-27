from fastdoctor.evidence import IncidentEvidence
from fastdoctor.invariants.base import (
    InvariantResult,
    ThreeLayerMapping,
)
from fastdoctor.runtime.failure_capture import (
    RuntimeFailure,
)


def test_incident_evidence_creation():

    runtime_failure = RuntimeFailure(
        exception_type="ResponseValidationError",
        message="UUID validation failed",
        endpoint="/orders/ORD-1007",
        method="GET",
        status_code=500,
        source_file="demo_app/main.py",
        source_line=21,
    )

    invariant = InvariantResult(
        invariant_id="I-001",
        name="Three-layer semantic type consistency",
        passed=False,
        expected="UUID",
        observed={
            "pydantic:OrderResponse.id": "UUID",
            "sqlalchemy:Order.id": "STRING",
            "postgres:orders.id": "STRING",
        },
        failures=[
            "Semantic type mismatch across three layers"
        ],
        evidence=[
            "pydantic:OrderResponse.id",
            "sqlalchemy:Order.id",
            "postgres:orders.id",
        ],
    )

    incident = IncidentEvidence(
        incident_id="INC-001",
        runtime_failure=runtime_failure,
        violated_invariants=[invariant],
        mappings=[],
        evidence=[
            "api:GET /orders/ORD-1007",
            "runtime:ResponseValidationError",
            "source:demo_app/main.py:21",
        ],
    )

    assert incident.incident_id == "INC-001"

    assert (
        incident.runtime_failure.exception_type
        == "ResponseValidationError"
    )

    assert (
        incident.runtime_failure.status_code
        == 500
    )

    assert len(incident.violated_invariants) == 1

    assert (
        incident.violated_invariants[0].invariant_id
        == "I-001"
    )

    assert (
        incident.violated_invariants[0].passed
        is False
    )

    assert len(incident.evidence) == 3