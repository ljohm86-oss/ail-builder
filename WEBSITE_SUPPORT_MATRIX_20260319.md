# Website Support Matrix 2026-03-19

## Purpose

This document defines the current website-oriented support matrix for the AIL CLI-first frozen product surface.

It exists to answer one practical question:

What kinds of website outputs can the current system support today as a formal product promise, and what kinds remain partial or out of scope?

Use this together with:

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`

## Status Levels

### Supported

The current system can intentionally generate this type inside the frozen product boundary, and it is reasonable to treat it as part of the supported website surface.

### Partial

The current system can produce a version of this type, but only inside a narrower boundary than the full category usually implies.

### Not Supported

The current system should not formally promise this category yet.

## Current Product Boundary

Formal frozen profiles:

- `landing`
- `ecom_min`
- `after_sales`

Experimental only:

- `app_min`

This matrix is deliberately centered on the frozen profiles, because that is the current product promise.

## Support Matrix

| Website Type | Current Status | Best-Fit Profile | Notes |
| --- | --- | --- | --- |
| Personal independent site | Supported | `landing` | Strong fit for personal homepage, portfolio-like site, service page, creator/freelancer site |
| Company introduction site | Supported | `landing` | Strong fit for company overview, team, FAQ, contact, stats, logo wall |
| Product marketing site | Supported | `landing` | Strong fit for SaaS/product website, feature presentation, CTA, FAQ, pricing-style sections |
| Personal blog-style site | Partial | `landing` | Good for content-forward site or article-list style presentation, but not a full blog product |
| Enterprise / brand website | Supported | `landing` | Supported when the result is still a marketing / introduction / product-facing website rather than a custom business system |
| Ecommerce independent storefront | Supported | `ecom_min` | Strong fit for minimal store funnel: list, detail, cart, checkout, category/shop navigation |
| Full ecommerce platform | Not Supported | none | Merchant admin, order ops, inventory, advanced payments, and platform behavior remain outside current promise |
| After-sales service site | Supported | `after_sales` | Strong fit for refund, exchange, complaint, support intake |
| Content CMS website | Not Supported | none | The system can generate content surfaces, but not a full CMS/back-office product |
| Full application / dashboard | Not Supported | `app_min` experimental only | Do not promise this as current website surface or v1 product surface |

## Recommended Positioning By Category

### 1. Personal Independent Site

Status:

- Supported

Recommended fit:

- personal homepage
- freelancer profile
- creator page
- service site
- portfolio-like presentation site

Recommended profile:

- `landing`

What to avoid promising:

- advanced content management
- account systems
- complex backend workflows

### 2. Company Introduction / Product Website

Status:

- Supported

Recommended fit:

- company intro site
- startup website
- SaaS marketing site
- product overview site
- feature, FAQ, contact, team, logo wall, stats sections

Recommended profile:

- `landing`

This is one of the strongest current surfaces.

### 3. Personal Blog-Style Website

Status:

- Partial

What is supported:

- article-list style landing or content site
- author/about page
- blog-like presentation structure

What is not yet part of the formal promise:

- post management backend
- CMS
- comments
- search
- editorial workflow

Recommended current wording:

- supported as a content-forward personal site
- not yet supported as a full blog platform

### 4. Ecommerce Independent Site

Status:

- Supported inside the `ecom_min` boundary

What is supported:

- storefront homepage
- product listing
- product detail
- cart
- checkout
- category navigation
- shop-style page variants

What is not yet part of the formal promise:

- merchant admin
- order operations center
- inventory system
- complex payment orchestration
- advanced membership systems

Recommended current wording:

- supported as a minimal ecommerce independent storefront
- not yet supported as a full ecommerce platform

### 5. After-Sales Service Website

Status:

- Supported

What is supported:

- refund application surface
- exchange application surface
- complaint submission surface
- contact/support intake flow

Recommended profile:

- `after_sales`

### 6. Full Application-Like Website or Dashboard

Status:

- Not Supported as a formal product promise

Why:

- current app surface is still experimental
- `app_min` remains outside the frozen release baseline

Recommended current wording:

- not yet part of the supported product surface

## Safe External Positioning

If we need a short external-facing description today, the safest accurate phrasing is:

The current system supports website-oriented generation for:

- personal independent sites
- company introduction and product websites
- minimal ecommerce independent storefronts
- after-sales service websites

It does not yet formally support:

- full application generation
- full ecommerce platform generation
- full CMS/blog platform generation

## Internal Development Implication

This matrix implies the current next frontier should stay focused on:

- productizing the website-oriented frozen surface
- clarifying preview and artifact consumption
- improving the supported website use cases

And should not let the mainline drift into:

- premature `app_min` promotion
- broad application promises
- full-platform ecommerce promises
- CMS promises

## One-Line Summary

As of 2026-03-19, the current supported product surface is a website-oriented CLI-first AIL system for personal/company/product sites, minimal ecommerce storefronts, and after-sales service sites; blog-platform, ecommerce-platform, and application-class promises should remain out of scope.
