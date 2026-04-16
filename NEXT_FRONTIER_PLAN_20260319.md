# Next Frontier Plan 2026-03-19

## Purpose

This document defines the next frontier after the current frozen-profile CLI product closure work.

It exists to answer four practical questions:

1. what is already complete enough to stop treating as the main build target
2. what the product can realistically do today
3. what remains outside the current supported product surface
4. what the next development frontier should be without rewriting the entire v1 plan

This document is not a replacement for:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`

It is the continuation layer after most of the original v1 CLI-first frozen-profile plan has already been executed.

## Current Position

The project has moved beyond:

- proving the CLI workflow is possible
- patching obvious frozen-profile first-pass failures
- assembling basic docs and trial scaffolding

The project is now in a different state:

- frozen-profile product closure is largely complete
- the CLI-first control plane is now coherent
- project/workspace/release entrypoints exist and are guarded
- preview handoff now extends into concrete target resolution and inspection

The current system is best understood as:

- a CLI-first AIL v1 system with a stable website-oriented frozen product surface
- a growing platform control layer above that product surface

## What Is Already Complete Enough

These areas should no longer be treated as the main frontier unless they regress:

### 1. Frozen-profile golden path

The canonical workflow is now working and guarded:

```text
init
  -> generate
  -> diagnose
  -> repair if needed
  -> compile --cloud
  -> sync
```

References:

- `/Users/carwynmac/ai-cl/testing/run_cli_checks.sh`
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`
- `/Users/carwynmac/ai-cl/testing/results/trial_run_smoke_results.json`

### 2. Frozen-profile product boundary

The supported frozen product surface is now stable enough to treat as intentional:

- `landing`
- `ecom_min`
- `after_sales`

Experimental only:

- `app_min`

References:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`
- `/Users/carwynmac/ai-cl/benchmark/results/latest/benchmark_results.json`

### 3. Project and workspace workbench

The project/workspace/release control surfaces now exist and are protected:

- `project summary`
- `project preview`
- `project open-target`
- `project inspect-target`
- `project check`
- `project doctor`
- `project continue`
- `project go`
- `workspace status`
- `workspace summary`
- `workspace preview`
- `workspace open-target`
- `workspace doctor`
- `workspace continue`
- `workspace go`
- `rc-check`
- `rc-go`

References:

- `/Users/carwynmac/ai-cl/cli/ail_cli.py`
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`
- `/Users/carwynmac/ai-cl/testing/results/rc_checks_results.json`
- `/Users/carwynmac/ai-cl/testing/results/readiness_snapshot.json`

### 4. Trial and RC operational surface

The system now has:

- single-trial recording
- batch-trial recording
- RC aggregation
- readiness snapshots
- converged workbench primary-action signals
- converged trial-entry route signals

References:

- `/Users/carwynmac/ai-cl/testing/run_trial_recording.sh`
- `/Users/carwynmac/ai-cl/testing/run_trial_batch_recording.sh`
- `/Users/carwynmac/ai-cl/testing/run_rc_checks.sh`
- `/Users/carwynmac/ai-cl/testing/run_readiness_snapshot.sh`

## What The Product Can Realistically Do Today

### 1. Personal site / independent site

This is supported today.

Strong-fit outputs include:

- personal homepage
- creator or freelancer site
- portfolio-like personal site
- service landing page
- simple content-forward single-person brand site

Recommended profile:

- `landing`

### 2. Company introduction and product website

This is supported today and is one of the strongest current surfaces.

Strong-fit outputs include:

- company introduction site
- SaaS product website
- startup landing site
- feature and pricing pages
- FAQ / team / contact / stats / logo wall style pages

Recommended profile:

- `landing`

### 3. Minimal ecommerce independent site

This is supported today inside the `ecom_min` boundary.

Strong-fit outputs include:

- storefront homepage
- product list and product detail pages
- cart
- checkout surface
- category navigation
- shop header / shop page
- simple store-oriented funnel

Recommended profile:

- `ecom_min`

### 4. After-sales workflow website

This is supported today inside the `after_sales` boundary.

Strong-fit outputs include:

- refund request surface
- exchange request surface
- complaint submission
- contact / support flow

Recommended profile:

- `after_sales`

## What The Product Does Not Yet Support As A Formal Promise

### 1. Full application generation

This is still not part of the supported v1 product promise.

Why:

- `app_min` remains experimental
- benchmark global release semantics still fail outside the frozen website-oriented baseline

That means the project should not yet claim:

- general app generation
- arbitrary dashboard / admin app generation
- broad application-type coverage

### 2. Full blog platform or CMS

The current system can produce blog-like or content-site outputs, but it should not yet be described as a complete blog product generator.

Not yet supported as a formal promise:

- authoring CMS
- article management backend
- comments system
- search system
- editorial workflow

### 3. Full ecommerce platform

The current system can produce minimal ecommerce storefronts, but it is not yet a full ecommerce platform generator.

Not yet supported as a formal promise:

- merchant admin
- order operations center
- advanced payment orchestration
- inventory system
- complex membership system

### 4. IDE-first or Studio-first product surface

The system has docs and retained secondary paths, but the mainline product surface is still CLI-first.

That should remain explicit until a later stage intentionally promotes:

- Studio
- IDE integration

## Progress Against The Original v1 Plan

### Relative to `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`

Estimated completion:

- `85%` to `90%`

Reasoning:

- core functional areas are implemented
- frozen-profile primary workflow is working
- cloud compile/query and local sync are working
- workbench/control surfaces now exist above the core workflow

What is still outside full completion:

- app-class product surface
- richer artifact distribution beyond descriptor-level handoff
- promoted IDE/Studio product path

### Relative to `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`

Estimated completion:

- `80%` to `85%`

Reasoning:

- Phase 1 is effectively complete
- Phase 2 is effectively complete
- Phase 3 is mostly complete
- Phase 4 is only partially complete

The main remaining unclosed area is not CLI correctness.

It is the next strategic product decision about what comes after frozen-profile CLI closure.

## Recommended Next Frontier

The next frontier should not be:

- more low-level frozen-profile patch churn
- broad profile expansion
- premature `app_min` promotion
- rewriting the core v1 plan from scratch

The next frontier should be:

### A. Website-surface productization

We should treat the website-oriented frozen surface as a real product line.

That means improving:

- handoff quality
- artifact inspection and preview flow
- packaging for repeatable usage
- clearer output expectations by supported site type

### B. Artifact / preview productization

We already have:

- preview handoff
- open-target
- inspect-target

The next layer is to make artifact and preview usage feel more like a coherent workflow and less like a set of adjacent commands.

### C. Explicit `app_min` strategy

We need a decision, not drift.

The project should explicitly decide whether `app_min` is:

1. staying experimental for the near term
2. entering a separate hardening phase
3. blocked until the website-oriented surface is fully productized

Recommended current answer:

- keep `app_min` experimental
- do not let it redefine the current main frontier

### D. Secondary-surface sequencing

We should decide the order for:

- Studio
- IDE integration

But as a sequencing decision, not as a parallel product build now.

Recommended current answer:

- CLI-first remains the mainline
- Studio / IDE remain explicitly secondary until the website-oriented product surface is more fully packaged

## Should We Rewrite The Plan Documents?

Recommended answer:

- no full rewrite

Reason:

- the original v1 spec and execution plan are still directionally correct
- the project did not invalidate them
- the project largely executed them

What we need now is:

- a continuation document
- not a replacement document

That means:

- keep `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- keep `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`
- use this document as the next-stage continuation layer

## Recommended Immediate Next Build Themes

### Priority 1

Keep pushing productized website-surface usage and preview flow.

### Priority 2

Improve artifact and preview consumption paths, not just generation.

### Priority 3

Make a deliberate `app_min` decision without letting it hijack the frozen-profile product line.

## One-Line Summary

The project has largely completed the original CLI-first frozen-profile v1 closure plan; the next frontier is not another rewrite, but a deliberate move from stable website generation workflow into clearer website-surface productization and explicit experimental-app strategy.
