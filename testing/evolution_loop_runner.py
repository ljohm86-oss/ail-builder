from __future__ import annotations

import json
from collections import Counter, defaultdict
import os
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("AIL_REPO_ROOT", Path(__file__).resolve().parents[1])).expanduser().resolve()
RAW_RESULTS = ROOT / "testing" / "results" / "raw_model_outputs_results.json"
REAL_RESULTS = ROOT / "testing" / "results" / "real_requirements_results.json"
BENCHMARK_RESULTS = ROOT / "benchmark" / "results" / "latest" / "benchmark_results.json"
DICT_GAP_RESULTS = ROOT / "testing" / "results" / "dictionary_gap_report.json"
SUGGESTED_TOKENS = ROOT / "testing" / "results" / "suggested_tokens.json"
ALIAS_WHITELIST = ROOT / "language" / "alias_drift_whitelist_v1.json"

RESULTS_DIR = ROOT / "testing" / "results"
PATCH_JSON = RESULTS_DIR / "patch_candidates_v3.json"
REPORT_MD = RESULTS_DIR / "evolution_loop_report.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_optional(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return load_json(path)


def priority_from_count(count: int) -> str:
    if count >= 5:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def add_candidate(
    bucket: dict[tuple[str, str, str, str], dict[str, Any]],
    *,
    candidate_type: str,
    target_layer: str,
    profile: str,
    name: str,
    reason: str,
    evidence_count: int,
    source_signals: list[str],
    recommended_action: str,
) -> None:
    key = (candidate_type, target_layer, profile, name)
    entry = bucket.setdefault(
        key,
        {
            "candidate_type": candidate_type,
            "target_layer": target_layer,
            "profile": profile,
            "name": name,
            "reason": reason,
            "evidence_count": 0,
            "source_signals": set(),
            "priority": "low",
            "recommended_action": recommended_action,
            "status": "proposed",
        },
    )
    entry["evidence_count"] = max(entry["evidence_count"], evidence_count)
    entry["source_signals"].update(source_signals)
    entry["priority"] = priority_from_count(entry["evidence_count"])


def parse_alias_sources(alias_whitelist: dict[str, Any]) -> tuple[set[str], set[str]]:
    return (
        set(alias_whitelist.get("component_aliases", {}).keys()),
        set(alias_whitelist.get("flow_aliases", {}).keys()),
    )


def collect_closed_signals(gap_report: dict[str, Any]) -> list[dict[str, Any]]:
    closed_signals: list[dict[str, Any]] = []
    for item in gap_report.get("closed_gaps", []):
        closed_signals.append(
            {
                "signal_type": "closed_gap",
                "profile": item["profile"],
                "name": item["suggested_token"],
                "evidence_count": item["evidence_count"],
                "source_signals": sorted(item.get("source_issue_types", [])),
                "reason": item["reason"],
                "sample_ids": item.get("sample_ids", []),
            }
        )
    for profile, items in gap_report.get("alias_normalized_by_profile", {}).items():
        for item in items:
            closed_signals.append(
                {
                    "signal_type": "alias_normalized",
                    "profile": profile,
                    "name": item["name"],
                    "evidence_count": item["count"],
                    "source_signals": ["alias_normalized"],
                    "reason": f"Alias/drift already normalized: {item['name']}",
                    "sample_ids": item.get("sample_ids", []),
                }
            )
    return sorted(closed_signals, key=lambda x: (-x["evidence_count"], x["profile"], x["name"]))


def collect_recoverable_patterns(raw_results: dict[str, Any]) -> list[dict[str, Any]]:
    aggregate: dict[tuple[str, str], dict[str, Any]] = {}
    for item in raw_results.get("results", []):
        for pattern in item.get("recoverable_patterns", []):
            key = (item["category"], pattern)
            entry = aggregate.setdefault(
                key,
                {
                    "profile": item["category"],
                    "name": pattern,
                    "evidence_count": 0,
                    "sample_ids": [],
                    "cohorts": set(),
                },
            )
            entry["evidence_count"] += 1
            entry["sample_ids"].append(item["id"])
            entry["cohorts"].add(item.get("sample_cohort", "unknown"))
    return sorted(
        [
            {
                "profile": item["profile"],
                "name": item["name"],
                "evidence_count": item["evidence_count"],
                "sample_ids": item["sample_ids"],
                "cohorts": sorted(item["cohorts"]),
            }
            for item in aggregate.values()
        ],
        key=lambda x: (-x["evidence_count"], x["profile"], x["name"]),
    )


def collect_active_patch_pressure(
    gap_report: dict[str, Any],
    suggestions: list[dict[str, Any]],
    alias_components: set[str],
    alias_flows: set[str],
    recoverable_patterns: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    bucket: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    recoverable_lookup = {(item["profile"], item["name"]) for item in recoverable_patterns}

    for item in suggestions:
        add_candidate(
            bucket,
            candidate_type="token_patch",
            target_layer="profile_dict",
            profile=item["profile"],
            name=item["suggested_token"],
            reason=item["reason"],
            evidence_count=item["evidence_count"],
            source_signals=list(item.get("source_signals", item.get("source_issue_types", []))) or ["dictionary_gap"],
            recommended_action="add_token",
        )

    alias_entries = gap_report.get("alias_normalized_by_profile", {})
    known_aliases = alias_components | alias_flows
    for profile, items in alias_entries.items():
        for item in items:
            alias_name = item["name"].split("->", 1)[0].strip()
            if alias_name in known_aliases:
                continue
            add_candidate(
                bucket,
                candidate_type="alias_patch",
                target_layer="whitelist",
                profile=profile,
                name=alias_name,
                reason=f"Observed alias/drift '{alias_name}' is not yet in whitelist",
                evidence_count=item["count"],
                source_signals=["alias_normalized"],
                recommended_action="add_alias_rule",
            )

    for profile, items in gap_report.get("under_specified_patterns", {}).items():
        for item in items:
            token = item["suggested_token"]
            if token == "after_sales:Support" and (profile, "recoverable_support_gap") in recoverable_lookup:
                continue
            if token in {"landing:Testimonial", "landing:Jobs", "landing:Portfolio"} and (
                profile,
                "recoverable_coverage_gap",
            ) in recoverable_lookup:
                continue
            if token in {"app:Composer", "app:SearchBar"} and (profile, "recoverable_coverage_gap") in recoverable_lookup:
                continue
            add_candidate(
                bucket,
                candidate_type="generator_rule_patch",
                target_layer="generator",
                profile=profile,
                name=token,
                reason=f"Requirement phrase '{item['phrase']}' still creates active pressure for '{token}'",
                evidence_count=item["count"],
                source_signals=["under_specified"],
                recommended_action="tighten_generator_rule",
            )

    for profile, items in gap_report.get("boundary_pressure", {}).items():
        for item in items:
            reason = item["reason"]
            if "support/contact" in reason and (profile, "recoverable_support_gap") in recoverable_lookup:
                continue
            if "auth/login/api" in reason and (profile, "recoverable_app_boundary_violation") in recoverable_lookup:
                continue
            if "testimonial/review" in reason and (profile, "recoverable_coverage_gap") in recoverable_lookup:
                continue
            target_layer = "generator"
            if "support/contact" in reason:
                target_layer = "repair"
            add_candidate(
                bucket,
                candidate_type="boundary_rule_patch",
                target_layer=target_layer,
                profile=profile,
                name=reason,
                reason=f"Boundary pressure remains active: {reason}",
                evidence_count=item["count"],
                source_signals=["boundary_pressure"],
                recommended_action="tighten_boundary_rule",
            )

    ordered: list[dict[str, Any]] = []
    for index, item in enumerate(
        sorted(
            bucket.values(),
            key=lambda x: (
                {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3),
                -x["evidence_count"],
                x["candidate_type"],
                x["profile"],
                x["name"],
            ),
        ),
        start=1,
    ):
        normalized = dict(item)
        normalized["id"] = f"PCV3-{index:03d}"
        normalized["source_signals"] = sorted(normalized["source_signals"])
        ordered.append(normalized)
    return ordered


def build_summary(
    raw_results: dict[str, Any],
    real_results: dict[str, Any],
    benchmark_results: dict[str, Any],
    gap_report: dict[str, Any],
    suggestions: list[dict[str, Any]],
    closed_signals: list[dict[str, Any]],
    recoverable_patterns: list[dict[str, Any]],
    active_patch_pressure: list[dict[str, Any]],
) -> dict[str, Any]:
    by_type = Counter(item["candidate_type"] for item in active_patch_pressure)
    by_priority = Counter(item["priority"] for item in active_patch_pressure)
    return {
        "raw_samples": raw_results["summary"]["total_samples"],
        "real_requirements": real_results["summary"]["total_requirements"],
        "benchmark_release_decision": benchmark_results.get("release_decision", "unknown"),
        "active_suggested_tokens": len(suggestions),
        "closed_signals_count": len(closed_signals),
        "recoverable_patterns_count": len(recoverable_patterns),
        "active_patch_pressure_count": len(active_patch_pressure),
        "candidate_types": dict(by_type),
        "priority_breakdown": dict(by_priority),
        "cohort_breakdown": raw_results.get("cohort_breakdown", {}),
    }


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Evolution Loop Report",
        "",
        "## Summary",
        f"- raw_samples: {payload['summary']['raw_samples']}",
        f"- real_requirements: {payload['summary']['real_requirements']}",
        f"- benchmark_release_decision: {payload['summary']['benchmark_release_decision']}",
        f"- active_suggested_tokens: {payload['summary']['active_suggested_tokens']}",
        f"- closed_signals_count: {payload['summary']['closed_signals_count']}",
        f"- recoverable_patterns_count: {payload['summary']['recoverable_patterns_count']}",
        f"- active_patch_pressure_count: {payload['summary']['active_patch_pressure_count']}",
        "",
        "## By Cohort",
    ]
    for cohort, stats in payload["summary"]["cohort_breakdown"].items():
        lines.append(
            f"- {cohort}: total={stats['total']}, initial_compile_rate={stats['initial_compile_rate']}, final_compile_rate={stats['final_compile_rate']}"
        )

    lines.extend(["", "## Closed Signals"])
    if payload["closed_signals"]:
        for item in payload["closed_signals"]:
            lines.extend(
                [
                    f"### {item['name']}",
                    f"- profile: {item['profile']}",
                    f"- signal_type: {item['signal_type']}",
                    f"- evidence_count: {item['evidence_count']}",
                    f"- reason: {item['reason']}",
                    "",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Recoverable Patterns"])
    if payload["recoverable_patterns"]:
        for item in payload["recoverable_patterns"]:
            lines.extend(
                [
                    f"### {item['name']}",
                    f"- profile: {item['profile']}",
                    f"- evidence_count: {item['evidence_count']}",
                    f"- cohorts: {', '.join(item['cohorts'])}",
                    f"- sample_ids: {', '.join(item['sample_ids']) if item['sample_ids'] else 'none'}",
                    "",
                ]
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Active Patch Pressure"])
    if payload["active_patch_pressure"]:
        for item in payload["active_patch_pressure"]:
            lines.extend(
                [
                    f"### {item['id']} · {item['name']}",
                    f"- candidate_type: {item['candidate_type']}",
                    f"- profile: {item['profile']}",
                    f"- target_layer: {item['target_layer']}",
                    f"- priority: {item['priority']}",
                    f"- evidence_count: {item['evidence_count']}",
                    f"- source_signals: {', '.join(item['source_signals']) if item['source_signals'] else 'none'}",
                    f"- recommended_action: {item['recommended_action']}",
                    f"- reason: {item['reason']}",
                    "",
                ]
            )
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_results = load_json(RAW_RESULTS)
    real_results = load_json(REAL_RESULTS)
    benchmark_results = load_json_optional(BENCHMARK_RESULTS, {"release_decision": "unknown"})
    gap_report = load_json(DICT_GAP_RESULTS)
    suggestions = load_json(SUGGESTED_TOKENS)
    alias_whitelist = load_json(ALIAS_WHITELIST)

    component_aliases, flow_aliases = parse_alias_sources(alias_whitelist)
    closed_signals = collect_closed_signals(gap_report)
    recoverable_patterns = collect_recoverable_patterns(raw_results)
    active_patch_pressure = collect_active_patch_pressure(
        gap_report, suggestions, component_aliases, flow_aliases, recoverable_patterns
    )
    summary = build_summary(
        raw_results,
        real_results,
        benchmark_results,
        gap_report,
        suggestions,
        closed_signals,
        recoverable_patterns,
        active_patch_pressure,
    )

    payload = {
        "version": "v3",
        "inputs": {
            "raw_results": str(RAW_RESULTS),
            "real_requirements_results": str(REAL_RESULTS),
            "benchmark_results": str(BENCHMARK_RESULTS),
            "dictionary_gap_report": str(DICT_GAP_RESULTS),
            "suggested_tokens": str(SUGGESTED_TOKENS),
            "alias_whitelist": str(ALIAS_WHITELIST),
        },
        "summary": summary,
        "closed_signals": closed_signals,
        "recoverable_patterns": recoverable_patterns,
        "active_patch_pressure": active_patch_pressure,
        "patch_candidates": active_patch_pressure,
    }

    PATCH_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_report(payload), encoding="utf-8")

    print(f"total_candidates={len(active_patch_pressure)}")
    print(f"benchmark_release_decision={summary['benchmark_release_decision']}")
    print(f"active_suggested_tokens={summary['active_suggested_tokens']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
