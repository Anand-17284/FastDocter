from pydantic import BaseModel

from fastdoctor.invariants.base import ContractNode


def analyze_pydantic_model(
    model: type[BaseModel],
) -> list[ContractNode]:

    nodes = []

    for field_name, field_info in model.model_fields.items():
        annotation = field_info.annotation

        nodes.append(
            ContractNode(
                id=f"pydantic:{model.__name__}.{field_name}",
                layer="pydantic",
                name=f"{model.__name__}.{field_name}",
                semantic_type=getattr(
                    annotation,
                    "__name__",
                    str(annotation),
                ),
            )
        )

    return nodes