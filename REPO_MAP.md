# Repository Map

## Purpose

This file is a top-level navigation map for `/Users/carwynmac/ai-cl`.

Use it to quickly understand:

- which paths are on the active mainline
- which paths are testing and benchmark infrastructure
- which paths are documentation and protocol specs
- where the current phase snapshot lives
- which paths are archived
- which paths are retained side workflows and should be treated carefully

For cleanup history, see:

- `/Users/carwynmac/ai-cl/archive/CLEANUP_AUDIT_20260316.md`
- `/Users/carwynmac/ai-cl/archive/ARCHIVE_INDEX.md`

For the current project-phase snapshot, see:

- `/Users/carwynmac/ai-cl/PROJECT_CONTEXT.md`

## Active Mainline

These paths are part of the current active AIL flow and should be treated as primary working areas.

| Path | Role |
| --- | --- |
| `/Users/carwynmac/ai-cl/ail_engine_v4.py` | Active dependency for v5 engine |
| `/Users/carwynmac/ai-cl/ail_engine_v5.py` | Current mainline engine/compiler logic |
| `/Users/carwynmac/ai-cl/ail_server_v5.py` | Current mainline server entry |
| `/Users/carwynmac/ai-cl/cli/` | AIL CLI v1 implementation |
| `/Users/carwynmac/ai-cl/profile_dicts/` | Current profile dictionaries |
| `/Users/carwynmac/ai-cl/profile_examples/` | Profile example inputs |
| `/Users/carwynmac/ai-cl/skills/` | Generator, diagnostic, repair, and related skill docs |
| `/Users/carwynmac/ai-cl/language/` | Alias/drift whitelist and language governance files |

## Testing and Benchmark

These paths form the current validation and regression system.

| Path | Role |
| --- | --- |
| `/Users/carwynmac/ai-cl/testing/` | Raw lane, repair smoke, real requirements, CLI smoke, evolution loop |
| `/Users/carwynmac/ai-cl/testing/results/` | Latest machine-readable and Markdown test outputs |
| `/Users/carwynmac/ai-cl/testing/run_trial_entry_checks.sh` | Unified frozen-profile trial and RC entry check |
| `/Users/carwynmac/ai-cl/benchmark/` | Frozen vs experimental benchmark harness |
| `/Users/carwynmac/ai-cl/benchmark/results/latest/` | Latest benchmark reports and artifacts |
| `/Users/carwynmac/ai-cl/verify_profiles.sh` | Main profile verification entry |
| `/Users/carwynmac/ai-cl/verify_landing_profile.sh` | Landing verification |
| `/Users/carwynmac/ai-cl/verify_ecom_profile.sh` | E-commerce verification |
| `/Users/carwynmac/ai-cl/verify_after_sales_profile.sh` | After-sales verification |
| `/Users/carwynmac/ai-cl/verify_app_profile.sh` | app_min technical probe |
| `/Users/carwynmac/ai-cl/verify_app_profile_smoke.sh` | app_min interaction smoke |

## Documentation and Specs

These paths hold the current protocol, implementation, and governance docs.

| Path | Role |
| --- | --- |
| `/Users/carwynmac/ai-cl/docs/` | Cloud sync, API, manifest, conflict, IDE, CLI specifications |
| `/Users/carwynmac/ai-cl/AIL_PROFILE_BOUNDARIES.md` | Profile boundary reference |
| `/Users/carwynmac/ai-cl/PROFILE_VERIFY.md` | Profile verification reference |

## Retained Side Workflows

These paths are not the mainline compile/benchmark path, but they still appear to support usable side workflows. Do not move them casually.

| Path | Role |
| --- | --- |
| `/Users/carwynmac/ai-cl/ail-studio-proxy.py` | Studio-side proxy path |
| `/Users/carwynmac/ai-cl/ail-studio-web/` | Studio web client workstream |
| `/Users/carwynmac/ai-cl/out/` | Side pipeline and artifact area; includes runnable `out/amazon-ail` flow |
| `/Users/carwynmac/ai-cl/output/` | Output artifacts still referenced by smoke flow |
| `/Users/carwynmac/ai-cl/output_projects/` | Generated projects used by tests, smoke runs, and validation |
| `/Users/carwynmac/ai-cl/workspaces/` | Retained workspace inputs; referenced by side pipeline flow |

## Archive

These paths are intentionally out of the mainline and should be treated as historical or disposable unless specifically needed.

| Path | Role |
| --- | --- |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/` | Archived old core/server/compiler/generator files |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/` | Archived old MCP agents |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/` | Archived top-level Studio docs |
| `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/` | Archived root-level generated/cache artifacts |

## Working Rules

### Safe Default

If a path is not clearly archival, assume it is active until proven otherwise.

### Before Moving Files

Run reference audit first:

```bash
rg -n "<name-or-path>" /Users/carwynmac/ai-cl --glob '!archive/**'
```

### After Cleanup

Run at least:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

### Archive Instead of Delete

Prefer moving files into `/Users/carwynmac/ai-cl/archive/` before any destructive cleanup.

## Suggested Reading Order

For someone new to the repo:

1. `/Users/carwynmac/ai-cl/REPO_MAP.md`
2. `/Users/carwynmac/ai-cl/archive/ARCHIVE_INDEX.md`
3. `/Users/carwynmac/ai-cl/docs/AIL_CLOUD_SYNC_PROTOCOL_V1.md`
4. `/Users/carwynmac/ai-cl/docs/AIL_CLI_IMPLEMENTATION_GUIDE.md`
5. `/Users/carwynmac/ai-cl/testing/raw_lane_baseline_v50.md`

## Current One-Line Summary

`/Users/carwynmac/ai-cl` now has a clearer split between active mainline code, test infrastructure, long-term specs, retained side workflows, and archived legacy material.
