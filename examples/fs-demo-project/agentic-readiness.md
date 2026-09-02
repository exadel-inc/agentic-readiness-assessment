# Agentic Readiness — fs-demo-project

## 1. Verdict

Raw score 75/105 (71 normalized), overall status **Partially ready**, verification confidence **Medium**. The repository gives an agent an unusually coherent golden path — clean feature traceability, a real CI-proven test suite (154 tests across 22 files, all green at the audited commit), and scoped tool permissions — but Gate 1 (setup) only reaches half credit because this audit host could not start the documented containerized Postgres, and Gate 4 (the probe) could not be attempted as a direct consequence, so the repository's fix-the-loop capability is asserted by CI history rather than demonstrated live in this run. The single most expensive blocker is **F-08** (host port 5432 already bound by an unrelated system service, preventing `docker compose up -d` from ever starting the project's database locally).

## 2. Run and Scope

```yaml
audited_by: Claude (agentic-readiness-assessment skill)
prompt_version: 4.1.0
started: 2026-09-01T22:55:00Z
completed: 2026-09-01T23:41:03Z
commit: 71ed88230843e03f10a7c4c998701d418afff667
branch: main
platform: linux (podman 4.9.3 / podman-compose 1.0.6 as `docker`/`docker compose`; Node v18.19.1; Python 3.12.3; make 4.3)
archetype: Application (Next.js 14 App Router monolith — server-rendered UI, REST API routes, and persistence in one deployable process)
scope: single component, no monorepo split. Contradicts the audit brief, which described a `backend/` (Python/pytest) plus `frontend/` (Node) layout; no such directories exist in this repository (confirmed by `find . -iname backend -o -iname frontend -o -iname conftest.py -o -iname pytest.ini -o -iname main.py`, zero matches). The whole tree — `src/app` (UI + `src/app/api` routes), `src/lib` (business logic and shared config helpers), `prisma/` (schema + migrations), `e2e/` (Playwright) — is one npm-managed TypeScript workspace, audited in full.
baseline_worktree: clean, HEAD at 71ed882 ("Add UI journey 15: dashboard shows recent quotes across both lines of business"), one unrelated stash entry (stash@{0}) untouched
final_worktree: clean except this report; stash entry untouched; no probe was run so nothing required reverting
clean_state_setup: unfrozen fallback not needed (`npm ci` succeeded frozen) — warmed-workspace-only for the dependency layer is ruled out (`node_modules` did not exist before this audit's `npm ci`); blocked for the database layer (see F-08)
normalized_score: 71
raw_total: 75
applicable_maximum: 105
status: Partially ready
confidence: Medium
gates:
  setup: Partial (Area 2) — dependency install Executed clean; database layer Environment-blocked (F-08)
  deliverable: Verified (Area 3) — Executed, `npm run build` succeeded locally
  verification: Verified (Area 5) — CI-proven, pipeline 347536 job `test`, commit 71ed882
  probe: not attempted — blocked by F-08 (Gate 3 did not execute locally, so the probe precondition was not met)
```

Components/workspaces: one — the root npm project (Next.js 14.2.35, TypeScript, Prisma 6.19.3, PostgreSQL 16, Vitest 4.1.10, Playwright 1.62.1). No backend/frontend split, no other packages.

Explicit constraints observed: no push/deploy/publish, no production migration, no real credentials, no privileged commands, no bulk restore, no lockfile mutation, one reversible probe edit (not used — see Gate 4), toolchain limited to what this host provides (git, curl, jq, uv, python3.12, podman, podman-compose, pre-commit, glab, Node v18.19.1).

## 3. Glossary

| Term | Meaning |
|---|---|
| Area | One of 14 scored readiness dimensions. Each has a weight shown as `Max`. |
| Gate | One of 4 mandatory checks. A gate's result **is** its anchor area's score, not a separate number. Gates 1–3 pass only at full points. |
| Probe | Gate 4. A deliberate small defect introduced and reverted, to test whether the repository's own verification catches a real break. |
| `F-nn` | A Fix Record: one stable ID per problem, holding the finding and its fix together. |
| Priority | P0 stops unattended work and needs a human. P1 lets the agent proceed incorrectly or unvalidated. P2 costs avoidable time or clarity. |
| Owner | Who fixes it: `repo`, `agent-environment` (the agent's image or toolchain), `platform` (org or infra config), or `external-service`. |
| Readiness status | Per area: Verified (full points), Partial (half, rounded down), Repository-blocked (0), or N/A (excluded from the maximum). |
| Verification state | How the evidence was obtained: Executed, Executed (unfrozen fallback), CI-proven, Environment-blocked, Not run: unsafe, or Not applicable. |
| Level | What a fix changes: `code`, `control`, `docs`, or `instructions`. |
| Normalized score | `points earned / applicable maximum * 100`. The applicable maximum is 105 minus the weight of every N/A area, so it is rarely 100. |
| Repository blocker | The repository itself is missing, wrong, unsafe, or contradictory. Counts against readiness. |
| Environment blocker | The repository documents enough, but this audit machine lacked a tool, service, or permission. Caps confidence; never a full zero. |
| Enforced control | Something that actually fails when violated. A rule that lives only in prose is documented guidance, not an enforced control. |
| Negative control | A safety defect such as a permission bypass, allow-all policy, unguarded secret file, or committed plaintext credential. Caps area 13 at 2. |
| Unfrozen fallback | The locked install failed, so a non-mutating unlocked install was used instead. Valid evidence, but caps the setup area at half. |

Gate 3 in this audit is anchored to **Area 5 (Unit or component tests)**: the archetype is a Next.js application, and its README/`.claude/skills/verify` prescribe `npm run test` (Vitest, against the real containerized Postgres) as the mandatory step before any change is considered done — the surfaces table's "Application/service" row names exactly this role.

## 4. Readiness Scorecard

| Area | Applicability | Status | Score | Verification | Evidence / Result | Fix IDs |
|---|---|---|---:|---|---|---|
| 1. Agent guidance and navigation | Applicable | Verified | 10 | Executed (local-read) | `CLAUDE.md`, `ARCHITECTURE.md`, README, five path-scoped `.claude/rules/*.md`, two mandatory skills (`verify`, `db-migration`), 14 dated `.exadel_colleague/lessons/*.md` — coherent, cross-linked, and matched by the actual code on the traced feature (§10). | |
| 2. Reproducible environment and dependency setup (**Gate 1**) | Applicable | Partial | 5 | Executed + Environment-blocked | `npm ci` succeeded clean in 53.96s (§12). `docker compose up -d` never reached `healthy`: host port 5432 already bound by an unrelated system Postgres (§12, F-08). | F-08 |
| 3. Build, package, render, or deliverable validation (**Gate 2**) | Applicable | Verified | 10 | Executed | `npm run build` succeeded in 64.4s: compiled, typechecked, 12/12 pages generated (§12). | |
| 4. Lint, format check, typecheck, static analysis, or policy validation | Applicable | Partial | 5 | Executed | No lint surface exists at all (no ESLint config/devDependency, no `lint` script). Standalone `npx tsc --noEmit` fails with 3 errors that `next build`'s embedded typecheck does not surface (§12). | F-04, F-05 |
| 5. Unit or component tests (**Gate 3**) | Applicable | Verified | 10 | CI-proven | Pipeline 347536, job `test`, commit 71ed882: 22 files / 154 tests, all passed, 7.87s (§12). Not executable locally this run (F-08). | |
| 6. Integration, contract, or functional tests | Applicable | Verified | 5 | CI-proven | Same job/trace as area 5: 13 of the 22 files are `route.test.ts` API-route tests running against the real migrated Postgres test database, not a mocked ORM client (`.claude/rules/testing.md:10-12`). | |
| 7. Runtime, API, CLI, or local-preview validation | Applicable | Partial | 2 | CI-proven | `smoke-test:vm-stable` (job 771896) succeeded at commit 71ed882, curling `/api/health` on a freshly deployed container. This proves the deployed process and Prisma/Postgres wiring, not any business-logic runtime path — a reachable health endpoint does not prove meaningful work. | F-09 |
| 8. Browser or UI validation | Applicable | Partial | 2 | Environment-blocked | `playwright.config.ts` and 10 `e2e/*.spec.ts` files are coherent and match the app's routes, but `npm run test:e2e` needs a running dev server backed by Postgres (blocked, F-08) and this host has no Playwright browser cache (`~/.cache/ms-playwright` absent). No CI job runs it either (F-02). | F-02, F-08 |
| 9. Coverage and feedback-loop quality | Applicable | Partial | 2 | Executed (partial) | Feedback is fast and legible (154 tests / 7.87s, one line per file, §12). No coverage instrumentation exists (`@vitest/coverage-v8` absent, no `coverage` config, no script). | F-06 |
| 10. CI enforcement and parity with local validation | Applicable | Partial | 5 | Executed (local-read) + CI-proven | `test` job is real and required-by-rule for MR/`main` pushes (`.gitlab-ci.yml:51-69`), but no CI job ever runs `npm run build` or `npm run test:e2e`, and the GitLab project has `only_allow_merge_if_pipeline_succeeds: false` (verified via `glab api`, §12). | F-02, F-03 |
| 11. Safety, test isolation, artifacts, and cleanup | Applicable | Verified | 5 | CI-proven | `pretest` resets the test DB every run (`package.json:15`); dozens of consecutive green `test` pipelines (`glab ci list`, §12) show this is reliable and non-flaky, not a one-off. | |
| 12. Delivery workflow from task through review or PR | Applicable | Verified | 5 | Executed (local-read) | `git log`/`git branch -a` show a consistent `ECFD-<n>` ticket → branch → merge-commit → `.exadel_colleague/lessons/lessons_taskECFD-<n>.md` pattern across 14+ tickets. | |
| 13. Agent guardrails and permission scoping | Applicable | Partial | 7 | Executed (local-read) | See breakdown below. No negative control found. | F-03 |
| 14. Context economy | Applicable | Partial | 2 | Executed (local-read) | No file over 800 lines sits on the traced change path (§10, max 371 lines). `.env` is tracked in git while `.gitignore:30` lists it as ignored — a literal, evidence-backed contradiction an agent must reconcile before trusting `git status`. | F-01 |

**Area 13 capability breakdown:** Prevention 4/4 (`.claude/settings.json` scopes Bash to an explicit allow-list of setup/build/test commands, not a blanket allow); Observation 0/2 (no hook, audit log, or artifact-capture mechanism found); Completion 2/2 (GitLab pipeline terminal status is a tracked, unambiguous run-finished signal, verified live via `glab api`); Enforcement 1/2 (CI genuinely executes the real test suite — full credit for that half — but merge is not gated on it, F-03). **No negative control found** — no permission bypass, allow-all policy, or plaintext real credential; the committed `.env`/compose passwords are explicitly documented disposable dev-only defaults (`.env:1-3`, `docker-compose.yml:1-2`).

**Addends:** 10 + 5 + 10 + 5 + 10 + 5 + 2 + 2 + 2 + 5 + 5 + 5 + 7 + 2 = **75**. Applicable maximum 105 (no area excluded as N/A). Normalized score = round(75/105×100) = **71**.

## 5. Mandatory Gates

| Gate | Anchor | Score | Verification state | Blocking Fix IDs |
|---|---|---:|---|---|
| Gate 1 — setup | Area 2 | 5/10 (Partial) | Executed (deps) + Environment-blocked (database) | F-08 |
| Gate 2 — deliverable | Area 3 | 10/10 (Verified) | Executed | — |
| Gate 3 — verification | Area 5 | 10/10 (Verified) | CI-proven | — |
| Gate 4 — probe | — | not attempted | Not run: precondition unmet | F-08 |

Gate 3 passes at full points via a currently required CI job proven against the exact audited commit, even though the same command was blocked locally. Gate 4 was correctly not attempted per the skill's own rule: the probe requires that "the Gate 3 verification command executed in this environment," and `npm run test` could not run in this environment (F-08) — only in CI. Running the probe against the CI pipeline instead was not attempted either, since triggering a pipeline run is outside this audit's safe, local scope.

## 6. What to Fix

| ID | Priority / Owner | Problem and blocked capability | Fix and target | Verify |
|---|---|---|---|---|
| F-01 | P1 / repo | `.env` is tracked in git despite `.gitignore:30` ignoring it; the documented setup step `cp .env.example .env` (README.md:9) overwrites a tracked file, and an automated `git add -A` delivery flow could commit locally-edited env values into a merge request. | `git rm --cached .env` and commit, so the existing ignore rule actually takes effect. Target: `.env` (git index), `.gitignore`. | `git ls-files \| grep -x .env` returns nothing. |
| F-02 | P1 / repo | No CI job ever runs `npm run build` or `npm run test:e2e`; both are documented as mandatory (README.md:26-32, `.claude/skills/verify/SKILL.md`) but nothing in `.gitlab-ci.yml` enforces them — an agent that skips e2e leaves no CI trace of that gap. | Add a CI job (with a Postgres service and installed Playwright browsers) that runs `npm run build` then `npm run test:e2e`, gating the same rules as the `test` job. Target: `.gitlab-ci.yml`. | New job appears green on the next MR pipeline; `glab api projects/<group>%2Ffs-demo-project/pipelines/<id>/jobs` lists it. |
| F-03 | P1 / platform | GitLab project setting `only_allow_merge_if_pipeline_succeeds` is `false` (confirmed via `glab api projects/<group>%2Ffs-demo-project`), and no job `needs:` ties deploy jobs to `test`'s outcome — a failing unit-test run does not structurally block merge. | Enable "Pipelines must succeed" under Settings → Merge requests for this project. Target: GitLab project settings (outside the repo). | `glab api projects/<group>%2Ffs-demo-project \| jq .only_allow_merge_if_pipeline_succeeds` returns `true`. |
| F-04 | P2 / repo | No lint surface exists: no ESLint config, no ESLint devDependency, no `lint` script in `package.json`. | Add `eslint-config-next` + a flat ESLint config, and a `"lint": "next lint"` script. Target: `package.json`, new `eslint.config.mjs`. | `npm run lint` exits 0. |
| F-05 | P2 / repo | `tsconfig.json` declares no `target`, so standalone `npx tsc --noEmit` fails on `src/lib/auth.test.ts:13-14` (top-level `await`) and `src/lib/deploy-config.test.ts:148` (regex flag) — errors `next build`'s own typecheck does not raise, so the signals disagree. | Add `"target": "es2020"` (or higher) to `tsconfig.json` `compilerOptions`. Target: `tsconfig.json`. | `npx tsc --noEmit` exits 0. |
| F-06 | P2 / repo | No coverage instrumentation: no `@vitest/coverage-v8`, no `coverage` block in `vitest.config.ts`, no coverage script. | Add `@vitest/coverage-v8`, a `test.coverage` block, and a `"test:coverage"` script. Target: `package.json`, `vitest.config.ts`. | `npm run test:coverage` produces a coverage report. |
| F-07 | P2 / repo | `package.json` declares no `engines` field and there is no `.nvmrc`; only `Dockerfile:3,8,18` and `.gitlab-ci.yml:53` (both `node:20-alpine`) reveal the real Node requirement. `npm ci` on Node 18 only warns (`EBADENGINE`) rather than failing. | Add `"engines": {"node": ">=20"}` to `package.json`, and an `.nvmrc` with `20`. Target: `package.json`. | `npm ci` on Node 18 fails fast, or `node -p "require('./package.json').engines.node"` prints a value. |
| F-08 | P1 / agent-environment | This audit host cannot start the project's Postgres: `docker compose up -d` leaves the `db` container in `Created` state (`rootlessport listen tcp 0.0.0.0:5432: bind: address already in use`) because an unrelated system-level Postgres service already binds `0.0.0.0:5432`/`::1:5432`. Blocks Gate 1 at full credit and blocks Gate 4 (probe) entirely. | Ensure the host or image running the assessment reserves port 5432 exclusively (or runs each job in its own network namespace) before invoking `docker compose up -d`. Target: agent-environment provisioning, not this repository. | `ss -ltn \| grep 5432` is empty before `docker compose up -d`; `docker compose ps` then shows `db` as `healthy`. |
| F-09 | P2 / repo | The only CI-proven runtime evidence is `/api/health` (a `SELECT 1` through Prisma) — it proves the deploy and DB wiring, not that any authenticated business-logic path (quote creation, calculation, policy issuance) still works after a change. | Add a second post-deploy smoke check that logs in with a seeded demo account and hits one authenticated read endpoint (e.g. `GET /api/auto-quotes`). Target: `.gitlab-ci.yml` `smoke-test:*` jobs. | Smoke-test job output shows a `200` from the authenticated endpoint, not only from `/api/health`. |

### F-01
- **Problem:** `.env` is tracked in git even though `.gitignore:30` lists it, so the documented `cp .env.example .env` setup step silently modifies a tracked file.
- **Blocks:** Trustworthy `git status`/`git diff` during setup; risks committing local env values via an automated `git add -A` delivery flow.
- **Evidence:** `git ls-files | grep -x .env` → `.env`; `.gitignore:30` → `.env`.
- **Priority:** P1
- **Owner:** repo
- **Target:** `.env` (git index)
- **Fix:** `git rm --cached .env` and commit.
- **Verify:** `git ls-files | grep -x .env` returns nothing.
- **Level:** control

### F-02
- **Problem:** No CI job runs `npm run build` or `npm run test:e2e`, though both are documented as mandatory before a ticket is done.
- **Blocks:** CI-side proof of the deliverable build and the browser/UI validation surface (areas 3 and 8) on every change, not just the ones this audit happened to run locally.
- **Evidence:** `.gitlab-ci.yml:51-69` — the only job is `test` (`npm ci; npm run migrate:deploy; npm run test`); no `playwright` or `next build` invocation anywhere in the file.
- **Priority:** P1
- **Owner:** repo
- **Target:** `.gitlab-ci.yml`
- **Fix:** Add a job that provisions Postgres + Playwright browsers and runs `npm run build` then `npm run test:e2e`, under the same `rules:` as the `test` job.
- **Verify:** The new job shows green in `glab api projects/<group>%2Ffs-demo-project/pipelines/<id>/jobs` on the next MR pipeline.
- **Level:** control

### F-03
- **Problem:** The GitLab project does not require pipelines to succeed before merge (`only_allow_merge_if_pipeline_succeeds: false`), and no job `needs:` chains deploy/smoke-test to `test`'s result.
- **Blocks:** Structural enforcement that a broken test suite blocks delivery — an MR can merge with a red `test` job.
- **Evidence:** `glab api projects/<group>%2Ffs-demo-project` → `"only_allow_merge_if_pipeline_succeeds": false`; `.gitlab-ci.yml` has no `needs:` key anywhere.
- **Priority:** P1
- **Owner:** platform
- **Target:** GitLab project setting (Settings → Merge requests → Merge checks)
- **Fix:** Enable "Pipelines must succeed."
- **Verify:** `glab api projects/<group>%2Ffs-demo-project | jq .only_allow_merge_if_pipeline_succeeds` returns `true`.
- **Level:** control

### F-04
- **Problem:** There is no lint tooling at all — no ESLint config, no ESLint devDependency, no `lint` script.
- **Blocks:** Static-analysis feedback (unused vars, hook-rule violations, accessibility lint) that unit tests and the type checker do not cover.
- **Evidence:** `package.json:5-19` (scripts list has no `lint`); `find . -iname "*eslint*" -not -path "./node_modules/*"` returns nothing.
- **Priority:** P2
- **Owner:** repo
- **Target:** `package.json`, new `eslint.config.mjs`
- **Fix:** Add `eslint-config-next` and a flat config; add `"lint": "next lint"`.
- **Verify:** `npm run lint` exits 0.
- **Level:** code

### F-05
- **Problem:** `tsconfig.json` has no `target`, so standalone `tsc --noEmit` reports 3 errors that `next build`'s embedded typecheck does not.
- **Blocks:** A reliable, fast typecheck-only command; an agent running `tsc --noEmit` for quick feedback gets false-positive noise on files that are not actually broken.
- **Evidence:** `npx tsc --noEmit` → `src/lib/auth.test.ts(13,25): error TS1378 ...`, `src/lib/auth.test.ts(14,28): error TS1378 ...`, `src/lib/deploy-config.test.ts(148,49): error TS1501 ...`; `tsconfig.json:2-23` has no `"target"` key.
- **Priority:** P2
- **Owner:** repo
- **Target:** `tsconfig.json`
- **Fix:** Add `"target": "es2020"` (or higher) under `compilerOptions`.
- **Verify:** `npx tsc --noEmit` exits 0.
- **Level:** code

### F-06
- **Problem:** No coverage instrumentation exists for the Vitest suite.
- **Blocks:** Objective evidence of how much of `src/lib`/`src/app/api` the 154 tests actually exercise.
- **Evidence:** `vitest.config.ts:1-18` has no `coverage` block; `package.json` `devDependencies` (lines 31-43) has no `@vitest/coverage-v8`.
- **Priority:** P2
- **Owner:** repo
- **Target:** `package.json`, `vitest.config.ts`
- **Fix:** Add `@vitest/coverage-v8`, a `test.coverage` block, and a `"test:coverage"` script.
- **Verify:** `npm run test:coverage` produces a coverage report.
- **Level:** code

### F-07
- **Problem:** `package.json` declares no Node version requirement, though the Dockerfile and CI both pin `node:20-alpine`.
- **Blocks:** A newcomer or agent reading only `package.json` has no signal that Node 18 is unsupported; `npm ci` only warns (`EBADENGINE`), it does not fail, so the mismatch surfaces later as confusing Vitest/Playwright runtime errors instead of an upfront, clear message.
- **Evidence:** `Dockerfile:3,8,18` → `FROM node:20-alpine`; `.gitlab-ci.yml:53` → `image: .../node:20-alpine`; `npm ci` on this host (Node v18.19.1) → `npm WARN EBADENGINE` for `@playwright/test`, `playwright`, `playwright-core`, `rolldown`, `vite`, `vitest`.
- **Priority:** P2
- **Owner:** repo
- **Target:** `package.json`
- **Fix:** Add `"engines": {"node": ">=20"}`, and an `.nvmrc` containing `20`.
- **Verify:** `node -p "require('./package.json').engines.node"` prints a value.
- **Level:** code

### F-08
- **Problem:** This audit host's port 5432 is already bound by a pre-existing, unrelated system Postgres service, so the documented `docker compose up -d` never starts the project's `db` container.
- **Blocks:** Local execution of every DB-touching command (`npm run migrate:deploy`, `npm run test`, `npm run dev`, `npm run test:e2e`) in this run, and — as a direct consequence — the Gate 4 probe, whose precondition ("the Gate 3 verification command executed in this environment") was never met.
- **Evidence:** `docker compose up -d` → `Error: rootlessport listen tcp 0.0.0.0:5432: bind: address already in use`; `ss -ltnp | grep 5432` → `postgres` process (PID 425381, started Aug 29, unrelated to this repo) already `LISTEN`ing on `127.0.0.1:5432` and `[::1]:5432`.
- **Priority:** P1
- **Owner:** agent-environment
- **Target:** the host/image that runs Colleague against this repository (unverified exact artifact — generic provisioning requirement)
- **Fix:** Reserve port 5432 exclusively for the repo's Compose stack before invoking it (dedicated network namespace, or stop/relocate the host's own Postgres for the duration of the run).
- **Verify:** `ss -ltn | grep 5432` is empty immediately before `docker compose up -d`; `docker compose ps` then reports `db` as `healthy`.
- **Level:** control

### F-09
- **Problem:** The only CI-proven runtime evidence is `/api/health`, which proves the deploy and DB wiring but exercises no authenticated business-logic path.
- **Blocks:** Confidence that a deployed change didn't break a real user flow (quote creation, calculation, policy issuance), beyond "the process started and can reach Postgres."
- **Evidence:** `documentation/DEVOPS.md:96-99` ("Smoke tests SSH into the VM and hit `/api/health`"); `.gitlab-ci.yml:96-111` (`smoke-test:vm-stable` script curls only `/api/health`).
- **Priority:** P2
- **Owner:** repo
- **Target:** `.gitlab-ci.yml` `smoke-test:*` jobs
- **Fix:** Add a second post-deploy smoke check that logs in with a seeded demo account and hits one authenticated read endpoint (e.g. `GET /api/auto-quotes`).
- **Verify:** Smoke-test job output shows a `200` from the authenticated endpoint, not only from `/api/health`.
- **Level:** control

## 7. What Can Be Delegated Today

| Capability | Rating | Basis |
|---|---|---|
| Research (navigate, find the change point) | Yes | Area 1 Verified; feature trace in §10 reached from route to UI to test in five small, well-named files. |
| Implementation | Yes | Area 1 Verified; `.claude/rules/*.md` are path-scoped and specific (API shape, auth, testing conventions), and were followed consistently across 14+ real tickets (Area 12 Verified). |
| Testing | Partially | Area 5/6 Verified via CI-proof, not local execution this run (F-08). An agent working in an environment without the port conflict would get full local signal; on a host shaped like this one, it cannot. |
| Deliverable validation (build) | Yes | Area 3 Verified, executed directly in this audit. |
| Runtime or API validation | Partially | Area 7 Partial — CI-proven only for `/api/health`, which does not exercise business logic (F-02 covers the gap). |
| Browser validation | No | Area 8 Partial/Environment-blocked and never CI-proven (F-02, F-08) — no evidence exists in this run or in CI history that the Playwright suite currently passes. |
| Autonomous task-to-PR delivery | No | Gate 1 is Partial (not full points) and the probe was not attempted, so two of the four gates are not both cleanly "pass": per the skill's own rule, autonomous delivery rates Yes only when every gate passes, the probe succeeded, and area 13 scored prevention points above zero. Prevention is scored (4/4), but Gate 1 and Gate 4 do not meet the bar. |

## 8. What Is Already Good

- **Config-as-code regression tests are an enforced control, not just documentation.** `src/lib/deploy-config.test.ts` and `src/lib/npm-scripts.test.ts` assert properties of the `Dockerfile`, `.dockerignore`, `docker-compose.demo-vm.yml`, and every DB-touching `package.json` script (e.g. "does not hardcode `@localhost:5432`") — and these run inside the same CI-proven `test` job, so a drifting deployment config fails the build, not just a human review.
- **Path-scoped instruction files are an enforced-by-convention pattern, applied consistently.** `.claude/rules/api-design.md`, `auth.md`, `database-migrations.md`, `frontend.md`, and `testing.md` each declare a `paths:` frontmatter scope and were followed on the traced feature (§10): auth-check-first, standard `{error, field}` shape, one component per file. Documented guidance, but corroborated by matching code across the whole `src/app/api` tree, not just one example.
- **Real, reliable CI evidence, not configuration theater.** The `test` job runs `npm ci`, real migrations, and 154 real Vitest tests against a genuine `postgres:16-alpine` service container — and has done so successfully across dozens of consecutive pipelines (`glab ci list`), not a single lucky green run. Enforced control.
- **A working task-to-delivery loop with captured learning.** 14+ `ECFD-<n>` tickets each produced a branch, a merge into `main`, and a same-ticket `.exadel_colleague/lessons/lessons_taskECFD-<n>.md` — a real, repeated pattern (Area 12), not aspirational process documentation.
- **Scoped tool permissions, not a blanket allow.** `.claude/settings.json` allows exactly the setup/build/test commands the golden path needs (`docker compose up -d`, `npm install`, `npm run build`, `npm run test`, etc.) and nothing else. Enforced control (Area 13 Prevention).

## 9. Surface Resolution

| Role | Resolved command | Source | Status | Justification |
|---|---|---|---|---|
| Setup — dependencies | `npm ci` | documented (README.md:11) | Executed | Frozen install succeeded clean, 53.96s; no lockfile mutation. |
| Setup — database | `docker compose up -d` | documented (README.md:8, CLAUDE.md:22-24) | Environment-blocked | Host port 5432 conflict (F-08); substitute (host's ambient Postgres) deliberately not used — it is a shared, non-disposable instance outside this audit's control, and using it would change the intended workflow rather than execute it. |
| Deliverable (Gate 2) | `npm run build` | documented (README.md:31) | Executed | Compiled, typechecked, 12/12 pages generated, 64.4s. |
| Primary verification (Gate 3) | `npm run test` | documented (README.md:29, `.claude/skills/verify/SKILL.md`) | CI-proven | Local run blocked by F-08; pipeline 347536 job `test` at commit 71ed882 ran it and passed (154/154). |
| Lint / static analysis | none documented; substitute `npx tsc --noEmit` | inferred | Executed | No `lint` script exists (F-04); standalone tsc surfaces a real tsconfig gap (F-05) that `next build`'s embedded check does not. |
| Integration tests | same `npm run test` invocation, `route.test.ts` subset | documented (`.claude/rules/testing.md:10-12`) | CI-proven | Same trace as primary verification; 13 of 22 files are route-level tests against the real test DB. |
| Runtime/API validation | `curl http://localhost:$PORT/api/health` | documented (`documentation/DEVOPS.md:96-99,104-111`) | CI-proven | `smoke-test:vm-stable` job succeeded at the audited commit; proves deploy + DB wiring only. |
| Browser/UI validation | `npm run test:e2e` | documented (README.md:30, verify skill) | Not run: environment-blocked | Needs the blocked local dev server + DB (F-08); no Playwright browser cache on this host either; no CI substitute exists (F-02). |
| Coverage | none documented; substitute `vitest run --coverage` | inferred | Not run: missing dependency | `@vitest/coverage-v8` is not installed; installing it ad hoc would mutate resolved dependencies beyond the sanctioned unfrozen-fallback scope, so it was not attempted (F-06). |
| CI enforcement | `.gitlab-ci.yml` `test` job; `glab api projects/<group>%2Ffs-demo-project` | documented (`.gitlab-ci.yml:51-69`) | Executed (local-read) + CI-proven | Confirmed the job's rules, and separately confirmed via the GitLab API that merge is not gated on pipeline success (F-03). |
| Probe (Gate 4) | — | — | Not attempted | Precondition ("Gate 3 verification command executed in this environment") unmet; see F-08. |

## 10. Golden Path

Clean-checkout route as documented (README.md, CLAUDE.md, `.claude/skills/verify/SKILL.md`): `cp .env.example .env` → `docker compose up -d` (wait for `db` healthy) → `npm install` → `npm run migrate:deploy` → `npm run db:seed` (or `db:reset`) → then, per change, `npm run test` → `npm run test:e2e` → `npm run build` → open a merge request. `DB_HOST` is the one environment-specific knob (defaults to `localhost`; set to the Docker bridge gateway IP when the app/tests run inside a container), and the verify skill is explicit that `CI` must never be set locally or Playwright double-starts the dev server.

**Representative feature trace** — "calculate an automobile quote's premium," picked because it touches every layer:
- Entry point: `src/app/api/auto-quotes/[id]/calculate/route.ts` (26 lines) — auth check first, delegates immediately, standard `{error, field}` shape, matching `.claude/rules/api-design.md`.
- Business logic: `src/lib/auto-quote-service.ts` (222 lines, persistence/orchestration) calling `src/lib/auto-quote.ts` (102 lines, pure premium-calculation rules).
- Persistence: `prisma/schema.prisma` `AutoQuote`/`Vehicle`/`AutoPolicy` models, applied through the migrations under `prisma/migrations/`.
- UI: `src/app/auto-quotes/[id]/page.tsx` (113 lines) renders the calculated result.
- Tests: `src/app/api/auto-quotes/[id]/calculate/route.test.ts` (route-level, real DB) and `src/lib/auto-quote.test.ts` (166 lines, pure-function unit tests) plus `e2e/auto-premium-rules.spec.ts` (148 lines, browser-level).

A newcomer (or agent) can find the equivalent set of files for a new line-of-business rule change by following this exact naming/layout pattern — nothing in this trace required guessing at conventions or cross-referencing undocumented structure.

## 11. Probe

Not attempted. The skill's rule is explicit: run the probe only when "the Gate 3 verification command executed in this environment — pass or fail." `npm run test` could not execute in this environment because its `pretest` hook requires a live, migrated Postgres test database, and the documented way to provide one (`docker compose up -d`) is blocked by F-08 (host port 5432 already bound by an unrelated system service). Gate 3 was instead satisfied by CI-proof (§5), which the skill treats as valid "Verified" evidence for scoring — but CI-proof is not "executed in this environment," so the probe's precondition was not met and no substitute was run in its place. Blocking Fix Record: **F-08**.

## 12. Commands Executed

| Command | Directory | Source / Safety Class | Purpose | Result | Notes / Artifacts |
|---|---|---|---|---|---|
| `git status --short`, `git log -1`, `git stash list` | repo root | local-read | Baseline | Clean tree at 71ed882; one untouched unrelated stash | |
| `find . -iname backend -o -iname frontend -o -iname conftest.py -o -iname pytest.ini -o -iname main.py` | repo root | local-read | Confirm repo layout | No matches — no backend/frontend split exists | |
| `npm ci` | repo root | local-build, documented | Frozen dependency install | Success, 192 packages, 53.96s; `EBADENGINE` warnings for playwright/vitest/vite/rolldown (need Node ≥20) | F-07 |
| `npx prisma generate` | repo root | local-build, documented (Dockerfile:15) | Generate Prisma client | Success, 3.16s | |
| `docker compose up -d` | repo root | local-build, documented | Start Postgres | Failed: `rootlessport listen tcp 0.0.0.0:5432: bind: address already in use` | Created container/volume/network removed afterward (`podman rm -f`, `podman volume rm`, `podman network rm`) |
| `ss -ltnp \| grep 5432`, `ps aux \| grep postgres`, `systemctl status postgresql` | host | local-read | Diagnose port conflict | Unrelated system Postgres (PID 425381, since Aug 29) owns the port | F-08 |
| `PGPASSWORD=*** psql -h localhost -U postgres -d postgres -c "\l"` | host | local-read | Confirm no `insurance_quoting*` database exists on the ambient server (so it was never used as a substitute) | No matching rows | Read-only; no writes made to this unrelated server |
| `npm run build` | repo root | local-build, documented | Deliverable build (Gate 2) | Success, 64.38s, 12/12 pages | `.next/` (gitignored) |
| `npx tsc --noEmit` | repo root | local-build, inferred | Typecheck (Area 4) | 3 errors (`auth.test.ts:13,14`, `deploy-config.test.ts:148`), 7.64s | F-05; `tsconfig.tsbuildinfo` created then deleted |
| `npm audit --omit=dev` | repo root | local-read | Dependency vulnerability check | 5 high-severity advisories against `next@14.2.35`/bundled `postcss` | Informational; not scored as its own area |
| `glab ci status --branch main`; `glab api .../repository/commits/<sha>/statuses`; `glab api .../jobs/<id>/trace` | repo root | external-read (the repository's own GitLab host) | CI-proof for Gates 3, and areas 6/7/10/11 | Pipeline 347536 (commit 71ed882): `test`, `deploy:vm-stable`, `smoke-test:vm-stable` all `success`; trace shows 22 files / 154 tests passed | |
| `glab api projects/<group>%2Ffs-demo-project` \| `jq` | repo root | external-read | Confirm merge-gate setting | `only_allow_merge_if_pipeline_succeeds: false` | F-03 |
| `git ls-files \| grep -x .env`; `git check-ignore -v .env` | repo root | local-read | Confirm tracked-vs-ignored contradiction | `.env` is tracked; `check-ignore` returns nothing (git doesn't ignore a file already tracked) | F-01 |
| `find src prisma e2e -name "*.ts" -o -name "*.tsx" \| xargs wc -l \| sort -rn` | repo root | local-read | Context economy scan (Area 14) | Largest file 371 lines; nothing near 800 | |
| `git status --short --ignored` | repo root | local-read | Confirm final worktree | Only expected gitignored build byproducts (`node_modules/`, `.next/`, `next-env.d.ts`); no tracked changes | |
| Refused: `docker compose up -d` retried against the ambient (non-project) Postgres instance | — | would-be external-write against unowned infrastructure | — | Not run | Would have created a persistent database on a shared host service outside this audit's control; recorded as a blocker (F-08) instead |

## 13. Confidence and Limits

Confidence is **Medium**, matching the skill's own definition for this exact shape of result: full scope was audited (there is only one component, and every file under it was in scope), Gate 3 is CI-proven at full points, and the one gate that fell short — Gate 1 — is environment-blocked with coherent, well-documented repository evidence (the docker-compose config, credentials, and healthcheck are all correct; the failure is a pre-existing, unrelated service on this specific host). That is the literal Medium criterion, not the High one (which requires every gate executed or CI-proven — Gate 1 was not) and not Low (which requires either unproven gates without a coherent explanation, or unaudited scope — neither applies here).

The one real limitation this leaves unresolved is the probe (Gate 4). Because Gate 3 was never executed locally, the skill's rule for running the probe was correctly not satisfied, and no defect-injection-and-catch cycle was exercised in this run. CI history is a strong proxy — 154 passing tests across dozens of consecutive green pipelines is not a lucky fluke — but it is proof that the suite currently passes, not proof that it would catch a newly introduced regression with a legible, well-located failure message. That specific claim (locatability, loop cost, signal quality of a real failure) remains unverified pending a run on a host where port 5432 is free.

Everything else scored in this report rests on evidence actually produced in this run (local execution, the GitLab API, or `git`/filesystem inspection) — nothing here was inferred from configuration alone. Unverified items, their classification, and the conclusion each leaves uncertain:

- `docker compose up -d` / local Postgres — Environment-blocked (F-08). Leaves Gate 1 at half credit and Gate 4 unattempted (see above).
- `npm run test:e2e` (Playwright) — Environment-blocked (F-08, compounded by no local browser cache) and never CI-proven (F-02). Leaves Area 8 unverified beyond "the config and specs look coherent."
- Coverage (`vitest run --coverage`) — Not run: the dependency it needs is not installed, and installing it would mutate resolved dependencies beyond the sanctioned scope (F-06). Leaves Area 9's "how much is actually covered" question open; only feedback-loop speed was verified.
- ESLint — Not run: there is nothing to run (F-04). Leaves Area 4's static-analysis half of the score resting entirely on the typecheck evidence.
