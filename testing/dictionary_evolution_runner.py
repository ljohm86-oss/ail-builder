from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("AIL_REPO_ROOT", Path(__file__).resolve().parents[1])).expanduser().resolve()
RAW_RESULTS = ROOT / "testing" / "results" / "raw_model_outputs_results.json"
REAL_RESULTS = ROOT / "testing" / "results" / "real_requirements_results.json"
BENCHMARK_RESULTS = ROOT / "benchmark" / "results" / "latest" / "benchmark_results.json"
RESULTS_DIR = ROOT / "testing" / "results"
GAP_JSON = RESULTS_DIR / "dictionary_gap_report.json"
TOKENS_JSON = RESULTS_DIR / "suggested_tokens.json"
GAP_MD = RESULTS_DIR / "dictionary_gap_report.md"
ALIAS_WHITELIST_PATH = ROOT / "language" / "alias_drift_whitelist_v1.json"

INSTALLED_TOKENS = {
    ("landing", "ui", "landing:Header"),
    ("landing", "ui", "landing:Hero"),
    ("landing", "ui", "landing:FeatureGrid"),
    ("landing", "ui", "landing:Stats"),
    ("landing", "ui", "landing:LogoCloud"),
    ("landing", "ui", "landing:Team"),
    ("landing", "ui", "landing:Testimonial"),
    ("landing", "ui", "landing:Jobs"),
    ("landing", "ui", "landing:Portfolio"),
    ("landing", "ui", "landing:FAQ"),
    ("landing", "ui", "landing:Pricing"),
    ("landing", "ui", "landing:CTA"),
    ("landing", "ui", "landing:Contact"),
    ("landing", "ui", "landing:Footer"),
    ("landing", "flow", "CONTACT_SUBMIT"),
    ("landing", "flow", "LEAD_CAPTURE"),
    ("ecom_min", "ui", "ecom:Header"),
    ("ecom_min", "ui", "ecom:Banner"),
    ("ecom_min", "ui", "ecom:CategoryNav"),
    ("ecom_min", "ui", "ecom:ProductGrid"),
    ("ecom_min", "ui", "ecom:ProductDetail"),
    ("ecom_min", "ui", "ecom:CartPanel"),
    ("ecom_min", "ui", "ecom:CheckoutPanel"),
    ("ecom_min", "ui", "ecom:ShopHeader"),
    ("ecom_min", "ui", "ecom:SearchResultGrid"),
    ("ecom_min", "flow", "ADD_TO_CART"),
    ("ecom_min", "flow", "CHECKOUT_SUBMIT"),
    ("ecom_min", "flow", "ORDER_PLACE"),
    ("after_sales", "ui", "after_sales:Entry"),
    ("after_sales", "ui", "after_sales:Refund"),
    ("after_sales", "ui", "after_sales:Exchange"),
    ("after_sales", "ui", "after_sales:Complaint"),
    ("after_sales", "ui", "after_sales:Support"),
    ("after_sales", "flow", "REFUND_FLOW"),
    ("after_sales", "flow", "EXCHANGE_FLOW"),
    ("after_sales", "flow", "COMPLAINT_DEESCALATE"),
    ("app_min", "ui", "app:TopBar"),
    ("app_min", "ui", "app:BottomTab"),
    ("app_min", "ui", "app:List"),
    ("app_min", "ui", "app:Card"),
    ("app_min", "ui", "app:ChatWindow"),
    ("app_min", "ui", "app:Composer"),
    ("app_min", "ui", "app:SearchBar"),
}


UNDER_SPECIFIED_CANDIDATES = {
    "landing": {
        "客户评价": {"suggested_token": "landing:Testimonial", "token_type": "ui"},
        "用户评价": {"suggested_token": "landing:Testimonial", "token_type": "ui"},
        "项目作品": {"suggested_token": "landing:Portfolio", "token_type": "ui"},
        "案例展示": {"suggested_token": "landing:Portfolio", "token_type": "ui"},
        "职位展示": {"suggested_token": "landing:Jobs", "token_type": "ui"},
        "品牌故事": {"suggested_token": "landing:Timeline", "token_type": "ui"},
    },
    "ecom_min": {
        "商品评价": {"suggested_token": "ecom:Reviews", "token_type": "ui"},
        "过滤": {"suggested_token": "ecom:FilterBar", "token_type": "ui"},
        "筛选": {"suggested_token": "ecom:FilterBar", "token_type": "ui"},
        "排序": {"suggested_token": "ecom:SortBar", "token_type": "ui"},
    },
    "after_sales": {
        "退款进度": {"suggested_token": "after_sales:Progress", "token_type": "ui"},
        "联系客服": {"suggested_token": "after_sales:Support", "token_type": "ui"},
        "客服": {"suggested_token": "after_sales:Support", "token_type": "ui"},
    },
    "app_min": {
        "搜索联系人": {"suggested_token": "app:SearchBar", "token_type": "ui"},
        "新增任务": {"suggested_token": "app:Composer", "token_type": "ui"},
        "编辑笔记": {"suggested_token": "app:Composer", "token_type": "ui"},
    },
}

BOUNDARY_RULES = {
    "landing": [
        ("客户评价", "landing lacks testimonial/review block"),
        ("用户评价", "landing lacks testimonial/review block"),
        ("项目作品", "landing lacks portfolio/showcase block"),
        ("案例展示", "landing lacks portfolio/showcase block"),
        ("职位展示", "landing lacks jobs/careers block"),
    ],
    "ecom_min": [
        ("商品评价", "ecom_min lacks reviews block"),
        ("过滤", "ecom_min lacks filter block"),
        ("筛选", "ecom_min lacks filter block"),
        ("排序", "ecom_min lacks sort block"),
    ],
    "after_sales": [
        ("退款进度", "after_sales lacks progress tracking block"),
        ("联系客服", "after_sales lacks support/contact block"),
        ("客服", "after_sales lacks support/contact block"),
    ],
    "app_min": [
        ("登录", "app_min is pushed toward auth/login boundary"),
        ("auth", "app_min is pushed toward auth/login boundary"),
        ("api", "app_min is pushed toward backend/api boundary"),
    ],
}

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_alias_maps() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    payload = load_json(ALIAS_WHITELIST_PATH)
    component_aliases = payload.get("component_aliases", {})
    flow_aliases = payload.get("flow_aliases", {})
    component_map = {
        alias: {
            "profile": ("landing" if alias.startswith("landing:") else "ecom_min" if alias.startswith("ecom:") else "unknown"),
            "token_type": "ui",
            "suggested_token": target,
        }
        for alias, target in component_aliases.items()
    }
    flow_profile_map = {
        "CONTACT_SUBMIT": "landing",
        "ADD_TO_CART": "ecom_min",
        "COMPLAINT_DEESCALATE": "after_sales",
    }
    flow_map = {
        alias: {
            "profile": flow_profile_map.get(target, "unknown"),
            "token_type": "flow",
            "suggested_token": target,
        }
        for alias, target in flow_aliases.items()
    }
    return component_map, flow_map


UNKNOWN_COMPONENT_TOKEN_MAP, UNKNOWN_FLOW_TOKEN_MAP = load_alias_maps()


def priority_from_count(count: int) -> str:
    if count >= 4:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def collect_unknowns(results: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    by_profile: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for item in results:
        issue_set = set(item.get("issues", []))
        if {"multiple_profiles", "multi_result_wrapper"} & issue_set:
            continue
        profile = item.get("category") or item.get("final_profile") or "unknown"
        diagnosis = item.get("pre_diagnosis", {})
        tokens = diagnosis.get(field, [])
        for token in tokens:
            bucket = by_profile[profile].setdefault(token, {"count": 0, "sample_ids": []})
            bucket["count"] += 1
            sample_id = item.get("id") or item.get("requirement_id") or item.get("task_id")
            if sample_id not in bucket["sample_ids"]:
                bucket["sample_ids"].append(sample_id)
    return by_profile


def collect_aliases(results: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    by_profile: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for item in results:
        profile = item.get("category") or item.get("final_profile") or "unknown"
        diagnosis = item.get("pre_diagnosis", {})
        aliases = diagnosis.get(field, [])
        for alias in aliases:
            bucket = by_profile[profile].setdefault(alias, {"count": 0, "sample_ids": []})
            bucket["count"] += 1
            sample_id = item.get("id") or item.get("requirement_id") or item.get("task_id")
            if sample_id not in bucket["sample_ids"]:
                bucket["sample_ids"].append(sample_id)
    return by_profile


def extract_under_specified_patterns(
    raw_results: list[dict[str, Any]],
    real_results: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    patterns: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for item in raw_results:
        if "under_specified" not in item.get("issues", []):
            continue
        category = item["category"]
        requirement = item["requirement"]
        sample_id = item.get("id") or item.get("requirement_id")
        for phrase, meta in UNDER_SPECIFIED_CANDIDATES.get(category, {}).items():
            if phrase in requirement:
                entry = patterns[category].setdefault(
                    phrase,
                    {
                        "count": 0,
                        "sample_ids": [],
                        "suggested_token": meta["suggested_token"],
                        "token_type": meta["token_type"],
                    },
                )
                entry["count"] += 1
                if sample_id not in entry["sample_ids"]:
                    entry["sample_ids"].append(sample_id)
                entry["raw_count"] = entry.get("raw_count", 0) + 1
                entry.setdefault("real_requirement_ids", [])
    for item in real_results:
        category = item["category"]
        requirement = item["requirement"]
        requirement_id = item["requirement_id"]
        for phrase, meta in UNDER_SPECIFIED_CANDIDATES.get(category, {}).items():
            if phrase in requirement:
                entry = patterns[category].setdefault(
                    phrase,
                    {
                        "count": 0,
                        "sample_ids": [],
                        "suggested_token": meta["suggested_token"],
                        "token_type": meta["token_type"],
                        "raw_count": 0,
                        "real_count": 0,
                        "real_requirement_ids": [],
                    },
                )
                entry["count"] += 1
                entry["real_count"] = entry.get("real_count", 0) + 1
                if requirement_id not in entry["real_requirement_ids"]:
                    entry["real_requirement_ids"].append(requirement_id)
    return patterns


def collect_boundary_pressure(raw_results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    pressure: dict[str, dict[str, Any]] = defaultdict(dict)
    for item in raw_results:
        category = item["category"]
        requirement = item["requirement"]
        sample_id = item["id"]
        if "app_min_boundary_exceeded" in item.get("issues", []):
            entry = pressure[category].setdefault(
                "app_min boundary auth/login/api pressure",
                {"count": 0, "sample_ids": []},
            )
            entry["count"] += 1
            if sample_id not in entry["sample_ids"]:
                entry["sample_ids"].append(sample_id)
        for phrase, description in BOUNDARY_RULES.get(category, []):
            if phrase in requirement:
                entry = pressure[category].setdefault(description, {"count": 0, "sample_ids": []})
                entry["count"] += 1
                if sample_id not in entry["sample_ids"]:
                    entry["sample_ids"].append(sample_id)
    return pressure


def build_suggested_tokens(
    unknown_components: dict[str, dict[str, Any]],
    unknown_flows: dict[str, dict[str, Any]],
    under_patterns: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    suggestions: dict[tuple[str, str, str], dict[str, Any]] = {}

    for profile, tokens in unknown_components.items():
        for token, meta in tokens.items():
            mapped = UNKNOWN_COMPONENT_TOKEN_MAP.get(token)
            suggested = mapped["suggested_token"] if mapped else token
            key = (profile, "ui", suggested)
            entry = suggestions.setdefault(
                key,
                {
                    "profile": profile,
                    "token_type": "ui",
                    "suggested_token": suggested,
                    "reason": f"Unknown component '{token}' appears in raw outputs",
                    "evidence_count": 0,
                    "source_issue_types": set(),
                    "priority": "low",
                    "sample_ids": [],
                },
            )
            entry["evidence_count"] += meta["count"]
            entry["source_issue_types"].update(["unknown_component"])
            entry["sample_ids"].extend(meta["sample_ids"])

    for profile, flows in unknown_flows.items():
        for flow, meta in flows.items():
            mapped = UNKNOWN_FLOW_TOKEN_MAP.get(flow)
            suggested = mapped["suggested_token"] if mapped else flow
            key = (profile, "flow", suggested)
            entry = suggestions.setdefault(
                key,
                {
                    "profile": profile,
                    "token_type": "flow",
                    "suggested_token": suggested,
                    "reason": f"Unknown flow '{flow}' appears in raw outputs",
                    "evidence_count": 0,
                    "source_issue_types": set(),
                    "priority": "low",
                    "sample_ids": [],
                },
            )
            entry["evidence_count"] += meta["count"]
            entry["source_issue_types"].update(["unknown_flow"])
            entry["sample_ids"].extend(meta["sample_ids"])

    for profile, phrases in under_patterns.items():
        for phrase, meta in phrases.items():
            key = (profile, meta["token_type"], meta["suggested_token"])
            entry = suggestions.setdefault(
                key,
                {
                    "profile": profile,
                    "token_type": meta["token_type"],
                    "suggested_token": meta["suggested_token"],
                    "reason": f"High frequency requirement phrase '{phrase}' appears in under_specified samples",
                    "evidence_count": 0,
                    "source_issue_types": set(),
                    "priority": "low",
                    "sample_ids": [],
                },
            )
            entry["evidence_count"] += meta["count"]
            entry["source_issue_types"].update(["under_specified"])
            entry["sample_ids"].extend(meta["sample_ids"])
            entry["sample_ids"].extend(meta.get("real_requirement_ids", []))

    normalized: list[dict[str, Any]] = []
    for entry in suggestions.values():
        entry["sample_ids"] = sorted(set(entry["sample_ids"]))
        entry["source_issue_types"] = sorted(entry["source_issue_types"])
        entry["priority"] = priority_from_count(entry["evidence_count"])
        normalized.append(entry)
    normalized.sort(key=lambda item: (-item["evidence_count"], item["profile"], item["token_type"], item["suggested_token"]))
    return normalized


def split_installed_suggestions(suggestions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    active: list[dict[str, Any]] = []
    closed: list[dict[str, Any]] = []
    for item in suggestions:
        key = (item["profile"], item["token_type"], item["suggested_token"])
        if key in INSTALLED_TOKENS:
            closed.append(item)
        else:
            active.append(item)
    return active, closed


def normalize_gap_dict(raw: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for profile, tokens in raw.items():
        items = []
        for token, meta in sorted(tokens.items(), key=lambda pair: (-pair[1]["count"], pair[0])):
            items.append({"name": token, "count": meta["count"], "sample_ids": sorted(meta["sample_ids"])})
        output[profile] = items
    return output


def normalize_pattern_dict(raw: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for profile, phrases in raw.items():
        items = []
        for phrase, meta in sorted(phrases.items(), key=lambda pair: (-pair[1]["count"], pair[0])):
            items.append(
                {
                    "phrase": phrase,
                    "count": meta["count"],
                    "sample_ids": sorted(meta["sample_ids"]),
                    "raw_count": meta.get("raw_count", 0),
                    "real_count": meta.get("real_count", 0),
                    "real_requirement_ids": sorted(meta.get("real_requirement_ids", [])),
                    "suggested_token": meta["suggested_token"],
                    "token_type": meta["token_type"],
                }
            )
        output[profile] = items
    return output


def normalize_pressure_dict(raw: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for profile, reasons in raw.items():
        items = []
        for reason, meta in sorted(reasons.items(), key=lambda pair: (-pair[1]["count"], pair[0])):
            items.append({"reason": reason, "count": meta["count"], "sample_ids": sorted(meta["sample_ids"])})
        output[profile] = items
    return output


def render_markdown(report: dict[str, Any], suggestions: list[dict[str, Any]], closed_suggestions: list[dict[str, Any]]) -> str:
    lines = [
        "# Dictionary Gap Report",
        "",
        "## Inputs",
        f"- raw_results: `{RAW_RESULTS}`",
        f"- real_requirements_results: `{REAL_RESULTS}`",
        f"- benchmark_results: `{BENCHMARK_RESULTS}`",
        "",
        "## Summary",
        f"- raw_samples: {report['summary']['raw_samples']}",
        f"- real_requirements: {report['summary']['real_requirements']}",
        f"- benchmark_release_decision: {report['summary']['benchmark_release_decision']}",
        f"- active_suggested_tokens: {report['summary']['active_suggested_tokens']}",
        f"- closed_gaps_detected: {report['summary']['closed_gaps_detected']}",
        "",
        "## Unknown Components",
    ]
    for profile, items in report["unknown_components_by_profile"].items():
        lines.append(f"### {profile}")
        if not items:
            lines.append("- none")
            continue
        for item in items:
            lines.append(f"- `{item['name']}`: {item['count']} ({', '.join(item['sample_ids'])})")
    lines.extend(["", "## Unknown Flows"])
    for profile, items in report["unknown_flows_by_profile"].items():
        lines.append(f"### {profile}")
        if not items:
            lines.append("- none")
            continue
        for item in items:
            lines.append(f"- `{item['name']}`: {item['count']} ({', '.join(item['sample_ids'])})")
    lines.extend(["", "## Alias / Drift Normalized"])
    for profile, items in report["alias_normalized_by_profile"].items():
        lines.append(f"### {profile}")
        if not items:
            lines.append("- none")
            continue
        for item in items:
            lines.append(f"- `{item['name']}`: {item['count']} ({', '.join(item['sample_ids'])})")
    lines.extend(["", "## Under-specified Patterns"])
    for profile, items in report["under_specified_patterns"].items():
        lines.append(f"### {profile}")
        if not items:
            lines.append("- none")
            continue
        for item in items:
            evidence_parts = []
            if item["sample_ids"]:
                evidence_parts.append(f"raw={','.join(item['sample_ids'])}")
            if item.get("real_requirement_ids"):
                evidence_parts.append(f"real={','.join(item['real_requirement_ids'])}")
            lines.append(
                f"- `{item['phrase']}` -> `{item['suggested_token']}`: {item['count']} ({'; '.join(evidence_parts) if evidence_parts else 'none'})"
            )
    lines.extend(["", "## Boundary Pressure"])
    for profile, items in report["boundary_pressure"].items():
        lines.append(f"### {profile}")
        if not items:
            lines.append("- none")
            continue
        for item in items:
            lines.append(f"- {item['reason']}: {item['count']} ({', '.join(item['sample_ids'])})")
    lines.extend(["", "## Closed Gaps"])
    if not closed_suggestions:
        lines.append("- none")
    else:
        for item in closed_suggestions:
            lines.append(
                f"- `{item['suggested_token']}` [{item['profile']}/{item['token_type']}] "
                f"evidence={item['evidence_count']} issues={','.join(item['source_issue_types'])}"
            )
    lines.extend(["", "## Suggested Tokens"])
    if not suggestions:
        lines.append("- none")
    else:
        for item in suggestions:
            lines.append(
                f"- `{item['suggested_token']}` [{item['profile']}/{item['token_type']}] "
                f"priority={item['priority']} evidence={item['evidence_count']} "
                f"issues={','.join(item['source_issue_types'])}"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    raw_payload = load_json(RAW_RESULTS)
    real_payload = load_json(REAL_RESULTS)
    benchmark_payload = load_json(BENCHMARK_RESULTS) if BENCHMARK_RESULTS.exists() else {}

    raw_results = raw_payload["results"]
    real_results = real_payload["results"]

    unknown_components = normalize_gap_dict(collect_unknowns(raw_results, "unknown_components"))
    unknown_flows = normalize_gap_dict(collect_unknowns(raw_results, "unknown_flows"))
    alias_components = normalize_gap_dict(collect_aliases(raw_results, "alias_components"))
    alias_flows = normalize_gap_dict(collect_aliases(raw_results, "alias_flows"))
    raw_under_patterns = extract_under_specified_patterns(raw_results, real_results)
    under_patterns = normalize_pattern_dict(raw_under_patterns)
    boundary_pressure = normalize_pressure_dict(collect_boundary_pressure(raw_results))
    all_suggestions = build_suggested_tokens(
        collect_unknowns(raw_results, "unknown_components"),
        collect_unknowns(raw_results, "unknown_flows"),
        raw_under_patterns,
    )
    suggestions, closed_suggestions = split_installed_suggestions(all_suggestions)

    report = {
        "summary": {
            "raw_samples": raw_payload["summary"]["total_samples"],
            "real_requirements": real_payload["summary"]["total_requirements"],
            "benchmark_release_decision": benchmark_payload.get("release_decision", "unknown"),
            "active_suggested_tokens": len(suggestions),
            "closed_gaps_detected": len(closed_suggestions),
            "alias_normalized_entries": sum(len(items) for items in alias_components.values()) + sum(len(items) for items in alias_flows.values()),
        },
        "unknown_components_by_profile": unknown_components,
        "unknown_flows_by_profile": unknown_flows,
        "alias_normalized_by_profile": {
            profile: sorted(alias_components.get(profile, []) + alias_flows.get(profile, []), key=lambda item: (-item["count"], item["name"]))
            for profile in sorted(set(alias_components) | set(alias_flows) | {"landing", "ecom_min", "after_sales", "app_min"})
        },
        "under_specified_patterns": under_patterns,
        "boundary_pressure": boundary_pressure,
        "closed_gaps": closed_suggestions,
    }

    GAP_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    TOKENS_JSON.write_text(json.dumps(suggestions, ensure_ascii=False, indent=2), encoding="utf-8")
    GAP_MD.write_text(render_markdown(report, suggestions, closed_suggestions), encoding="utf-8")

    print(f"unknown_component_profiles={len([p for p, items in unknown_components.items() if items])}")
    print(f"unknown_flow_profiles={len([p for p, items in unknown_flows.items() if items])}")
    print(f"suggested_tokens={len(suggestions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
