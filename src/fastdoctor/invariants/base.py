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

    passed: bool | None

    expected: str | None

    observed: dict[str, str]

    failures: list[str] = field(default_factory=list)

    evidence: list[str] = field(default_factory=list)

    field_name: str | None = None

    violated_layers: list[str] = field(default_factory=list)

    status: str = field(init=False)

    def __post_init__(self):

        if self.passed is True:
            self.status = "VERIFIED"

        elif self.passed is False:
            self.status = "VIOLATED"

        else:
            self.status = "UNVERIFIED"
    
@dataclass
class ThreeLayerMapping:
    field_name: str
    pydantic: ContractNode | None
    sqlalchemy: ContractNode | None
    postgres: ContractNode | None
    relationship: str
    evidence: list[str] = field(default_factory=list)
    confidence: str = "UNKNOWN"
    missing_layers: list[str] = field(default_factory=list)
    ambiguous_layers: list[str] = field(default_factory=list)
    candidate_ids: dict[str, list[str]] = field(default_factory=dict)
