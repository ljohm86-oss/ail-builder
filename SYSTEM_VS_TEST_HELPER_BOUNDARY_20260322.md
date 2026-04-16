# System vs Test Helper Boundary

## Purpose

This note records one operational boundary that matters during website-quality work:

- what changes are now part of the AIL product system itself
- what changes were only introduced as sample-local testing helpers

The goal is to avoid mixing up:

- reusable product capability improvements
- one-off runtime validation scaffolding

## Short Answer

Yes: the recent website-quality improvements have primarily been implemented through the AIL system's own generation logic.

In practice that means:

- the real product improvements were made in the generator and related core files
- a small amount of sample-local code was added only to support runtime screenshot validation

## System-Level Changes

These changes are part of the real product surface because they were implemented in the system source of truth:

- `/Users/carwynmac/ai-cl/ail_engine_v5.py`
- `/Users/carwynmac/ai-cl/cli/ail_cli.py`
- `/Users/carwynmac/ai-cl/ail_server_v5.py`

When a change lands here, the effect is intended to carry forward into future generated projects.

Recent examples that are now system-level behavior:

- personal-site single-page anchor navigation instead of broken route links
- personal-site default brand fallback, about section, persona row, and stronger case-card structure
- company/product-site hero, product-intro structure, FAQ defaults, trust/testimonial treatment, and stronger brand-entry handling
- ecommerce storefront shell cleanup for `ecom_min`
- ecommerce storefront removal of broken after-sales entry from storefront pages
- ecommerce storefront safer default frontend behavior when no backend API is present
- ecommerce cart layout, hierarchy, summary panel, and checkout readability fixes

## Test-Only Helpers

Some changes were intentionally applied only to generated sample projects during runtime validation.

These were not product-feature changes. They existed only to make screenshots and flow checks realistic.

The main example is the filled-state screenshot helper:

- adding a `?demo_seed=filled` URL behavior inside one generated sample's `Cart.vue` or `Checkout.vue`
- seeding `localStorage` with demo cart items if the cart is empty

This helper was used so we could capture:

- non-empty cart screenshots
- non-empty checkout screenshots

without changing the core product logic or introducing permanent fake data behavior.

Typical sample-local helper targets looked like:

- `/Users/carwynmac/ai-cl/output_projects/.../frontend/src/views/Cart.vue`
- `/Users/carwynmac/ai-cl/output_projects/.../frontend/src/views/Checkout.vue`

Those edits were disposable validation scaffolding.

## How To Tell The Difference

Use this rule:

- if the change is in `/Users/carwynmac/ai-cl/ail_engine_v5.py`, treat it as a real system capability change
- if the change only exists inside `/Users/carwynmac/ai-cl/output_projects/...`, treat it as sample-local unless explicitly promoted back into the generator

Another simple check:

- if regenerating a fresh project preserves the behavior, it is system-level
- if the behavior only exists in one already-generated sample, it is test-only

## Why This Distinction Matters

Without this boundary, it becomes easy to overstate progress.

For example:

- a better screenshot captured from a sample-local seeded cart does not automatically mean the system now generates demo data
- a layout improvement in the generator does mean future projects will inherit that improvement

This distinction keeps product truth honest while still allowing practical runtime validation.

## Current Working Rule

For current website-quality work, the correct default assumption is:

- layout, copy, structure, and behavior improvements are product work when they land in the generator
- runtime seeding and temporary view edits inside generated samples are validation tools only

## Current Recommendation

When reviewing future progress:

1. cite the system file when claiming capability has improved
2. cite the sample file only when explaining how a test was performed
3. explicitly label any seeded or mocked runtime path as test-only

This keeps our quality narrative accurate and repeatable.
