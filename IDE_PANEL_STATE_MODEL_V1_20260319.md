# IDE Panel State Model V1 2026-03-19

## Purpose

This document defines the first stable state model for the initial IDE panel built on top of the CLI-first AIL system.

It exists to answer four practical questions:

1. which states the panel may enter
2. what each state means
3. which CLI fields should drive each state
4. how the panel should behave in each state without inventing new semantics

Use this together with:

- `/Users/carwynmac/ai-cl/IDE_PANEL_CONTRACT_V1_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_CONSUMPTION_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/SECONDARY_SURFACE_STRATEGY_20260319.md`
- `/Users/carwynmac/ai-cl/PROJECT_CONTEXT.md`

## State Philosophy

The IDE panel should not invent its own abstract state machine.

Instead, it should map the existing CLI and aggregate semantics into a small stable UI state model.

The goal is:

- fewer panel states
- stronger alignment with CLI truth
- less room for IDE-only ambiguity

## Canonical Panel States

The first IDE panel should use these five states:

1. `loading`
2. `ok`
3. `warning`
4. `conflict`
5. `attention`

These are intentionally narrow.

They are sufficient for the current CLI-first system because the underlying semantics already exist in:

- project workbench outputs
- workspace workbench outputs
- RC and readiness outputs
- preview and inspection outputs

## State Definitions

### 1. `loading`

Meaning:

- the panel is still collecting authoritative JSON inputs
- no stable user-facing interpretation should be shown yet

Use when:

- initial panel hydration is in progress
- a refresh action is still running
- one or more required upstream payloads are not yet available

Typical sources involved:

- `project summary --json`
- `project preview --json`
- `rc-check --json`
- or workspace fallbacks

### 2. `ok`

Meaning:

- the current project or workspace is healthy enough for the supported surface
- the user can follow the recommended main action without first resolving a blocker

Use when most of the following are true:

- project or workspace summary status is healthy
- doctor status is `ok` or equivalent healthy recommendation
- no managed-zone conflict is active
- RC and readiness are not signaling immediate attention for the supported surface

Typical examples:

- healthy frozen-profile project with a valid build and preview handoff
- healthy workspace on the frozen supported surface

### 3. `warning`

Meaning:

- the current context is usable, but there is something non-blocking the user should notice

Use when:

- the panel can still recommend a next action
- no hard conflict exists
- no immediate release-blocking attention is required
- but one or more useful signals are weaker than ideal

Typical examples:

- preview artifact exists but build metadata is incomplete
- workspace is healthy but release recommendation is not yet fully refreshed
- a fallback path was used, but the workflow still succeeded

### 4. `conflict`

Meaning:

- the user must explicitly resolve a managed-zone or sync-related conflict before a safe continue path is possible

Use when:

- project check reports `conflict`
- doctor recommends explicit conflict resolution
- sync safety is blocked by local drift in managed files

Typical examples:

- generated file drift conflicts with incoming managed writes
- overwrite or backup decision is required

This state is stronger than `warning` and should visually block the default continue action.

### 5. `attention`

Meaning:

- the panel does not have a clean healthy path and should steer the user to review, diagnose, or refresh before normal continuation

Use when:

- doctor status is not healthy and not just conflict
- RC or readiness is not green enough for the supported surface
- required project structure is missing
- authoritative inputs are stale or incomplete in a way that affects safe interpretation

Typical examples:

- source is not compile-ready
- project structure is incomplete
- workspace-level release summary is not healthy enough to recommend direct execution

This is the broadest non-healthy state.

## State Mapping Rules

### Project Context Mapping

Primary inputs:

- `project summary --json`
- `project preview --json`
- `project check --json`
- `project doctor --fix-plan --json`
- `rc-check --json`

Recommended mapping:

- `conflict`
  - if `project check.status = conflict`
  - or `doctor_status` implies explicit conflict resolution

- `attention`
  - if `project check.status = error`
  - or `doctor_status = validation_failed`
  - or `recommended_action` requires repair before normal continuation
  - or release-facing context is not healthy enough to recommend normal execution

- `warning`
  - if project is usable but some non-blocking support signal is degraded
  - and no conflict or attention rule matched

- `ok`
  - if project is healthy, preview handoff exists, and the recommended primary action is a normal continue path

### Workspace Context Mapping

Primary inputs:

- `workspace summary --json`
- `workspace preview --json`
- `workspace doctor --json`
- `rc-check --json`

Recommended mapping:

- `attention`
  - if workspace doctor recommends release or readiness recovery
  - or RC/readiness are not healthy enough for the supported surface

- `warning`
  - if workspace is usable but some release-facing signal is stale, incomplete, or not ideal
  - and no attention rule matched

- `ok`
  - if workspace summary, workspace doctor, and RC/release signals all support the current recommended workspace action

Workspace-level `conflict` should only be used if a delegated project-level conflict is explicitly surfaced.

Otherwise workspace non-health should map to `attention`, not `conflict`.

## Required Source Fields

The panel state model should rely on these fields first:

From `project summary --json`:

- `status`
- `recommended_primary_action`
- `recommended_primary_reason`
- `doctor_status`

From `project check --json`:

- `status`
- `ready_for_compile_sync`
- `ready_for_sync`
- `conflicts`

From `project doctor --fix-plan --json`:

- `status`
- `doctor_status`
- `recommended_action`
- `fix_plan.mode`

From `workspace summary --json`:

- `status`
- `recommended_workspace_action`
- `recommended_workspace_reason`

From `workspace doctor --json`:

- `status`
- `route_taken`
- `recommended_workspace_action`

From `rc-check --json`:

- `status`
- `rc.status`
- `readiness.status`
- `recommended_release_action`
- `recommended_release_reason`

## UI Behavior By State

### `loading`

Panel behavior:

- show skeleton or explicit loading treatment
- disable all action buttons except cancel if supported
- do not show fallback guesses as settled truth

### `ok`

Panel behavior:

- highlight the recommended main action
- show preview handoff prominently
- allow safe action buttons

Recommended emphasis:

- `Project Go`
- `Workspace Go`
- `Project Preview`

### `warning`

Panel behavior:

- still allow normal safe actions
- add one-line explanation of what is weaker than ideal
- do not visually escalate to a blocking error

Recommended emphasis:

- show the next step
- show the warning reason directly under the summary header

### `conflict`

Panel behavior:

- suppress the default continue action as the primary CTA
- elevate conflict explanation and explicit recovery path
- point to project doctor or conflict-resolution action

Recommended emphasis:

- `Project Doctor`
- sync conflict explanation
- backup / overwrite / cancel choices when available later

### `attention`

Panel behavior:

- elevate the recovery or review action over normal continue
- explain why the panel is not currently in a healthy path
- avoid presenting the current context as ready for routine continuation

Recommended emphasis:

- `Project Doctor --fix-plan`
- `RC Check Refresh`
- `Workspace Doctor`

## State Priority

When multiple signals disagree, use this priority order:

1. `loading`
2. `conflict`
3. `attention`
4. `warning`
5. `ok`

Interpretation:

- if a hard conflict exists, do not downgrade it into warning
- if recovery is required, do not present the state as healthy
- if only soft degradation exists, do not overstate it as a blocker

## V1 Non-Goals

This state model should not try to represent:

- every low-level compiler nuance
- every transport-level cloud variant
- every benchmark sub-metric as its own panel state
- app-oriented semantics beyond the supported frozen website surface

That detail can still be shown in the panel body without becoming part of the top-level panel state.

## Recommended V1 Success Criteria

The first panel state model is successful if it does all of the following:

- stays aligned with current CLI truth
- keeps the state count small and understandable
- distinguishes conflict from general attention
- gives users a stable meaning for healthy vs non-healthy states
- avoids inventing IDE-only workflow semantics

## Internal Development Implication

This state model implies:

- state transitions should be driven by existing JSON payloads
- action enablement should follow state priority
- future IDE features should extend this model only when the CLI truth genuinely expands

In short:

- use five states
- derive them from existing truth
- preserve conflict as distinct
- reserve attention for broader non-healthy conditions
- keep the IDE language aligned with the CLI language
