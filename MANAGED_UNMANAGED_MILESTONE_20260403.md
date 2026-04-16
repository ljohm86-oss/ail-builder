# Managed / Unmanaged Workflow Milestone 2026-04-03

## Purpose

This document marks the current managed / unmanaged frontend customization track as a stable milestone.

The goal is not to claim full round-trip editing.
The goal is to state clearly that AIL now has a practical, repeatable, user-facing customization workflow that no longer depends on editing generated files directly.

## Milestone Summary

The current frontend customization path is now stable enough to treat as a product milestone:

- `AIL/source` remains the structural source of truth
- generated frontend code now has a real managed / unmanaged boundary
- users now have durable theme, CSS, and component override layers
- users can now discover hook surfaces from generated catalogs and CLI inspection
- users can now scaffold live hook files from starter examples without manually reverse-engineering managed Vue files

This is the first point where the system supports a credible "generate, customize, rebuild, keep going" loop.

## Current Boundary

Managed frontend surface:

- `frontend/src/ail-managed/**`

Unmanaged frontend surface:

- `frontend/src/ail-overrides/theme.tokens.css`
- `frontend/src/ail-overrides/custom.css`
- `frontend/src/ail-overrides/components/**`
- `frontend/public/ail-overrides/**`

This means the recommended durable editing path is now:

1. change structure or core content in `.ail/source.ail`
2. change global brand/theme tokens in `theme.tokens.css`
3. change small local styles in `custom.css`
4. change durable inserts or custom fragments in `components/**`

## Current Protection Layer

The system now protects users from silent loss in both major overwrite paths:

- local rebuild now records managed drift backups under:
  - `/.ail/local_rebuild_backups/<timestamp>/summary.md`
- sync conflict handling now records managed drift backups under:
  - `/.ail/conflicts/<build_id>/summary.md`

That means a user who edits managed code by mistake is no longer exposed to silent overwrite as the default behavior.

## Current Hook Workflow

Generated projects now expose hook discovery and scaffolding through:

- `/.ail/hook_catalog.json`
- `/.ail/hook_catalog.md`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hooks --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hooks --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init <hook_name> --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init --follow-recommended --json`

The current workflow is now:

1. inspect the hook surface from the catalog or CLI
2. narrow with `--suggest`
3. filter further with `--page-key`, `--section-key`, and `--slot-key`
4. scaffold a live override file with `project hook-init`
5. keep the resulting durable file under `frontend/src/ail-overrides/components/**`

At the repo root, the shortest happy path is now:

1. run `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hooks --json`
2. copy the recommended `workspace hook-init` command
3. or jump directly to `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init --follow-recommended --json`

This is now practical enough for real operator and user use.

## Current Hook Scope

The hook system now supports:

- page-level hooks
- section-level hooks
- selected high-value child-slot hooks
- lightweight `context.runtime`

High-value hook coverage now exists across:

- landing / company-homepage surfaces
- ecom discovery-to-purchase surfaces
- after-sales tracked-case surfaces

This means durable customization is no longer limited to one narrow project type.

## Current CLI Ergonomics

The current helper flow now includes:

- shorthand hook names such as `home.before`
- automatic template selection through `--template auto`
- suggestion mode through `--suggest`
- catalog path discovery through `--open-catalog`
- safe overwrite behavior through `--force`
- progressively narrower suggestion filters:
  - `--page-key`
  - `--section-key`
  - `--slot-key`

That is enough to make first-time hook authoring much less fragile than it was one phase earlier.

## What This Milestone Does Not Claim

This milestone does **not** mean:

- full round-trip source recovery from arbitrary code edits
- complete hook coverage for every generated block
- rich business-state props for every hook
- a complete low-code editor

The honest product claim is narrower:

- AIL now supports a durable, inspectable, CLI-assisted frontend override workflow
- and that workflow is stable enough to pause here as a milestone

## Current Recommended Pause Point

This is a good pause point for the customization productization line because:

- the boundary is real
- the backup story is real
- the hook discovery story is real
- the hook scaffolding story is real
- repo-level smoke remains green

The one later validation interruption after this milestone was environmental, not logical: a saturated Codex exec/session pool caused Python runtime loading failures during fresh smoke reruns. After restarting Codex and rerunning from a clean pool on 2026-04-04, fresh compile and full CLI smoke both returned to green, so this milestone remains valid without qualification.

If work resumes later, the next highest-value follow-ups would be:

1. richer guided hook selection or auto-scaffold UX
2. broader hook coverage only where it remains template-safe
3. more selective runtime context for the highest-value hooks

## Most Important Truth

The system is now past the point where "user customization" means "edit generated files and hope".

The better truth is now:

- generate with AIL
- keep structure in AIL
- keep durable overrides in unmanaged files
- discover and scaffold hooks from the CLI
- rebuild without losing the intended customization path
