# First User Trial Round 2 Summary 2026-03-17

## Purpose

This document summarizes the second controlled AI-operated frozen-profile trial run after the CLI generate-path fix.

It should be read together with:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_004.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_005.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_006.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_summary_20260317.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_summary_post_fix_20260317.md`

## Scope

The same three frozen-profile scenarios were re-run:

- `landing`
- `ecom_min`
- `after_sales`

Canonical path executed:

```text
init
  -> generate
  -> diagnose
  -> compile --cloud
  -> sync
```

## Results

### Completion

- total trials: `3`
- completed: `3`
- failed: `0`

### First-Pass Diagnose Outcome

- first-pass diagnose success: `3/3`
- first-pass diagnose failure: `0/3`

### Repair Requirement

- repair required: `0/3`
- repair not required: `3/3`

### Compile / Sync Outcome

- compile success: `3/3`
- sync success: `3/3`

## Main Finding

The frozen-profile CLI golden path now behaves consistently as a true first-pass path:

- `generate` writes diagnose-compatible user source
- `diagnose` passes immediately
- `compile --cloud` succeeds
- `sync` succeeds

The previously mandatory repair step has been removed from the standard frozen-profile happy path.

## Residual Friction

No blocking friction was observed in the second round.

The remaining non-blocking friction is warning noise:

- generate still reports fallback-generator usage when the cloud generate endpoint is unavailable in the local environment
- compile still reports current compiler compatibility insertion of `^SYS[CLIProject]`

These warnings do not prevent task completion, but they are now the clearest remaining UX rough edges on the happy path.

## Comparison With Round 1

### Round 1

- `generate -> diagnose` failed on all `3/3` frozen-profile trials
- `repair` was required on all `3/3`

### Round 2

- `generate -> diagnose` passed on all `3/3`
- `repair` was required on `0/3`

## Interpretation

This is the strongest product-quality improvement observed so far on the frozen-profile CLI path.

What it means:

- the golden path is now substantially smoother
- repair has returned to its intended role as recovery, not default first action
- the next round of UX work should focus on warning quality, not workflow correctness

## One-Line Conclusion

The second controlled frozen-profile trial confirms that the CLI golden path now succeeds cleanly without repair on the standard v1 examples, with only minor residual warning noise remaining.
