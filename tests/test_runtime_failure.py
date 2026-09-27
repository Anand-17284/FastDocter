from fastdoctor.runtime.failure_capture import (
    capture_runtime_failure,
)


def test_capture_runtime_failure():

    try:
        raise ValueError("Test runtime failure")
    except ValueError as exc:

        failure = capture_runtime_failure(
            exc,
            endpoint="/orders/ORD-1007",
            method="GET",
            status_code=500,
        )

    assert failure.exception_type == "ValueError"
    assert failure.message == "Test runtime failure"
    assert failure.endpoint == "/orders/ORD-1007"
    assert failure.method == "GET"
    assert failure.status_code == 500
    assert failure.source_file is not None
    assert failure.source_line is not None