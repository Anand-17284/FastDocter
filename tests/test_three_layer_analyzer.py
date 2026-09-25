from demo_app.models import Order
from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.three_layer import analyze_three_layers


def test_analyze_three_layers():

    result = analyze_three_layers(
        pydantic_model=OrderResponse,
        sqlalchemy_model=Order,
        table_name="orders",
    )

    assert "pydantic" in result
    assert "sqlalchemy" in result
    assert "postgres" in result

    assert len(result["pydantic"]) == 2
    assert len(result["sqlalchemy"]) == 2
    assert len(result["postgres"]) == 2

    pydantic_id = next(
        node
        for node in result["pydantic"]
        if node.name.endswith(".id")
    )

    sqlalchemy_id = next(
        node
        for node in result["sqlalchemy"]
        if node.name.endswith(".id")
    )

    postgres_id = next(
        node
        for node in result["postgres"]
        if node.name.endswith(".id")
    )

    assert pydantic_id.semantic_type == "UUID"
    assert sqlalchemy_id.semantic_type == "STRING"
    assert postgres_id.semantic_type == "STRING"