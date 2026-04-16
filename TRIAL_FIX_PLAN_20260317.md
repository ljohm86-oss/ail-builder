# Trial Fix Plan 2026-03-17

## 1. Purpose

This document turns the first controlled user trial findings into a focused fix plan.

It exists to answer:

- what the most important product friction is right now
- whether it should be treated as a v1 priority
- what should be fixed first
- how to validate that the fix worked

This is not a broad roadmap.

It is a narrow plan based on the most important issue surfaced in:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_summary_20260317.md`

## 2. Core Finding

Across all three frozen-profile trial scenarios:

- `landing`
- `ecom_min`
- `after_sales`

the same pattern appeared:

1. `generate` produced AIL
2. `diagnose` returned `validation_failed`
3. `repair` fixed the AIL immediately
4. `compile --cloud` succeeded
5. `sync` succeeded

The recurring reason was:

- generated AIL included an unsupported `^SYS[...]` line on first pass

This means the current v1 path is:

- operational
- recoverable
- but unnecessarily rough on first contact

## 3. Why This Matters

This issue is now the highest-priority UX problem for the frozen-profile path.

Why:

- it affects the first impression
- it appears on the standard supported examples
- it is repeated across all three frozen profiles
- it makes the user feel that generation failed even though the system is actually close to success

This is a stronger v1 priority than:

- adding more token coverage
- expanding profiles
- improving experimental `app_min`
- doing more local cleanup

## 4. Product Decision

Treat this as a v1 product-closure issue, not a minor polish issue.

Desired v1 behavior:

- standard frozen-profile example prompts should ideally pass `diagnose` immediately after `generate`

Fallback acceptable behavior:

- if that is not yet true, the quickstart and trial materials must clearly present `diagnose -> repair` as a normal first-run path

## 5. Fix Goal

Primary goal:

Reduce or eliminate the generator-to-diagnose mismatch on the standard frozen-profile golden path.

Operational interpretation:

- frozen profile first-pass generate output should be closer to compile-candidate quality

## 6. Candidate Fix Directions

There are two realistic paths.

### Option A. Improve First-Pass Generate Output

Goal:

- make `generate` produce AIL that diagnose accepts without the mandatory repair step for standard frozen-profile prompts

Likely area:

- generator path
- CLI generation path if local wrapper behavior is involved
- generator skill alignment

Benefits:

- best first-run user experience
- less confusion
- cleaner story for quickstart and trials

Risks:

- can spill into broader generator behavior if not kept narrow

### Option B. Keep Repair in the Golden Path, But Normalize It

Goal:

- accept that first-pass generation may still need repair
- make that expectation explicit and smooth

Likely area:

- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
- `/Users/carwynmac/ai-cl/FIRST_USER_TRIAL_OPERATOR_GUIDE.md`
- CLI messaging around diagnose / repair

Benefits:

- low engineering risk
- fast to roll out

Risks:

- preserves avoidable friction
- weakens the perception of generation quality

## 7. Recommended Priority Order

Recommended order:

### Step 1

Do the smallest possible root-cause investigation for the `^SYS[...]` first-pass mismatch.

Question to answer:

- is this coming from the generator output itself, from CLI wrapping, or from diagnose expectations?

### Step 2

If the mismatch can be fixed narrowly, fix generation first.

Desired outcome:

- frozen-profile first-pass examples become diagnose-clean

### Step 3

If the mismatch cannot be fixed quickly, improve quickstart wording and CLI messaging immediately so the user understands repair is the expected next step.

### Step 4

Re-run the same three trial scenarios and compare results.

## 8. What Not To Do

Do not respond to this finding by:

- expanding profile scope
- broadening benchmark
- changing release policy
- adding unrelated token patches
- rewriting compile pipeline
- treating this as a generic “generator quality” project

Keep the fix narrow:

- frozen-profile examples
- first-pass generate
- diagnose/repair path clarity

## 9. Validation Plan

Use the exact same three controlled scenarios again:

1. `landing`
2. `ecom_min`
3. `after_sales`

Success target:

- `generate -> diagnose` succeeds directly for more of the frozen-profile examples

Minimum fallback target:

- if pre-repair diagnose still fails, the user-facing guidance must make the recovery path feel expected and easy

Suggested evidence files:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_001.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_002.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_003.md`
- new rerun results after the fix

## 10. Success Criteria

This fix effort should be considered successful if one of these becomes true:

### Preferred Success

- standard frozen-profile examples pass `diagnose` immediately after `generate`

### Acceptable Success

- first-pass diagnose may still fail
- but the user experience is clearly framed and low-friction
- and the controlled trial no longer treats the step as a confusing failure

## 11. Current Recommendation

Recommended next move:

1. investigate the exact source of the `^SYS[...]` mismatch
2. attempt a narrow generator-side fix first
3. if not immediately fixable, improve the quickstart and CLI messaging as a temporary experience fix

## 12. One-Line Fix Decision

The next v1 product fix should focus on removing the repeated first-pass generate-to-diagnose mismatch on frozen-profile examples, because it is now the clearest blocker to a smooth first user experience.
