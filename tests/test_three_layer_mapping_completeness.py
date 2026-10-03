from fastdoctor.analyzer.three_layer_mapping import map_three_layers
from fastdoctor.evidence import IncidentEvidence
from fastdoctor.invariants.base import ContractNode
from fastdoctor.invariants.engine import InvariantEngine
from fastdoctor.runtime.failure_capture import RuntimeFailure


def node(layer: str, field_name: str, node_id: str | None = None):
    ids = {
        "pydantic": "pydantic",
        "sqlalchemy": "sqlalchemy",
        "postgres": "postgres",
    }
    names = {
        "pydantic": f"OrderResponse.{field_name}",
        "sqlalchemy": f"Order.{field_name}",
        "postgres": f"orders.{field_name}",
    }
    return ContractNode(
        id=node_id or f"{ids[layer]}:{names[layer]}",
        layer=layer,
        name=names[layer],
        semantic_type="STRING",
        metadata={"nullable": False, "table_name": "orders"},
    )


def complete_layers(field_name: str = "name"):
    return (
        [node("pydantic", field_name)],
        [node("sqlalchemy", field_name)],
        [node("postgres", field_name)],
    )


def test_valid_mapping_keeps_existing_behavior():
    mappings = map_three_layers(*complete_layers())

    assert len(mappings) == 1
    mapping = mappings[0]
    assert mapping.pydantic is not None
    assert mapping.sqlalchemy is not None
    assert mapping.postgres is not None
    assert mapping.missing_layers == []
    assert mapping.ambiguous_layers == []
    assert mapping.confidence == "HIGH"
    assert all(result.status == "VERIFIED" for result in InvariantEngine().check(mapping))


def test_missing_pydantic_field_is_retained_as_unverified_evidence():
    _, sqlalchemy, postgres = complete_layers()
    mapping = map_three_layers([], sqlalchemy, postgres)[0]

    assert mapping.pydantic is None
    assert mapping.missing_layers == ["pydantic"]
    assert mapping.candidate_ids["pydantic"] == []
    assert "missing from pydantic" in " ".join(mapping.evidence)
    assert [result.status for result in InvariantEngine().check(mapping)] == [
        "UNVERIFIED",
        "UNVERIFIED",
    ]


def test_missing_sqlalchemy_field_is_retained_as_unverified_evidence():
    pydantic, _, postgres = complete_layers()
    mapping = map_three_layers(pydantic, [], postgres)[0]

    assert mapping.sqlalchemy is None
    assert mapping.missing_layers == ["sqlalchemy"]
    assert [result.status for result in InvariantEngine().check(mapping)] == [
        "UNVERIFIED",
        "UNVERIFIED",
    ]


def test_missing_postgres_field_is_retained_as_unverified_evidence():
    pydantic, sqlalchemy, _ = complete_layers()
    mapping = map_three_layers(pydantic, sqlalchemy, [])[0]

    assert mapping.postgres is None
    assert mapping.missing_layers == ["postgres"]
    assert [result.status for result in InvariantEngine().check(mapping)] == [
        "UNVERIFIED",
        "UNVERIFIED",
    ]


def test_ambiguous_mapping_keeps_candidates_and_is_unverified():
    pydantic, sqlalchemy, postgres = complete_layers()
    sqlalchemy.append(node("sqlalchemy", "name", "sqlalchemy:Other.name"))
    mapping = map_three_layers(pydantic, sqlalchemy, postgres)[0]

    assert mapping.sqlalchemy is None
    assert mapping.missing_layers == []
    assert mapping.ambiguous_layers == ["sqlalchemy"]
    assert mapping.candidate_ids["sqlalchemy"] == [
        "sqlalchemy:Order.name",
        "sqlalchemy:Other.name",
    ]
    assert [result.status for result in InvariantEngine().check(mapping)] == [
        "UNVERIFIED",
        "UNVERIFIED",
    ]


def test_incomplete_mapping_diagnostics_are_serialized():
    pydantic, sqlalchemy, _ = complete_layers()
    mapping = map_three_layers(pydantic, sqlalchemy, [])[0]
    incident = IncidentEvidence(
        incident_id="INC-TEST",
        runtime_failure=RuntimeFailure(
            exception_type="TestError",
            message="test",
            endpoint="/test",
            method="GET",
        ),
        mappings=[mapping],
    )

    serialized = incident.to_dict()["mappings"][0]

    assert serialized["postgres"] is None
    assert serialized["missing_layers"] == ["postgres"]
    assert serialized["ambiguous_layers"] == []
    assert serialized["candidate_ids"]["postgres"] == []


def test_ambiguous_mapping_diagnostics_are_serialized():
    pydantic, sqlalchemy, postgres = complete_layers()
    sqlalchemy.append(node("sqlalchemy", "name", "sqlalchemy:Other.name"))
    mapping = map_three_layers(pydantic, sqlalchemy, postgres)[0]
    incident = IncidentEvidence(
        incident_id="INC-TEST",
        runtime_failure=RuntimeFailure(
            exception_type="TestError",
            message="test",
            endpoint="/test",
            method="GET",
        ),
        mappings=[mapping],
    )

    serialized = incident.to_dict()["mappings"][0]

    assert serialized["ambiguous_layers"] == ["sqlalchemy"]
    assert serialized["candidate_ids"]["sqlalchemy"] == [
        "sqlalchemy:Order.name",
        "sqlalchemy:Other.name",
    ]
    assert [result.status for result in InvariantEngine().check(mapping)] == [
        "UNVERIFIED",
        "UNVERIFIED",
    ]
