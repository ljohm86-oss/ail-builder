# Project State Review 2026-04-03

## Purpose

This document is the current short reality check for AIL after the managed / unmanaged customization track was promoted to a stable milestone on 2026-04-03.

It exists to answer:

- what the current supported website frontier actually looks like now
- what changed after the hook workflow became a stable milestone instead of an internal mechanism
- how close the current website-first phase now is to a clean completion boundary
- what the next highest-value direction looks like once both website quality and durable customization are materially stronger

## Short Answer

The project has moved one step beyond "strong website generation with better proofs."

The more accurate state now is:

- the supported website frontier is already strong
- the durable customization path is now also strong enough to stand beside it
- the current phase is no longer waiting for basic capability rescue
- the remaining decision is mostly about where to open the next phase

The biggest change since the 2026-04-02 review is not another website quality jump.
It is that the managed / unmanaged + hook workflow is now stable enough to be treated as a milestone in its own right.

That means the product truth is now stronger in two directions at once:

- better website baselines
- better post-generation customization behavior

## Current Supported Frontier

Formal supported profiles:

- `landing`
- `ecom_min`
- `after_sales`

Experimental only:

- `app_min`

Safest product truth:

- websites are supported
- apps are not yet supported as a formal delivery promise

## Current Stable Baselines By Line

### 1. Personal Independent Site

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteSignatureReview`

Current judgment:

- strongest authored-polish line

Why it matters:

- it is still the clearest proof of authored page quality
- it now carries a stronger signature layer through:
  - header editorial-note framing
  - `AUTHOR SIGNATURE`
  - `CURATED SHELF`
  - ordered case markers
  - footer signoff framing

Current limit:

- still not yet a highly distinctive authored personal-brand system

### 2. Company / Product Website

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandPostureReview`

Current judgment:

- strongest mainstream homepage line

Why it matters:

- it remains the best proof of a strong mainstream product homepage
- it now combines:
  - a strong proof / FAQ / intake / closure structure
  - a clearer point-of-view brand layer through:
    - header note strip
    - `BRAND POSTURE`
    - `FINAL BRAND LINE`

Current limit:

- still not yet a highly distinctive signature-brand homepage

### 3. Ecommerce Independent Storefront

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/EcomDiscoveryShopBoardReview`

Current judgment:

- strongest structural and runtime continuity line

Why it matters:

- it remains the clearest proof that AIL can support a believable multi-page frontstage
- the discovery front half is now stronger across:
  - home
  - search/category
  - shop
  - direct product entry
- the purchase back half still keeps the strongest runtime continuity across:
  - product
  - cart
  - checkout
  - completion / continue browsing

Current limit:

- still not a full ecommerce platform
- still should not be positioned as backend, merchant-ops, or payment software

### 4. After-Sales Service Website

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/AfterSalesFooterClosureReview`

Current judgment:

- strongest bounded tracked-case / operational-surface line

Why it matters:

- it proves AIL can support narrower operational website surfaces while staying inside website boundaries
- the tracked route now reads like one continuous handling path from:
  - intake / entry mode separation
  - case snapshot / board summary
  - status / flow / ops / history
  - actions / active panel
  - timeline / prep guidance / footer actions

Current limit:

- still not a full after-sales operations system
- still not a queue / ticket / multi-role workflow product

## Durable Customization Truth

The most important capability shift since the earlier website reviews is now unmistakable:

AIL is no longer only improving generated output quality.
It now also has a credible user-facing customization loop.

What is now true:

- `AIL/source` remains the structural source of truth
- managed / unmanaged frontend boundaries exist in generated projects
- theme and custom CSS have stable override entry points
- durable Vue/HTML hook insertion exists at:
  - page level
  - section level
  - selected child-slot level
- landing, ecommerce, and after-sales expose lightweight `context.runtime`
- generated projects emit project-local hook catalogs
- CLI now supports:
  - `project hooks`
  - `workspace hooks`
  - `project hook-init`
  - `workspace hook-init`
  - `--suggest`
  - `--open-catalog`
  - `--page-key`
  - `--section-key`
  - `--slot-key`
  - `--follow-recommended`
  - `--use-last-project`
- users can scaffold live durable hook files from starter examples instead of inventing them by hand

Why this matters:

- users now have a more realistic path for keeping part of their edits across rebuilds
- the project is no longer only solving "can we generate strong websites?"
- it is now also solving "can users keep extending them safely?"

## Current Product Truth

The clearest current product truth is now:

- Personal is the strongest authored-polish proof.
- Company/Product is the strongest mainstream homepage proof.
- Ecommerce is the strongest interaction and continuity proof.
- After-sales is the strongest bounded operational-surface proof.
- Managed/unmanaged + hooks are now the strongest proof that AIL can support durable post-generation customization without pretending to solve full round-trip editing.

Across all supported lines, AIL is now past purely structural generation.
It is producing more believable website surfaces and it now has a practical customization workflow beside them.

## Completion Estimate

If the goal is still defined as "finish the current website-first phase cleanly," the project now looks slightly further along than it did on 2026-04-02.

Current completion estimate for the website-first phase:

- about `92%` to `95%` complete

What is already done:

- four supported website lines have clear strong baselines
- all four lines have real runtime evidence, not only structural review
- ecommerce has strong front-half and back-half continuity proof
- company and personal now both have stronger brand/author signature baselines
- after-sales has a stronger tracked-case handling path
- safe split phase-1 is landed
- managed/unmanaged phase-1 is landed
- hooks / child-slots / runtime-context phase-2 is landed in a practical usable form
- hook catalogs, workspace/project inspection, starter examples, and hook scaffolding are now all landed as a stable milestone

What still remains before this phase feels fully closed:

- one clean packaging pass that updates the highest-level operator-facing docs to the 2026-04-03 truth everywhere
- one deliberate decision about whether the next phase is:
  - stronger brand distinctiveness
  - deeper durable customization
  - or broader platform capability
- optional extra demo/showcase cleanup, only if we want a cleaner outward-facing bundle

Practical schedule estimate:

- if we only want to finish the current website-first phase cleanly: about `1` to `2` focused working days
- if we want one more visible quality pass or one more productization pass before calling the phase done: about `1` more week

## Best Current Working Interpretation

As of 2026-04-03:

- the supported mainline is still website-first
- the strongest authored/polish website is personal with a clearer signature baseline
- the strongest mainstream homepage website is company with a clearer brand-posture baseline
- the strongest end-to-end interaction proof is still ecommerce
- after-sales remains the strongest bounded tracked-case website surface
- the codebase is healthier than before
- the product is healthier than before because durable override boundaries, discovery, and scaffolding are now real user-facing capabilities
- the one later validation interruption after this review was environmental rather than product-level, and fresh compile plus fresh full CLI smoke were reconfirmed green on 2026-04-04 after restarting Codex

## One-Line Conclusion

As of 2026-04-03, AIL's website-first phase looks extremely close to a clean completion boundary: the four supported website lines now have strong baselines with broad runtime proof, and the managed / unmanaged + hook workflow has matured into a real customization milestone rather than an internal implementation detail.
