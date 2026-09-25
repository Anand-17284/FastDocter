from demo_app.models import Order
from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.pydantic import analyze_pydantic_model
from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model
from fastdoctor.analyzer.postgres import analyze_postgres_column
from fastdoctor.analyzer.three_layer_mapping import map_three_layers
from fastdoctor.invariants.cross_layer import check_three_layer_mapping


def create_mappings():

    pydantic_nodes = analyze_pydantic_model(
        OrderResponse
    )

    sqlalchemy_nodes = analyze_sqlalchemy_model(
        Order
    )

    postgres_nodes = [
        analyze_postgres_column(
            table_name="orders",
            column_name="id",
            postgres_type="character varying",
            nullable=False,
        ),
        analyze_postgres_column(
            table_name="orders",
            column_name="customer_name",
            postgres_type="character varying",
            nullable=False,
        ),
    ]

    return map_three_layers(
        pydantic_nodes,
        sqlalchemy_nodes,
        postgres_nodes,
    )


def test_id_type_mismatch_is_detected():

    mappings = create_mappings()

    order_id = next(
        mapping
        for mapping in mappings
        if mapping.field_name == "id"
    )

    result = check_three_layer_mapping(order_id)

    assert result.passed is False

    assert result.invariant_id == "I-001"

    assert (
        "Semantic type mismatch"
        in result.failures[0]
    )

    assert (
        result.observed["pydantic:OrderResponse.id"]
        == "UUID"
    )

    assert (
        result.observed["sqlalchemy:Order.id"]
        == "STRING"
    )

    assert (
        result.observed["postgres:orders.id"]
        == "STRING"
    )


def test_customer_name_type_consistency_passes():

    mappings = create_mappings()

    customer_name = next(
        mapping
        for mapping in mappings
        if mapping.field_name == "customer_name"
    )

    result = check_three_layer_mapping(
        customer_name
    )

    

    assert result.passed is True

    assert result.failures == []

    assert (
        result.observed[
            "pydantic:OrderResponse.customer_name"
        ]
        == "STRING"
    )

    assert (
        result.observed[
            "sqlalchemy:Order.customer_name"
        ]
        == "STRING"
    )

    assert (
        result.observed[
            "postgres:orders.customer_name"
        ]
        == "STRING"
    )