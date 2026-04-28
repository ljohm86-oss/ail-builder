# Context Test Report 2026-04-28

## Summary

This report captures one external regression pass over the `context` workflow after the addition of:

- `context preset`
- `context inspect`
- `context apply-check`
- `context bundle`
- `context patch`

Overall judgment:

- `alpha test-ready`
- the main `context` workflow now behaves like a real collaboration surface rather than a one-off compression utility

## Test Environment

- platform: Windows + PowerShell
- repo state observed during test pass:
  - `f12636f docs: add context test matrix`
  - `d8d6628 feat: add context patch export`
  - `dc5dce6 feat: add context bundle export`
  - `5617230 feat: add context presets`
  - `718165a feat: add context apply check`

## What Was Confirmed

### Presets

Confirmed:

- `context preset --json` returns the full catalog
- `preset_count = 5`
- visible presets:
  - `generic`
  - `codebase`
  - `writing`
  - `website`
  - `ecommerce`

This means compression is no longer one undifferentiated mode. Operators can declare the intended reading surface before handoff.

### Text Compression

Confirmed:

- `context compress --preset writing --text-file ... --json`
- returned `compression_mode = text`
- returned `source_kind = markdown`

This is a strong sign that long-form writing can now be compressed into one skeleton without collapsing into generic code-oriented output.

### Code Skeleton Extraction

Confirmed:

- `context compress --preset codebase --input-file ... --emit-skeleton`
- skeleton included:
  - `PRESET: codebase`
  - `MODE: file`
  - `IMPORTS:`
  - `SYMBOLS:`

This is the expected minimum for code-oriented AI or MCP handoff.

### Inspect

Confirmed:

- `context inspect --emit-summary`
- returned a compact summary including:
  - `skeleton_char_count`
  - `compression_ratio`

Observed example values in the test pass:

- `skeleton_char_count = 17947`
- `compression_ratio = 0.022`

This validates the intended operator workflow: inspect the bundle shape before restore or downstream editing.

### Bundle

Confirmed:

- `context bundle --preset writing --text ...`
- completed successfully
- generated a usable bundle with `file_count = 7`

Important nuance:

- bundle contents vary depending on whether a candidate input is provided
- `apply_check.json` and `apply_check_summary.txt` should only be expected when the bundle run includes a candidate surface

This is the correct behavior and should be reflected in future tests and documentation.

### Apply-check

Confirmed:

- `context apply-check --input-dir`
- returned:
  - `alignment_score = 90`
  - `apply_check_passed = true`

This shows the continuity gate is doing useful work rather than only echoing metadata.

### Patch

Confirmed:

- `context patch --input-dir`
- returned:
  - `patch_mode = directory_structural_patch`
  - `changed_paths = 2`

This means the workflow now supports a true delta handoff surface:

- original skeleton bundle
- edited candidate
- exported patch package

## Boundary Clarification

One early patch attempt failed because the candidate input mode did not match the source bundle mode.

That is not a product defect.
It is the intended boundary.

`context patch` must be run with the same mode family as the original bundle:

- text bundle -> text candidate
- file bundle -> file candidate
- directory bundle -> directory candidate

This rule should stay explicit in both docs and future tests because it prevents ambiguous patch generation.

## Current Workflow Value

At this point the `context` line supports a coherent operator workflow:

1. `context compress`
2. `context inspect`
3. `context apply-check`
4. `context patch`
5. `context patch-apply`
6. `context restore`
7. `context bundle`

That is enough to support:

- codebase context handoff
- writing-context handoff
- project-tree compression
- AI editing with continuity checks
- delta export after downstream edits

## Practical Strengths

The strongest parts of the current implementation are:

- preset-driven skeleton emphasis
- exact restore packages next to AI-facing skeletons
- inspect summaries that avoid opening the full manifest
- apply-check as a structural continuity gate
- patch export as a collaboration artifact rather than an internal debug tool

## Remaining Constraints

The current `context` workflow should still be described carefully.

It is not yet:

- semantic merge-aware regeneration
- AST-perfect code patching
- automatic patch application back into a live tree
- a guarantee against all hallucinations

The strongest accurate claim is:

- it materially reduces context-window pressure and structural drift risk while preserving exact machine restore paths

## Follow-on Note

The next natural gap identified during this test pass was controlled patch replay.

That gap has since been addressed by:

- `context patch-apply`

The remaining follow-on work should therefore focus on:

- deeper validation around replay edge cases
- cautious future work such as merge-aware or policy-aware patch application

## Final Judgment

`context` is now strong enough for repeated external testing.

Recommended label:

- `alpha test-ready`

That means:

- main flows are working
- boundaries are becoming clear
- exported artifacts are useful in real cross-tool workflows
- future work should focus on controlled replay and deeper validation, not on rethinking the core compression model
