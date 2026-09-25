from fastdoctor.invariants.base import ContractNode
from fastdoctor.invariants.nullability import (
    check_three_layer_nullability,
)


def test_three_layer_nullability_passes():

    pydantic = ContractNode(
        id="pydantic:OrderResponse.customer_name",
        layer="pydantic",
        name="OrderResponse.customer_name",
        semantic_type="str",
        metadata={
            "required": True,
            "nullable": False,
        },
    )

    sqlalchemy = ContractNode(
        id="sqlalchemy:Order.customer_name",
        layer="sqlalchemy",
        name="Order.customer_name",
        semantic_type="STRING",
        metadata={
            "nullable": False,
        },
    )

    postgres = ContractNode(
        id="postgres:orders.customer_name",
        layer="postgres",
        name="orders.customer_name",
        semantic_type="STRING",
        metadata={
            "nullable": False,
        },
    )

    result = check_three_layer_nullability(
        pydantic,
        sqlalchemy,
        postgres,
    )

    assert result.passed is True
    assert result.invariant_id == "I-002"


def test_three_layer_nullability_fails():

    pydantic = ContractNode(
        id="pydantic:OrderResponse.customer_name",
        layer="pydantic",
        name="OrderResponse.customer_name",
        semantic_type="str",
        metadata={
            "required": True,
            "nullable": False,
        },
    )

    sqlalchemy = ContractNode(
        id="sqlalchemy:Order.customer_name",
        layer="sqlalchemy",
        name="Order.customer_name",
        semantic_type="STRING",
        metadata={
            "nullable": True,
        },
    )

    postgres = ContractNode(
        id="postgres:orders.customer_name",
        layer="postgres",
        name="orders.customer_name",
        semantic_type="STRING",
        metadata={
            "nullable": True,
        },
    )

    result = check_three_layer_nullability(
        pydantic,
        sqlalchemy,
        postgres,
    )

    assert result.passed is False
    assert result.invariant_id == "I-002"
    assert len(result.failures) > 0