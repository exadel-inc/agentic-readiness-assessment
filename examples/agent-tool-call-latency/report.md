# Agent tool-call latency — 2026-09-21 to 2026-10-21

## Headline

Agents on this machine made **120,896 tool calls in 30 days, 282 hours of tool time**. They ran in four agent clients: Claude Code (its CLI, desktop app, headless mode and Agent SDK apps), Codex, Cursor and Antigravity, with T3 Code driving Claude Code and Codex for half of the calls. **Between 45 and 74 of those hours were waste**: time the agents spent blocked, queued or waiting for a prompt, not doing the work. The rest is real work, mostly 3D asset builds, end-to-end suites and benchmarks.

| Fix | Waste in the window | Status |
|---|---:|---|
| F1. Run long work and condition waits in the background | 21.0 h of shell calls killed at the 10-minute cap | Applied 2026-10-20; no call has hit the cap since |
| F2. Give each checkout its own debug ports, so parallel agents need no lock | up to 17.1 h of lock-wrapped runs, beyond the capped ones counted in F1 | Applied 2026-10-20; no lock-wrapped run since |
| F3. Allow rules for read-only shell commands | 876 ms against 78 ms per call; about 2.4 h | Applied 2026-10-20 |
| F4. Allow-list read-only commands in Antigravity | 19.3 h of commands waiting for approval, 15.3 h of it one overnight wait | Proposed |
| F5. One browser launch per screenshot set | part of 11.7 h of screenshot runs | Proposed |
| F6. Let Codex run its safe commands without the reviewer | 0.65 h | Proposed |
| F7. Open worktrees as Cursor workspaces | 1.9 h of edits waiting for review | Needs investigation |

## Where the time goes

| Client | Calls | Hours | p50 | p90 | Calls at a timeout cap |
|---|---:|---:|---:|---:|---:|
| T3 Code → Claude Code | 45,715 | 140.8 | 0.2 s | 11.5 s | 109 |
| Claude Code CLI | 44,760 | 63.7 | 0.6 s | 4.7 s | 23 |
| T3 Code → Codex | 8,825 | 23.7 | 0.1 s | 3.4 s | 0 |
| Agent SDK app | 14,828 | 23.5 | 0.1 s | 4.5 s | 7 |
| Antigravity (IDE and CLI) | 606 | 20.8 | 0.1 s | 17.4 s | 0 |
| Cursor | 1,652 | 7.3 | 0.6 s | 7.2 s | 5 |
| Codex Desktop | 3,111 | 1.7 | 0.5 s | 3.9 s | 0 |
| Other (`claude -p`, Claude Desktop, Codex via plugin) | 1,399 | 0.4 | | | 0 |

| Category | Hours | Verdict |
|---|---:|---|
| Render / 3D (Blender asset builds and headless renders) | 57.1 | Need: the build output is the asset. 394 of 601 kit builds already pass `--only` |
| Tests: e2e / UI | 51.1 | Lock queue is waste (F2); screenshot start-up partly waste (F5); suites themselves are need |
| Wait / poll | 42.3 | Waste where a foreground loop blocked the turn (F1) |
| Waiting on you | 34.3 | User time, not tool time. 19.3 h of it is Antigravity commands waiting for approval (F4); 11.1 h is eight `AskUserQuestion` calls nobody was there to answer |
| Scripts & data | 19.0 | Need: one-off inline scripts, median 0.6 s |
| Read & search | 17.7 | Part waste: the approval check on cheap commands (F3) |
| Tests: unit / types / build | 16.4 | Need |
| Benchmarks | 12.1 | Need: timing measurements |
| Browser / computer use, Git, subagents, edits, other shell, MCP, web, installs | 31.3 | No pattern above 2% of tool time |
| Approval review (Codex) | 0.65 | Waste for safe commands (F6) |

## Fixes, ranked

### F1. Run long work and condition waits in the background

- **Where:** Claude Code, mostly under T3 Code; the desktop TTS app and the 3D game repositories.
- **Waste:** 126 shell calls ended at the 10-minute Bash cap: 105 under T3 Code (17.5 h), 14 in the CLI (2.3 h), 7 in Agent SDK apps (1.2 h). 64 of them were `until … sleep` loops and 29 were lock-wrapped runs. 21.0 h in 30 days, so about 21 h a month.
- **Cause, confirmed in the log:** the agent polled for a condition in one foreground call; the turn could do nothing else until the cap killed it. 9 of the 72 capped waits were followed directly by another wait.
- **Change:** a "Waiting on long work" section in `~/.claude/CLAUDE.md` (also read by Codex through `~/.codex/AGENTS.md`): long work and condition waits run with `run_in_background` or `Monitor`, the completion notification is the signal, and the wait matches failure states.
- **Owner:** agent environment. **Status:** applied 2026-10-20.
- **Early effect, 1.5 days, 12,267 calls:** no shell call has reached the cap; the longest `until` loop took 159 s; 364 calls ran in the background, against 69 in the whole week before.
- **Next audit:** *Calls ending at a timeout cap* should show no Bash row.

### F2. Give each checkout its own debug ports

- **Where:** the desktop TTS app (704 runs), the 3D game (151).
- **Waste:** 917 lock-wrapped runs, 21.9 h, p50 1.2 s and p90 5.1 min: most runs went straight through, and the rest queued behind another checkout's run. 29 hit the cap (4.8 h, counted under F1). The lock files were three files under `/tmp/`, each named after the app.
- **Cause, confirmed in the repository:** the end-to-end harness used fixed CDP ports (9222, 9333, 9400+, 9450+), so two checkouts refused each other's ports and agents serialised themselves with `lockf`.
- **Change:** per-checkout port blocks derived from the worktree path; the agent instructions now say not to lock (`AGENTS.md:16`).
- **Owner:** repository. **Status:** applied, merged 2026-10-20.
- **Early effect:** no lock-wrapped run in that repository since the merge.
- **Next audit:** *lock-wrapped run* should be gone from *Patterns by total time*.

### F3. Allow rules for read-only shell commands

- **Where:** Claude Code in auto mode (CLI, and T3 Code sessions that use it).
- **Waste:** within T3 Code → Claude Code, a read-only command approved by the auto-mode classifier took 876 ms at p50 (3,346 calls); the same commands approved by an allow rule took 78 ms (2,170 calls). In the CLI, classifier-approved read-only commands took 518–581 ms. About 2.4 h a month, estimated on 2026-10-19 from the 14,364 auto-mode calls the rules cover.
- **Cause, confirmed by benchmark on 2026-10-19:** in auto mode every shell command no explicit allow rule matches waits for the classifier, including built-in read-only commands. In a headless benchmark with the rules, `cat` took 77 ms, `git status` 121 ms and `sed -n` 51 ms; without them, read-only commands took 350–600 ms.
- **Change:** 51 new `permissions.allow` rules for read-only commands in `~/.claude/settings.json`, plus deny rules for `~/.ssh`, `~/.aws`, `~/.gnupg` and the GitHub CLI's token file.
- **Owner:** agent environment. **Status:** applied 2026-10-20.
- **Early effect:** in T3 Code sessions, read/search commands went from 122 ms to 87 ms at p50 and local git from 318 ms to 246 ms; 2,940 read-only calls (2,150 read/search, 790 git) were approved by the new rules. The CLI has not been used since.
- **Next audit:** the `classifier` rows in *Cheap operations by harness, mode and approval path* should shrink to compound commands and interpreters.

### F4. Allow-list read-only commands in Antigravity

- **Where:** Antigravity IDE.
- **Waste:** 38 `run_command` steps sat waiting for approval for 19.3 h in total: 15 `git`, 8 `python3`, 6 `find`, 2 `gh`, and single `ls` and `diff` calls. Most waits were under a minute; five lasted more than 25 minutes, and one, 15.3 h, overnight. During each wait the agent's run stood still.
- **Cause, confirmed in the log:** the step's status history passes through a waiting state (status 9) and resumes only after it. A `find -maxdepth 1` spent all but 0.1 s of its 314.9 s there, which only a pending approval explains.
- **Change:** add read-only prefixes (`git status`, `git log`, `git diff`, `find`, `ls`, `diff`, `gh pr view`) to the Allow list under Settings > General > Permission Settings, or per project under Settings > Projects. Per a post on Google's Antigravity forum (2026-10-15, v2.23.0): "Your configured Allow, Deny, and Ask rules are layered on top of your permission preset and always take precedence", and the Allow list takes "command prefixes or regular expressions". Forum reports describe allow-list entries moving after a restart in some builds, so check the list after restarting.
- **Owner:** agent environment. **Status:** proposed.
- **Next audit:** *Waiting on you: approval prompt* for Antigravity should keep only commands outside the list.

### F5. One browser launch per screenshot set

- **Where:** the 3D game repository.
- **Waste:** 1,733 runs of its screenshot tools (`tools/shot.ts`, `tools/still.ts`), 11.7 h, p50 10.7 s; one session made 988 screenshot calls. Each run starts its own headless Chromium (`rewrite/tools/shot.ts:94`, `rewrite/tools/still.ts:397`), so a sweep of nine viewpoints pays the start-up nine times. The share that is start-up was not determined: it needs one timed run with a single trivial shot.
- **Change:** shoot every viewpoint on one level from one launch, with `--at "+N=…"` steps between `--shots`. Resolution, samples and viewpoints stay unchanged.
- **Owner:** repository, or the agent instructions for that repository. **Status:** proposed.
- **Next audit:** *screenshot run* calls per session should drop while hours per sweep fall.

### F6. Let Codex run its safe commands without the reviewer

- **Where:** Codex Desktop and T3 Code → Codex, with `approvals_reviewer = "auto_review"`.
- **Waste:** 721 reviewer turns, p50 3.0 s, 0.65 h. About 130 of the reviewed actions were safe commands (`gh pr view`, `gh pr list`, `glab mr view`, `glab ci status`, `git fetch`, `git add`), counted on 2026-10-19 from the reviewer prompts.
- **Change:** `prefix_rule(pattern=[...], decision="allow")` entries in `~/.codex/rules/default.rules` for those prefixes. The JavaScript REPL tool (`cua_repl`) runs arbitrary code and stays reviewed.
- **Owner:** agent environment. **Status:** proposed.

### F7. Open worktrees as Cursor workspaces

- **Where:** Cursor.
- **Waste:** 37 edits blocked with `outOfWorkspace` and waited for the user's review, 1.9 h. Every one targeted a git worktree outside the folder Cursor had open. Five edits ended at 28.5 minutes; two of them were review waits, and three are not explained by the log.
- **Change:** needs investigation: open the worktree itself as the workspace, or find whether Cursor can allow edits outside the open folder.
- **Owner:** agent environment. **Status:** needs investigation.

## Ruled out

- **Claude Code 2.1.304 as a slow release.** The release table flagged its edits (p50 322 ms), but on the same release T3 Code's mode-approved edits took 12 ms. Two other things made it look slow:
  - edits that went through the auto-mode classifier (p50 312 ms, 232 calls), which is F3's cause applied to edits;
  - **hooks**: in the headless `claude -p` runs of a workflow-engine demo project, every edit runs 5 PreToolUse and 3 PostToolUse hooks (`.claude/settings.json`), so edits take 676 ms (271 calls) and reads 316 ms against 21 ms elsewhere. That cost is real but came to about 0.1 h in the window, below the 2% threshold.
- **Claude Code 2.1.280, 2.1.283 and 2.1.291.** Their edits did take 0.8–1.1 s, but those releases are no longer in use; the releases since take 14–35 ms.
- **The login shell in Codex.** `zsh -lc` costs about 100 ms, but with `shell_snapshot = true` Codex runs commands in a non-login shell (checked 2026-10-19).
- **Blender builds as waste.** They are the asset pipeline's output; two thirds already build only the changed piece.

## Not measured

- **T3 Code driving Cursor, Antigravity and Grok over ACP:** under 50 calls in the window (19 Cursor calls in T3's event log). Their own transcripts (`~/.cursor/projects/*/agent-transcripts/`) carry no per-call timestamps; T3's provider log does, but these calls were not extracted.
- **Kiro, OpenCode, Zed, Copilot CLI:** installed, but no tool calls in the window.
- **Wall-clock effect of F1–F3:** measured over 1.5 days only. Re-run after a week to confirm the early numbers.

## Corrections to CAUSES.md

- **A slow release** (replace the *Confirm* line): "Compare releases within one approval path. The release table can flag a release whose calls simply went through a slower approval path more often (Claude Code 2.1.304, 2026-10-21)."
- **New entry, hooks on every call** (confirmed 2026-10-21, Claude Code). Signal: one surface or project whose cheap operations cost hundreds of milliseconds more than the same release elsewhere. Cause: a chain of pre-tool and post-tool hooks configured in that project's settings. Fix: narrow the hooks' matchers to the tools that need them, or make each hook cheaper.
- **New entry, an approval prompt nobody is watching** (confirmed 2026-10-21, Antigravity and Cursor). Signal: *Waiting on you: approval prompt* with waits of minutes to hours. Cause: the client stops a read-only command, or an edit outside the open folder, for the user's approval. Fix: the client's allow list for read-only prefixes; for edits, open the worktree as the workspace.

Re-run after a week of normal use with `--since 2026-10-21`, and compare *Calls ending at a timeout cap*, *lock-wrapped run*, the `classifier` rows and Antigravity's approval waits.
