# Changelog

All notable changes to this plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- A second skill, `agent-tool-call-latency`. It measures every tool call agents made on the machine from local session history, in any agent client, and ranks fixes for the waste: foreground waits killed at the tool's cap, locks and fixed ports that serialise parallel agents, approval and reviewer overhead, slow client releases, and start-up repeated for every call. It ships adapters for Claude Code, Codex, T3 Code, Cursor and Antigravity, a shared call-record format that adapters for other clients write to, and a hook-based capture for clients whose logs have no per-call timing. An example report from a real run is in `examples/agent-tool-call-latency/`.
- A CI job that runs every skill's script tests, and plugin and marketplace descriptions that name the second skill.
- A closing line at the end of every report, pointing to Exadel's AI Maturity & Readiness Assessment with a tracked link.
- Automatic `v<version>` tags and published GitHub releases after validation succeeds on `main`.
- A dependency-free script that updates or verifies the version across every platform manifest.
- A repository script for the GitHub tag and release publication performed by CI.

## [4.5.1] - 2026-09-23

### Added

- `gemini-extension.json`, the manifest the Gemini CLI extension gallery indexes.
- `SECURITY.md`, with a disclosure channel and a plain statement of what the skill reads, runs and writes on a user's machine.
- Install instructions for Gemini CLI, GitHub Copilot CLI, JetBrains Junie, `npx skills add`, and clients that discover skills on the filesystem.
- Support and privacy sections in the README.
- A CI workflow that parses every manifest, checks that the mirrored versions agree with `plugin.json`, and runs `claude plugin validate . --strict`.
- A CLA signature workflow for pull request contributors.
- `author`, `homepage`, `repository` and `license` on the Claude Code marketplace entry.
- Gemini and other-client publishing routes in [docs/PUBLISHING.md](docs/PUBLISHING.md).
- A HOL Plugin Scanner workflow for the community Codex marketplace requirements, with offline scanning and no automated submissions.
- The Codex composer icon field and a square Colleague icon for both Codex image fields.
- Dependabot updates for pinned GitHub Actions.

### Changed

- `CONTRIBUTING.md` rewritten around what this repository holds. The previous version was scaffolding, referring to a test suite, a linter and an npm script that do not exist here, and ending in two unfilled headings.
- The pull request template moved from the repository root to `.github/`, so the plugin payload carries only what a client needs.
- One product name that survived the first redaction pass generalized in the published example report, and the redaction note in `examples/README.md` corrected to match.
- The Exadel services pitch appears once, at the end of the README, instead of twice.
- GitHub Actions in the validation workflows are pinned to immutable commits.
- The marketplace scanner uses the public-marketplace profile and runs the Cisco deep skill scan.
- Platform manifest versions are synchronized at `4.5.1`. The assessment prompt and scoring contract are unchanged.
- The README header image is named `banner.png`; `logo.png` contains the square Colleague icon.

### Removed

- The README line saying the marketplace catalog had not yet reached the default branch. It reached it in 4.1.1.

## [4.5.0] - 2026-09-07

### Added

- Dependency-free deterministic validation of the generated report contract.
- The assessment delegation and decision record, covering deterministic calculations, report validation and human approval boundaries.

### Changed

- Host execution evidence is now required for model identity, permissions, command boundaries, stop conditions and context telemetry.
- Assessment instructions are model-neutral, portable from an installed skill directory, and explicit about two-phase report finalization.
- Report validation strengthened for status conditions, negative controls, Gate 3 anchor agreement and escaped Markdown table pipes.
- The version moved to `4.5.0`.

## [4.1.1] - 2026-09-02

### Added

- Initial plugin scaffold with the `agentic-readiness-assessment` skill.
- Assessment prompt imported from its source repository.
- Example report under `examples/`, from a run against a Next.js application, linked from the README.
- Native Codex and Claude Code plugin manifests.
- A self-hosted Claude Code marketplace catalog and publication guide.

### Removed

- `screenshot.png`, an unused placeholder carried over from the repository template.

### Changed

- The version in `plugin.json` is the canonical source of truth for the skill and is mirrored into the platform manifests. The skill reads the root manifest and records it as `prompt_version` in generated reports. See [Versioning](README.md#versioning).

[Unreleased]: https://github.com/exadel-inc/agentic-readiness-assessment/compare/v4.5.1...main
[4.5.1]: https://github.com/exadel-inc/agentic-readiness-assessment/compare/v4.5.0...v4.5.1
[4.5.0]: https://github.com/exadel-inc/agentic-readiness-assessment/compare/v4.1.1...v4.5.0
[4.1.1]: https://github.com/exadel-inc/agentic-readiness-assessment/releases/tag/v4.1.1
