# V1 Release Gate

## 1. Purpose

This document defines the release gate for AIL v1.

Its purpose is to answer one operational question:

When is the current system ready for a v1 release candidate or internal user trial?

This gate is intentionally narrower than the full engineering surface.

It exists to make release decisions based on:

- the frozen product scope
- current benchmark semantics
- current workflow integrity signals

It does not treat every experimental capability as release-blocking.

## 2. Release Philosophy

AIL v1 should be released based on the completeness and stability of the frozen-profile product path.

That means:

- release decisions are based on the supported user workflow
- frozen profiles are gating
- experimental areas remain visible but do not define release readiness

Core principle:

Release the complete supported workflow, not the complete set of imaginable capabilities.

## 3. Product Scope Covered by This Gate

This gate applies to the v1 product scope defined in:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`

The frozen release profiles are:

- `landing`
- `ecom_min`
- `after_sales`

Experimental profile:

- `app_min`

`app_min` is not part of the v1 release baseline.

## 4. Release-Critical Workflow

The workflow that must be considered healthy for v1 release is:

```text
ail init
  -> ail generate
  -> ail diagnose
  -> ail repair if needed
  -> ail compile --cloud
  -> ail sync
```

This workflow must remain operational for the frozen profiles.

For the standard frozen-profile example prompts, the current preferred release-quality behavior is:

- `generate -> diagnose` should pass on the first try
- `repair` should remain available as a recovery step
- `repair` should not be treated as an expected mandatory first action for the standard examples

## 5. Hard Release Gates

The following are release-blocking for v1.

### Gate A. Frozen Benchmark Baseline Must Remain Green

Required condition:

- `release_baseline.ok` must be `true` in `/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json`

Primary references:

- `/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json`
- `/Users/carwynmac/ai-cl/benchmark/results/latest/report.md`

Interpretation:

- frozen profile baseline must remain green
- experimental failures and side gates must not be misclassified as frozen release blockers
- global `release_decision` may remain `fail` while the frozen release baseline is still acceptable for v1

### Gate B. CLI Smoke Must Pass

Required condition:

- CLI smoke checks must pass

Primary references:

- `/Users/carwynmac/ai-cl/testing/run_cli_checks.sh`
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`

Minimum expected checks:

- `compile_json_ok`
- `sync_json_ok`
- `compile_error_json_ok`
- `sync_conflict_json_ok`
- `diagnose_json_ok`
- `repair_json_ok`
- `post_repair_diagnose_json_ok`

Interpretation:

- the primary v1 entry surface must remain healthy

### Gate B2. Frozen-Profile First-Pass Path Must Remain Smooth

Required condition:

- the standard frozen-profile example prompts should continue to pass `generate -> diagnose` on the first pass in the CLI golden path

Primary references:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_summary_post_fix_20260317.md`
- `/Users/carwynmac/ai-cl/testing/results/trial_run_smoke_results.json`
- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`

Interpretation:

- this is the current release-quality expectation for first user experience
- `repair` remains part of the product, but frozen-profile examples should not regress back into requiring immediate repair by default

### Gate C. Repair Smoke Must Pass

Required condition:

- repair smoke success rate must remain healthy

Current expected floor:

- `100.0%` on the current smoke case set

Primary references:

- `/Users/carwynmac/ai-cl/testing/repair_smoke.sh`
- `/Users/carwynmac/ai-cl/testing/results/repair_smoke_results.json`
- `/Users/carwynmac/ai-cl/testing/results/repair_smoke_report.md`

Interpretation:

- the repair stage must still rescue the current known bad sample set

### Gate D. Raw Lane Must Stay Stage-Stable

Required condition:

- raw lane final compile rate must remain stable
- active patch pressure must not reappear

Current expected baseline:

- `total_samples: 50`
- `final_compile_rate: 100.0%`
- `active_patch_pressure_count: 0`

Primary references:

- `/Users/carwynmac/ai-cl/testing/raw_lane_baseline_v50.md`
- `/Users/carwynmac/ai-cl/testing/results/raw_model_outputs_results.json`
- `/Users/carwynmac/ai-cl/testing/results/evolution_loop_report.md`
- `/Users/carwynmac/ai-cl/testing/results/patch_candidates_v3.json`

Interpretation:

- the system may still show recoverable patterns
- but it must not regress into active unresolved patch pressure

### Gate E. Project Integrity Check Must Remain True

Required condition:

- no observed regression in active validation paths after changes affecting top-level workflow files

Primary reference:

- `/Users/carwynmac/ai-cl/testing/PROJECT_INTEGRITY_CHECK_20260316.md`

Interpretation:

- this is a stability guard around cleanup and structural changes

## 6. Non-Blocking Signals

The following do not block v1 release by themselves.

### A. Experimental `app_min` Failures

These are not release-blocking as long as:

- they remain clearly marked experimental
- they do not contaminate frozen benchmark semantics

### B. Recoverable Patterns in Raw Lane

These do not block release if:

- final compile rate remains stable
- repair remains successful
- no active patch pressure reappears

Examples:

- `recoverable_coverage_gap`
- `recoverable_support_gap`
- `recoverable_app_boundary_violation`

### C. Studio Ambiguity

Studio not being the primary entrypoint does not block v1 release.

Why:

- CLI is the primary v1 surface
- Studio is a retained side workflow, not a required v1 release surface

### D. Experimental or Archived Side Pipelines

Items under retained side workflows or archives do not block release unless they break the mainline validation path.

## 7. Release Checklist

Before declaring a v1 release candidate or internal user trial ready, confirm:

- frozen benchmark baseline is green
- CLI checks pass
- frozen-profile first-pass path remains smooth
- repair smoke passes
- raw lane remains at current stage-stable behavior
- no new active patch pressure exists
- quickstart path is usable
- frozen profile examples are available

## 8. Suggested Command Set

The preferred unified gate command is:

```bash
bash /Users/carwynmac/ai-cl/testing/run_rc_checks.sh
```

The underlying commands remain:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/testing/run_trial_entry_checks.sh
bash /Users/carwynmac/ai-cl/testing/repair_smoke.sh
bash /Users/carwynmac/ai-cl/testing/run_raw_model_outputs.sh
bash /Users/carwynmac/ai-cl/testing/run_evolution_loop.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

If top-level files or workflow paths changed, also review:

```bash
cat /Users/carwynmac/ai-cl/testing/PROJECT_INTEGRITY_CHECK_20260316.md
```

## 9. Release Decision Table

| Condition | Result |
| --- | --- |
| Frozen benchmark pass + CLI smoke pass + frozen-profile first-pass path healthy + repair smoke pass + raw lane stable | release candidate allowed |
| Frozen benchmark fails | block release |
| CLI smoke fails | block release |
| Frozen-profile first-pass path regresses back into predictable immediate repair | block release |
| Repair smoke regresses materially | block release |
| Raw lane final compile rate regresses or active patch pressure returns | block release |
| Experimental `app_min` still fails but frozen baseline is healthy | release allowed |

## 10. What Should Trigger Re-Evaluation

The following changes should trigger a fresh release gate evaluation:

- changes to CLI behavior
- changes to cloud compile integration
- changes to sync or manifest behavior
- changes to frozen profile rules
- changes to benchmark policy
- changes to top-level workflow files

## 11. What Does Not Need To Block Progress

The following should not hold v1 hostage:

- desire for broader profile coverage
- desire for Studio-first experience
- desire to eliminate every recoverable raw-lane pattern
- desire to perfect experimental flows before frozen flows are released

## 12. Current Release Position

Based on the current repository state and latest recorded signals:

- benchmark release baseline is healthy
- CLI primary path is healthy
- frozen-profile first-pass path is healthy
- repair smoke is healthy
- raw lane is stage-stable
- no active patch pressure is present

Current interpretation:

The project is approaching a viable v1 release-candidate state for the frozen-profile product path.

## 13. One-Line Gate Decision

AIL v1 should be considered releasable when the frozen-profile CLI workflow remains green across benchmark, CLI smoke, first-pass frozen-profile diagnose behavior, repair smoke, and raw-lane stage-stability checks, regardless of experimental `app_min` incompleteness.
