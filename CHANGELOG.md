# Changelog

All notable changes to this plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `gemini-extension.json`, the manifest the Gemini CLI extension gallery indexes.
- `SECURITY.md`, with a disclosure channel and a plain statement of what the skill reads, runs and writes on a user's machine.
- Install instructions for Gemini CLI, GitHub Copilot CLI, JetBrains Junie, `npx skills add`, and clients that discover skills on the filesystem.
- Support and privacy sections in the README.
- A CI workflow that parses every manifest, checks that the mirrored versions agree with `plugin.json`, and runs `claude plugin validate . --strict`.
- `author`, `homepage`, `repository` and `license` on the Claude Code marketplace entry.
- Gemini and other-client publishing routes in [docs/PUBLISHING.md](docs/PUBLISHING.md).

### Changed

- `CONTRIBUTING.md` rewritten around what this repository holds. The previous version was scaffolding, referring to a test suite, a linter and an npm script that do not exist here, and ending in two unfilled headings.
- The pull request template moved from the repository root to `.github/`, so the plugin payload carries only what a client needs.
- One product name that survived the first redaction pass generalized in the published example report, and the redaction note in `examples/README.md` corrected to match.
- The Exadel services pitch appears once, at the end of the README, instead of twice.

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

[Unreleased]: https://github.com/exadel-inc/agentic-readiness-assessment/compare/549c87a...main
[4.5.0]: https://github.com/exadel-inc/agentic-readiness-assessment/commits/549c87a
[4.1.1]: https://github.com/exadel-inc/agentic-readiness-assessment/commits/d0e74a4
