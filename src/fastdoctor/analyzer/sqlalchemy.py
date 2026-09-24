from sqlalchemy.orm import DeclarativeBase

from fastdoctor.invariants.base import ContractNode
from fastdoctor.invariants.normalization import normalize_type


def analyze_sqlalchemy_model(
    model: type[DeclarativeBase],
) -> list[ContractNode]:

    nodes = []

    table_name = model.__table__.name

    for column in model.__table__.columns:

        raw_type = type(column.type).__name__

        nodes.append(
            ContractNode(
                id=f"sqlalchemy:{model.__name__}.{column.name}",
                layer="sqlalchemy",
                name=f"{model.__name__}.{column.name}",
                semantic_type=normalize_type(raw_type),
                metadata={
                    "nullable": column.nullable,
                    "raw_type": raw_type,
                    "table_name": table_name,
                    "column_name": column.name,
                    "primary_key": column.primary_key,
                },
            )
        )

    return nodes