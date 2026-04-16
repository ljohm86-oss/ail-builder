# Frozen Profile Coverage Fix Plan 2026-03-17

## 1. Purpose

This document defines the next narrow product-quality fix after the frozen-profile CLI path became first-pass stable.

It is based on:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_batch_expanded_summary_20260317.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_007.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_008.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_010.md`

This is not a new token plan.

It is a coverage plan for already-supported frozen-profile sections that are not being hit reliably enough on richer prompts.

## 2. Current Situation

The frozen-profile CLI path is now workflow-stable:

- `generate -> diagnose` passes
- `compile --cloud` succeeds
- `sync` succeeds
- immediate `repair` is no longer required on the standard examples

That means the mainline problem has moved.

The current issue is no longer path correctness.

It is richer prompt coverage quality.

## 3. What The Expanded Trial Showed

The expanded batch showed two different classes of result.

### A. Healthy cases

These completed cleanly and also felt coverage-appropriate:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_009.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_011.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_012.md`

### B. Coverage-underhit cases

These completed cleanly, but under-hit explicitly requested supported sections:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_007.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_008.md`
- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_010.md`

This means the problem is now:

- not “can the system finish?”
- but “does first-pass generation use enough of the supported frozen-profile surface when the prompt is richer?”

## 4. In-Scope Fix Targets

This fix plan only covers already-supported tokens and sections.

### Landing

Improve first-pass hit rate for:

- `landing:Team`
- `landing:FAQ`
- `landing:Stats`
- `landing:LogoCloud`

especially when explicitly requested alongside other valid landing sections.

### E-commerce

Improve first-pass hit rate for:

- `ecom:Banner`
- `ecom:CategoryNav`
- `ecom:ShopHeader`

when the requirement explicitly asks for richer commerce structure that is already supported.

## 5. Explicit Non-Goals

This fix plan does not include:

- new token creation
- new alias patching
- profile expansion
- compiler rewrite
- benchmark policy changes
- `app_min` improvements
- Studio work

## 6. Coverage Gaps To Fix

### Gap A. Richer landing prompts collapse to the minimum landing skeleton too often

Observed examples:

- richer landing prompt requested `团队` and `FAQ`
- output only stably hit `Testimonial` and `Contact`

Observed example:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_007.md`

### Gap B. Landing data/logo prompts do not reliably activate all already-supported richer sections

Observed examples:

- prompt requested `团队介绍`
- prompt requested `公司数据展示`
- prompt requested `合作伙伴 Logo`

Output hit:

- `LogoCloud`
- `Contact`

But under-hit:

- `Team`
- `Stats`

Observed example:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_008.md`

### Gap C. Richer ecom prompts still collapse to the minimum commerce path

Observed examples:

- prompt requested `首页横幅`
- prompt requested `分类导航`

Output stayed valid and useful, but still collapsed to the simpler:

- header
- product grid
- product detail
- cart
- checkout

Observed example:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_results_010.md`

## 7. Likely Root Cause Direction

The current evidence suggests this is primarily a first-pass generation coverage issue, not a repair issue.

Why:

- the AIL is valid
- diagnose accepts it
- compile succeeds
- sync succeeds

So the system is not failing structurally.

It is choosing too small a supported subset of the profile surface on richer prompts.

That means the first place to improve is:

- generator-side coverage rules

not:

- repair-first rescue logic

Repair should remain available, but it should not be the primary tool for fixing this class of issue.

## 8. Recommended Fix Order

### Step 1. Tighten landing richer-coverage rules

Priority:

- highest

Reason:

- `landing` is the most visible frozen profile
- current richer prompts are still under-hitting clearly supported sections

Target:

- improve first-pass use of `Team`, `FAQ`, `Stats`, and `LogoCloud` when explicitly requested

### Step 2. Tighten ecom richer-coverage rules

Priority:

- second

Reason:

- the minimal ecom path is already strong
- the problem is richer supported-section usage, not base viability

Target:

- improve first-pass use of `Banner`, `CategoryNav`, and `ShopHeader` when explicitly requested

### Step 3. Only then consider repair-side supplementary coverage

Priority:

- third

Reason:

- repair should stay a recovery mechanism
- do not turn richer supported-section coverage into a repair-dependent path

## 9. Expected Files To Change

Primary likely files:

- `/Users/carwynmac/ai-cl/skills/ail-generator-v1.2/SKILL.md`
- `/Users/carwynmac/ai-cl/testing/real_requirements_runner.py`
- `/Users/carwynmac/ai-cl/testing/raw_model_outputs_runner.py`

Possible secondary files:

- `/Users/carwynmac/ai-cl/skills/ail-repair-v1/SKILL.md`

Try to avoid changes to:

- `/Users/carwynmac/ai-cl/cli/`
- `/Users/carwynmac/ai-cl/ail_engine_v4.py`
- `/Users/carwynmac/ai-cl/ail_engine_v5.py`
- benchmark policy or compiler behavior

## 10. Validation Plan

After the coverage fix, re-run:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/testing/run_real_requirements.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

And re-run these richer trial scenarios specifically:

- landing richer coverage
- landing data/logo coverage
- ecom banner/category coverage

Success signal:

- still `0/3` blocking failures
- still no forced repair on the frozen-profile path
- improved presence of explicitly requested supported sections

## 11. Success Criteria

This fix plan should be considered successful if:

### Required

- the frozen-profile path remains first-pass stable
- no compile or sync regressions appear
- no benchmark release regression appears

### Desired

- richer landing prompts hit more of:
  - `Team`
  - `FAQ`
  - `Stats`
  - `LogoCloud`
- richer ecom prompts hit more of:
  - `Banner`
  - `CategoryNav`
  - `ShopHeader`

## 12. One-Line Fix Decision

The next focused product-quality fix should improve first-pass coverage of already-supported richer frozen-profile sections, without reopening tokens, profiles, or compiler semantics.
