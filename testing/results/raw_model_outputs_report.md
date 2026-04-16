# Raw Model Outputs Report

## Summary
- total_samples: 50
- initial_compile_candidates: 30
- repair_attempts: 41
- repair_success: 41
- final_compile_candidates: 50

## Category Breakdown

### landing
- total: 21
- initial_compile_candidates: 13
- repair_success: 18
- final_compile_candidates: 21

### ecom_min
- total: 13
- initial_compile_candidates: 6
- repair_success: 10
- final_compile_candidates: 13

### after_sales
- total: 8
- initial_compile_candidates: 6
- repair_success: 7
- final_compile_candidates: 8

### app_min
- total: 8
- initial_compile_candidates: 5
- repair_success: 6
- final_compile_candidates: 8

## By Cohort

### legacy_raw
- total: 27
- initial_compile_candidates: 8
- repair_attempts: 27
- repair_success: 27
- final_compile_candidates: 27
- initial_compile_rate: 29.63
- final_compile_rate: 100.0
- recoverable_patterns: recoverable_app_boundary_violation:3, recoverable_coverage_gap:5, recoverable_support_gap:2

### patch_validation
- total: 13
- initial_compile_candidates: 12
- repair_attempts: 13
- repair_success: 13
- final_compile_candidates: 13
- initial_compile_rate: 92.31
- final_compile_rate: 100.0
- recoverable_patterns: recoverable_support_gap:2, recoverable_coverage_gap:8

### clean_control
- total: 10
- initial_compile_candidates: 10
- repair_attempts: 1
- repair_success: 1
- final_compile_candidates: 10
- initial_compile_rate: 100.0
- final_compile_rate: 100.0
- recoverable_patterns: recoverable_support_gap:1

## Legacy vs Patch Validation Comparison
- legacy_raw.initial_compile_rate: 29.63
- legacy_raw.final_compile_rate: 100.0
- patch_validation.initial_compile_rate: 92.31
- patch_validation.final_compile_rate: 100.0
- patch_validation.recoverable_patterns: recoverable_support_gap:2, recoverable_coverage_gap:8

## Recoverable Patterns
- recoverable_coverage_gap: 13
- recoverable_support_gap: 5
- recoverable_app_boundary_violation: 3

## Top Issues
- under_specified: 34
- alias_flow: 6
- alias_component: 4
- multi_result_wrapper: 4
- multiple_profiles: 3
- structure_invalid: 3
- unknown_component: 3
- app_min_boundary_exceeded: 3
- unsupported_constructs: 3

## Normalized Top Issues
- under_specified: 16
- recoverable_coverage_gap: 13
- alias_flow: 6
- recoverable_support_gap: 5
- alias_component: 4
- multi_result_wrapper: 4
- multiple_profiles: 3
- structure_invalid: 3
- unknown_component: 3
- recoverable_app_boundary_violation: 3
- unsupported_constructs: 3

## Sample Results

### RAW_L1
- category: landing
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: landing
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_L2
- category: landing
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_L3
- category: landing
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: alias_component, under_specified
- normalized_issue_types: alias_component, under_specified
- recoverable_patterns: none
- post_repair_signal_types: under_specified, compile_candidate_after_repair
- final_status: PASS

### RAW_L4
- category: landing
- source_type: simulated_ide_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: multiple_profiles, structure_invalid, unknown_component, multi_result_wrapper
- normalized_issue_types: multiple_profiles, structure_invalid, unknown_component, multi_result_wrapper
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_L5
- category: landing
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: multiple_profiles, structure_invalid, unknown_component, under_specified
- normalized_issue_types: multiple_profiles, structure_invalid, unknown_component, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_L6
- category: landing
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: alias_flow
- normalized_issue_types: alias_flow
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_L7
- category: landing
- source_type: simulated_ide_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: multi_result_wrapper
- normalized_issue_types: multi_result_wrapper
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_L8
- category: landing
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: landing
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_E1
- category: ecom_min
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_E2
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: under_specified
- normalized_issue_types: under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E3
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: alias_component, under_specified
- normalized_issue_types: alias_component, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E4
- category: ecom_min
- source_type: simulated_ide_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: multiple_profiles, structure_invalid, unknown_component, multi_result_wrapper
- normalized_issue_types: multiple_profiles, structure_invalid, unknown_component, multi_result_wrapper
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E5
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: alias_flow, under_specified
- normalized_issue_types: alias_flow, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E6
- category: ecom_min
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_A1
- category: after_sales
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: after_sales
- issues: under_specified
- normalized_issue_types: recoverable_support_gap
- recoverable_patterns: recoverable_support_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_support_gap
- final_status: PASS

### RAW_A2
- category: after_sales
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: after_sales
- issues: under_specified
- normalized_issue_types: under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_A3
- category: after_sales
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: after_sales
- issues: alias_flow, under_specified
- normalized_issue_types: alias_flow, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_P1
- category: app_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: app_min
- issues: app_min_boundary_exceeded
- normalized_issue_types: recoverable_app_boundary_violation
- recoverable_patterns: recoverable_app_boundary_violation
- post_repair_signal_types: compile_candidate_after_repair, recoverable_app_boundary_violation
- final_status: PASS

### RAW_P2
- category: app_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: app_min
- issues: app_min_boundary_exceeded
- normalized_issue_types: recoverable_app_boundary_violation
- recoverable_patterns: recoverable_app_boundary_violation
- post_repair_signal_types: compile_candidate_after_repair, recoverable_app_boundary_violation
- final_status: PASS

### RAW_P3
- category: app_min
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: app_min
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_L9
- category: landing
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: alias_component, under_specified
- normalized_issue_types: alias_component, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_A4
- category: after_sales
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: after_sales
- issues: under_specified
- normalized_issue_types: recoverable_support_gap
- recoverable_patterns: recoverable_support_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_support_gap
- final_status: PASS

### RAW_P4
- category: app_min
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: app_min
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L10
- category: landing
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: under_specified, compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L11
- category: landing
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L12
- category: landing
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: under_specified, compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L13
- category: landing
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L14
- category: landing
- source_type: simulated_ide_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: unsupported_constructs, under_specified
- normalized_issue_types: unsupported_constructs, recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L15
- category: landing
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L16
- category: landing
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L17
- category: landing
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L18
- category: landing
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: landing
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_L19
- category: landing
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: under_specified
- recoverable_patterns: none
- post_repair_signal_types: under_specified, compile_candidate_after_repair
- final_status: PASS

### RAW_L20
- category: landing
- source_type: simulated_ide_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: multi_result_wrapper, under_specified
- normalized_issue_types: multi_result_wrapper, recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: under_specified, compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_L21
- category: landing
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: landing
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_E7
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: alias_component, under_specified
- normalized_issue_types: alias_component, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E8
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: alias_flow, under_specified
- normalized_issue_types: alias_flow, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E9
- category: ecom_min
- source_type: simulated_ide_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: unsupported_constructs, under_specified
- normalized_issue_types: unsupported_constructs, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E10
- category: ecom_min
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_E11
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: under_specified
- normalized_issue_types: under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E12
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: alias_flow, under_specified
- normalized_issue_types: alias_flow, under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_E13
- category: ecom_min
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: ecom_min
- issues: under_specified
- normalized_issue_types: under_specified
- recoverable_patterns: none
- post_repair_signal_types: compile_candidate_after_repair
- final_status: PASS

### RAW_A5
- category: after_sales
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: after_sales
- issues: under_specified
- normalized_issue_types: recoverable_support_gap
- recoverable_patterns: recoverable_support_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_support_gap
- final_status: PASS

### RAW_A6
- category: after_sales
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: after_sales
- issues: under_specified
- normalized_issue_types: recoverable_support_gap
- recoverable_patterns: recoverable_support_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_support_gap
- final_status: PASS

### RAW_A7
- category: after_sales
- source_type: simulated_ide_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: after_sales
- issues: alias_flow, unsupported_constructs, under_specified
- normalized_issue_types: alias_flow, unsupported_constructs, recoverable_support_gap
- recoverable_patterns: recoverable_support_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_support_gap
- final_status: PASS

### RAW_A8
- category: after_sales
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: after_sales
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS

### RAW_P5
- category: app_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: app_min
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_P6
- category: app_min
- source_type: simulated_team_output
- sample_cohort: patch_validation
- pre_compile_recommended: yes
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: app_min
- issues: under_specified
- normalized_issue_types: recoverable_coverage_gap
- recoverable_patterns: recoverable_coverage_gap
- post_repair_signal_types: compile_candidate_after_repair, recoverable_coverage_gap
- final_status: PASS

### RAW_P7
- category: app_min
- source_type: simulated_team_output
- sample_cohort: legacy_raw
- pre_compile_recommended: no
- repair_applied: yes
- post_compile_recommended: yes
- final_profile: app_min
- issues: app_min_boundary_exceeded
- normalized_issue_types: recoverable_app_boundary_violation
- recoverable_patterns: recoverable_app_boundary_violation
- post_repair_signal_types: compile_candidate_after_repair, recoverable_app_boundary_violation
- final_status: PASS

### RAW_P8
- category: app_min
- source_type: clean_control
- sample_cohort: clean_control
- pre_compile_recommended: yes
- repair_applied: no
- post_compile_recommended: yes
- final_profile: app_min
- issues: none
- normalized_issue_types: none
- recoverable_patterns: none
- post_repair_signal_types: none
- final_status: PASS
