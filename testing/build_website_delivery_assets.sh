#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/carwynmac/ai-cl"
RESULTS_DIR="$ROOT/testing/results"
OUT_DIR="$RESULTS_DIR/website_delivery_assets_20260319"
SUMMARY_JSON="$RESULTS_DIR/website_delivery_assets_20260319.json"
SUMMARY_MD="$RESULTS_DIR/website_delivery_assets_20260319.md"
VALIDATION_JSON="$RESULTS_DIR/website_delivery_validation_20260319.json"
DEMO_JSON="$RESULTS_DIR/website_demo_pack_run_20260319.json"

mkdir -p "$OUT_DIR"

python3 - "$ROOT" "$OUT_DIR" "$SUMMARY_JSON" "$SUMMARY_MD" "$VALIDATION_JSON" "$DEMO_JSON" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
summary_json = Path(sys.argv[3])
summary_md = Path(sys.argv[4])
validation_json = Path(sys.argv[5])
demo_json = Path(sys.argv[6])

validation = json.loads(validation_json.read_text(encoding='utf-8'))
demo = json.loads(demo_json.read_text(encoding='utf-8'))

validation_cases = {item['pack']: item for item in validation['cases']}
demo_cases = {item['pack']: item for item in demo['cases']}

packs = [
    {
        'id': 'company_product',
        'pack': 'Company / Product Website Pack',
        'support_level': 'Supported',
        'canonical_requirement': '做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。',
        'demo_requirement': '做一个企业产品官网，包含首页、产品优势、团队介绍、客户评价、FAQ、数据展示、合作伙伴 Logo、联系我们。',
        'expected_profile': 'landing',
        'expected_primary_route': 'project_continue_diagnose_compile_sync',
        'expected_primary_preview_target': 'artifact_root',
        'expected_export_primary_target': 'artifact_root',
        'best_entry_command': 'PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario landing --base-url embedded://local --json',
        'safe_talking_points': [
            'Supported as a company introduction and product website.',
            'Strongest current website-oriented surface.',
            'Best fit for SaaS, brand, and product marketing sites.'
        ],
        'avoid_promises': [
            'complete business system',
            'internal enterprise portal',
            'application dashboard'
        ],
    },
    {
        'id': 'personal_independent',
        'pack': 'Personal Independent Site Pack',
        'support_level': 'Supported',
        'canonical_requirement': '做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。',
        'demo_requirement': '做一个设计师个人网站，包含首页、自我介绍、作品集、客户评价、FAQ、联系方式、立即预约。',
        'expected_profile': 'landing',
        'expected_primary_route': 'project_continue_diagnose_compile_sync',
        'expected_primary_preview_target': 'artifact_root',
        'expected_export_primary_target': 'artifact_root',
        'best_entry_command': 'PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。" --base-url embedded://local --json',
        'safe_talking_points': [
            'Supported as a personal independent site.',
            'Strong fit for creator, freelancer, and portfolio-like websites.',
            'Good for service introduction plus contact-oriented sites.'
        ],
        'avoid_promises': [
            'blog platform',
            'creator dashboard',
            'account-based personal product'
        ],
    },
    {
        'id': 'ecom_storefront',
        'pack': 'Ecommerce Independent Storefront Pack',
        'support_level': 'Supported',
        'canonical_requirement': '做一个数码商城，包含首页商品列表、商品详情、购物车、结算。',
        'demo_requirement': '做一个服装独立站，包含首页横幅、分类导航、商品列表、商品详情、购物车、结算。',
        'expected_profile': 'ecom_min',
        'expected_primary_route': 'project_continue_diagnose_compile_sync',
        'expected_primary_preview_target': 'artifact_root',
        'expected_export_primary_target': 'artifact_root',
        'best_entry_command': 'PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario ecom_min --base-url embedded://local --json',
        'safe_talking_points': [
            'Supported as a minimal ecommerce independent storefront.',
            'Strong fit for simple storefront funnels.',
            'Good for homepage, catalog, product detail, cart, and checkout.'
        ],
        'avoid_promises': [
            'ecommerce platform',
            'merchant backend',
            'inventory, operations, and payment platform'
        ],
    },
    {
        'id': 'after_sales',
        'pack': 'After-Sales Service Website Pack',
        'support_level': 'Supported',
        'canonical_requirement': '做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。',
        'demo_requirement': '做一个品牌售后服务网站，包含退款申请、换货申请、投诉提交、进度查询说明、联系客服。',
        'expected_profile': 'after_sales',
        'expected_primary_route': 'project_continue_diagnose_compile_sync',
        'expected_primary_preview_target': 'artifact_root',
        'expected_export_primary_target': 'artifact_root',
        'best_entry_command': 'PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario after_sales --base-url embedded://local --json',
        'safe_talking_points': [
            'Supported as an after-sales service website.',
            'Strong fit for refund, exchange, and complaint intake surfaces.',
            'Works best as a support-entry website, not an operations platform.'
        ],
        'avoid_promises': [
            'support operations platform',
            'CRM',
            'internal service console'
        ],
    },
    {
        'id': 'blog_style_partial',
        'pack': 'Personal Blog-Style Site Pack',
        'support_level': 'Partial',
        'canonical_requirement': '做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。',
        'demo_requirement': '做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。',
        'expected_profile': 'landing',
        'expected_primary_route': 'project_continue_diagnose_compile_sync',
        'expected_primary_preview_target': 'artifact_root',
        'expected_export_primary_target': 'artifact_root',
        'best_entry_command': 'PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。" --base-url embedded://local --json',
        'safe_talking_points': [
            'Usable as a blog-style personal site.',
            'Position as a content-forward website, not a blog platform.',
            'Keep promises inside the current landing-oriented website surface.'
        ],
        'avoid_promises': [
            'blog platform',
            'CMS',
            'publishing backend'
        ],
    },
]

assets = []
for pack in packs:
    v = validation_cases[pack['pack']]
    d = demo_cases.get(pack['pack'], {})
    payload = {
        'asset_version': '2026-03-19',
        'pack_id': pack['id'],
        'pack': pack['pack'],
        'support_level': pack['support_level'],
        'canonical_requirement': pack['canonical_requirement'],
        'demo_requirement': pack['demo_requirement'],
        'expected_profile': pack['expected_profile'],
        'expected_primary_route': pack['expected_primary_route'],
        'expected_primary_preview_target': pack['expected_primary_preview_target'],
        'expected_export_primary_target': pack['expected_export_primary_target'],
        'best_entry_command': pack['best_entry_command'],
        'recommended_validation_flow': 'trial-run -> project go -> project preview -> project export-handoff',
        'safe_talking_points': pack['safe_talking_points'],
        'avoid_promises': pack['avoid_promises'],
        'validated_behavior': {
            'detected_profile': v['trial_run']['detected_profile'],
            'trial_status': v['trial_run']['status'],
            'repair_used': v['trial_run']['repair_used'],
            'managed_files_written': v['trial_run']['managed_files_written'],
            'project_go_route': v['project_go']['route_taken'],
            'preview_primary_target': v['project_preview']['primary_target'],
            'export_primary_target_label': v['project_export_handoff']['primary_target_label'],
            'delivery_ready': v['validation']['delivery_ready'],
        },
        'demo_behavior': {
            'demo_ready': (d.get('validation') or {}).get('demo_ready'),
            'flow_ok': (d.get('validation') or {}).get('flow_ok'),
        },
        'evidence': {
            'delivery_validation_json': str(validation_json),
            'demo_pack_run_json': str(demo_json),
            'website_frontier_summary': str(root / 'WEBSITE_FRONTIER_SUMMARY_20260319.md'),
            'website_demo_pack': str(root / 'WEBSITE_DEMO_PACK_20260319.md'),
            'website_delivery_checklist': str(root / 'WEBSITE_DELIVERY_CHECKLIST_20260319.md'),
        },
    }
    assets.append(payload)

    json_path = out_dir / f"{pack['id']}.json"
    md_path = out_dir / f"{pack['id']}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        f"# {pack['pack']} Delivery Asset",
        '',
        '## Core',
        '',
        f"- support_level: `{payload['support_level']}`",
        f"- expected_profile: `{payload['expected_profile']}`",
        f"- expected_primary_route: `{payload['expected_primary_route']}`",
        f"- expected_primary_preview_target: `{payload['expected_primary_preview_target']}`",
        f"- expected_export_primary_target: `{payload['expected_export_primary_target']}`",
        '',
        '## Requirements',
        '',
        f"- canonical_requirement: `{payload['canonical_requirement']}`",
        f"- demo_requirement: `{payload['demo_requirement']}`",
        f"- best_entry_command: `{payload['best_entry_command']}`",
        '',
        '## Validated Behavior',
        '',
        f"- detected_profile: `{payload['validated_behavior']['detected_profile']}`",
        f"- trial_status: `{payload['validated_behavior']['trial_status']}`",
        f"- repair_used: `{payload['validated_behavior']['repair_used']}`",
        f"- managed_files_written: `{payload['validated_behavior']['managed_files_written']}`",
        f"- project_go_route: `{payload['validated_behavior']['project_go_route']}`",
        f"- preview_primary_target: `{payload['validated_behavior']['preview_primary_target']}`",
        f"- export_primary_target_label: `{payload['validated_behavior']['export_primary_target_label']}`",
        f"- delivery_ready: `{payload['validated_behavior']['delivery_ready']}`",
        '',
        '## Safe Talking Points',
        '',
    ]
    lines.extend([f"- {item}" for item in payload['safe_talking_points']])
    lines.extend(['', '## Avoid Promising', ''])
    lines.extend([f"- {item}" for item in payload['avoid_promises']])
    lines.extend(['', '## Evidence', '', f"- delivery_validation_json: `{validation_json}`", f"- demo_pack_run_json: `{demo_json}`"])
    md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

manifest = {
    'asset_version': '2026-03-19',
    'status': 'ok' if all(a['validated_behavior']['delivery_ready'] for a in assets if a['support_level'] == 'Supported') else 'attention',
    'asset_dir': str(out_dir),
    'supported_count': sum(1 for a in assets if a['support_level'] == 'Supported'),
    'partial_count': sum(1 for a in assets if a['support_level'] == 'Partial'),
    'delivery_ready_supported_count': sum(1 for a in assets if a['support_level'] == 'Supported' and a['validated_behavior']['delivery_ready']),
    'delivery_ready_partial_count': sum(1 for a in assets if a['support_level'] == 'Partial' and a['validated_behavior']['delivery_ready']),
    'recommended_validation_flow': 'trial-run -> project go -> project preview -> project export-handoff',
    'assets': [
        {
            'pack_id': a['pack_id'],
            'pack': a['pack'],
            'support_level': a['support_level'],
            'expected_profile': a['expected_profile'],
            'expected_primary_route': a['expected_primary_route'],
            'expected_primary_preview_target': a['expected_primary_preview_target'],
            'json_path': str(out_dir / f"{a['pack_id']}.json"),
            'md_path': str(out_dir / f"{a['pack_id']}.md"),
        }
        for a in assets
    ],
}
summary_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

lines = [
    '# Website Delivery Assets 2026-03-19',
    '',
    '## Summary',
    '',
    f"- status: `{manifest['status']}`",
    f"- asset_dir: `{manifest['asset_dir']}`",
    f"- supported_count: `{manifest['supported_count']}`",
    f"- partial_count: `{manifest['partial_count']}`",
    f"- delivery_ready_supported_count: `{manifest['delivery_ready_supported_count']}`",
    f"- delivery_ready_partial_count: `{manifest['delivery_ready_partial_count']}`",
    f"- recommended_validation_flow: `{manifest['recommended_validation_flow']}`",
    '',
    '## Assets',
    '',
]
for asset in manifest['assets']:
    lines.extend([
        f"### {asset['pack']}",
        '',
        f"- support_level: `{asset['support_level']}`",
        f"- expected_profile: `{asset['expected_profile']}`",
        f"- expected_primary_route: `{asset['expected_primary_route']}`",
        f"- expected_primary_preview_target: `{asset['expected_primary_preview_target']}`",
        f"- json_path: `{asset['json_path']}`",
        f"- md_path: `{asset['md_path']}`",
        '',
    ])
summary_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')

print(summary_md)
print(summary_json)
print(out_dir)
PY

echo "Website delivery asset summary: $SUMMARY_MD"
echo "Website delivery asset summary JSON: $SUMMARY_JSON"
echo "Website delivery asset directory: $OUT_DIR"
