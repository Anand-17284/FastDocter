from fastapi.testclient import TestClient

from demo_app.main import app
from fastdoctor.analyzer.three_layer import (
    analyze_three_layers,
)

from fastdoctor.analyzer.three_layer_mapping import (
    map_three_layers,
)

from fastdoctor.evidence import (
    IncidentEvidence,
    build_incident_evidence,
)

from fastdoctor.invariants.engine import InvariantEngine
from fastdoctor.runtime.failure_capture import (
    capture_runtime_failure,
)


client = TestClient(
    app,
    raise_server_exceptions=True,
)


def test_build_incident_evidence_from_real_api_failure():

    # 1. Reproduce the real API failure.
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

    # 2. Analyze the three contract layers.
    from demo_app.models import Order
    from demo_app.schemas import OrderResponse

    layers = analyze_three_layers(
        pydantic_model=OrderResponse,
        sqlalchemy_model=Order,
        table_name="orders",
    )

    # 3. Map corresponding fields.
    mappings = map_three_layers(
        pydantic_nodes=layers["pydantic"],
        sqlalchemy_nodes=layers["sqlalchemy"],
        postgres_nodes=layers["postgres"],
    )

    # 4. Run the invariant engine.
    engine = InvariantEngine()

    invariant_results = []

    for mapping in mappings:
        invariant_results.extend(
            engine.check(mapping)
        )

    violated_invariants = [
        result
        for result in invariant_results
        if not result.passed
    ]

    # 5. Build unified incident evidence.
    incident = build_incident_evidence(
        incident_id="INC-001",
        runtime_failure=runtime_failure,
        mappings=mappings,
        violated_invariants=violated_invariants,
    )

    # 6. Verify the evidence chain.
    assert incident.runtime_failure.exception_type == (
        "ResponseValidationError"
    )

    assert incident.runtime_failure.status_code == 500

    assert incident.runtime_failure.source_file is not None

    assert len(incident.mappings) > 0

    assert len(incident.violated_invariants) > 0

    assert any(
        item == "api:GET /orders/ORD-1007"
        for item in incident.evidence
    )

    assert any(
        item == "invariant:I-001"
        for item in incident.evidence
    )

    assert any(
        item == "field:id"
            for item in incident.evidence
    )

    assert any(
        item == "violated_layer:sqlalchemy:Order.id"
        for item in incident.evidence
    )

    assert any(
        item == "violated_layer:postgres:orders.id"
        for item in incident.evidence
    )

    assert any(
        result.invariant_id == "I-001"
        for result in incident.violated_invariants
    )

    print("\nINCIDENT EVIDENCE")
    print("=================")
    print("ID:", incident.incident_id)
    print(
        "Failure:",
        incident.runtime_failure.exception_type,
    )
    print(
        "Endpoint:",
        incident.runtime_failure.endpoint,
    )
    print(
        "Source:",
        incident.runtime_failure.source_file,
        incident.runtime_failure.source_line,
    )
    print(
        "Mappings:",
        len(incident.mappings),
    )
    print(
        "Violated invariants:",
        len(incident.violated_invariants),
    )

    for result in incident.violated_invariants:
        print(
            f" - {result.invariant_id}: "
            f"{result.name}"
        )

        print(
            "   Field:",
            result.field_name,
        )

        print("   Observed:")

        for node_id, semantic_type in result.observed.items():
            print(
                f"     {node_id} = {semantic_type}"
            )

        print("   Evidence:")

        for evidence_item in result.evidence:
            print(
                f"     - {evidence_item}"
            )