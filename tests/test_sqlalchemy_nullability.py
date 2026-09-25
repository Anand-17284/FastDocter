
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from fastdoctor.analyzer.sqlalchemy import analyze_sqlalchemy_model


class Base(DeclarativeBase):
    pass


class NullabilityModel(Base):
    __tablename__ = "nullability_test"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    required_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    optional_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )


def test_sqlalchemy_nullability_metadata():
    nodes = analyze_sqlalchemy_model(NullabilityModel)

    for node in nodes:
        print("\nFIELD:", node.name)
        print("TYPE:", node.semantic_type)
        print("METADATA:", node.metadata)

    required = next(
        node for node in nodes
        if node.name.endswith("required_name")
    )

    optional = next(
        node for node in nodes
        if node.name.endswith("optional_name")
    )

    assert required.metadata["nullable"] is False
    assert optional.metadata["nullable"] is True