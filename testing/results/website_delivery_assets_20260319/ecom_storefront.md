# Ecommerce Independent Storefront Pack Delivery Asset

## Core

- support_level: `Supported`
- expected_profile: `ecom_min`
- expected_primary_route: `project_continue_diagnose_compile_sync`
- expected_primary_preview_target: `artifact_root`
- expected_export_primary_target: `artifact_root`

## Requirements

- canonical_requirement: `做一个数码商城，包含首页商品列表、商品详情、购物车、结算。`
- demo_requirement: `做一个服装独立站，包含首页横幅、分类导航、商品列表、商品详情、购物车、结算。`
- best_entry_command: `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario ecom_min --base-url embedded://local --json`

## Validated Behavior

- detected_profile: `ecom_min`
- trial_status: `ok`
- repair_used: `False`
- managed_files_written: `10`
- project_go_route: `project_continue_diagnose_compile_sync`
- preview_primary_target: `artifact_root`
- export_primary_target_label: `artifact_root`
- delivery_ready: `True`

## Safe Talking Points

- Supported as a minimal ecommerce independent storefront.
- Strong fit for simple storefront funnels.
- Good for homepage, catalog, product detail, cart, and checkout.

## Avoid Promising

- ecommerce platform
- merchant backend
- inventory, operations, and payment platform

## Evidence

- delivery_validation_json: `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.json`
- demo_pack_run_json: `/Users/carwynmac/ai-cl/testing/results/website_demo_pack_run_20260319.json`
