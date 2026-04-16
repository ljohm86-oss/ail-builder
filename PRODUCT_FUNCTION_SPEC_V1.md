# Product Function Spec v1

## 1. Purpose

This document defines the AIL platform product scope for v1.

Its purpose is to stop uncontrolled local optimization and shift the project toward a complete, usable product surface.

This spec is not about:

- adding more token patches
- extending profiles indefinitely
- polishing isolated subsystems without closing the full user loop

This spec is about one question:

What must be fully implemented so that AIL v1 is a complete product, not a partial engineering system?

## 2. Product Goal

AIL v1 should allow a user to:

1. describe an application requirement
2. generate or edit AIL as the source of truth
3. diagnose and repair AIL into the current supported system boundary
4. compile it through the cloud compile path
5. sync generated artifacts into a local project safely
6. preview and iterate on the result

The primary product goal is:

Deliver one complete AIL-driven application generation workflow for the currently frozen profiles.

## 3. Product Principles

- AIL is the single source of truth.
- Generated files are rebuildable artifacts.
- User custom code must remain outside managed zones.
- v1 should optimize for complete workflow closure, not maximum feature breadth.
- Frozen profile reliability is more important than experimental profile coverage.

## 4. Target Users

### Primary User

Developer or technical operator who wants to turn structured product requirements into a runnable generated project with cloud compile and local sync.

Typical traits:

- comfortable with CLI or technical tooling
- wants a reliable generation workflow more than visual editing
- can understand profile boundaries and generated/custom separation

### Secondary User

Internal product or platform teammate validating AIL prompts, profile boundaries, repair flows, and compile output quality.

### Not Primary for v1

- non-technical end users
- multi-user collaboration teams
- large enterprise workflow authors
- users expecting arbitrary full-stack app generation beyond current profile boundaries

## 5. Product Boundary for v1

### In Scope

AIL v1 must support a complete workflow for:

- `landing`
- `ecom_min`
- `after_sales`

Experimental support may remain visible for:

- `app_min`

But `app_min` is not part of the formal release baseline and must not block the v1 product definition.

### Out of Scope

The following are not required for v1 product completeness:

- reverse code-to-AIL sync
- patch compile as a required product path
- collaborative editing
- AST merge
- broad profile expansion
- arbitrary backend system generation
- `app_min` as a frozen release profile

## 6. Required v1 Functional Areas

AIL v1 is complete only if all of the following functional areas exist as working product features.

### A. Project Initialization

User must be able to:

- initialize an AIL project
- create the `.ail/` working directory
- create `.ail/source.ail`
- create baseline manifest/build tracking files

Current implementation basis:

- `/Users/carwynmac/ai-cl/cli/ail_cli.py`
- `ail init`

### B. Requirement to AIL

User must be able to:

- provide a requirement
- generate an AIL candidate
- store it in `.ail/source.ail`
- preserve AIL as the single source of truth

Current implementation basis:

- `ail generate`

### C. AIL Diagnosis and Repair

User must be able to:

- diagnose whether the current AIL fits supported system boundaries
- identify invalid or weak outputs
- repair the AIL into a compile candidate when possible

Current implementation basis:

- `ail diagnose`
- `ail repair`
- Generator / Diagnostic / Repair skills

### D. Cloud Compile

User must be able to:

- compile current `.ail/source.ail`
- receive a cloud build result
- persist build metadata locally
- separate compile from sync

Current implementation basis:

- `ail compile --cloud`
- `.ail/last_build.json`

### E. Managed Sync

User must be able to:

- sync cloud-generated artifacts into the local project
- apply changes only to managed zones
- update manifest state
- avoid writing into custom zones

Current implementation basis:

- `ail sync`
- manifest handling
- sync engine

### F. Conflict Detection and Safe Handling

User must be able to:

- detect local drift in managed files
- refuse silent overwrite by default
- inspect conflict state
- back up local managed files before overwrite when explicitly requested

Current implementation basis:

- `ail conflicts`
- `ail sync --backup-and-overwrite`

### G. Validation and Regression Surface

The product must remain guarded by:

- CLI smoke
- repair smoke
- raw lane
- evolution loop
- benchmark release baseline

Current implementation basis:

- `/Users/carwynmac/ai-cl/testing/`
- `/Users/carwynmac/ai-cl/benchmark/`

## 7. Required v1 User Flows

These are the canonical user flows AIL v1 must support.

### Flow 1: New Project Flow

```text
User requirement
    ↓
ail init
    ↓
ail generate
    ↓
ail diagnose
    ↓
ail repair (if needed)
    ↓
ail compile --cloud
    ↓
ail sync
    ↓
local runnable/generated project
```

### Flow 2: Existing Project Iteration

```text
Edit requirement or source.ail
    ↓
ail diagnose
    ↓
ail repair (if needed)
    ↓
ail compile --cloud
    ↓
ail sync
    ↓
updated project
```

### Flow 3: Conflict-Safe Sync

```text
compile result cached
    ↓
local managed file drift exists
    ↓
ail conflicts
    ↓
ail sync --abort-on-conflict
or
ail sync --backup-and-overwrite
```

## 8. What Makes v1 “Complete”

AIL v1 should be considered complete when all of the following are true:

1. a new user can initialize an AIL project and reach a generated project using a documented golden path
2. the frozen profiles can complete the full generate -> diagnose -> repair -> compile -> sync workflow
3. cloud compile and local sync are manifest-aware and conflict-safe
4. the CLI provides a stable primary entrypoint
5. current regression lines remain healthy:
   - benchmark release baseline pass
   - raw lane final compile rate remains stable
   - repair smoke remains stable
   - CLI smoke remains stable

## 9. What Does Not Make v1 Complete

The following can improve the system, but they do not define v1 completeness by themselves:

- more token patches
- more alias normalization
- more sample sets
- more benchmarks
- more docs
- more profile breadth
- more experimental app coverage

These may help quality, but they do not replace a complete user workflow.

## 10. Current State Assessment

Based on the current repository state:

- the engineering core is already close to a v1-capable platform
- the main missing step is product-level closure and prioritization
- the project should stop treating every local improvement as equally important

Current state can be summarized as:

The platform core exists. The next step is to finish and expose the primary product workflow.

## 11. Recommended Development Priority

### Priority 1

Make the CLI path the official v1 primary entrypoint.

Why:

- it is already the most coherent product surface
- it already covers init/generate/diagnose/repair/compile/sync/conflicts
- it is easier to harden than the Studio path

### Priority 2

Close the frozen-profile golden path for:

- `landing`
- `ecom_min`
- `after_sales`

Why:

- these are already the formal release baseline
- they match the benchmark gate

### Priority 3

Create a first-user quickstart experience around the CLI.

Why:

- this turns the platform from “engineering-capable” into “user-usable”

### Priority 4

Decide the Studio role explicitly:

- retain as side workflow
- promote as secondary product entrypoint
- or defer

Why:

- it should not remain ambiguous

## 12. Recommended v1 Build Plan

### Phase 1: Product Closure

Focus on:

- CLI golden path
- frozen profile support path
- conflict-safe sync
- quickstart docs

### Phase 2: User Experience Packaging

Focus on:

- examples
- one-command demos
- error clarity
- first-run guidance

### Phase 3: Secondary Entry Decisions

Focus on:

- Studio decision
- IDE path sequencing
- future patch compile path

## 13. Explicit Non-Goals for Current Phase

Do not prioritize these before the v1 core is complete:

- new profile expansion
- experimental app feature growth
- large-scale compiler rewrites
- profile-generalized product promises
- deep Studio expansion before CLI is the stable primary entrypoint

## 14. Acceptance Criteria

AIL v1 product scope is ready when:

- CLI v1 is the documented primary path
- frozen profile users can complete the full workflow end-to-end
- conflict-safe sync is part of the standard flow
- quickstart usage is documented
- benchmark release baseline remains pass
- integrity checks remain healthy

## 15. One-Line Product Decision

AIL v1 should be developed as a complete frozen-profile generation workflow, not as an open-ended collection of partially optimized subsystems.
