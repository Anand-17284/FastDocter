from fastdoctor.analyzer.postgres import analyze_postgres_column


def test_postgres_nullability_metadata():
    required = analyze_postgres_column(
        table_name="orders",
        column_name="customer_name",
        postgres_type="character varying",
        nullable=False,
    )

    optional = analyze_postgres_column(
        table_name="orders",
        column_name="description",
        postgres_type="character varying",
        nullable=True,
    )

    print("\nREQUIRED COLUMN:")
    print(required)

    print("\nOPTIONAL COLUMN:")
    print(optional)

    assert required.metadata["nullable"] is False
    assert optional.metadata["nullable"] is True