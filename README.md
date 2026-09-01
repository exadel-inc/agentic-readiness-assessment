# Agentic Readiness Assessment

![GitHub contributors](https://img.shields.io/github/contributors/exadel-inc/agentic-readiness-assessment)
![GitHub Repo stars](https://img.shields.io/github/stars/exadel-inc/agentic-readiness-assessment?style=plastic)
![GitHub Repo forks](https://img.shields.io/github/forks/exadel-inc/agentic-readiness-assessment?style=plastic)
![GitHub issues](https://img.shields.io/github/issues/exadel-inc/agentic-readiness-assessment)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

![](logo.png)

**Agentic Readiness Assessment** is an agent plugin that evaluates a software repository for readiness to be developed and maintained by AI coding agents. It inspects the repository in place and produces an evidence-based readiness scorecard together with actionable recommendations.

## Description

<!-- TODO: describe the readiness areas, the scoring model, and what the generated report looks like. -->

The plugin ships a single Agent Skill, [`agentic-readiness-assessment`](skills/agentic-readiness-assessment/SKILL.md). The skill runs entirely locally: it reads the repository in your working directory, requires no backend or MCP server, and sends no repository contents anywhere.

## Supported clients

Cursor is the supported client. The plugin uses the portable [Agent Plugins](https://agent-plugins.org/specification) manifest and the open [Agent Skills](https://agentskills.io/specification) format under `skills/`, so the same repository can be extended to other clients later without moving the skill content.

## Installation

Once the plugin is published, install it from the [Cursor marketplace](https://cursor.com/marketplace).

To try it before publication, clone the repository and point Cursor at your local copy:

```sh
git clone https://github.com/exadel-inc/agentic-readiness-assessment.git
```

<!-- TODO: confirm and document the local-install step for Cursor. -->

## Getting Started

Ask your agent for an assessment from inside the repository you want to evaluate:

- "Run an agentic readiness assessment on this repository."
- "Generate an AI-readiness scorecard for this codebase."
- "How ready is this repo for AI coding agents, and what should we fix first?"

<!-- TODO: document the generated files, the output format, and any inputs the skill accepts. -->

## System Requirements

- Cursor (see [Supported clients](#supported-clients)).
- No additional runtime dependencies. The skill uses prompt-driven analysis only.

## Data handling and privacy

- The skill performs read-only analysis of the repository in the current working directory.
- No repository contents are transmitted to any external service by the plugin itself. Your agent client's own model requests are subject to that client's privacy policy.
- The plugin contains no credentials and requires none.

## Limitations

<!-- TODO: list known failure cases, e.g. very large monorepos, unsupported languages, missing CI configuration. -->

## Documentation

- [Skill definition](skills/agentic-readiness-assessment/SKILL.md)
- [Changelog](CHANGELOG.md)

## Contributing

Contributions are welcomed and greatly appreciated. See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

After creating your first contributing PR you will be requested to sign our Contributor License Agreement by commenting your PR with a special message.

## License

Distributed under the Apache License 2.0. See [LICENSE](LICENSE) for more information.

## Contact

<!-- TODO: add maintainer contacts. -->
