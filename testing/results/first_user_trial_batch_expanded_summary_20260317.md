# First User Trial Expanded Batch Summary 2026-03-17

## Purpose

This document summarizes an expanded controlled AI-operated frozen-profile trial batch after the first-pass CLI generate-path fix.

It extends the earlier trial evidence by testing not only the minimum happy-path examples, but also richer supported prompts.

Primary references:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_007.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_008.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_009.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_010.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_011.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_012.md`

## Scope

Six frozen-profile scenarios were executed:

- 2 `landing`
- 2 `ecom_min`
- 2 `after_sales`

The run used the current CLI golden path:

```text
init
  -> generate
  -> diagnose
  -> compile --cloud
  -> sync
```

## Results

### Workflow Stability

- total trials: `6`
- completed: `6`
- failed: `0`
- first-pass diagnose success: `6/6`
- repair required: `0/6`
- compile success: `6/6`
- sync success: `6/6`

### By Profile

- `landing`: `2/2` completed, `2/2` first-pass diagnose success
- `ecom_min`: `2/2` completed, `2/2` first-pass diagnose success
- `after_sales`: `2/2` completed, `2/2` first-pass diagnose success

## Main Finding

The frozen-profile workflow is now clearly stable at the path level.

That means:

- no blocking first-pass diagnose failures
- no mandatory repair step
- no compile failures
- no sync failures

This confirms that the earlier `^SYS[...]` first-pass mismatch was a real blocker and that its fix materially improved the product path.

## Secondary Finding

The next bottleneck is no longer workflow correctness.

It is supported-section coverage on richer prompts.

Observed pattern:

- minimal and focused prompts behaved strongly
- richer prompts still sometimes under-hit supported sections even though they remained structurally valid and compile-clean

### Observed coverage gaps

#### Landing richer coverage

Examples:

- `team`
- `FAQ`
- `stats`

The richer landing prompts remained valid, but the first-pass generated AIL did not always include all explicitly requested supported sections.

#### E-commerce richer coverage

Examples:

- `banner`
- `category navigation`

The richer ecom prompt stayed valid and usable, but sometimes collapsed back to the minimal product/cart/checkout path instead of using the richer supported ecom surface.

## Interpretation

This is a healthy shift in problem quality.

Earlier problem:

- the path itself was rough and repair-dependent

Current problem:

- the path is smooth
- richer frozen-profile prompts are not yet coverage-strong enough

That is a much better problem to have.

It means the project has moved from:

- fixing path breakage

to:

- improving first-pass quality within an already stable path

## Recommended Priority

Current priority order should now be:

1. keep the smooth first-pass frozen-profile path stable
2. improve richer prompt coverage for already-supported frozen-profile sections
3. keep `repair` available as recovery
4. do not reopen profile expansion or compiler rewrite work

## One-Line Conclusion

The expanded frozen-profile batch confirms that AIL v1 is now workflow-stable on the CLI golden path, and the next meaningful quality target is richer supported-section coverage rather than basic path correctness.
