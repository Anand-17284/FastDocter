from dataclasses import dataclass, field


@dataclass
class ContractNode:
    id: str
    layer: str
    name: str
    semantic_type: str
    metadata: dict = field(default_factory=dict)

@dataclass
class FieldMapping:
    source: ContractNode
    target: ContractNode
    relationship: str
    evidence: list[str] = field(default_factory=list)
    confidence: str = "UNKNOWN"

@dataclass
class InvariantResult:
    invariant_id: str
    name: str
    passed: bool
    expected: str | None
    observed: dict[str, str]
    failures: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
