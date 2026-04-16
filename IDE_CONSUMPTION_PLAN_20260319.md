# IDE Consumption Plan 2026-03-19

## Purpose

This document defines how IDE integration should consume the current CLI-first AIL system without creating a parallel product truth.

It exists to answer four practical questions:

1. what the IDE should consume first
2. which existing CLI and cloud surfaces should be treated as authoritative
3. what the IDE should explicitly avoid doing in the near term
4. what a realistic phased IDE rollout should look like

Use this together with:

- `/Users/carwynmac/ai-cl/docs/AIL_IDE_SYNC_IMPLEMENTATION_CHECKLIST.md`
- `/Users/carwynmac/ai-cl/SECONDARY_SURFACE_STRATEGY_20260319.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/APP_MIN_STRATEGY_REVIEW_20260319.md`

## Current IDE Position

The IDE is not the mainline product surface today.

The IDE should currently be treated as:

- a downstream integration layer
- a consumer of stable CLI and cloud semantics
- a convenience surface for the current website-oriented frozen product line

The IDE should not currently be treated as:

- a competing workflow authority
- a replacement for the CLI workbench
- the place where recovery or release semantics are first invented

## Authority Model

The authoritative semantics should remain in the following order:

1. cloud API contracts
2. CLI JSON outputs
3. RC and readiness aggregates
4. IDE presentation and UX

That means the IDE should consume truth from the system in that direction.

It should not invert the dependency and invent new control semantics first.

## What The IDE Should Consume First

### 1. Trial entry outputs

The IDE should be able to consume:

- `python3 -m cli trial-run --json`

This provides:

- frozen-profile first-user flow
- cloud status
- preview handoff
- default next action
- canonical route identity

This is the cleanest way for an IDE to expose a guided first success path without redefining the system.

### 2. Project workbench outputs

The IDE should consume:

- `python3 -m cli project summary --json`
- `python3 -m cli project preview --json`
- `python3 -m cli project check --json`
- `python3 -m cli project doctor --fix-plan --json`
- `python3 -m cli project go --json`

These commands already capture the stabilized project-level action model:

- overview
- preview handoff
- health check
- diagnosis and recovery planning
- recommended execution path

### 3. Workspace workbench outputs

The IDE should consume:

- `python3 -m cli workspace status --json`
- `python3 -m cli workspace summary --json`
- `python3 -m cli workspace preview --json`
- `python3 -m cli workspace doctor --json`
- `python3 -m cli workspace continue --json`
- `python3 -m cli workspace go --json`

These commands already capture the workspace-level control surface.

They are the right source for IDE-wide overview and operator-facing workspace actions.

### 4. RC and readiness outputs

The IDE should consume:

- `python3 -m cli rc-check --json`
- `python3 -m cli rc-check --refresh --json`
- `/Users/carwynmac/ai-cl/testing/results/readiness_snapshot.json`
- `/Users/carwynmac/ai-cl/testing/results/rc_checks_results.json`

These provide the current release-facing truth and should be used for:

- release health display
- operator confidence signals
- escalation recommendations

### 5. Preview and target inspection outputs

The IDE should consume:

- `python3 -m cli build artifact <build_id> --json`
- `python3 -m cli cloud status --json`
- `python3 -m cli project open-target --json`
- `python3 -m cli project inspect-target --json`
- `python3 -m cli workspace open-target --json`

These already define how the system talks about:

- what to inspect first
- which artifact or directory matters
- which concrete file or folder should be opened next

## What The IDE Should Reuse Directly

The IDE should directly reuse these stabilized concepts instead of inventing replacements:

- `preview_handoff`
- `preview_hint`
- `open_targets`
- `recommended_primary_action`
- `recommended_primary_command`
- `recommended_primary_reason`
- `route_taken`
- `route_reason`
- `doctor_status`
- `recommended_action`

These fields now appear repeatedly across trial, project, workspace, and release surfaces.

That repetition is a feature. It means the IDE can build one coherent action model on top of them.

## What The IDE Should Not Do Yet

### 1. Do not invent a second workflow model

The IDE should not create its own independent notions of:

- what the primary action is
- what recovery means
- when sync is safe
- when release is acceptable

Those semantics already exist.

### 2. Do not make `app_min` look productized

The IDE should not visually position `app_min` as equal to the frozen website-oriented surfaces.

Current safe truth remains:

- website generation is supported
- application generation remains experimental

### 3. Do not bypass managed-zone and sync discipline

The IDE must continue to obey the AIL-managed ownership model documented in:

- `/Users/carwynmac/ai-cl/docs/AIL_IDE_SYNC_IMPLEMENTATION_CHECKLIST.md`

Especially:

- AIL remains the source of truth
- sync only writes managed zones
- conflict handling remains explicit

### 4. Do not become the first place where release truth is interpreted

The IDE should display RC and readiness outputs.

It should not redefine them.

## Recommended Phased Rollout

### Phase 1. Read-only IDE workbench consumption

Goal:

- make the IDE a high-quality viewer of the current system

Focus:

- surface `project summary`
- surface `project preview`
- surface `workspace summary`
- surface `rc-check`
- surface preview targets and inspection payloads

This phase is intentionally light-risk because it consumes already-stable JSON.

### Phase 2. Guided action triggers

Goal:

- let the IDE trigger stabilized CLI actions

Focus:

- trigger `project go`
- trigger `project doctor --fix-plan`
- trigger `workspace go`
- trigger `rc-check --refresh`

This phase still keeps workflow truth inside CLI, while making the IDE more useful.

### Phase 3. Sync and conflict UX packaging

Goal:

- package the existing sync and conflict semantics into stronger IDE UX

Focus:

- managed-zone decorations
- conflict summary display
- manifest-based sync preview
- explicit overwrite / backup / cancel choices

This phase should still follow the existing sync checklist rather than redefining it.

### Phase 4. Candidate promotion review

Only after the previous phases are stable should we ask whether the IDE deserves partial promotion from secondary surface toward a stronger product role.

That review should ask:

- is it smoke-guarded enough
- is it trial-guarded enough
- is it clearer than CLI for real users
- does it still preserve the same boundary truth

## Recommended Near-Term IDE Deliverables

The highest-value near-term IDE deliverables are:

1. a project summary panel driven by `project summary --json`
2. a preview panel driven by `project preview --json` and `project inspect-target --json`
3. a workspace overview panel driven by `workspace summary --json`
4. a release panel driven by `rc-check --json`
5. safe action buttons that trigger `project go` or `workspace go`

These are strong because they use the product truth that already exists.

## Explicit Non-Goals For The Near Term

Do not make these the near-term IDE priority:

- full custom IDE-native compile semantics
- full app-oriented UX centered on `app_min`
- code-to-AIL reverse sync
- alternative recovery semantics
- replacing CLI as the release authority

## Recommended Current Positioning

The safest accurate internal statement today is:

- CLI defines the truth
- IDE consumes and packages the truth
- IDE promotion can happen later if the packaged experience proves clearer without changing the product boundary

## Internal Development Implication

This plan implies:

- the next IDE work should be consumption-first, not reinvention-first
- every IDE milestone should map to an already-stable CLI or cloud surface
- any IDE work that needs new product truth should be treated as premature for now

In short:

- consume stable JSON first
- trigger stable actions second
- package sync and preview third
- discuss promotion only after the IDE proves it reduces friction without introducing ambiguity
