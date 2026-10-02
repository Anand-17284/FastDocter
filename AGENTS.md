# FastDoctor Repository Instructions

These instructions apply to all work in this repository.

## Before making changes

- Inspect the relevant implementation, its callers, related tests, and repository state before editing. Trace the existing execution flow and cross-layer assumptions first.
- Keep the central architecture focused on cross-layer correctness:

  ```text
  FastAPI / Pydantic → SQLAlchemy / ORM → PostgreSQL
  ```

- Prefer the smallest correct architectural change that preserves this flow. Do not add parallel abstractions or broaden scope without a concrete need.
- Do not introduce dependencies unless the change requires them. Explain the need and consider existing dependencies and standard-library options first.
- Preserve unrelated user changes and repository state. Never automatically commit or push.

## Correctness and evidence

- Treat missing, ambiguous, unsupported, or `UNKNOWN` evidence as `UNVERIFIED`. Never automatically report it as `VIOLATED` or as a successful verification.
- Keep the distinction between `VERIFIED`, `VIOLATED`, and `UNVERIFIED` explicit in invariant results, serialization, user-facing output, and tests. In particular, do not use truthiness checks that conflate `False` with `None`.
- Make diagnosis deterministic where possible: use explicit inputs, stable mappings, documented normalization rules, and reproducible evidence. Do not rely on arbitrary first matches when mappings are ambiguous.
- Keep facts separate from interpretation. In reports and technical summaries, label material claims as `FACT`, `INFERENCE`, `RECOMMENDATION`, or `UNVERIFIED` when their certainty matters.
- Do not claim production readiness without concrete evidence for the relevant deployment, security, reliability, operational, and test requirements.

## Tests and validation

- Never weaken, remove, skip, or rewrite a test merely to make a change pass. Update an existing test only when the behavior or contract intentionally changes, and retain meaningful coverage of the old risk.
- Every new behavior must have executable tests that exercise its expected result and important failure or unknown-evidence cases.
- After every code or configuration change, run the relevant tests. Before declaring a task complete, run the full test suite and report the exact command and outcome.
- If the full suite cannot run or pass because of unavailable infrastructure or another external blocker, report that limitation clearly; do not imply full validation occurred. Keep unit tests deterministic and independent of a live database wherever practical.

## PostgreSQL and secrets

- Do not perform destructive PostgreSQL operations. Never run or add unapproved `DROP`, `TRUNCATE`, destructive migrations, or data-changing commands as part of diagnosis, tests, or repair. Use explicitly scoped, disposable test databases for integration testing.
- Prefer read-only database inspection and parameterized SQL. Make database targets explicit; do not silently connect to a developer's default database for tests or diagnostics.
- Never print, log, serialize, commit, or otherwise expose credentials, tokens, connection strings containing secrets, or other secret values. Redact sensitive exception and database details before creating incident evidence. Do not read or disclose secret files unless strictly necessary to the task.

## Diagnosis and future repair behavior

- Keep diagnosis separate from repair. Diagnosis should collect traceable evidence, run deterministic invariants, and preserve uncertainty rather than guessing.
- Constrain any future AI-generated repair: treat model output as an untrusted proposal, scope it to the diagnosed issue, validate it against repository rules and tests, and require explicit human review before applying or executing changes with meaningful risk. Do not allow generated SQL or code to perform destructive database operations.
- Do not apply speculative fixes or broaden a repair beyond the evidence supporting it. Record assumptions and unresolved uncertainty.
