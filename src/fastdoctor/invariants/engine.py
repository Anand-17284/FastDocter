from fastdoctor.invariants.base import (
    InvariantResult,
    ThreeLayerMapping,
)
from fastdoctor.invariants.cross_layer import (
    check_three_layer_mapping,
)
from fastdoctor.invariants.nullability import (
    check_three_layer_nullability,
)


class InvariantEngine:

    def check(
        self,
        mapping: ThreeLayerMapping,
    ) -> list[InvariantResult]:

        results = []

        # I-001: Semantic type consistency
        results.append(
            check_three_layer_mapping(mapping)
        )

        # I-002: Nullability consistency
        results.append(
            check_three_layer_nullability(
                mapping.pydantic,
                mapping.sqlalchemy,
                mapping.postgres,
            )
        )

        return results