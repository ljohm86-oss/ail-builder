from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path("/Users/carwynmac/ai-cl")
INPUT_PATH = ROOT / "testing" / "raw_model_outputs_v1" / "raw_model_outputs_v1.json"
RESULTS_DIR = ROOT / "testing" / "results"
RESULTS_JSON = RESULTS_DIR / "raw_model_outputs_results.json"
RESULTS_MD = RESULTS_DIR / "raw_model_outputs_report.md"

PATCH_VALIDATION_IDS = {"RAW_L9", "RAW_A4", "RAW_P4"}


def load_helper():
    module_path = ROOT / "testing" / "repair_smoke_runner.py"
    spec = importlib.util.spec_from_file_location("repair_smoke_runner", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load helper module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helper = load_helper()


def normalized_ui_tokens(ail_text: str) -> set[str]:
    parsed = helper.parse_program(ail_text)
    return {helper.UI_REPLACEMENTS.get(token, token) for page in parsed["pages"] for token in page["ui"]}


def normalized_flows(ail_text: str) -> set[str]:
    parsed = helper.parse_program(ail_text)
    return {helper.FLOW_REPLACEMENTS.get(flow, flow) for flow in parsed["flows"]}


def detect_under_specified(category: str, requirement: str, ail_text: str) -> bool:
    ui_tokens = normalized_ui_tokens(ail_text)
    flows = normalized_flows(ail_text)
    if category == "landing":
        checks = [
            (
                ("功能" in requirement) or ("服务" in requirement) or ("FAQ" in requirement) or ("常见问题" in requirement),
                "landing:FeatureGrid",
            ),
            (
                any(word in requirement for word in ["团队", "团队介绍", "成员", "关于我们", "关于团队"]),
                "landing:Team",
            ),
            (any(word in requirement for word in ["FAQ", "常见问题", "常见问答", "问答"]), "landing:FAQ"),
            ("联系" in requirement, "landing:Contact"),
            (
                any(word in requirement for word in ["数据", "统计", "数字", "数据展示", "公司数据展示", "关键数据"]),
                "landing:Stats",
            ),
            (
                ("客户 Logo" in requirement)
                or ("客户标识" in requirement)
                or ("客户 logos" in requirement)
                or ("合作伙伴" in requirement)
                or ("合作伙伴 logo" in requirement)
                or ("品牌墙" in requirement)
                or ("客户墙" in requirement)
                or any(word in requirement.lower() for word in ["logo", "logos", "partners", "partner logos", "logo wall"]),
                "landing:LogoCloud",
            ),
            (
                ("客户评价" in requirement)
                or ("用户评价" in requirement)
                or ("评价" in requirement)
                or ("testimonial" in requirement.lower())
                or ("testimonials" in requirement.lower())
                or ("用户反馈" in requirement)
                or ("客户反馈" in requirement)
                or ("review block" in requirement.lower())
                or ("customer review" in requirement.lower())
                or ("口碑" in requirement),
                "landing:Testimonial",
            ),
            (
                ("职位展示" in requirement)
                or ("招聘岗位" in requirement)
                or ("职位列表" in requirement)
                or ("jobs" in requirement.lower())
                or ("careers" in requirement.lower())
                or ("join us" in requirement.lower())
                or ("招聘信息" in requirement),
                "landing:Jobs",
            ),
            (
                ("项目作品" in requirement)
                or ("作品集" in requirement)
                or ("portfolio" in requirement.lower())
                or ("案例展示" in requirement)
                or ("case studies" in requirement.lower())
                or ("项目案例" in requirement)
                or ("作品展示" in requirement),
                "landing:Portfolio",
            ),
            ((("开始" in requirement) or ("预约演示" in requirement) or ("试用" in requirement)), "landing:CTA"),
        ]
        if any(required and token not in ui_tokens for required, token in checks):
            return True
        if "联系" in requirement and "CONTACT_SUBMIT" not in flows:
            return True
    elif category == "ecom_min":
        checks = [
            ("商品" in requirement, "ecom:ProductGrid"),
            ("详情" in requirement, "ecom:ProductDetail"),
            ("购物车" in requirement, "ecom:CartPanel"),
            ("结算" in requirement, "ecom:CheckoutPanel"),
            (
                any(word in requirement for word in ["横幅", "首页横幅", "促销"]) or "banner" in requirement.lower(),
                "ecom:Banner",
            ),
            (
                any(word in requirement for word in ["分类", "分类导航", "分类页", "筛选"]) or "filters" in requirement.lower(),
                "ecom:CategoryNav",
            ),
            (
                any(word in requirement for word in ["店铺", "店铺页", "品牌店铺"]) or "shop" in requirement.lower(),
                "ecom:ShopHeader",
            ),
            (
                any(word in requirement for word in ["搜索", "搜索结果", "搜索结果页"]) or "search" in requirement.lower(),
                "ecom:SearchResultGrid",
            ),
        ]
        if any(required and token not in ui_tokens for required, token in checks):
            return True
    elif category == "after_sales":
        checks = [
            ("退款" in requirement, "after_sales:Refund"),
            ("换货" in requirement, "after_sales:Exchange"),
            (any(word in requirement for word in ["投诉", "升级"]), "after_sales:Complaint"),
            (any(word in requirement for word in ["客服", "联系客服", "support", "客服支持", "在线客服"]), "after_sales:Support"),
        ]
        if any(required and token not in ui_tokens for required, token in checks):
            return True
    elif category == "app_min":
        checks = [
            (any(word in requirement for word in ["顶部栏", "顶部", "header"]), "app:TopBar"),
            (any(word in requirement for word in ["底部 tab", "底部", "tab"]), "app:BottomTab"),
            (any(word in requirement for word in ["聊天", "消息"]), "app:ChatWindow"),
            (any(word in requirement for word in ["列表", "联系人", "任务", "笔记"]), "app:List"),
            (any(word in requirement for word in ["卡片", "个人", "发现", "我的", "详情"]), "app:Card"),
            (
                any(word in requirement for word in ["新增任务", "编辑", "编辑输入", "输入", "输入内容", "输入框", "composer"]),
                "app:Composer",
            ),
            (any(word in requirement for word in ["搜索联系人", "搜索", "search", "search bar", "查找"]), "app:SearchBar"),
        ]
        if any(required and token not in ui_tokens for required, token in checks):
            return True
    return False


def extract_issue_types(category: str, requirement: str, ail_text: str, diagnosis: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if diagnosis["multiple_profiles"] == "yes":
        issues.append("multiple_profiles")
    if diagnosis["structure_valid"] == "no":
        issues.append("structure_invalid")
    if diagnosis.get("alias_components"):
        issues.append("alias_component")
    if diagnosis.get("alias_flows"):
        issues.append("alias_flow")
    if diagnosis["unknown_components"]:
        issues.append("unknown_component")
    if diagnosis["unknown_flows"]:
        issues.append("unknown_flow")
    if diagnosis["unsupported_constructs"]:
        if any(item in {"---"} or item.startswith("**Task") or item.startswith("```") for item in diagnosis["unsupported_constructs"]):
            issues.append("multi_result_wrapper")
        else:
            issues.append("unsupported_constructs")
    if diagnosis["boundary_exceeded"] == "yes":
        if category == "app_min":
            issues.append("app_min_boundary_exceeded")
        else:
            issues.append("boundary_exceeded")
    if detect_under_specified(category, requirement, ail_text):
        issues.append("under_specified")
    return issues


def infer_sample_cohort(sample: dict[str, Any]) -> str:
    if sample.get("sample_cohort"):
        return str(sample["sample_cohort"])
    if sample["source_type"] == "clean_control" or "clean_control" in sample.get("expected_noise_tags", []):
        return "clean_control"
    if sample["id"] in PATCH_VALIDATION_IDS:
        return "patch_validation"
    return "legacy_raw"


def expected_installed_tokens(category: str, requirement: str) -> set[str]:
    expected: set[str] = set()
    lower = requirement.lower()
    if category == "landing":
        if (
            any(word in requirement for word in ["客户评价", "用户评价", "评价", "用户反馈", "客户反馈", "口碑"])
            or "testimonial" in lower
            or "testimonials" in lower
            or "review block" in lower
            or "customer review" in lower
        ):
            expected.add("landing:Testimonial")
        if any(word in requirement for word in ["职位展示", "招聘岗位", "职位列表", "招聘信息"]) or any(word in lower for word in ["jobs", "careers", "join us"]):
            expected.add("landing:Jobs")
        if any(word in requirement for word in ["项目作品", "作品集", "案例展示", "项目案例", "作品展示"]) or any(word in lower for word in ["portfolio", "case studies"]):
            expected.add("landing:Portfolio")
    elif category == "app_min":
        if any(word in requirement for word in ["新增任务", "编辑", "编辑输入", "输入", "输入内容", "输入框", "composer"]):
            expected.add("app:Composer")
        if any(word in requirement for word in ["搜索联系人", "搜索", "查找"]) or any(word in lower for word in ["search", "search bar"]):
            expected.add("app:SearchBar")
    return expected


def recoverable_patterns_for_sample(
    sample: dict[str, Any],
    pre_issues: list[str],
    post_issues: list[str],
    repaired_output: str,
) -> list[str]:
    category = sample["category"]
    requirement = sample["requirement"]
    pre_ui = normalized_ui_tokens(sample["raw_output"])
    post_ui = normalized_ui_tokens(repaired_output)
    patterns: list[str] = []

    if (
        category == "after_sales"
        and any(word in requirement for word in ["客服", "联系客服", "support", "客服支持", "在线客服"])
        and "after_sales:Support" not in pre_ui
        and "after_sales:Support" in post_ui
        and "under_specified" in pre_issues
        and "under_specified" not in post_issues
    ):
        patterns.append("recoverable_support_gap")

    if (
        category == "app_min"
        and "app_min_boundary_exceeded" in pre_issues
        and "app_min_boundary_exceeded" not in post_issues
    ):
        patterns.append("recoverable_app_boundary_violation")

    expected = expected_installed_tokens(category, requirement)
    if expected:
        recovered = {token for token in expected if token not in pre_ui and token in post_ui}
        if recovered:
            patterns.append("recoverable_coverage_gap")

    return patterns


def normalized_issue_types(pre_issues: list[str], recoverable_patterns: list[str]) -> list[str]:
    normalized = list(pre_issues)
    if "recoverable_support_gap" in recoverable_patterns and "under_specified" in normalized:
        normalized.remove("under_specified")
    if "recoverable_coverage_gap" in recoverable_patterns and "under_specified" in normalized:
        normalized.remove("under_specified")
    if "recoverable_app_boundary_violation" in recoverable_patterns and "app_min_boundary_exceeded" in normalized:
        normalized.remove("app_min_boundary_exceeded")
    for item in recoverable_patterns:
        if item not in normalized:
            normalized.append(item)
    return normalized


def pct(numerator: int, denominator: int) -> float:
    return round((numerator / denominator) * 100, 2) if denominator else 0.0


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Raw Model Outputs Report",
        "",
        "## Summary",
        f"- total_samples: {payload['summary']['total_samples']}",
        f"- initial_compile_candidates: {payload['summary']['initial_compile_candidates']}",
        f"- repair_attempts: {payload['summary']['repair_attempts']}",
        f"- repair_success: {payload['summary']['repair_success']}",
        f"- final_compile_candidates: {payload['summary']['final_compile_candidates']}",
        "",
        "## Category Breakdown",
        "",
    ]
    for category in ["landing", "ecom_min", "after_sales", "app_min"]:
        stats = payload["category_breakdown"][category]
        lines.extend(
            [
                f"### {category}",
                f"- total: {stats['total']}",
                f"- initial_compile_candidates: {stats['initial_compile_candidates']}",
                f"- repair_success: {stats['repair_success']}",
                f"- final_compile_candidates: {stats['final_compile_candidates']}",
                "",
            ]
        )

    lines.extend(["## By Cohort", ""])
    for cohort in ["legacy_raw", "patch_validation", "clean_control"]:
        stats = payload["cohort_breakdown"].get(cohort, {})
        lines.extend(
            [
                f"### {cohort}",
                f"- total: {stats.get('total', 0)}",
                f"- initial_compile_candidates: {stats.get('initial_compile_candidates', 0)}",
                f"- repair_attempts: {stats.get('repair_attempts', 0)}",
                f"- repair_success: {stats.get('repair_success', 0)}",
                f"- final_compile_candidates: {stats.get('final_compile_candidates', 0)}",
                f"- initial_compile_rate: {stats.get('initial_compile_rate', 0.0)}",
                f"- final_compile_rate: {stats.get('final_compile_rate', 0.0)}",
                f"- recoverable_patterns: {', '.join(f'{k}:{v}' for k, v in stats.get('recoverable_pattern_counts', {}).items()) if stats.get('recoverable_pattern_counts') else 'none'}",
                "",
            ]
        )

    comparison = payload["legacy_vs_patch_validation"]
    lines.extend(
        [
            "## Legacy vs Patch Validation Comparison",
            f"- legacy_raw.initial_compile_rate: {comparison['legacy_raw']['initial_compile_rate']}",
            f"- legacy_raw.final_compile_rate: {comparison['legacy_raw']['final_compile_rate']}",
            f"- patch_validation.initial_compile_rate: {comparison['patch_validation']['initial_compile_rate']}",
            f"- patch_validation.final_compile_rate: {comparison['patch_validation']['final_compile_rate']}",
            f"- patch_validation.recoverable_patterns: {', '.join(f'{k}:{v}' for k, v in comparison['patch_validation'].get('recoverable_pattern_counts', {}).items()) if comparison['patch_validation'].get('recoverable_pattern_counts') else 'none'}",
            "",
            "## Recoverable Patterns",
        ]
    )
    if payload["recoverable_pattern_counts"]:
        for issue, count in payload["recoverable_pattern_counts"]:
            lines.append(f"- {issue}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Top Issues"])
    if payload["top_issues"]:
        for issue, count in payload["top_issues"]:
            lines.append(f"- {issue}: {count}")
    else:
        lines.append("- none")

    lines.extend(["", "## Normalized Top Issues"])
    if payload["normalized_top_issues"]:
        for issue, count in payload["normalized_top_issues"]:
            lines.append(f"- {issue}: {count}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("## Sample Results")
    for item in payload["results"]:
        final_status = "PASS" if item["post_compile_recommended"] else "FAIL"
        lines.extend(
            [
                "",
                f"### {item['id']}",
                f"- category: {item['category']}",
                f"- source_type: {item['source_type']}",
                f"- sample_cohort: {item['sample_cohort']}",
                f"- pre_compile_recommended: {'yes' if item['pre_compile_recommended'] else 'no'}",
                f"- repair_applied: {'yes' if item['repair_applied'] else 'no'}",
                f"- post_compile_recommended: {'yes' if item['post_compile_recommended'] else 'no'}",
                f"- final_profile: {item['final_profile']}",
                f"- issues: {', '.join(item['issues']) if item['issues'] else 'none'}",
                f"- normalized_issue_types: {', '.join(item['normalized_issue_types']) if item['normalized_issue_types'] else 'none'}",
                f"- recoverable_patterns: {', '.join(item['recoverable_patterns']) if item['recoverable_patterns'] else 'none'}",
                f"- post_repair_signal_types: {', '.join(item['post_repair_signal_types']) if item['post_repair_signal_types'] else 'none'}",
                f"- final_status: {final_status}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    samples = payload["samples"]
    results = []
    issue_counter: Counter[str] = Counter()
    normalized_issue_counter: Counter[str] = Counter()
    recoverable_pattern_counter: Counter[str] = Counter()
    category_breakdown = {
        category: {"total": 0, "initial_compile_candidates": 0, "repair_success": 0, "final_compile_candidates": 0}
        for category in ["landing", "ecom_min", "after_sales", "app_min"]
    }
    cohort_breakdown = {
        cohort: {
            "total": 0,
            "initial_compile_candidates": 0,
            "repair_attempts": 0,
            "repair_success": 0,
            "final_compile_candidates": 0,
            "recoverable_pattern_counts": Counter(),
        }
        for cohort in ["legacy_raw", "patch_validation", "clean_control"]
    }

    initial_compile_candidates = 0
    repair_attempts = 0
    repair_success = 0
    final_compile_candidates = 0

    for sample in samples:
        category = sample["category"]
        cohort = infer_sample_cohort(sample)
        requirement = sample["requirement"]
        raw_output = sample["raw_output"]
        pre = helper.diagnose(requirement, raw_output)
        pre_ok = pre["compile_recommended"] == "yes"
        pre_issues = extract_issue_types(category, requirement, raw_output, pre)
        issue_counter.update(pre_issues)

        repair_applied = False
        repaired_output = raw_output
        if not pre_ok or "under_specified" in pre_issues:
            repair_applied = True
            repair_attempts += 1
            repaired_output = helper.repair(requirement, raw_output)

        post = helper.diagnose(requirement, repaired_output)
        post_ok = post["compile_recommended"] == "yes"
        post_issues = extract_issue_types(category, requirement, repaired_output, post)
        recoverable_patterns = recoverable_patterns_for_sample(sample, pre_issues, post_issues, repaired_output)
        normalized_issues = normalized_issue_types(pre_issues, recoverable_patterns)
        normalized_issue_counter.update(normalized_issues)
        recoverable_pattern_counter.update(recoverable_patterns)

        post_repair_signal_types = list(post_issues)
        if repair_applied and post_ok:
            post_repair_signal_types.append("compile_candidate_after_repair")
        if recoverable_patterns:
            post_repair_signal_types.extend(recoverable_patterns)
        post_repair_signal_types = list(dict.fromkeys(post_repair_signal_types))

        category_breakdown[category]["total"] += 1
        cohort_breakdown[cohort]["total"] += 1
        if pre_ok:
            category_breakdown[category]["initial_compile_candidates"] += 1
            cohort_breakdown[cohort]["initial_compile_candidates"] += 1
            initial_compile_candidates += 1
        if repair_applied:
            cohort_breakdown[cohort]["repair_attempts"] += 1
        if repair_applied and post_ok:
            category_breakdown[category]["repair_success"] += 1
            cohort_breakdown[cohort]["repair_success"] += 1
            repair_success += 1
        if post_ok:
            category_breakdown[category]["final_compile_candidates"] += 1
            cohort_breakdown[cohort]["final_compile_candidates"] += 1
            final_compile_candidates += 1
        cohort_breakdown[cohort]["recoverable_pattern_counts"].update(recoverable_patterns)

        results.append(
            {
                "id": sample["id"],
                "category": category,
                "source_type": sample["source_type"],
                "sample_cohort": cohort,
                "requirement": requirement,
                "raw_output": raw_output,
                "generated_ail": raw_output,
                "pre_compile_recommended": pre_ok,
                "repair_applied": repair_applied,
                "post_compile_recommended": post_ok,
                "final_profile": post["detected_profile"],
                "issues": pre_issues,
                "normalized_issue_types": normalized_issues,
                "recoverable_patterns": recoverable_patterns,
                "post_repair_signal_types": post_repair_signal_types,
                "expected_noise_tags": sample["expected_noise_tags"],
                "pre_diagnosis": pre,
                "post_diagnosis": post,
                "repaired_output": repaired_output,
                "post_issues": post_issues,
            }
        )

    for cohort, stats in cohort_breakdown.items():
        stats["recoverable_pattern_counts"] = dict(stats["recoverable_pattern_counts"])
        stats["initial_compile_rate"] = pct(stats["initial_compile_candidates"], stats["total"])
        stats["final_compile_rate"] = pct(stats["final_compile_candidates"], stats["total"])

    summary = {
        "total_samples": len(samples),
        "initial_compile_candidates": initial_compile_candidates,
        "repair_attempts": repair_attempts,
        "repair_success": repair_success,
        "final_compile_candidates": final_compile_candidates,
        "source_file": str(INPUT_PATH),
        "source_version": payload.get("version", "unknown"),
        "cohort_types": ["legacy_raw", "patch_validation", "clean_control"],
    }
    legacy = cohort_breakdown["legacy_raw"]
    patch_validation = cohort_breakdown["patch_validation"]
    output = {
        "summary": summary,
        "category_breakdown": category_breakdown,
        "cohort_breakdown": cohort_breakdown,
        "legacy_vs_patch_validation": {
            "legacy_raw": {
                "initial_compile_rate": legacy["initial_compile_rate"],
                "final_compile_rate": legacy["final_compile_rate"],
                "recoverable_pattern_counts": legacy["recoverable_pattern_counts"],
            },
            "patch_validation": {
                "initial_compile_rate": patch_validation["initial_compile_rate"],
                "final_compile_rate": patch_validation["final_compile_rate"],
                "recoverable_pattern_counts": patch_validation["recoverable_pattern_counts"],
            },
        },
        "top_issues": issue_counter.most_common(),
        "normalized_top_issues": normalized_issue_counter.most_common(),
        "recoverable_pattern_counts": recoverable_pattern_counter.most_common(),
        "results": results,
    }
    RESULTS_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    RESULTS_MD.write_text(render_report(output), encoding="utf-8")

    initial_rate = pct(initial_compile_candidates, len(samples))
    repair_success_rate = pct(repair_success, repair_attempts)
    final_rate = pct(final_compile_candidates, len(samples))
    print(f"total_samples={len(samples)}")
    print(f"initial_compile_rate={initial_rate}")
    print(f"repair_success_rate={repair_success_rate}")
    print(f"final_compile_rate={final_rate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
