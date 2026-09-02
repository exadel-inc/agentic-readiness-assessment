# Assessment Skill Assurance Design

## Goal

Make `agentic-readiness-assessment` a more reliable coding-agent skill by adding a deterministic report-contract check, an explicit host-runtime contract, and recorded architectural decisions without expanding its report beyond the existing thirteen sections.

## Scope

The solution addresses the solution-design audit gaps that the plugin can own. Host-enforced permission modes, model pinning, and token telemetry remain runtime responsibilities; the skill will require them to be recorded or explicitly marked unavailable rather than claiming to enforce them itself.

## PR grouping

### PR 1 — Deterministic report validation

Add a dependency-free Python validator and unit tests. It will validate generated reports after the prompt's single write: thirteen ordered sections, one fixed glossary table, the required Run and Scope keys, score arithmetic, gate/anchor agreement, and Fix Record completeness. The prompt will require one corrective rewrite when validation fails and will record a validation result in the existing Confidence and Limits section.

This makes report structure and arithmetic deterministic without attempting to parse repository-specific prose.

### PR 2 — Agent execution contract

Add a concise reference document that names the architecture as a coding-agent workflow: agentic repository investigation followed by deterministic assessment, validation, and report steps. It will define the required host-supplied evidence for model identity, permission profile, command boundary, run stop condition, and context telemetry. The prompt will use the contract before execution and report unavailable host evidence as an environment limitation.

The reference is intentionally declarative. A portable skill cannot impose a host tool allowlist or pin a model; it can make those missing controls visible.

### PR 3 — Assessment decision record

Add a decision-record template and a delegation map for the assessment flow. They assign language interpretation to the model, command execution and arithmetic to deterministic tools, and scope/irreversible decisions to humans. Each decision records cost, complexity, risk, and a detection mechanism. The prompt will use this material to keep numeric scoring and report validation out of model judgement wherever a deterministic tool is available.

## Data flow

1. The agent reads the execution contract and records host evidence or an explicit limitation.
2. It follows the delegated workflow: inspect, classify, execute safe repository commands, calculate through the deterministic helper, and write one report.
3. It runs the validator against that report.
4. A failed validator result permits one full corrective rewrite, followed by one recheck; an unresolved failure is reported as a repository-assessment limitation.

## Compatibility

The report retains its thirteen-section shape, scoring areas, weights, gates, statuses, and Fix Record fields. New validation and host-evidence details live in already-existing Run and Scope / Confidence and Limits prose, so this is a prompt-semantic minor release rather than a report-contract break.

The release sequence is intentionally ordered: PR 1 supplies executable enforcement, PR 2 makes host limitations observable, and PR 3 documents the delegation and trade-offs used by both.

## Testing

PR 1 uses Python `unittest` and markdown fixtures. Tests first demonstrate rejection of a malformed report and acceptance of a valid minimal report. The JSON manifest validation in `docs/PUBLISHING.md` remains the packaging check for each PR.

PRs 2 and 3 add documentation and prompt references; their regression checks run the validator tests and JSON validation, plus repository searches confirming the prompt references the new artifacts.

## Non-goals

- Do not add dependencies, remote services, or a custom agent runtime.
- Do not claim that the skill can enforce host permission settings, model pinning, or context telemetry.
- Do not add report sections or change scoring arithmetic.
- Do not implement multi-agent fan-out for a linear assessment workflow.
