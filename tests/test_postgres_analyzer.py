from fastdoctor.analyzer.postgres import analyze_postgres_column


def test_postgres_varchar_column_is_analyzed():

    node = analyze_postgres_column(
        table_name="orders",
        column_name="id",
        postgres_type="character varying",
        nullable=False,
    )

    assert node.semantic_type == "STRING"


def test_postgres_uuid_column_is_analyzed():

    node = analyze_postgres_column(
        table_name="orders",
        column_name="id",
        postgres_type="uuid",
        nullable=False,
    )

    assert node.semantic_type == "UUID"


def test_postgres_int4_column_is_analyzed():

    node = analyze_postgres_column(
        table_name="orders",
        column_name="quantity",
        postgres_type="int4",
        nullable=False,
    )

    assert node.semantic_type == "INTEGER"


def test_postgres_bool_column_is_analyzed():

    node = analyze_postgres_column(
        table_name="orders",
        column_name="active",
        postgres_type="bool",
        nullable=False,
    )

    assert node.semantic_type == "BOOLEAN"


def test_unknown_postgres_type_is_unverified():

    node = analyze_postgres_column(
        table_name="orders",
        column_name="mystery",
        postgres_type="some_future_type",
        nullable=False,
    )

    assert node.semantic_type == "UNKNOWN"