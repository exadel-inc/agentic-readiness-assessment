---
name: agent-tool-call-latency
description: Measure every agent tool call on this machine from local session history, in any harness, find where the time goes, and rank fixes for slow commands, harness overhead and wasted waiting.
disable-model-invocation: true
argument-hint: "[window, e.g. '14 days'; or a harness or project to focus on]"
---

# Agent tool-call latency

An **audit** of how long the agent's tool calls take, across every harness the user runs (CLI agents, desktop apps, frontends that drive other agents), measured from the user's own session history. It runs as **inventory**, **measure**, **diagnose**, **decisions** (the user rules on each fix), **execution** (approved fixes only) and **report**.

The skill's scripts are harness-neutral: adapters turn each harness's history into one [call record](references/SCHEMA.md) format, and everything after extraction reads only that format. A harness without a built-in adapter gets one written during the inventory.

Work in `~/.cache/agent-tool-call-latency/<today>/` (the **work directory**); `<skill>` below is this file's folder. The default window is 30 days; an argument narrows the window, the harnesses or the projects, and the phases stay the same.

## Guardrails

- **History is read-only.** Session files and databases are the user's chat history: open them read-only and never write, move or delete anything under a harness's directories.
- **Records stay local.** `calls.jsonl` holds commands, with secrets masked. It stays in the work directory; the report names command patterns, not full commands.
- **Causes are confirmed before they are ranked.** An entry in [CAUSES.md](references/CAUSES.md) is a hypothesis until this run confirms it on this machine with a benchmark, the harness's current documentation, a `path:line` in the repository, or the raw log.
- **Fixes remove waste.** Queueing, overhead, repeated start-up, killed and re-run work, foreground waiting, and tests the change cannot affect are waste. A change that makes a check prove less is not a fix.
- **The audit's own sessions are excluded.** Benchmarks run under `/tmp/agent-latency-bench/`, which every extraction passes to `--exclude-cwd`.

## Phase 1: Inventory

1. Run `python3 <skill>/scripts/extract.py --list` to see which built-in adapters find history.
2. Find the harnesses they miss. Check the installed agent CLIs and apps (`ls /Applications`, `command -v` for agent CLIs, dot-directories in `~` that hold sessions), and keep those whose history changed inside the window.
3. Write an adapter for each one, following [ADAPTERS.md](references/ADAPTERS.md), into `<work directory>/adapters/`.

Done when every harness with history in the window has an adapter that meets [ADAPTERS.md § Done when](references/ADAPTERS.md#done-when), or a recorded reason it cannot be measured (for example, no per-call timestamps), which becomes a hook-capture proposal in phase 4.

## Phase 2: Measure

1. Extract: `python3 <skill>/scripts/extract.py --since <first day> --out <work directory>/calls.jsonl --exclude-cwd /agent-latency-bench/ [--adapter <file> ...]`.
2. Validate: `python3 <skill>/scripts/validate_calls.py <work directory>/calls.jsonl`. A schema error or an unexplained WARN sends you back to the adapter.
3. Aggregate: `python3 <skill>/scripts/aggregate.py <work directory>/calls.jsonl --out-dir <work directory>` and read `summary.md`.
4. Name the unnamed buckets. For each family in *Unnamed shell commands* above 1 h, read its commands, add a `[category, label, regex]` row to `<work directory>/patterns.json`, and re-run step 3 with `--patterns`.

Done when no unnamed command family above 1 h is left.

## Phase 3: Diagnose

Work down the candidates in order of hours: *Patterns by total time*, *Calls ending at a timeout cap*, gaps in *Cheap operations by harness, mode and approval path*, *Releases where cheap operations were slow*, reviewer time, and slow MCP servers. For each one:

1. Read at least five of its real commands from `calls.jsonl`, and open the session around one slow call through its `src`.
2. Split the time into **need** (the work itself: a five-minute suite that has to run) and **waste**.
3. Match the waste against [CAUSES.md](references/CAUSES.md) and confirm it here. Harness overhead is confirmed by a [benchmark](references/BENCHMARK.md); harness behaviour by its current documentation, quoted; a repository cause by the `path:line` that creates it.
4. Estimate the recoverable hours per month: waste per call × calls per month, with the arithmetic shown.

Category totals are tool time, not wall time: a subagent's duration contains its own calls.

Done when every pattern above 2% of tool time, every cap row, and every cheap-operation gap of 200 ms or more at p50 has a confirmed cause, a *need* verdict, or *not determined* after about five attempts.

## Phase 4: Decisions

Present the fixes grouped by owner (repository, agent environment, harness vendor) and ranked by recoverable hours. Each line carries the hours, the exact change (file and setting, or the repository and the script), how its effect will show in the next audit, and its risk. Add a hook-capture proposal for each harness phase 1 could not measure. Close with the three fixes you would apply first.

Then stop for the user's rulings. A fix the user does not approve stays untouched.

## Phase 5: Execution

Apply the approved fixes:

- **Agent environment** (settings, rules, global instructions): back up the file (`<file>.pre-latency-audit`), edit it, confirm the harness still loads it, and re-run the benchmark when the fix targets overhead.
- **Repository:** follow the repository's own workflow: a branch, its checks, and a pull request per repository.

When an approved fix turns out unsafe as stated, apply the safe subset and record the deviation.

## Phase 6: Report

Write `<work directory>/report.md`; if the user's instructions set a visual style, follow it for any rendered version. In order:

1. **Headline:** tool time in the window, the hours the fixes recover, and the top three fixes.
2. **Where the time goes:** the harness and category tables, trimmed to the rows a fix or a verdict refers to.
3. **Fixes, ranked:** for each, where it applies, hours per month, the evidence, how the cause was confirmed, the change, its owner, its status (applied, approved, declined), and the row of the next audit that will show whether it worked.
4. **Ruled out:** each cause checked and rejected, one line with its evidence.
5. **Not measured:** harnesses or periods without timing, and which conclusions that leaves uncertain.
6. **Corrections to CAUSES.md:** entries this run confirmed (new date), corrected, or added, written as replacement text.

Close by saying when to re-run: after a week of normal use, with `--since` set to the day after the last fix landed, comparing the same rows.
