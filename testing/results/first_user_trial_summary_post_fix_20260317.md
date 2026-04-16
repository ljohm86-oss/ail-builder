# First User Trial Summary Post-Fix 2026-03-17

## Purpose

This document records the controlled frozen-profile trial status after the CLI generate-path fix that removed the first-pass `^SYS[...]` mismatch from persisted user source.

It should be read together with:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_summary_20260317.md`
- `/Users/carwynmac/ai-cl/TRIAL_FIX_INVESTIGATION_20260317.md`

The earlier summary remains the historical pre-fix record.

This document captures the current post-fix state.

## Scope

The same three frozen v1 profiles were rechecked on the canonical CLI path:

- `landing`
- `ecom_min`
- `after_sales`

Canonical path:

```text
init
  -> generate
  -> diagnose
  -> compile --cloud
  -> sync
```

`repair` remains available, but it is no longer expected as the default first-run step for these standard example prompts.

## Rechecked Scenarios

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

### First-Pass Diagnose Outcome

- pre-repair diagnose success: `3/3`
- pre-repair diagnose failure: `0/3`

### Compile / Sync Outcome

- compile success: `3/3`
- sync success: `3/3`

## Main Finding

The frozen-profile CLI golden path now behaves the way v1 should feel to a first user:

- `generate` writes diagnose-compatible `.ail/source.ail`
- `diagnose` succeeds on the first pass for the standard frozen-profile examples
- `compile --cloud` still succeeds
- `sync` still succeeds

## What Changed

Before the fix:

- generated AIL persisted `^SYS[...]` into user source
- diagnose rejected that output
- repair became a de facto mandatory first step

After the fix:

- `^SYS[...]` is no longer persisted into `.ail/source.ail` on the CLI generate path
- compile-side compatibility normalization remains in place
- the standard frozen-profile examples no longer require immediate repair

## Interpretation

This is a meaningful product-quality improvement.

What improved:

- first-run friction decreased
- the quickstart path became clearer
- frozen-profile examples now better match user expectation

What did not change:

- compile compatibility behavior remains stable
- sync behavior remains stable
- repair is still available for noisy AIL and non-golden-path inputs

## Current Recommendation

The frozen-profile quickstart can now be presented as:

```text
generate
  -> diagnose
  -> compile --cloud
  -> sync
```

with:

- `repair` kept as a recovery step when needed
- not as the expected first action for standard examples

## One-Line Conclusion

After the CLI generate-path fix, the frozen-profile v1 golden path now passes `generate -> diagnose -> compile -> sync` cleanly on the first pass for the standard example prompts.
