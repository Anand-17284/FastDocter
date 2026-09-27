import json

from fastdoctor.artifact import (
    write_incident_artifact,
)
from fastdoctor.evidence import IncidentEvidence
from fastdoctor.runtime.failure_capture import (
    RuntimeFailure,
)


def test_write_incident_artifact(tmp_path):

    runtime_failure = RuntimeFailure(
        exception_type="ResponseValidationError",
        message="Invalid UUID",
        endpoint="/orders/ORD-1007",
        method="GET",
        status_code=500,
        source_file="demo_app/main.py",
        source_line=21,
    )

    incident = IncidentEvidence(
        incident_id="INC-TEST",
        runtime_failure=runtime_failure,
        evidence=[
            "api:GET /orders/ORD-1007",
            "runtime:ResponseValidationError",
        ],
    )

    artifact_path = write_incident_artifact(
        incident,
        output_dir=str(tmp_path),
    )

    assert artifact_path.exists()

    assert artifact_path.name == (
        "INC-TEST.json"
    )

    with artifact_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    assert data["incident_id"] == "INC-TEST"

    assert (
        data["runtime_failure"]["exception_type"]
        == "ResponseValidationError"
    )

    assert (
        data["runtime_failure"]["endpoint"]
        == "/orders/ORD-1007"
    )