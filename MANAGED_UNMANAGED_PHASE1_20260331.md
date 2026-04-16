# Managed / Unmanaged Phase 1 2026-03-31

## Purpose

This document captures the first shipped step of the managed / unmanaged boundary for generated frontend projects.

It exists to answer a narrow operator question:

- where should users make durable frontend edits now
- what is still generated and reset by AIL
- what protection now exists if a user edits managed code by mistake

## Current Phase-1 Behavior

### Generated frontend boundary

Generated frontend projects now scaffold:

- managed frontend zone:
  - `frontend/src/ail-managed/`
- unmanaged frontend zone:
  - `frontend/src/ail-overrides/`
  - `frontend/public/ail-overrides/`

Phase 1 keeps a compatibility layer in place:

- legacy generated files still continue to exist under:
  - `frontend/src/views/`
  - `frontend/src/router/routes.generated.ts`
  - `frontend/src/router/roles.generated.ts`

That compatibility layer is intentional. It avoids breaking the current website-first delivery path while the new boundary is phased in.

### Local rebuild protection

Phase 1 now also protects local managed rebuilds.

When `build_project()` overwrites an existing managed frontend file, it now:

- backs up the previous managed file first
- writes the new managed content after the backup
- emits a local summary under:
  - `.ail/local_rebuild_backups/<timestamp>/summary.md`

This means local rebuilds no longer silently discard edits made inside managed frontend files.

### Stable entry behavior

The generated frontend entry now imports unmanaged theme and CSS overrides through:

- `frontend/src/main.ts`
- `frontend/src/main.js`

Specifically:

- `frontend/src/style.css`
- `frontend/src/ail-overrides/theme.tokens.css`
- `frontend/src/ail-overrides/custom.css`

This means high-frequency visual changes no longer need to go into generated views.

### Durable user-edit zones

Users should now place durable changes in:

- `frontend/src/ail-overrides/theme.tokens.css`
- `frontend/src/ail-overrides/custom.css`
- `frontend/src/ail-overrides/components/`
- `frontend/src/ail-overrides/assets/`
- `frontend/public/ail-overrides/`

These paths are scaffolded once and then preserved across rebuilds.

## Verified Phase-1 Outcomes

The following were rechecked during implementation:

- a fresh generated sample now contains:
  - `frontend/src/ail-managed/views/`
  - `frontend/src/ail-managed/router/`
  - `frontend/src/ail-overrides/README.md`
  - `frontend/src/ail-overrides/theme.tokens.css`
  - `frontend/src/ail-overrides/custom.css`
- the frontend router now imports from:
  - `@/ail-managed/router/routes.generated`
  - `@/ail-managed/router/roles.generated`
- a user marker written into:
  - `frontend/src/ail-overrides/theme.tokens.css`
  survived a second rebuild
- a user marker written into:
  - `frontend/src/ail-managed/views/Home.vue`
  was backed up before the second rebuild replaced it
- local rebuild backup summary now appears under:
  - `.ail/local_rebuild_backups/<timestamp>/summary.md`
- repo-level smoke remained green after the boundary changes:
  - `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`

Reference validation sample:

- `/Users/carwynmac/ai-cl/output_projects/ManagedBoundarySmoke`

## Managed conflict protection

The CLI sync flow already had conflict detection. Phase 1 strengthens the operator-facing behavior:

- conflict errors now explicitly tell the operator to move durable changes into:
  - `.ail/source.ail`
  - `frontend/src/ail-overrides/theme.tokens.css`
  - `frontend/src/ail-overrides/custom.css`
- `ail sync --backup-and-overwrite` now also writes:
  - `.ail/conflicts/<build_id>/summary.md`

That summary records:

- which managed files drifted
- which backups were created
- where durable changes should be migrated instead

Phase 1 now also mirrors this operator protection during local rebuilds:

- local managed overwrites now back up drifted files before replacement
- local rebuild summaries now explain where durable edits should move instead:
  - `.ail/source.ail`
  - `frontend/src/ail-overrides/theme.tokens.css`
  - `frontend/src/ail-overrides/custom.css`

## Current Truth

Phase 1 does **not** yet mean full bidirectional round-trip editing.

The current truth is:

- `AIL/source` remains the main structural source of truth
- `frontend/src/ail-managed/` is the generated frontend zone
- `frontend/src/ail-overrides/` is now the intended durable customization zone
- managed drift protection is friendlier than before
- compatibility files still exist while the old website-first flow is phased toward the new boundary

## Next Recommended Step

If this boundary is kept, the safest Phase-2 follow-up is:

1. move more runtime/frontend references away from legacy `frontend/src/views` and into `frontend/src/ail-managed`
2. decide whether sync manifests should promote `frontend/src/ail-managed/**` into the primary managed root instead of only preserving the legacy generated mirror
