# Personal Blog-Style Site Pack Delivery Asset

## Core

- support_level: `Partial`
- expected_profile: `landing`
- expected_primary_route: `project_continue_diagnose_compile_sync`
- expected_primary_preview_target: `artifact_root`
- expected_export_primary_target: `artifact_root`

## Requirements

- canonical_requirement: `做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。`
- demo_requirement: `做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。`
- best_entry_command: `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。" --base-url embedded://local --json`

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

- Usable as a blog-style personal site.
- Position as a content-forward website, not a blog platform.
- Keep promises inside the current landing-oriented website surface.

## Avoid Promising

- blog platform
- CMS
- publishing backend

## Evidence

- delivery_validation_json: `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.json`
- demo_pack_run_json: `/Users/carwynmac/ai-cl/testing/results/website_demo_pack_run_20260319.json`
