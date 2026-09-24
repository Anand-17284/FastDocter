from demo_app.models import Order
from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.mapping import map_fields
from fastdoctor.analyzer.pydantic import analyze_pydantic_model
from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model


def test_pydantic_sqlalchemy_field_mapping():

    pydantic_nodes = analyze_pydantic_model(OrderResponse)
    sqlalchemy_nodes = analyze_sqlalchemy_model(Order)

    mappings = map_fields(
        pydantic_nodes,
        sqlalchemy_nodes,
    )

    order_mapping = next(
        mapping
        for mapping in mappings
        if mapping.source.name == "OrderResponse.id"
    )

    assert order_mapping.target.name == "Order.id"
    assert order_mapping.relationship == "field_name_match"
    assert order_mapping.confidence == "MEDIUM"
    assert "Field name 'id' matches" in order_mapping.evidence