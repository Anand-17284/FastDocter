from pydantic import BaseModel

from fastdoctor.analyzer.pydantic import analyze_pydantic_model


class NullabilityModel(BaseModel):
    required_name: str
    optional_name: str | None = None


def test_pydantic_nullability_metadata():
    nodes = analyze_pydantic_model(NullabilityModel)

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

    assert required.metadata["required"] is True
    assert required.metadata["nullable"] is False

    assert optional.metadata["required"] is False
    assert optional.metadata["nullable"] is True