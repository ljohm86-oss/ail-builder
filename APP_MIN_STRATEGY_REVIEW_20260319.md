# App Min Strategy Review 2026-03-19

## Purpose

This document reviews the current status of `app_min` and defines the recommended strategy for it after the main frozen website-oriented v1 path has largely closed.

It exists to answer three practical questions:

1. what `app_min` currently is
2. why it should or should not become a near-term primary development frontier
3. what conditions would justify promoting it later

Use this together with:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json`

## Current Status

`app_min` is currently:

- visible
- tested
- intentionally experimental
- outside the formal frozen release baseline

That status is already reflected in the main project docs:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`

## What The Current Evidence Says

### 1. Frozen baseline is green without `app_min`

Current benchmark state:

- `release_decision = fail`
- `release_baseline.ok = true`
- `release_baseline.total = 16`
- `release_baseline.passed = 16`
- `release_baseline.failed = 0`

Reference:

- `/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json`

Interpretation:

- the supported website-oriented frozen surface is healthy
- the global benchmark is still held back by non-frozen scope
- `app_min` is the clearest example of why global release semantics are still broader than the current formal product promise

### 2. `app_min` still attracts boundary pressure

Current testing evidence still shows repeated `app_min` pressure around:

- auth / login
- API / backend-like constructs
- multi-page expansion
- app-boundary drift

References:

- `/Users/carwynmac/ai-cl/testing/repair_smoke_runner.py`
- `/Users/carwynmac/ai-cl/testing/results/raw_model_outputs_results.json`
- `/Users/carwynmac/ai-cl/testing/results/dictionary_gap_report.md`
- `/Users/carwynmac/ai-cl/testing/results/evolution_loop_report.md`

Interpretation:

- `app_min` is not just "one more profile"
- it naturally pulls the system toward a broader class of application semantics than the current frozen website surface

### 3. Repair can often collapse `app_min` back to a narrow boundary, but that is not the same as product closure

The current system can often rescue `app_min`-style outputs by collapsing them back into a narrow single-page app boundary.

That is useful, but it does not prove:

- a mature app product surface
- a stable first-user app path
- a clear application support promise

It proves:

- the system has a recoverable experimental app lane

That is a different thing.

## Why `app_min` Should Not Become The Main Near-Term Frontier

### 1. It would distort the current product truth

The project's strongest honest product truth today is:

- website-oriented frozen generation is working
- project/workspace/release control planes are coherent
- preview and artifact handoff are now productizing

If `app_min` becomes the main frontier too early, the product story will stop matching the strongest current system truth.

### 2. It would pull the team back into boundary-churn work

The current next frontier is higher-level productization:

- website support clarity
- preview consumption
- operator and workbench flow
- packaging and release discipline

Promoting `app_min` now would pull primary effort back into:

- boundary suppression
- auth/backend drift handling
- broader app semantics
- more patch-style governance pressure

That would be a real context shift, not a small extension of the current track.

### 3. It is not required to make the current product line stronger

The website-oriented line can still grow substantially without `app_min`.

There is still room to improve:

- website surface packaging
- preview/product usage flow
- artifact consumption
- clearer supported site-type positioning
- more intentional operator and release flow

So `app_min` is not the next required step for value creation.

## Recommended Strategy

### Recommended Answer

Keep `app_min` experimental for the near term.

That means:

- do not promote it into the frozen product surface yet
- do not let it redefine RC or release semantics
- do not let it take over the main development frontier
- continue to keep it visible as an experimental lane

### Practical Product Positioning

Current recommended wording:

- website generation is part of the supported surface
- application generation remains experimental

That keeps the product promise aligned with the actual strongest part of the system.

## What Still Makes `app_min` Worth Keeping

Keeping `app_min` visible is still useful because it gives us:

- an experimental research lane
- a pressure test for profile-boundary enforcement
- early signal on future app product direction
- a place to accumulate app-oriented evidence without polluting the mainline promise

So the recommendation is not:

- remove `app_min`

It is:

- keep `app_min`, but keep it clearly off the primary product promise

## Conditions That Would Justify Promotion Later

`app_min` should only be reconsidered for promotion if most of the following become true:

### A. Benchmark semantics improve for `app_min`

We need more than “repair can rescue it”.

We need:

- stable first-pass behavior
- clearer benchmark pass conditions
- less recurring boundary pressure

### B. A credible app user path exists

Not just:

- generate
- repair

But a believable application-oriented first-user path that does not mostly feel like boundary recovery.

### C. Product boundary can be stated honestly

We would need to be able to say, in one sentence, what kind of app is actually supported.

For example:

- single-page mobile-like content app
- simple chat-like front surface
- simple list/detail single-view app

Until that sentence is stable, promotion would still be premature.

### D. It stops competing with the website-oriented mainline

Promotion should happen only after the website-oriented product line is sufficiently packaged that app work will not derail it.

## Recommended Near-Term Actions

### 1. Keep `app_min` explicitly experimental

Do not change:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`

to treat `app_min` as frozen.

### 2. Do not rewrite the main plan around `app_min`

Instead:

- keep the current continuation strategy in `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`

### 3. Revisit only after the website-oriented next frontier has advanced

The current priority should remain:

- supported website/product surfaces
- preview and artifact productization
- clearer usage flow

Then `app_min` can be revisited as a separate promotion decision, not a background assumption.

## One-Line Summary

`app_min` should remain a visible experimental lane, but it should not become the main near-term development frontier or the formal product promise until it has a clearer app boundary, a stronger first-pass path, and evidence that it will not derail the now-stable website-oriented frozen product line.
