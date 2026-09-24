from fastdoctor.invariants.base import ContractNode, FieldMapping


def map_sqlalchemy_to_postgres(
    sqlalchemy_nodes: list[ContractNode],
    postgres_nodes: list[ContractNode],
) -> list[FieldMapping]:

    mappings = []

    for sqlalchemy_node in sqlalchemy_nodes:

        sqlalchemy_field = sqlalchemy_node.name.split(".")[-1]

        for postgres_node in postgres_nodes:

            postgres_field = postgres_node.name.split(".")[-1]

            if sqlalchemy_field == postgres_field:

                mappings.append(
                    FieldMapping(
                        source=sqlalchemy_node,
                        target=postgres_node,
                        relationship="field_name_match",
                        evidence=[
                            (
                                f"SQLAlchemy field "
                                f"'{sqlalchemy_field}' matches "
                                f"PostgreSQL column "
                                f"'{postgres_field}'"
                            )
                        ],
                        confidence="MEDIUM",
                    )
                )

    return mappings