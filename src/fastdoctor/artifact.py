from pathlib import Path
import json

from fastdoctor.evidence import IncidentEvidence


def write_incident_artifact(
    incident: IncidentEvidence,
    output_dir: str = "artifacts/incidents",
) -> Path:

    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_file = (
        output_path
        / f"{incident.incident_id}.json"
    )

    with artifact_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            incident.to_dict(),
            file,
            indent=2,
            sort_keys=True,
        )

    return artifact_file