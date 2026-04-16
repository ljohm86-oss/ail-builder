# RC Checks Report

## Status

- overall_status: `ok`
- command_status: `ok`
- benchmark_command_ok: `false`

## Checks

- cli_checks_ok: `true`
- project_check_ok: `true`
- website_check_ok: `true`
- website_check_out_of_scope_ok: `true`
- project_check_conflict_ok: `true`
- project_doctor_ok: `true`
- project_doctor_validation_ok: `true`
- project_doctor_apply_safe_noop_ok: `true`
- project_doctor_apply_safe_repair_ok: `true`
- project_doctor_apply_safe_continue_noop_ok: `true`
- project_doctor_apply_safe_continue_repair_ok: `true`
- project_continue_auto_repair_ok: `true`
- project_continue_auto_no_repair_ok: `true`
- project_preview_ok: `true`
- project_preview_conflict_ok: `true`
- project_open_target_ok: `true`
- project_open_target_default_ok: `true`
- project_inspect_target_ok: `true`
- project_inspect_target_default_ok: `true`
- project_run_inspect_command_ok: `true`
- project_run_inspect_command_default_ok: `true`
- project_export_handoff_ok: `true`
- project_export_handoff_conflict_ok: `true`
- project_go_ok: `true`
- project_go_repair_ok: `true`
- project_go_conflict_ok: `true`
- workspace_preview_ok: `true`
- workspace_preview_project_ok: `true`
- workspace_open_target_ok: `true`
- workspace_open_target_project_ok: `true`
- workspace_inspect_target_ok: `true`
- workspace_inspect_target_project_ok: `true`
- workspace_run_inspect_command_ok: `true`
- workspace_run_inspect_command_project_ok: `true`
- workspace_export_handoff_ok: `true`
- workspace_export_handoff_project_ok: `true`
- workspace_doctor_ok: `true`
- workspace_doctor_project_ok: `true`
- workspace_continue_ok: `true`
- workspace_continue_project_ok: `true`
- workspace_go_ok: `true`
- workspace_go_project_ok: `true`
- rc_go_ok: `true`
- rc_go_refresh_ok: `true`
- project_summary_probe_ok: `true`
- project_workbench_primary_action_converged: `true`
- trial_entry_route_converged: `true`
- trial_entry_ok: `true`
- repair_smoke_ok: `true`
- raw_lane_ok: `true`
- evolution_ok: `true`
- benchmark_ok: `true`

## Metrics

- raw_total_samples: `50`
- raw_initial_compile_rate: `60.0`
- raw_final_compile_rate: `100.0`
- repair_success_rate: `100.0`
- active_patch_pressure_count: `0`
- active_suggested_tokens: `0`
- website_check_smoke_ok: `True`
- website_check_out_of_scope_smoke_ok: `True`
- project_check_smoke_ok: `True`
- project_check_conflict_smoke_ok: `True`
- project_doctor_smoke_ok: `True`
- project_doctor_validation_smoke_ok: `True`
- project_doctor_apply_safe_noop_smoke_ok: `True`
- project_doctor_apply_safe_repair_smoke_ok: `True`
- project_doctor_apply_safe_continue_noop_smoke_ok: `True`
- project_doctor_apply_safe_continue_repair_smoke_ok: `True`
- project_continue_auto_repair_smoke_ok: `True`
- project_continue_auto_no_repair_smoke_ok: `True`
- project_preview_smoke_ok: `True`
- project_preview_conflict_smoke_ok: `True`
- project_open_target_smoke_ok: `True`
- project_open_target_default_smoke_ok: `True`
- project_inspect_target_smoke_ok: `True`
- project_inspect_target_default_smoke_ok: `True`
- project_run_inspect_command_smoke_ok: `True`
- project_run_inspect_command_default_smoke_ok: `True`
- project_export_handoff_smoke_ok: `True`
- project_export_handoff_conflict_smoke_ok: `True`
- project_go_smoke_ok: `True`
- project_go_repair_smoke_ok: `True`
- project_go_conflict_smoke_ok: `True`
- workspace_preview_smoke_ok: `True`
- workspace_preview_project_smoke_ok: `True`
- workspace_open_target_smoke_ok: `True`
- workspace_open_target_project_smoke_ok: `True`
- workspace_inspect_target_smoke_ok: `True`
- workspace_inspect_target_project_smoke_ok: `True`
- workspace_run_inspect_command_smoke_ok: `True`
- workspace_run_inspect_command_project_smoke_ok: `True`
- workspace_export_handoff_smoke_ok: `True`
- workspace_export_handoff_project_smoke_ok: `True`
- workspace_doctor_smoke_ok: `True`
- workspace_doctor_project_smoke_ok: `True`
- workspace_continue_smoke_ok: `True`
- workspace_continue_project_smoke_ok: `True`
- workspace_go_smoke_ok: `True`
- workspace_go_project_smoke_ok: `True`
- rc_go_smoke_ok: `True`
- rc_go_refresh_smoke_ok: `True`
- project_summary_probe_ok: `True`
- project_workbench_primary_action_converged: `True`
- trial_entry_route_converged: `True`
- benchmark_release_decision: `fail`
- benchmark_release_baseline_ok: `True`
- benchmark_release_baseline_passed: `16`
- benchmark_release_baseline_failed: `0`

## Project Workbench Primary Action

- recommended_primary_action: `project_continue_diagnose_compile_sync`
- recommended_primary_command: `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project continue --diagnose-compile-sync --base-url embedded://local --json`
- recommended_primary_reason: `Project is healthy; use the safe continue path as the default next iteration action after source changes.`
- doctor_status: `ok`
- converged: `True`
- trial_batch_distribution: `{'project_continue_diagnose_compile_sync': 3}`
- probe_error: `None`

## Trial Entry Route

- expected_route: `trial_run_canonical_flow`
- converged: `True`
- trial_batch_distribution: `{'trial_run_canonical_flow': 3}`

## Interpretation

- The current frozen-profile RC gate is green.
- CLI checks, trial entry, repair smoke, raw lane, evolution loop, and frozen benchmark baseline are all healthy.
- Global benchmark `release_decision` may still be `fail` while frozen v1 release baseline remains acceptable.

## Artifacts

- cli_smoke_results: `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`
- trial_run_smoke_results: `/Users/carwynmac/ai-cl/testing/results/trial_run_smoke_results.json`
- repair_smoke_results: `/Users/carwynmac/ai-cl/testing/results/repair_smoke_results.json`
- raw_model_outputs_results: `/Users/carwynmac/ai-cl/testing/results/raw_model_outputs_results.json`
- patch_candidates_v3: `/Users/carwynmac/ai-cl/testing/results/patch_candidates_v3.json`
- benchmark_results: `/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json`
- benchmark_log: `/Users/carwynmac/ai-cl/testing/results/rc_benchmark.log`

## Command

```bash
bash /Users/carwynmac/ai-cl/testing/run_rc_checks.sh
```
