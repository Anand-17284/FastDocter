from demo_app.models import Order
from demo_app.schemas import OrderResponse

from fastdoctor.analyzer.pydantic import (
    analyze_pydantic_model,
)
from fastdoctor.analyzer.sqlalchemy import (
    analyze_sqlalchemy_model,
)
from fastdoctor.analyzer.postgres import (
    analyze_postgres_column,
)
from fastdoctor.analyzer.field_discovery import (
    discover_field_mappings,
)


def test_discover_pydantic_to_sqlalchemy_mapping():

    pydantic_nodes = analyze_pydantic_model(
        OrderResponse
    )

    sqlalchemy_nodes = analyze_sqlalchemy_model(
        Order
    )

    mappings = discover_field_mappings(
        pydantic_nodes,
        sqlalchemy_nodes,
        relationship="pydantic_to_sqlalchemy",
    )

    order_mapping = next(
        mapping
        for mapping in mappings
        if mapping.source.name == "OrderResponse.id"
    )

    assert order_mapping.target.name == "Order.id"

    assert (
        order_mapping.relationship
        == "pydantic_to_sqlalchemy"
    )

    assert order_mapping.confidence == "MEDIUM"


def test_discover_sqlalchemy_to_postgres_mapping():

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

    mappings = discover_field_mappings(
        sqlalchemy_nodes,
        postgres_nodes,
        relationship="sqlalchemy_to_postgres",
    )

    order_mapping = next(
        mapping
        for mapping in mappings
        if mapping.source.name == "Order.id"
    )

    assert order_mapping.target.name == "orders.id"

    assert (
        order_mapping.relationship
        == "sqlalchemy_to_postgres"
    )

    assert order_mapping.confidence == "MEDIUM"