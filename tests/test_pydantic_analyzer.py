from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.pydantic import analyze_pydantic_model


def test_pydantic_model_is_analyzed():

    nodes = analyze_pydantic_model(OrderResponse)

    order_id = next(
        node for node in nodes
        if node.name == "OrderResponse.id"
    )

    assert order_id.layer == "pydantic"
    assert order_id.semantic_type == "UUID"