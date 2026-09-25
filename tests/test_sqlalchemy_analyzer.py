from demo_app.models import Order

from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model


def test_sqlalchemy_model_is_analyzed():

    nodes = analyze_sqlalchemy_model(Order)

    order_id = next(
        node for node in nodes
        if node.name == "Order.id"
    )

    assert order_id.layer == "sqlalchemy"
    assert order_id.semantic_type == "STRING"
    assert order_id.metadata["table_name"] == "orders"
    assert order_id.metadata["column_name"] == "id"
    assert order_id.metadata["nullable"] is False
    assert order_id.metadata["primary_key"] is True