from fastdoctor.invariants.base import (
    ContractNode,
    ThreeLayerMapping,
)
from fastdoctor.invariants.cross_layer import (
    check_three_layer_mapping,
)


def test_unknown_three_layer_type_is_unverified():

    mapping = ThreeLayerMapping(
        field_name="id",
        pydantic=ContractNode(
            id="pydantic:OrderResponse.id",
            layer="pydantic",
            name="OrderResponse.id",
            semantic_type="UNKNOWN",
        ),
        sqlalchemy=ContractNode(
            id="sqlalchemy:Order.id",
            layer="sqlalchemy",
            name="Order.id",
            semantic_type="STRING",
        ),
        postgres=ContractNode(
            id="postgres:orders.id",
            layer="postgres",
            name="orders.id",
            semantic_type="STRING",
        ),
        relationship="All three field names match",
    )

    result = check_three_layer_mapping(mapping)

    assert result.passed is None
    assert "could not be verified" in result.failures[0]
