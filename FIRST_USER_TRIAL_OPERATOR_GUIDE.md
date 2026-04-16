# First User Trial Operator Guide

## 1. Purpose

This guide is for the person running the first AIL v1 user trial.

It explains:

- how to prepare the session
- how to introduce the trial
- when to help and when not to help
- how to record useful observations
- how to avoid turning the trial into a coached demo

Use this guide together with:

- `/Users/carwynmac/ai-cl/FIRST_USER_TRIAL_PLAN.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_template.md`
- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`

## 2. Operator Goal

The operator's job is not to make the user succeed at all costs.

The operator's job is to learn whether the current v1 path is understandable and usable with minimal help.

This means:

- do not over-explain too early
- do not rescue the user before observing the friction
- do not substitute your own product knowledge for product clarity

## 3. What The Operator Should Prepare

Before the session, make sure these are ready:

- the repository is in a healthy state
- the trial scenario is selected
- the user has the quickstart doc
- the operator has the trial template open

Minimum preflight commands:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/testing/run_trial_entry_checks.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

If either of these fails, do not run the trial.

## 4. Trial Materials

Give the user only what they need.

Recommended material set:

1. the selected scenario requirement
2. `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
3. the preferred command:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario <landing|ecom_min|after_sales> --base-url embedded://local
```

Optional operator-only references:

- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_template.md`

Do not front-load architecture docs unless the trial is specifically testing documentation depth.

## 5. How To Introduce The Trial

Suggested framing:

```text
Please try to complete the workflow using the quickstart and the assigned requirement.
If something feels unclear, confusing, or blocked, say it out loud.
I may ask a few follow-up questions, but I’ll try not to interrupt your flow.
```

Keep the intro short.

The trial is about product clarity, not a tutorial session.

## 6. Operator Behavior Rules

### Do

- observe carefully
- note hesitation points
- capture exact user wording when possible
- wait long enough to see whether the user can self-recover
- ask short clarification questions after the friction appears

### Do Not

- narrate the architecture while the user is working
- jump in at the first pause
- explain internal history
- defend the system
- reinterpret the user’s confusion as their mistake

## 7. Help Escalation Rules

Use this escalation ladder.

### Level 0: No Help

The user is still progressing, even if slowly.

Operator action:

- observe only

### Level 1: Clarifying Prompt

The user is stuck because the next step is ambiguous, but not blocked by a system failure.

Operator action:

- ask a small redirecting question or point back to the quickstart

Example:

```text
What does the quickstart say the next command should be after diagnose?
```

### Level 2: Minimal Intervention

The user is blocked by a confusing but recoverable step.

Operator action:

- provide the smallest useful hint

Example:

```text
The system expects `.ail/source.ail` to remain the source of truth.
```

### Level 3: Trial Rescue

The user is blocked by a real issue that prevents any further progress.

Operator action:

- help them continue
- record the exact rescue point as a product gap

If a Level 3 intervention is needed, treat that step as a meaningful failure signal, even if the user later finishes.

## 8. What To Watch For

The operator should actively watch for these signals.

### A. Source of Truth Confusion

Watch for:

- user editing generated files instead of AIL
- user asking whether generated code is the primary editable source

### B. Diagnose / Repair Confusion

Watch for:

- user not understanding why diagnose comes before compile
- user not understanding when repair should be used
- user treating repair as an automatic mandatory next step before diagnose says it is needed

### C. Compile / Sync Confusion

Watch for:

- user assuming compile already changed the local project
- user not understanding why sync is a separate step

### D. Managed vs Custom Confusion

Watch for:

- user not understanding why sync refuses overwrite
- user not understanding where custom code should live

### E. Profile Expectation Mismatch

Watch for:

- user expecting a broader system than the selected frozen profile supports
- user assuming `app_min` or arbitrary backend breadth is part of the current supported path

## 9. What To Record Verbatim

Try to record exact user language for:

- first moment of confusion
- first blocker
- first expression of lost confidence
- first point where the product feels useful

These phrases are more valuable than operator paraphrases.

## 10. Session Structure

Suggested session structure:

### Part 1. Setup

- confirm environment
- give the requirement
- give the quickstart
- prefer `trial-run` as the entry command instead of manually stitching the full path unless the session is explicitly testing command-by-command understanding

### Part 2. Silent Run

- let the user begin with minimal intervention

Current expected frozen-profile behavior:

- after `generate`, the user should normally be able to run `diagnose` and continue without immediate repair on the standard example prompts

If they reach for `repair` immediately without diagnosis requiring it, treat that as a useful product-understanding signal.

### Part 3. Guided Recovery

- if blocked, use the escalation ladder

### Part 4. Short Debrief

Ask:

- what was the most confusing step?
- what felt smooth?
- what would you expect next?
- would you try this again without assistance?

## 11. How To Classify Issues

When recording issues, put them into one of these buckets:

- `documentation_gap`
- `cli_ux_gap`
- `error_clarity_gap`
- `profile_expectation_gap`
- `workflow_gap`

Use the simplest fitting category.

Do not create new categories during the trial unless absolutely necessary.

## 12. What Counts As A Good Trial

A good trial is not one where the operator makes the session feel smooth.

A good trial is one where:

- the user’s real friction becomes visible
- the friction is captured clearly
- the user reaches enough of the workflow to produce actionable evidence

## 13. What Counts As A Strong Success

Strong success means:

- the user completes the golden path
- needs only light prompts
- understands AIL as source of truth
- understands compile vs sync
- understands that `repair` is a recovery tool, not the default first action
- sees the generated result as useful

## 14. What Counts As A Red Flag

Red flags include:

- user cannot tell what to do after generate
- user treats generated files as the primary editable artifact
- user cannot understand diagnose or repair
- standard frozen-profile examples still require immediate repair to progress
- user cannot recover from sync conflict semantics
- user finishes only because the operator effectively drove the session

## 15. Post-Trial Operator Tasks

Immediately after the session:

1. complete `/Users/carwynmac/ai-cl/testing/results/first_user_trial_template.md`
2. classify the main issues
3. write the smallest fixes first
4. avoid expanding scope beyond the frozen-profile v1 path

## 16. Operator Reminder

Your role is to reveal the truth about the current product path, not to protect the product from honest friction.

That makes the trial more useful, not less.
