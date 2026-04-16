# IDE Panel Contract V1 2026-03-19

## Purpose

This document defines the first minimal IDE panel contract for the current CLI-first AIL system.

It exists to answer four practical questions:

1. what the first IDE panel should show
2. which CLI JSON payloads should feed it
3. which actions the panel may safely trigger in v1
4. what the panel must not try to own yet

Use this together with:

- `/Users/carwynmac/ai-cl/IDE_CONSUMPTION_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/docs/AIL_IDE_SYNC_IMPLEMENTATION_CHECKLIST.md`
- `/Users/carwynmac/ai-cl/SECONDARY_SURFACE_STRATEGY_20260319.md`
- `/Users/carwynmac/ai-cl/PROJECT_CONTEXT.md`

## Panel Goal

The first IDE panel should not try to be a full IDE product surface.

Its goal is much narrower:

- show the current project state
- show the current preview handoff
- show the current release/readiness summary
- expose one or two safe actions that already exist in CLI

This makes the panel a consumption-first surface rather than a second control plane.

## Recommended First Panel Name

Recommended internal name:

- `AIL Workbench`

Recommended visible sections:

1. Project
2. Preview
3. Release
4. Actions

## Panel Data Sources

The panel should consume only existing authoritative JSON outputs.

### Project Section Source

Primary source:

- `python3 -m cli project summary --json`

Required fields to consume:

- `status`
- `project_root`
- `source_of_truth`
- `manifest`
- `last_build`
- `cloud_status`
- `recommended_primary_action`
- `recommended_primary_command`
- `recommended_primary_reason`

### Preview Section Source

Primary source:

- `python3 -m cli project preview --json`

Required fields to consume:

- `preview_handoff.primary_target`
- `preview_handoff.open_targets`
- `preview_handoff.preview_hint`
- `preview_handoff.next_steps`
- `latest_build_id`
- `latest_artifact_id`
- `latest_artifact_local_path`

Optional deep inspection source:

- `python3 -m cli project inspect-target --json`

Use this only when the user explicitly expands or selects a target.

### Release Section Source

Primary source:

- `python3 -m cli rc-check --json`

Required fields to consume:

- `status`
- `rc.status`
- `readiness.status`
- `benchmark.release_baseline_ok`
- `latest_trial_batch.status`
- `recommended_release_action`
- `recommended_release_command`
- `recommended_release_reason`

### Workspace Summary Fallback

If the current directory is not an initialized project, the panel should fall back to:

- `python3 -m cli workspace summary --json`

Required fields to consume:

- `status`
- `product_surface`
- `readiness`
- `rc`
- `latest_trial_batch`
- `recommended_workspace_action`
- `recommended_workspace_command`
- `recommended_workspace_reason`

## Panel Layout Contract

### 1. Project Section

The first block should answer:

- what project am I in
- is it healthy
- what is the default next project action

Minimum display contract:

- project root path
- source of truth path
- latest build presence
- doctor or project status summary
- one-line default action reason

### 2. Preview Section

The second block should answer:

- what should I inspect first
- what artifact or generated surface exists now
- which target should open next

Minimum display contract:

- preview hint
- primary preview target label
- up to 5 open targets
- artifact local path when present

### 3. Release Section

The third block should answer:

- is the current system green enough for the supported surface
- what does the RC or readiness layer recommend next

Minimum display contract:

- RC status
- readiness status
- frozen baseline status
- latest trial batch status
- one-line release recommendation

### 4. Actions Section

The fourth block should expose only safe, already-stabilized actions.

Recommended first action buttons:

- `Project Go`
  - runs `python3 -m cli project go --json`
- `Project Preview`
  - runs `python3 -m cli project preview --json`
- `RC Check Refresh`
  - runs `python3 -m cli rc-check --refresh --json`

If the panel is in workspace fallback mode, replace `Project Go` with:

- `Workspace Go`
  - runs `python3 -m cli workspace go --json`

## Recommended V1 Interaction Rules

### Rule 1. Read first, act second

The panel should load summary and preview data before offering actions.

### Rule 2. No hidden auto-fix behavior

The panel should not silently execute recovery logic on load.

### Rule 3. Open-target and inspect-target are explicit interactions

Target resolution and inspection should happen only when the user asks for more detail.

### Rule 4. Preserve CLI terminology

Use the same labels and meanings already present in CLI payloads whenever possible.

Examples:

- `recommended_primary_action`
- `preview_handoff`
- `doctor_status`
- `route_taken`

This keeps the panel aligned with the system's existing action language.

## V1 Non-Goals

The first IDE panel should not try to do the following:

- define new recovery semantics
- define new release semantics
- replace sync conflict UX with a custom protocol
- make `app_min` look like a supported product surface
- become a fully custom compile orchestrator
- replace CLI as the system of record

## Suggested Minimal API Mapping

### Initial Load In Project Context

1. run `project summary --json`
2. run `project preview --json`
3. run `rc-check --json`

### Initial Load Outside Project Context

1. run `workspace summary --json`
2. run `workspace preview --json`
3. run `rc-check --json`

### On Action Trigger

- `Project Go` -> `project go --json`
- `Workspace Go` -> `workspace go --json`
- `Project Preview` -> `project preview --json`
- `RC Check Refresh` -> `rc-check --refresh --json`

### On Target Expansion

1. run `project open-target <label> --json`
2. optionally run `project inspect-target <label> --json`

## Recommended V1 Success Criteria

The first IDE panel should be considered successful if it can do all of the following without introducing new product semantics:

- correctly distinguish project context from workspace context
- show one coherent project or workspace summary
- show one coherent preview handoff
- show one coherent RC or readiness summary
- trigger safe existing actions
- avoid contradicting CLI language or product boundaries

## Recommended Internal Positioning

The safest accurate way to describe this panel is:

- a thin IDE workbench over the current CLI-first system
- a convenience surface for reading and triggering stable actions
- not a new workflow authority

## Internal Development Implication

This contract implies:

- the first IDE panel should be built from existing CLI JSON outputs
- panel evolution should follow existing CLI/workbench semantics
- any panel feature that needs new truth should be deferred until later

In short:

- summarize first
- preview second
- release third
- trigger safe actions fourth
- avoid inventing a second product model
