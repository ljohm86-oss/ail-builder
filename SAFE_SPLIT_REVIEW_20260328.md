# SAFE_SPLIT_REVIEW_20260328

## Current Status

Phase-1 extraction is now implemented.

Current module shape after extraction:
- `/Users/carwynmac/ai-cl/ail_engine_v5.py`: 3315 lines, 205870 bytes
- `/Users/carwynmac/ai-cl/ail_engine_v5_ecom.py`: 3179 lines, 243986 bytes

What has already moved into `/Users/carwynmac/ai-cl/ail_engine_v5_ecom.py`:
- `_is_ecom_page`
- `_ecom_component_props`
- `_after_sales_component_props`
- `_ecom_product_image_data_uri`
- `_ecom_mock_products_js`
- `_generate_ecom_home_view`
- `_generate_ecom_product_view`
- `_generate_ecom_cart_view`
- `_generate_ecom_checkout_view`
- `_generate_ecom_category_view`
- `_generate_ecom_shop_view`
- `_generate_ecom_search_view`
- `_generate_ecom_after_sales_view`

Compatibility status:
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`
- `status = ok`

Recommended pause point after phase 1:
- stop here and treat this as a stable split checkpoint
- do not move straight into `landing` extraction without a separate second-stage review
- use the new module boundary first, and only reopen deeper engine reshaping if a clear maintenance need appears

## Scope

Audit target:
- `/Users/carwynmac/ai-cl/ail_engine_v5.py`

Goal:
- identify the safest first extraction point
- avoid destabilizing the runtime-backed website baselines

## Current file shape

Observed size:
- lines: 6485
- size: 439K
- characters: 421589

Observed generator counts:
- `_generate_*` methods: 14

Largest generator methods inside `AILProjectGeneratorV5`:
- `_generate_landing_view`: 1501 lines
- `_generate_ecom_after_sales_view`: 714 lines
- `_generate_ecom_product_view`: 509 lines
- `_generate_ecom_checkout_view`: 495 lines
- `_generate_ecom_home_view`: 346 lines
- `_generate_ecom_cart_view`: 340 lines
- `_generate_ecom_shop_view`: 262 lines
- `_generate_app_home_view`: 214 lines
- `_generate_ecom_search_view`: 195 lines
- `_generate_ecom_category_view`: 182 lines

Approximate responsibility footprint inside `AILProjectGeneratorV5`:
- ecom-related methods/helpers: 3134 lines
- landing-related methods/helpers: 1587 lines
- app-related methods/helpers: 251 lines
- other/core/shared logic: 1284 lines

## Recommendation

Safest first split:
- extract the ecom/after-sales view-generation cluster first

Reasoning:
1. It is the largest cohesive cluster in the file.
2. It already has relatively clear boundaries:
   - `_is_ecom_page`
   - `_ecom_component_props`
   - `_after_sales_component_props`
   - `_ecom_product_image_data_uri`
   - `_ecom_mock_products_js`
   - `_generate_ecom_home_view`
   - `_generate_ecom_product_view`
   - `_generate_ecom_cart_view`
   - `_generate_ecom_checkout_view`
   - `_generate_ecom_category_view`
   - `_generate_ecom_shop_view`
   - `_generate_ecom_search_view`
   - `_generate_ecom_after_sales_view`
3. Recent runtime-backed work has concentrated here, so extracting it would remove the most pressure from the main file.
4. The dispatcher already isolates these pages by route, which makes delegation cleaner than landing.

## Why not split landing first

`landing` is the single largest method, but it is a worse first cut:
- the logic is dense and highly branched
- it mixes personal and business variants in one generator
- it is more likely to require internal reshaping before extraction
- a first-pass extraction there carries higher regression risk

Conclusion:
- `landing` is a good second-stage refactor target
- it is not the safest first extraction

## Why not split app first

`app_min` is too small to justify being the first split:
- low payoff
- does not materially reduce file size or maintenance pressure

## Suggested first extraction boundary

Preferred first module candidate:
- `/Users/carwynmac/ai-cl/ail_engine_v5_ecom.py`

Move in phase 1:
- ecom helper methods
- ecom mock-data/image helpers
- all ecom/after-sales view generators

Keep in `/Users/carwynmac/ai-cl/ail_engine_v5.py` for phase 1:
- parser classes
- project orchestration
- shared write/build helpers
- landing generators
- app generators
- top-level dispatch method, but make it delegate to imported ecom helpers

## Lowest-risk migration shape

Phase 1:
- extract pure helper/render methods only
- keep method signatures compatible with current class usage
- keep dispatcher behavior unchanged

Phase 2:
- switch `_generate_vue_view` to delegate into the extracted ecom module
- keep smoke coverage unchanged

Phase 3:
- only after ecom extraction is stable, consider splitting landing

## Practical first step

If we implement this refactor, the safest first patch is:
- create `/Users/carwynmac/ai-cl/ail_engine_v5_ecom.py`
- move only:
  - `_ecom_product_image_data_uri`
  - `_ecom_mock_products_js`
  - `_generate_ecom_home_view`
  - `_generate_ecom_product_view`
  - `_generate_ecom_cart_view`
  - `_generate_ecom_checkout_view`
  - `_generate_ecom_category_view`
  - `_generate_ecom_shop_view`
  - `_generate_ecom_search_view`
  - `_generate_ecom_after_sales_view`
- leave `_is_ecom_page`, `_ecom_component_props`, and `_after_sales_component_props` in place initially if needed for a smaller first diff

## Bottom line

Best first split:
- `ecom` cluster first

Best second split:
- `landing` cluster later

Do not start with:
- `app_min`
- parser/build orchestration
- shared CLI/runtime glue
