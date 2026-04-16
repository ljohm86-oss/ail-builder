# V1 Execution Plan

## 1. Purpose

This document translates `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md` into an execution plan.

Its purpose is to answer:

- what we should build next
- in what order
- what we should explicitly defer
- how we know v1 is actually getting closer to completion

This is not a speculative roadmap.

It is a practical execution guide for closing AIL v1 as a complete product workflow.

## 2. Execution Goal

The execution goal for v1 is:

Make the CLI-driven frozen-profile workflow complete, documented, and stable enough for real user trials.

That means the following path must work cleanly:

```text
init
  -> generate
  -> diagnose
  -> repair
  -> compile --cloud
  -> sync
  -> preview/use generated result
```

Scope of that workflow:

- `landing`
- `ecom_min`
- `after_sales`

## 3. Current Starting Point

What already exists:

- active engine/server path
- CLI v1 skeleton with working commands
- cloud compile and sync protocol docs
- manifest and conflict model docs
- benchmark harness
- raw lane
- repair smoke
- evolution loop
- CLI smoke

What is still missing at the product level:

- one explicit primary user path
- a first-user quickstart flow
- a locked frozen-profile user experience path
- a clear definition of what "done for v1" means operationally

## 4. Execution Principles

- Prefer one complete user path over multiple half-finished entrypoints.
- Use the frozen profiles as the v1 product scope.
- Keep `app_min` experimental.
- Do not expand profiles before the main user workflow is fully closed.
- Do not spend time on local optimization work unless it removes friction from the primary path.

## 5. Phase Plan

## Phase 1: Close the Primary Product Path

Goal:

Make CLI the official v1 entrypoint for the frozen profiles.

Must complete:

- confirm the command surface is stable
- confirm JSON and text output are sufficient
- confirm conflict-safe sync behavior is stable
- document the one true golden path

Primary files likely involved:

- `/Users/carwynmac/ai-cl/cli/`
- `/Users/carwynmac/ai-cl/docs/`
- `/Users/carwynmac/ai-cl/testing/`

Exit condition:

- a user can go from requirement to synced generated project with documented steps

## Phase 2: Package the Frozen Profile Experience

Goal:

Make the three frozen profiles easy to experience on purpose.

Must complete:

- define recommended prompts per profile
- define expected outputs per profile
- define what "good result" looks like
- define first-user examples

Profiles:

- `landing`
- `ecom_min`
- `after_sales`

Exit condition:

- a new user can intentionally choose one of the three profiles and succeed on the first pass

## Phase 3: Reduce First-Run Friction

Goal:

Make the first 5 to 10 minutes of usage smooth.

Must complete:

- quickstart docs
- one-command or minimal-command setup guidance
- clear failure messages for common issues
- predictable examples

Exit condition:

- internal users do not need repo archaeology to get the first result

## Phase 4: Decide Secondary Entry Strategy

Goal:

Decide what happens to Studio and IDE-facing entrypoints after CLI is solid.

Must complete:

- explicit Studio decision
- explicit IDE sequencing decision
- avoid parallel product surfaces before CLI closure

Exit condition:

- secondary entrypoints are either promoted intentionally or deferred intentionally

## 6. What To Build Next

This is the recommended immediate build order.

### Priority A: Document and Freeze the Golden CLI Path

Deliverables:

- one canonical quickstart doc
- one canonical command sequence
- one canonical frozen-profile example set

Reason:

- users need one path that is clearly "the path"

### Priority B: Harden Frozen Profile Outcomes

Deliverables:

- landing example flow
- ecom example flow
- after_sales example flow

Reason:

- v1 must feel intentional, not accidental

### Priority C: Convert Internal Validation Into Release Readiness Signals

Deliverables:

- clear rule for what must stay green
- clear rule for what can stay experimental

Reason:

- current test infrastructure is strong, but it needs to serve product decisions directly

## 7. What Not To Build Right Now

Do not prioritize these before the primary path is complete:

- new token patches
- new profile expansion
- app_min promotion
- broad Studio feature work
- compile pipeline rewrite
- benchmark expansion for its own sake
- cleanup work unrelated to active delivery

## 8. Recommended This-Week Plan

This is the most practical near-term sequence.

### Step 1

Create the official user quickstart for the CLI path.

Desired result:

- a new user can follow one document and reach a synced output

### Step 2

Create frozen-profile first-run examples.

Desired result:

- one landing example
- one ecom example
- one after_sales example

### Step 3

Define v1 operational gates.

Desired result:

- benchmark baseline must pass
- CLI smoke must pass
- repair smoke must pass
- raw lane must remain at current stable level or better

### Step 4

Run an internal first-user trial.

Desired result:

- someone who did not build the current repo follows the quickstart
- friction points are recorded

## 9. Recommended Next Deliverables

These are the most useful concrete next artifacts.

### 1. Quickstart

Suggested file:

- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`

### 2. Frozen Profile Example Pack

Suggested file:

- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`

### 3. v1 Release Gate Note

Suggested file:

- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`

## 10. Acceptance Signals

v1 execution is moving in the right direction if:

- the CLI golden path becomes easier to follow
- frozen profile outcomes become easier to reproduce
- users need fewer hidden assumptions
- experimental areas stop blocking primary path decisions
- test infrastructure continues to support release decisions cleanly

## 11. Risk Areas

These are the main risks if execution drifts.

### Risk 1: Local optimization trap

Symptom:

- continuing to improve isolated subsystems without improving the user path

Mitigation:

- ask whether each task shortens or strengthens the golden path

### Risk 2: Profile breadth trap

Symptom:

- adding more profiles before frozen profiles are a polished user experience

Mitigation:

- treat `landing`, `ecom_min`, and `after_sales` as the v1 product

### Risk 3: Entry surface fragmentation

Symptom:

- trying to develop CLI, Studio, and IDE entrypoints at the same time

Mitigation:

- keep CLI as the primary v1 surface

## 12. Stop/Go Rule

Before starting any new major work item, ask:

1. Does this help complete the frozen-profile user path?
2. Does this reduce first-user friction?
3. Does this improve product closure more than a quickstart/example/gate task would?

If the answer is no, defer it.

## 13. One-Line Execution Decision

The next stage of AIL development should focus on turning the existing engineering core into a complete frozen-profile product path, with CLI as the primary v1 entrypoint.
