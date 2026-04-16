# Archive Index

## Purpose

This file is a quick index for archived material under `/Users/carwynmac/ai-cl/archive/`.

Use it when you need to answer:

- what was archived
- where it was archived
- why it was archived
- which active areas were intentionally left out of archive moves

For detailed rationale and validation results, see:

- `/Users/carwynmac/ai-cl/archive/CLEANUP_AUDIT_20260316.md`

## Archive Directories

| Directory | Contents | Status |
| --- | --- | --- |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/` | Old engine/server/compiler/generator variants | Archived, not on current mainline |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/` | Old MCP agent variants | Archived, not on current mainline |
| `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/` | Top-level Studio docs and runbooks | Archived docs only |
| `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/` | Root-level generated/cache artifacts | Archived disposable artifacts |
| `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/studio_web_generated/` | Studio web generated output artifacts | Archived generated artifacts |

## What Is In Each Archive

### `/Users/carwynmac/ai-cl/archive/legacy_20260316/legacy_core/`

Includes:

- `ail_server_v2.py`
- `ail_server_v3.py`
- `ail_server_v4.py`
- `ail_compiler_v2_core.py`
- `ail_desktop_compiler.py`
- `ail_fullstack_v1_2.py`
- `ail_generator_v2.py`
- `ail_engine_v3.py`

Use this archive when:

- investigating old implementation history
- comparing older compile behavior
- recovering a pre-v5 experiment

### `/Users/carwynmac/ai-cl/archive/legacy_20260316/mcp_legacy/`

Includes:

- `mcp_agent.py`
- `mcp_agent_auto.py`
- `mcp_agent_v1_1.py`
- `mcp_agent_v1_2.py`
- `mcp_agent_v2.py`
- `mcp_agent_v3.py`
- `mcp_agent_v4.py`
- `mcp_agent_v5.py`

Use this archive when:

- checking historical MCP agent iterations
- recovering old agent-side experiments

### `/Users/carwynmac/ai-cl/archive/legacy_20260316/studio_docs/`

Includes:

- `AIL_STUDIO_ARCH_GUARD.md`
- `AIL_STUDIO_BETA_GATE.md`
- `AIL_STUDIO_BETA_RUNBOOK.md`
- `AIL_STUDIO_FREEZE_LINE.md`
- `AIL_STUDIO_WEB_RULES.md`

Use this archive when:

- reviewing Studio planning history
- checking old Studio runbooks or freeze notes

### `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/`

Includes:

- `ail_data.db`
- `__pycache__/`
- `.pycache/`

Use this archive when:

- recovering a root-level generated database artifact
- checking removed runtime cache artifacts

### `/Users/carwynmac/ai-cl/archive/generated_or_cache_20260316/studio_web_generated/`

Includes:

- `dist/`
- `test-results/`

Use this archive when:

- reviewing old built Studio web output
- checking archived Studio Playwright output artifacts

## Active Areas Intentionally Kept Out Of Archive

These areas were reviewed and intentionally left in the active workspace:

| Path | Why It Was Kept |
| --- | --- |
| `/Users/carwynmac/ai-cl/ail_engine_v4.py` | Imported by `ail_engine_v5.py` |
| `/Users/carwynmac/ai-cl/ail_engine_v5.py` | Current mainline engine |
| `/Users/carwynmac/ai-cl/ail_server_v5.py` | Current mainline server |
| `/Users/carwynmac/ai-cl/verify_profiles.sh` and `verify_*.sh` | Active benchmark and profile verification path |
| `/Users/carwynmac/ai-cl/AIL_PROFILE_BOUNDARIES.md` | Current boundary reference |
| `/Users/carwynmac/ai-cl/PROFILE_VERIFY.md` | Current verification reference |
| `/Users/carwynmac/ai-cl/ail-studio-proxy.py` | Studio code path still preserved |
| `/Users/carwynmac/ai-cl/ail-studio-web/` | Studio code path still preserved |
| `/Users/carwynmac/ai-cl/output/` | Used by active smoke flow |
| `/Users/carwynmac/ai-cl/out/` | Contains runnable side pipeline work |
| `/Users/carwynmac/ai-cl/workspaces/` | Referenced by the retained `out/amazon-ail` pipeline |

## Quick Rules

- Do not delete archived files before checking whether they are still useful as historical references.
- Do not move active engine/server/verify files without rerunning checks.
- Do not assume `out/`, `output/`, or `workspaces/` are disposable; parts of them are still used.
- If a future cleanup moves more files, update both:
  - `/Users/carwynmac/ai-cl/archive/ARCHIVE_INDEX.md`
  - `/Users/carwynmac/ai-cl/archive/CLEANUP_AUDIT_20260316.md`

## Minimum Validation After Future Cleanup

Run:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

Treat regressions in either path as a stop signal for further cleanup.
