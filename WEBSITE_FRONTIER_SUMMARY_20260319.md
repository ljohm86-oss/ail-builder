# Website Frontier Summary 2026-03-19

## Purpose

This document is the single-page summary for the current website-oriented AIL product frontier.

It exists to answer:

- what the current website product surface is
- what is supported, partial, and out of scope
- what evidence we have that the supported surface is real
- what the best demo and delivery path is
- what the next website-oriented frontier should be

Use this as the top-level website summary before diving into the deeper supporting documents.

## Current Headline

As of 2026-03-19, AIL has a stable CLI-first website product surface for:

- company and product websites
- personal independent sites
- minimal ecommerce independent storefronts
- after-sales service websites

It also supports blog-style personal sites in a narrower, partial sense.

It should not yet be positioned as:

- a full application generator
- a dashboard generator
- a CMS platform
- a full ecommerce platform

## Current Supported Surface

### Supported

- Personal Independent Site
- Company Introduction Site
- Product Marketing Website
- Enterprise or Brand Website
- Ecommerce Independent Storefront
- After-Sales Service Website

### Partial

- Personal Blog-Style Site

### Not Supported

- Full Blog or CMS Platform
- Full Ecommerce Platform
- Full Application or Dashboard Product

Primary frozen profiles behind this surface:

- `landing`
- `ecom_min`
- `after_sales`

Experimental only:

- `app_min`

## Strongest Product Truth

The strongest current product truth is:

- CLI-first
- website-oriented
- frozen-profile based
- backed by compile, sync, preview, export-handoff, and workbench flows

This is no longer just a collection of low-level commands. It is now a working website-oriented control surface with:

- trial entry
- project workbench
- workspace workbench
- RC and readiness views
- preview, target resolution, inspection, and export handoff

## Delivery Evidence

The key evidence file is:

- `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.md`

Current validated result:

- `status = ok`
- `cases_total = 5`
- `delivery_ready_count = 5`
- `supported_ready_count = 4`
- `partial_ready_count = 1`

Validated packs:

- Personal Independent Site Pack
- Company / Product Website Pack
- Ecommerce Independent Storefront Pack
- After-Sales Service Website Pack
- Personal Blog-Style Site Pack (`Partial`)

Common stable signals across the validated cases:

- expected profile detected
- `trial-run` succeeded
- `project go` succeeded
- `project preview` resolved `artifact_root`
- `project export-handoff` resolved `artifact_root`

## Demo Evidence

The key demo execution files are:

- `/Users/carwynmac/ai-cl/WEBSITE_DEMO_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/testing/run_website_demo_pack.sh`
- `/Users/carwynmac/ai-cl/testing/results/website_demo_pack_run_20260319.md`

Current demo run result:

- `status = ok`
- `case_count = 4`
- `demo_ready_count = 4`
- `supported_demo_ready_count = 4`

Default demo order:

1. Company / Product Website
2. Personal Independent Site
3. Ecommerce Independent Storefront
4. After-Sales Service Website

Optional only:

5. Blog-Style Personal Site (`Partial`)

## Sales Positioning Truth

The cleanest short positioning right now is:

AIL currently supports CLI-first generation and delivery for company and product websites, personal independent sites, minimal ecommerce storefronts, and after-sales service websites.

The main supporting doc is:

- `/Users/carwynmac/ai-cl/WEBSITE_SALES_POSITIONING_20260319.md`

The two most important sales constraints are:

- do not position the current product as a full app or dashboard system
- do not position the current ecommerce or blog support as full platform support

## Best Current Workflow

For website delivery or demo validation, the most reliable current sequence is:

```text
trial-run -> project go -> project preview -> project export-handoff
```

This matters because it matches the current workbench truth and avoids weaker validation timing.

## What Is Actually Finished

The website frontier is now complete enough to support:

- product packaging
- delivery qualification
- demo execution
- safe outward positioning
- requirement templating
- repeatable validation evidence

This means the website line is no longer missing core definition material.

## What Is Still Deliberately Out Of Scope

Keep these outside the current website frontier:

- app-oriented product promises
- dashboard or internal tool promises
- CMS promises
- full ecommerce platform promises
- premature `app_min` promotion

## Best Next Frontier

The next website-oriented frontier should stay focused on:

- making the website surface easier to consume and hand off
- improving website-oriented product entry and preview experience
- turning current website packs into even clearer delivery assets

It should not drift into:

- broad application promises
- platform promises
- secondary-surface over-expansion

## Supporting Document Set

Use these documents together:

- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_PRODUCT_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_DEMO_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_DELIVERY_CHECKLIST_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_REQUIREMENT_TEMPLATES_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_SALES_POSITIONING_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/website_demo_pack_run_20260319.md`

## One-Line Summary

The current website frontier is real, validated, and productizable: AIL now has a stable CLI-first website surface for company/product sites, personal independent sites, minimal storefronts, and after-sales websites, while app, CMS, and full-platform promises remain intentionally out of scope.
