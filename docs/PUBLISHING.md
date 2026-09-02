# Publishing

This repository is one plugin root shared by Cursor, Codex, and Claude Code. The implementation stays in `skills/agentic-readiness-assessment/SKILL.md`; each platform-specific manifest only describes that shared skill.

## Before a release

1. Update the canonical version in `plugin.json` and mirror it in `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json`.
2. Record the change in `CHANGELOG.md`.
3. Validate the JSON files:

   ```sh
   python3 -m json.tool plugin.json >/dev/null
   python3 -m json.tool .codex-plugin/plugin.json >/dev/null
   python3 -m json.tool .claude-plugin/plugin.json >/dev/null
   python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
   ```

4. Validate the Claude package with a current Claude Code release:

   ```sh
   claude plugin validate . --strict
   ```

5. Load the Claude plugin locally and verify that the skill is discoverable:

   ```sh
   claude --plugin-dir .
   ```

   In Claude Code, run `/agentic-readiness-assessment:agentic-readiness-assessment` from a disposable test repository.

## Codex and ChatGPT

Create a skills-only submission in the [OpenAI plugin submission portal](https://platform.openai.com/plugins). Upload an archive whose root contains `.codex-plugin/`, `skills/`, `logo.png`, `LICENSE`, and the other repository metadata required for review.

The submission form also requires publisher verification, public support and legal URLs, listing assets, starter prompts, release notes, and positive and negative test cases. Automated safety and policy checks run before manual review. Approval does not publish the plugin automatically; publish the approved version from the portal.

The assessment depends on local repository access and may run repository-provided validation commands. Call this out explicitly in the submission. OpenAI's [Claude plugin conversion guidance](https://developers.openai.com/plugins/guides/submit-claude-plugin) says plugins whose core value requires arbitrary local file or execution access may need product-specific review.

For later versions, update all manifests, upload the new archive, submit that version for review, and publish it after approval.

## Claude Code

The repository is immediately usable as a self-hosted Claude marketplace after these files are present on the default branch:

```sh
claude plugin marketplace add exadel-inc/agentic-readiness-assessment
claude plugin install agentic-readiness-assessment@exadel-agent-plugins
```

For public discovery, submit the plugin through the [Claude plugin submission form](https://platform.claude.com/plugins/submit). Third-party plugins that pass validation, automated safety screening, and review are published in the `claude-community` marketplace. The `claude-plugins-official` marketplace is curated separately by Anthropic and has no application process.

After acceptance, verify the community catalog has synchronized, then test:

```sh
claude plugin marketplace add anthropics/claude-plugins-community
claude plugin install agentic-readiness-assessment@claude-community
```

Anthropic pins an approved plugin to a repository commit and updates that pin as subsequent commits are reviewed by its pipeline. See the [Claude Code plugin documentation](https://code.claude.com/docs/en/plugins#submit-your-plugin-to-the-community-marketplace) for the current workflow.
