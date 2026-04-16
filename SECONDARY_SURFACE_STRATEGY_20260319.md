# Secondary Surface Strategy 2026-03-19

## Purpose

This document defines the near-term strategy for secondary product surfaces around the current CLI-first AIL system.

It exists to answer four practical questions:

1. which surface is the mainline today
2. what role IDE and Studio should play right now
3. when a secondary surface should be promoted
4. how to avoid splitting effort before the main product line is fully packaged

Use this together with:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/APP_MIN_STRATEGY_REVIEW_20260319.md`

## Current Mainline

The current mainline product surface is:

- CLI-first
- frozen-profile website-oriented
- workbench-driven
- RC/readiness guarded

That mainline now includes:

- `trial-run`
- project workbench
- workspace workbench
- preview handoff
- RC and readiness control surfaces

The current strongest product truth is not:

- IDE-first app generation
- Studio-first visual authoring
- general application generation

The current strongest product truth is:

- website-oriented generation is working inside the frozen product boundary
- the CLI control plane is coherent enough to drive the system end to end

## What Counts As A Secondary Surface

In the current project, a secondary surface means any user-facing entry layer that is not the CLI-first mainline.

Right now the two most obvious secondary surfaces are:

- IDE integration
- Studio/web visual surface

These are important, but they are not yet the product truth anchor.

## Recommended Role Of IDE Right Now

### Current Role

IDE should be treated as:

- a future convenience surface
- an integration target
- a consumer of stable CLI and cloud semantics

IDE should not yet be treated as:

- the primary product story
- the main execution surface
- the place where core product truth is decided

### Why

The project already has stable workbench semantics in CLI:

- `project summary`
- `project preview`
- `project doctor`
- `project continue`
- `project go`
- `workspace summary`
- `workspace doctor`
- `workspace continue`
- `workspace go`
- `rc-check`
- `rc-go`

That means IDE work should now be downstream of these semantics, not upstream of them.

The right near-term IDE strategy is:

- consume CLI/cloud/workbench outputs
- reuse the established action model
- avoid inventing a second control plane

## Recommended Role Of Studio Right Now

### Current Role

Studio should be treated as:

- a retained exploratory surface
- a possible future demo or guided authoring surface
- a secondary consumer of the stable CLI/cloud/workbench system

Studio should not yet be treated as:

- the primary shipping surface
- the primary trial surface
- the place where mainline feature decisions are made

### Why

The current strongest operational evidence all comes from the CLI-first path:

- CLI smoke
- trial-run
- recorded trial batches
- RC aggregation
- readiness snapshots
- converged project/workspace primary-action signals

That means Studio is not blocked forever, but it should not compete with the current mainline for product-definition authority.

## Promotion Rule For A Secondary Surface

A secondary surface should only be promoted when all of the following are true:

### 1. The CLI semantics underneath it are already stable

That means the surface should be consuming a stable mainline, not trying to define one.

### 2. The surface does not need unique product truth to function

If a surface needs its own workflow semantics, its own recovery model, or its own release rules, then it is still too early to promote it.

### 3. The surface improves access, not ambiguity

Promotion is justified only if it makes the product easier to use without making the support boundary harder to explain.

### 4. The surface can be evaluated with real guarded checks

Promotion should happen only when it can be protected by:

- smoke coverage
- trial coverage
- readiness or RC signals
- stable operator expectations

## When Not To Promote A Secondary Surface

Do not promote a secondary surface if it would:

- split core development effort away from the frozen website-oriented mainline
- create a second competing action model
- encourage premature `app_min` expansion
- blur the supported product boundary
- make release truth harder to explain

This is especially important right now because the current system has only recently converged on:

- one stable frozen product surface
- one stable project workbench primary path
- one stable trial-entry route

## Recommended Near-Term Strategy

### 1. Keep CLI as the authority surface

CLI should remain the place where:

- product truth is defined
- workbench semantics are stabilized
- recovery semantics are tested
- release and readiness truth are judged

### 2. Treat IDE as a downstream integration surface

Near-term IDE work should prioritize:

- consuming `--json` payloads
- reusing preview handoff structures
- reusing primary-action recommendations
- reusing RC/readiness outputs

It should not prioritize:

- inventing parallel workflow logic
- bypassing the CLI/cloud action model

### 3. Treat Studio as a downstream guided surface

Near-term Studio work should prioritize:

- guided consumption of stable outputs
- display and inspection of build/preview surfaces
- guided trial or demo paths if justified later

It should not prioritize:

- becoming the place where core system behavior is debugged first
- driving mainline workflow definitions

### 4. Keep website productization as the main frontier

The next mainline value is still more likely to come from:

- clearer website surface packaging
- stronger preview/artifact consumption
- better operator and workbench flow
- more explicit support positioning

than from shifting core effort into IDE or Studio promotion.

## Practical Priority Order

Recommended order for the next stage:

1. continue strengthening the CLI-first website product surface
2. continue strengthening preview and artifact consumption flows
3. make IDE a thin consumer of stable JSON and workbench semantics
4. revisit Studio only after there is a stronger reason to make it more than a retained secondary surface

## Promotion Triggers To Watch

A stronger case for IDE or Studio promotion would appear if one or more of these become true:

- the CLI mainline stops changing meaningfully and mostly needs accessibility improvements
- a recurring user group clearly wants the same workflow in a richer surface
- preview/artifact consumption becomes easier to understand visually than textually
- the secondary surface can be smoke-guarded and trial-guarded without new ambiguity

## Recommended Current Positioning

The safest accurate statement today is:

- CLI is the main product surface
- IDE and Studio are secondary surfaces
- both can grow, but neither should redefine the mainline yet

## Internal Development Implication

This strategy implies:

- do not rewrite the current CLI-first plan
- do not split the mainline into competing product surfaces
- do continue building secondary surfaces, but only as downstream consumers of the stabilized CLI/cloud/workbench model

In short:

- stabilize truth in CLI
- consume truth in secondary surfaces
- promote only when promotion reduces friction more than it increases ambiguity
