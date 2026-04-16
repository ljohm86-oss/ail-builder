# First User Trial Batch Recorded Summary 2026-03-17

## Purpose

This document summarizes the latest automated recorded frozen-profile batch.
It is generated from `run_trial_recording.sh` outputs and exists to give a single view of the newest recorded trial set.

## Scope

- scenarios_run: `3`
- records_created: `3`

Scenarios:
- `landing`
- `ecom_min`
- `after_sales`

## Results

- completed_count: `3`
- success_count: `3`
- repair_required_count: `0`

## Recommended Primary Action Distribution

- `project_continue_diagnose_compile_sync`: `3`

## Route Taken Distribution

- `trial_run_canonical_flow`: `3`


## Recorded Files

- `landing` -> `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_024.md` | profile=`landing` | completed=`yes` | repair=`no` | result=`success` | primary_action=`project_continue_diagnose_compile_sync` | route_taken=`trial_run_canonical_flow`
- `ecom_min` -> `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_025.md` | profile=`ecom_min` | completed=`yes` | repair=`no` | result=`success` | primary_action=`project_continue_diagnose_compile_sync` | route_taken=`trial_run_canonical_flow`
- `after_sales` -> `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_026.md` | profile=`after_sales` | completed=`yes` | repair=`no` | result=`success` | primary_action=`project_continue_diagnose_compile_sync` | route_taken=`trial_run_canonical_flow`

## Interpretation

- The latest recorded frozen-profile batch completed successfully.
- These runs now leave both structured capture JSON and markdown result records automatically.

## Artifacts

- summary_json: `/Users/carwynmac/ai-cl/testing/results/first_user_trial_batch_recorded_summary_20260317.json`
- results_dir: `/Users/carwynmac/ai-cl/testing/results`

## Command

```bash
bash /Users/carwynmac/ai-cl/testing/run_trial_batch_recording.sh
```
