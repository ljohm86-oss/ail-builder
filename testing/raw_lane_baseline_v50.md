# Raw Lane Baseline v50

## 1. Overview

This document records the current stable raw lane baseline for the AIL system at a 50-sample scale.

Purpose:

- provide a fixed comparison point for future patch work
- prevent subjective judgment about whether the system improved or regressed
- keep raw-lane, evolution-loop, and benchmark signals aligned

This baseline is based on the latest raw sample set, raw lane results, evolution loop results, and benchmark report.

## 2. Sample Set Summary

- total_samples: `50`

### Category Distribution

- landing: `21`
- ecom_min: `13`
- after_sales: `8`
- app_min: `8`

### Cohort Distribution

- legacy_raw: `27`
- patch_validation: `13`
- clean_control: `10`

## 3. Core Metrics

- initial_compile_rate: `60.0%`
- repair_success_rate: `100.0%`
- final_compile_rate: `100.0%`
- closed_signals_count: `11`
- recoverable_patterns_count: `4`
- active_patch_pressure_count: `0`
- benchmark_release_decision: `pass`

## 4. Cohort Breakdown

### legacy_raw

- total: `27`
- initial_compile_rate: `29.63%`
- final_compile_rate: `100.0%`

### patch_validation

- total: `13`
- initial_compile_rate: `92.31%`
- final_compile_rate: `100.0%`

### clean_control

- total: `10`
- initial_compile_rate: `100.0%`
- final_compile_rate: `100.0%`

## 5. Recoverable Pattern Summary

### recoverable_coverage_gap

- evidence_count: `13`
- meaning: installed UI coverage exists, but raw outputs still omit the expected block and Repair fills it back in

### recoverable_support_gap

- evidence_count: `5`
- meaning: after-sales support/contact intent is present, raw outputs omit `after_sales:Support`, and Repair restores it

### recoverable_app_boundary_violation

- evidence_count: `3`
- meaning: app_min raw outputs drift toward auth/login/api or multi-page behavior, but Repair consistently collapses them back to the supported single-page app boundary

## 6. Evolution Status

- active_suggested_tokens: `0`
- active_patch_pressure: `[]`
- current state: `stage-stable`

Interpretation:

- the system is no longer surfacing active token gaps
- the dominant remaining signals are recoverable patterns, not new dictionary pressure
- current raw-lane noise is being absorbed rather than creating new patch pressure

## 7. Baseline Interpretation

At the current 50-sample scale, the AIL system is stage-stable for raw lane evaluation.

What this means:

- the system maintains `100.0%` final compile candidate coverage after Repair
- benchmark remains `pass`
- evolution loop shows no active patch pressure
- remaining instability is concentrated in recoverable patterns, not in missing tokens or uncontrolled drift

This baseline should be treated as the reference point for future patch work.

## 8. Baseline Usage Rules

- every future patch should be compared against this baseline before being considered successful
- the primary comparison points are:
  - compile rates
  - recoverable pattern counts
  - active patch pressure
  - benchmark release decision
- if a future patch causes worse compile rates, higher active patch pressure, or benchmark regression, treat it as a potential rollback candidate
- improvements should be justified against this baseline using measured deltas, not intuition

## 9. Current Baseline Snapshot

- total_samples: `50`
- initial_compile_rate: `60.0%`
- repair_success_rate: `100.0%`
- final_compile_rate: `100.0%`
- active_patch_pressure_count: `0`
- benchmark_release_decision: `pass`
