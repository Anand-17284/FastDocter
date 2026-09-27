from fastapi.testclient import TestClient

from demo_app.main import app
from fastdoctor.runtime.failure_capture import (
    capture_runtime_failure,
)


client = TestClient(
    app,
    raise_server_exceptions=True,
)


def test_capture_real_api_failure():

    try:
        client.get("/orders/ORD-1007")

    except Exception as exc:

        failure = capture_runtime_failure(
            exc,
            endpoint="/orders/ORD-1007",
            method="GET",
            status_code=500,
        )

        print("\nRUNTIME FAILURE")
        print("---------------")
        print("TYPE:", failure.exception_type)
        print("MESSAGE:", failure.message)
        print("ENDPOINT:", failure.endpoint)
        print("METHOD:", failure.method)
        print("STATUS:", failure.status_code)
        print("SOURCE:", failure.source_file)
        print("LINE:", failure.source_line)

        assert failure.exception_type == "ResponseValidationError"
        assert failure.endpoint == "/orders/ORD-1007"
        assert failure.method == "GET"
        assert failure.status_code == 500
        assert failure.source_file is not None
        assert failure.source_line is not None

    else:
        raise AssertionError(
            "Expected the API request to raise an exception"
        )