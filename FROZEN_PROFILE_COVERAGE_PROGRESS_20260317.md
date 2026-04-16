# Frozen Profile Coverage Progress 2026-03-17

## Purpose

This document records the current status of the narrow frozen-profile coverage fixes completed on 2026-03-17.

It exists to answer two practical questions:

1. are there any remaining frozen-profile coverage fixes that should still be treated as active blockers
2. what coverage work should explicitly *not* be reopened right now

Primary references:

- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_COVERAGE_FIX_PLAN_20260317.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_batch_expanded_summary_20260317.md`
- `/Users/carwynmac/ai-cl/testing/results/patch_candidates_v3.json`
- `/Users/carwynmac/ai-cl/testing/results/evolution_loop_report.md`

## What Was Fixed

### Landing richer coverage

The following richer landing sections were tightened for first-pass generation and repair-side consistency:

- `landing:Team`
- `landing:FAQ`
- `landing:Stats`
- `landing:LogoCloud`

Observed improvement after the fix:

- richer landing prompts now first-pass hit `Team`, `FAQ`, `Stats`, and `LogoCloud` when explicitly requested
- first-pass `diagnose` remains green
- no `repair` step is required for the validated richer landing scenarios

### E-commerce richer coverage

The following richer e-commerce sections were tightened for first-pass generation and reporting consistency:

- `ecom:Banner`
- `ecom:CategoryNav`
- `ecom:ShopHeader`
- `ecom:SearchResultGrid` synonym handling on richer prompt forms

Observed improvement after the fix:

- richer ecom prompts now first-pass hit `Banner`, `CategoryNav`, and `ShopHeader` when explicitly requested
- first-pass `diagnose` remains green
- no `repair` step is required for the validated richer ecom scenarios

## Current Validation State

The following checks were re-run after the richer coverage fixes:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/testing/run_raw_model_outputs.sh
bash /Users/carwynmac/ai-cl/testing/run_evolution_loop.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

Observed current state:

- CLI checks: pass
- raw lane:
  - `total_samples=50`
  - `initial_compile_rate=60.0`
  - `repair_success_rate=100.0`
  - `final_compile_rate=100.0`
- evolution loop:
  - `total_candidates=0`
  - `active_suggested_tokens=0`
  - `active_patch_pressure=[]`
- benchmark:
  - `BENCHMARK_DONE total=20 passed=16 failed=4`
  - this matches the current known baseline and does not represent a new regression

## Remaining Coverage Blockers

### Active frozen-profile coverage blockers

Current answer:

- none observed at blocker level

Reason:

- the richer landing scenarios that previously under-hit supported sections now first-pass diagnose successfully while including the intended richer sections
- the richer ecom scenarios that previously collapsed to the minimal path now first-pass diagnose successfully while including the intended richer sections
- evolution loop currently reports `active_patch_pressure_count = 0`

### What is still visible in the data

The reports still contain:

- `recoverable_coverage_gap`
- `under_specified`

But these are currently concentrated in:

- historical raw samples
- patch-validation samples designed to preserve old noisy forms

They are not currently evidence that the frozen-profile CLI first-pass path still needs another narrow coverage patch.

## What Should Not Be Reopened Right Now

The following work should *not* be reopened as primary development focus right now:

- another frozen-profile token patch
- another alias patch
- another landing richer-coverage patch pass
- another ecom richer-coverage patch pass
- `after_sales` coverage patching without new evidence
- profile expansion
- compiler rewrite
- benchmark policy changes

## Why Further Coverage Patch Churn Is Not The Best Next Step

The current evidence says the project has moved past the stage where frozen-profile coverage is the main blocker.

The mainline path is now:

- first-pass stable
- compile-stable
- sync-stable
- benchmark-stable

The remaining visible issues are now mostly:

- historical noisy samples being recoverable rather than clean
- product-surface and packaging gaps
- first-user guidance and trial execution concerns

That means additional narrow coverage patching would likely have lower return than moving on to the next development phase.

## Current Decision

Recommended decision:

- stop frozen-profile coverage patching unless new trial evidence reopens a specific supported-section miss
- treat current frozen-profile coverage work as sufficient for the present v1 stage
- move development focus to the next product-closing step

## One-Line Conclusion

Frozen-profile coverage is no longer the main blocker; the project should stop patch-chasing in this area and move to the next stage of v1 product development.
