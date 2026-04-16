# Personal Independent Site Pack Delivery Asset

## Core

- support_level: `Supported`
- expected_profile: `landing`
- expected_primary_route: `project_continue_diagnose_compile_sync`
- expected_primary_preview_target: `artifact_root`
- expected_export_primary_target: `artifact_root`

## Requirements

- canonical_requirement: `做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。`
- demo_requirement: `做一个设计师个人网站，包含首页、自我介绍、作品集、客户评价、FAQ、联系方式、立即预约。`
- best_entry_command: `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。" --base-url embedded://local --json`

## Validated Behavior

- detected_profile: `landing`
- trial_status: `ok`
- repair_used: `False`
- managed_files_written: `6`
- project_go_route: `project_continue_diagnose_compile_sync`
- preview_primary_target: `artifact_root`
- export_primary_target_label: `artifact_root`
- delivery_ready: `True`

## Safe Talking Points

- Supported as a personal independent site.
- Strong fit for creator, freelancer, and portfolio-like websites.
- Good for service introduction plus contact-oriented sites.

## Avoid Promising

- blog platform
- creator dashboard
- account-based personal product

## Evidence

- delivery_validation_json: `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.json`
- demo_pack_run_json: `/Users/carwynmac/ai-cl/testing/results/website_demo_pack_run_20260319.json`
