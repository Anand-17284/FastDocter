from fastapi.testclient import TestClient

from demo_app.main import app


client = TestClient(
    app,
    raise_server_exceptions=False,
)


def test_order_endpoint_reproduces_failure():

    response = client.get("/orders/ORD-1007")

    print("\nSTATUS:", response.status_code)
    print("BODY:", response.text)

    assert response.status_code == 500