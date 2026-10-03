from dataclasses import dataclass, field

from fastdoctor.invariants.base import (
    InvariantResult,
    ThreeLayerMapping,
)
from fastdoctor.runtime.failure_capture import (
    RuntimeFailure,
)


@dataclass
class IncidentEvidence:
    incident_id: str
    runtime_failure: RuntimeFailure
    violated_invariants: list[InvariantResult] = field(
        default_factory=list
    )
    mappings: list[ThreeLayerMapping] = field(
        default_factory=list
    )
    evidence: list[str] = field(
        default_factory=list
    )

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "runtime_failure": {
                "exception_type": self.runtime_failure.exception_type,
                "message": self.runtime_failure.message,
                "endpoint": self.runtime_failure.endpoint,
                "method": self.runtime_failure.method,
                "status_code": self.runtime_failure.status_code,
                "source_file": self.runtime_failure.source_file,
                "source_line": self.runtime_failure.source_line,
            },
            "mappings": [
                {
                    "field_name": mapping.field_name,
                    "relationship": mapping.relationship,
                    "confidence": mapping.confidence,
                    "pydantic": mapping.pydantic.id if mapping.pydantic else None,
                    "sqlalchemy": mapping.sqlalchemy.id if mapping.sqlalchemy else None,
                    "postgres": mapping.postgres.id if mapping.postgres else None,
                    "missing_layers": mapping.missing_layers,
                    "ambiguous_layers": mapping.ambiguous_layers,
                    "candidate_ids": mapping.candidate_ids,
                    "evidence": mapping.evidence,
                }
                for mapping in self.mappings
            ],
            "violated_invariants": [
                {
                    "invariant_id": invariant.invariant_id,
                    "name": invariant.name,
                    "field_name": invariant.field_name,
                    "passed": invariant.passed,
                    "status": invariant.status,
                    "expected": invariant.expected,
                    "observed": invariant.observed,
                    "failures": invariant.failures,
                    "violated_layers": invariant.violated_layers,
                    "evidence": invariant.evidence,
                }
                for invariant in self.violated_invariants
            ],
            "evidence": self.evidence,
        }


def build_incident_evidence(
    incident_id: str,
    runtime_failure: RuntimeFailure,
    mappings: list[ThreeLayerMapping],
    violated_invariants: list[InvariantResult],
) -> IncidentEvidence:

    evidence = [
        f"api:{runtime_failure.method} {runtime_failure.endpoint}",
        f"runtime:{runtime_failure.exception_type}",
    ]

    if runtime_failure.source_file is not None:
        evidence.append(
            (
                f"source:{runtime_failure.source_file}:"
                f"{runtime_failure.source_line}"
            )
        )

    for mapping in mappings:
        evidence.extend(mapping.evidence)

        evidence.append(
            f"relationship:{mapping.relationship}"
        )

        evidence.append(
            f"confidence:{mapping.confidence}"
        )

    for invariant in violated_invariants:
        evidence.append(
            f"invariant:{invariant.invariant_id}"
        )

        if invariant.field_name:
            evidence.append(
                f"field:{invariant.field_name}"
            )

        for layer in invariant.violated_layers:
            evidence.append(
                f"violated_layer:{layer}"
            )

    return IncidentEvidence(
        incident_id=incident_id,
        runtime_failure=runtime_failure,
        violated_invariants=violated_invariants,
        mappings=mappings,
        evidence=evidence,
    )
