from fastdoctor.analyzer.three_layer_mapping import map_three_layers
from fastdoctor.invariants.engine import InvariantEngine
from fastdoctor.invariants.base import ContractNode


def make_mapping():
    pydantic_nodes = [
        ContractNode(
            id="pydantic:OrderResponse.customer_name",
            layer="pydantic",
            name="OrderResponse.customer_name",
            semantic_type="str",
            metadata={
                "required": True,
                "nullable": False,
            },
        )
    ]

    sqlalchemy_nodes = [
        ContractNode(
            id="sqlalchemy:Order.customer_name",
            layer="sqlalchemy",
            name="Order.customer_name",
            semantic_type="STRING",
            metadata={
                "nullable": False,
            },
        )
    ]

    postgres_nodes = [
        ContractNode(
            id="postgres:orders.customer_name",
            layer="postgres",
            name="orders.customer_name",
            semantic_type="STRING",
            metadata={
                "nullable": False,
            },
        )
    ]

    mappings = map_three_layers(
        pydantic_nodes,
        sqlalchemy_nodes,
        postgres_nodes,
    )

    return mappings[0]


def test_invariant_engine_runs_all_applicable_invariants():

    mapping = make_mapping()

    engine = InvariantEngine()

    results = engine.check(mapping)

    invariant_ids = {
        result.invariant_id
        for result in results
    }

    assert "I-001" in invariant_ids
    assert "I-002" in invariant_ids

    assert all(
        result.passed
        for result in results
    )

def test_invariant_engine_rejects_nullability_mismatch():

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

    mapping = map_three_layers(
        [pydantic],
        [sqlalchemy],
        [postgres],
    )[0]

    engine = InvariantEngine()

    results = engine.check(mapping)

    type_result = next(
        result
        for result in results
        if result.invariant_id == "I-001"
    )

    nullability_result = next(
        result
        for result in results
        if result.invariant_id == "I-002"
    )

    assert type_result.passed is True
    assert nullability_result.passed is False

    assert (
        "Nullability mismatch"
        in nullability_result.failures[0]
    )

    assert (
        "pydantic:OrderResponse.customer_name"
        in nullability_result.evidence
    )

    assert (
        "sqlalchemy:Order.customer_name"
        in nullability_result.evidence
    )

    assert (
        "postgres:orders.customer_name"
        in nullability_result.evidence
    )