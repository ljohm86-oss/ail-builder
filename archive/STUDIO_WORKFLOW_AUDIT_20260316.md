# Studio Workflow Audit 2026-03-16

## Purpose

This document records a focused audit of the retained Studio workstream in `/Users/carwynmac/ai-cl`.

Scope:

- `/Users/carwynmac/ai-cl/ail-studio-proxy.py`
- `/Users/carwynmac/ai-cl/ail-studio-web/`

The goal of this audit is not to archive or remove these paths.

The goal is to answer:

- what the Studio workstream currently is
- whether it still looks runnable
- why it was intentionally not moved during cleanup
- what should happen before any future Studio cleanup

## Summary

Current judgment:

- the Studio code path should remain in place
- it still looks like a coherent retained side workflow
- top-level Studio docs were archived, but Studio runtime code was intentionally kept

Reason:

- `ail-studio-web/` still contains a structured frontend app
- `ail-studio-proxy.py` still provides a matching runtime service layer
- the frontend and proxy are wired together through concrete endpoints
- Playwright E2E tests still exist for the Studio UI

This is enough evidence to treat Studio as a retained side workflow, not as dead top-level clutter.

## Components Audited

### 1. Proxy Service

Path:

- `/Users/carwynmac/ai-cl/ail-studio-proxy.py`

Observed role:

- Flask service
- manages project runners under `/Users/carwynmac/ai-cl/output_projects`
- exposes run/status/stop-style endpoints
- streams process logs through SSE

Key observations from code:

- `BASE_PROJECTS_ROOT = Path("/Users/carwynmac/ai-cl/output_projects").resolve()`
- validates `project_root` to stay inside `output_projects`
- expects `start.sh` in generated project roots
- tracks running processes and log tails
- supports stop/stop-all/status/stream-style behavior

Interpretation:

- this is not just an abandoned utility file
- it is a runtime support service for preview/run behavior

### 2. Studio Frontend

Path:

- `/Users/carwynmac/ai-cl/ail-studio-web/`

Observed role:

- Vue 3 + Vite frontend
- local session state UI
- generate/compile actions
- run panel integration
- preview URL handling

Package signals:

- `dev`
- `build`
- `preview`
- `test:e2e`

Interpretation:

- this is a structured app, not a loose experiment directory

### 3. Frontend-to-Service Wiring

Observed frontend endpoints:

- `/mothership/generate_ail`
- `/mothership/compile`
- `/proxy`

Observed Vite proxy config:

- `/mothership` -> `http://127.0.0.1:5002`
- `/proxy` -> `http://127.0.0.1:5050`

Interpretation:

- the Studio web app is explicitly wired to:
  - current AIL mothership compile service
  - local run/proxy service
- this is concrete implementation wiring, not stale commentary

## Evidence of Ongoing Workflow Structure

### Frontend Runtime State

Observed in `/Users/carwynmac/ai-cl/ail-studio-web/src/App.vue`:

- local session persistence
- compile card state
- run status state
- frontend/backend URL handling
- preview reset guard

Interpretation:

- the frontend has a meaningful interactive flow around generate -> compile -> run -> preview

### E2E Test Presence

Observed test file:

- `/Users/carwynmac/ai-cl/ail-studio-web/tests/run-panel.spec.ts`

Observed test coverage:

- compile card presence
- run state transitions
- detect flow
- URL copy behavior
- stop behavior
- log controls
- preview reset safety guard

Interpretation:

- the Studio path was tested as a real workflow, not just sketched

## Why Top-Level Studio Docs Were Archived But Code Was Kept

Archived docs:

- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_ARCH_GUARD.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_BETA_GATE.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_BETA_RUNBOOK.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_FREEZE_LINE.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_WEB_RULES.md`

Reason those docs were movable:

- they were top-level planning/runbook documents
- they had no active references from mainline docs, testing, benchmark, CLI, skills, or language paths

Reason Studio code was not movable:

- the frontend and proxy still form a coherent coupled runtime path
- the path still has configuration, runtime state handling, and tests
- moving it without a dedicated migration plan would be high-risk

## Current Risk Assessment

### Low Risk Actions

- keep Studio code where it is
- keep Studio listed as a retained side workflow
- archive only detached top-level Studio notes

### Higher Risk Actions

Do not do these casually:

- move `/Users/carwynmac/ai-cl/ail-studio-proxy.py`
- move `/Users/carwynmac/ai-cl/ail-studio-web/`
- remove Studio tests without replacement
- change proxy target assumptions without auditing the frontend

## Recommended Next Audit Before Any Studio Cleanup

Before moving or deprecating Studio code, answer these questions explicitly:

1. Is Studio still expected to be runnable by the team?
2. Is Studio still a supported side workflow, or only historical?
3. Should Studio remain in this repository, or move to its own workspace?
4. Are committed frontend build artifacts inside `ail-studio-web/` still needed?
5. Are committed dependencies inside `ail-studio-web/node_modules/` intentional, or just residue?

Additional findings from this pass:

- `ail-studio-web/node_modules/` is large, about `100M`
- `package.json` and `package-lock.json` are present
- no `.gitignore` was found inside `ail-studio-web/`
- no active external references were found from current mainline docs, testing, benchmark, CLI, skills, or language paths to the absolute `ail-studio-web/node_modules` path

Interpretation:

- `node_modules/` does not look like a current mainline dependency
- but moving it would change the Studio side workflow from "immediately runnable if deps are already present" to "requires reinstall"
- that is a side-workflow policy choice, not just cleanup

## Suggested Future Studio-Specific Cleanup Scope

This cleanup pass already moved the lowest-risk generated Studio artifacts to:

- `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/studio_web_generated/dist/`
- `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/studio_web_generated/test-results/`

If a future Studio cleanup is desired, audit these next:

- `/Users/carwynmac/ai-cl/ail-studio-web/node_modules/`
- committed dependency state and offline expectations

Why these are better candidates than the Studio source itself:

- they are more likely to be generated artifacts
- they are less likely to define workflow ownership
- cleaning them would be less disruptive than moving the Studio runtime path

## Current Recommendation

Treat the Studio code path as:

- retained
- separate from the active mainline
- not yet ready for archive movement

Treat `ail-studio-web/node_modules/` as:

- non-mainline
- likely generated dependency state
- not yet safe to move without an explicit decision on Studio offline runnability

If future cleanup continues, Studio should get a dedicated cleanup pass rather than being mixed into generic top-level cleanup.
