# First User Trial Template

## Trial Metadata

- date:
- trial_operator:
- user_id:
- user_type:
- scenario_id:
- selected_profile:

## Scenario

- requirement:
- expected_profile:

## Completion

- completed: yes / no
- reached_generate: yes / no
- reached_diagnose: yes / no
- reached_repair: yes / no
- reached_compile: yes / no
- reached_sync: yes / no

## Time

- start_time:
- end_time:
- time_to_first_result:

## Friction Log

### 1. First Blocker

- step:
- description:
- user_message_or_question:
- operator_intervention:

### 2. Additional Friction

- step:
- description:
- user_message_or_question:
- operator_intervention:

### 3. Managed vs Custom Understanding

- did_user_understand_ail_is_source_of_truth: yes / no
- did_user_understand_generated_vs_custom: yes / no
- notes:

## Output Assessment

- detected_profile_by_user:
- actual_profile:
- did_output_feel_useful: yes / no
- user_confidence_level: high / medium / low
- notes:

## Failure / Recovery

- compile_or_sync_error_seen: yes / no
- was_recovery_path_clear: yes / no
- notes:

## Trial Outcome

- trial_result: success / partial / failed
- main_reason:
- should_user_continue_without_operator: yes / no

## Recommended Fixes

### Highest Priority Fix

- category: documentation_gap / cli_ux_gap / error_clarity_gap / profile_expectation_gap / workflow_gap
- description:

### Additional Fix

- category: documentation_gap / cli_ux_gap / error_clarity_gap / profile_expectation_gap / workflow_gap
- description:

## Summary

- what_worked:
- what_failed:
- what_should_be_changed_before_next_trial:
