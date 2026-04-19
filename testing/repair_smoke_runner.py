from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("AIL_REPO_ROOT", Path(__file__).resolve().parents[1])).expanduser().resolve()
CASES_PATH = ROOT / "testing" / "repair_smoke_cases_v1.md"
RESULTS_DIR = ROOT / "testing" / "results"
RESULTS_PATH = RESULTS_DIR / "repair_smoke_results.json"
REPORT_PATH = RESULTS_DIR / "repair_smoke_report.md"
ALIAS_WHITELIST_PATH = ROOT / "language" / "alias_drift_whitelist_v1.json"

SUPPORTED = {
    "landing": {
        "ui": {
            "landing:Header",
            "landing:Hero",
            "landing:FeatureGrid",
            "landing:Stats",
            "landing:LogoCloud",
            "landing:Team",
            "landing:Testimonial",
            "landing:Jobs",
            "landing:Portfolio",
            "landing:FAQ",
            "landing:Pricing",
            "landing:CTA",
            "landing:Contact",
            "landing:Footer",
        },
        "flows": {"CONTACT_SUBMIT", "LEAD_CAPTURE"},
    },
    "ecom_min": {
        "ui": {
            "ecom:Header",
            "ecom:Banner",
            "ecom:CategoryNav",
            "ecom:ProductGrid",
            "ecom:ProductDetail",
            "ecom:CartPanel",
            "ecom:CheckoutPanel",
            "ecom:ShopHeader",
            "ecom:SearchResultGrid",
        },
        "flows": {"ADD_TO_CART", "CHECKOUT_SUBMIT", "ORDER_PLACE"},
    },
    "after_sales": {
        "ui": {
            "after_sales:Entry",
            "after_sales:Refund",
            "after_sales:Exchange",
            "after_sales:Complaint",
            "after_sales:Support",
        },
        "flows": {"REFUND_FLOW", "EXCHANGE_FLOW", "COMPLAINT_DEESCALATE"},
    },
    "app_min": {
        "ui": {
            "app:TopBar",
            "app:BottomTab",
            "app:List",
            "app:Card",
            "app:ChatWindow",
            "app:Composer",
            "app:SearchBar",
        },
        "flows": set(),
    },
}

PROFILE_KEYWORDS = {
    "landing": ["官网", "landing", "saas", "营销", "落地页", "联系我们", "faq", "团队", "功能介绍"],
    "ecom_min": ["商城", "商品", "购物车", "结算", "店铺", "电商", "搜索结果"],
    "after_sales": ["售后", "退款", "换货", "投诉", "升级处理"],
    "app_min": ["app", "聊天", "联系人", "顶部栏", "底部 tab", "单页"],
}

AIL_LINE_RE = re.compile(r"^(#PROFILE\[.*\]|>DB_TABLE\[.*\]|@API\[.*\]|@PAGE\[.*\]|#UI\[.*\]|#FLOW\[.*\])$")
PROFILE_RE = re.compile(r"^#PROFILE\[([^\]]+)\]$")
PAGE_RE = re.compile(r"^@PAGE\[([^,]+),([^\]]+)\]$")
UI_RE = re.compile(r"^#UI\[([^\]]+)\]")
FLOW_RE = re.compile(r"^#FLOW\[([^\]]+)\]")
UNSUPPORTED_RE = re.compile(r"(<[A-Za-z!/]|</|import\s|export\s|const\s+\w+\s*=|<template>|<script|<style)")

def load_alias_whitelist() -> dict[str, dict[str, str]]:
    payload = json.loads(ALIAS_WHITELIST_PATH.read_text(encoding="utf-8"))
    return {
        "component_aliases": payload.get("component_aliases", {}),
        "flow_aliases": payload.get("flow_aliases", {}),
    }


ALIASES = load_alias_whitelist()
UI_REPLACEMENTS = {
    **ALIASES["component_aliases"],
}

FLOW_REPLACEMENTS = {
    **ALIASES["flow_aliases"],
    "EMAIL_CAPTURE": "LEAD_CAPTURE",
    "REFUND_REQUEST": "REFUND_FLOW",
}


def load_cases() -> list[dict[str, str]]:
    text = CASES_PATH.read_text(encoding="utf-8")
    chunks = [chunk.strip() for chunk in re.split(r"^## Case ", text, flags=re.MULTILINE) if chunk.strip()]
    cases: list[dict[str, str]] = []
    for chunk in chunks:
        header, *rest = chunk.splitlines()
        if not header.startswith("R"):
            continue
        body = "\n".join(rest)
        case_id = re.search(r"Case ID:\s*(.+)", body)
        requirement = re.search(r"Requirement:\n(.*?)\nBroken AIL:", body, re.DOTALL)
        broken = re.search(r"Broken AIL:\n```ail\n(.*?)\n```", body, re.DOTALL)
        goal = re.search(r"Expected Repair Goal:\n(.*?)\nExpected Post-Repair Diagnosis:", body, re.DOTALL)
        expected = re.search(r"Expected Post-Repair Diagnosis:\n(.*)$", body, re.DOTALL)
        if not (case_id and requirement and broken and goal and expected):
            raise ValueError(f"Invalid case block: {header}")
        cases.append(
            {
                "case_id": case_id.group(1).strip(),
                "requirement": requirement.group(1).strip(),
                "broken_ail": broken.group(1).strip(),
                "expected_goal": goal.group(1).strip(),
                "expected_post": expected.group(1).strip(),
            }
        )
    return cases


def detect_expected_profile(requirement: str) -> str:
    lower = requirement.lower()
    scores = {}
    for profile, keywords in PROFILE_KEYWORDS.items():
        scores[profile] = sum(1 for keyword in keywords if keyword.lower() in lower)
    return max(scores.items(), key=lambda item: item[1])[0]


def split_candidates(text: str) -> list[str]:
    lines = text.splitlines()
    candidates: list[list[str]] = []
    current: list[str] = []
    saw_wrapper = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^\*\*Task\s+\d+\*\*$", stripped) or re.match(r"^Task\s+\d+$", stripped):
            saw_wrapper = True
            if current:
                candidates.append(current)
                current = []
            continue
        if stripped == "---":
            saw_wrapper = True
            if current:
                candidates.append(current)
                current = []
            continue
        current.append(line)
    if current:
        candidates.append(current)
    if not saw_wrapper:
        return [text.strip()]
    return ["\n".join(block).strip() for block in candidates if "\n".join(block).strip()]


def normalize_lines(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lines.append(line)
    return lines


def parse_program(text: str) -> dict[str, Any]:
    lines = normalize_lines(text)
    profiles: list[str] = []
    pages: list[dict[str, Any]] = []
    db_lines: list[str] = []
    api_lines: list[str] = []
    flows: list[str] = []
    unsupported_constructs: list[str] = []
    current_page: dict[str, Any] | None = None

    for line in lines:
        if UNSUPPORTED_RE.search(line):
            unsupported_constructs.append(line)
            continue
        match = PROFILE_RE.match(line)
        if match:
            profiles.append(match.group(1).strip())
            current_page = None
            continue
        if line.startswith(">DB_TABLE["):
            db_lines.append(line)
            current_page = None
            continue
        if line.startswith("@API["):
            api_lines.append(line)
            current_page = None
            continue
        match = PAGE_RE.match(line)
        if match:
            current_page = {"name": match.group(1).strip(), "path": match.group(2).strip(), "ui": []}
            pages.append(current_page)
            continue
        match = UI_RE.match(line)
        if match:
            token = match.group(1).strip()
            if current_page is not None:
                current_page["ui"].append(token)
            else:
                unsupported_constructs.append(f"orphan_ui:{token}")
            continue
        match = FLOW_RE.match(line)
        if match:
            flows.append(match.group(1).strip())
            continue
        if not AIL_LINE_RE.match(line):
            unsupported_constructs.append(line)

    return {
        "lines": lines,
        "profiles": profiles,
        "pages": pages,
        "db_lines": db_lines,
        "api_lines": api_lines,
        "flows": flows,
        "unsupported_constructs": unsupported_constructs,
    }


def diagnose(requirement: str, ail_text: str) -> dict[str, Any]:
    expected_profile = detect_expected_profile(requirement)
    candidates = split_candidates(ail_text)
    parsed = parse_program(ail_text)
    detected_profile = parsed["profiles"][0] if len(parsed["profiles"]) == 1 else (parsed["profiles"][0] if parsed["profiles"] else "none")
    multiple_profiles = len(parsed["profiles"]) > 1 or len(candidates) > 1
    profile_match = detected_profile == expected_profile and not multiple_profiles

    allowed_ui = SUPPORTED.get(detected_profile, {}).get("ui", set())
    allowed_flows = SUPPORTED.get(detected_profile, {}).get("flows", set())
    unknown_components = []
    alias_components = []
    for page in parsed["pages"]:
        for token in page["ui"]:
            normalized = UI_REPLACEMENTS.get(token, token)
            if normalized != token:
                alias_components.append(f"{token}->{normalized}")
            if normalized not in allowed_ui:
                unknown_components.append(token)
    alias_flows = []
    unknown_flows = []
    for flow in parsed["flows"]:
        normalized = FLOW_REPLACEMENTS.get(flow, flow)
        if normalized != flow:
            alias_flows.append(f"{flow}->{normalized}")
        if normalized not in allowed_flows:
            unknown_flows.append(flow)

    structure_valid = True
    state = "start"
    saw_page = False
    for line in parsed["lines"]:
        if line.startswith("#PROFILE["):
            if state != "start":
                structure_valid = False
                break
            state = "profile"
            continue
        if line.startswith(">DB_TABLE["):
            if state not in {"profile", "db"}:
                structure_valid = False
                break
            state = "db"
            continue
        if line.startswith("@API["):
            if state not in {"profile", "db", "api"}:
                structure_valid = False
                break
            state = "api"
            continue
        if line.startswith("@PAGE["):
            if state not in {"profile", "db", "api", "page", "ui"}:
                structure_valid = False
                break
            state = "page"
            saw_page = True
            continue
        if line.startswith("#UI["):
            if state not in {"page", "ui"}:
                structure_valid = False
                break
            state = "ui"
            continue
        if line.startswith("#FLOW["):
            if not saw_page or state not in {"page", "ui", "flow"}:
                structure_valid = False
                break
            state = "flow"
            continue

    boundary_exceeded = False
    boundary_reason = ""
    if detected_profile == "app_min":
        auth_markers = [
            "@API[AUTH",
            "@API[",
            ">DB_AUTH",
            ">DB_TABLE[",
            "*AUTH",
            "/login",
            "/register",
            "@PAGE[Login",
            "@PAGE[Settings",
            "@PAGE[Register",
            "token",
            "backend",
            "用户系统",
        ]
        for line in parsed["lines"]:
            if any(marker in line for marker in auth_markers):
                boundary_exceeded = True
                boundary_reason = "app_min contains auth or multi-page backend-like constructs"
                break
        if not boundary_exceeded and len(parsed["pages"]) > 1:
            boundary_exceeded = True
            boundary_reason = "app_min expanded into multi-page structure"

    if multiple_profiles and not boundary_reason:
        boundary_reason = "multiple profile or multi-result wrapper detected"
    if (alias_components or alias_flows) and not boundary_reason:
        boundary_reason = "alias/drift candidate present"
    if unknown_components and not boundary_reason:
        boundary_reason = "unknown UI token present"
    if unknown_flows and not boundary_reason:
        boundary_reason = "unknown flow present"

    compile_recommended = (
        len(parsed["profiles"]) == 1
        and not multiple_profiles
        and structure_valid
        and not alias_components
        and not alias_flows
        and not unknown_components
        and not unknown_flows
        and not parsed["unsupported_constructs"]
        and not boundary_exceeded
    )
    valid = compile_recommended

    return {
        "valid": "yes" if valid else "no",
        "compile_recommended": "yes" if compile_recommended else "no",
        "confidence": "high" if expected_profile != "landing" or detected_profile != "none" else "medium",
        "detected_profile": detected_profile,
        "profile_match": "yes" if profile_match else "no",
        "multiple_profiles": "yes" if multiple_profiles else "no",
        "structure_valid": "yes" if structure_valid else "no",
        "structure_notes": "order ok" if structure_valid else "profile/db/api/page/ui/flow ordering violated or wrapper detected",
        "alias_components": alias_components,
        "alias_flows": alias_flows,
        "unknown_components": unknown_components,
        "unknown_flows": unknown_flows,
        "unsupported_constructs": parsed["unsupported_constructs"],
        "boundary_exceeded": "yes" if boundary_exceeded else "no",
        "boundary_reason": boundary_reason or "none",
        "model_output_issue": "yes" if (multiple_profiles or alias_components or alias_flows or unknown_components or unknown_flows or parsed["unsupported_constructs"]) else "no",
        "dictionary_gap": "no",
        "compiler_gap": "yes" if (compile_recommended and "under_specified" in boundary_reason) else "no",
        "unsupported_by_current_system": "yes" if boundary_exceeded and detected_profile == "after_sales" else "no",
        "expected_profile": expected_profile,
        "parsed": parsed,
    }


def score_candidate(requirement: str, candidate: str) -> int:
    expected = detect_expected_profile(requirement)
    parsed = parse_program(candidate)
    score = 0
    if expected in parsed["profiles"]:
        score += 10
    for line in parsed["lines"]:
        if expected == "landing" and "landing:" in line:
            score += 1
        elif expected == "ecom_min" and "ecom:" in line:
            score += 1
        elif expected == "after_sales" and "after_sales:" in line:
            score += 1
        elif expected == "app_min" and "app:" in line:
            score += 1
    return score


def choose_candidate(requirement: str, ail_text: str) -> str:
    candidates = split_candidates(ail_text)
    if len(candidates) == 1:
        return candidates[0]
    return max(candidates, key=lambda item: score_candidate(requirement, item))


def add_unique(items: list[str], token: str) -> None:
    if token not in items:
        items.append(token)


def repair(requirement: str, ail_text: str) -> str:
    expected_profile = detect_expected_profile(requirement)
    candidate = choose_candidate(requirement, ail_text)
    parsed = parse_program(candidate)

    profile = expected_profile
    if expected_profile in parsed["profiles"]:
        profile = expected_profile
    elif parsed["profiles"]:
        profile = parsed["profiles"][0]

    pages = parsed["pages"]
    if profile == "app_min":
        home_page = None
        home_ui: list[str] = []
        for page in pages:
            if page["path"] == "/" and home_page is None:
                home_page = {"name": "Home", "path": "/", "ui": []}
            for token in page["ui"]:
                replacement = UI_REPLACEMENTS.get(token, token)
                if replacement in SUPPORTED["app_min"]["ui"]:
                    add_unique(home_ui, replacement)
        if home_page is None:
            home_page = {"name": "Home", "path": "/", "ui": []}
        for token in home_ui:
            add_unique(home_page["ui"], token)
        if "聊天" in requirement or "chat" in requirement.lower():
            add_unique(home_page["ui"], "app:ChatWindow")
        if "顶部栏" in requirement or "top" in requirement.lower():
            add_unique(home_page["ui"], "app:TopBar")
        if "底部" in requirement or "tab" in requirement.lower():
            add_unique(home_page["ui"], "app:BottomTab")
        if "列表" in requirement or "联系人" in requirement:
            add_unique(home_page["ui"], "app:List")
        if any(word in requirement for word in ["卡片", "个人", "发现", "我的", "详情"]):
            add_unique(home_page["ui"], "app:Card")
        if any(word in requirement for word in ["新增任务", "编辑", "编辑输入", "输入", "输入内容", "输入框", "composer"]):
            add_unique(home_page["ui"], "app:Composer")
        if any(word in requirement for word in ["搜索联系人", "搜索", "search", "search bar", "查找"]):
            add_unique(home_page["ui"], "app:SearchBar")
        pages = [home_page]
        flows: list[str] = []
        db_lines: list[str] = []
        api_lines: list[str] = []
    else:
        flows = []
        for flow in parsed["flows"]:
            repaired_flow = FLOW_REPLACEMENTS.get(flow, flow)
            if repaired_flow in SUPPORTED[profile]["flows"]:
                add_unique(flows, repaired_flow)
        db_lines = parsed["db_lines"]
        api_lines = parsed["api_lines"]
        cleaned_pages = []
        for page in pages:
            cleaned = {"name": page["name"], "path": page["path"], "ui": []}
            for token in page["ui"]:
                repaired = UI_REPLACEMENTS.get(token, token)
                if repaired in SUPPORTED[profile]["ui"]:
                    add_unique(cleaned["ui"], repaired)
            cleaned_pages.append(cleaned)
        pages = cleaned_pages

        if profile == "landing":
            home_page = next((page for page in pages if page["path"] == "/"), None)
            if home_page is None:
                home_page = {"name": "Home", "path": "/", "ui": []}
                pages.insert(0, home_page)
            add_unique(home_page["ui"], "landing:Header")
            add_unique(home_page["ui"], "landing:Hero")
            if any(word in requirement for word in ["功能", "服务", "模块"]):
                add_unique(home_page["ui"], "landing:FeatureGrid")
            if any(word in requirement for word in ["团队", "团队介绍", "成员", "关于我们", "关于团队"]):
                add_unique(home_page["ui"], "landing:Team")
            if any(word in requirement for word in ["FAQ", "常见问题", "常见问答", "问答"]):
                add_unique(home_page["ui"], "landing:FAQ")
            if any(word in requirement for word in ["统计", "数据", "数字", "数据展示", "公司数据展示", "关键数据"]):
                add_unique(home_page["ui"], "landing:Stats")
            if (
                "客户 Logo" in requirement
                or "客户标识" in requirement
                or "客户 logos" in requirement
                or "合作伙伴" in requirement
                or "合作伙伴 logo" in requirement
                or "品牌墙" in requirement
                or "客户墙" in requirement
                or any(word in requirement.lower() for word in ["logo", "logos", "partners", "partner logos", "logo wall"])
            ):
                add_unique(home_page["ui"], "landing:LogoCloud")
            if any(
                word in requirement
                for word in [
                    "客户评价",
                    "用户评价",
                    "评价",
                    "testimonials",
                    "testimonial",
                    "用户反馈",
                    "客户反馈",
                    "review block",
                    "customer review",
                    "口碑",
                ]
            ):
                add_unique(home_page["ui"], "landing:Testimonial")
            if any(word in requirement for word in ["职位展示", "招聘岗位", "职位列表", "jobs", "careers", "join us", "招聘信息"]):
                add_unique(home_page["ui"], "landing:Jobs")
            if any(word in requirement for word in ["项目作品", "作品集", "portfolio", "案例展示", "case studies", "项目案例", "作品展示"]):
                add_unique(home_page["ui"], "landing:Portfolio")
            if "立即开始" in requirement or "预约演示" in requirement or "开始" in requirement:
                add_unique(home_page["ui"], "landing:CTA")
            add_unique(home_page["ui"], "landing:Footer")

            if "联系" in requirement:
                contact_page = next((page for page in pages if page["path"] == "/contact"), None)
                if contact_page is None:
                    contact_page = {"name": "Contact", "path": "/contact", "ui": []}
                    pages.append(contact_page)
                add_unique(contact_page["ui"], "landing:Contact")
                add_unique(flows, "CONTACT_SUBMIT")
            if "邮箱" in requirement or "留资" in requirement:
                add_unique(flows, "LEAD_CAPTURE")

        elif profile == "ecom_min":
            home_page = next((page for page in pages if page["path"] == "/"), None)
            if home_page is None:
                home_page = {"name": "Home", "path": "/", "ui": []}
                pages.insert(0, home_page)
            add_unique(home_page["ui"], "ecom:Header")
            if any(word in requirement for word in ["横幅", "首页横幅", "促销"]) or "banner" in requirement.lower():
                add_unique(home_page["ui"], "ecom:Banner")
            if any(word in requirement for word in ["分类", "分类导航", "分类页", "筛选"]) or "filters" in requirement.lower():
                add_unique(home_page["ui"], "ecom:CategoryNav")
            if "商品" in requirement:
                add_unique(home_page["ui"], "ecom:ProductGrid")
            if "详情" in requirement:
                product_page = next((page for page in pages if page["path"] == "/product/:id"), None)
                if product_page is None:
                    product_page = {"name": "Product", "path": "/product/:id", "ui": []}
                    pages.append(product_page)
                add_unique(product_page["ui"], "ecom:ProductDetail")
            if "购物车" in requirement:
                cart_page = next((page for page in pages if page["path"] == "/cart"), None)
                if cart_page is None:
                    cart_page = {"name": "Cart", "path": "/cart", "ui": []}
                    pages.append(cart_page)
                add_unique(cart_page["ui"], "ecom:CartPanel")
                add_unique(flows, "ADD_TO_CART")
            if "结算" in requirement:
                checkout_page = next((page for page in pages if page["path"] == "/checkout"), None)
                if checkout_page is None:
                    checkout_page = {"name": "Checkout", "path": "/checkout", "ui": []}
                    pages.append(checkout_page)
                add_unique(checkout_page["ui"], "ecom:CheckoutPanel")
                add_unique(flows, "CHECKOUT_SUBMIT")
                add_unique(flows, "ORDER_PLACE")
            if any(word in requirement for word in ["店铺", "店铺页", "品牌店铺"]) or "shop" in requirement.lower():
                shop_page = next((page for page in pages if page["path"] == "/shop/:id"), None)
                if shop_page is None:
                    shop_page = {"name": "Shop", "path": "/shop/:id", "ui": []}
                    pages.append(shop_page)
                add_unique(shop_page["ui"], "ecom:ShopHeader")
            if any(word in requirement for word in ["搜索", "搜索结果", "搜索结果页"]) or "search" in requirement.lower():
                search_page = next((page for page in pages if page["path"] == "/search"), None)
                if search_page is None:
                    search_page = {"name": "Search", "path": "/search", "ui": []}
                    pages.append(search_page)
                add_unique(search_page["ui"], "ecom:SearchResultGrid")

        elif profile == "after_sales":
            page = next((page for page in pages if page["path"] == "/after-sales"), None)
            if page is None:
                page = {"name": "AfterSales", "path": "/after-sales", "ui": []}
                pages = [page]
            add_unique(page["ui"], "after_sales:Entry")
            if "退款" in requirement:
                add_unique(page["ui"], "after_sales:Refund")
                add_unique(flows, "REFUND_FLOW")
            if "换货" in requirement:
                add_unique(page["ui"], "after_sales:Exchange")
                add_unique(flows, "EXCHANGE_FLOW")
            if "投诉" in requirement or "升级" in requirement:
                add_unique(page["ui"], "after_sales:Complaint")
                add_unique(flows, "COMPLAINT_DEESCALATE")
            if any(word in requirement for word in ["客服", "联系客服", "support", "客服支持", "在线客服"]):
                add_unique(page["ui"], "after_sales:Support")

    output_lines = [f"#PROFILE[{profile}]"]
    output_lines.extend(db_lines)
    output_lines.extend(api_lines)
    for page in pages:
        output_lines.append(f"@PAGE[{page['name']},{page['path']}]")
        for token in page["ui"]:
            output_lines.append(f"#UI[{token}]")
    for flow in flows:
        output_lines.append(f"#FLOW[{flow}]")
    return "\n".join(output_lines).strip() + "\n"


def summarize_issues(diagnosis: dict[str, Any]) -> str:
    issues: list[str] = []
    if diagnosis["multiple_profiles"] == "yes":
        issues.append("multiple_profiles")
    if diagnosis["structure_valid"] == "no":
        issues.append("structure_invalid")
    if diagnosis.get("alias_components"):
        issues.append(f"alias_component={','.join(diagnosis['alias_components'])}")
    if diagnosis.get("alias_flows"):
        issues.append(f"alias_flow={','.join(diagnosis['alias_flows'])}")
    if diagnosis["unknown_components"]:
        issues.append(f"unknown_component={','.join(diagnosis['unknown_components'])}")
    if diagnosis["unknown_flows"]:
        issues.append(f"unknown_flow={','.join(diagnosis['unknown_flows'])}")
    if diagnosis["unsupported_constructs"]:
        issues.append("unsupported_constructs")
    if diagnosis["boundary_exceeded"] == "yes":
        issues.append(f"boundary_exceeded={diagnosis['boundary_reason']}")
    return "; ".join(issues) if issues else "none"


def build_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Repair Smoke Report",
        "",
        "## Summary",
        f"- total_cases: {payload['case_count']}",
        f"- repair_success: {payload['repair_success_count']}",
        f"- repair_failed: {payload['repair_failure_count']}",
        f"- success_rate: {payload['success_rate']}%",
        "",
        "## Case Results",
    ]
    for item in sorted(payload["results"], key=lambda result: result["case_id"]):
        pre_ok = item["pre_compile_recommended"]
        post_ok = item["compile_recommended_after_repair"]
        if not pre_ok and post_ok:
            final_status = "PASS"
        elif pre_ok and post_ok and not item["repair_applied"]:
            final_status = "PASS (no repair needed)"
        else:
            final_status = "FAIL"
        requirement = item["requirement"].replace("\n", " ").strip()
        lines.extend(
            [
                "",
                f"### {item['case_id']}",
                f"- requirement: {requirement}",
                f"- pre_compile_recommended: {'yes' if pre_ok else 'no'}",
                f"- repair_applied: {'yes' if item['repair_applied'] else 'no'}",
                f"- post_compile_recommended: {'yes' if post_ok else 'no'}",
                f"- final_status: {final_status}",
                f"- pre_issues: {summarize_issues(item['pre_diagnosis'])}",
                f"- post_issues: {summarize_issues(item['post_diagnosis'])}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    results = []
    repaired_success = 0
    for case in cases:
        pre = diagnose(case["requirement"], case["broken_ail"])
        repaired_ail = case["broken_ail"]
        repair_applied = False
        if pre["compile_recommended"] == "no":
            repaired_ail = repair(case["requirement"], case["broken_ail"])
            repair_applied = True
        post = diagnose(case["requirement"], repaired_ail)
        if post["compile_recommended"] == "yes":
            repaired_success += 1
        results.append(
            {
                "case_id": case["case_id"],
                "requirement": case["requirement"],
                "pre_diagnosis": pre,
                "post_diagnosis": post,
                "repair_applied": repair_applied,
                "pre_compile_recommended": pre["compile_recommended"] == "yes",
                "compile_recommended_after_repair": post["compile_recommended"] == "yes",
                "repaired_ail": repaired_ail,
            }
        )

    payload = {
        "case_count": len(cases),
        "repair_success_count": repaired_success,
        "repair_failure_count": len(cases) - repaired_success,
        "success_rate": round((repaired_success / len(cases)) * 100, 2) if cases else 0.0,
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(build_report(payload), encoding="utf-8")
    print(f"total_cases={payload['case_count']}")
    print(f"repair_success_count={payload['repair_success_count']}")
    print(f"repair_failure_count={payload['repair_failure_count']}")
    print(f"success_rate={payload['success_rate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
