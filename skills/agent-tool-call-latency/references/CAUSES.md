# Known causes

Causes found in earlier audits, each with the signal that points at it in `summary.md`, how to confirm it, and the fix. Harness behaviour changes between releases, so every entry carries the date it was last confirmed: treat it as a hypothesis to re-check on this machine, never as a finding. When this run confirms, corrects or retires an entry, update its date and text here.

Every fix removes **waste**: queueing, overhead, repeated start-up, killed and re-run work, waiting in the foreground, running what the change cannot affect. A fix that makes a check prove less (lower render fidelity, fewer viewpoints, skipped tests) is not a latency fix, however much time it saves.

## Foreground waiting until the tool's cap

*Confirmed 2026-10-20, Claude Code.*

- **Signal:** `until loop`, `while + sleep loop` or `watch command` with a high p90, and the same tool in *Calls ending at a timeout cap* (Claude Code's Bash cap is 10 minutes).
- **Cause:** the agent polls for a condition (a CI run, a log line, a server) inside one foreground call. The turn can do nothing else meanwhile, and a call killed at the cap is usually run again.
- **Confirm:** read the commands of the capped calls, and check whether the next call in the session repeats the same wait.
- **Fix (agent environment):** an instruction in the user's global agent instructions (`CLAUDE.md`, `AGENTS.md`): long work and condition waits run in the background (`run_in_background`, `Monitor`, or the harness's equivalent), the completion notification is the signal, and the wait matches failure states as well as success.

## A shared lock or fixed ports serialise parallel agents

*Confirmed 2026-10-20, an Electron app's end-to-end harness.*

- **Signal:** `lock-wrapped run` with a low p50 and a p90 near the cap, mostly in one project; or e2e runs whose p90 is far above their p50.
- **Cause:** the test harness uses a fixed resource (a debug port, a lock file, a shared temp path, one browser session), so agents in parallel checkouts queue behind one lock or refuse each other's ports.
- **Confirm:** find the lock in the commands, then the fixed resource in the repository's test scripts (`grep -rn` for the port numbers or the lock path).
- **Fix (repository):** derive each fixed resource from the checkout (a port block hashed from the worktree path, a per-checkout session name), keep the main checkout's old values, and refuse a resource that another program holds. Then remove the lock instruction from the repository's agent docs.

## The approval check delays cheap shell commands

*Confirmed 2026-10-19, Claude Code 2.1.30x in auto mode.*

- **Signal:** in *Cheap operations by harness, mode and approval path*, `shell read / search` and `shell git local` cost hundreds of milliseconds more under `approval = classifier` than under `mode` or a rule.
- **Cause:** in auto mode every shell command that no explicit allow rule matches waits for the safety classifier, including the built-in read-only commands (`ls`, `cat`, `git status`): those skip the prompt but not the classifier. Measured: 350–600 ms with the classifier against 50–120 ms with a rule.
- **Confirm:** benchmark ([BENCHMARK.md](BENCHMARK.md)) the same read-only commands with and without allow rules.
- **Fix (agent environment):** `permissions.allow` rules such as `Bash(git status *)` for read-only commands, in user settings, or in the project's committed settings when the whole team should get them. A compound command needs a rule for each part; wrappers like `timeout` and `nice` are stripped before matching; deny rules win over allow rules; project rules need the workspace to be trusted; Agent SDK frontends load `.claude/settings.local.json` from the session's working directory, not from the repository root. `sed`, `sort` and `uniq` can write files (`-i`, `-o`), so a strictly read-only list leaves them out.

## A slow release

*Confirmed 2026-10-19, Claude Code 2.1.280, 2.1.283 and 2.1.291.*

- **Signal:** *Releases where cheap operations were slow*.
- **Cause:** a regression in one release. In those three releases an edit took about 1 s; other releases took about 50 ms, and 2.1.303 took 22 ms.
- **Confirm:** the same operation in the same mode is fast in neighbouring releases. Mode differences can mimic a slow release, so compare within one mode.
- **Fix (agent environment):** upgrade, or pin a known-good release until a fix ships.

## An automatic reviewer holds each escalated action

*Confirmed 2026-10-19, Codex with `approvals_reviewer = "auto_review"`.*

- **Signal:** `Approval review: automatic reviewer`, about 3 s per review.
- **Cause:** every action that needs escalation outside the sandbox waits for a reviewer model's turn.
- **Confirm:** list which actions were reviewed. Each reviewer session's prompt carries the action as `Planned action JSON: {...}`; count them by command family.
- **Fix (agent environment):** a `prefix_rule(pattern=[...], decision="allow")` in `~/.codex/rules/*.rules` runs a matching command outside the sandbox without review. Linear `bash -lc` chains are split and each part must match. For MCP tools, `[mcp_servers.<server>.tools.<tool>] approval_mode = "approve"` in `config.toml`. Keep reviewing tools that run arbitrary code (a JavaScript REPL, a browser `evaluate`): the reviewer is their only check.

## Start-up repeated for every call

*Confirmed 2026-10-20, a 3D asset pipeline.*

- **Signal:** `screenshot run`, `Blender headless` or a script family with many calls and a p50 of tens of seconds.
- **Cause:** each call launches a heavy process (a headless browser, a 3D renderer, a dev server) for one output.
- **Confirm:** time one call's start-up against its work, from the script's own logging or by running it once with a single trivial output.
- **Fix (repository or agent instructions):** produce every output from one launch, through the tool's batch options or a small driver. Keep resolution, samples and viewpoints unchanged.

## The whole suite while iterating

*Confirmed 2026-10-20, an Electron app's end-to-end harness.*

- **Signal:** e2e or unit suites run many times per session, each at full length.
- **Cause:** the repository's agent docs say to run everything after each change.
- **Fix (repository):** while iterating, run the specs the change can affect; run the full suite once before the pull request.

## Checked and usually not a cause: the login shell

*Checked 2026-10-19, Codex with `shell_snapshot = true` on zsh.*

`zsh -lc true` takes about 100 ms against about 10 ms for `zsh -c`, and logs that show `/bin/zsh -lc` suggest every command pays it. With shell snapshots on, Codex runs commands in a non-login shell: ask it to run `[[ -o login ]] && echo LOGIN || echo NON_LOGIN`. Blame the login shell only when that prints `LOGIN`; the cost then sits in `~/.zprofile` (`eval "$(brew shellenv)"` alone was 75 ms), not in `~/.zshrc`.

## Not latency: waiting on the user

`Waiting on you` is time the user took to answer a question or an approval prompt. Report it apart from tool time. It points at approval prompts worth replacing with rules, not at slow tools.
