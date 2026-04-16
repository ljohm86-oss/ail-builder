# Next Development Research 2026-03-17

## Purpose

This document identifies the most valuable next development step now that:

- the frozen-profile CLI path is first-pass stable
- richer frozen-profile coverage no longer shows active blocker-level misses
- evolution loop reports no active patch pressure

This is not a patch plan.

It is a product-development focus recommendation.

## Current Starting Point

The current system already has:

- a coherent CLI golden path
- stable frozen profiles:
  - `landing`
  - `ecom_min`
  - `after_sales`
- release gate documentation
- quickstart documentation
- frozen-profile example prompts
- controlled AI-operated trial evidence

Primary references:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`
- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`
- `/Users/carwynmac/ai-cl/FIRST_USER_TRIAL_PLAN.md`
- `/Users/carwynmac/ai-cl/V1_PROGRESS_REVIEW_20260317.md`
- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_COVERAGE_PROGRESS_20260317.md`

## What The Project No Longer Needs Most

The project does not primarily need:

- more token work
- more alias normalization work
- more frozen-profile coverage patching
- more local cleanup work
- broader profile expansion

Those are no longer the shortest path to user-visible progress.

## What The Project Still Lacks

The biggest remaining gap is not capability.

It is product packaging.

The current path still expects the user to manually execute a multi-step CLI flow:

```text
init
  -> generate
  -> diagnose
  -> compile --cloud
  -> sync
```

That path is now stable, but it is still spread across several commands and still assumes the user knows how to interpret the outcome after sync.

## Recommended Next Development Focus

### Primary recommendation

Build a single controlled first-user entrypoint for the frozen-profile CLI path.

Best current shape:

- a one-command trial runner or demo launcher
- scoped only to the frozen profiles
- built on top of the existing CLI rather than replacing it

Examples of acceptable forms:

- `demo_v1.sh`
- `start_v1_trial.sh`
- `python3 -m cli trial-run ...`

The exact interface can vary.

The key is that the user gets one guided path rather than stitching together the quickstart manually.

## Why This Is The Best Next Step

### 1. It uses what is already stable

The current CLI path is already strong enough.

A one-command wrapper would reuse:

- `ail init`
- `ail generate`
- `ail diagnose`
- `ail compile --cloud`
- `ail sync`

### 2. It reduces the highest remaining friction

The next friction is not failed generation.

It is:

- command sequencing
- confidence about what to run next
- interpreting the result after sync

### 3. It creates a real product surface

A guided entrypoint turns the current system from:

- a working toolchain

into:

- a guided first-user experience

That is the most leverage-heavy shift available right now.

## Recommended Scope For The Next Development Step

### In scope

- one-command frozen-profile trial runner
- use only current frozen profiles
- reuse current CLI commands internally
- print a concise progress summary
- write outputs to a predictable temp or working directory
- end with a clear “what to open / what to inspect next” message

### Out of scope

- Studio-first flow
- new compiler work
- profile expansion
- `app_min` promotion
- patch compile
- interactive terminal wizard complexity

## Candidate Design

### Minimal viable design

A shell or Python wrapper that:

1. creates a trial project
2. runs `generate`
3. runs `diagnose`
4. runs `repair` only if needed
5. runs `compile --cloud`
6. runs `sync`
7. prints:
   - project path
   - detected profile
   - whether repair was needed
   - where managed files were written

### Suggested success signal

The user should be able to get from requirement to synced generated project with one command and one resulting project path.

## Secondary Development Option

If the one-command entrypoint is intentionally deferred, the next-best development step would be:

- a preview/serve handoff guide or lightweight preview launcher

But this is second-best because the current bigger gap is still path packaging, not serving itself.

## What Should Wait Until After That

These should stay behind the next step:

- larger external user trial expansion
- Studio-first polishing
- IDE integration implementation
- app_min work
- additional benchmark widening

## Recommended Decision

Proceed next with:

- a frozen-profile one-command trial runner built on top of the existing CLI path

Do not reopen another patch cycle before that unless new evidence shows a real regression.

## One-Line Conclusion

The next best development move is no longer another patch; it is a one-command first-user runner that packages the now-stable frozen-profile CLI path into a real product entrypoint.
