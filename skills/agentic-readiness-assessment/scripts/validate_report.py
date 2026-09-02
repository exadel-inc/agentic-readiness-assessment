from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

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
RUN_KEYS = (
    "audited_by",
    "prompt_version",
    "started",
    "completed",
    "commit",
    "branch",
    "platform",
    "archetype",
    "scope",
    "baseline_worktree",
    "final_worktree",
    "clean_state_setup",
    "normalized_score",
    "raw_total",
    "applicable_maximum",
    "status",
    "confidence",
    "gates",
)


def validate(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not re.search(r"^# Agentic Readiness — .+", content, re.MULTILINE):
        errors.append("missing report title")

    headings = re.findall(r"^## (.+)$", content, re.MULTILINE)
    missing = [section for section in SECTIONS if section not in headings]
    errors.extend(f"missing section: {section}" for section in missing)
    if not missing and tuple(headings) != SECTIONS:
        errors.append("sections are not in the required order")

    glossary = re.search(r"^## Glossary\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL)
    if not glossary or "| Term | Meaning |" not in glossary.group(1):
        errors.append("missing glossary table header")

    run_scope = re.search(
        r"^## Run and Scope\n.*?^```yaml\n(.*?)^```",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not run_scope:
        errors.append("missing Run and Scope YAML block")
    else:
        yaml = run_scope.group(1)
        for key in RUN_KEYS:
            if not re.search(rf"^{re.escape(key)}:\s", yaml, re.MULTILINE):
                errors.append(f"missing Run and Scope key: {key}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an agentic-readiness report contract.")
    parser.add_argument("report", type=Path)
    args = parser.parse_args(argv)

    errors = validate(args.report)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
