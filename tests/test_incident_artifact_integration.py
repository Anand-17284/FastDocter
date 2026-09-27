import json

from fastapi.testclient import TestClient

from demo_app.main import app
from fastdoctor.artifact import write_incident_artifact
from fastdoctor.evidence import build_incident_evidence
from fastdoctor.invariants.engine import InvariantEngine
from fastdoctor.analyzer.three_layer import analyze_three_layers
from fastdoctor.analyzer.three_layer_mapping import map_three_layers
from fastdoctor.runtime.failure_capture import capture_runtime_failure
from demo_app.models import Order
from demo_app.schemas import OrderResponse

client = TestClient(app)


def test_real_incident_creates_json_artifact(tmp_path):

    # 1. Reproduce the real API failure
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

    # 2. Analyze the three layers
    layers = analyze_three_layers(
        pydantic_model=OrderResponse,
        sqlalchemy_model=Order,
        table_name="orders",
    )

    # 3. Map the layers
    mappings = map_three_layers(
        pydantic_nodes=layers["pydantic"],
        sqlalchemy_nodes=layers["sqlalchemy"],
        postgres_nodes=layers["postgres"],
    )

    # 4. Run invariant checks
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

    # 5. Build incident evidence
    incident = build_incident_evidence(
        incident_id="INC-001",
        runtime_failure=runtime_failure,
        mappings=mappings,
        violated_invariants=violated_invariants,
    )

    # 6. Write JSON artifact
    artifact_path = write_incident_artifact(
        incident,
        output_dir=str(tmp_path),
    )

    # 7. Verify artifact
    assert artifact_path.exists()

    with artifact_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert data["incident_id"] == "INC-001"

    assert (
        data["runtime_failure"]["exception_type"]
        == "ResponseValidationError"
    )

    assert (
        data["runtime_failure"]["endpoint"]
        == "/orders/ORD-1007"
    )

    assert (
        data["runtime_failure"]["status_code"]
        == 500
    )

    assert len(data["mappings"]) >= 1

    assert len(
        data["violated_invariants"]
    ) >= 1

    print("\nINCIDENT ARTIFACT")
    print("=================")
    print(f"FILE: {artifact_path}")
    print(f"INCIDENT: {data['incident_id']}")
    print(
        "FAILURE:",
        data["runtime_failure"]["exception_type"],
    )
    print(
        "ENDPOINT:",
        data["runtime_failure"]["endpoint"],
    )
    print(
        "MAPPINGS:",
        len(data["mappings"]),
    )
    print(
        "VIOLATIONS:",
        len(data["violated_invariants"]),
    )
    