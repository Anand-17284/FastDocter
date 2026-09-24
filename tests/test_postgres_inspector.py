from fastdoctor.analyzer.postgres_inspector import (
    PostgresColumnInfo,
    postgres_column_to_node,
)


def test_postgres_column_to_node():

    column = PostgresColumnInfo(
        table_name="orders",
        column_name="id",
        data_type="character varying",
        is_nullable=False,
    )

    node = postgres_column_to_node(column)

    assert node.id == "postgres:orders.id"
    assert node.layer == "postgres"
    assert node.semantic_type == "VARCHAR"

    assert node.metadata["table_name"] == "orders"
    assert node.metadata["column_name"] == "id"
    assert node.metadata["raw_type"] == "character varying"
    assert node.metadata["nullable"] is False