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

RUN_SCOPE = """```yaml
audited_by: agent
prompt_version: 4.2.0
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
normalized_score: 100
raw_total: 105
applicable_maximum: 105
status: Ready
confidence: High
gates:
  setup: pass
  deliverable: pass
  verification: pass
  probe: pass
```"""


def report(*, sections: tuple[str, ...] = SECTIONS, run_scope: str = RUN_SCOPE) -> str:
    parts = ["# Agentic Readiness — Example"]
    for section in sections:
        body = "| Term | Meaning |\n| --- | --- |" if section == "Glossary" else "Content"
        if section == "Run and Scope":
            body = run_scope
        parts.append(f"## {section}\n\n{body}")
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

    def test_rejects_a_missing_glossary_header(self) -> None:
        malformed = report().replace("| Term | Meaning |", "Glossary")

        self.assertIn("missing glossary table header", self.validate(malformed))

    def test_rejects_a_missing_run_scope_key(self) -> None:
        run_scope = RUN_SCOPE.replace("prompt_version: 4.2.0\n", "")

        self.assertIn("missing Run and Scope key: prompt_version", self.validate(report(run_scope=run_scope)))


if __name__ == "__main__":
    unittest.main()
