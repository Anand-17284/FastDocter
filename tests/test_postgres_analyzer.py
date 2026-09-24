from fastdoctor.analyzer.postgres import analyze_postgres_column


def test_postgres_varchar_column_is_analyzed():

    node = analyze_postgres_column(
        table_name="orders",
        column_name="id",
        postgres_type="character varying",
        nullable=False,
    )

    assert node.id == "postgres:orders.id"
    assert node.layer == "postgres"
    assert node.name == "orders.id"
    assert node.semantic_type == "VARCHAR"
    assert node.metadata["nullable"] is False