# Legacy Archive 2026-03-16

This archive contains legacy or currently unrelated files moved out of the repository root to reduce top-level noise.

## Included groups

- `legacy_core/`
  - older AIL server/compiler/generator experiment files not used by the current v5 + CLI workflow
- `mcp_legacy/`
  - older MCP agent variants not used by the current testing, benchmark, or CLI path

## Intentionally not moved

The AIL Studio files remain in the repository root for now because they still reference each other and may still be useful as a separate workstream.

## Safety note

This archive move was intentionally conservative:

- current v5 engine files were not moved
- benchmark / testing / docs / CLI files were not moved
- only files with no current in-repo references were archived

Studio docs archived on 2026-03-16:
- AIL_STUDIO_ARCH_GUARD.md
- AIL_STUDIO_BETA_GATE.md
- AIL_STUDIO_BETA_RUNBOOK.md
- AIL_STUDIO_FREEZE_LINE.md
- AIL_STUDIO_WEB_RULES.md
- ail_engine_v3.py (archived after reference audit; no active in-repo references found on 2026-03-16)
