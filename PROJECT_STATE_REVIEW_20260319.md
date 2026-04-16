# Project State Review 2026-03-19

## Purpose

This document is the current state review for the AIL project after the website-oriented frontier work completed on 2026-03-19.

It exists to answer:

- whether recent work has been only small polish or real product progress
- how much of the original CLI-first v1 plan is now complete
- what the system can realistically do today
- what the system still cannot honestly promise
- whether the old plan needs a rewrite
- what the next engineering frontier should be

Use this as the shortest current reality check before reading deeper planning docs.

## Short Answer

Recent work has not been random micro-polish.

What happened over the last stretch is that the project moved from:

- low-level flow success

to:

- a coherent control plane
- a coherent website product line
- repeatable delivery, preview, export, inspection, and asset-consumption surfaces

Individual commands may be small on their own, but together they closed an important product layer:

- project workbench
- workspace workbench
- release/readiness workbench
- website-oriented control surface

That is real product progress, not decorative cleanup.

## Completion Estimate Against Earlier Direction

Against:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`

current completion is best described as:

- roughly `85% to 90%`

Against:

- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`

current completion is best described as:

- roughly `80% to 85%`

Why these numbers are reasonable:

- the frozen-profile mainline is working
- compile, sync, diagnose, repair, trial, RC, and readiness are in place
- project/workspace/release workbenches exist and are guarded by smoke
- website packaging, demo, delivery, and asset-consumption layers now exist

The remaining gap is not “basic CLI viability.” It is the unfinished product surface outside the main website-oriented line:

- `app_min`
- artifact distribution beyond descriptors
- IDE / Studio implementation beyond planning and consumption contracts

## What Is Real And Stable Today

### 1. Frozen website-oriented product surface

The supported frozen product surface is now:

- `landing`
- `ecom_min`
- `after_sales`

These are the profiles behind the current main product truth.

Experimental only:

- `app_min`

### 2. Canonical CLI flow

The mainline flow is stable:

```text
init
  -> generate
  -> diagnose
  -> repair if needed
  -> compile --cloud
  -> sync
```

This is no longer just “possible.” It is guarded by:

- `/Users/carwynmac/ai-cl/testing/run_cli_checks.sh`
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`

### 3. Project / workspace / release control plane

These surfaces now exist and have converged semantics:

- `project summary`
- `project preview`
- `project open-target`
- `project inspect-target`
- `project run-inspect-command`
- `project export-handoff`
- `project check`
- `project doctor`
- `project continue`
- `project go`
- `workspace status`
- `workspace summary`
- `workspace preview`
- `workspace open-target`
- `workspace inspect-target`
- `workspace run-inspect-command`
- `workspace export-handoff`
- `workspace doctor`
- `workspace continue`
- `workspace go`
- `rc-check`
- `rc-go`

This is important because the product now has:

- inspection
- recovery
- high-level execution
- handoff export

at more than one level of abstraction.

### 4. Website product line

The website line is now much more than a matrix or promise sheet.

It has:

- support boundary docs
- product packs
- requirement templates
- delivery checklist
- demo pack
- sales positioning
- frontier summary
- reusable delivery assets
- validated website delivery evidence
- executable website CLI surfaces

Current website-oriented CLI line:

- `website check`
- `website assets`
- `website open-asset`
- `website inspect-asset`
- `website preview`
- `website run-inspect-command`
- `website export-handoff`
- `website summary`
- `website go`

That means the website product line now has:

- qualification
- asset consumption
- preview
- inspection
- handoff export
- high-level execution

not just documentation.

## What The System Can Do Today

### Supported

These are the safest current “yes” answers.

#### Personal independent site

Supported.

Good fit:

- creator site
- freelancer site
- portfolio-like site
- service website
- personal independent landing site

Recommended profile:

- `landing`

#### Company introduction and product website

Supported.

Good fit:

- company introduction site
- SaaS product website
- startup landing site
- feature / FAQ / contact / team / pricing style pages

Recommended profile:

- `landing`

#### Minimal ecommerce independent storefront

Supported.

Good fit:

- storefront homepage
- product list
- product detail
- cart
- checkout
- category navigation

Recommended profile:

- `ecom_min`

#### After-sales service website

Supported.

Good fit:

- refund request
- exchange request
- complaint submission
- support contact flow

Recommended profile:

- `after_sales`

### Partial

#### Blog-style personal site

Partial.

Good fit:

- personal blog-style website
- content-forward website
- simple article-list style site

Safe positioning:

- a blog-style website

Unsafe positioning:

- full blog platform
- CMS
- publishing backend

## What The System Cannot Honestly Promise Yet

### 1. Full application generation

Still not a formal promise.

Do not position the product as:

- a general app generator
- a dashboard generator
- an internal tool generator
- a broad application platform

Why:

- `app_min` is still experimental
- the mainline frozen website boundary is green, but the broader app surface is not

### 2. Full blog or CMS platform

Still not supported as a product promise.

Do not promise:

- CMS authoring workflows
- article management backend
- comment systems
- publishing console
- rich content operations

### 3. Full ecommerce platform

Still not supported as a product promise.

Do not promise:

- merchant back office
- complex order operations
- advanced inventory systems
- full platform commerce admin

### 4. Full artifact distribution service

The system can describe artifacts and route users to them, but it is not yet a fully developed artifact distribution platform.

Current state:

- descriptor-level artifact support exists
- preview / open-target / inspect-target / export-handoff exist

Still not true:

- signed downloadable artifacts
- full remote artifact hosting/distribution

## Evidence That The Website Line Is Real

The strongest current evidence set is:

- `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/website_demo_pack_run_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/website_delivery_assets_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`

What these collectively show:

- supported website packs validate cleanly
- demo packs run cleanly
- reusable delivery assets are built
- website CLI surfaces are wired into smoke

## Do We Need To Rewrite The Old Plan?

No.

A full rewrite of the earlier plan would add churn without much value.

The earlier documents are still directionally correct:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`

The better approach is what the repo already started doing:

- keep the original v1 plan
- add continuation and frontier documents for the current phase

That is why these newer docs matter:

- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_FRONTIER_SUMMARY_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_NEXT_TASKS_20260319.md`
- `/Users/carwynmac/ai-cl/APP_MIN_STRATEGY_REVIEW_20260319.md`
- `/Users/carwynmac/ai-cl/SECONDARY_SURFACE_STRATEGY_20260319.md`

So the right move is:

- do not rewrite the old plan
- keep using continuation documents for the current frontier

## What The Next Engineering Frontier Should Be

The next frontier should not be “more website boundary definition.”

That part is already in good shape.

The next frontier should be:

### 1. Better consumption of the website product line

Continue turning the website line into a more direct delivery and operator surface.

Good examples:

- make website-oriented assets easier to consume
- tighten website-oriented preview / handoff usage
- keep the website control plane coherent

### 2. Better website delivery experience

Focus on real delivery/operator ergonomics instead of re-litigating support boundaries.

Good examples:

- website-oriented summaries
- website-oriented export payloads
- clearer delivery bundles

### 3. Keep `app_min` out of the mainline until it earns promotion

This is still the right guardrail.

Do not let website momentum get diluted by reopening app promises too early.

### 4. Treat IDE and Studio as consumers, not new truth layers

This is already captured in:

- `/Users/carwynmac/ai-cl/SECONDARY_SURFACE_STRATEGY_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_CONSUMPTION_PLAN_20260319.md`

The key rule remains:

- CLI is still the primary truth layer

## One-Line Summary

AIL is no longer just a CLI experiment with frozen-profile success; it is now a coherent CLI-first website-oriented product line with a real control plane, real delivery evidence, and clear boundaries, while application generation, CMS promises, and full platform promises remain intentionally outside the current mainline.
