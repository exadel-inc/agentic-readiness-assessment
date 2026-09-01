# Changelog

All notable changes to this plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial plugin scaffold with the `agentic-readiness-assessment` skill.
- Assessment prompt imported from its source repository.

### Changed

- The version in `plugin.json` is now the single source of truth for the skill, set to `4.1.0` so that `MAJOR.MINOR` continues the assessment prompt's prior revision history. The skill reads it and records it as `prompt_version` in generated reports. See [Versioning](README.md#versioning).

[Unreleased]: https://github.com/exadel-inc/agentic-readiness-assessment/commits/main
