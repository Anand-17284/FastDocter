from fastapi.testclient import TestClient

from demo_app.main import app
from demo_app.models import Order
from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.three_layer import (
    analyze_three_layers,
)
from fastdoctor.analyzer.three_layer_mapping import (
    map_three_layers,
)
from fastdoctor.evidence import (
    build_incident_evidence,
)
from fastdoctor.invariants.engine import (
    InvariantEngine,
)
from fastdoctor.runtime.failure_capture import (
    capture_runtime_failure,
)


client = TestClient(
    app,
    raise_server_exceptions=True,
)


def test_incident_evidence_to_dict():

    try:
        client.get("/orders/ORD-1007")

    except Exception as exc:
        runtime_failure = capture_runtime_failure(
            exc,
            endpoint="/orders/ORD-1007",
            method="GET",
            status_code=500,
        )

    else:
        raise AssertionError(
            "Expected the API request to fail"
        )

    layers = analyze_three_layers(
        pydantic_model=OrderResponse,
        sqlalchemy_model=Order,
        table_name="orders",
    )

    mappings = map_three_layers(
        pydantic_nodes=layers["pydantic"],
        sqlalchemy_nodes=layers["sqlalchemy"],
        postgres_nodes=layers["postgres"],
    )

    engine = InvariantEngine()

    results = []

    for mapping in mappings:
        results.extend(
            engine.check(mapping)
        )

    violated_invariants = [
        result
        for result in results
        if not result.passed
    ]

    incident = build_incident_evidence(
        incident_id="INC-001",
        runtime_failure=runtime_failure,
        mappings=mappings,
        violated_invariants=violated_invariants,
    )

    data = incident.to_dict()

    assert data["incident_id"] == "INC-001"

    assert (
        data["runtime_failure"]["exception_type"]
        == "ResponseValidationError"
    )

    assert (
        data["runtime_failure"]["endpoint"]
        == "/orders/ORD-1007"
    )

    assert len(data["mappings"]) > 0

    assert len(data["violated_invariants"]) > 0

    invariant = data["violated_invariants"][0]

    assert invariant["invariant_id"] == "I-001"
    assert invariant["expected"] == "UUID"

    assert (
        invariant["observed"][
            "pydantic:OrderResponse.id"
        ]
        == "UUID"
    )

    assert (
        "sqlalchemy:Order.id"
        in invariant["violated_layers"]
    )

    assert (
        "postgres:orders.id"
        in invariant["violated_layers"]
    )

    assert len(data["evidence"]) > 0