# Website Next Tasks 2026-03-19

## Purpose

This document turns the current website-oriented frontier into a small set of concrete next implementation tasks.

It exists to answer:

- what we should build next for the website surface
- what should stay out of scope for now
- what counts as a good stopping point for each task

Use this together with:

- `/Users/carwynmac/ai-cl/WEBSITE_FRONTIER_SUMMARY_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_DELIVERY_CHECKLIST_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_DEMO_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/APP_MIN_STRATEGY_REVIEW_20260319.md`

## Current Starting Point

What is already true:

- website support boundary is documented
- website delivery boundary is documented
- website demo path is documented
- website sales positioning is documented
- website demo execution has a working script
- website delivery validation has real green evidence

That means the next work should not be more definition churn.

The next work should be execution work that makes the website surface easier to use, easier to hand off, and easier to trust.

## Current Completion Snapshot

As of 2026-03-19, the first four website-oriented priorities are now substantially complete.

- Priority 1 completed through website-oriented preview handoff improvements in:
  - `project preview`
  - `project export-handoff`
  - `workspace preview`
  - `workspace export-handoff`
- Priority 2 completed through:
  - `python3 -m cli website check`
- Priority 3 completed through website-oriented export payloads:
  - `website_delivery_summary`
  - `website_surface_summary`
- Priority 4 completed through reusable delivery assets:
  - `/Users/carwynmac/ai-cl/testing/build_website_delivery_assets.sh`
  - `/Users/carwynmac/ai-cl/testing/results/website_delivery_assets_20260319.md`

The current website line is no longer waiting on boundary definition. It now has:

- supported/partial matrix
- demo pack
- delivery checklist
- requirement templates
- website-oriented delivery entry
- website-oriented preview/export payloads
- reusable delivery assets
- real validation evidence

## Priority 1. Strengthen Website Preview Consumption

### Current Status

- Completed

### Why This Is First

The current website surface can already generate, sync, preview, and export handoff.

The next leverage point is not more profile expansion. It is making the generated website output easier to consume immediately after a successful run.

### Task

Improve the website-oriented preview and handoff experience around:

- `project preview`
- `project export-handoff`
- `workspace preview`
- `workspace export-handoff`

Focus on:

- clearer preview target ordering
- more useful website-oriented handoff labels
- cleaner top-level artifact inspection for website outputs

### Good Stopping Point

- a successful website project consistently points users to the best first inspection target
- handoff output feels website-oriented instead of generic artifact-oriented
- no regression in CLI smoke, RC, or readiness

## Priority 2. Build A Website-Oriented Delivery Entry

### Current Status

- Completed

### Why This Matters

The system already has:

- `trial-run`
- `project go`
- `workspace go`

But the website product line still lacks a dedicated delivery-facing CLI entry that says:

- run the supported website flow
- check it against the website delivery boundary
- summarize the result as a website delivery decision

### Task

Add a thin website-oriented delivery entry, likely one of:

- `python3 -m cli website check`
- `python3 -m cli website deliver-check`

It should:

- consume current website-oriented flows
- not create a second product truth
- report supported vs partial vs out-of-scope using the already-defined website surface

### Good Stopping Point

- a single CLI command can evaluate a website requirement against current website delivery rules
- output uses the existing website pack language
- no new boundary ambiguity is introduced

## Priority 3. Improve Website-Oriented Export Payloads

### Current Status

- Completed

### Why This Matters

The export layer is already functional, but it still feels generic.

If we want the website line to be easier to hand to:

- operators
- IDEs
- agents
- future guided surfaces

then website-oriented exports should be slightly more opinionated.

### Task

Enhance the website-oriented export bundle around:

- primary inspection target
- generated route summary
- generated view summary
- pack/profile-oriented notes

Without inventing new semantics outside the existing CLI truth.

### Good Stopping Point

- export handoff gives a better website-oriented "what was generated" summary
- project-level export is easier to consume than raw artifact inspection
- downstream consumers need less custom interpretation

## Priority 4. Turn Demo Packs Into Reusable Delivery Assets

### Current Status

- Completed

### Why This Matters

We now have:

- demo docs
- demo run script
- delivery validation evidence

The next step is making those assets easier to reuse in real delivery and presentation contexts.

### Task

Extend the website demo asset layer so that each website pack has a more reusable bundle of:

- requirement
- expected profile
- expected primary route
- expected primary preview target
- safe talking points

### Good Stopping Point

- each supported website pack can be demonstrated and explained with minimal improvisation
- the demo layer stays aligned with actual validated behavior

## Priority 5. Keep `app_min` Explicitly Out Of The Mainline

### Current Status

- Active guardrail, not a build task

### Why This Matters

The biggest way to waste momentum now would be to let website work drift back into application-boundary churn.

### Task

Do not treat these as near-term website next tasks:

- `app_min` promotion
- dashboard support
- CMS support
- full ecommerce platform support
- auth-heavy or admin-heavy surface work

### Good Stopping Point

- website roadmap stays website-oriented
- no task reopens application promises by accident

## Suggested Order Of Execution

Completed order:

1. strengthen website preview consumption
2. add a website-oriented delivery entry
3. improve website-oriented export payloads
4. turn demo packs into reusable delivery assets

Ongoing guardrail:

5. keep `app_min` explicitly outside the active website track

Next execution focus should move beyond these four completed items and into higher-value website product work, while preserving the same website-only boundary.

## New Immediate Focus

The next website work should now focus on one of:

1. stronger website delivery consumption on top of the new reusable assets
2. website-oriented operator or IDE consumption of those delivery assets
3. website-specific product polish that improves real delivery outcomes without reopening app-style scope

This means the website track should now prefer:

- consuming the new delivery assets
- improving delivery ergonomics
- keeping the mainline website-oriented

And should still avoid:

- `app_min` promotion
- dashboard or CMS reopening
- broad new planning churn

## What Not To Do Next

Avoid these as immediate next tasks:

- rewriting the v1 plan
- reopening frozen-profile token churn
- expanding app support promises
- building a second truth layer in IDE or Studio
- adding more strategic docs before the current tasks are executed

## One-Line Summary

The next website frontier should focus on improving preview consumption, delivery entry, and export quality for the already-supported website surface, while keeping `app_min`, CMS, dashboard, and platform promises outside the near-term track.
