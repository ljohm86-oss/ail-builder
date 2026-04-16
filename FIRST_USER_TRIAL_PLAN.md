# First User Trial Plan

## 1. Purpose

This document defines the first real user trial for AIL v1.

Its purpose is to answer:

- who should try the system first
- what exact workflow they should run
- what counts as success
- what feedback should be collected

This is not a broad launch plan.

It is a controlled first-user trial plan for the current frozen-profile CLI workflow.

## 2. Trial Goal

The goal of the first user trial is:

Validate that a real user can complete the frozen-profile AIL workflow with acceptable friction using the current CLI-first product path.

The trial is not trying to prove:

- broad market fit
- support for arbitrary product types
- experimental profile readiness
- Studio-first usability

The trial is only trying to prove:

- the current v1 path is understandable
- the current v1 path is runnable
- the current v1 path produces useful first results

## 3. Trial Scope

### In Scope

- CLI-first workflow
- frozen profiles only:
  - `landing`
  - `ecom_min`
  - `after_sales`
- first-run experience
- diagnose / repair usability
- compile / sync usability
- basic interpretation of generated output

### Out of Scope

- `app_min`
- Studio as primary entrypoint
- custom code authoring workflow
- patch compile
- collaborative workflows
- reverse sync

## 4. Recommended Trial Users

### Primary Trial User Type

Use 3 to 5 technical users with enough comfort to run terminal commands, but who are not deeply embedded in the current repo internals.

Ideal characteristics:

- can follow a written quickstart
- can report friction clearly
- are not relying on insider memory about how the repo evolved

### Avoid For This First Trial

- users expecting no terminal usage
- users testing unsupported product types
- users focused on app-style experimental flows
- users expecting broad arbitrary backend generation

## 5. Trial Materials

The trial should use these documents as the official source set:

- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`
- `/Users/carwynmac/ai-cl/PROJECT_CONTEXT.md`

The trial operator should also keep these references available:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`
- `/Users/carwynmac/ai-cl/testing/raw_lane_baseline_v50.md`

## 6. Trial Workflow

Each user should run one complete golden-path flow.

Preferred unified entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario <landing|ecom_min|after_sales> --base-url embedded://local
```

Batch validation entry for operators:

```bash
bash /Users/carwynmac/ai-cl/testing/run_trial_entry_checks.sh
```

Canonical path:

```text
init
  -> generate
  -> diagnose
  -> repair if needed
  -> compile --cloud
  -> sync
```

Current expectation for the standard frozen-profile example prompts:

- `generate -> diagnose` should usually succeed on the first pass
- `repair` should remain available as a recovery step for noisy or drifted AIL
- a user needing immediate repair on the standard examples should now be treated as a meaningful trial signal, not as the expected normal path

Each trial user should perform exactly one profile-first task from the supported example set.

## 7. Trial Scenarios

Use one scenario per profile.

### Scenario A: Landing

Requirement:

```text
做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。
```

Expected profile:

- `landing`

### Scenario B: E-commerce

Requirement:

```text
做一个数码商城，包含首页商品列表、商品详情、购物车、结算。
```

Expected profile:

- `ecom_min`

### Scenario C: After-sales

Requirement:

```text
做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。
```

Expected profile:

- `after_sales`

## 8. Trial Setup

Before any trial begins, the operator should verify:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/testing/run_trial_entry_checks.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

Expected state:

- CLI checks pass
- frozen-profile trial entry checks pass
- benchmark release baseline remains pass

If these do not hold, do not begin the trial.

## 9. Trial Instructions for Users

Each user should be given only:

1. the selected scenario requirement
2. `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
3. the instruction to stop and report any point where the path becomes unclear

Do not preload the user with internal architecture explanation unless they get blocked.

The purpose is to test whether the product path is understandable, not whether an expert can rescue it.

## 10. What To Observe

The trial should capture the following.

### A. Time To First Result

Track:

- time from first command to first synced generated project

### B. First-Run Friction

Track:

- where the user pauses
- where the user asks for help
- where they misunderstand managed vs custom
- where they misunderstand diagnose / repair
- whether they expect repair too early or use it without need
- where compile or sync feels unclear

### C. Output Confidence

Track:

- whether the user can tell which profile they got
- whether the output feels like a reasonable first result
- whether the user understands what to do next after sync

### D. Failure Mode Clarity

Track:

- whether errors are understandable
- whether the user knows how to recover after a failed diagnose/repair/compile/sync step

## 11. Success Criteria

The first user trial should be considered successful if most users can:

1. complete the golden path with only light guidance
2. reach a synced local generated project
3. understand that `.ail/source.ail` is the source of truth
4. understand that generated files live in managed zones
5. identify the profile they worked with
6. explain the next iteration step after the first result

Preferred current success shape:

- users can move from `generate` to `diagnose` to `compile --cloud` without first needing `repair` on the standard frozen-profile examples

## 12. Failure Signals

The trial should be treated as not yet ready for wider rollout if users consistently:

- get lost before compile
- do not understand diagnose / repair
- are forced into immediate repair on the standard frozen-profile examples
- cannot interpret sync conflicts
- confuse generated files with editable source of truth
- cannot tell what the product currently supports
- repeatedly choose unsupported expectations

## 13. Feedback Format

Use a simple per-user report with:

- scenario used
- completed: yes/no
- time to first result
- where the user got stuck
- which step required help
- what instruction was unclear
- whether the output felt useful
- recommended fix

Suggested output file pattern:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_<date>.md`

## 14. Recommended Trial Sequence

### Step 1

Operator validates current release gate prerequisites.

### Step 2

Assign one frozen-profile scenario to each trial user.

### Step 3

User runs the quickstart with minimal intervention.

Default expectation:

- the user should try `generate -> diagnose` first
- `repair` should be introduced only when diagnosis actually indicates it is needed

### Step 4

Capture friction and completion data.

### Step 5

Group all issues into:

- documentation gap
- CLI UX gap
- error clarity gap
- profile expectation gap

### Step 6

Fix only issues that improve the primary v1 path.

## 15. What To Fix First After Trial

If the trial reveals issues, prioritize them in this order:

1. broken golden-path step
2. unclear quickstart instruction
3. regression of first-pass frozen-profile `generate -> diagnose`
4. confusing error or recovery instruction
5. frozen-profile expectation mismatch
6. optional ergonomics improvements

Do not use the first trial to justify uncontrolled feature expansion.

## 16. Recommended Immediate Next Deliverable

After this plan is accepted, the next most useful artifact is:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_template.md`

That file should provide a standard form for recording each trial result.

## 17. One-Line Trial Decision

The first user trial should validate whether the frozen-profile CLI workflow is understandable and complete for real users, not whether the entire AIL vision is already finished.
