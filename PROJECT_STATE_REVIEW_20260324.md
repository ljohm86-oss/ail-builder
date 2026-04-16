# Project State Review 2026-03-24

## Purpose

This document is the current short reality check for the AIL project after the latest real-runtime website work completed on 2026-03-24.

It exists to answer:

- what the supported website frontier actually looks like now
- which recent improvements are already system-level product logic
- which website line is currently strongest in each sense
- where the current boundaries still are

Use this as the shortest up-to-date stage summary before reopening deeper evidence files.

## Short Answer

Recent work is still real product progress, not sample dressing.

The biggest update since the 2026-03-22 review is that the ecommerce line is no longer only a route-valid minimal storefront. It now has runtime-backed continuity across:

- discovery
- shop
- product
- cart
- checkout
- retained completion state

This does not change the core product truth:

- websites remain the supported mainline
- apps remain out of scope
- supported website quality is stronger now than it was a few days ago

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

## Current Runtime Truth By Line

### 1. Personal Independent Site

Current reviewed baseline:

- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteStoryReview`

Current judgment:

- strongest polished line

What is now true:

- anchor navigation is correct
- hero persona is clearer
- about language reads more like a real collaboration method
- visual treatment reads more like a portfolio surface
- project cards read more like compact case cards with:
  - project type
  - delivery scope
  - result

Why this matters:

- this is the strongest “show what the system can already do well” line

Current limit:

- still not yet a highly distinctive authored personal-brand system

### 2. Company / Product Website

Current reviewed baseline:

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteSecondaryCtaReview`

Current judgment:

- strongest mainstream homepage line

What is now true:

- the first screen reads more like a product homepage claim surface
- the page has a clearer brand layer
- trust cards and FAQ read more like real pre-sales communication
- the contact area reads more like demo / consultation intake, not only a generic form
- primary and secondary CTA roles are clearer

Why this matters:

- this line is now much more credible as a product-site system than as a generic landing template

Current limit:

- still not yet a highly distinctive brand homepage with highly memorable sentence-level brand language

### 3. Ecommerce Independent Storefront

Current reviewed baseline:

- `/Users/carwynmac/ai-cl/output_projects/EcomDiscoveryCartCheckoutReview`

Current judgment:

- strongest structural and interaction-proof line

What is now true:

- the storefront route loop remains real:
  - `/`
  - `/search`
  - `/category/:name`
  - `/shop/:id`
  - `/product/:id`
  - `/cart`
  - `/checkout`
- the storefront shell is cleaner and safer by default:
  - no broken homepage after-sales entry
  - no default empty-backend `/api/products` dependency
  - no default empty-backend `/api/order/submit` dependency
- discovery and purchase now read more like one system:
  - `search/category -> shop`
  - `shop -> product`
  - `product -> cart`
  - `cart -> checkout`
  - `checkout -> retained completion`
- runtime now confirms discovery memory can survive through the purchase path:
  - search/category context can still be visible in product detail
  - cart can still show discovery memory
  - checkout can still show discovery memory
  - retained completion can still expose a return path back to browsing

Why this matters:

- this line now proves the system can do more than marketing pages
- it is the clearest evidence that `ecom_min` is a real minimal storefront frontstage, not a fake shell

Current limit:

- still not a full ecommerce platform
- should not be positioned as merchant backend, payment platform, or operations software

### 4. After-Sales Service Website

Current reviewed baseline:

- `/Users/carwynmac/ai-cl/output_projects/AfterSalesCaseOpsReview`

Current judgment:

- strongest bounded operational surface line

What is now true:

- the page now reads more like a service-center surface
- it includes:
  - order context
  - routing actions
  - handling-flow framing
  - case-ops summary
  - latest update / next step style guidance

Why this matters:

- it shows the system can also support narrower operational website surfaces when the boundary is kept clear

Current limit:

- still not a full after-sales operations system
- not yet a ticket history, queue, or multi-state workflow product

## Current Product Truth

The current product truth is now easiest to say like this:

- Personal is the strongest polish proof.
- Company/Product is the strongest mainstream homepage proof.
- Ecommerce is the strongest interaction and continuity proof.
- After-sales is the strongest bounded operational-surface proof.

Across all four supported lines, the system is no longer only producing structurally valid pages. It is producing more believable website surfaces with clearer conversion, guidance, and flow continuity.

## What Has Actually Been System-Level

The main recent gains are system-level because they were implemented in:

- `/Users/carwynmac/ai-cl/ail_engine_v5.py`
- `/Users/carwynmac/ai-cl/testing/cli_smoke.sh`

Not just in sample output directories.

This is especially true for:

- company/product hero, FAQ, trust, and intake layers
- ecommerce discovery, shop, product, cart, checkout, and completion continuity
- after-sales handling-flow and case-ops surface improvements

Sample-local helpers still exist for some ecommerce filled-state screenshot checks, but those remain explicitly bounded as validation helpers, not product logic.

## Best Current Working Interpretation

As of 2026-03-24:

- the supported mainline is still website-first
- the strongest qualitative website is still personal
- the strongest product-homepage website is still company/product
- the strongest end-to-end interaction proof is now ecommerce
- the most bounded but improving supported line is still after-sales

## One-Line Conclusion

As of 2026-03-24, AIL’s supported website frontier is materially stronger than it was on 2026-03-22, with ecommerce now upgraded from “real minimal storefront” to “runtime-confirmed discovery-to-purchase storefront path,” while personal, company/product, and after-sales remain credible supported lines with clear but still honest boundaries.
