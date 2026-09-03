# Changelog

All notable changes to this plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial plugin scaffold with the `agentic-readiness-assessment` skill.
- Assessment prompt imported from its source repository.
- Example report under `examples/`, from a run against a Next.js application, linked from the README.
- Native Codex and Claude Code plugin manifests.
- A self-hosted Claude Code marketplace catalog and publication guide.

### Removed

- `screenshot.png`, an unused placeholder carried over from the repository template.

### Changed

- Added dependency-free deterministic validation for the generated report contract.
- Require host execution evidence for model identity, permissions, command boundaries, stop conditions, and context telemetry.
- Added the assessment delegation and decision record for deterministic calculations, report validation, and human approval boundaries.
- Made assessment instructions model-neutral, portable from an installed skill directory, and explicit about two-phase report finalization.
- Strengthened report validation for status conditions, negative controls, Gate 3 anchor agreement, and escaped Markdown table pipes.
- The version in `plugin.json` remains the canonical source of truth for the skill and is mirrored into platform manifests. It is now `4.5.0`; the skill reads the root manifest and records it as `prompt_version` in generated reports. See [Versioning](README.md#versioning).

[Unreleased]: https://github.com/exadel-inc/agentic-readiness-assessment/commits/main
