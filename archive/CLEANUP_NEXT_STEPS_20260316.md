# Cleanup Next Steps 2026-03-16

## Purpose

This document records the current cleanup stop line for `/Users/carwynmac/ai-cl`.

It exists to answer one practical question:

- what should we do next if we want to keep cleaning the repo without breaking active workflows?

This is not a record of what was already moved.

For that, see:

- `/Users/carwynmac/ai-cl/archive/CLEANUP_AUDIT_20260316.md`
- `/Users/carwynmac/ai-cl/archive/ARCHIVE_INDEX.md`

## Current Stop Line

Cleanup should pause here for now.

Reason:

- the obvious legacy and disposable top-level items have already been archived
- the remaining top-level paths are either active mainline files or retained side workflows
- further moves now have a higher chance of breaking runnable paths than improving repo clarity

## What Was Safe To Move

Already archived safely:

- legacy core/server/compiler/generator files
- legacy MCP agent variants
- top-level Studio planning/runbook docs
- root-level generated/cache artifacts
- `ail_engine_v3.py`

These were either:

- clearly old-version code
- disposable runtime artifacts
- unreferenced top-level docs

## What Is No Longer Low-Risk

The following areas should not be moved casually:

| Path | Why It Needs Deeper Audit |
| --- | --- |
| `/Users/carwynmac/ai-cl/ail_engine_v4.py` | Directly imported by `ail_engine_v5.py` |
| `/Users/carwynmac/ai-cl/ail_engine_v5.py` | Current mainline engine |
| `/Users/carwynmac/ai-cl/ail_server_v5.py` | Current server entry |
| `/Users/carwynmac/ai-cl/verify_*.sh` | Part of active verification and benchmark path |
| `/Users/carwynmac/ai-cl/AIL_PROFILE_BOUNDARIES.md` | Current reference doc for active profiles |
| `/Users/carwynmac/ai-cl/PROFILE_VERIFY.md` | Current verification reference |
| `/Users/carwynmac/ai-cl/ail-studio-proxy.py` | May still be needed for Studio workflow |
| `/Users/carwynmac/ai-cl/ail-studio-web/` | May still be needed for Studio workflow |
| `/Users/carwynmac/ai-cl/out/` | Contains a retained side pipeline |
| `/Users/carwynmac/ai-cl/output/` | Still referenced by smoke flow |
| `/Users/carwynmac/ai-cl/workspaces/` | Referenced by retained pipeline |
| `/Users/carwynmac/ai-cl/output_projects/` | Actively used by compile outputs and validation |

## Safe Next Candidate Types

If future cleanup continues, focus on these categories first:

### 1. Unreferenced top-level notes

Candidate rule:

- top-level Markdown docs with no active references from:
  - `docs/`
  - `testing/`
  - `benchmark/`
  - `cli/`
  - active scripts

Action:

- archive docs first

### 2. Root-level generated artifacts

Candidate rule:

- generated files that are not referenced as active sources of truth

Action:

- archive, do not delete

### 3. Old version variants

Candidate rule:

- files with version suffixes that are no longer referenced by the active mainline

Action:

- confirm with `rg`
- archive only after reference audit

## Areas Requiring Separate Audit Before Any Move

These should each get their own focused audit before any cleanup:

### Studio Workstream

Scope:

- `/Users/carwynmac/ai-cl/ail-studio-proxy.py`
- `/Users/carwynmac/ai-cl/ail-studio-web/`

Questions to answer first:

- Is the Studio path still runnable?
- Is it intended to remain in this repo?
- Are there active docs or scripts that still depend on it?

### Side Pipeline Workstream

Scope:

- `/Users/carwynmac/ai-cl/out/amazon-ail/`
- `/Users/carwynmac/ai-cl/workspaces/amazon-clone/`

Questions to answer first:

- Is the pipeline still expected to run?
- Is it experimental, archival, or still a supported side workflow?
- Should it stay in repo root or be moved under a dedicated sub-area?

### Output Artifact Policy

Scope:

- `/Users/carwynmac/ai-cl/output/`
- `/Users/carwynmac/ai-cl/output_projects/`

Questions to answer first:

- Which outputs are relied on by active tests?
- Which outputs are just historical build artifacts?
- Should there be retention rules by project age or tag?

## Future Cleanup Procedure

Use this sequence for any additional cleanup:

1. identify a narrow candidate set
2. run reference audit
3. classify each item:
   - active mainline
   - retained side workflow
   - archive candidate
4. move to archive, do not delete
5. rerun validation
6. update:
   - `/Users/carwynmac/ai-cl/archive/CLEANUP_AUDIT_20260316.md`
   - `/Users/carwynmac/ai-cl/archive/ARCHIVE_INDEX.md`
   - this file if the stop line changes

## Minimum Validation

After any future cleanup touching top-level workflow files, run:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

If cleanup touches testing infrastructure more broadly, also run:

```bash
bash /Users/carwynmac/ai-cl/testing/run_raw_model_outputs.sh
bash /Users/carwynmac/ai-cl/testing/run_evolution_loop.sh
```

## Current Recommendation

Do not continue moving files immediately.

The best next action is to wait for one of these triggers:

- a new clearly obsolete top-level file appears
- a workflow is explicitly declared deprecated
- one retained side workflow is selected for dedicated audit

Until then, the repo is in a good enough cleanup state and should prefer stability over extra movement.
