from fastdoctor.analyzer.pydantic import analyze_pydantic_model
from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model
from fastdoctor.analyzer.postgres_inspector import inspect_postgres_table
from fastdoctor.invariants.base import ContractNode


def analyze_three_layers(
    pydantic_model,
    sqlalchemy_model,
    table_name: str,
) -> dict[str, list[ContractNode]]:

    pydantic_nodes = analyze_pydantic_model(
        pydantic_model
    )

    sqlalchemy_nodes = analyze_sqlalchemy_model(
        sqlalchemy_model
    )

    postgres_nodes = inspect_postgres_table(
        table_name
    )

    return {
        "pydantic": pydantic_nodes,
        "sqlalchemy": sqlalchemy_nodes,
        "postgres": postgres_nodes,
    }