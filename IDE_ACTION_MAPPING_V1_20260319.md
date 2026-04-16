# IDE Action Mapping V1 2026-03-19

## Purpose

This document defines how the first IDE panel actions should map to existing CLI commands in the current CLI-first AIL system.

It exists to answer four practical questions:

1. which actions the first IDE panel should expose
2. which CLI commands each action should trigger
3. in which panel states each action should be enabled or suppressed
4. which sections should be refreshed after each action completes

Use this together with:

- `/Users/carwynmac/ai-cl/IDE_PANEL_CONTRACT_V1_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_PANEL_STATE_MODEL_V1_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_CONSUMPTION_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/PROJECT_CONTEXT.md`

## Mapping Philosophy

The IDE should not invent custom workflow actions first.

The first IDE panel should expose a small action set that directly maps to already-stable CLI commands.

That means:

- action labels may be IDE-friendly
- action meaning must remain CLI-aligned
- action enablement must follow the panel state model
- action completion should refresh the panel from authoritative JSON again

## Recommended V1 Actions

The first IDE panel should support these actions:

1. `Project Go`
2. `Project Preview`
3. `Project Doctor`
4. `Workspace Go`
5. `Workspace Doctor`
6. `RC Check Refresh`

Anything beyond these should be deferred unless it clearly reuses an already-stable CLI action.

## Action Mapping Table

| IDE Action | CLI Command | Primary Context | Main Purpose |
| --- | --- | --- | --- |
| `Project Go` | `python3 -m cli project go --json` | project | execute the current recommended project route |
| `Project Preview` | `python3 -m cli project preview --json` | project | refresh preview handoff and artifact inspection entry |
| `Project Doctor` | `python3 -m cli project doctor --fix-plan --json` | project | surface structured recovery path |
| `Workspace Go` | `python3 -m cli workspace go --json` | workspace | execute the current recommended workspace route |
| `Workspace Doctor` | `python3 -m cli workspace doctor --json` | workspace | surface workspace-level recovery or review path |
| `RC Check Refresh` | `python3 -m cli rc-check --refresh --json` | project or workspace | refresh high-level readiness and release-facing truth |

## Enablement Rules By State

The IDE should use the panel state model from:

- `/Users/carwynmac/ai-cl/IDE_PANEL_STATE_MODEL_V1_20260319.md`

The following action rules are recommended.

### In `loading`

Enable:

- none

Reason:

- authoritative inputs are still being gathered
- the panel should not fire new actions until it has a settled interpretation

### In `ok`

Enable:

- `Project Go` in project context
- `Project Preview` in project context
- `Workspace Go` in workspace context
- `RC Check Refresh`

Optional:

- `Project Doctor`
- `Workspace Doctor`

These may remain available as secondary actions, but they should not visually compete with the main healthy path.

### In `warning`

Enable:

- same actions as `ok`

Behavior note:

- keep the recommended healthy path available
- visually explain what is weaker than ideal
- do not overreact by disabling normal continuation if the system is still usable

### In `conflict`

Enable:

- `Project Doctor`
- `RC Check Refresh`

Suppress as primary CTA:

- `Project Go`

Optional:

- `Project Preview`

Only keep this available if it helps inspection without implying safe continuation.

Behavior note:

- conflict must redirect the user toward recovery, not routine continuation

### In `attention`

Enable:

- `Project Doctor` in project context
- `Workspace Doctor` in workspace context
- `RC Check Refresh`

Suppress as primary CTA:

- `Project Go`
- `Workspace Go`

Optional:

- `Project Preview`

Only if it helps inspection and does not misrepresent the context as healthy.

## Context Rules

### Project Context

Primary visible actions should be:

1. `Project Go`
2. `Project Preview`
3. `Project Doctor`
4. `RC Check Refresh`

In project context, `Workspace Go` and `Workspace Doctor` should not be primary actions.

### Workspace Context

Primary visible actions should be:

1. `Workspace Go`
2. `Workspace Doctor`
3. `RC Check Refresh`

In workspace fallback mode, `Project Go` should not appear unless the panel has explicitly entered a concrete project context.

## Refresh Rules After Actions

Every action should be followed by a controlled re-read of authoritative JSON.

### After `Project Go`

Refresh in this order:

1. `project summary --json`
2. `project preview --json`
3. `rc-check --json`

Reason:

- the panel needs updated project health
- updated preview handoff
- updated release-facing summary

### After `Project Preview`

Refresh in this order:

1. `project preview --json`
2. optionally `project inspect-target --json` if the user has an expanded target open

Reason:

- preview is the authoritative source for current artifact handoff

### After `Project Doctor`

Refresh in this order:

1. `project doctor --fix-plan --json`
2. `project summary --json`
3. `project preview --json`

Reason:

- recovery output may change the recommended path
- the panel should immediately reflect that change

### After `Workspace Go`

Refresh in this order:

1. `workspace summary --json`
2. `workspace preview --json`
3. `rc-check --json`

### After `Workspace Doctor`

Refresh in this order:

1. `workspace doctor --json`
2. `workspace summary --json`
3. `rc-check --json`

### After `RC Check Refresh`

Refresh in this order:

1. `rc-check --refresh --json`
2. `project summary --json` or `workspace summary --json`
3. `project preview --json` or `workspace preview --json`

Reason:

- release-facing truth should update first
- then the local panel context should realign to that updated truth

## Error Handling Rules

The IDE should preserve CLI semantics when an action fails.

Recommended behavior:

- keep the prior panel state visible until the action returns
- show action-local failure inline
- re-enter normal panel state derivation only after authoritative JSON is refreshed again

The panel should not synthesize a custom failure taxonomy beyond the existing high-level states.

## Suggested Button Priority

### Healthy Project

Recommended button order:

1. `Project Go`
2. `Project Preview`
3. `RC Check Refresh`
4. `Project Doctor`

### Conflict Project

Recommended button order:

1. `Project Doctor`
2. `Project Preview`
3. `RC Check Refresh`

### Healthy Workspace

Recommended button order:

1. `Workspace Go`
2. `RC Check Refresh`
3. `Workspace Doctor`

### Attention Workspace

Recommended button order:

1. `Workspace Doctor`
2. `RC Check Refresh`
3. `Workspace Go`

## V1 Non-Goals

The first IDE action mapping should not attempt:

- custom IDE-native sync orchestration
- hidden auto-repair on load
- independent release-approval logic
- app-oriented actions outside the frozen website surface
- replacing CLI actions with IDE-only equivalents

## Recommended V1 Success Criteria

The action mapping is successful if it does all of the following:

- every panel action maps to an existing stable CLI command
- action availability follows the state model consistently
- healthy paths remain fast in `ok` and `warning`
- conflict and attention states redirect users toward recovery
- action completion always re-syncs the panel with authoritative JSON

## Internal Development Implication

This mapping implies:

- the first IDE panel can be implemented without inventing new product behavior
- action wiring should be thin and explicit
- most implementation risk sits in presentation, not in workflow definition

In short:

- map UI buttons directly to CLI
- gate buttons by state
- refresh from JSON after every action
- keep the IDE as a consumer of stable truth
