# Contributing to Agentic Readiness Assessment

Contributions are welcome, whether that is a bug report, a proposed change to the assessment prompt, a new example report, or a fix to the packaging.

## What lives here

This repository is one plugin root shared by Cursor, Codex, Claude Code and every client that reads the [Agent Skills](https://agentskills.io/specification) format. There is no application to build or deploy. The substance is:

- `skills/agentic-readiness-assessment/SKILL.md`, the assessment prompt itself, with its `references/`, `scripts/` and `tests/`
- `plugin.json` and the platform manifests under `.claude-plugin/`, `.codex-plugin/` and `gemini-extension.json`
- `examples/`, real reports produced by the skill

A change to `SKILL.md` changes what every user's report looks like. Read [Versioning](README.md#versioning) before you open one, because the version bump depends on whether your change breaks comparability between reports.

## How to propose a change

1. Fork the repository and branch from `main`.
2. Make the change.
3. Run the checks below.
4. Open a pull request describing what changed in the report a user receives, not only what changed in the file.

## Checks

```sh
python3 -m json.tool plugin.json > /dev/null
python3 -m json.tool gemini-extension.json > /dev/null
python3 -m json.tool .codex-plugin/plugin.json > /dev/null
python3 -m json.tool .claude-plugin/plugin.json > /dev/null
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
claude plugin validate . --strict
```

CI runs the same checks on every pull request. There is no build step and no linter. If your change touches a script the skill ships, run that script's own tests as well.

## Changing the assessment prompt

- Keep the report contract stable unless you intend to break it: the fourteen scoring areas, their weights, the three gates, the readiness thresholds and the report's section list.
- Describe the change in [CHANGELOG.md](CHANGELOG.md) and in the commit message, never inside `SKILL.md`. The revision history lives in git.
- If the change alters what a report says, add or update an example under `examples/` so the effect is visible.

## Adding an example report

Example reports come from real runs. Before publishing one, replace every identifier belonging to the audited project: host names, project paths, credentials, machine names, ticket prefixes and any product name that is not part of the report's substance. List what you replaced in [examples/README.md](examples/README.md). Scores, findings, fix records, commands and evidence stay exactly as generated.

## Licensing

Contributions are made under the [Apache License 2.0](LICENSE) that covers this project. On your first pull request you will be asked to sign the [Contributor License Agreement](CLA.md) by leaving a comment on it.

## Reporting bugs

Open an [issue](https://github.com/exadel-inc/agentic-readiness-assessment/issues) using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include the report the skill produced, or the part of it that is wrong, and the repository archetype you ran it against.

Security reports do not go in issues. See [SECURITY.md](SECURITY.md).

## Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
