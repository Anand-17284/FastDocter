from demo_app.models import Order
from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.pydantic import analyze_pydantic_model
from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model
from fastdoctor.analyzer.postgres import analyze_postgres_column
from fastdoctor.analyzer.three_layer_mapping import map_three_layers


def test_three_layer_mapping():

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

    mappings = map_three_layers(
        pydantic_nodes,
        sqlalchemy_nodes,
        postgres_nodes,
    )

    assert len(mappings) == 2

    order_id = next(
        mapping
        for mapping in mappings
        if mapping.field_name == "id"
    )

    assert order_id.pydantic.name == "OrderResponse.id"
    assert order_id.sqlalchemy.name == "Order.id"
    assert order_id.postgres.name == "orders.id"

    assert order_id.pydantic.semantic_type == "UUID"
    assert order_id.sqlalchemy.semantic_type == "STRING"
    assert order_id.postgres.semantic_type == "STRING"