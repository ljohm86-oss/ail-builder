# First User Trial Summary 2026-03-17

## Status Update

This summary originally recorded the first controlled frozen-profile trial before the CLI generate-path fix for `^SYS[...]`.

That issue has since been investigated and narrowly fixed in the CLI golden path.

Current status after the fix:

- the same frozen-profile example prompts now pass `generate -> diagnose` on the first pass
- `compile --cloud` still succeeds
- `sync` still succeeds

Relevant follow-up records:

- `/Users/carwynmac/ai-cl/TRIAL_FIX_INVESTIGATION_20260317.md`

This means the findings below remain historically accurate, but they no longer describe the current best-known frozen-profile quickstart behavior.

## Scope

This summary records a controlled AI-operated first-user trial across the three frozen v1 profiles:

- `landing`
- `ecom_min`
- `after_sales`

Detailed records:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_001.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_002.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_003.md`

## Trial Method

Each scenario ran the canonical v1 path:

```text
init
  -> generate
  -> diagnose
  -> repair
  -> compile --cloud
  -> sync
```

The runs were executed in isolated temporary project directories.

## Scenarios

### 1. Landing

- requirement: `做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。`
- expected profile: `landing`

### 2. E-commerce

- requirement: `做一个数码商城，包含首页商品列表、商品详情、购物车、结算。`
- expected profile: `ecom_min`

### 3. After-sales

- requirement: `做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。`
- expected profile: `after_sales`

## Results

### Completion

- total trials: `3`
- completed: `3`
- failed: `0`

### Path Health

- reached_generate: `3/3`
- reached_diagnose: `3/3`
- reached_repair: `3/3`
- reached_compile: `3/3`
- reached_sync: `3/3`

### Compile / Sync Outcome

- compile success after repair: `3/3`
- sync success after repair: `3/3`

## Main Finding At Time Of Trial

The frozen-profile v1 path is functionally complete, but the current first-pass generator output still creates avoidable friction.

Across all three scenarios:

- pre-repair diagnose returned `validation_failed`
- post-repair diagnose returned `ok`
- compile succeeded after repair
- sync succeeded after repair

## Most Important Pattern At Time Of Trial

The repeated first-trial friction was not profile confusion.

It was:

- generated AIL includes an unsupported `^SYS[...]` line in the first pass
- diagnose rejects that output as not compile-recommended
- repair fixes it immediately

This means the current user experience is:

- complete
- recoverable
- but not yet first-pass smooth

## Interpretation At Time Of Trial

This is good news and bad news.

Good:

- the frozen-profile workflow is real
- repair does its job
- compile and sync are stable

Bad:

- standard example prompts still rely on repair as a de facto mandatory first step
- users may perceive this as confusion unless we either:
  - improve first-pass generation
  - or explicitly frame repair as part of the normal path

## Recommendation At Time Of Trial

Before a broader first-user rollout, treat this as the primary UX issue to resolve:

- reduce the generator-to-diagnose mismatch for the frozen-profile examples

If that is not addressed immediately, the fallback recommendation is:

- make the quickstart and operator guide explicitly treat `diagnose -> repair` as a normal first-run path

## Historical One-Line Conclusion

The frozen-profile v1 workflow is operational end-to-end, but first-pass generator output still creates a predictable repair step that should be smoothed before broader user trials.

## Current One-Line Conclusion

The frozen-profile v1 workflow remains operational end-to-end, and the standard example prompts now reach `diagnose` cleanly on the first pass in the CLI golden path.
