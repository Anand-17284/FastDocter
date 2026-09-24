from demo_app.models import Order

from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model
from fastdoctor.analyzer.postgres import analyze_postgres_column
from fastdoctor.analyzer.database_mapping import (
    map_sqlalchemy_to_postgres,
)


def test_sqlalchemy_postgres_field_mapping():

    sqlalchemy_nodes = analyze_sqlalchemy_model(Order)

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

    mappings = map_sqlalchemy_to_postgres(
        sqlalchemy_nodes,
        postgres_nodes,
    )

    order_mapping = next(
        mapping
        for mapping in mappings
        if mapping.source.name == "Order.id"
    )

    assert order_mapping.target.name == "orders.id"

    assert (
        order_mapping.relationship
        == "field_name_match"
    )

    assert order_mapping.confidence == "MEDIUM"

    assert (
        "SQLAlchemy field 'id' matches PostgreSQL column 'id'"
        in order_mapping.evidence
    )