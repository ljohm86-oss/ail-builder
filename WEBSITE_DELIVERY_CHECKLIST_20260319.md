# Website Delivery Checklist 2026-03-19

## Purpose

This checklist turns the current website-oriented product surface into a practical delivery gate.

Use it to answer:

- should we accept this website request inside the current product boundary
- which pack should we map it to
- what should we verify before calling the result deliverable
- what should we explicitly avoid promising

Use this together with:

- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_PRODUCT_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_REQUIREMENT_TEMPLATES_20260319.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`

## Current Delivery Truth

Current supported website delivery surface:

- personal independent site
- company introduction site
- product marketing website
- enterprise or brand website
- ecommerce independent storefront
- after-sales service website

Partial only:

- personal blog-style site

Do not position as supported delivery today:

- full blog or CMS platform
- full ecommerce platform
- application or dashboard product

## Step 1. Classify The Request

Before accepting a request, map it to exactly one primary pack:

1. Personal Independent Site Pack
2. Company / Product Website Pack
3. Ecommerce Independent Storefront Pack
4. After-Sales Service Website Pack
5. Personal Blog-Style Site Pack (`Partial`)

If the request needs two packs at once, simplify it before treating it as current product scope.

## Step 2. Decide Support Level

Mark the request as one of:

- `Supported`
- `Partial`
- `Out of Scope`

Use these rules:

- `Supported`:
  - the request fits `landing`, `ecom_min`, or `after_sales`
  - the result is still website-oriented
  - no app, platform, or CMS promise is implied
- `Partial`:
  - the request is still website-oriented, but the category normally implies features we do not support
  - current best example is blog-style site
- `Out of Scope`:
  - the request depends on app workflows, dashboards, back-office systems, CMS behavior, or platform behavior

## Step 3. Boundary Check

Reject or narrow the request if it includes any of the following:

- login or user center
- admin panel or dashboard
- merchant backend
- order operations center
- inventory system
- CRM or support console
- CMS or publishing backend
- comments system
- advanced search system
- workflow approval system
- internal enterprise portal

These are signs that the request is drifting out of the current website product surface.

## Step 4. Requirement Quality Check

Prefer a requirement that:

- clearly names a website outcome
- stays inside one dominant pack
- lists a small number of concrete supported sections
- avoids mixing frontend website asks with backend app asks

Prefer these inputs:

- canonical templates from `/Users/carwynmac/ai-cl/WEBSITE_REQUIREMENT_TEMPLATES_20260319.md`
- one or two richer supported additions at most

Avoid:

- vague "build me a platform" wording
- multi-system requests
- asking for both public website and private console in one requirement

## Step 5. Generation Path Check

Before calling a website deliverable, the canonical CLI path should stay healthy:

```text
trial-run
  or
init -> generate -> diagnose -> repair if needed -> compile --cloud -> sync
```

Expected current behavior for supported website asks:

- `generate -> diagnose` should usually pass on first pass
- `repair` may exist, but should not be the assumed first step
- `compile --cloud` should succeed
- `sync` should succeed without unmanaged drift overwrite

## Step 6. Delivery Validation Check

For a supported website delivery, confirm:

- the detected profile matches the intended pack
- the generated structure stays website-oriented
- preview handoff points to reasonable output targets
- latest build exists
- latest artifact descriptor exists
- project or workspace workbench remains healthy

Recommended minimum commands:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "<requirement>" --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project go --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project preview --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project export-handoff --base-url embedded://local --json
```

Recommended order for stable delivery validation:

```text
trial-run -> project go -> project preview -> project export-handoff
```

For repo-level review, also use:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace summary --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli rc-check --base-url embedded://local --json
```

## Step 7. Safe Delivery Language

Use delivery wording that matches the actual surface:

- "personal independent site"
- "company introduction website"
- "product marketing website"
- "minimal ecommerce independent storefront"
- "after-sales service website"
- "blog-style personal site" for partial cases

Avoid delivery wording like:

- platform
- dashboard
- application
- CMS
- admin system
- full ecommerce system

## Step 8. Final Delivery Decision

Treat the request as ready for current delivery only if all are true:

- the request maps to one supported or partial pack
- the requirement stays inside current website boundaries
- the generated profile is correct
- the canonical path is healthy
- preview and handoff outputs are coherent
- delivery wording does not over-promise the product surface

If any of these fail:

- narrow the scope
- reword the requirement
- downgrade to `Partial`
- or mark it `Out of Scope`

## Quick Decision Table

| Situation | Decision |
| --- | --- |
| Personal site, company site, product site, or after-sales site with clear website sections | Accept as `Supported` |
| Minimal storefront with list, detail, cart, checkout | Accept as `Supported` |
| Blog-like personal content site without CMS asks | Accept as `Partial` |
| Website ask mixed with login, dashboard, admin, CMS, or platform behavior | Narrow or reject as `Out of Scope` |
| Requirement spans both marketing site and internal tool | Split the request before accepting |

## One-Line Summary

The current website delivery standard is: accept only website-oriented requests that stay inside `landing`, `ecom_min`, or `after_sales`, validate them through the canonical CLI path, and avoid promising app, CMS, or platform behavior.
