# Project Integrity Check 2026-03-16

## Purpose

This document records a post-cleanup integrity check for `/Users/carwynmac/ai-cl`.

The goal of this check was to verify that recent archive and cleanup actions did not break active workflows.

This is not a full file-by-file audit.

It is a workflow integrity check based on the current mainline validation paths.

## Commands Run

The following commands were executed:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/testing/repair_smoke.sh
bash /Users/carwynmac/ai-cl/testing/run_raw_model_outputs.sh
bash /Users/carwynmac/ai-cl/testing/run_evolution_loop.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

## Results

### 1. CLI Checks

Command:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
```

Result:

- PASS

Latest result file:

- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`

Validated checks:

- `compile_json_ok`
- `sync_json_ok`
- `compile_error_json_ok`
- `sync_conflict_json_ok`
- `diagnose_json_ok`
- `repair_json_ok`
- `post_repair_diagnose_json_ok`

### 2. Repair Smoke

Command:

```bash
bash /Users/carwynmac/ai-cl/testing/repair_smoke.sh
```

Result:

- `total_cases=8`
- `repair_success_count=8`
- `repair_failure_count=0`
- `success_rate=100.0`

Interpretation:

- repair smoke remains healthy
- repair flow still converts the current smoke set into compile candidates

### 3. Raw Lane

Command:

```bash
bash /Users/carwynmac/ai-cl/testing/run_raw_model_outputs.sh
```

Result:

- `total_samples=50`
- `initial_compile_rate=60.0`
- `repair_success_rate=100.0`
- `final_compile_rate=100.0`

Interpretation:

- raw lane remains stable at the current 50-sample baseline
- recoverable patterns are still being absorbed successfully

### 4. Evolution Loop

Command:

```bash
bash /Users/carwynmac/ai-cl/testing/run_evolution_loop.sh
```

Result:

- `total_candidates=0`
- `benchmark_release_decision=pass`
- `active_suggested_tokens=0`

Interpretation:

- no active patch pressure reappeared after cleanup
- no new token gap surfaced

### 5. Benchmark

Command:

```bash
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

Result:

- `total=20`
- `passed=16`
- `failed=4`

Interpretation:

- this matches the known current benchmark baseline
- the 4 failed tasks remain the expected experimental `app_min` failures
- release baseline behavior remains stable

## Overall Integrity Assessment

Current assessment:

- project integrity is healthy
- active mainline workflows still run
- cleanup actions did not introduce an observable regression in the current validation paths

In practical terms, the following remain intact:

- CLI v1 minimal workflow
- repair smoke workflow
- raw lane workflow
- evolution loop workflow
- benchmark release baseline

## What This Check Confirms

This check gives confidence that:

- active files needed by the current workflows are still present
- recent archive moves did not break the current command surface
- benchmark and testing baselines remain consistent with the known system state

## What This Check Does Not Confirm

This check does not prove:

- that every retained file is necessary
- that every archived file is obsolete forever
- that every side workflow was exercised
- that every generated project under `output_projects/` is still valid

Those would require narrower audits.

## One-Line Conclusion

As of 2026-03-16, `/Users/carwynmac/ai-cl` remains operational on its active validation paths after cleanup, with no observed regression in CLI, raw lane, repair smoke, evolution loop, or benchmark baseline behavior.
