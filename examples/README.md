# Example reports

Real reports produced by the plugin's skills, kept here so you can see the output before you run them.

## Agentic readiness assessment

| Repository | Archetype | Score | Status | Confidence | Report |
|---|---|---:|---|---|---|
| `fs-demo-project` | Next.js 14 App Router application (TypeScript, Prisma, PostgreSQL) | 71 / 100 | Partially ready | Medium | [agentic-readiness.md](fs-demo-project/agentic-readiness.md) |

Each report is the file the skill writes to `reports/agentic-readiness.md` in the audited repository, at the version recorded in its own run block.

Six identifiers internal to the audited project were replaced before publishing: the CI host name, the group segment of its project path, a local database password, the name of the machine that ran the audit, the name of the agent product that ran it, and the tool-specific naming of its ticket prefix and agent-lessons directory. Scores, findings, fix records, commands and evidence are exactly as generated.

## Agent tool-call latency

| Machine | Window | Calls | Tool time | Clients | Report |
|---|---|---:|---:|---|---|
| A developer laptop (macOS) | 2026-09-21 to 2026-10-21 | 120,896 | 282 h | Claude Code, Codex, T3 Code, Cursor, Antigravity | [report.md](agent-tool-call-latency/report.md) |

The report is the file the skill writes to `~/.cache/agent-tool-call-latency/<date>/report.md`. The run found waste between 45 and 74 hours. Three of its fixes came from an earlier audit of the same machine and were applied the day before, so the report also shows their first measured effect, over 1.5 days. The Cursor and Antigravity adapters were written during this run, following `references/ADAPTERS.md`, and now ship with the skill.

Five kinds of identifier were generalised before publishing:
- repository names, replaced by what each repository is (a desktop app, a 3D game, an agent platform, a workflow-engine demo project);
- the names of three lock files, which carried a project's name;
- a repository-internal path prefix on two source references;
- the names of the credential directories the deny rules cover;
- the paths of the user's agent configuration files.

Numbers, findings, fixes and statuses are exactly as generated. The skill now names repositories generically on its own, so the next report needs less of this.

