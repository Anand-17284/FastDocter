from typing import get_args, get_origin, Union

from pydantic import BaseModel

from fastdoctor.invariants.base import ContractNode


def analyze_pydantic_model(
    model: type[BaseModel],
) -> list[ContractNode]:

    nodes = []

    for field_name, field_info in model.model_fields.items():

        annotation = field_info.annotation

        # Detect Optional / nullable types such as:
        # str | None
        # Optional[str]
        origin = get_origin(annotation)
        args = get_args(annotation)

        nullable = (
            origin is Union
            and type(None) in args
        ) or (
            type(None) in args
        )

        required = field_info.is_required()

        semantic_type = getattr(
            annotation,
            "__name__",
            str(annotation),
        )

        nodes.append(
            ContractNode(
                id=f"pydantic:{model.__name__}.{field_name}",
                layer="pydantic",
                name=f"{model.__name__}.{field_name}",
                semantic_type=semantic_type,
                metadata={
                    "required": required,
                    "nullable": nullable,
                },
            )
        )

    return nodes