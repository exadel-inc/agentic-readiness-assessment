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
FIX_RECORD_FIELDS = ("Problem", "Blocks", "Evidence", "Priority", "Owner", "Target", "Fix", "Verify", "Level")
AREA_STATUSES = ("Verified", "Partial", "Repository-blocked", "N/A")


def section(content: str, heading: str) -> str | None:
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", content, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


def yaml_block(content: str) -> str | None:
    run_scope = section(content, "Run and Scope")
    if run_scope is None:
        return None
    match = re.search(r"^```yaml\n(.*?)^```$", run_scope, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else None


def integer(yaml: str, key: str, errors: list[str]) -> int | None:
    match = re.search(rf"^{re.escape(key)}:\s*(\d+)\s*$", yaml, re.MULTILINE)
    if not match:
        errors.append(f"invalid Run and Scope integer: {key}")
        return None
    return int(match.group(1))


def allowed_value(yaml: str, key: str, values: tuple[str, ...], errors: list[str]) -> None:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", yaml, re.MULTILINE)
    if match and match.group(1) not in values:
        errors.append(f"invalid Run and Scope {key}: {match.group(1)}")


def validate_scorecard(content: str, errors: list[str]) -> tuple[dict[int, int], int, int]:
    scorecard = section(content, "Readiness Scorecard")
    scores: dict[int, int] = {}
    total = 0
    applicable_maximum = 0
    if scorecard is None:
        return scores, total, applicable_maximum

    for number, (name, maximum) in enumerate(AREAS, start=1):
        match = re.search(
            rf"^\| {re.escape(name)} \| [^|]* \| ([^|]*) \| ([^|]*) \|",
            scorecard,
            re.MULTILINE,
        )
        if not match:
            errors.append(f"missing scorecard row: {name}")
            continue
        status = match.group(1).strip()
        score = match.group(2).strip()
        if status not in AREA_STATUSES:
            errors.append(f"invalid status for {name}: {status}")
        expected = {
            "Verified": maximum,
            "Partial": maximum // 2,
            "Repository-blocked": 0,
        }.get(status)
        if status == "N/A":
            if score != "N/A":
                errors.append(f"invalid score for {name}: {score}")
            continue
        applicable_maximum += maximum
        if expected is None or score != f"{expected}/{maximum}":
            errors.append(f"invalid score for {name}: {score}")
            continue
        scores[number] = expected
        total += expected
    return scores, total, applicable_maximum


def validate_gates(yaml: str, scores: dict[int, int], errors: list[str]) -> None:
    expected = {
        "setup": (2,),
        "deliverable": (3,),
        "verification": (4, 5, 6),
    }
    for gate, anchors in expected.items():
        match = re.search(
            rf"^  {gate}:\n    anchor:\s*(\d+)\n    score:\s*(\d+)\s*$",
            yaml,
            re.MULTILINE,
        )
        if not match:
            errors.append(f"missing gate entry: {gate}")
            continue
        anchor, score = (int(value) for value in match.groups())
        if anchor not in anchors:
            errors.append(f"invalid gate anchor: {gate}")
            continue
        if scores.get(anchor) != score:
            errors.append(f"gate {gate} score does not match anchor area {anchor}")

    if not re.search(r"^  probe:\n    result:\s*(pass|fail|not attempted)\s*$", yaml, re.MULTILINE):
        errors.append("missing gate entry: probe")


def validate_fix_records(content: str, errors: list[str]) -> None:
    fixes = section(content, "What to Fix")
    if fixes is None:
        return
    for identifier, record in re.findall(r"^### (F-\d\d)\n(.*?)(?=^### |\Z)", fixes, re.MULTILINE | re.DOTALL):
        for field in FIX_RECORD_FIELDS:
            if not re.search(rf"^\*\*{re.escape(field)}:\*\*\s+\S", record, re.MULTILINE):
                errors.append(f"{identifier} is missing Fix Record field: {field}")


def validate(path: Path) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return [f"cannot read report: {path}"]

    errors: list[str] = []
    if not re.search(r"^# Agentic Readiness — .+", content, re.MULTILINE):
        errors.append("missing report title")

    headings = re.findall(r"^## (.+)$", content, re.MULTILINE)
    missing = [heading for heading in SECTIONS if heading not in headings]
    errors.extend(f"missing section: {heading}" for heading in missing)
    if not missing and tuple(headings) != SECTIONS:
        errors.append("sections are not in the required order")

    glossary = section(content, "Glossary")
    if glossary is None or not re.search(r"^\| Term \| Meaning \|$", glossary, re.MULTILINE):
        errors.append("missing glossary table header")

    yaml = yaml_block(content)
    if yaml is None:
        errors.append("missing Run and Scope YAML block")
    else:
        for key in RUN_KEYS:
            if not re.search(rf"^{re.escape(key)}:\s", yaml, re.MULTILINE):
                errors.append(f"missing Run and Scope key: {key}")
        allowed_value(yaml, "status", ("Ready", "Partially ready", "Not ready"), errors)
        allowed_value(yaml, "confidence", ("High", "Medium", "Low"), errors)
        scores, scorecard_total, scorecard_maximum = validate_scorecard(content, errors)
        raw_total = integer(yaml, "raw_total", errors)
        applicable_maximum = integer(yaml, "applicable_maximum", errors)
        normalized_score = integer(yaml, "normalized_score", errors)
        if raw_total is not None and raw_total != scorecard_total:
            errors.append("raw_total does not equal scorecard total")
        if applicable_maximum is not None and applicable_maximum != scorecard_maximum:
            errors.append("applicable_maximum does not equal scorecard maximum")
        if raw_total is not None and applicable_maximum not in (None, 0) and normalized_score is not None:
            if normalized_score != round(raw_total / applicable_maximum * 100):
                errors.append("normalized_score does not match raw_total and applicable_maximum")
        validate_gates(yaml, scores, errors)

    validate_fix_records(content, errors)
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
