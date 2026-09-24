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

from fastdoctor.invariants.three_layer import (
    check_three_layer_type_consistency,
)


def test_three_layer_uuid_mismatch_is_detected():

    pydantic_nodes = analyze_pydantic_model(
        OrderResponse
    )

    sqlalchemy_nodes = analyze_sqlalchemy_model(
        Order
    )

    postgres_node = analyze_postgres_column(
        table_name="orders",
        column_name="id",
        postgres_type="character varying",
        nullable=False,
    )

    pydantic_node = next(
        node
        for node in pydantic_nodes
        if node.name == "OrderResponse.id"
    )

    sqlalchemy_node = next(
        node
        for node in sqlalchemy_nodes
        if node.name == "Order.id"
    )

    result = check_three_layer_type_consistency(
        pydantic_node,
        sqlalchemy_node,
        postgres_node,
    )

    assert result.passed is False

    assert (
        "Semantic type mismatch"
        in result.failures[0]
    )

    assert (
        result.observed[
            "pydantic:OrderResponse.id"
        ]
        == "UUID"
    )

    assert (
        result.observed[
            "sqlalchemy:Order.id"
        ]
        == "VARCHAR"
    )

    assert (
        result.observed[
            "postgres:orders.id"
        ]
        == "VARCHAR"
    )

    assert (
        "pydantic:OrderResponse.id"
        in result.evidence
    )

    assert (
        "sqlalchemy:Order.id"
        in result.evidence
    )

    assert (
        "postgres:orders.id"
        in result.evidence
    )