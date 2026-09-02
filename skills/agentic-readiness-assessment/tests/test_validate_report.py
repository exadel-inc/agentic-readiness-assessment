from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import validate_report


SECTIONS = (
    "Verdict",
    "Run and Scope",
    "Glossary",
    "Readiness Scorecard",
    "Mandatory Gates",
    "What to Fix",
    "What Can Be Delegated Today",
    "What Is Already Good",
    "Surface Resolution",
    "Golden Path",
    "Probe",
    "Commands Executed",
    "Confidence and Limits",
)
AREAS = (
    ("Agent guidance and navigation", 10),
    ("Reproducible environment and dependency setup", 10),
    ("Build, package, render, or deliverable validation", 10),
    ("Lint, format check, typecheck, static analysis, or policy validation", 10),
    ("Unit or component tests", 10),
    ("Integration, contract, or functional tests", 5),
    ("Runtime, API, CLI, or local-preview validation", 5),
    ("Browser or UI validation", 5),
    ("Coverage and feedback-loop quality", 5),
    ("CI enforcement and parity with local validation", 10),
    ("Safety, test isolation, artifacts, and cleanup", 5),
    ("Delivery workflow from task through review or PR", 5),
    ("Agent guardrails and permission scoping", 10),
    ("Context economy", 5),
)
FIX_FIELDS = ("Problem", "Blocks", "Evidence", "Priority", "Owner", "Target", "Fix", "Verify", "Level")


def run_scope(*, raw_total: int = 105, normalized_score: int = 100, setup_score: int = 10) -> str:
    return f"""```yaml
audited_by: agent
prompt_version: 4.4.0
started: now
completed: now
commit: abc123
branch: main
platform: test
archetype: documentation
scope: repository
baseline_worktree: clean
final_worktree: clean
clean_state_setup: verified
normalized_score: {normalized_score}
raw_total: {raw_total}
applicable_maximum: 105
status: Ready
confidence: High
gates:
  setup:
    anchor: 2
    score: {setup_score}
  deliverable:
    anchor: 3
    score: 10
  verification:
    anchor: 5
    score: 10
  probe:
    result: pass
```"""


def scorecard(*, setup_status: str = "Verified") -> str:
    rows = ["| Area | Applicability | Status | Score | Verification | Evidence / Result | Fix IDs |"]
    rows.append("| --- | --- | --- | --- | --- | --- | --- |")
    for name, maximum in AREAS:
        status = setup_status if name == "Reproducible environment and dependency setup" else "Verified"
        score = maximum if status == "Verified" else maximum // 2
        rows.append(f"| {name} | applicable | {status} | {score}/{maximum} | Executed | evidence | |")
    return "\n".join(rows)


def fix_records(*, complete: bool = True) -> str:
    fields = FIX_FIELDS if complete else FIX_FIELDS[:-1]
    body = ["| ID | Priority / Owner | Problem and blocked capability | Fix and target | Verify |", "| --- | --- | --- | --- | --- |", "| F-01 | P2 / repo | problem | fix | command |", "", "### F-01"]
    body.extend(f"**{field}:** value" for field in fields)
    return "\n".join(body)


def report(*, sections: tuple[str, ...] = SECTIONS, run_scope_body: str | None = None, glossary: str = "| Term | Meaning |\n| --- | --- |", scorecard_body: str | None = None, fixes: str | None = None) -> str:
    bodies = {
        "Run and Scope": run_scope() if run_scope_body is None else run_scope_body,
        "Glossary": glossary,
        "Readiness Scorecard": scorecard() if scorecard_body is None else scorecard_body,
        "What to Fix": fix_records() if fixes is None else fixes,
    }
    parts = ["# Agentic Readiness — Example"]
    for section in sections:
        parts.append(f"## {section}\n\n{bodies.get(section, 'Content')}")
    return "\n\n".join(parts)


class ValidateReportTests(unittest.TestCase):
    def validate(self, content: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "agentic-readiness.md"
            path.write_text(content, encoding="utf-8")
            return validate_report.validate(path)

    def test_accepts_a_report_with_the_required_contract(self) -> None:
        self.assertEqual(self.validate(report()), [])

    def test_rejects_a_missing_required_section(self) -> None:
        sections = tuple(section for section in SECTIONS if section != "Probe")
        self.assertIn("missing section: Probe", self.validate(report(sections=sections)))

    def test_rejects_sections_out_of_order(self) -> None:
        sections = list(SECTIONS)
        sections[0], sections[1] = sections[1], sections[0]
        self.assertIn("sections are not in the required order", self.validate(report(sections=tuple(sections))))

    def test_rejects_an_unreadable_report(self) -> None:
        errors = validate_report.validate(Path("does-not-exist.md"))
        self.assertEqual(errors, ["cannot read report: does-not-exist.md"])

    def test_rejects_glossary_text_that_is_not_a_header_row(self) -> None:
        errors = self.validate(report(glossary="The required header is | Term | Meaning |."))
        self.assertIn("missing glossary table header", errors)

    def test_rejects_a_yaml_block_outside_run_and_scope(self) -> None:
        malformed = report(run_scope_body="Content").replace("## Confidence and Limits\n\nContent", f"## Confidence and Limits\n\n{run_scope()}")
        self.assertIn("missing Run and Scope YAML block", self.validate(malformed))

    def test_rejects_a_missing_gate_map_entry(self) -> None:
        malformed = run_scope().replace("  probe:\n    result: pass\n", "")
        self.assertIn("missing gate entry: probe", self.validate(report(run_scope_body=malformed)))

    def test_rejects_score_arithmetic_that_does_not_match_scorecard(self) -> None:
        errors = self.validate(report(run_scope_body=run_scope(raw_total=104, normalized_score=100)))
        self.assertIn("raw_total does not equal scorecard total", errors)
        self.assertIn("normalized_score does not match raw_total and applicable_maximum", errors)

    def test_rejects_an_invalid_area_status_and_score(self) -> None:
        errors = self.validate(report(scorecard_body=scorecard(setup_status="Ready")))
        self.assertIn("invalid status for Reproducible environment and dependency setup: Ready", errors)
        self.assertIn("invalid score for Reproducible environment and dependency setup: 5/10", errors)

    def test_rejects_a_gate_score_that_does_not_match_its_anchor(self) -> None:
        errors = self.validate(report(run_scope_body=run_scope(setup_score=5)))
        self.assertIn("gate setup score does not match anchor area 2", errors)

    def test_rejects_an_invalid_overall_status(self) -> None:
        errors = self.validate(report(run_scope_body=run_scope().replace("status: Ready", "status: Unknown")))
        self.assertIn("invalid Run and Scope status: Unknown", errors)

    def test_rejects_an_incomplete_fix_record(self) -> None:
        self.assertIn("F-01 is missing Fix Record field: Level", self.validate(report(fixes=fix_records(complete=False))))


if __name__ == "__main__":
    unittest.main()
