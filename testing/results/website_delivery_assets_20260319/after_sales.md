# After-Sales Service Website Pack Delivery Asset

## Core

- support_level: `Supported`
- expected_profile: `after_sales`
- expected_primary_route: `project_continue_diagnose_compile_sync`
- expected_primary_preview_target: `artifact_root`
- expected_export_primary_target: `artifact_root`

## Requirements

- canonical_requirement: `做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。`
- demo_requirement: `做一个品牌售后服务网站，包含退款申请、换货申请、投诉提交、进度查询说明、联系客服。`
- best_entry_command: `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario after_sales --base-url embedded://local --json`

## Validated Behavior

- detected_profile: `after_sales`
- trial_status: `ok`
- repair_used: `False`
- managed_files_written: `7`
- project_go_route: `project_continue_diagnose_compile_sync`
- preview_primary_target: `artifact_root`
- export_primary_target_label: `artifact_root`
- delivery_ready: `True`

## Safe Talking Points

- Supported as an after-sales service website.
- Strong fit for refund, exchange, and complaint intake surfaces.
- Works best as a support-entry website, not an operations platform.

## Avoid Promising

- support operations platform
- CRM
- internal service console

## Evidence

- delivery_validation_json: `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.json`
- demo_pack_run_json: `/Users/carwynmac/ai-cl/testing/results/website_demo_pack_run_20260319.json`
