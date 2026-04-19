from __future__ import annotations

import importlib.util
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("AIL_REPO_ROOT", Path(__file__).resolve().parents[1])).expanduser().resolve()
INPUT_PATH = ROOT / "testing" / "real_requirements_v1.json"
RESULTS_DIR = ROOT / "testing" / "results"
RESULTS_JSON = RESULTS_DIR / "real_requirements_results.json"
RESULTS_MD = RESULTS_DIR / "real_requirements_report.md"
LIMITS = {"landing": 10, "ecom_min": 10, "after_sales": 5, "app_min": 5}


def load_repair_module():
    module_path = ROOT / "testing" / "repair_smoke_runner.py"
    spec = importlib.util.spec_from_file_location("repair_smoke_runner", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load helper module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


repair_mod = load_repair_module()


def select_requirements(payload: dict[str, Any]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    counters = defaultdict(int)
    for item in payload["requirements"]:
        category = item["category"]
        if counters[category] >= LIMITS[category]:
            continue
        selected.append(item)
        counters[category] += 1
    return selected


def add_unique(items: list[str], token: str) -> None:
    if token not in items:
        items.append(token)


def generate_landing(requirement: str) -> str:
    pages: list[dict[str, Any]] = [{"name": "Home", "path": "/", "ui": []}]
    home = pages[0]["ui"]
    add_unique(home, "landing:Header")
    add_unique(home, "landing:Hero")
    add_unique(home, "landing:Footer")
    if any(word in requirement for word in ["功能", "服务", "模块", "课程", "案例", "项目作品", "职位展示", "招聘岗位"]):
        add_unique(home, "landing:FeatureGrid")
    if any(word in requirement for word in ["团队", "团队介绍", "成员", "关于我们", "关于我", "关于团队", "品牌故事"]):
        add_unique(home, "landing:Team")
    if any(word in requirement for word in ["FAQ", "常见问题", "常见问答", "问答"]):
        add_unique(home, "landing:FAQ")
    if any(word in requirement for word in ["数据", "统计", "数字", "数据展示", "公司数据展示", "关键数据"]):
        add_unique(home, "landing:Stats")
    if any(word in requirement.lower() for word in ["logo", "logos", "partners", "partner logos", "logo wall"]):
        add_unique(home, "landing:LogoCloud")
    if any(word in requirement for word in ["客户 Logo", "客户标识", "客户 logos", "合作伙伴", "合作伙伴 logo", "品牌墙", "客户墙"]):
        add_unique(home, "landing:LogoCloud")
    if any(
        word in requirement
        for word in [
            "客户评价",
            "用户评价",
            "评价",
            "testimonial",
            "testimonials",
            "用户反馈",
            "客户反馈",
            "review block",
            "customer review",
            "口碑",
        ]
    ):
        add_unique(home, "landing:Testimonial")
    if any(word in requirement for word in ["职位展示", "招聘岗位", "职位列表", "jobs", "careers", "join us", "招聘信息"]):
        add_unique(home, "landing:Jobs")
    if any(word in requirement for word in ["项目作品", "作品集", "portfolio", "案例展示", "case studies", "项目案例", "作品展示"]):
        add_unique(home, "landing:Portfolio")
    if any(word in requirement for word in ["价格", "试用", "预约演示", "立即开始", "立即体验", "开始使用", "cta"]):
        add_unique(home, "landing:CTA")

    if any(word in requirement for word in ["关于我们", "关于我", "品牌故事"]):
        pages.append({"name": "About", "path": "/about", "ui": ["landing:Hero"]})
    if any(word in requirement for word in ["功能", "服务", "模块", "课程", "案例", "项目作品", "职位展示", "职位列表", "作品展示", "项目案例"]):
        pages.append({"name": "Features", "path": "/features", "ui": ["landing:FeatureGrid"]})
    if "价格" in requirement:
        pages.append({"name": "Pricing", "path": "/pricing", "ui": ["landing:Pricing"]})
    if any(word in requirement for word in ["联系", "联系方式", "联系我们"]):
        pages.append({"name": "Contact", "path": "/contact", "ui": ["landing:Contact"]})

    flows: list[str] = []
    if any(word in requirement for word in ["联系", "联系方式", "联系我们", "预约演示"]):
        add_unique(flows, "CONTACT_SUBMIT")
    if any(word in requirement for word in ["留资", "试用", "预约演示", "开始使用", "立即开始", "立即体验"]):
        add_unique(flows, "LEAD_CAPTURE")

    return render_program("landing", pages, [], [], flows)


def generate_ecom(requirement: str) -> str:
    pages: list[dict[str, Any]] = [{"name": "Home", "path": "/", "ui": ["ecom:Header"]}]
    home = pages[0]["ui"]
    if any(word in requirement for word in ["横幅", "首页横幅", "促销"]) or "banner" in requirement.lower():
        add_unique(home, "ecom:Banner")
    if any(word in requirement for word in ["分类", "分类导航", "分类页", "筛选"]) or "filters" in requirement.lower():
        add_unique(home, "ecom:CategoryNav")
    add_unique(home, "ecom:ProductGrid")

    if any(word in requirement for word in ["商品详情", "详情"]):
        pages.append({"name": "Product", "path": "/product/:id", "ui": ["ecom:ProductDetail"]})
    if "购物车" in requirement:
        pages.append({"name": "Cart", "path": "/cart", "ui": ["ecom:CartPanel"]})
    if "结算" in requirement:
        pages.append({"name": "Checkout", "path": "/checkout", "ui": ["ecom:CheckoutPanel"]})
    if any(word in requirement for word in ["店铺", "店铺页", "品牌店铺"]) or "shop" in requirement.lower():
        pages.append({"name": "Shop", "path": "/shop/:id", "ui": ["ecom:ShopHeader", "ecom:ProductGrid"]})
    if any(word in requirement for word in ["搜索", "搜索结果", "搜索结果页"]) or "search" in requirement.lower():
        pages.append({"name": "Search", "path": "/search", "ui": ["ecom:SearchResultGrid"]})
    if any(word in requirement for word in ["分类", "分类导航", "分类页", "筛选"]) or "filters" in requirement.lower():
        pages.append({"name": "Category", "path": "/category/:name", "ui": ["ecom:CategoryNav", "ecom:ProductGrid"]})

    flows: list[str] = []
    if "购物车" in requirement or "加入购物车" in requirement:
        add_unique(flows, "ADD_TO_CART")
    if "结算" in requirement:
        add_unique(flows, "CHECKOUT_SUBMIT")
        add_unique(flows, "ORDER_PLACE")
    return render_program("ecom_min", pages, [], [], flows)


def generate_after_sales(requirement: str) -> str:
    page = {"name": "AfterSales", "path": "/after-sales", "ui": ["after_sales:Entry"]}
    flows: list[str] = []
    if "退款" in requirement:
        add_unique(page["ui"], "after_sales:Refund")
        add_unique(flows, "REFUND_FLOW")
    if "换货" in requirement:
        add_unique(page["ui"], "after_sales:Exchange")
        add_unique(flows, "EXCHANGE_FLOW")
    if any(word in requirement for word in ["投诉", "升级"]):
        add_unique(page["ui"], "after_sales:Complaint")
        add_unique(flows, "COMPLAINT_DEESCALATE")
    if any(word in requirement for word in ["客服", "联系客服", "support", "客服支持", "在线客服"]):
        add_unique(page["ui"], "after_sales:Support")
    return render_program("after_sales", [page], [], [], flows)


def generate_app(requirement: str) -> str:
    page = {"name": "Home", "path": "/", "ui": ["app:TopBar", "app:BottomTab"]}
    if any(word in requirement for word in ["聊天", "消息", "Chat"]):
        add_unique(page["ui"], "app:List")
        add_unique(page["ui"], "app:ChatWindow")
    if any(word in requirement for word in ["联系人", "任务", "笔记", "列表", "搜索联系人"]):
        add_unique(page["ui"], "app:List")
    if any(word in requirement for word in ["发现", "我的", "卡片", "个人", "详情", "新增任务", "编辑笔记"]):
        add_unique(page["ui"], "app:Card")
    if any(word in requirement for word in ["新增任务", "编辑", "编辑输入", "输入", "输入内容", "输入框", "composer"]):
        add_unique(page["ui"], "app:Composer")
    if any(word in requirement for word in ["搜索联系人", "搜索", "search", "search bar", "查找"]):
        add_unique(page["ui"], "app:SearchBar")
    return render_program("app_min", [page], [], [], [])


def render_program(profile: str, pages: list[dict[str, Any]], db_lines: list[str], api_lines: list[str], flows: list[str]) -> str:
    lines = [f"#PROFILE[{profile}]"]
    lines.extend(db_lines)
    lines.extend(api_lines)
    for page in pages:
        lines.append(f"@PAGE[{page['name']},{page['path']}]")
        for token in page["ui"]:
            lines.append(f"#UI[{token}]")
    for flow in flows:
        lines.append(f"#FLOW[{flow}]")
    return "\n".join(lines) + "\n"


def generate_ail(category: str, requirement: str) -> str:
    if category == "landing":
        return generate_landing(requirement)
    if category == "ecom_min":
        return generate_ecom(requirement)
    if category == "after_sales":
        return generate_after_sales(requirement)
    if category == "app_min":
        return generate_app(requirement)
    raise ValueError(f"Unsupported category: {category}")


def detect_under_specified(category: str, requirement: str, ail_text: str) -> bool:
    parsed = repair_mod.parse_program(ail_text)
    ui_tokens = {token for page in parsed["pages"] for token in page["ui"]}
    flows = set(parsed["flows"])
    if category == "landing":
        checks = [
            ("功能" in requirement or "服务" in requirement or "模块" in requirement, "landing:FeatureGrid"),
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
                "客户 Logo" in requirement
                or "客户标识" in requirement
                or "客户 logos" in requirement
                or "合作伙伴" in requirement
                or "合作伙伴 logo" in requirement
                or "品牌墙" in requirement
                or "客户墙" in requirement
                or any(word in requirement.lower() for word in ["logo", "logos", "partners", "partner logos", "logo wall"]),
                "landing:LogoCloud",
            ),
            (
                "客户评价" in requirement
                or "用户评价" in requirement
                or "评价" in requirement
                or "testimonial" in requirement.lower()
                or "testimonials" in requirement.lower()
                or "用户反馈" in requirement
                or "客户反馈" in requirement
                or "review block" in requirement.lower()
                or "customer review" in requirement.lower()
                or "口碑" in requirement,
                "landing:Testimonial",
            ),
            (
                "职位展示" in requirement
                or "招聘岗位" in requirement
                or "职位列表" in requirement
                or "jobs" in requirement.lower()
                or "careers" in requirement.lower()
                or "join us" in requirement.lower()
                or "招聘信息" in requirement,
                "landing:Jobs",
            ),
            (
                "项目作品" in requirement
                or "作品集" in requirement
                or "portfolio" in requirement.lower()
                or "案例展示" in requirement
                or "case studies" in requirement.lower()
                or "项目案例" in requirement
                or "作品展示" in requirement,
                "landing:Portfolio",
            ),
            ("试用" in requirement or "开始" in requirement or "预约演示" in requirement or "立即体验" in requirement, "landing:CTA"),
        ]
        if any(required and token not in ui_tokens for required, token in checks):
            return True
        if "联系" in requirement and "CONTACT_SUBMIT" not in flows:
            return True
        if any(word in requirement for word in ["试用", "预约演示", "立即开始", "立即体验"]) and not ({"CONTACT_SUBMIT", "LEAD_CAPTURE"} & flows):
            return True
    if category == "ecom_min":
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
    if category == "after_sales":
        checks = [
            ("退款" in requirement, "after_sales:Refund"),
            ("换货" in requirement, "after_sales:Exchange"),
            (any(word in requirement for word in ["投诉", "升级"]), "after_sales:Complaint"),
            (any(word in requirement for word in ["客服", "联系客服", "support", "客服支持", "在线客服"]), "after_sales:Support"),
        ]
        if any(required and token not in ui_tokens for required, token in checks):
            return True
    if category == "app_min":
        checks = [
            (any(word in requirement for word in ["顶部栏", "顶部", "header"]), "app:TopBar"),
            (any(word in requirement for word in ["底部 tab", "底部", "tab"]), "app:BottomTab"),
            (any(word in requirement for word in ["聊天", "消息"]), "app:ChatWindow"),
            (any(word in requirement for word in ["列表", "联系人", "任务", "笔记"]), "app:List"),
            (any(word in requirement for word in ["卡片", "个人", "发现", "我的", "详情"]), "app:Card"),
            (any(word in requirement for word in ["新增任务", "编辑", "编辑输入", "输入", "输入内容", "输入框", "composer"]), "app:Composer"),
            (any(word in requirement for word in ["搜索联系人", "搜索", "search", "search bar", "查找"]), "app:SearchBar"),
        ]
        if any(required and token not in ui_tokens for required, token in checks):
            return True
    return False


def extract_issue_types(diagnosis: dict[str, Any], category: str, requirement: str, ail_text: str) -> list[str]:
    issues: list[str] = []
    if diagnosis["multiple_profiles"] == "yes":
        issues.append("multiple_profiles")
    if diagnosis["structure_valid"] == "no":
        issues.append("structure_invalid")
    if diagnosis["unknown_components"]:
        issues.append("unknown_component")
    if diagnosis["unknown_flows"]:
        issues.append("unknown_flow")
    if diagnosis["boundary_exceeded"] == "yes":
        issues.append("boundary_exceeded")
    if detect_under_specified(category, requirement, ail_text):
        issues.append("under_specified")
    if diagnosis["unsupported_constructs"]:
        issues.append("unsupported_constructs")
    return issues


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Real Requirements Test Report",
        "",
        "## Summary",
        f"- total_requirements: {payload['summary']['total_requirements']}",
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
    lines.append("## Top Issues")
    if payload["top_issues"]:
        for issue, count in payload["top_issues"]:
            lines.append(f"- {issue}: {count}")
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    selected = select_requirements(payload)
    results = []
    issue_counter: Counter[str] = Counter()
    category_breakdown = {
        category: {"total": 0, "initial_compile_candidates": 0, "repair_success": 0, "final_compile_candidates": 0}
        for category in LIMITS
    }
    initial_compile_candidates = 0
    repair_attempts = 0
    repair_success = 0
    final_compile_candidates = 0

    for item in selected:
        requirement = item["requirement"]
        category = item["category"]
        generated_ail = generate_ail(category, requirement)
        pre = repair_mod.diagnose(requirement, generated_ail)
        pre_ok = pre["compile_recommended"] == "yes"
        issues = extract_issue_types(pre, category, requirement, generated_ail)
        issue_counter.update(issues)
        repaired_ail = generated_ail
        repair_applied = False
        if not pre_ok:
            repair_attempts += 1
            repaired_ail = repair_mod.repair(requirement, generated_ail)
            repair_applied = True
        post = repair_mod.diagnose(requirement, repaired_ail)
        post_ok = post["compile_recommended"] == "yes"

        category_breakdown[category]["total"] += 1
        if pre_ok:
            category_breakdown[category]["initial_compile_candidates"] += 1
            initial_compile_candidates += 1
        if repair_applied and post_ok:
            category_breakdown[category]["repair_success"] += 1
            repair_success += 1
        if post_ok:
            category_breakdown[category]["final_compile_candidates"] += 1
            final_compile_candidates += 1

        results.append(
            {
                "requirement_id": item["id"],
                "category": category,
                "title": item["title"],
                "requirement": requirement,
                "generated_ail": generated_ail,
                "pre_compile_recommended": pre_ok,
                "repair_applied": repair_applied,
                "post_compile_recommended": post_ok,
                "final_profile": post["detected_profile"],
                "issues": issues,
                "pre_diagnosis": pre,
                "post_diagnosis": post,
            }
        )

    summary = {
        "total_requirements": len(selected),
        "initial_compile_candidates": initial_compile_candidates,
        "repair_attempts": repair_attempts,
        "repair_success": repair_success,
        "final_compile_candidates": final_compile_candidates,
        "source_file": str(INPUT_PATH),
        "source_version": payload.get("version", "unknown"),
    }
    output = {
        "summary": summary,
        "category_breakdown": category_breakdown,
        "top_issues": issue_counter.most_common(),
        "results": results,
    }
    RESULTS_JSON.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    RESULTS_MD.write_text(render_report(output), encoding="utf-8")

    initial_rate = round((initial_compile_candidates / len(selected)) * 100, 2) if selected else 0.0
    repair_success_rate = round((repair_success / repair_attempts) * 100, 2) if repair_attempts else 0.0
    final_rate = round((final_compile_candidates / len(selected)) * 100, 2) if selected else 0.0
    print(f"total_requirements={len(selected)}")
    print(f"initial_compile_rate={initial_rate}")
    print(f"repair_success_rate={repair_success_rate}")
    print(f"final_compile_rate={final_rate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
