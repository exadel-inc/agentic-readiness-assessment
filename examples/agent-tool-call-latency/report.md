# Agent tool-call latency — developer laptop

## 1. Verdict

Agents on this machine spent **282 hours in tool calls over 30 days** (120,896 calls), and **between 45 and 74 of those hours were waste**: time an agent sat blocked, queued or waiting for an approval instead of doing work. The rest is real work, mostly 3D asset builds, end-to-end suites and benchmarks. The largest waste was foreground wait loops that held the agent's turn until the 10-minute tool cap killed them (F-01, 21.0 h). Three fixes were applied the day before this run, and in the 1.5 days since, no call has reached the cap and no run has queued behind a lock. The largest waste still open is Antigravity commands waiting for approval (F-04, 19.3 h).

## 2. Run and Scope

```yaml
audited_by: Claude Opus 5.5 (agent-tool-call-latency skill)
plugin_version: 4.5.1
started: 2026-10-21T10:30:34Z
completed: 2026-10-21T10:54:14Z
window: 2026-09-21T05:06Z to 2026-10-21T10:34Z
platform: macOS 15.8, zsh, Python 3.14
clients:
  claude-code: 107,016 records, built-in adapter (CLI, desktop app, headless, Agent SDK apps)
  codex: 11,946 records, built-in adapter (desktop app, CLI)
  t3-code: frontend; relabels the Claude Code and Codex calls it started
  cursor: 1,848 records, adapter written in this run
  antigravity: 606 records, adapter written in this run (IDE and CLI)
not_extracted: T3-driven Cursor, Antigravity and Grok sessions over ACP (under 50 calls); Kiro, OpenCode, Zed and Copilot CLI (no calls in the window)
excluded: the audit's own benchmark sessions
calls: 120,896 after 520 copied-history duplicates were dropped
tool_hours: 281.9
waste_hours: 45 to 74
fixes: {applied: 3, proposed: 3, needs_investigation: 1}
work_directory: ~/.cache/agent-tool-call-latency/2026-10-21/
```

## 3. Glossary

| Term | Meaning |
|---|---|
| Tool time | The sum of every call's duration. Parallel calls and subagents overlap, so it exceeds wall time. |
| Need | Time the work itself takes: a build, a suite, a render. |
| Waste | Time an agent was blocked, queued, waiting for a prompt or re-paying start-up. A fix removes waste without making any check prove less. |
| At cap | A call that ended at its tool's timeout, here mostly the 10-minute Bash cap. |
| Approval path | How the client approved a call: by permission mode, by an allow rule, by a classifier or reviewer model, or by the user. |
| p50 / p90 | The median and the 90th-percentile duration. |
| `F-nn` | A fix record: the problem, its evidence, the confirmed cause, the change, its owner and status, and how the next audit verifies it. |

## 4. Where the time goes

Half of all calls returned in under 405 ms; the p90 was 5.9 s, and 4,978 calls (4.1%) took longer than 30 s.

| Client | Calls | Hours | p50 | p90 | At cap |
|---|---:|---:|---:|---:|---:|
| T3 Code → Claude Code | 45,715 | 140.8 | 0.2 s | 11.5 s | 109 |
| Claude Code CLI | 44,760 | 63.7 | 0.6 s | 4.7 s | 23 |
| T3 Code → Codex | 8,825 | 23.7 | 0.1 s | 3.4 s | 0 |
| Agent SDK apps | 14,828 | 23.5 | 0.1 s | 4.5 s | 7 |
| Antigravity (IDE and CLI) | 606 | 20.8 | 0.1 s | 17.4 s | 0 |
| Cursor | 1,652 | 7.3 | 0.6 s | 7.2 s | 5 |
| Codex Desktop | 3,111 | 1.7 | 0.5 s | 3.9 s | 0 |
| Headless Claude Code, Claude Desktop, Codex via plugin | 1,399 | 0.4 | | | 0 |

| Category | Hours | Verdict |
|---|---:|---|
| Render / 3D | 57.1 | Need: Blender asset builds and renders are the asset pipeline's output, and 394 of 601 kit builds already build only the changed piece |
| Tests: e2e / UI | 51.1 | The lock queue is waste (F-02); screenshot start-up is partly waste (F-05); the suites themselves are need |
| Wait / poll | 42.3 | Waste where a foreground loop held the turn (F-01) |
| Waiting on you | 34.3 | User time, not tool time: 19.3 h of Antigravity commands waiting for approval (F-04), and 11.1 h of eight questions nobody was there to answer |
| Scripts & data | 19.0 | Need: one-off inline scripts with a 0.6 s median |
| Read & search | 17.7 | Partly waste: the approval check on cheap commands (F-03) |
| Tests: unit / types / build | 16.4 | Need |
| Benchmarks | 12.1 | Need: timing measurements |
| Browser, Git, subagents, edits, other shell, MCP, web, installs | 31.3 | No pattern above 2% of tool time |
| Approval review (Codex) | 0.65 | Waste for safe commands (F-06) |

Each shell command is named by its heaviest step, so `mkdir -p out && blender -b …` counts as a Blender run.

## 5. What to Fix

| ID | Waste in the window | Owner | Status | The next audit shows it worked when |
|---|---|---|---|---|
| F-01 | 21.0 h of calls killed at the 10-minute cap | agent environment | Applied 2026-10-20 | *Calls ending at a timeout cap* has no Bash row |
| F-02 | up to 17.1 h of lock-wrapped runs beyond F-01's | repository | Applied 2026-10-20 | *lock-wrapped run* is gone from the patterns |
| F-03 | 876 ms against 78 ms per read-only command; about 2.4 h | agent environment | Applied 2026-10-20 | The `classifier` rows shrink to compound commands and interpreters |
| F-04 | 19.3 h of commands waiting for approval | agent environment | Proposed | Antigravity's approval waits keep only commands outside the allow list |
| F-05 | part of 11.7 h of screenshot runs | repository | Proposed | Screenshot calls per session drop while hours per sweep fall |
| F-06 | 0.65 h of reviewer turns | agent environment | Proposed | Reviewer turns drop by the safe commands' share |
| F-07 | 1.9 h of edits waiting for review | agent environment | Needs investigation | Cursor's `outOfWorkspace` waits disappear |

### F-01

- **Problem:** Agents polled for a condition (a CI run, a log line, another agent's output) inside one foreground shell call, so the turn could do nothing else until the 10-minute Bash cap killed the call.
- **Evidence:** 126 shell calls ended at the cap: 105 under T3 Code (17.5 h), 14 in the CLI (2.3 h), 7 in Agent SDK apps (1.2 h). 64 were `until … sleep` loops and 29 lock-wrapped runs. 21.0 h in 30 days.
- **Cause:** confirmed in the log: the capped commands are wait loops. 9 of the 72 capped waits were followed directly by another wait.
- **Fix:** a "Waiting on long work" section in the user's global agent instructions, read by both Claude Code and Codex: long work and condition waits run in the background (`run_in_background`, `Monitor`), the completion notification is the signal, and a wait matches failure states as well as success.
- **Owner:** agent environment.
- **Status:** applied 2026-10-20. Over the next 1.5 days (12,267 calls), no shell call reached the cap, the longest `until` loop took 159 s, and 364 calls ran in the background, against 69 in the whole week before.
- **Verify:** *Calls ending at a timeout cap* has no Bash row.

### F-02

- **Problem:** Agents in parallel checkouts of a desktop app queued their end-to-end runs behind one global lock.
- **Evidence:** 917 lock-wrapped runs, 21.9 h, p50 1.2 s and p90 5.1 min: most went straight through, and the rest waited for another checkout's run. 704 in the desktop app, 151 in a 3D game. 29 hit the cap (4.8 h, counted in F-01).
- **Cause:** confirmed in the repository: its harness used fixed debug ports (9222, 9333, 9400+, 9450+), so two checkouts refused each other's ports, and agents serialised themselves with `lockf` on three lock files under `/tmp/`.
- **Fix:** per-checkout port blocks derived from the worktree path, and an agent instruction not to lock (`AGENTS.md:16`).
- **Owner:** repository.
- **Status:** applied, merged 2026-10-20. No lock-wrapped run in that repository since.
- **Verify:** *lock-wrapped run* is gone from *Patterns by total time*.

### F-03

- **Problem:** In auto mode, every cheap shell command without a matching allow rule waited for the permission classifier.
- **Evidence:** within T3 Code → Claude Code, read-only commands approved by the classifier took 876 ms at p50 (3,346 calls); the same commands approved by an allow rule took 78 ms (2,170 calls). In the CLI, classifier-approved read-only commands took 518–581 ms. About 2.4 h a month, estimated on 2026-10-19 from the 14,364 auto-mode calls the rules cover.
- **Cause:** confirmed by a benchmark on 2026-10-19: with allow rules, `cat` took 77 ms, `git status` 121 ms and `sed -n` 51 ms in headless auto mode; without them, read-only commands took 350–600 ms. Built-in read-only commands skip the prompt but not the classifier.
- **Fix:** 51 `permissions.allow` rules for read-only commands in the user's Claude Code settings, plus deny rules for credential directories.
- **Owner:** agent environment.
- **Status:** applied 2026-10-20. In T3 Code sessions since, read/search commands went from 122 ms to 87 ms at p50 and local git from 318 ms to 246 ms; the new rules approved 2,940 read-only calls (2,150 read/search, 790 git). The CLI has not been used since.
- **Verify:** the `classifier` rows of *Cheap operations by harness, mode and approval path* shrink to compound commands and interpreters.

### F-04

- **Problem:** Antigravity stopped read-only commands until the user approved them, and the agent's run stood still meanwhile.
- **Evidence:** 38 `run_command` steps waited 19.3 h in total: 15 `git`, 8 `python3`, 6 `find`, 2 `gh`, and single `ls` and `diff` calls. Most waits were under a minute; five lasted more than 25 minutes, and one, 15.3 h, overnight.
- **Cause:** confirmed in the log: each step's status history passes through a waiting state (status 9) and resumes only after it. A `find -maxdepth 1` spent all but 0.1 s of its 314.9 s there.
- **Fix:** add read-only prefixes (`git status`, `git log`, `git diff`, `find`, `ls`, `diff`, `gh pr view`) to the Allow list under Settings > General > Permission Settings, or per project under Settings > Projects. A post on Google's Antigravity forum (2026-10-15, v2.23.0) says Allow, Deny and Ask rules "always take precedence" over the permission preset and take "command prefixes or regular expressions". Some builds reportedly move allow-list entries after a restart, so check the list after restarting.
- **Owner:** agent environment.
- **Status:** proposed.
- **Verify:** Antigravity's approval waits keep only commands outside the list.

### F-05

- **Problem:** A 3D game's screenshot tools start a fresh headless browser for every run, so a sweep of nine viewpoints pays the browser start, the game boot and the level load nine times.
- **Evidence:** 1,733 screenshot runs, 11.7 h, p50 10.7 s; one session made 988 screenshot calls. Each run launches Chromium (`tools/shot.ts:94`, `tools/still.ts:397`). The share that is start-up was not determined: it needs one timed run with a single trivial shot.
- **Cause:** confirmed in the repository, at the lines above.
- **Fix:** shoot every viewpoint on one level from one launch, with `--at "+N=…"` steps between `--shots`. Resolution, samples and viewpoints stay unchanged.
- **Owner:** repository, or the agent instructions for that repository.
- **Status:** proposed.
- **Verify:** screenshot calls per session drop while hours per sweep fall.

### F-06

- **Problem:** Codex's automatic reviewer held each escalated action for about 3 s, including safe commands.
- **Evidence:** 721 reviewer turns, p50 3.0 s, 0.65 h. About 130 of the reviewed actions were safe (`gh pr view`, `gh pr list`, `glab mr view`, `glab ci status`, `git fetch`, `git add`), counted on 2026-10-19 from the reviewer prompts. The largest reviewed group was computer-use JavaScript (`cua_repl`).
- **Cause:** confirmed in the configuration: `approvals_reviewer = "auto_review"` sends every action that leaves the sandbox to a reviewer model.
- **Fix:** `prefix_rule(pattern=[...], decision="allow")` entries in Codex's rules file for those prefixes. `cua_repl` runs arbitrary code and stays reviewed.
- **Owner:** agent environment.
- **Status:** proposed.
- **Verify:** reviewer turns drop by the safe commands' share.

### F-07

- **Problem:** Cursor blocked edits to files outside the folder it had open and waited for the user's review.
- **Evidence:** 37 edits blocked with `outOfWorkspace`, 1.9 h; every one targeted a git worktree outside the open folder. Five edits ended at 28.5 minutes; two were review waits, and the log does not explain the other three.
- **Cause:** confirmed in the log (`blockReason: outOfWorkspace` with `reviewData`).
- **Fix:** needs investigation: open the worktree itself as the workspace, or find whether Cursor can allow edits outside the open folder.
- **Owner:** agent environment.
- **Status:** needs investigation.
- **Verify:** Cursor's `outOfWorkspace` waits disappear.

## 6. Same operation, different client

Workloads differ between clients, so compare cheap operations only: p50 / p90, approval waits excluded.

| Operation | T3 → Claude Code | Claude Code CLI | Agent SDK apps | T3 → Codex | Codex Desktop | Cursor | Antigravity |
|---|---|---|---|---|---|---|---|
| Read | 22 / 332 ms | 13 / 269 ms | 18 / 243 ms | 0 / 1 ms | 0 / 0 ms | 89 / 566 ms | 6 / 132 ms |
| Edit / write | 15 / 773 ms | 134 / 1,162 ms | 12 / 21 ms | 1 / 59 ms | 141 / 3,605 ms | 1,610 / 26,879 ms | 8 / 4,912 ms |
| Shell read / search | 102 / 1,007 ms | 535 / 1,365 ms | 79 / 242 ms | 1 / 241 ms | 1 / 180 ms | 594 / 3,846 ms | 143 / 3,117 ms |
| Shell git (local) | 270 / 1,167 ms | 711 / 1,960 ms | 184 / 469 ms | 97 / 547 ms | 78 / 318 ms | 898 / 2,470 ms | 164 / 4,394 ms |

- The CLI is the slowest Claude Code surface for shell commands; the gap is the classifier (F-03).
- Codex times the command alone, so its cheap operations read close to zero.
- Cursor's edits take 1.6 s at p50 (208 calls, 3.7 h), the slowest edit of any client here. That is below the 2% ranking threshold, so no fix is ranked for it.

## 7. Patterns by total time

| Pattern | Hours | Calls | p50 | p90 | At cap | Where |
|---|---:|---:|---:|---:|---:|---|
| Render / 3D: Blender Python asset build | 41.3 | 4,303 | 3.0 s | 97.9 s | 10 | 3D game |
| Wait / poll: until loop | 30.8 | 1,110 | 3.9 s | 6.9 min | 64 | desktop app, 3D game |
| Tests: e2e / UI: lock-wrapped run | 21.9 | 917 | 1.2 s | 5.1 min | 29 | desktop app, 3D game |
| Waiting on you: approval prompt | 21.9 | 223 | 0.3 s | 2.4 min | 2 | Antigravity, Cursor, desktop app |
| Tests: e2e / UI: screenshot run | 19.7 | 2,221 | 11.7 s | 80.4 s | 6 | 3D game |
| Render / 3D: Blender headless | 15.8 | 1,117 | 25.3 s | 121.6 s | 3 | 3D game |
| Read & search: read / search shell | 15.6 | 41,497 | 0.4 s | 1.2 s | 1 | all |
| Waiting on you: question | 12.4 | 70 | 18.0 s | 4.7 min | 0 | |
| Benchmarks: benchmark / equivalence run | 12.1 | 518 | 1.2 s | 6.8 min | 5 | 3D game, desktop app |
| Scripts & data: python script | 9.9 | 9,539 | 0.6 s | 4.1 s | 0 | 3D game, agent platform |
| Tests: e2e / UI: e2e suite | 9.6 | 729 | 8.6 s | 108.8 s | 0 | agent platform, desktop app |
| Scripts & data: node / tsx script | 9.1 | 6,147 | 0.7 s | 9.3 s | 4 | desktop app |

The MCP servers cost little: the slowest were computer use (`cua_repl`, 215 calls, p50 2.9 s, 4.7 h) and Playwright (643 calls, p50 1.4 s, 3.6 h). T3 Code's own orchestration tools returned in 18 ms at p50 (819 calls).

## 8. Ruled out

- **Claude Code 2.1.304 as a slow release.** The release table flagged its edits (p50 322 ms), but on the same release T3 Code's mode-approved edits took 12 ms. Two other things made it look slow:
  - edits that went through the classifier (p50 312 ms, 232 calls), F-03's cause applied to edits;
  - in a workflow-engine demo project run headless, every edit runs 5 PreToolUse and 3 PostToolUse hooks, so its edits took 676 ms (271 calls) and its reads 316 ms. That cost is real but came to about 0.1 h, below the 2% threshold.
- **Claude Code 2.1.280, 2.1.283 and 2.1.291.** Their edits took 0.8–1.1 s, but none is in use any more; the releases since take 14–35 ms.
- **The login shell in Codex.** `zsh -lc` costs about 100 ms, but with shell snapshots on, Codex runs commands in a non-login shell (checked 2026-10-19).
- **Blender builds as waste.** They are the asset pipeline's output, and two thirds already build only the changed piece.

## 9. Confidence and limits

The window is fully measured for Claude Code, Codex, Cursor and Antigravity. Claude Code's call times are derived from transcript line timestamps, and a parallel call is timed from the end of the message that issued it. The other clients record each call's own start and end.

The early effect of F-01 to F-03 rests on 1.5 days and 12,267 calls, almost all from T3 Code sessions. The CLI has not been used since the fixes, so the CLI's share of F-03 is an estimate, not a measurement. The two adapters written in this run passed the validator and were spot-checked against their stores, but their per-session call counts were not compared with the clients' own UI.

Not measured:
- T3 Code driving Cursor, Antigravity and Grok over ACP: under 50 calls. Their transcripts carry no per-call timestamps; T3's provider log does, but these calls were not extracted.
- Kiro, OpenCode, Zed, Copilot CLI: no tool calls in the window.
- The start-up share of F-05, and the three unexplained 28.5-minute Cursor edits in F-07.

## 10. Commands Executed

| Command | Result |
|---|---|
| `extract.py --list` | 3 of the 4 built-in adapters found history: Claude Code (2,000 sessions), Codex (210), T3 Code (103 sources) |
| `sqlite3` read-only queries on Cursor's and Antigravity's stores | tool-call fields, timestamps and the approval state located |
| `extract.py --since 2026-09-21 --exclude-cwd … --adapter cursor.py --adapter antigravity.py --out calls.jsonl` | 120,896 calls after 520 duplicates, in 30 s |
| `validate_calls.py calls.jsonl` | 0 invalid, 0 duplicate records |
| `aggregate.py calls.jsonl --patterns patterns.json` | 281.9 h; 5 patterns added for unnamed families above 1 h |
| `extract.py` with the shipped adapters only | 120,919 calls, 281.93 h: the same totals, plus this session's latest calls |

## 11. Corrections to CAUSES.md

- **A slow release:** compare releases within one approval path and one surface. Claude Code 2.1.304 looked slow because of classifier approvals and project hooks.
- **New, hooks on every call:** a project whose cheap operations cost hundreds of milliseconds more than the same release elsewhere runs a chain of pre-tool and post-tool hooks on every call. Narrow the matchers or make the hooks cheaper.
- **New, an approval prompt nobody is watching:** a read-only command, or an edit outside the open folder, waits for a user who is not there. Use the client's allow list for read-only prefixes, and open worktrees as workspaces.

Re-run after a week of normal use with `--since 2026-10-21`, comparing *Calls ending at a timeout cap*, *lock-wrapped run*, the `classifier` rows and Antigravity's approval waits.

---

This report covers one machine's agents. For the organization-level version, covering people and process as well as code, see Exadel's [AI Maturity & Readiness Assessment](https://exadel.com/services/ai-maturity-readiness-assessment/?utm_source=agent-tool-call-latency&utm_medium=plugin-report&utm_campaign=readiness-test-2026-10).
