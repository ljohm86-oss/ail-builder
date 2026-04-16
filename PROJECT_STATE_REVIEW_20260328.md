# Project State Review 2026-03-28

## Purpose

This document is the current short reality check for the AIL project after the latest website-runtime and safe-split work completed on 2026-03-28.

It exists to answer:

- what the supported website frontier actually looks like now
- which line is currently strongest in polish, mainstream homepage quality, structural/runtime proof, and bounded operational-surface support
- what the newest stable baseline is for each supported website line
- where the current honest boundaries still are

Use this as the shortest current stage summary before reopening longer evidence files.

## Short Answer

Recent work is still real product progress, not sample dressing.

The biggest change since the 2026-03-24 state review is not that a new profile was added, but that:

- the after-sales line has been pushed much further into a real tracked-case handling surface
- the engine has also completed a first-stage safe split, with ecom / after-sales generation extracted out of the main engine file

This does not change the core product truth:

- websites remain the supported mainline
- apps remain out of scope
- supported website quality is stronger now than it was on 2026-03-24

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

- this is still the strongest "show what the system can already do well" line

Current limit:

- still not yet a highly distinctive authored personal-brand system

### 2. Company / Product Website

Current reviewed baseline:

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteDecisionIntakeReview`

Current judgment:

- strongest mainstream homepage line

What is now true:

- the first screen reads more like a product homepage claim surface
- the page has a clearer brand layer
- trust cards and FAQ read more like real pre-sales communication
- the contact area reads more like demo / consultation intake, not only a generic form
- the lower and middle homepage sections now read more like one proof / decision path
- the decision-to-intake path is clearer before the contact surface begins

Why this matters:

- this line now reads much more like a real product-site system than a generic landing template

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

- this line is still the clearest evidence that `ecom_min` is a real minimal storefront frontstage, not a fake shell

Current limit:

- still not a full ecommerce platform
- should not be positioned as merchant backend, payment platform, or operations software

### 4. After-Sales Service Website

Current reviewed baseline:

- `/Users/carwynmac/ai-cl/output_projects/AfterSalesFooterClosureReview`

Current judgment:

- strongest bounded operational-surface line

What is now true:

- the route now reads more like a service-center and tracked-case website surface, not only a support-entry page
- the no-order route now reads more like a real intake entry
- the order-carried route now reads more like a tracked case board
- the tracked route now has a clearer continuous handling path across:
  - snapshot
  - status
  - flow
  - ops
  - history
  - actions
  - active panel
  - timeline / prep guidance
  - footer actions
- the tracked route also now keeps short continuity strips between those sections, so the page reads more like one handling axis than a stack of separate boards

Why this matters:

- it shows the system can support narrower operational website surfaces with real path continuity, while still staying inside website boundaries

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
- `/Users/carwynmac/ai-cl/ail_engine_v5_ecom.py`
- `/Users/carwynmac/ai-cl/testing/cli_smoke.sh`

Not just in sample output directories.

This is especially true for:

- company/product hero, FAQ, trust, and intake layers
- ecommerce discovery, shop, product, cart, checkout, and completion continuity
- after-sales intake, tracked-case board, and lower-half handling continuity

Sample-local helpers still exist for some storefront filled-state / completion-state checks, but those remain explicitly bounded as validation helpers, not product logic.

## Safe Split Status

As of 2026-03-28:

- first-stage safe split is implemented
- `/Users/carwynmac/ai-cl/ail_engine_v5_ecom.py` now contains the ecom / after-sales view-generation cluster
- `/Users/carwynmac/ai-cl/ail_engine_v5.py` remains the main orchestrator and delegates through `AILEcomGeneratorMixin`
- this is the current recommended pause point before any second-stage `landing` extraction

## Best Current Working Interpretation

As of 2026-03-28:

- the supported mainline is still website-first
- the strongest qualitative website is still personal
- the strongest product-homepage website is still company/product
- the strongest end-to-end interaction proof is still ecommerce
- after-sales has become materially stronger as a bounded tracked-case website surface
- the engine is in a healthier maintenance state now that the first split has landed

## One-Line Conclusion

As of 2026-03-28, AIL's supported website frontier is materially stronger than it was on 2026-03-24: ecommerce remains the strongest discovery-to-purchase proof line, company/product remains the strongest mainstream homepage line, personal remains the strongest polish line, and after-sales has now advanced from a service-center surface into a more complete tracked-case handling path while still staying inside honest website boundaries.
