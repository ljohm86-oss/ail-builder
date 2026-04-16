# System vs Test Helper Detailed Matrix

## Purpose

This file is the detailed follow-up to:

- `/Users/carwynmac/ai-cl/SYSTEM_VS_TEST_HELPER_BOUNDARY_20260322.md`

It breaks the current website-quality work into three active lines:

- personal independent site
- company / product website
- ecommerce storefront

For each line, it records:

- what is already system-level
- what was only sample-local test support
- what has direct rendered runtime evidence

## Reading Rule

Use this interpretation consistently:

- changes in `/Users/carwynmac/ai-cl/ail_engine_v5.py` are product-system changes
- changes only inside `/Users/carwynmac/ai-cl/output_projects/...` are sample-local unless explicitly promoted back into the generator
- screenshots validate quality, but they do not by themselves prove that a behavior is system-level

## Personal Independent Site

### System-level changes

These are already part of the generator:

- single-page anchor navigation instead of broken route links
- personal-site fallback visible brand naming
- hero title and supporting copy that read more like a personal portfolio
- dedicated `About` section rather than only a hero anchor
- warmer visual treatment for the personal portfolio surface
- stronger persona expression in the hero entrance
- stronger service-section copy
- portfolio cards that read more like compact project cards
- clearer separation between case types
- stronger narrative connection from `About` into the case collection
- collaboration/method language that reads more like a real working style

Primary system file:

- `/Users/carwynmac/ai-cl/ail_engine_v5.py`

### Sample-local test helpers

No recent personal-site quality improvements depended on seeded runtime data or sample-only state helpers.

Personal-site validation was mostly:

- regenerate a fresh sample
- run the site
- capture screenshots

### Latest runtime evidence

Latest strongest personal-site sample referenced in the current review:

- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteStoryReview`

Other recent personal-site runtime checkpoints that led to the current baseline:

- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteVisualIdentityReview`
- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteCaseReview`
- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteCaseReview2`
- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteCaseStructureReview`
- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSitePersonaReview`

Representative runtime screenshots:

- `/tmp/personal_independent_site_visual_identity_review_headless.png`
- `/tmp/personal_independent_site_case_review_headless.png`
- `/tmp/personal_independent_site_case_review2_headless.png`
- `/tmp/personal_independent_site_case_structure_review_headless.png`
- `/tmp/personal_independent_site_persona_review_headless.png`
- `/tmp/personal_independent_site_story_review_headless.png`

### Current truth

Personal-site quality gains are predominantly system-level and have direct rendered evidence.

## Company / Product Website

### System-level changes

These are already part of the generator:

- fallback brand handling so raw generated project names do not leak as the hero brand
- stronger company/product hero copy
- stronger product-intro layer
- stronger FAQ defaults
- clearer trust/testimonial structure
- clearer product-site brand treatment
- stronger dark navigation pill treatment
- stronger trust / FAQ brand accents
- clearer hero brand-row layer
- clearer hero brand-mark layer
- compact hero brand-grid exposing fit / scenario / next-step metadata
- tighter hero claim language
- stronger first-screen rhythm through headline scale, spacing, CTA weight, and signal structure

Primary system file:

- `/Users/carwynmac/ai-cl/ail_engine_v5.py`

### Sample-local test helpers

No recent company/product-site quality work relied on seeded demo-state helpers.

Validation was mostly:

- regenerate a fresh sample
- run the site
- capture rendered screenshots

### Latest runtime evidence

Latest strongest company/product-site sample referenced in the current review:

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandLineReview`

Important recent runtime checkpoints that led to the current baseline:

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteTrustReview`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteTrustReview2`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteTrustReview3`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteVisualReview`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteTrustSurfaceReview`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteTrustSurfaceReview2`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandIdentityReview`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandIdentityReview2`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandIdentityReview3`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteHeroTempoReview`
- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandDifferentiationReview`

Representative runtime screenshots:

- `/tmp/company_product_site_visual_review_headless.png`
- `/tmp/company_product_site_trust_surface_review_headless.png`
- `/tmp/company_product_site_trust_surface_review2_headless.png`
- `/tmp/company_product_site_brand_identity_review_headless.png`
- `/tmp/company_product_site_brand_identity_review2_headless.png`
- `/tmp/company_product_site_brand_identity_review3_headless.png`
- `/tmp/company_product_site_hero_tempo_review_headless.png`
- `/tmp/company_product_site_brand_differentiation_review_headless.png`
- `/tmp/company_product_site_brand_line_review_headless.png`

### Current truth

Company/product-site gains are predominantly system-level and have direct rendered evidence.

## Ecommerce Storefront

### System-level changes

These are already part of the generator:

- cleaner storefront shell for `ecom_min`
- removal of broken storefront after-sales navigation in storefront pages
- safer default frontend behavior with no forced empty backend proxies
- cleaner home/product shell treatment
- stronger product detail structure
- stronger cart layout and summary panel
- stronger checkout flow surface
- checkout no longer forcing the storefront flow into a broken route
- explicit checkout text-color and readability fixes so important content does not disappear into dark-shell inheritance

Primary system file:

- `/Users/carwynmac/ai-cl/ail_engine_v5.py`

### Sample-local test helpers

Ecommerce validation did use sample-local helpers.

Those helpers were only used so that runtime screenshots could be captured in a non-empty state.

Typical helper pattern:

- add `?demo_seed=filled`
- if `localStorage` cart is empty, seed two items into the cart

Typical helper targets:

- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontFlowReview/frontend/src/views/Cart.vue`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontFlowReview/frontend/src/views/Checkout.vue`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCartDensityReview/frontend/src/views/Cart.vue`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCartDensityReview/frontend/src/views/Checkout.vue`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCartDensityReview2/frontend/src/views/Cart.vue`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCartDensityReview2/frontend/src/views/Checkout.vue`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCheckoutColorReview/frontend/src/views/Checkout.vue`

These helpers are not product features.

They only existed to validate:

- filled cart state
- filled checkout state
- rendered density and readability

### Latest runtime evidence

Current system-level storefront baseline used in the main review:

- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontSurfaceReview3`

Additional runtime checkpoints that exposed later ecommerce quality issues and fixes:

- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontFlowReview`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCartDensityReview`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCartDensityReview2`
- `/Users/carwynmac/ai-cl/output_projects/EcomStorefrontCheckoutColorReview`

Representative runtime screenshots:

- `/tmp/ecom_storefront_surface_review3_home_headless.png`
- `/tmp/ecom_storefront_surface_review3_product_headless.png`
- `/tmp/ecom_storefront_flow_review_cart_headless.png`
- `/tmp/ecom_storefront_flow_review_checkout_headless.png`
- `/tmp/ecom_storefront_flow_review_cart_filled_headless.png`
- `/tmp/ecom_storefront_flow_review_checkout_filled_headless.png`
- `/tmp/ecom_storefront_cart_density_review_cart_filled_headless.png`
- `/tmp/ecom_storefront_cart_density_review_checkout_filled_headless.png`
- `/tmp/ecom_storefront_cart_density_review2_cart_filled_headless.png`
- `/tmp/ecom_storefront_cart_density_review2_checkout_filled_headless.png`
- `/tmp/ecom_storefront_checkout_color_review_filled_headless.png`

### Current truth

Ecommerce quality gains are mostly system-level, but the filled-state screenshot evidence did rely on sample-local seeding helpers.

That means:

- storefront shell, cart structure, checkout structure, broken-link cleanup, and readability fixes are system truth
- filled cart/checkout screenshots prove the rendered quality of those structures under sample-local seeded data
- the presence of demo cart items is not itself a product feature

## Summary Table

| Line | System-level quality improvements | Sample-local helper used | Direct runtime screenshot evidence |
| --- | --- | --- | --- |
| Personal Independent Site | Yes | No | Yes |
| Company / Product Website | Yes | No | Yes |
| Ecommerce Storefront | Yes | Yes, for filled-state only | Yes |

## Operational Rule Going Forward

When summarizing progress:

1. claim capability gains from generator changes
2. claim runtime quality from screenshots
3. call out sample-local seeding explicitly when used

This keeps product truth accurate without throwing away useful runtime validation.
