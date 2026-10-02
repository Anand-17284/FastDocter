from fastdoctor.invariants.base import InvariantResult


def test_passed_invariant_is_verified():

    result = InvariantResult(
        invariant_id="I-TEST",
        name="Test invariant",
        passed=True,
        expected="STRING",
        observed={"field": "STRING"},
    )

    assert result.status == "VERIFIED"


def test_failed_invariant_is_violated():

    result = InvariantResult(
        invariant_id="I-TEST",
        name="Test invariant",
        passed=False,
        expected="UUID",
        observed={"field": "STRING"},
    )

    assert result.status == "VIOLATED"


def test_unknown_invariant_is_unverified():

    result = InvariantResult(
        invariant_id="I-TEST",
        name="Test invariant",
        passed=None,
        expected="UUID",
        observed={"field": "UNKNOWN"},
    )

    assert result.status == "UNVERIFIED"

def test_invariant_status_is_serialized():

    from fastdoctor.evidence import IncidentEvidence
    from fastdoctor.runtime.failure_capture import RuntimeFailure

    invariant = InvariantResult(
        invariant_id="I-TEST",
        name="Test invariant",
        passed=False,
        expected="UUID",
        observed={"field": "STRING"},
    )

    runtime_failure = RuntimeFailure(
        exception_type="TestError",
        message="Test failure",
        endpoint="/test",
        method="GET",
        status_code=500,
        source_file=None,
        source_line=None,
    )

    evidence = IncidentEvidence(
        incident_id="INC-TEST",
        runtime_failure=runtime_failure,
        violated_invariants=[invariant],
    )

    result = evidence.to_dict()

    assert result["violated_invariants"][0]["status"] == "VIOLATED"