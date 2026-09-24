from demo_app.models import Order
from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.mapping import map_fields
from fastdoctor.analyzer.pydantic import analyze_pydantic_model
from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model
from fastdoctor.invariants.cross_layer import check_mapped_field_type


def test_uuid_and_varchar_mismatch_is_detected():

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

    result = check_mapped_field_type(order_mapping)

    assert result.passed is False

    assert (
        "Type mismatch"
        in result.failures[0]
    )

    assert "pydantic:OrderResponse.id" in result.evidence
    assert "sqlalchemy:Order.id" in result.evidence
    assert "field_name_match" in result.evidence
    assert "Field name 'id' matches" in result.evidence