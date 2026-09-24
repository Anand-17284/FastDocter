from fastdoctor.invariants.base import ContractNode
from fastdoctor.invariants.type_consistency import (
    check_semantic_type_consistency,
)


def test_uuid_consistency_detects_mismatch():

    nodes = [
        ContractNode(
            id="openapi:order.id",
            layer="openapi",
            name="Order.id",
            semantic_type="UUID",
        ),
        ContractNode(
            id="pydantic:OrderResponse.id",
            layer="pydantic",
            name="OrderResponse.id",
            semantic_type="UUID",
        ),
        ContractNode(
            id="sqlalchemy:Order.id",
            layer="sqlalchemy",
            name="Order.id",
            semantic_type="String",
        ),
        ContractNode(
            id="postgres:orders.id",
            layer="postgres",
            name="orders.id",
            semantic_type="VARCHAR",
        ),
    ]

    result = check_semantic_type_consistency(nodes)

    assert result.passed is False
    assert "Semantic type mismatch across layers" in result.failures