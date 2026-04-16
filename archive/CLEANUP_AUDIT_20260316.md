# Cleanup Audit 2026-03-16

## Purpose

This document records the repository cleanup performed on 2026-03-16.

The goal of this cleanup was:

- reduce top-level clutter
- archive clearly legacy or disposable artifacts
- avoid breaking active benchmark, CLI, and verification workflows
- keep a written record of what was moved and why

This was a conservative cleanup.

Files were only moved when one of these was true:

- they were clearly old-version implementations no longer referenced by the active in-repo flow
- they were generated or cache artifacts
- they were top-level documentation files with no active references from the current main workflow

## Cleanup Principles

- Do not delete first. Archive first.
- Do not move files that are still referenced by active scripts.
- Do not move files on the current compiler or benchmark path.
- Prefer preserving runnable workflows over maximizing tidiness.

## Archive Targets Created

| Path | Purpose |
| --- | --- |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/` | Legacy code and old workflow archive |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/` | Old server/compiler/core variants |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/` | Old MCP agent variants |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/` | Top-level Studio planning/runbook docs |
| `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/` | Root-level generated/cache artifacts |

## Archived Items

### Legacy Core

Moved to `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/`:

- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_server_v2.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_server_v3.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_server_v4.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_compiler_v2_core.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_desktop_compiler.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_fullstack_v1_2.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_generator_v2.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/ail_engine_v3.py`

Rationale:

- these are old-version implementations
- active workflows are centered on `ail_engine_v5.py` and `ail_server_v5.py`
- `ail_engine_v3.py` was archived only after confirming no active in-repo references
- `ail_engine_v4.py` was intentionally not moved because `ail_engine_v5.py` imports it directly

### Legacy MCP Agents

Moved to `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/`:

- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent_auto.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent_v1_1.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent_v1_2.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent_v2.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent_v3.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent_v4.py`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/mcp_agent_v5.py`

Rationale:

- these were treated as legacy variants
- no active mainline testing or CLI path was using them

### Studio Top-Level Docs

Moved to `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/`:

- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_ARCH_GUARD.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_BETA_GATE.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_BETA_RUNBOOK.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_FREEZE_LINE.md`
- `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/AIL_STUDIO_WEB_RULES.md`

Rationale:

- these were top-level planning/runbook documents
- no active references were found from current mainline docs, testing, CLI, benchmark, skills, or language directories
- the Studio code path itself was intentionally preserved

### Generated and Cache Artifacts

Moved to `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/`:

- `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/ail_data.db`
- `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/__pycache__/`
- `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/.pycache/`

Rationale:

- root-level `ail_data.db` appeared to be a stray generated artifact, not an active repository source of truth
- Python cache directories are disposable runtime artifacts

### Studio Generated Artifacts

Moved to `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/studio_web_generated/`:

- `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/studio_web_generated/dist/`
- `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/studio_web_generated/test-results/`

Rationale:

- these were generated artifacts under `/Users/carwynmac/ai-cl/ail-studio-web/`
- no active references were found from current mainline docs, testing, benchmark, CLI, skills, or language paths
- Studio source and retained runtime code were kept in place

## Items Explicitly Kept

The following items were reviewed and intentionally left in place.

### Active Engine and Server Path

- `/Users/carwynmac/ai-cl/ail_engine_v4.py`
- `/Users/carwynmac/ai-cl/ail_engine_v5.py`
- `/Users/carwynmac/ai-cl/ail_server_v5.py`

Reason:

- `ail_engine_v5.py` imports `ail_engine_v4.py`
- these files remain on the active compile path

### Verification and Benchmark Gate

- `/Users/carwynmac/ai-cl/verify_after_sales_profile.sh`
- `/Users/carwynmac/ai-cl/verify_app_profile.sh`
- `/Users/carwynmac/ai-cl/verify_app_profile_smoke.sh`
- `/Users/carwynmac/ai-cl/verify_ecom_profile.sh`
- `/Users/carwynmac/ai-cl/verify_landing_profile.sh`
- `/Users/carwynmac/ai-cl/verify_profiles.sh`
- `/Users/carwynmac/ai-cl/AIL_PROFILE_BOUNDARIES.md`
- `/Users/carwynmac/ai-cl/PROFILE_VERIFY.md`

Reason:

- these files are still referenced by benchmark and verification workflows

### Studio Code Path

- `/Users/carwynmac/ai-cl/ail-studio-proxy.py`
- `/Users/carwynmac/ai-cl/ail-studio-web/`

Reason:

- likely still form a coherent Studio workstream
- code and runtime path were not audited deeply enough to safely move them
- only top-level Studio docs were archived

### Output and Workspace Trees

- `/Users/carwynmac/ai-cl/output/`
- `/Users/carwynmac/ai-cl/out/`
- `/Users/carwynmac/ai-cl/workspaces/`

Reason:

- `/Users/carwynmac/ai-cl/output/` is used by `verify_app_profile_smoke.sh`
- `/Users/carwynmac/ai-cl/out/amazon-ail/` contains a still-runnable pipeline flow
- `/Users/carwynmac/ai-cl/workspaces/amazon-clone/` is referenced by that pipeline

## Validation Performed

After cleanup, the following checks were rerun:

### CLI Checks

Command:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
```

Result:

- passed

Representative latest result:

```json
{
  "status": "ok",
  "checks": {
    "compile_json_ok": true,
    "sync_json_ok": true,
    "compile_error_json_ok": true,
    "sync_conflict_json_ok": true,
    "diagnose_json_ok": true,
    "repair_json_ok": true,
    "post_repair_diagnose_json_ok": true
  }
}
```

### Benchmark

Command:

```bash
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

Result:

- completed
- `total=20`
- `passed=16`
- `failed=4`

Interpretation:

- this matches the known current benchmark baseline
- no new cleanup-induced regression was observed

## Current Top-Level State

After cleanup, the repository root is more focused on active paths:

- `cli/`
- `docs/`
- `testing/`
- `benchmark/`
- `skills/`
- `language/`
- active engine/server files
- active verification scripts
- retained Studio code path
- retained output/workspace trees that still support runnable flows

## What This Audit Does Not Claim

- It does not prove every retained file is necessary.
- It does not prove all archived files are permanently obsolete.
- It does not replace a deeper dependency graph or ownership review.

This audit only records a conservative cleanup pass that preserved active workflows.

## Recommended Next Rule

For future cleanup:

1. search references first
2. archive before delete
3. rerun CLI checks
4. rerun benchmark if cleanup touches top-level workflow files
5. record the decision in this file or a new dated audit file
