from __future__ import annotations

import base64
from datetime import datetime
import json
import re
import shutil
from pathlib import Path
from typing import Any

from ail_engine_v4 import AILParserV4, AILProjectGeneratorV4
from ail_engine_v5_ecom import AILEcomGeneratorMixin


class AILParserV5(AILParserV4):
    """AIL V5 parser keeps V4 syntax unchanged."""
    PROFILE_PATTERN = re.compile(r"^#PROFILE\[([^\]]+)\]$")
    FLOW_PATTERN = re.compile(r"^#FLOW\[([^\]]+)\]\{(.*)\}$", re.DOTALL)
    SUPPORTED_PROFILES = {"ecom_min", "after_sales", "landing", "app_min"}

    @staticmethod
    def _clean_action_token(token: str) -> str:
        action = token.strip().strip("~").strip()
        if not action:
            return ""

        # Recover from stray tail braces introduced by broken concatenation.
        if action.startswith(("@PAGE[", "^SYS[", "#LIB[", ">DB_REL[")):
            action = action.rstrip("}").strip()

        return action

    def split_actions(self) -> list[str]:
        actions: list[str] = []
        current: list[str] = []
        quote_char: str | None = None
        escape = False
        round_depth = 0
        square_depth = 0
        curly_depth = 0

        for char in self.ail_code:
            if quote_char is not None:
                current.append(char)
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == quote_char:
                    quote_char = None
                continue

            if char in ('"', "'"):
                quote_char = char
                current.append(char)
                continue

            if char == "(":
                round_depth += 1
            elif char == ")":
                round_depth = max(0, round_depth - 1)
            elif char == "[":
                square_depth += 1
            elif char == "]":
                square_depth = max(0, square_depth - 1)
            elif char == "{":
                curly_depth += 1
            elif char == "}":
                curly_depth = max(0, curly_depth - 1)

            if char in {"~", "\n"} and round_depth == 0 and square_depth == 0 and curly_depth == 0:
                token = self._clean_action_token("".join(current))
                if token:
                    actions.append(token)
                current = []
                continue

            current.append(char)

        tail = self._clean_action_token("".join(current))
        if tail:
            actions.append(tail)
        return actions

    def parse(self) -> dict[str, Any]:
        profiles: list[str] = []
        filtered_tokens: list[str] = []
        seen_profiles: set[str] = set()

        for raw_action in self.split_actions():
            token = raw_action.strip()
            profile_match = self.PROFILE_PATTERN.fullmatch(token)
            if profile_match:
                profile_name = profile_match.group(1).strip().lower()
                if profile_name in self.SUPPORTED_PROFILES and profile_name not in seen_profiles:
                    seen_profiles.add(profile_name)
                    profiles.append(profile_name)
                continue
            flow_match = self.FLOW_PATTERN.fullmatch(token)
            if flow_match:
                flow_name = flow_match.group(1).strip()
                flow_config = flow_match.group(2).strip()
                filtered_tokens.append(f"#UI[flow:{flow_name}]{{{flow_config}}}")
                continue
            filtered_tokens.append(token)

        original_code = self.ail_code
        try:
            self.ail_code = "~".join(filtered_tokens)
            ast = super().parse()
        finally:
            self.ail_code = original_code

        ast["profiles"] = profiles
        return ast


class AILProjectGeneratorV5(AILEcomGeneratorMixin, AILProjectGeneratorV4):
    def __init__(
        self,
        ast: dict[str, Any],
        base_dir: str = "./output_projects",
        template_dir: str = "/Users/carwynmac/ai-cl/output_projects/ail_vue_base",
    ) -> None:
        super().__init__(ast, base_dir=base_dir)
        self.template_dir = Path(template_dir).expanduser()
        self._api_client_import: str | None = None
        self._landing_dictionary = self._load_profile_dictionary("landing")
        self._local_rebuild_backup_id: str | None = None
        self._local_rebuild_backups: list[tuple[str, str]] = []

    def _resolve_template_dir(self) -> Path:
        template_path = self.template_dir
        if not template_path.is_absolute():
            template_path = (Path.cwd() / template_path).resolve()

        if not template_path.exists():
            raise FileNotFoundError(f"Frontend template directory not found: {template_path}")
        if not template_path.is_dir():
            raise NotADirectoryError(f"Frontend template path is not a directory: {template_path}")

        return template_path

    @staticmethod
    def _safe_write_text(path: Path, content: str) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise RuntimeError(f"Failed to write file: {path} ({exc})") from exc

    def _backup_existing_managed_file(self, project_root: Path, path: Path) -> None:
        if not path.exists():
            return
        relative = path.resolve().relative_to(project_root.resolve()).as_posix()
        if self._local_rebuild_backup_id is None:
            self._local_rebuild_backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffixes = path.suffixes
        if suffixes:
            full_suffix = "".join(suffixes)
            backup_name = f"{path.name[:-len(full_suffix)]}.local{full_suffix}"
        else:
            backup_name = f"{path.name}.local"
        backup_target = (
            project_root
            / ".ail"
            / "local_rebuild_backups"
            / self._local_rebuild_backup_id
            / Path(relative).with_name(backup_name)
        )
        backup_target.parent.mkdir(parents=True, exist_ok=True)
        backup_target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        backup_rel = backup_target.resolve().relative_to(project_root.resolve()).as_posix()
        self._local_rebuild_backups.append((relative, backup_rel))

    def _safe_write_managed_text(self, project_root: Path, path: Path, content: str) -> None:
        if path.exists():
            try:
                current = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise RuntimeError(f"Failed to read managed file before overwrite: {path} ({exc})") from exc
            if current != content:
                self._backup_existing_managed_file(project_root, path)
        self._safe_write_text(path, content)

    def _write_local_rebuild_backup_summary(self, project_root: Path) -> None:
        if not self._local_rebuild_backups or not self._local_rebuild_backup_id:
            return
        summary_path = (
            project_root
            / ".ail"
            / "local_rebuild_backups"
            / self._local_rebuild_backup_id
            / "summary.md"
        )
        lines = [
            "# Local Rebuild Backup Summary",
            "",
            "These files were overwritten by a local managed rebuild and were backed up first.",
            "",
            "Move durable structure/content changes back into `.ail/source.ail`.",
            "Move durable visual changes into `frontend/src/ail-overrides/theme.tokens.css` or `frontend/src/ail-overrides/custom.css`.",
            "",
            "Backups:",
            "",
        ]
        for original_rel, backup_rel in self._local_rebuild_backups:
            lines.append(f"- `{original_rel}` -> `{backup_rel}`")
        self._safe_write_text(summary_path, "\n".join(lines) + "\n")
        print(
            "MANAGED_BACKUP_SUMMARY="
            f"{summary_path.resolve().relative_to(project_root.resolve()).as_posix()}"
        )

    @staticmethod
    def _safe_remove_tree(path: Path) -> None:
        if not path.exists():
            return
        try:
            shutil.rmtree(path)
        except OSError as exc:
            raise RuntimeError(f"Failed to remove managed directory: {path} ({exc})") from exc

    def _ensure_override_scaffold(self, frontend_dir: Path) -> None:
        overrides_dir = frontend_dir / "src" / "ail-overrides"
        components_dir = overrides_dir / "components"
        examples_dir = components_dir / "examples"
        assets_dir = overrides_dir / "assets"
        public_overrides_dir = frontend_dir / "public" / "ail-overrides"

        for path in (overrides_dir, components_dir, examples_dir, assets_dir, public_overrides_dir):
            path.mkdir(parents=True, exist_ok=True)

        readme_path = overrides_dir / "README.md"
        if not readme_path.exists():
            self._safe_write_text(
                readme_path,
                (
                    "# AIL Overrides\n\n"
                    "Files in this folder are unmanaged.\n\n"
                    "- edit `theme.tokens.css` for global theme tokens\n"
                    "- edit `custom.css` for local visual overrides\n"
                    "- place durable custom Vue code in `components/`\n"
                    "- place durable assets in `assets/` or `public/ail-overrides/`\n"
                    "- do not put long-term edits into generated managed views\n"
                ),
            )

        theme_tokens_path = overrides_dir / "theme.tokens.css"
        if not theme_tokens_path.exists():
            self._safe_write_text(
                theme_tokens_path,
                (
                    "/* Unmanaged theme tokens: safe to edit. */\n"
                    ":root {\n"
                    "  /* Example tokens\n"
                    "  --ail-brand: #2563eb;\n"
                    "  --ail-accent: #0ea5e9;\n"
                    "  --ail-display-font: 'Avenir Next', 'Helvetica Neue', sans-serif;\n"
                    "  */\n"
                    "}\n"
                ),
            )

        custom_css_path = overrides_dir / "custom.css"
        if not custom_css_path.exists():
            self._safe_write_text(
                custom_css_path,
                "/* Unmanaged local overrides: safe to edit. */\n",
            )

        for marker in (
            components_dir / ".gitkeep",
            assets_dir / ".gitkeep",
            public_overrides_dir / ".gitkeep",
        ):
            if not marker.exists():
                self._safe_write_text(marker, "")

        components_readme_path = components_dir / "README.md"
        if not components_readme_path.exists():
            self._safe_write_text(
                components_readme_path,
                (
                    "# AIL Component Hooks\n\n"
                    "Files in this folder are unmanaged and safe to edit.\n\n"
                    "Hook naming:\n\n"
                    "- `page.home.before.vue`\n"
                    "- `page.home.after.vue`\n"
                    "- `page.home.before.html`\n"
                    "- `page.contact.after.vue`\n\n"
                    "Rules:\n\n"
                    "- filename without extension becomes the hook name\n"
                    "- Vue components (`.vue`) render as dynamic components\n"
                    "- HTML partials (`.html`) render as raw named partials\n"
                    "- copy one starter file from `components/examples/` into `components/` and rename it to a real hook name\n"
                    "- inspect `.ail/hook_catalog.md` for the current page / section / slot hook inventory\n"
                    "- rebuilds keep this folder intact\n"
                    "- long-term structure/content changes still belong in `.ail/source.ail`\n"
                ),
            )

        examples_readme_path = examples_dir / "README.md"
        if not examples_readme_path.exists():
            self._safe_write_text(
                examples_readme_path,
                (
                    "# AIL Hook Examples\n\n"
                    "These example files are safe starter references.\n\n"
                    "How to use:\n\n"
                    "1. inspect `.ail/hook_catalog.md`\n"
                    "2. copy one example from this folder into `../`\n"
                    "3. rename it to a real hook name such as `page.home.before.vue`\n"
                    "4. edit it and rebuild or refresh the frontend\n\n"
                    "Why these files do not render automatically:\n\n"
                    "- filenames ending in `.example.vue` or `.example.html` do not match active hook names\n"
                    "- they are reference material only until you copy and rename them\n"
                ),
            )

        vue_example_path = examples_dir / "page.home.before.example.vue"
        if not vue_example_path.exists():
            self._safe_write_text(
                vue_example_path,
                (
                    "<template>\n"
                    '  <aside class=\"ail-example-hook-card\">\n'
                    '    <div class=\"ail-example-hook-card__eyebrow\">Example Hook</div>\n'
                    "    <h3>{{ title }}</h3>\n"
                    "    <p>Hook: <code>{{ hookName }}</code></p>\n"
                    '    <p>Page: <code>{{ context?.pageKey || "unknown" }}</code></p>\n'
                    '    <p v-if=\"runtimeKeys.length\">Runtime keys: {{ runtimeKeys.join(\", \") }}</p>\n'
                    "  </aside>\n"
                    "</template>\n\n"
                    "<script setup lang=\"ts\">\n"
                    'import { computed } from "vue";\n\n'
                    "const props = defineProps<{\n"
                    "  context?: Record<string, any> | null;\n"
                    "  hookName: string;\n"
                    "}>();\n\n"
                    'const title = computed(() => props.context?.pageName ? `${props.context.pageName} override` : "AIL override");\n'
                    "const runtimeKeys = computed(() => Object.keys((props.context?.runtime as Record<string, unknown> | undefined) || {}));\n"
                    "</script>\n\n"
                    "<style scoped>\n"
                    ".ail-example-hook-card {\n"
                    "  margin: 12px 0;\n"
                    "  padding: 14px 16px;\n"
                    "  border: 1px dashed rgba(37, 99, 235, 0.35);\n"
                    "  border-radius: 16px;\n"
                    "  background: rgba(239, 246, 255, 0.72);\n"
                    "  color: #0f172a;\n"
                    "}\n"
                    ".ail-example-hook-card__eyebrow {\n"
                    "  font-size: 11px;\n"
                    "  letter-spacing: 0.18em;\n"
                    "  text-transform: uppercase;\n"
                    "  color: #2563eb;\n"
                    "  margin-bottom: 8px;\n"
                    "}\n"
                    "code {\n"
                    "  font-size: 0.92em;\n"
                    "}\n"
                    "</style>\n"
                ),
            )

        html_example_path = examples_dir / "page.home.section.hero.after.example.html"
        if not html_example_path.exists():
            self._safe_write_text(
                html_example_path,
                (
                    "<section class=\"ail-example-partial\">\n"
                    "  <p><strong>Example partial:</strong> copy this file into <code>components/</code> and rename it to a real hook such as <code>page.home.section.hero.after.html</code>.</p>\n"
                    "  <p>Use HTML partials for small trust notes, badges, helper copy, or decorative inserts.</p>\n"
                    "</section>\n"
                ),
            )

    def _write_managed_system_files(self, project_root: Path, frontend_dir: Path) -> None:
        system_dir = frontend_dir / "src" / "ail-managed" / "system"
        system_dir.mkdir(parents=True, exist_ok=True)
        self._safe_write_managed_text(
            project_root,
            system_dir / "AILSlotHost.vue",
            (
                "<template>\n"
                "  <component :is=\"resolvedComponent\" v-if=\"resolvedComponent\" :context=\"props.context\" :hook-name=\"props.name\" class=\"ail-slot-host ail-slot-host--component\" />\n"
                "  <div v-else-if=\"resolvedPartial\" class=\"ail-slot-host ail-slot-host--partial\" :data-ail-hook=\"props.name\" :data-ail-context=\"serializedContext\" v-html=\"resolvedPartial\"></div>\n"
                "</template>\n\n"
                "<script setup lang=\"ts\">\n"
                'import { computed } from "vue";\n\n'
                "const props = defineProps<{\n"
                "  name: string;\n"
                "  context?: Record<string, unknown> | null;\n"
                "}>();\n\n"
                "const componentModules = import.meta.glob(\"../../ail-overrides/components/**/*.vue\", { eager: true });\n"
                "const partialModules = import.meta.glob(\"../../ail-overrides/components/**/*.html\", { eager: true, query: \"?raw\", import: \"default\" });\n\n"
                "function hookKey(path: string): string {\n"
                "  const normalized = path.replace(/\\\\/g, \"/\");\n"
                "  const marker = \"/ail-overrides/components/\";\n"
                "  const relative = normalized.includes(marker) ? normalized.split(marker)[1] : normalized.split(\"/\").pop() || normalized;\n"
                "  return relative.replace(/\\.(vue|html)$/i, \"\").replace(/\\//g, \".\");\n"
                "}\n\n"
                "const componentRegistry = Object.fromEntries(\n"
                "  Object.entries(componentModules).map(([path, mod]) => [hookKey(path), (mod as { default?: unknown }).default ?? mod]),\n"
                ");\n\n"
                "const partialRegistry = Object.fromEntries(\n"
                "  Object.entries(partialModules).map(([path, mod]) => [hookKey(path), typeof mod === \"string\" ? mod : \"\"]),\n"
                ");\n\n"
                "const resolvedComponent = computed(() => componentRegistry[props.name] ?? null);\n"
                "const resolvedPartial = computed(() => partialRegistry[props.name] ?? \"\");\n"
                "const serializedContext = computed(() => JSON.stringify(props.context ?? null));\n"
                "</script>\n\n"
                "<style scoped>\n"
                ".ail-slot-host {\n"
                "  width: 100%;\n"
                "}\n"
                ".ail-slot-host--partial :deep(*) {\n"
                "  box-sizing: border-box;\n"
                "}\n"
                "</style>\n"
            ),
        )

    @staticmethod
    def _page_hook_key(page: dict[str, Any]) -> str:
        raw_name = str(page.get("name", "")).strip() or str(page.get("path", "")).strip() or "page"
        normalized = re.sub(r"[^a-z0-9]+", ".", AILProjectGeneratorV5._sanitize_file_stem(raw_name).lower())
        return normalized.strip(".") or "page"

    def _hook_runtime_context_pairs(self, page: dict[str, Any]) -> list[tuple[str, str]]:
        page_path = str(page.get("path", "")).strip() or "/"
        profiles = self._profiles()
        if "landing" in profiles and page_path in {"/", "/about", "/features", "/pricing", "/contact"}:
            return [
                ("singlePageLanding", "!!singlePageLanding"),
                ("navCount", "navLinks.length"),
                ("faqCount", "faqItems.length"),
                ("contactEnabled", "!!contactSectionEnabled"),
                ("contactSent", "!!contactSent"),
                ("leadSent", "!!leadSent"),
                ("portfolioMode", "!!personalPortfolioMode"),
            ]
        if page_path == "/after-sales":
            return [
                ("hasOrderContext", "!!orderId"),
                ("activePanel", 'String(activePanel || "")'),
                ("hasActivePanel", "!!activePanel"),
                ("trackedCaseOwner", 'String(trackedCaseOwnerTag || "")'),
                ("trackedCaseFocus", 'String(trackedCaseFocus || "")'),
                ("caseStepCount", "caseFlowTrack.length"),
            ]
        if page_path == "/search":
            return [
                ("keyword", 'String(keyword || "").trim()'),
                ("activeCategory", 'String(activeCategory || "").trim() || "全部"'),
                ("resultCount", "results.length"),
            ]
        if page_path == "/category/:name":
            return [
                ("categoryName", 'String(categoryName || "").trim()'),
                ("sortBy", 'String(sortBy || "").trim() || "sales"'),
                ("resultCount", "displayProducts.length"),
            ]
        if page_path == "/shop/:id":
            return [
                ("shopId", 'String(shopId || "").trim()'),
                ("shopName", 'String((shopInfo && shopInfo.shop_name) || "")'),
                ("shopProductCount", "shopProducts.length"),
                ("recommendedCount", "recommended.length"),
                ("hasDiscoverySource", "!!sourceDiscoveryLabel"),
            ]
        if page_path == "/product/:id":
            return [
                ("hasShopSource", "!!sourceShopId"),
                ("hasDiscoverySource", "!!sourceDiscoveryLabel"),
                ("spec", 'String(spec || "").trim() || "标准款"'),
                ("quantity", "normalizedQuantity"),
                ("cartCount", "cartCount"),
                ("hasAddFeedback", "!!showAddFeedback"),
            ]
        if page_path == "/cart":
            return [
                ("itemCount", "itemCount"),
                ("grandTotal", "grandTotal"),
                ("hasProductSource", "!!sourceProductTitle"),
                ("hasDiscoverySource", "!!sourceDiscoveryLabel"),
                ("hasShopSource", "!!sourceShopId"),
            ]
        if page_path == "/checkout":
            return [
                ("displayItemCount", "displayItemCount"),
                ("displayGrandTotal", "displayGrandTotal"),
                ("paymentLabel", 'String(currentPaymentLabel || "")'),
                ("hasProductSource", "!!sourceProductTitle"),
                ("hasDiscoverySource", "!!sourceDiscoveryLabel"),
                ("hasRecentOrder", "!!recentOrder"),
            ]
        return []

    def _hook_context_attr(
        self,
        page: dict[str, Any],
        hook_scope: str,
        *,
        section_key: str | None = None,
        slot_key: str | None = None,
    ) -> str:
        context: dict[str, Any] = {
            "pageKey": self._page_hook_key(page),
            "pageName": str(page.get("name", "")).strip() or "Page",
            "pagePath": str(page.get("path", "")).strip() or "/",
            "profiles": sorted(self._profiles()),
            "hookScope": hook_scope,
        }
        if section_key:
            context["sectionKey"] = section_key
        if slot_key:
            context["slotKey"] = slot_key
        parts = [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in context.items()]
        runtime_pairs = self._hook_runtime_context_pairs(page)
        if runtime_pairs:
            runtime_body = ", ".join(f"{key}: {expr}" for key, expr in runtime_pairs)
            parts.append(f"runtime: {{ {runtime_body} }}")
        return ":context='{ " + ", ".join(parts) + " }'"

    def _hook_context_schema(
        self,
        page: dict[str, Any],
        hook_scope: str,
    ) -> dict[str, list[str]]:
        static_fields = ["pageKey", "pageName", "pagePath", "profiles", "hookScope"]
        if hook_scope in {"section", "slot"}:
            static_fields.append("sectionKey")
        if hook_scope == "slot":
            static_fields.append("slotKey")
        runtime_fields = [key for key, _ in self._hook_runtime_context_pairs(page)]
        return {"static": static_fields, "runtime": runtime_fields}

    def _section_hook_mappings(
        self,
        page: dict[str, Any],
        content: str,
    ) -> list[tuple[str, str, str]]:
        page_path = str(page.get("path", "")).strip() or "/"
        mappings: list[tuple[str, str, str]] = []
        if 'class="ecom-home"' in content:
            mappings.extend(
                [
                    ('    <header class="ec-header" data-ecom="Header">', "header", "header"),
                    ('    <section class="ec-banner" data-ecom="Banner">', "banner", "section"),
                    ('    <section class="ec-service-strip">', "service-strip", "section"),
                    ('    <section class="ec-categories" data-ecom="CategoryNav">', "filters", "section"),
                    ('    <section class="ec-products" data-ecom="ProductGrid">', "hot-products", "section"),
                    ('    <section class="ec-products">', "recommend-products", "section"),
                    ('    <section class="ec-shops">', "shops", "section"),
                ]
            )
        elif page_path in {"/", "/about", "/features", "/pricing", "/contact"}:
            mappings.extend(
                [
                    ('    <section id="hero" class="landing-hero" data-landing="Hero">', "hero", "section"),
                    ('    <section id="about" class="landing-section about-section" data-landing="About">', "about", "section"),
                    ('    <section id="features" class="landing-section" data-landing="FeatureGrid">', "features", "section"),
                    ('    <section id="portfolio" class="landing-section" data-landing="Portfolio">', "portfolio", "section"),
                    ('    <section id="pricing" class="landing-section" data-landing="Pricing">', "pricing", "section"),
                    ('    <section id="testimonials" class="landing-section" data-landing="Testimonial">', "testimonials", "section"),
                    ('    <section id="faq" class="landing-section" data-landing="FAQ">', "faq", "section"),
                    ('    <section id="contact" class="landing-section" data-landing="Contact">', "contact", "section"),
                    ('    <section id="cta" class="landing-section cta" data-landing="CTA">', "cta", "section"),
                    ('    <footer id="footer" class="landing-footer" data-landing="Footer">', "footer", "footer"),
                ]
            )
        if page_path == "/search":
            mappings.extend(
                [
                    ('    <header class="search-hero">', "hero", "header"),
                    ('    <section class="search-surface">', "surface", "section"),
                ]
            )
        if page_path == "/category/:name":
            mappings.extend(
                [
                    ('    <header class="category-hero">', "hero", "header"),
                    ('    <section class="category-surface">', "surface", "section"),
                ]
            )
        if page_path == "/shop/:id":
            mappings.extend(
                [
                    ('    <header class="shop-hero">', "hero", "header"),
                    ('    <section class="shop-surface">', "surface", "section"),
                    ('    <section v-if="sourceDiscoveryLabel" class="shop-discovery-bridge">', "discovery-bridge", "section"),
                    ('    <section>\n      <div class="section-head">\n        <div>\n          <h3>店铺商品</h3>', "shop-products", "section"),
                    ('    <section>\n      <div class="section-head">\n        <div>\n          <h3>跨店推荐区</h3>', "recommendations", "section"),
                ]
            )
        if page_path == "/product/:id":
            mappings.extend(
                [
                    ('    <header class="topbar">', "topbar", "header"),
                    ('      <div class="media-panel">', "media", "div"),
                    ('        <section v-if="sourceShopId" class="source-shop-block">', "source-shop", "section"),
                    ('        <section class="purchase-panel">', "purchase", "section"),
                    ('        <section v-if="showAddFeedback" class="add-feedback">', "add-feedback", "section"),
                    ('        <div class="detail-block">', "detail", "div"),
                    ('    <section v-if="related.length > 0" class="related">', "related", "section"),
                ]
            )
        if page_path == "/cart":
            mappings.extend(
                [
                    ('    <header class="cart-hero">', "hero", "header"),
                    ('    <section class="checkout-step-strip">', "steps", "section"),
                    ('    <section class="service-strip">', "service-strip", "section"),
                    ('    <section v-if="sourceProductTitle" class="product-handoff">', "product-handoff", "section"),
                    ('    <section v-if="sourceDiscoveryLabel" class="cart-discovery-bridge">', "discovery-memory", "section"),
                    ('    <section v-if="sourceProductTitle || sourceDiscoveryLabel" class="purchase-axis-bridge">', "purchase-axis", "section"),
                    ('    <div class="cart-layout">', "cart-layout", "div"),
                    ('      <aside class="summary-panel">', "summary-panel", "aside"),
                ]
            )
        if page_path == "/checkout":
            mappings.extend(
                [
                    ('    <header class="checkout-hero">', "hero", "header"),
                    ('    <section class="checkout-step-strip">', "steps", "section"),
                    ('    <section class="service-strip">', "service-strip", "section"),
                    ('    <section v-if="sourceProductTitle" class="checkout-handoff">', "checkout-handoff", "section"),
                    ('    <section v-if="sourceDiscoveryLabel" class="checkout-discovery-bridge">', "discovery-memory", "section"),
                    ('    <section v-if="sourceProductTitle || sourceDiscoveryLabel" class="checkout-axis-bridge">', "purchase-axis", "section"),
                    ('    <section v-if="recentOrder" class="completion-banner">', "completion-banner", "section"),
                    ('    <section v-if="recentOrder" class="completion-axis-bridge">', "return-axis", "section"),
                    ('    <section v-if="recentOrder" class="completion-followup">', "followup", "section"),
                    ('    <article class="address">', "address", "article"),
                    ('    <article class="payment">', "payment", "article"),
                    ('    <aside class="checkout-summary">', "summary-panel", "aside"),
                    ('    <footer class="summary">', "summary-footer", "footer"),
                ]
            )
        if page_path == "/after-sales":
            mappings.extend(
                [
                    ('    <div class="context-grid">', "context", "div"),
                    ('    <section class="progress-board">', "case-status", "section"),
                    ('    <section class="flow-board">', "case-flow", "section"),
                    ('    <section class="ops-board">', "case-ops", "section"),
                    ('    <section class="history-board">', "case-history", "section"),
                    ('    <div class="cards">', "actions", "div"),
                    ('    <section v-if="activePanel" class="panel">', "active-panel", "section"),
                    ('    <section class="timeline">', "timeline", "section"),
                    ('    <section class="materials">', "materials", "section"),
                    ('    <footer class="actions">', "footer-actions", "footer"),
                ]
            )
        return mappings

    def _slot_hook_mappings(
        self,
        page: dict[str, Any],
    ) -> list[tuple[str, str, str, str]]:
        page_path = str(page.get("path", "")).strip() or "/"
        mappings: list[tuple[str, str, str, str]] = []
        if page_path == "/product/:id":
            mappings.extend(
                [
                    ('          <div class="purchase-strip">', "purchase", "purchase-strip", "div"),
                    ('          <div class="field-grid">', "purchase", "field-grid", "div"),
                    ('          <div class="decision-grid">', "purchase", "decision-grid", "div"),
                    ('          <div class="actions">', "purchase", "actions", "div"),
                ]
            )
        if page_path == "/checkout":
            mappings.extend(
                [
                    ('      <div class="completion-axis-flow">', "return-axis", "return-flow", "div"),
                    ('      <div class="completion-followup-actions">', "followup", "followup-actions", "div"),
                ]
            )
        if page_path == "/after-sales":
            mappings.extend(
                [
                    ('    <div class="action-entry-strip">', "actions", "entry-strip", "div"),
                    ('    <div class="cards">', "actions", "cards", "div"),
                    ('      <div class="panel-head">', "active-panel", "panel-head", "div"),
                    ('    <div class="panel-support-strip">', "active-panel", "panel-support-strip", "div"),
                    ('      <div class="timeline-grid">', "timeline", "timeline-grid", "div"),
                    ('      <div class="materials-grid">', "materials", "materials-grid", "div"),
                    ('    <div class="support-footer-strip">', "footer-actions", "support-footer-strip", "div"),
                ]
            )
        if page_path in {"/", "/about", "/features", "/pricing", "/contact"}:
            mappings.extend(
                [
                    ('      <div class="hero-brand-grid">', "hero", "brand-grid", "div"),
                    ('      <div class="hero-actions">', "hero", "hero-actions", "div"),
                    ('      <div class="quote-grid">', "testimonials", "quote-grid", "div"),
                    ('      <div class="faq-scan-strip">', "faq", "scan-strip", "div"),
                    ('      <div class="contact-form-shell contact-form-shell--business">', "contact", "form-shell", "div"),
                    ('      <div class="cta-capture-strip">', "cta", "capture-strip", "div"),
                    ('      <div class="cta-close-strip">', "cta", "close-strip", "div"),
                    ('      <div v-if="contactSent && !personalPortfolioMode" class="footer-success-bridge">', "footer", "success-bridge", "div"),
                ]
            )
        return mappings

    def _page_hook_catalog_entry(
        self,
        page: dict[str, Any],
        content: str,
    ) -> dict[str, Any]:
        page_key = self._page_hook_key(page)
        section_mappings = self._section_hook_mappings(page, content)
        slot_mappings = self._slot_hook_mappings(page)
        return {
            "pageKey": page_key,
            "pageName": str(page.get("name", "")).strip() or "Page",
            "pagePath": str(page.get("path", "")).strip() or "/",
            "pageHooks": [f"page.{page_key}.before", f"page.{page_key}.after"],
            "sectionHooks": [
                {
                    "sectionKey": section_key,
                    "hooks": [
                        f"page.{page_key}.section.{section_key}.before",
                        f"page.{page_key}.section.{section_key}.after",
                    ],
                }
                for _, section_key, _ in section_mappings
            ],
            "slotHooks": [
                {
                    "sectionKey": section_key,
                    "slotKey": slot_key,
                    "hooks": [
                        f"page.{page_key}.section.{section_key}.slot.{slot_key}.before",
                        f"page.{page_key}.section.{section_key}.slot.{slot_key}.after",
                    ],
                }
                for _, section_key, slot_key, _ in slot_mappings
            ],
            "context": {
                "page": self._hook_context_schema(page, "page"),
                "section": self._hook_context_schema(page, "section"),
                "slot": self._hook_context_schema(page, "slot"),
            },
        }

    def _write_hook_catalog(
        self,
        project_root: Path,
        entries: list[dict[str, Any]],
    ) -> None:
        ail_dir = project_root / ".ail"
        ail_dir.mkdir(parents=True, exist_ok=True)
        json_path = ail_dir / "hook_catalog.json"
        md_path = ail_dir / "hook_catalog.md"
        payload = {"status": "ok", "generated_at": datetime.now().isoformat(), "pages": entries}
        self._safe_write_text(json_path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

        lines = [
            "# AIL Hook Catalog",
            "",
            "This file is generated. It lists the durable page / section / slot hook points currently available in this project.",
            "",
            "Use these together with:",
            "",
            "- `.ail/source.ail` for structural/content changes",
            "- `frontend/src/ail-overrides/theme.tokens.css` for theme tokens",
            "- `frontend/src/ail-overrides/custom.css` for local CSS overrides",
            "- `frontend/src/ail-overrides/components/**` for durable Vue/HTML hook inserts",
            "",
        ]
        for entry in entries:
            lines.extend(
                [
                    f"## {entry['pageName']} `{entry['pagePath']}`",
                    "",
                    f"- page key: `{entry['pageKey']}`",
                    "- page hooks:",
                ]
            )
            for hook_name in entry["pageHooks"]:
                lines.append(f"  - `{hook_name}`")
            section_hooks = entry["sectionHooks"]
            if section_hooks:
                lines.append("- section hooks:")
                for item in section_hooks:
                    lines.append(f"  - `{item['sectionKey']}`")
                    for hook_name in item["hooks"]:
                        lines.append(f"    - `{hook_name}`")
            slot_hooks = entry["slotHooks"]
            if slot_hooks:
                lines.append("- slot hooks:")
                for item in slot_hooks:
                    lines.append(f"  - `{item['sectionKey']}` / `{item['slotKey']}`")
                    for hook_name in item["hooks"]:
                        lines.append(f"    - `{hook_name}`")
            lines.append("- context fields:")
            lines.append(
                "  - page: "
                + ", ".join(f"`{field}`" for field in entry["context"]["page"]["static"])
            )
            if entry["context"]["page"]["runtime"]:
                lines.append(
                    "  - runtime: "
                    + ", ".join(f"`{field}`" for field in entry["context"]["page"]["runtime"])
                )
            if entry["context"]["section"]["static"]:
                lines.append(
                    "  - section: "
                    + ", ".join(f"`{field}`" for field in entry["context"]["section"]["static"])
                )
            if entry["context"]["slot"]["static"]:
                lines.append(
                    "  - slot: "
                    + ", ".join(f"`{field}`" for field in entry["context"]["slot"]["static"])
                )
            lines.append("")
        self._safe_write_text(md_path, "\n".join(lines))

    @staticmethod
    def _find_block_end(content: str, start_idx: int, tag_name: str) -> int | None:
        pattern = re.compile(rf"<(/?){tag_name}\b", re.IGNORECASE)
        depth = 0
        for match in pattern.finditer(content, start_idx):
            is_closing = bool(match.group(1))
            tag_close = content.find(">", match.start())
            if tag_close == -1:
                return None
            if not is_closing:
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    return tag_close + 1
        return None

    def _inject_named_block_hooks(
        self,
        page: dict[str, Any],
        content: str,
        page_hook_key: str,
        mappings: list[tuple[str, str, str]],
    ) -> str:
        inserts: list[tuple[int, str]] = []
        for anchor, section_key, tag_name in mappings:
            start_idx = content.find(anchor)
            if start_idx == -1:
                continue
            end_idx = self._find_block_end(content, start_idx, tag_name)
            if end_idx is None:
                continue
            line_start = content.rfind("\n", 0, start_idx) + 1
            indent = content[line_start:start_idx]
            before_context_attr = self._hook_context_attr(page, "section", section_key=section_key)
            after_context_attr = before_context_attr
            before_hook = f'{indent}<AILSlotHost name="page.{page_hook_key}.section.{section_key}.before" {before_context_attr} />\n'
            after_hook = f'\n{indent}<AILSlotHost name="page.{page_hook_key}.section.{section_key}.after" {after_context_attr} />'
            inserts.append((start_idx, before_hook))
            inserts.append((end_idx, after_hook))
        for insert_idx, snippet in sorted(inserts, key=lambda item: item[0], reverse=True):
            content = content[:insert_idx] + snippet + content[insert_idx:]
        return content

    def _inject_named_slot_hooks(
        self,
        page: dict[str, Any],
        content: str,
        page_hook_key: str,
        mappings: list[tuple[str, str, str, str]],
    ) -> str:
        inserts: list[tuple[int, str]] = []
        for anchor, section_key, slot_key, tag_name in mappings:
            start_idx = content.find(anchor)
            if start_idx == -1:
                continue
            end_idx = self._find_block_end(content, start_idx, tag_name)
            if end_idx is None:
                continue
            line_start = content.rfind("\n", 0, start_idx) + 1
            indent = content[line_start:start_idx]
            context_attr = self._hook_context_attr(
                page,
                "slot",
                section_key=section_key,
                slot_key=slot_key,
            )
            before_hook = (
                f'{indent}<AILSlotHost '
                f'name="page.{page_hook_key}.section.{section_key}.slot.{slot_key}.before" {context_attr} />\n'
            )
            after_hook = (
                f'\n{indent}<AILSlotHost '
                f'name="page.{page_hook_key}.section.{section_key}.slot.{slot_key}.after" {context_attr} />'
            )
            inserts.append((start_idx, before_hook))
            inserts.append((end_idx, after_hook))
        for insert_idx, snippet in sorted(inserts, key=lambda item: item[0], reverse=True):
            content = content[:insert_idx] + snippet + content[insert_idx:]
        return content

    def _inject_section_slot_hosts(self, page: dict[str, Any], content: str) -> str:
        page_hook_key = self._page_hook_key(page)
        mappings = self._section_hook_mappings(page, content)
        if not mappings:
            return content
        return self._inject_named_block_hooks(page, content, page_hook_key, mappings)

    def _inject_slot_slot_hosts(self, page: dict[str, Any], content: str) -> str:
        page_hook_key = self._page_hook_key(page)
        mappings = self._slot_hook_mappings(page)
        if not mappings:
            return content
        return self._inject_named_slot_hooks(page, content, page_hook_key, mappings)

    def _inject_page_slot_hosts(self, page: dict[str, Any], content: str) -> str:
        if "<template>\n" not in content or "\n</template>" not in content:
            return content
        hook_key = self._page_hook_key(page)
        page_context_attr = self._hook_context_attr(page, "page")
        before_hook = f'  <AILSlotHost name="page.{hook_key}.before" {page_context_attr} />\n'
        after_hook = f'  <AILSlotHost name="page.{hook_key}.after" {page_context_attr} />\n'
        content = content.replace("<template>\n", "<template>\n" + before_hook, 1)
        content = content.replace("\n</template>", "\n" + after_hook + "</template>", 1)
        return content

    def _write_frontend_entry_files(self, project_root: Path, frontend_dir: Path) -> None:
        self._safe_write_managed_text(
            project_root,
            frontend_dir / "src" / "main.ts",
            (
                'import { createApp } from "vue";\n'
                'import "./style.css";\n'
                'import "./ail-overrides/theme.tokens.css";\n'
                'import "./ail-overrides/custom.css";\n'
                'import App from "./App.vue";\n'
                'import AILSlotHost from "./ail-managed/system/AILSlotHost.vue";\n'
                'import router from "@/router";\n'
                "\n"
                "const app = createApp(App);\n"
                'app.component("AILSlotHost", AILSlotHost);\n'
                "app.use(router);\n"
                'app.mount("#app");\n'
            ),
        )
        self._safe_write_managed_text(
            project_root,
            frontend_dir / "src" / "main.js",
            (
                'import { createApp } from "vue";\n'
                'import "./style.css";\n'
                'import "./ail-overrides/theme.tokens.css";\n'
                'import "./ail-overrides/custom.css";\n'
                'import App from "./App.vue";\n'
                'import AILSlotHost from "./ail-managed/system/AILSlotHost.vue";\n'
                'import router from "./router"\n'
                "\n"
                "const app = createApp(App)\n"
                'app.component("AILSlotHost", AILSlotHost)\n'
                "app.use(router)\n"
                'app.mount("#app")\n'
            ),
        )

    def _reset_frontend_managed_zones(self, frontend_dir: Path) -> None:
        # Keep managed roots in place so rebuilds can detect drift and back up
        # overwritten files before writing fresh generated content.
        for path in (
            frontend_dir / "src" / "views",
            frontend_dir / "src" / "ail-managed" / "views",
            frontend_dir / "src" / "ail-managed" / "router",
            frontend_dir / "src" / "ail-managed" / "system",
            frontend_dir / "src" / "router",
        ):
            path.mkdir(parents=True, exist_ok=True)
        router_dir = frontend_dir / "src" / "router"
        for filename in ("routes.generated.ts", "roles.generated.ts"):
            target = router_dir / filename
            if target.exists():
                try:
                    target.unlink()
                except OSError as exc:
                    raise RuntimeError(f"Failed to remove managed router file: {target} ({exc})") from exc

    @staticmethod
    def _parse_component_config(config: str) -> dict[str, str]:
        props: dict[str, str] = {}
        text = str(config or "").strip()
        if not text:
            return props

        parts: list[str] = []
        current: list[str] = []
        quote_char = None
        escape = False
        round_depth = 0
        square_depth = 0
        curly_depth = 0

        for char in text:
            if quote_char is not None:
                current.append(char)
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == quote_char:
                    quote_char = None
                continue

            if char in {'"', "'"}:
                quote_char = char
                current.append(char)
                continue

            if char == "(":
                round_depth += 1
            elif char == ")":
                round_depth = max(0, round_depth - 1)
            elif char == "[":
                square_depth += 1
            elif char == "]":
                square_depth = max(0, square_depth - 1)
            elif char == "{":
                curly_depth += 1
            elif char == "}":
                curly_depth = max(0, curly_depth - 1)

            if char == "," and round_depth == 0 and square_depth == 0 and curly_depth == 0:
                part = "".join(current).strip()
                if part:
                    parts.append(part)
                current = []
                continue

            current.append(char)

        tail = "".join(current).strip()
        if tail:
            parts.append(tail)

        for part in parts:
            separator_index = -1
            quote_char = None
            escape = False
            round_depth = 0
            square_depth = 0
            curly_depth = 0
            for index, char in enumerate(part):
                if quote_char is not None:
                    if escape:
                        escape = False
                    elif char == "\\":
                        escape = True
                    elif char == quote_char:
                        quote_char = None
                    continue

                if char in {'"', "'"}:
                    quote_char = char
                    continue

                if char == "(":
                    round_depth += 1
                elif char == ")":
                    round_depth = max(0, round_depth - 1)
                elif char == "[":
                    square_depth += 1
                elif char == "]":
                    square_depth = max(0, square_depth - 1)
                elif char == "{":
                    curly_depth += 1
                elif char == "}":
                    curly_depth = max(0, curly_depth - 1)

                if char in {":", "="} and round_depth == 0 and square_depth == 0 and curly_depth == 0:
                    separator_index = index
                    break

            if separator_index >= 0:
                key = part[:separator_index].strip()
                value = part[separator_index + 1 :].strip()
                props[key] = value
            else:
                props[part] = "true"
        return props

    @staticmethod
    def _load_profile_dictionary(profile_name: str) -> dict[str, Any]:
        dict_path = Path(__file__).with_name("profile_dicts") / f"{profile_name}_profile_v1.json"
        if not dict_path.exists():
            return {}
        try:
            return json.loads(dict_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _pick_home_page(self, pages: list[dict[str, Any]]) -> dict[str, Any] | None:
        for page in pages:
            if str(page.get("name", "")).strip().lower() == "home":
                return page
        for page in pages:
            if str(page.get("path", "")).strip() == "/":
                return page
        return pages[0] if pages else None

    def _profiles(self) -> set[str]:
        raw_profiles = self.ast.get("profiles", [])
        if not isinstance(raw_profiles, list):
            return set()
        profiles: set[str] = set()
        for item in raw_profiles:
            profile_name = str(item).strip().lower()
            if profile_name:
                profiles.add(profile_name)
        return profiles

    def _frontend_pages(self) -> list[dict[str, Any]]:
        pages = super()._frontend_pages()
        if "ecom_min" not in self._profiles():
            return pages

        existing_paths = {
            str(page.get("path", "")).strip()
            for page in pages
            if isinstance(page, dict)
        }
        implicit_pages = [
            {
                "name": "Category",
                "path": "/category/:name",
                "components": [{"source": "ecom", "name": "CategoryGrid", "config": ""}],
            },
            {
                "name": "Shop",
                "path": "/shop/:id",
                "components": [{"source": "ecom", "name": "ShopHeader", "config": ""}],
            },
            {
                "name": "Search",
                "path": "/search",
                "components": [{"source": "ecom", "name": "SearchResultGrid", "config": ""}],
            },
        ]
        missing_pages = [
            page for page in implicit_pages
            if str(page.get("path", "")).strip() not in existing_paths
        ]
        return pages + missing_pages

    def _ensure_primary_keys(self) -> None:
        raw_database = self.ast.get("database")
        if not isinstance(raw_database, dict):
            return

        for _, fields in raw_database.items():
            if not isinstance(fields, dict):
                continue
            fields["id"] = "int"

    def _database_schema(self) -> dict[str, dict[str, str]]:
        schema = super()._database_schema()
        for fields in schema.values():
            fields.pop("id", None)
        return schema

    def _write_generated_routes(self, project_root: Path, frontend_dir: Path, pages: list[dict[str, Any]]) -> None:
        router_dir = frontend_dir / "src" / "router"
        managed_router_dir = frontend_dir / "src" / "ail-managed" / "router"
        routes_path = router_dir / "routes.generated.ts"
        managed_routes_path = managed_router_dir / "routes.generated.ts"
        routes: list[dict[str, str]] = []

        for page in pages:
            page_name = str(page.get("name", "")).strip() or "Page"
            page_path = str(page.get("path", "")).strip() or "/"
            if not page_path.startswith("/"):
                page_path = f"/{page_path}"
            view_name = self._sanitize_file_stem(page_name)
            routes.append({"path": page_path, "name": page_name, "view": view_name})

        if not routes:
            routes.append({"path": "/", "name": "Home", "view": "Home"})

        lines = ["export const routes = ["]
        for route in routes:
            lines.append(
                f'  {{ path: {json.dumps(route["path"])}, '
                f'name: {json.dumps(route["name"])}, '
                f'component: () => import("@/ail-managed/views/{route["view"]}.vue") }},'
            )
        lines.append("];")
        content = "\n".join(lines) + "\n"
        self._safe_write_managed_text(project_root, routes_path, content)
        self._safe_write_managed_text(project_root, managed_routes_path, content)

    def _build_roles_and_nav_pages(
        self,
        pages: list[dict[str, Any]],
    ) -> tuple[dict[str, str], list[dict[str, Any]]]:
        has_auth = self._has_login_api()
        role_required: dict[str, str] = {}
        nav_pages: list[dict[str, Any]] = []
        seen_paths: set[str] = set()

        for page in pages:
            path = str(page.get("path", "")).strip()
            label = str(page.get("name", "")).strip() or "Page"
            page_role = str(page.get("page_role", "")).strip().lower()

            if not path.startswith("/") or path == "/" or path in seen_paths:
                continue
            seen_paths.add(path)

            if page_role:
                role_required[path] = page_role
                nav_pages.append({"path": path, "label": label, "role": page_role})
                continue

            if path in {"/login", "/403"}:
                nav_pages.append({"path": path, "label": label, "public": True})
                continue

            if has_auth:
                nav_pages.append({"path": path, "label": label, "requiresAuth": True})
            else:
                nav_pages.append({"path": path, "label": label, "public": True})

        return role_required, nav_pages

    def _write_generated_roles(self, project_root: Path, frontend_dir: Path, pages: list[dict[str, Any]]) -> None:
        router_dir = frontend_dir / "src" / "router"
        managed_router_dir = frontend_dir / "src" / "ail-managed" / "router"
        roles_path = router_dir / "roles.generated.ts"
        managed_roles_path = managed_router_dir / "roles.generated.ts"
        role_required, nav_pages = self._build_roles_and_nav_pages(pages)
        lines: list[str] = ["export const roleRequired: Record<string, string> = {"]
        for path, required_role in role_required.items():
            lines.append(f"  {json.dumps(path, ensure_ascii=False)}: {json.dumps(required_role, ensure_ascii=False)},")
        lines.append("};")
        lines.append("")
        lines.append("export type NavPage = {")
        lines.append("  path: string;")
        lines.append("  label: string;")
        lines.append("  public?: boolean;")
        lines.append("  requiresAuth?: boolean;")
        lines.append("  role?: string;")
        lines.append("};")
        lines.append("")
        lines.append("export const navPages: NavPage[] = [")
        for page in nav_pages:
            parts = [
                f'path: {json.dumps(str(page.get("path", "")), ensure_ascii=False)}',
                f'label: {json.dumps(str(page.get("label", "")), ensure_ascii=False)}',
            ]
            if bool(page.get("public", False)):
                parts.append("public: true")
            if bool(page.get("requiresAuth", False)):
                parts.append("requiresAuth: true")
            role = str(page.get("role", "")).strip()
            if role:
                parts.append(f"role: {json.dumps(role, ensure_ascii=False)}")
            lines.append(f"  {{ {', '.join(parts)} }},")
        lines.append("];")
        content = "\n".join(lines) + "\n"
        self._safe_write_managed_text(project_root, roles_path, content)
        self._safe_write_managed_text(project_root, managed_roles_path, content)

    def _write_router_index_with_guard(self, project_root: Path, frontend_dir: Path, pages: list[dict[str, Any]]) -> None:
        router_dir = frontend_dir / "src" / "router"
        index_ts_path = router_dir / "index.ts"
        auth_enabled_literal = "true" if self._has_login_api() else "false"

        content = (
            'import { createRouter, createWebHistory } from "vue-router";\n'
            'import { routes as generatedRoutes } from "@/ail-managed/router/routes.generated";\n'
            'import { roleRequired } from "@/ail-managed/router/roles.generated";\n'
            "\n"
            "const fallback = [\n"
            '  { path: "/", name: "Home", component: () => import("@/ail-managed/views/Home.vue") },\n'
            "];\n"
            "\n"
            "const routes = generatedRoutes?.length ? generatedRoutes : fallback;\n"
            "let cachedRole: string | null = null;\n"
            "let cachedToken: string | null = null;\n"
            f"const authEnabled = {auth_enabled_literal};\n"
            "\n"
            "const router = createRouter({\n"
            "  history: createWebHistory(),\n"
            "  routes,\n"
            "});\n"
            "\n"
            "router.beforeEach(async (to, _from, next) => {\n"
            '  const token = localStorage.getItem("token") || localStorage.getItem("access_token");\n'
            '  if (authEnabled && !token && to.path !== "/" && to.path !== "/login" && to.path !== "/403") {\n'
            '    next("/login");\n'
            "    return;\n"
            "  }\n"
            "  const requiredRole = roleRequired[to.path];\n"
            "  if (authEnabled && token && requiredRole) {\n"
            "    try {\n"
            "      if (cachedToken !== token) {\n"
            "        cachedToken = token;\n"
            "        cachedRole = null;\n"
            "      }\n"
            "      if (!cachedRole) {\n"
            "        const response = await fetch('/api/me', { headers: { Authorization: `Bearer ${token}` } });\n"
            "        if (!response.ok) {\n"
            '          next("/403");\n'
            "          return;\n"
            "        }\n"
            "        const data = await response.json().catch(() => ({}));\n"
            "        cachedRole = typeof data?.role === 'string' ? data.role.toLowerCase() : 'user';\n"
            "      }\n"
            "      const allowedRoles = String(requiredRole)\n"
            "        .split('|')\n"
            "        .map((r) => r.trim().toLowerCase())\n"
            "        .filter(Boolean);\n"
            "      if (!allowedRoles.includes(String(cachedRole || '').toLowerCase())) {\n"
            '        next("/403");\n'
            "        return;\n"
            "      }\n"
            "    } catch (_error) {\n"
            '      next("/403");\n'
            "      return;\n"
            "    }\n"
            "  }\n"
            "  if (authEnabled && !token) {\n"
            "    cachedRole = null;\n"
            "    cachedToken = null;\n"
            "  }\n"
            "  next();\n"
            "});\n"
            "\n"
            "export default router;\n"
        )
        self._safe_write_managed_text(project_root, index_ts_path, content)

    @staticmethod
    def _ensure_forbidden_page(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for page in pages:
            page_name = str(page.get("name", "")).strip().lower()
            page_path = str(page.get("path", "")).strip()
            if page_path == "/403" or page_name == "forbidden":
                return pages
        return pages + [{"name": "Forbidden", "path": "/403", "components": []}]

    def _write_start_script(self, project_root: Path) -> None:
        lines = [
            "#!/bin/bash",
            "set -euo pipefail",
            "",
            'echo "🚀 正在点燃 AIL 全栈引擎..."',
            'cd "$(dirname "$0")"',
            "",
            'if [ -n "${BACKEND_PORT:-}" ]; then',
            '  BACKEND_SOURCE="env"',
            "else",
            '  BACKEND_SOURCE="default"',
            "fi",
            'if [ -n "${FRONTEND_PORT:-}" ]; then',
            '  FRONTEND_SOURCE="env"',
            "else",
            '  FRONTEND_SOURCE="default"',
            "fi",
            'BACKEND_PORT="${BACKEND_PORT:-8000}"',
            'FRONTEND_PORT="${FRONTEND_PORT:-5173}"',
            'echo "BACKEND_PORT=${BACKEND_PORT} (source=${BACKEND_SOURCE})"',
            'echo "FRONTEND_PORT=${FRONTEND_PORT} (source=${FRONTEND_SOURCE})"',
            "MAX_FRONTEND_PORT_TRIES=20",
            "",
            "is_port_in_use() {",
            '  lsof -tiTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1',
            "}",
            "",
            'SELECTED_FRONTEND_PORT=""',
            "for offset in $(seq 0 $((MAX_FRONTEND_PORT_TRIES - 1))); do",
            "  candidate_port=$((FRONTEND_PORT + offset))",
            '  if ! is_port_in_use "${candidate_port}"; then',
            '    SELECTED_FRONTEND_PORT="${candidate_port}"',
            "    break",
            "  fi",
            "done",
            "",
            'if [ -z "${SELECTED_FRONTEND_PORT}" ]; then',
            '  echo "❌ 未找到可用前端端口：${FRONTEND_PORT}-$((FRONTEND_PORT + MAX_FRONTEND_PORT_TRIES - 1))"',
            "  exit 1",
            "fi",
            "",
            "(",
            "  cd backend",
            '  uvicorn main:app --reload --port "${BACKEND_PORT}" >/tmp/ail_uvicorn.log 2>&1',
            ") &",
            "BACKEND_PID=$!",
            'echo "🛰️ 后端已启动，PID: ${BACKEND_PID}"',
            "",
            "(",
            "  cd frontend",
            '  node ./node_modules/vite/bin/vite.js --host 0.0.0.0 --port "${SELECTED_FRONTEND_PORT}" >/tmp/ail_vite.log 2>&1',
            ") &",
            "FRONTEND_PID=$!",
            'echo "🎨 前端已启动，PID: ${FRONTEND_PID}"',
            'echo "FRONTEND_URL=http://127.0.0.1:${SELECTED_FRONTEND_PORT}"',
            'echo "BACKEND_URL=http://127.0.0.1:${BACKEND_PORT}"',
            "",
            "CLEANED_UP=0",
            "",
            "cleanup() {",
            '  if [ "${CLEANED_UP}" = "1" ]; then',
            "    return",
            "  fi",
            "  CLEANED_UP=1",
            '  echo ""',
            '  echo "🛑 捕获退出信号，正在优雅关闭前后端进程..."',
            "  kill \"${BACKEND_PID}\" \"${FRONTEND_PID}\" 2>/dev/null || true",
            "  wait \"${BACKEND_PID}\" \"${FRONTEND_PID}\" 2>/dev/null || true",
            '  echo "✅ 全栈引擎已安全熄火。"',
            "}",
            "",
            "trap cleanup SIGINT SIGTERM EXIT",
            "wait",
        ]

        script_path = project_root / "start.sh"
        self._safe_write_text(script_path, "\n".join(lines) + "\n")
        script_path.chmod(0o755)

    @staticmethod
    def _extract_openapi_paths_from_main(main_content: str) -> list[str]:
        paths = re.findall(r'@app\.(?:get|post|put|patch|delete)\("([^"]+)"\)', main_content)
        return list(dict.fromkeys(paths))

    def _write_verify_api_script(self, project_root: Path, openapi_paths: list[str]) -> None:
        has_register = "/api/register" in openapi_paths
        has_login = "/api/login" in openapi_paths
        has_tools = "/api/tools" in openapi_paths
        has_me = "/api/me" in openapi_paths
        script_path = project_root / "verify_api.sh"
        admin_endpoint = next((path for path in openapi_paths if "admin" in path.lower()), "")
        or_role_api_endpoint = ""
        for api in self._backend_apis():
            route = str(api.get("route", "")).strip()
            auth_role = str(api.get("auth_role", "")).strip()
            if route.startswith("/api/") and "|" in auth_role:
                or_role_api_endpoint = route
                break

        if not (has_register and has_login):
            lines = [
                "#!/bin/bash",
                "set -euo pipefail",
                "",
                'echo "No auth endpoints detected for API regression script."',
                f'echo "Detected paths: {", ".join(openapi_paths) if openapi_paths else "(none)"}"',
                'echo "Expected: /api/register, /api/login"',
                "exit 0",
            ]
            self._safe_write_text(script_path, "\n".join(lines) + "\n")
            script_path.chmod(0o755)
            return

        lines = [
            "#!/bin/bash",
            "set -euo pipefail",
            'cd "$(dirname "$0")"',
            "",
            'echo "=========================================="',
            'echo " API Regression Test"',
            'echo "=========================================="',
            "",
            'BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"',
            f'ADMIN_ENDPOINT="{admin_endpoint}"',
            f'OR_ROLE_API_ENDPOINT="{or_role_api_endpoint}"',
            f'HAS_ME_ENDPOINT={"1" if has_me else "0"}',
            f'HAS_TOOLS_ENDPOINT={"1" if has_tools else "0"}',
            'USERNAME="ais_user_$(date +%s)"',
            'PASSWORD="123456"',
            "",
            'echo "Base URL: ${BASE_URL}"',
            'echo "Username: ${USERNAME}"',
            "",
            "register_ok=0",
            "for attempt in 1 2 3; do",
            '  REGISTER_STATUS=$(curl -s -o /tmp/register_resp.json -w "%{http_code}" \\',
            '    -H "Content-Type: application/json" \\',
            '    -d "{\\"username\\":\\"${USERNAME}\\",\\"password\\":\\"${PASSWORD}\\"}" \\',
            '    "${BASE_URL}/api/register")',
            '  echo "[register attempt ${attempt}] status=${REGISTER_STATUS} resp=$(cat /tmp/register_resp.json)"',
            '  if [ "${REGISTER_STATUS}" = "200" ] || [ "${REGISTER_STATUS}" = "201" ]; then',
            "    register_ok=1",
            "    break",
            "  fi",
            '  if [ "${REGISTER_STATUS}" = "409" ]; then',
            '    USERNAME="ais_user_$(date +%s)_${attempt}"',
            "    sleep 1",
            "    continue",
            "  fi",
            '  echo "❌ register failed: ${REGISTER_STATUS}"',
            "  exit 1",
            "done",
            'if [ "${register_ok}" != "1" ]; then',
            '  echo "❌ register could not succeed after retries"',
            "  exit 1",
            "fi",
            'echo "✅ register ok"',
            "",
            'LOGIN_STATUS=$(curl -s -o /tmp/login_resp.json -w "%{http_code}" \\',
            '  -H "Content-Type: application/json" \\',
            '  -d "{\\"username\\":\\"${USERNAME}\\",\\"password\\":\\"${PASSWORD}\\"}" \\',
            '  "${BASE_URL}/api/login")',
            'LOGIN_BODY=$(cat /tmp/login_resp.json)',
            'echo "[login] status=${LOGIN_STATUS} resp=${LOGIN_BODY}"',
            'if [ "${LOGIN_STATUS}" != "200" ]; then',
            '  echo "❌ login failed"',
            "  exit 1",
            "fi",
            'TOKEN=$(echo "${LOGIN_BODY}" | python3 -c "import sys,json; print(json.load(sys.stdin).get(\'access_token\',\'\'))" 2>/dev/null || echo "")',
            'USER_ID=$(echo "${LOGIN_BODY}" | python3 -c "import sys,json; print(json.load(sys.stdin).get(\'user_id\',\'\'))" 2>/dev/null || echo "")',
            'TOKEN_LEN=${#TOKEN}',
            'if [ "${TOKEN_LEN}" -le 20 ]; then',
            '  echo "❌ token too short: ${TOKEN_LEN}"',
            "  exit 1",
            "fi",
            'if [ -z "${USER_ID}" ]; then',
            '  echo "⚠️ login response missing user_id, fallback to username for role switch checks"',
            "fi",
            'echo "✅ login ok token_len=${TOKEN_LEN} user_id=${USER_ID}"',
            "",
            'if [ "${HAS_ME_ENDPOINT}" = "1" ]; then',
            '  ME_STATUS=$(curl -s -o /tmp/me_resp.json -w "%{http_code}" \\',
            '    -H "Authorization: Bearer ${TOKEN}" \\',
            '    "${BASE_URL}/api/me")',
            '  ME_BODY=$(cat /tmp/me_resp.json)',
            '  echo "[me] status=${ME_STATUS} resp=${ME_BODY}"',
            '  if [ "${ME_STATUS}" != "200" ]; then',
            '    echo "❌ /api/me check failed"',
            "    exit 1",
            "  fi",
            '  ME_ROLE=$(echo "${ME_BODY}" | python3 -c "import sys,json; print((json.load(sys.stdin).get(\'role\',\'\') or \'\').strip().lower())" 2>/dev/null || echo "")',
            '  if [ -n "${ME_ROLE}" ] && [ "${ME_ROLE}" != "user" ]; then',
            '    echo "❌ expected initial /api/me role=user, got ${ME_ROLE}"',
            "    exit 1",
            "  fi",
            "fi",
            "",
            'OR_ROLE_VALUE=""',
            'if [ -f "frontend/src/router/roles.generated.ts" ]; then',
            '  OR_ROLE_VALUE=$(python3 -c "import re,pathlib; p=pathlib.Path(\'frontend/src/router/roles.generated.ts\'); t=p.read_text(encoding=\'utf-8\') if p.exists() else \'\'; m=re.search(r\'\\\"([^\\\"]+\\|[^\\\"]+)\\\"\', t); print(m.group(1) if m else \'\')")',
            "fi",
            'if [ -z "${OR_ROLE_VALUE}" ] && [ -f "backend/main.py" ]; then',
            '  if grep -q "split(\\"|\\")" backend/main.py || grep -q "split(\'|\')" backend/main.py; then',
            '    OR_ROLE_VALUE="admin|ops"',
            "  fi",
            "fi",
            'if [ -n "${OR_ROLE_VALUE}" ]; then',
            '  echo "OR role detected: ${OR_ROLE_VALUE}"',
            '  if [ "${HAS_ME_ENDPOINT}" = "1" ] && [ -f "backend/ail_data.db" ]; then',
            '    ROLE_SWITCH_RESULT=$(python3 - <<PY',
            "import sqlite3",
            "username = '${USERNAME}'",
            "user_id = '${USER_ID}'.strip()",
            "conn = None",
            "try:",
            "    conn = sqlite3.connect('backend/ail_data.db')",
            "    cur = conn.cursor()",
            "    cur.execute('PRAGMA table_info(users)')",
            "    cols = {str(row[1]).strip().lower() for row in cur.fetchall()}",
            "    if 'role' not in cols or ('username' not in cols and 'id' not in cols):",
            "        print('role switch skipped (schema mismatch)')",
            "        raise SystemExit(0)",
            "    print('schema check passed')",
            "    params = []",
            "    where_clause = ''",
            "    strategy = ''",
            "    if user_id:",
            "        try:",
            "            uid = int(user_id)",
            "            where_clause = 'id = ?'",
            "            params = [uid]",
            "            strategy = f'id={uid}'",
            "        except Exception:",
            "            where_clause = ''",
            "            params = []",
            "            strategy = ''",
            "    if not where_clause:",
            "        where_clause = 'username = ?'",
            "        params = [username]",
            "        strategy = f'username={username}'",
            "    cur.execute(f'UPDATE users SET role = ? WHERE {where_clause}', ['ops', *params])",
            "    conn.commit()",
            "    cur.execute(f'SELECT role FROM users WHERE {where_clause} LIMIT 1', params)",
            "    row = cur.fetchone()",
            "    if not row:",
            "        print('role switch skipped (target user not found)')",
            "        raise SystemExit(0)",
            "    current_role = str(row[0] or '').strip().lower()",
            "    if current_role != 'ops':",
            "        print(f'role switch skipped (post-check role={current_role or \"null\"})')",
            "        raise SystemExit(0)",
            "    print(f'role updated to ops ({strategy})')",
            "finally:",
            "    if conn is not None:",
            "        conn.close()",
            "PY",
            "    )",
            '    echo "${ROLE_SWITCH_RESULT}"',
            '    if echo "${ROLE_SWITCH_RESULT}" | grep -q "role updated to ops"; then',
            '      ME_OPS_STATUS=$(curl -s -o /tmp/me_ops_resp.json -w "%{http_code}" \\',
            '        -H "Authorization: Bearer ${TOKEN}" \\',
            '        "${BASE_URL}/api/me")',
            '      ME_OPS_BODY=$(cat /tmp/me_ops_resp.json)',
            '      echo "[me after role switch] status=${ME_OPS_STATUS} resp=${ME_OPS_BODY}"',
            '      if [ "${ME_OPS_STATUS}" != "200" ]; then',
            '        echo "❌ /api/me after role switch failed"',
            "        exit 1",
            "      fi",
            '      ME_OPS_ROLE=$(echo "${ME_OPS_BODY}" | python3 -c "import sys,json; print((json.load(sys.stdin).get(\'role\',\'\') or \'\').strip().lower())" 2>/dev/null || echo "")',
            '      if [ "${ME_OPS_ROLE}" != "ops" ]; then',
            '        echo "❌ expected /api/me role=ops after switch, got ${ME_OPS_ROLE}"',
            "        exit 1",
            "      fi",
            "    else",
            '      echo "OR role auto switch skipped (safe guard)"',
            "    fi",
            "  else",
            '    echo "OR role auto switch skipped (missing /api/me or backend/ail_data.db)"',
            "  fi",
            '  if [ -n "${OR_ROLE_API_ENDPOINT}" ]; then',
            '    OR_ROLE_API_STATUS=$(curl -s -o /tmp/or_role_api_resp.json -w "%{http_code}" \\',
            '      -H "Authorization: Bearer ${TOKEN}" \\',
            '      "${BASE_URL}${OR_ROLE_API_ENDPOINT}")',
            '    echo "[or role api] endpoint=${OR_ROLE_API_ENDPOINT} status=${OR_ROLE_API_STATUS} resp=$(cat /tmp/or_role_api_resp.json)"',
            '    if [ "${OR_ROLE_API_STATUS}" != "200" ]; then',
            '      echo "❌ OR role API check failed"',
            "      exit 1",
            "    fi",
            "  fi",
            "fi",
            "",
            'if [ -n "${ADMIN_ENDPOINT}" ]; then',
            '  echo "RBAC admin endpoint: ${ADMIN_ENDPOINT}"',
            '  RBAC_STATUS=$(curl -s -o /tmp/rbac_admin.json -w "%{http_code}" \\',
            '    -H "Authorization: Bearer ${TOKEN}" \\',
            '    "${BASE_URL}${ADMIN_ENDPOINT}")',
            '  RBAC_BODY=$(cat /tmp/rbac_admin.json)',
            '  echo "[rbac admin] status=${RBAC_STATUS} resp=${RBAC_BODY}"',
            '  if [ "${RBAC_STATUS}" != "403" ]; then',
            '    echo "❌ expected 403 for RBAC admin endpoint"',
            "    exit 1",
            "  fi",
            '  echo "RBAC check passed (403)"',
            "else",
            '  echo "RBAC check skipped"',
            "fi",
            "",
            'if [ "${HAS_TOOLS_ENDPOINT}" = "1" ]; then',
            '  NO_TOKEN_POST_STATUS=$(curl -s -o /tmp/no_token_post.json -w "%{http_code}" \\',
            '    -H "Content-Type: application/json" \\',
            '    -d \'{"name":"test_tool","description":"test desc","author_id":1}\' \\',
            '    "${BASE_URL}/api/tools")',
            '  echo "[tools post no token] status=${NO_TOKEN_POST_STATUS} resp=$(cat /tmp/no_token_post.json)"',
            '  if [ "${NO_TOKEN_POST_STATUS}" != "401" ]; then',
            '    echo "❌ expected 401 for post /api/tools without token"',
            "    exit 1",
            "  fi",
            "",
            '  NO_TOKEN_GET_STATUS=$(curl -s -o /tmp/no_token_get.json -w "%{http_code}" \\',
            '    "${BASE_URL}/api/tools")',
            '  echo "[tools get no token] status=${NO_TOKEN_GET_STATUS} resp=$(cat /tmp/no_token_get.json)"',
            '  if [ "${NO_TOKEN_GET_STATUS}" != "401" ]; then',
            '    echo "❌ expected 401 for get /api/tools without token"',
            "    exit 1",
            "  fi",
            "",
            '  WITH_TOKEN_POST_STATUS=$(curl -s -o /tmp/with_token_post.json -w "%{http_code}" \\',
            '    -H "Authorization: Bearer ${TOKEN}" \\',
            '    -H "Content-Type: application/json" \\',
            '    -d \'{"name":"test_tool","description":"test desc","author_id":999}\' \\',
            '    "${BASE_URL}/api/tools")',
            '  echo "[tools post with token] status=${WITH_TOKEN_POST_STATUS} resp=$(cat /tmp/with_token_post.json)"',
            '  if [ "${WITH_TOKEN_POST_STATUS}" != "200" ]; then',
            '    echo "❌ expected 200 for post /api/tools with token"',
            "    exit 1",
            "  fi",
            '  POST_AUTHOR_ID=$(python3 -c "import json; print(json.load(open(\'/tmp/with_token_post.json\')).get(\'author_id\', \'\'))" 2>/dev/null || echo "")',
            '  POST_USER_ID=$(python3 -c "import json; print(json.load(open(\'/tmp/with_token_post.json\')).get(\'user_id\', \'\'))" 2>/dev/null || echo "")',
            '  if [ "${POST_AUTHOR_ID}" != "${USER_ID}" ]; then',
            '    echo "❌ forged author_id was not overridden: post.author_id=${POST_AUTHOR_ID}, expected=${USER_ID}"',
            "    exit 1",
            "  fi",
            '  if [ -n "${POST_USER_ID}" ] && [ "${POST_USER_ID}" != "${USER_ID}" ]; then',
            '    echo "❌ post.user_id mismatch: ${POST_USER_ID}, expected=${USER_ID}"',
            "    exit 1",
            "  fi",
            '  echo "✅ post author/user id override verified"',
            "",
            '  WITH_TOKEN_GET_STATUS=$(curl -s -o /tmp/with_token_get.json -w "%{http_code}" \\',
            '    -H "Authorization: Bearer ${TOKEN}" \\',
            '    "${BASE_URL}/api/tools")',
            '  WITH_TOKEN_GET_BODY=$(cat /tmp/with_token_get.json)',
            '  echo "[tools get with token] status=${WITH_TOKEN_GET_STATUS} resp=${WITH_TOKEN_GET_BODY}"',
            '  if [ "${WITH_TOKEN_GET_STATUS}" != "200" ]; then',
            '    echo "❌ expected 200 for get /api/tools with token"',
            "    exit 1",
            "  fi",
            '  if ! echo "${WITH_TOKEN_GET_BODY}" | grep -q "test_tool"; then',
            '    echo "❌ test_tool not found in tools list"',
            "    exit 1",
            "  fi",
            '  GET_FIRST_AUTHOR_ID=$(python3 -c "import json; d=json.load(open(\'/tmp/with_token_get.json\')); row=d[0] if isinstance(d,list) and d else {}; print(row.get(\'author_id\', \'\'))" 2>/dev/null || echo "")',
            '  GET_FIRST_USER_ID=$(python3 -c "import json; d=json.load(open(\'/tmp/with_token_get.json\')); row=d[0] if isinstance(d,list) and d else {}; print(row.get(\'user_id\', \'\'))" 2>/dev/null || echo "")',
            '  if [ "${GET_FIRST_AUTHOR_ID}" != "${USER_ID}" ]; then',
            '    echo "❌ get author_id mismatch: ${GET_FIRST_AUTHOR_ID}, expected=${USER_ID}"',
            "    exit 1",
            "  fi",
            '  if [ -n "${GET_FIRST_USER_ID}" ] && [ "${GET_FIRST_USER_ID}" != "${USER_ID}" ]; then',
            '    echo "❌ get user_id mismatch: ${GET_FIRST_USER_ID}, expected=${USER_ID}"',
            "    exit 1",
            "  fi",
            '  echo "✅ get author/user id verified"',
            "else",
            '  echo "Tools checks skipped (/api/tools not found)"',
            "fi",
            "",
            'echo "✅ all API checks passed"',
        ]

        self._safe_write_text(script_path, "\n".join(lines) + "\n")
        script_path.chmod(0o755)

    @staticmethod
    def _inject_vite_api_proxy(content: str) -> str:
        if re.search(r'proxy\s*:\s*{[^}]*[\'"]\/api[\'"]\s*:', content, re.S):
            return content

        api_proxy_entry = "      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },"

        if re.search(r'proxy\s*:\s*{', content):
            return re.sub(
                r'(proxy\s*:\s*{)',
                rf"\1\n{api_proxy_entry}",
                content,
                count=1,
            )

        if re.search(r'server\s*:\s*{', content):
            return re.sub(
                r'(server\s*:\s*{)',
                (
                    "\\1\n"
                    "    proxy: {\n"
                    "      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true }\n"
                    "    },"
                ),
                content,
                count=1,
            )

        server_block = (
            "  server: {\n"
            "    proxy: {\n"
            "      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true }\n"
            "    }\n"
            "  },\n"
        )

        if "resolve:" in content:
            return content.replace("  resolve:", f"{server_block}  resolve:", 1)

        marker = "})"
        idx = content.rfind(marker)
        if idx == -1:
            return content.rstrip() + "\n" + server_block
        return content[:idx] + server_block + content[idx:]

    def _ensure_vite_api_proxy(self, frontend_dir: Path) -> None:
        ts_path = frontend_dir / "vite.config.ts"
        js_path = frontend_dir / "vite.config.js"
        source_path = ts_path if ts_path.exists() else js_path
        if not source_path.exists():
            return

        original = source_path.read_text(encoding="utf-8")
        updated = self._inject_vite_api_proxy(original)
        if updated != original:
            self._safe_write_text(source_path, updated)

        if source_path == js_path and not ts_path.exists():
            self._safe_write_text(ts_path, updated)

    def _has_tools_api(self) -> bool:
        for api in self._backend_apis():
            route = str(api.get("route", "")).strip()
            if route == "/api/tools":
                return True
        return False

    def _has_login_api(self) -> bool:
        for api in self._backend_apis():
            route = str(api.get("route", "")).strip()
            if route == "/api/login":
                return True
        return False

    def _has_tools_page(self) -> bool:
        for page in self._frontend_pages():
            page_name = str(page.get("name", "")).strip().lower()
            page_path = str(page.get("path", "")).strip()
            if page_path == "/tools" or page_name == "tools":
                return True
        return False

    def _has_login_page(self) -> bool:
        for page in self._frontend_pages():
            page_name = str(page.get("name", "")).strip().lower()
            page_path = str(page.get("path", "")).strip()
            if page_path == "/login" or page_name == "login":
                return True
        return False

    def _has_admin_page(self) -> bool:
        for page in self._frontend_pages():
            page_name = str(page.get("name", "")).strip().lower()
            page_path = str(page.get("path", "")).strip().lower()
            if page_name == "admin" or page_path == "/admin":
                return True
        return False

    def _has_admin_api(self) -> bool:
        for api in self._backend_apis():
            route = str(api.get("route", "")).strip().lower()
            if "admin" in route:
                return True
        return False

    def _resolve_api_client_import(self, frontend_dir: Path) -> str | None:
        if (frontend_dir / "src" / "lib" / "api.ts").exists():
            return "@/lib/api"
        if (frontend_dir / "src" / "lib" / "request.ts").exists():
            return "@/lib/request"
        return None

    def _generate_tools_vue_view(self) -> str:
        if self._api_client_import:
            script = (
                "<script setup>\n"
                "import { onMounted, reactive, ref } from 'vue'\n"
                f"import api from '{self._api_client_import}'\n\n"
                "const form = reactive({ name: '', description: '' })\n"
                "const tools = ref([])\n"
                "const loading = ref(false)\n"
                "const error = ref('')\n\n"
                "async function fetchTools() {\n"
                "  loading.value = true\n"
                "  error.value = ''\n"
                "  try {\n"
                "    const res = await api.get('/api/tools')\n"
                "    tools.value = Array.isArray(res?.data) ? res.data : []\n"
                "  } catch (e) {\n"
                "    error.value = 'Failed to load tools'\n"
                "  } finally {\n"
                "    loading.value = false\n"
                "  }\n"
                "}\n\n"
                "async function createTool() {\n"
                "  if (!form.name.trim()) return\n"
                "  error.value = ''\n"
                "  try {\n"
                "    await api.post('/api/tools', {\n"
                "      name: form.name.trim(),\n"
                "      description: form.description.trim(),\n"
                "      author_id: 999,\n"
                "    })\n"
                "    form.name = ''\n"
                "    form.description = ''\n"
                "    await fetchTools()\n"
                "  } catch (e) {\n"
                "    error.value = 'Failed to create tool'\n"
                "  }\n"
                "}\n\n"
                "onMounted(fetchTools)\n"
                "</script>\n"
            )
        else:
            script = (
                "<script setup>\n"
                "import { onMounted, reactive, ref } from 'vue'\n\n"
                "const form = reactive({ name: '', description: '' })\n"
                "const tools = ref([])\n"
                "const loading = ref(false)\n"
                "const error = ref('')\n\n"
                "function authHeaders() {\n"
                "  const token = localStorage.getItem('token') || localStorage.getItem('access_token') || ''\n"
                "  return token ? { Authorization: `Bearer ${token}` } : {}\n"
                "}\n\n"
                "async function fetchTools() {\n"
                "  loading.value = true\n"
                "  error.value = ''\n"
                "  try {\n"
                "    const res = await fetch('/api/tools', { headers: authHeaders() })\n"
                "    if (!res.ok) throw new Error('fetch failed')\n"
                "    const data = await res.json()\n"
                "    tools.value = Array.isArray(data) ? data : []\n"
                "  } catch (e) {\n"
                "    error.value = 'Failed to load tools'\n"
                "  } finally {\n"
                "    loading.value = false\n"
                "  }\n"
                "}\n\n"
                "async function createTool() {\n"
                "  if (!form.name.trim()) return\n"
                "  error.value = ''\n"
                "  try {\n"
                "    const res = await fetch('/api/tools', {\n"
                "      method: 'POST',\n"
                "      headers: {\n"
                "        'Content-Type': 'application/json',\n"
                "        ...authHeaders(),\n"
                "      },\n"
                "      body: JSON.stringify({\n"
                "        name: form.name.trim(),\n"
                "        description: form.description.trim(),\n"
                "        author_id: 999,\n"
                "      }),\n"
                "    })\n"
                "    if (!res.ok) throw new Error('create failed')\n"
                "    form.name = ''\n"
                "    form.description = ''\n"
                "    await fetchTools()\n"
                "  } catch (e) {\n"
                "    error.value = 'Failed to create tool'\n"
                "  }\n"
                "}\n\n"
                "onMounted(fetchTools)\n"
                "</script>\n"
            )

        template = (
            "<template>\n"
            "  <section class=\"tools-page\">\n"
            "    <h2>Tools</h2>\n"
            "    <div class=\"tool-form\">\n"
            "      <input v-model=\"form.name\" placeholder=\"Tool name\" />\n"
            "      <input v-model=\"form.description\" placeholder=\"Description\" />\n"
            "      <button type=\"button\" @click=\"createTool\">Create</button>\n"
            "    </div>\n"
            "    <p v-if=\"error\" class=\"error\">{{ error }}</p>\n"
            "    <p v-if=\"loading\">Loading...</p>\n"
            "    <ul v-else>\n"
            "      <li v-for=\"tool in tools\" :key=\"tool.id || `${tool.name}-${tool.author_id || ''}`\">\n"
            "        <strong>{{ tool.name }}</strong> - {{ tool.description }}\n"
            "      </li>\n"
            "    </ul>\n"
            "  </section>\n"
            "</template>\n"
        )

        style = (
            "<style scoped>\n"
            ".tools-page { display: grid; gap: 12px; }\n"
            ".tool-form { display: grid; gap: 8px; max-width: 420px; }\n"
            ".error { color: #ff6b6b; }\n"
            "</style>\n"
        )
        return template + "\n" + script + "\n" + style

    def _generate_login_vue_view(self) -> str:
        redirect_path = "/tools" if self._has_tools_page() else "/"

        script = (
            "<script setup>\n"
            "import { reactive, ref } from 'vue'\n"
            "import { useRouter } from 'vue-router'\n\n"
            "const router = useRouter()\n"
            "const form = reactive({ username: '', password: '' })\n"
            "const loading = ref(false)\n"
            "const error = ref('')\n\n"
            "async function login() {\n"
            "  if (loading.value) return\n"
            "  error.value = ''\n"
            "  loading.value = true\n"
            "  try {\n"
            "    const response = await fetch('/api/login', {\n"
            "      method: 'POST',\n"
            "      headers: { 'Content-Type': 'application/json' },\n"
            "      body: JSON.stringify({\n"
            "        username: form.username.trim(),\n"
            "        password: form.password,\n"
            "      }),\n"
            "    })\n"
            "    const data = await response.json().catch(() => ({}))\n"
            "    if (!response.ok) {\n"
            "      error.value = data?.detail || 'Invalid credentials'\n"
            "      return\n"
            "    }\n"
            "    const token = typeof data?.access_token === 'string' ? data.access_token : ''\n"
            "    if (!token) {\n"
            "      error.value = 'Invalid credentials'\n"
            "      return\n"
            "    }\n"
            "    localStorage.setItem('token', token)\n"
            "    localStorage.setItem('access_token', token)\n"
            f"    router.push({json.dumps(redirect_path)})\n"
            "  } catch (e) {\n"
            "    error.value = 'Invalid credentials'\n"
            "  } finally {\n"
            "    loading.value = false\n"
            "  }\n"
            "}\n"
            "</script>\n"
        )

        template = (
            "<template>\n"
            "  <section class=\"login-page\">\n"
            "    <h2>Login</h2>\n"
            "    <form class=\"login-form\" @submit.prevent=\"login\">\n"
            "      <input v-model=\"form.username\" type=\"text\" placeholder=\"Username\" autocomplete=\"username\" required />\n"
            "      <input v-model=\"form.password\" type=\"password\" placeholder=\"Password\" autocomplete=\"current-password\" required />\n"
            "      <button type=\"submit\" :disabled=\"loading\">{{ loading ? 'Signing in...' : 'Sign in' }}</button>\n"
            "    </form>\n"
            "    <p v-if=\"error\" class=\"error\">{{ error }}</p>\n"
            "  </section>\n"
            "</template>\n"
        )

        style = (
            "<style scoped>\n"
            ".login-page { display: grid; gap: 12px; max-width: 360px; }\n"
            ".login-form { display: grid; gap: 8px; }\n"
            ".error { color: #ff6b6b; }\n"
            "</style>\n"
        )
        return template + "\n" + script + "\n" + style

    def _generate_home_dashboard_view(self) -> str:
        has_login = self._has_login_page()
        logout_target = "/login" if has_login else "/"

        script = (
            "<script setup>\n"
            "import { ref, onMounted, computed } from 'vue'\n"
            "import { useRouter } from 'vue-router'\n"
            "import { navPages } from '@/router/roles.generated'\n\n"
            "const router = useRouter()\n"
            "const loggedIn = ref(false)\n"
            "const username = ref('')\n"
            "const role = ref('')\n"
            "const error = ref('')\n\n"
            "const visibleNavPages = computed(() => navPages.filter((page) => {\n"
            "  if (page.public) return true\n"
            "  if (page.role) {\n"
            "    const allowedRoles = String(page.role)\n"
            "      .split('|')\n"
            "      .map((r) => r.trim().toLowerCase())\n"
            "      .filter(Boolean)\n"
            "    return loggedIn.value && allowedRoles.includes(String(role.value || '').toLowerCase())\n"
            "  }\n"
            "  if (page.requiresAuth) return loggedIn.value\n"
            "  return true\n"
            "}))\n\n"
            "function readToken() {\n"
            "  return localStorage.getItem('token') || localStorage.getItem('access_token') || ''\n"
            "}\n\n"
            "function refreshAuthState() {\n"
            "  const token = readToken()\n"
            "  loggedIn.value = Boolean(token)\n"
            "  if (!token) {\n"
            "    username.value = ''\n"
            "    role.value = ''\n"
            "    return Promise.resolve()\n"
            "  }\n"
            "  error.value = ''\n"
            "  return fetch('/api/me', {\n"
            "    headers: { Authorization: `Bearer ${token}` },\n"
            "  })\n"
            "    .then((res) => res.json().catch(() => ({})).then((data) => ({ ok: res.ok, data })))\n"
            "    .then(({ ok, data }) => {\n"
            "      if (!ok) {\n"
            "        loggedIn.value = false\n"
            "        username.value = ''\n"
            "        role.value = ''\n"
            "        error.value = data?.detail || 'Failed to fetch profile'\n"
            "        return\n"
            "      }\n"
            "      loggedIn.value = true\n"
            "      username.value = typeof data?.username === 'string' ? data.username : ''\n"
            "      role.value = typeof data?.role === 'string' ? data.role.toLowerCase() : 'user'\n"
            "    })\n"
            "    .catch(() => {\n"
            "      loggedIn.value = false\n"
            "      username.value = ''\n"
            "      role.value = ''\n"
            "      error.value = 'Failed to fetch profile'\n"
            "    })\n"
            "}\n\n"
            "function logout() {\n"
            "  localStorage.removeItem('token')\n"
            "  localStorage.removeItem('access_token')\n"
            "  loggedIn.value = false\n"
            "  username.value = ''\n"
            "  role.value = ''\n"
            "  error.value = ''\n"
            f"  router.push({json.dumps(logout_target)})\n"
            "}\n\n"
            "onMounted(() => {\n"
            "  refreshAuthState()\n"
            "})\n"
            "</script>\n"
        )

        template = (
            "<template>\n"
            "  <section class=\"home-dashboard\">\n"
            f"    <h1>{self.system_name} Dashboard</h1>\n"
            "    <p class=\"status\" :class=\"loggedIn ? 'ok' : 'warn'\">\n"
            "      <span v-if=\"loggedIn && username\">Logged in as {{ username }} (role: {{ role || 'user' }})</span>\n"
            "      <span v-else-if=\"loggedIn\">Logged in</span>\n"
            "      <span v-else>Not logged in</span>\n"
            "    </p>\n"
            "    <p v-if=\"error\" class=\"error\">{{ error }}</p>\n"
            "    <div class=\"actions\">\n"
            "      <router-link v-for=\"page in visibleNavPages\" :key=\"page.path\" class=\"nav-btn\" :to=\"page.path\">{{ page.label }}</router-link>\n"
            "      <button class=\"nav-btn danger\" type=\"button\" @click=\"logout\">Logout</button>\n"
            "    </div>\n"
            "  </section>\n"
            "</template>\n"
        )

        style = (
            "<style scoped>\n"
            ".home-dashboard { display: grid; gap: 12px; max-width: 460px; }\n"
            ".status.ok { color: #4ade80; }\n"
            ".status.warn { color: #fbbf24; }\n"
            ".error { color: #ff6b6b; }\n"
            ".actions { display: flex; gap: 8px; flex-wrap: wrap; }\n"
            ".nav-btn { padding: 8px 12px; border: 1px solid #3f3f46; border-radius: 8px; background: #18181b; color: #f4f4f5; text-decoration: none; cursor: pointer; }\n"
            ".nav-btn.danger { border-color: #7f1d1d; color: #fecaca; }\n"
            "</style>\n"
        )
        return template + "\n" + script + "\n" + style

    @staticmethod
    def _strip_wrapped_quotes(value: str) -> str:
        text = str(value or "").strip()
        if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
            return text[1:-1]
        return text

    def _is_landing_page(self, page: dict[str, Any]) -> bool:
        page_path = str(page.get("path", "")).strip()
        profiles = self._profiles()

        if profiles:
            if "landing" in profiles and page_path in {"/", "/about", "/features", "/pricing", "/contact"}:
                return True
            if "landing" not in profiles:
                return False

        components = page.get("components", [])
        if not isinstance(components, list):
            return False
        for item in components:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source", "")).strip().lower()
            if source == "landing":
                return True
        return False

    def _landing_component_props(self, page: dict[str, Any], component_name: str) -> dict[str, str]:
        components = page.get("components", [])
        if not isinstance(components, list):
            return {}
        supported = {
            str(item).strip().lower()
            for item in self._landing_dictionary.get("ui_tokens", [])
            if str(item).strip()
        }
        target = component_name.strip().lower()
        if supported and target not in supported:
            return {}
        for item in components:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source", "")).strip().lower()
            raw_name = str(item.get("name", "")).strip().lower()
            if source != "landing" or raw_name != target:
                continue
            config = str(item.get("config", "")).strip()
            parsed = self._parse_component_config(config)
            return {k: self._strip_wrapped_quotes(v) for k, v in parsed.items()}
        return {}

    def _landing_has_component(self, page: dict[str, Any], component_name: str) -> bool:
        components = page.get("components", [])
        if not isinstance(components, list):
            return False
        target = component_name.strip().lower()
        supported = {
            str(item).strip().lower()
            for item in self._landing_dictionary.get("ui_tokens", [])
            if str(item).strip()
        }
        if supported and target not in supported:
            return False
        for item in components:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source", "")).strip().lower()
            raw_name = str(item.get("name", "")).strip().lower()
            if source == "landing" and raw_name == target:
                return True
        return False

    def _landing_flow_props(self, page: dict[str, Any], flow_name: str) -> dict[str, str]:
        components = page.get("components", [])
        if not isinstance(components, list):
            return {}
        supported = {
            str(item).strip().upper()
            for item in self._landing_dictionary.get("flows", [])
            if str(item).strip()
        }
        target = flow_name.strip().upper()
        if supported and target not in supported:
            return {}
        for item in components:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source", "")).strip().lower()
            raw_name = str(item.get("name", "")).strip().upper()
            if source != "flow" or raw_name != target:
                continue
            config = str(item.get("config", "")).strip()
            parsed = self._parse_component_config(config)
            return {k: self._strip_wrapped_quotes(v) for k, v in parsed.items()}
        return {}

    @staticmethod
    def _parse_json_array(raw: str) -> list[Any]:
        text = str(raw or "").strip()
        if not text:
            return []
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return []
        return value if isinstance(value, list) else []

    def _is_app_page(self, page: dict[str, Any]) -> bool:
        page_path = str(page.get("path", "")).strip()
        profiles = self._profiles()

        if profiles:
            if "app_min" in profiles and page_path == "/":
                return True
            if "app_min" not in profiles:
                return False

        components = page.get("components", [])
        if not isinstance(components, list):
            return False
        for item in components:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source", "")).strip().lower()
            if source == "app":
                return True
        return False

    def _app_component_props(self, page: dict[str, Any], component_name: str) -> list[dict[str, str]]:
        components = page.get("components", [])
        if not isinstance(components, list):
            return []
        target = component_name.strip().lower()
        matches: list[dict[str, str]] = []
        for item in components:
            if not isinstance(item, dict):
                continue
            source = str(item.get("source", "")).strip().lower()
            raw_name = str(item.get("name", "")).strip().lower()
            if source != "app" or raw_name != target:
                continue
            config = str(item.get("config", "")).strip()
            parsed = self._parse_component_config(config)
            matches.append({k: self._strip_wrapped_quotes(v) for k, v in parsed.items()})
        return matches

    @staticmethod
    def _split_pipe_items(raw: str, fallback: list[str]) -> list[str]:
        items = [item.strip() for item in str(raw or "").split("|") if item.strip()]
        return items if items else fallback

    def _generate_landing_view(self, page: dict[str, Any]) -> str:
        page_path = str(page.get("path", "")).strip()
        page_name = str(page.get("name", "")).strip() or "Landing"
        frontend_paths = {
            str(item.get("path", "")).strip() or "/"
            for item in self._frontend_pages()
        }
        explicit_landing_subpages = {"/about", "/features", "/pricing", "/contact"}
        single_page_landing = page_path == "/" and not any(
            path in explicit_landing_subpages for path in frontend_paths
        )

        header_cfg = self._landing_component_props(page, "Header")
        hero_cfg = self._landing_component_props(page, "Hero")
        feature_cfg = self._landing_component_props(page, "FeatureGrid")
        testimonial_cfg = self._landing_component_props(page, "Testimonial")
        pricing_cfg = self._landing_component_props(page, "Pricing")
        cta_cfg = self._landing_component_props(page, "CTA")
        contact_cfg = self._landing_component_props(page, "Contact")
        footer_cfg = self._landing_component_props(page, "Footer")
        faq_cfg = self._landing_component_props(page, "FAQ")
        team_cfg = self._landing_component_props(page, "Team")
        stats_cfg = self._landing_component_props(page, "Stats")
        logo_cfg = self._landing_component_props(page, "LogoCloud")
        jobs_cfg = self._landing_component_props(page, "Jobs")
        portfolio_cfg = self._landing_component_props(page, "Portfolio")
        contact_submit_flow = self._landing_flow_props(page, "CONTACT_SUBMIT")
        lead_capture_flow = self._landing_flow_props(page, "LEAD_CAPTURE")
        jobs_present = self._landing_has_component(page, "Jobs")
        portfolio_present = self._landing_has_component(page, "Portfolio")
        pricing_present = self._landing_has_component(page, "Pricing")
        contact_present = self._landing_has_component(page, "Contact") or bool(contact_submit_flow) or bool(lead_capture_flow)
        faq_present = self._landing_has_component(page, "FAQ")
        personal_portfolio_mode = single_page_landing and portfolio_present and contact_present and not pricing_present

        brand = header_cfg.get("brand") or footer_cfg.get("brand") or self.system_name or "Brand Site"

        def normalize_personal_brand(raw: str) -> str:
            text = str(raw or "").strip()
            if not text:
                return "个人作品集"
            compact = text.replace(" ", "")
            generated_markers = (
                "demo",
                "site",
                "landing",
                "portfolio",
                "project",
                "brand",
                "fix",
                "smoke",
                "test",
            )
            looks_generated = (
                bool(re.fullmatch(r"[A-Za-z0-9_-]{10,}", compact))
                or any(marker in compact.lower() for marker in generated_markers)
                or bool(re.search(r"[a-z][A-Z]", compact))
            )
            return "个人作品集" if looks_generated else text

        def normalize_business_brand(raw: str) -> str:
            text = str(raw or "").strip()
            if not text:
                return "品牌官网"
            compact = text.replace(" ", "")
            generated_markers = (
                "demo",
                "site",
                "landing",
                "portfolio",
                "project",
                "brand",
                "fix",
                "smoke",
                "test",
                "review",
                "company",
                "product",
            )
            looks_generated = (
                bool(re.fullmatch(r"[A-Za-z0-9_-]{10,}", compact))
                or any(marker in compact.lower() for marker in generated_markers)
                or bool(re.search(r"[a-z][A-Z]", compact))
            )
            return "品牌官网" if looks_generated else text

        personal_brand = normalize_personal_brand(brand) if personal_portfolio_mode else brand
        business_brand = normalize_business_brand(brand) if not personal_portfolio_mode else brand
        display_brand = personal_brand if personal_portfolio_mode else business_brand
        footer_brand_raw = footer_cfg.get("brand", brand)
        footer_brand = normalize_personal_brand(footer_brand_raw) if personal_portfolio_mode else normalize_business_brand(footer_brand_raw)
        default_nav_labels = ["关于我", "服务说明", "作品展示", "联系方式"] if personal_portfolio_mode else ["产品介绍", "产品能力", "客户评价", "联系我们"]
        nav_labels = self._split_pipe_items(
            header_cfg.get("links", "|".join(default_nav_labels)),
            default_nav_labels,
        )

        def link_to_path(label: str) -> str:
            lowered = label.strip().lower()
            if lowered in {"home", "首页"}:
                return "/"
            if lowered in {"about", "关于", "关于我们", "关于我", "about me", "产品介绍"}:
                return "/about"
            if lowered in {"features", "功能", "能力", "产品能力", "服务", "服务说明", "services"}:
                return "/features"
            if lowered in {"portfolio", "work", "works", "projects", "案例", "作品", "作品展示", "项目作品"}:
                return "/features"
            if lowered in {"客户评价", "评价", "testimonials"}:
                return "/about"
            if lowered in {"pricing", "价格", "方案"}:
                return "/pricing"
            if lowered in {"contact", "联系我们", "联系", "联系方式", "联系我"}:
                return "/contact"
            return "/"

        def single_page_target(label: str) -> str:
            lowered = label.strip().lower()
            if lowered in {"home", "首页"}:
                return "#hero"
            if lowered in {"about", "关于", "关于我们", "关于我", "about me", "产品介绍"}:
                return "#about"
            if lowered in {"features", "功能", "能力", "产品能力", "服务", "服务说明", "services"}:
                return "#features"
            if lowered in {"portfolio", "work", "works", "projects", "案例", "作品", "作品展示", "项目作品"}:
                return "#portfolio" if portfolio_present else "#features"
            if lowered in {"客户评价", "评价", "testimonials"}:
                return "#testimonials"
            if lowered in {"pricing", "价格", "方案"}:
                if pricing_present:
                    return "#pricing"
                if portfolio_present:
                    return "#portfolio"
                return "#cta"
            if lowered in {"contact", "联系我们", "联系", "联系方式", "联系我"}:
                if contact_present:
                    return "#contact"
                return "#cta"
            return "#hero"

        nav_links = [
            {
                "label": label,
                "target": single_page_target(label) if single_page_landing else link_to_path(label),
            }
            for label in nav_labels
        ]

        generic_business_brand = (not personal_portfolio_mode) and display_brand == "品牌官网"
        default_hero_title = (
            "先把产品价值讲明白"
            if generic_business_brand
            else f"{display_brand}｜先把产品价值讲明白"
        )
        default_hero_subtitle = "先说清适合对象、关键场景和价值差异，再把产品能力、FAQ、预约演示和联系入口接成同一条首页路径。"
        default_cta_primary = "预约演示"
        default_cta_secondary = "先看适用场景"
        if personal_portfolio_mode:
            if personal_brand == "个人作品集":
                default_hero_title = "把个人表达收成一张好用的首页"
            else:
                default_hero_title = f"{personal_brand} · 让第一页先把你讲明白"
            default_hero_subtitle = "我更在意先把你是谁、适合什么合作、以及为什么值得继续联系讲清楚，再决定页面是不是要更满、更热闹，或者更像一份品牌作品。"
            default_cta_primary = "联系我"
            default_cta_secondary = "查看作品"
        hero_title = hero_cfg.get("title", default_hero_title)
        hero_subtitle = hero_cfg.get("subtitle", default_hero_subtitle)
        cta_primary = hero_cfg.get("cta_primary", default_cta_primary)
        cta_secondary = hero_cfg.get("cta_secondary", default_cta_secondary)

        default_about_title = "为什么这类官网更容易把产品讲明白"
        default_about_body = "与其把首页做成一组抽象卖点，我们更倾向先说明产品适合谁、解决什么问题、和现有做法相比差在哪里，再用能力、FAQ 和联系入口把这条认知路径接稳。"
        default_about_note = "这尤其适合还在持续验证定位、准备预约演示、或者希望减少销售和产品同学重复解释成本的产品团队、创业团队和服务型产品。"
        default_about_highlights = ["适合对象先讲透", "价值差异先于功能堆砌", "FAQ 与演示入口接进同一条认知链"]
        if personal_portfolio_mode:
            default_about_title = "关于我"
            default_about_body = "我更偏一起编辑一张公开作品的合作方式，而不是先堆很多视觉效果再回头找逻辑。通常会先把个人定位、合作边界和首页目标梳理清楚，再决定哪些内容该靠语气去讲，哪些该靠结构去托住。"
            default_about_note = "所以你在下面看到的案例，不是按行业平铺出来的，而是按我最常处理的判断顺序排的：有的先补信任感，有的先补产品表达，也有一些更适合把旧内容重新整理成长期能继续使用的入口。"
            default_about_highlights = ["更像并肩编辑，而不是外包接单", "先收判断顺序，再做视觉选择", "页面交付后仍然方便继续补内容和迭代"]
        about_title = hero_cfg.get("about_title", default_about_title)
        about_body = hero_cfg.get("about_body", default_about_body)
        about_note = hero_cfg.get("about_note", default_about_note)
        about_highlights = self._split_pipe_items(
            hero_cfg.get("about_points", "|".join(default_about_highlights)),
            default_about_highlights,
        )

        default_feature_title = "产品能力"
        default_feature_items = ["适合对象更明确", "关键场景更容易代入", "客户疑问提前回答", "演示与询盘入口更顺手"]
        default_feature_descriptions = [
            "先回答这款产品服务谁、谁最容易从中受益，减少首页一上来就只谈功能堆砌的模糊感。",
            "用真实业务场景去承接产品价值，让来访者更容易把自己代入进去，而不是只看抽象流程。",
            "把销售会被反复追问的问题提前放进页面里，减少演示前后的重复解释成本。",
            "把预约演示、FAQ 和联系入口接成一条更自然的下一步动作，让官网更像一个稳定的承接面。",
        ]
        if personal_portfolio_mode:
            default_feature_title = "服务说明"
            default_feature_items = ["个人品牌首页梳理", "产品表达页重写", "前端体验细节收口", "上线后的继续编辑"]
            default_feature_descriptions = [
                "适合个人主页、服务页和作品入口，先把来访者最该知道的判断顺序排清楚。",
                "把核心价值、能力边界和合作方式重新写成更能被第一次访问理解的页面语言。",
                "把信息层级、按钮路径和关键交互收得更顺，让页面不只是好看，而是真的更好用。",
                "支持后续继续补案例、改文案、调细节，页面不会在第一次上线后就锁死。",
            ]
        feature_title = feature_cfg.get("title", default_feature_title)
        feature_items = self._split_pipe_items(
            feature_cfg.get("items", "|".join(default_feature_items)),
            default_feature_items,
        )
        feature_descriptions = default_feature_descriptions[: len(feature_items)]

        default_testimonial_title = "客户评价"
        default_testimonial_items = ["价值表达更清楚", "演示沟通更顺畅", "询盘转化更自然"]
        default_testimonial_intro = "这些反馈更像真实团队在官网上线后最先感受到的变化：解释成本有没有下降、来访者理解是否更快、询盘是否更聚焦。"
        default_testimonial_cards = [
            {
                "quote": "官网上线后，第一次来访的客户不用等到演示里才弄清我们适合什么场景，首页本身就把适合对象和价值差异讲清楚了。",
                "role": "增长负责人 / B2B SaaS",
                "result": "演示前解释成本明显下降",
                "context": "官网重写 / 销售前置页 / 首次访问承接",
            },
            {
                "quote": "以前很多定位和边界都要靠口头补充，现在首页先把适合谁、为什么值得继续了解讲明白了，真正进入演示时大家讨论得更快更准。",
                "role": "产品负责人 / 创业团队",
                "result": "咨询更快进入真实需求",
                "context": "早期产品 / 定位澄清 / 预约演示入口",
            },
            {
                "quote": "客户评价、FAQ 和联系入口放在同一条叙事里后，官网终于不只是静态展示页，而是一个能持续承接询盘和销售动作的前置页面。",
                "role": "联合创始人 / 服务型产品",
                "result": "官网开始稳定承接销售动作",
                "context": "服务转化 / FAQ 承接 / 联系动作收口",
            },
        ]
        if personal_portfolio_mode:
            default_testimonial_title = "合作反馈"
            default_testimonial_items = ["判断更快对齐", "表达更像本人", "交付后还能继续编辑"]
            default_testimonial_intro = "这些反馈更像我最常见的一类合作结果：不是只觉得页面更整齐，而是会明显感觉到判断更快对齐了，内容更像本人了，后面继续改也不费劲。"
            default_testimonial_cards = [
                {
                    "quote": "最省心的地方不是速度，而是几轮沟通之后，页面终于像本人在说话，不再像一个套模板的自我介绍页。",
                    "role": "独立合作 / 个人品牌",
                    "result": "语气终于和人对上了",
                    "context": "个人主页 / 语气校准 / 启动阶段",
                },
                {
                    "quote": "页面不是只看起来更完整，而是真的更容易让别人判断我适合接什么、不适合接什么。",
                    "role": "内容创作者 / 咨询顾问",
                    "result": "边界和价值都更清楚",
                    "context": "服务介绍 / 内容表达 / 来访判断",
                },
                {
                    "quote": "上线后要继续补案例、改标题、换排序时，没有那种一改就全乱掉的感觉，后续维护非常顺。",
                    "role": "自由职业者 / 服务提供者",
                    "result": "后续继续编辑更轻松",
                    "context": "上线后迭代 / 案例补充 / 文案更新",
                },
            ]
        testimonial_title = testimonial_cfg.get("title", default_testimonial_title)
        testimonial_intro = testimonial_cfg.get("subtitle", default_testimonial_intro)
        testimonial_items = self._split_pipe_items(
            testimonial_cfg.get("items", "|".join(default_testimonial_items)),
            default_testimonial_items,
        )
        testimonial_cards = []
        for entry in self._parse_json_array(testimonial_cfg.get("items", "")):
            if not isinstance(entry, dict):
                continue
            quote = str(entry.get("quote", "") or entry.get("text", "")).strip()
            role = str(entry.get("role", "") or entry.get("author", "")).strip()
            result = str(entry.get("result", "") or entry.get("outcome", "")).strip()
            context = str(entry.get("context", "") or entry.get("scope", "")).strip()
            if quote:
                testimonial_cards.append({
                    "quote": quote,
                    "role": role or ("合作反馈" if personal_portfolio_mode else "客户反馈"),
                    "result": result or ("表达更清楚" if personal_portfolio_mode else "信任建立更自然"),
                    "context": context or "",
                })
        if not testimonial_cards:
            if testimonial_items != default_testimonial_items:
                for item in testimonial_items:
                    testimonial_cards.append({
                        "quote": item,
                        "role": "合作反馈" if personal_portfolio_mode else "客户反馈",
                        "result": "表达更清楚" if personal_portfolio_mode else "信任建立更自然",
                        "context": "",
                    })
            else:
                testimonial_cards = [dict(card) for card in default_testimonial_cards]

        pricing_title = pricing_cfg.get("title", "价格方案")
        pricing_items = self._split_pipe_items(
            pricing_cfg.get("plans", "基础版|专业版|企业版"),
            ["基础版", "专业版", "企业版"],
        )

        default_cta_title = "如果你希望官网先把适合对象、价值差异和预约动作讲顺，我们可以一起把第一屏到联系入口收成同一条路径"
        default_cta_button = "预约演示"
        default_cta_note = "更适合：官网重写 / 首次上线 / 预约演示前置页"
        default_cta_capture_items = ["官网重写", "首次上线", "预约演示前置页"]
        if personal_portfolio_mode:
            default_cta_title = "如果你想先把第一页讲对，再决定它要不要更像一张作品，我们可以从这里开始"
            default_cta_button = "发起联系"
            default_cta_note = "更适合：个人主页 / 服务说明 / 作品整理 / 旧页面重写"
            default_cta_capture_items = ["个人主页", "服务说明", "作品整理", "旧页面重写"]
        cta_title = cta_cfg.get("title", default_cta_title)
        cta_button = cta_cfg.get("button", default_cta_button)
        cta_note = cta_cfg.get("subtitle", default_cta_note)
        cta_capture_items = self._split_pipe_items(
            cta_cfg.get("focus_items", "|".join(default_cta_capture_items)),
            default_cta_capture_items,
        )

        default_contact_title = "预约演示 / 联系我们"
        default_contact_intro = "如果你已经基本判断这类官网适合当前阶段，可以把产品、目标和希望承接的动作发给我们，我们会先按场景给出更具体的建议。"
        default_contact_response_items = [
            "24 小时内回复",
            "定位 / FAQ / 演示承接可拆分讨论",
            "先对齐目标，再进入页面制作",
        ]
        default_contact_handoff_cards = [
            {"label": "回复节奏", "value": "24 小时内回复"},
            {"label": "讨论范围", "value": "定位 / FAQ / 演示承接可拆分讨论"},
            {"label": "推进方式", "value": "先对齐目标，再进入页面制作"},
        ]
        default_contact_success_items = [
            "我们会先按场景回一版简短建议",
            "通常会先判断首页、FAQ 和预约动作谁该先收",
            "如果方向明确，再进入页面细化和制作",
        ]
        if personal_portfolio_mode:
            default_contact_title = "发起联系"
            default_contact_intro = "如果你已经大致知道自己想做哪类页面，可以直接把目标、现有内容和时间节奏发给我。我通常会先帮你判断：首页应该先讲什么、哪些内容该往后放、哪些地方暂时不用做太满。"
            default_contact_response_items = [
                "先收首页判断顺序",
                "支持个人主页 / 服务页 / 作品集 / 旧页重写",
                "通常先给结构建议，再进入制作",
            ]
            default_contact_handoff_cards = [
                {"label": "回复节奏", "value": "先收目标、边界和首页判断顺序"},
                {"label": "讨论范围", "value": "支持个人主页 / 服务页 / 作品集 / 旧页重写"},
                {"label": "推进方式", "value": "通常先给结构建议，再进入制作"},
            ]
            default_contact_success_items = [
                "我会先按目标和内容边界回一版更短的首页建议",
                "通常先看首页结构、服务说明和作品排序谁该先收",
                "方向明确后再进入制作",
            ]
        contact_title = contact_cfg.get("title", default_contact_title)
        contact_intro = contact_cfg.get("subtitle", default_contact_intro)
        contact_name_placeholder = "姓名"
        contact_email_placeholder = "邮箱"
        contact_message_placeholder = "请填写您的需求"
        contact_submit_label = "提交信息"
        if not personal_portfolio_mode:
            contact_name_placeholder = "例如：产品负责人 / 创始人"
            contact_email_placeholder = "例如：team@yourcompany.com"
            contact_message_placeholder = "请写下产品阶段、最想先讲清的价值差异，以及希望官网承接的动作。"
            contact_submit_label = "发送咨询信息"
        contact_fields = self._split_pipe_items(
            contact_cfg.get("fields", "name|email|message"),
            ["name", "email", "message"],
        )
        contact_response_items = self._split_pipe_items(
            contact_cfg.get("response_items", "|".join(default_contact_response_items)),
            default_contact_response_items,
        )
        contact_success_items = self._split_pipe_items(
            contact_cfg.get("success_items", "|".join(default_contact_success_items)),
            default_contact_success_items,
        )
        contact_handoff_cards = []
        for entry in self._parse_json_array(contact_cfg.get("handoff_cards", "")):
            if not isinstance(entry, dict):
                continue
            label = str(entry.get("label", "")).strip()
            value = str(entry.get("value", "")).strip()
            if label and value:
                contact_handoff_cards.append({"label": label, "value": value})
        if not contact_handoff_cards:
            contact_handoff_cards = [dict(item) for item in default_contact_handoff_cards]
        default_footer_links = ["关于我", "服务说明", "作品展示", "联系方式"] if personal_portfolio_mode else ["产品介绍", "产品能力", "客户评价", "联系我们"]
        footer_links = self._split_pipe_items(
            footer_cfg.get("links", "|".join(default_footer_links)),
            default_footer_links,
        )
        single_page_label_targets = {
            "home": "#hero",
            "首页": "#hero",
            "about": "#about",
            "关于": "#about",
            "关于我们": "#about",
            "关于我": "#about",
            "about me": "#about",
            "产品介绍": "#about",
            "features": "#features",
            "功能": "#features",
            "能力": "#features",
            "产品能力": "#features",
            "服务": "#features",
            "服务说明": "#features",
            "services": "#features",
            "客户评价": "#testimonials",
            "评价": "#testimonials",
            "testimonials": "#testimonials",
            "portfolio": "#portfolio",
            "work": "#portfolio",
            "works": "#portfolio",
            "projects": "#portfolio",
            "案例": "#portfolio",
            "作品": "#portfolio",
            "作品展示": "#portfolio",
            "项目作品": "#portfolio",
            "pricing": "#pricing" if pricing_present else ("#portfolio" if portfolio_present else "#cta"),
            "价格": "#pricing" if pricing_present else ("#portfolio" if portfolio_present else "#cta"),
            "方案": "#pricing" if pricing_present else ("#portfolio" if portfolio_present else "#cta"),
            "contact": "#contact" if contact_present else "#cta",
            "联系我们": "#contact" if contact_present else "#cta",
            "联系": "#contact" if contact_present else "#cta",
            "联系方式": "#contact" if contact_present else "#cta",
            "联系我": "#contact" if contact_present else "#cta",
        }
        faq_title = faq_cfg.get("title", "常见问题")

        faq_items = []
        for entry in self._parse_json_array(faq_cfg.get("items", "")):
            if not isinstance(entry, dict):
                continue
            question = str(entry.get("q", "")).strip()
            answer = str(entry.get("a", "")).strip()
            context = str(entry.get("context", entry.get("label", ""))).strip()
            followup = str(entry.get("followup", entry.get("next", ""))).strip()
            if question and answer:
                faq_items.append({"q": question, "a": answer, "context": context, "followup": followup})
        if not faq_items and faq_present and not personal_portfolio_mode:
            faq_items = [
                {
                    "q": "如果团队还在反复解释产品适合谁，官网最先应该讲清什么？",
                    "a": "先把适合对象、关键场景和价值差异摆在第一屏和产品介绍里，让第一次访问的人先完成一轮判断，再决定要不要继续预约演示或留下联系方式。",
                    "context": "定位澄清 / 首次访问承接",
                    "followup": "最稳的起点 usually 是：首页主张、产品介绍和 FAQ 用同一套判断逻辑。"
                },
                {
                    "q": "产品还在持续迭代，这样的官网会不会很快过时？",
                    "a": "不会。当前结构本来就适合跟着产品一起扩展，后面可以继续补能力页、场景页、案例、FAQ 和更多转化入口，而不用每次都重写整套首页。",
                    "context": "早期产品 / 内容可扩展",
                    "followup": "先把稳定的主张和场景写清，再把会变化的细节留给后续模块逐步补齐。"
                },
                {
                    "q": "如果销售和演示还很依赖人工解释，这页实际能帮到什么？",
                    "a": "它会先把适合对象、关键问题、能力边界和常见疑问讲在前面，让销售和演示不必每次都从零解释，官网会更像一个稳定的销售前置页。",
                    "context": "销售前置 / 演示承接",
                    "followup": "比较理想的状态是：官网先完成第一轮解释，演示再往更具体的场景里走。"
                },
                {
                    "q": "如果团队还在早期阶段、客户案例不多，这样的官网也值得先上线吗？",
                    "a": "值得。早期阶段更需要先把定位、适合对象、关键场景、FAQ 和联系入口讲清楚，用结构化表达替代还没积累起来的大量客户案例。",
                    "context": "早期阶段 / 信任补强",
                    "followup": "没有太多案例时，可以先把 FAQ、信任反馈和预约演示入口做扎实。"
                },
            ]

        team_members = []
        for entry in self._parse_json_array(team_cfg.get("members", "")):
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name", "")).strip()
            role = str(entry.get("role", "")).strip()
            avatar = str(entry.get("avatar", "")).strip()
            if name and role:
                team_members.append({"name": name, "role": role, "avatar": avatar})

        stats_items = []
        for entry in self._parse_json_array(stats_cfg.get("items", "")):
            if not isinstance(entry, dict):
                continue
            label = str(entry.get("label", "")).strip()
            value = str(entry.get("value", "")).strip()
            if label and value:
                stats_items.append({"label": label, "value": value})

        logo_items = []
        for entry in self._parse_json_array(logo_cfg.get("logos", "")):
            logo_text = str(entry).strip()
            if logo_text:
                logo_items.append(logo_text)

        jobs_title = jobs_cfg.get("title", "开放职位")
        jobs_items = self._split_pipe_items(
            jobs_cfg.get("items", "产品经理|前端工程师|设计师"),
            ["产品经理", "前端工程师", "设计师"],
        )

        default_portfolio_title = "项目作品"
        default_portfolio_intro = "这些案例用来说明不同类型页面在结构、表达和交付上的处理方式，帮助来访者快速理解我们能把什么事情做好。"
        default_portfolio_items = ["企业官网", "SaaS 控制台", "品牌落地页"]
        default_portfolio_meta = ["品牌表达 / 页面结构 / 交付质量", "复杂功能 / 信息组织 / 稳定体验", "定位叙事 / 视觉方向 / 落地执行"]
        default_portfolio_outcomes = ["品牌辨识度更清楚", "关键功能路径更顺手", "页面表达更完整可复用"]
        default_portfolio_details = ["企业官网 / 核心信息重组", "后台产品 / 复杂路径梳理", "品牌专题 / 表达与落地协同"]
        default_portfolio_descriptions = [
            "展示核心成果、视觉表达与落地质量。",
            "展示核心成果、视觉表达与落地质量。",
            "展示核心成果、视觉表达与落地质量。",
        ]
        if personal_portfolio_mode:
            default_portfolio_title = "作品展示"
            default_portfolio_intro = "这些案例不是为了证明我做过多少种风格，而是为了说明我通常怎么挑首页里的重点：哪些项目先补判断，哪些先补表达，哪些先补能长期继续使用的内容骨架。"
            default_portfolio_items = ["独立顾问主页", "产品介绍页", "内容专题页"]
            default_portfolio_meta = [
                "独立顾问 / 个人服务型合作",
                "产品团队 / 单产品官网",
                "内容作者 / 长期内容项目",
            ]
            default_portfolio_outcomes = [
                "第一次来访就知道你适合哪类合作",
                "产品价值和预约动作更快连起来",
                "旧内容被重新整理成持续可读资产",
            ]
            default_portfolio_details = [
                "首页定位、合作方式、联系入口",
                "适合对象、价值主张、预约演示",
                "专题结构、内容分层、持续更新",
            ]
            default_portfolio_descriptions = [
                "把个人定位、代表能力和合作方式收成一个更清晰的首页入口，让第一次来访的人更快判断要不要继续联系，也更快理解这不是一张泛化模板页。",
                "围绕一个明确产品重新组织适合对象、关键场景和预约动作，让页面更像一份能承接演示的官网提案，而不是一组堆在一起的功能块。",
                "把分散文章、案例和主题重新编排成一个长期可维护的内容入口，让旧内容也能继续被看见、被引用、被重新组织。",
            ]
        portfolio_title = portfolio_cfg.get("title", default_portfolio_title)
        portfolio_intro = portfolio_cfg.get("subtitle", default_portfolio_intro)
        portfolio_items = self._split_pipe_items(
            portfolio_cfg.get("items", "|".join(default_portfolio_items)),
            default_portfolio_items,
        )
        portfolio_meta = self._split_pipe_items(
            portfolio_cfg.get("meta", "|".join(default_portfolio_meta)),
            default_portfolio_meta,
        )
        if len(portfolio_meta) < len(portfolio_items):
            portfolio_meta.extend(default_portfolio_meta[len(portfolio_meta) : len(portfolio_items)])
        portfolio_outcomes = self._split_pipe_items(
            portfolio_cfg.get("outcomes", "|".join(default_portfolio_outcomes)),
            default_portfolio_outcomes,
        )
        if len(portfolio_outcomes) < len(portfolio_items):
            portfolio_outcomes.extend(default_portfolio_outcomes[len(portfolio_outcomes) : len(portfolio_items)])
        portfolio_details = self._split_pipe_items(
            portfolio_cfg.get("details", "|".join(default_portfolio_details)),
            default_portfolio_details,
        )
        if len(portfolio_details) < len(portfolio_items):
            portfolio_details.extend(default_portfolio_details[len(portfolio_details) : len(portfolio_items)])
        portfolio_descriptions = default_portfolio_descriptions[: len(portfolio_items)]
        cta_primary_target = "/pricing"
        cta_secondary_target = "/features"
        cta_button_target = "/contact"
        if single_page_landing:
            cta_primary_target = "#contact" if contact_present else ("#portfolio" if portfolio_present else "#cta")
            cta_secondary_target = "#portfolio" if portfolio_present else "#features"
            cta_button_target = "#contact" if contact_present else "#cta"
        cta_primary_target_expr = json.dumps(cta_primary_target, ensure_ascii=False).replace('"', "'")
        cta_secondary_target_expr = json.dumps(cta_secondary_target, ensure_ascii=False).replace('"', "'")
        cta_button_target_expr = json.dumps(cta_button_target, ensure_ascii=False).replace('"', "'")

        faq_section = ""
        if faq_items:
            faq_intro = "把团队在定位、销售前置和上线准备里最常被问到的问题提前讲清，帮助来访者在预约演示前先完成一轮场景判断。"
            if personal_portfolio_mode:
                faq_intro = "把最常见的合作疑问提前讲清楚，能让联系和沟通更顺，也减少来回解释的成本。"
            faq_path_strip = (
                "      <div class=\"section-path-strip\">\n"
                "        <span class=\"section-path-current\">04 常见问题</span>\n"
                "        <span class=\"section-path-next\">下一步：预约演示 / 联系我们</span>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            faq_scan_strip = (
                "      <div class=\"faq-scan-strip\">\n"
                "        <span>定位澄清</span>\n"
                "        <span>销售前置</span>\n"
                "        <span>上线准备</span>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            faq_contact_bridge = (
                "      <div class=\"faq-contact-bridge\">\n"
                "        <span class=\"faq-contact-bridge-label\">FAQ TO CONTACT</span>\n"
                "        <strong>如果这些问题已经帮你完成一轮判断，下一步就把当前阶段、首页目标和希望承接的动作一起发来。</strong>\n"
                "        <div class=\"faq-contact-bridge-strip\">\n"
                "          <span class=\"faq-contact-bridge-current\">带着当前判断进入预约演示 / 联系我们</span>\n"
                "          <span class=\"faq-contact-bridge-next\">先发阶段、目标和承接动作</span>\n"
                "        </div>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            faq_section = (
                "    <section id=\"faq\" class=\"landing-section\" data-landing=\"FAQ\">\n"
                f"      <h2>{faq_title}</h2>\n"
                f"      <p class=\"section-lead\">{faq_intro}</p>\n"
                f"{faq_path_strip}"
                f"{faq_scan_strip}"
                "      <div class=\"faq-list\">\n"
                "        <details v-for=\"item in faqItems\" :key=\"`faq-${item.q}`\" class=\"faq-item\">\n"
                "          <summary>\n"
                "            <span class=\"faq-question\">{{ item.q }}</span>\n"
                "            <span class=\"faq-summary-hint\">查看建议</span>\n"
                "          </summary>\n"
                "          <div class=\"faq-body\">\n"
                "            <span v-if=\"item.context\" class=\"faq-context\">{{ item.context }}</span>\n"
                "            <div class=\"faq-copy-block\">\n"
                "              <span class=\"faq-copy-label\">核心判断</span>\n"
                "              <p class=\"faq-answer\">{{ item.a }}</p>\n"
                "            </div>\n"
                "            <div v-if=\"item.followup\" class=\"faq-followup-block\">\n"
                "              <span class=\"faq-followup-label\">下一步建议</span>\n"
                "              <p class=\"faq-followup\">{{ item.followup }}</p>\n"
                "            </div>\n"
                "          </div>\n"
                "        </details>\n"
                "      </div>\n"
                f"{faq_contact_bridge}"
                "    </section>\n"
            )

        team_section = ""
        if team_members:
            team_section = (
                "    <section id=\"team\" class=\"landing-section\" data-landing=\"Team\">\n"
                "      <h2>团队成员</h2>\n"
                "      <div class=\"team-grid\">\n"
                "        <article v-for=\"member in teamMembers\" :key=\"`member-${member.name}-${member.role}`\" class=\"team-card\">\n"
                "          <div class=\"avatar\">{{ member.avatar || member.name.slice(0, 1) }}</div>\n"
                "          <strong>{{ member.name }}</strong>\n"
                "          <span>{{ member.role }}</span>\n"
                "        </article>\n"
                "      </div>\n"
                "    </section>\n"
            )

        stats_section = ""
        if stats_items:
            stats_section = (
                "    <section id=\"stats\" class=\"landing-section\" data-landing=\"Stats\">\n"
                "      <div class=\"stats-grid\">\n"
                "        <article v-for=\"item in statsItems\" :key=\"`stat-${item.label}`\" class=\"stat-card\">\n"
                "          <strong>{{ item.value }}</strong>\n"
                "          <span>{{ item.label }}</span>\n"
                "        </article>\n"
                "      </div>\n"
                "    </section>\n"
            )

        logo_section = ""
        if logo_items:
            logo_section = (
                "    <section id=\"logos\" class=\"landing-section\" data-landing=\"LogoCloud\">\n"
                "      <h2>Trusted by teams</h2>\n"
                "      <div class=\"logo-grid\">\n"
                "        <article v-for=\"logo in logoItems\" :key=\"`logo-${logo}`\" class=\"logo-card\">\n"
                "          <span>{{ logo }}</span>\n"
                "        </article>\n"
                "      </div>\n"
                "    </section>\n"
            )

        jobs_section = ""
        if jobs_present:
            jobs_section = (
                "    <section id=\"jobs\" class=\"landing-section\" data-landing=\"Jobs\">\n"
                f"      <h2>{jobs_title}</h2>\n"
                "      <div class=\"jobs-grid\">\n"
                "        <article v-for=\"job in jobsItems\" :key=\"`job-${job}`\" class=\"jobs-card\">\n"
                "          <strong>{{ job }}</strong>\n"
                "          <span>欢迎投递并与我们一起打造下一代产品。</span>\n"
                "        </article>\n"
                "      </div>\n"
                "    </section>\n"
            )

        portfolio_section = ""
        if portfolio_present:
            portfolio_section = (
                "    <section id=\"portfolio\" class=\"landing-section\" data-landing=\"Portfolio\">\n"
                + f"      <h2>{portfolio_title}</h2>\n"
                + f"      <p class=\"section-lead\">{portfolio_intro}</p>\n"
                + (
                    "      <div class=\"portfolio-curation-strip\">\n"
                    "        <span class=\"portfolio-curation-label\">CURATED SHELF</span>\n"
                    "        <strong>我通常不会把项目按行业平铺，而会先挑那些最能说明判断、结构和交付气质的案例放在前面。</strong>\n"
                    "        <div class=\"portfolio-curation-grid\">\n"
                    "          <article v-for=\"item in portfolioCurationItems\" :key=\"`portfolio-curation-${item.label}`\" class=\"portfolio-curation-card\">\n"
                    "            <span>{{ item.label }}</span>\n"
                    "            <em>{{ item.value }}</em>\n"
                    "          </article>\n"
                    "        </div>\n"
                    "      </div>\n"
                    if personal_portfolio_mode
                    else ""
                )
                + "      <div class=\"portfolio-grid\">\n"
                + "        <article v-for=\"(item, index) in portfolioItems\" :key=\"`portfolio-${item}`\" class=\"portfolio-card\">\n"
                + "          <span v-if=\"personalPortfolioMode\" class=\"portfolio-sequence\">CASE {{ String(index + 1).padStart(2, '0') }}</span>\n"
                + "          <span class=\"portfolio-meta\">{{ portfolioMeta[index] || '品牌表达 / 页面结构 / 交付质量' }}</span>\n"
                + "          <strong>{{ item }}</strong>\n"
                + "          <p>{{ portfolioDescriptions[index] || '展示核心成果、视觉表达与落地质量。' }}</p>\n"
                + "          <div v-if=\"personalPortfolioMode\" class=\"portfolio-brief\">\n"
                + "            <span><strong>项目类型</strong><em>{{ portfolioMeta[index] || '个人服务型项目' }}</em></span>\n"
                + "            <span><strong>交付范围</strong><em>{{ portfolioDetails[index] || '结构整理、页面表达与交付落地' }}</em></span>\n"
                + "            <span><strong>结果</strong><em>{{ portfolioOutcomes[index] || '页面表达更完整可复用' }}</em></span>\n"
                + "          </div>\n"
                + "          <span v-if=\"personalPortfolioMode\" class=\"portfolio-editor-note\">{{ portfolioSequenceNotes[index] || '先收判断，再收表达，最后收交付节奏。' }}</span>\n"
                + "          <span v-else class=\"portfolio-detail\">{{ portfolioDetails[index] || '独立站点 / 结构整理 / 表达升级' }}</span>\n"
                + "          <span v-if=\"!personalPortfolioMode\" class=\"portfolio-outcome\">{{ portfolioOutcomes[index] || '页面表达更完整可复用' }}</span>\n"
                + "        </article>\n"
                + "      </div>\n"
                + "    </section>\n"
            )

        home_pricing_section = ""
        if single_page_landing and pricing_present:
            home_pricing_section = (
                "    <section id=\"pricing\" class=\"landing-section\" data-landing=\"Pricing\">\n"
                f"      <h2>{pricing_title}</h2>\n"
                "      <div class=\"price-grid\">\n"
                "        <article v-for=\"plan in pricingItems\" :key=\"`plan-${plan}`\">\n"
                "          <h3>{{ plan }}</h3>\n"
                "          <p>适合快速验证与稳定增长场景。</p>\n"
                f"          <button type=\"button\" @click=\"go({cta_button_target_expr})\">咨询方案</button>\n"
                "        </article>\n"
                "      </div>\n"
                "    </section>\n"
            )

        home_contact_section = ""
        if single_page_landing and contact_present:
            contact_path_strip = (
                "      <div class=\"section-path-strip\">\n"
                "        <span class=\"section-path-current\">05 预约演示 / 联系我们</span>\n"
                "        <span class=\"section-path-next\">下一步：发送咨询信息</span>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            contact_entry_bridge = (
                "      <div class=\"contact-entry-bridge\">\n"
                "        <span class=\"contact-entry-bridge-label\">FROM FAQ</span>\n"
                "        <strong>如果你已经完成了适合对象、场景和 FAQ 的一轮判断，这里就把下一步收成一次更短的咨询 intake。</strong>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            contact_intake_bridge = (
                "      <div class=\"contact-intake-bridge\">\n"
                "        <span class=\"contact-intake-bridge-label\">DECISION TO INTAKE</span>\n"
                "        <strong>先把当前阶段、首页目标和想承接的动作写清，页面就能更快从判断层进入真正的咨询 intake。</strong>\n"
                "        <div class=\"contact-intake-bridge-strip\">\n"
                "          <span class=\"contact-intake-bridge-current\">当前：带着判断进入</span>\n"
                "          <span class=\"contact-intake-bridge-next\">下一步：发阶段 / 目标 / 动作</span>\n"
                "        </div>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            home_contact_section = (
                "    <section id=\"contact\" class=\"landing-section\" data-landing=\"Contact\">\n"
                f"      <h2>{contact_title}</h2>\n"
                f"      <p class=\"section-lead\">{contact_intro}</p>\n"
                f"{contact_path_strip}"
                f"{contact_entry_bridge}"
                "      <div class=\"contact-response-strip\">\n"
                "        <span v-for=\"item in contactResponseItems\" :key=\"`contact-response-${item}`\">{{ item }}</span>\n"
                "      </div>\n"
                f"{contact_intake_bridge}"
                + (
                    "      <div class=\"contact-handoff-grid\">\n"
                    "        <article v-for=\"item in contactHandoffCards\" :key=\"`contact-handoff-${item.label}`\" class=\"contact-handoff-card\">\n"
                    "          <span>{{ item.label }}</span>\n"
                    "          <strong>{{ item.value }}</strong>\n"
                    "        </article>\n"
                    "      </div>\n"
                    if not personal_portfolio_mode
                    else ""
                )
                +
                "      <div :class=\"['contact-form-shell', { 'contact-form-shell--business': !personalPortfolioMode }]\">\n"
                + (
                    "        <div class=\"contact-form-intake\">\n"
                    "          <strong>把这三项先发给我们，会更快进入建议阶段</strong>\n"
                    "          <div class=\"contact-form-checklist\">\n"
                    "            <span>产品现在在什么阶段</span>\n"
                    "            <span>最想先讲清的价值差异</span>\n"
                    "            <span>希望官网承接什么动作</span>\n"
                    "          </div>\n"
                    "        </div>\n"
                    if not personal_portfolio_mode
                    else ""
                )
                + "        <div class=\"contact-form-panel\">\n"
                + "          <form class=\"contact-form\" @submit.prevent=\"submitContact\">\n"
                + f"            <label v-if=\"contactFields.includes('name')\" class=\"contact-field\"><span>怎么称呼你</span><input v-model=\"contactForm.name\" type=\"text\" placeholder=\"{contact_name_placeholder}\" required /></label>\n"
                + f"            <label v-if=\"contactFields.includes('email')\" class=\"contact-field\"><span>联系邮箱</span><input v-model=\"contactForm.email\" type=\"email\" placeholder=\"{contact_email_placeholder}\" required /></label>\n"
                + f"            <label v-if=\"contactFields.includes('message')\" class=\"contact-field\"><span>{'想先讨论什么' if not personal_portfolio_mode else '你想做什么'}</span><textarea v-model=\"contactForm.message\" rows=\"4\" placeholder=\"{contact_message_placeholder}\" required></textarea><small class=\"contact-field-hint\">{'建议直接写产品阶段、首页目标和希望承接的动作，2 到 4 句就足够开始。' if not personal_portfolio_mode else '建议直接写目标、内容范围和时间节奏，先把方向说清楚就够了。'}</small></label>\n"
                + "            <div class=\"contact-form-actions\">\n"
                + f"              <button type=\"submit\" :disabled=\"contactSent\">{{{{ contactSent ? '已收到咨询' : '{contact_submit_label}' }}}}</button>\n"
                + (
                    "              <span class=\"contact-submit-hint\">不会直接进入冗长流程，我们通常会先回一版简短建议，再决定下一步怎么推进。</span>\n"
                    if not personal_portfolio_mode
                    else ""
                )
                + "            </div>\n"
                + "          </form>\n"
                + (
                    "          <p class=\"contact-form-note\">收到后我们通常会先回一版建议：先收哪一屏、FAQ 要不要先上、演示入口怎么接。</p>\n"
                    if not personal_portfolio_mode
                    else ""
                )
                + (
                    "          <div v-if=\"contactSent\" class=\"contact-success-card\">\n"
                    "            <strong>已收到你的咨询</strong>\n"
                    "            <p>我们会先按当前阶段整理一版更短的首页建议，让下一步更容易判断。</p>\n"
                    "            <div class=\"contact-success-steps\">\n"
                    "              <span v-for=\"item in contactSuccessItems\" :key=\"`contact-success-${item}`\">{{ item }}</span>\n"
                    "            </div>\n"
                    "          </div>\n"
                    if not personal_portfolio_mode
                    else ""
                )
                + "        </div>\n"
                + "      </div>\n"
                "      <p v-if=\"contactSent && personalPortfolioMode\" class=\"contact-success\">已收到您的咨询，我们会尽快联系您。</p>\n"
                "    </section>\n"
                + (
                    "    <section class=\"landing-section\" data-landing=\"LeadCapture\">\n"
                    "      <h2>订阅更新</h2>\n"
                    "      <form class=\"contact-form\" @submit.prevent=\"submitLeadCapture\">\n"
                    "        <input v-model=\"leadForm.email\" type=\"email\" placeholder=\"输入邮箱，获取更新\" required />\n"
                    "        <button type=\"submit\">立即订阅</button>\n"
                    "      </form>\n"
                    "      <p v-if=\"leadSent\" class=\"contact-success\">邮箱已提交，我们会发送最新动态。</p>\n"
                    "    </section>\n"
                    if lead_capture_flow
                    else ""
                )
            )

        hero_kicker = "      <span class=\"hero-kicker\">PRODUCT SITE / FIT / TRUST</span>\n"
        if personal_portfolio_mode:
            hero_kicker = "      <span class=\"hero-kicker\">PERSONAL WORK / DESIGN / DELIVERY</span>\n"
        hero_brand_row = ""
        if not personal_portfolio_mode:
            hero_brand_row = (
                "      <div class=\"hero-brand-row\">\n"
                f"        <strong class=\"hero-brand-mark\">{display_brand}</strong>\n"
                "        <span class=\"hero-brand-tag\">定位清楚，演示更顺</span>\n"
                "      </div>\n"
            )
        hero_brand_grid = ""
        if not personal_portfolio_mode:
            hero_brand_grid = (
                "      <div class=\"hero-brand-grid\">\n"
                "        <article class=\"hero-brand-card hero-brand-card--fit\">\n"
                "          <span>01 适合对象</span>\n"
                "          <strong>产品团队 / 创业团队</strong>\n"
                "          <em>先看是否相关</em>\n"
                "        </article>\n"
                "        <article class=\"hero-brand-card hero-brand-card--scenario\">\n"
                "          <span>02 场景线索</span>\n"
                "          <strong>定位澄清 / 价值承接</strong>\n"
                "          <em>先看问题是否成立</em>\n"
                "        </article>\n"
                "        <article class=\"hero-brand-card hero-brand-card--next\">\n"
                "          <span>03 下一步动作</span>\n"
                "          <strong>FAQ / 演示 / 联系入口</strong>\n"
                "          <em>先看怎么继续</em>\n"
                "        </article>\n"
                "      </div>\n"
            )
        hero_memory_strip = ""
        if not personal_portfolio_mode:
            hero_memory_strip = (
                "      <div class=\"hero-memory-strip\">\n"
                "        <strong class=\"hero-memory-label\">首页判断法</strong>\n"
                "        <span>先定对象</span>\n"
                "        <span>再亮差异</span>\n"
                "        <span>后接动作</span>\n"
                "      </div>\n"
            )
        hero_decision_open = "      <div class=\"hero-decision-block\">\n" if not personal_portfolio_mode else ""
        hero_decision_close = "      </div>\n" if not personal_portfolio_mode else ""
        hero_persona_row = ""
        if personal_portfolio_mode:
            hero_persona_row = (
                "      <div class=\"hero-persona-row\">\n"
                "        <span v-for=\"item in heroPersonaItems\" :key=\"`persona-${item}`\" class=\"hero-persona-chip\">{{ item }}</span>\n"
                "      </div>\n"
            )
        hero_signature_strip = ""
        if personal_portfolio_mode:
            hero_signature_strip = (
                "      <div class=\"hero-signature-strip\">\n"
                "        <span class=\"hero-signature-label\">AUTHOR SIGNATURE</span>\n"
                "        <strong>我更在意先把语气、判断顺序和交付边界讲清，再去决定页面要不要更满、更热闹。</strong>\n"
                "        <div class=\"hero-signature-grid\">\n"
                "          <article v-for=\"item in heroSignatureItems\" :key=\"`hero-signature-${item.label}`\" class=\"hero-signature-card\">\n"
                "            <span>{{ item.label }}</span>\n"
                "            <em>{{ item.value }}</em>\n"
                "          </article>\n"
                "        </div>\n"
                "      </div>\n"
            )
        hero_signal_strip = ""
        if not personal_portfolio_mode:
            hero_signal_strip = (
                "      <div class=\"hero-signal-strip\">\n"
                "        <article v-for=\"item in aboutHighlights.slice(0, 3)\" :key=\"`hero-signal-${item}`\" class=\"hero-signal-card\">\n"
                "          <span class=\"hero-signal-dot\"></span>\n"
                "          <strong>{{ item }}</strong>\n"
                "        </article>\n"
                "      </div>\n"
            )
        personal_header_note = ""
        if personal_portfolio_mode:
            personal_header_note = (
                "      <div class=\"personal-header-note\">\n"
                "        <span v-for=\"item in personalHeaderItems\" :key=\"`personal-header-${item}`\">{{ item }}</span>\n"
                "      </div>\n"
            )
        personal_footer_signoff = ""
        if personal_portfolio_mode:
            personal_footer_signoff = (
                "      <div class=\"footer-signoff-strip\">\n"
                "        <span class=\"footer-signoff-label\">SIGNED OFF</span>\n"
                "        <div class=\"footer-signoff-grid\">\n"
                "          <span v-for=\"item in personalFooterItems\" :key=\"`personal-footer-${item}`\">{{ item }}</span>\n"
                "        </div>\n"
                "      </div>\n"
            )
        company_header_note = ""
        if not personal_portfolio_mode:
            company_header_note = (
                "      <div class=\"company-header-note\">\n"
                "        <span v-for=\"item in companyHeaderItems\" :key=\"`company-header-${item}`\">{{ item }}</span>\n"
                "      </div>\n"
            )
        company_brand_posture = ""
        if not personal_portfolio_mode:
            company_brand_posture = (
                "      <div class=\"hero-brand-posture\">\n"
                "        <span class=\"hero-brand-posture-label\">BRAND POSTURE</span>\n"
                "        <strong>先把产品值不值得继续看讲清，再把演示、咨询和下一步动作留给真的有兴趣的人。</strong>\n"
                "        <div class=\"hero-brand-posture-grid\">\n"
                "          <article v-for=\"item in companyBrandPostureItems\" :key=\"`company-posture-${item.label}`\" class=\"hero-brand-posture-card\">\n"
                "            <span>{{ item.label }}</span>\n"
                "            <em>{{ item.value }}</em>\n"
                "          </article>\n"
                "        </div>\n"
                "      </div>\n"
            )
        company_footer_signoff = ""
        if not personal_portfolio_mode:
            company_footer_signoff = (
                "      <div class=\"company-footer-signoff\">\n"
                "        <span class=\"company-footer-signoff-label\">FINAL BRAND LINE</span>\n"
                "        <div class=\"company-footer-signoff-grid\">\n"
                "          <span v-for=\"item in companyFooterItems\" :key=\"`company-footer-${item}`\">{{ item }}</span>\n"
                "        </div>\n"
            "      </div>\n"
            )
        about_section = ""
        if single_page_landing:
            about_path_strip = (
                "      <div class=\"section-path-strip\">\n"
                "        <span class=\"section-path-current\">01 产品介绍</span>\n"
                "        <span class=\"section-path-next\">下一步：产品能力</span>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            about_feature_bridge = (
                "      <div class=\"section-proof-bridge section-proof-bridge--about\">\n"
                "        <span class=\"section-proof-bridge-label\">ABOUT TO FEATURES</span>\n"
                "        <strong>适合对象、关键场景和价值差异已经对齐，下一步看首页怎么把这些判断承接成更具体的能力表达。</strong>\n"
                "        <div class=\"section-proof-bridge-strip\">\n"
                "          <span class=\"section-proof-bridge-current\">当前：对象 / 场景 / 差异</span>\n"
                "          <span class=\"section-proof-bridge-next\">下一步：能力承接</span>\n"
                "        </div>\n"
                "      </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            about_section = (
                "    <section id=\"about\" class=\"landing-section about-section\" data-landing=\"About\">\n"
                f"      <h2>{about_title}</h2>\n"
                f"{about_path_strip}"
                "      <div class=\"about-shell\">\n"
                "        <div class=\"about-copy\">\n"
                f"          <p>{about_body}</p>\n"
                f"          <p class=\"about-note\">{about_note}</p>\n"
                "        </div>\n"
                "        <div class=\"about-points\">\n"
                "          <article v-for=\"item in aboutHighlights\" :key=\"`about-${item}`\">\n"
                "            <span class=\"about-point-dot\"></span>\n"
                "            <strong>{{ item }}</strong>\n"
                "          </article>\n"
                "        </div>\n"
                "      </div>\n"
                f"{about_feature_bridge}"
                "    </section>\n"
            )
        features_path_strip = (
            "      <div class=\"section-path-strip\">\n"
            "        <span class=\"section-path-current\">02 产品能力</span>\n"
            "        <span class=\"section-path-next\">下一步：客户评价</span>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        features_trust_bridge = (
            "      <div class=\"section-proof-bridge section-proof-bridge--features\">\n"
            "        <span class=\"section-proof-bridge-label\">FEATURES TO TRUST</span>\n"
            "        <strong>能力层先回答这页怎么承接前面的判断，下一步再看真实团队为什么会觉得这种官网更好用。</strong>\n"
            "        <div class=\"section-proof-bridge-strip\">\n"
            "          <span class=\"section-proof-bridge-current\">当前：能力承接</span>\n"
            "          <span class=\"section-proof-bridge-next\">下一步：团队反馈</span>\n"
            "        </div>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        testimonials_path_strip = (
            "      <div class=\"section-path-strip\">\n"
            "        <span class=\"section-path-current\">03 客户评价</span>\n"
            "        <span class=\"section-path-next\">下一步：常见问题</span>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        trust_faq_bridge = (
            "      <div class=\"section-proof-bridge section-proof-bridge--trust\">\n"
            "        <span class=\"section-proof-bridge-label\">TRUST TO FAQ</span>\n"
            "        <strong>团队反馈先说明这类首页为什么更容易承接销售和演示，下一步再把来访者最常见的判断问题提前讲清楚。</strong>\n"
            "        <div class=\"section-proof-bridge-strip\">\n"
            "          <span class=\"section-proof-bridge-current\">当前：团队反馈</span>\n"
            "          <span class=\"section-proof-bridge-next\">下一步：售前判断</span>\n"
            "        </div>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        cta_close_strip = (
            "      <div class=\"cta-close-strip\">\n"
            "        <span class=\"cta-close-current\">01 发来当前阶段与目标</span>\n"
            "        <span class=\"cta-close-next\">02 收到首页建议</span>\n"
            "        <span class=\"cta-close-next\">03 再决定怎么推进</span>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        intake_closure_bridge = (
            "      <div class=\"intake-closure-bridge\">\n"
            "        <span class=\"intake-closure-bridge-label\">INTAKE TO CLOSURE</span>\n"
            "        <strong>前面已经把阶段、首页目标和承接动作收进咨询 intake，下一步就把预期收成更短的 closing loop，避免最后只剩一个孤立按钮。</strong>\n"
            "        <div class=\"intake-closure-bridge-strip\">\n"
            "          <span class=\"intake-closure-bridge-current\">当前：已发阶段 / 目标 / 动作</span>\n"
            "          <span class=\"intake-closure-bridge-next\">下一步：确认建议与推进方式</span>\n"
            "        </div>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        cta_success_bridge = (
            "      <div v-if=\"contactSent && !personalPortfolioMode\" class=\"cta-success-bridge\">\n"
            "        <span class=\"cta-success-bridge-label\">POST SUBMIT</span>\n"
            "        <strong>咨询已收到，接下来我们会先回一版更短的首页建议，再决定要不要继续推进页面制作。</strong>\n"
            "        <div class=\"cta-success-bridge-strip\">\n"
            "          <span class=\"cta-success-bridge-current\">已收到当前阶段与目标</span>\n"
            "          <span class=\"cta-success-bridge-next\">先看首页建议</span>\n"
            "          <span class=\"cta-success-bridge-next\">再决定是否继续推进</span>\n"
            "        </div>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        cta_landing_bridge = (
            "      <div v-if=\"contactSent && !personalPortfolioMode\" class=\"cta-landing-bridge\">\n"
            "        <span class=\"cta-landing-bridge-label\">CLOSURE TO LANDING</span>\n"
            "        <strong>前面已经确认过建议和推进方式，下一步就把这次咨询收进一个更明确的最终页面落点，而不是直接掉进普通 footer。</strong>\n"
            "        <div class=\"cta-landing-bridge-strip\">\n"
            "          <span class=\"cta-landing-bridge-current\">当前：已确认建议与推进方式</span>\n"
            "          <span class=\"cta-landing-bridge-next\">下一步：进入最终页面落点</span>\n"
            "        </div>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )
        footer_success_bridge = (
            "      <div v-if=\"contactSent && !personalPortfolioMode\" class=\"footer-success-bridge\">\n"
            "        <span class=\"footer-success-bridge-label\">FINAL LANDING</span>\n"
            "        <strong>咨询已经进入后续沟通，你可以继续回看产品介绍、客户评价，或回到联系我们补充更多上下文。</strong>\n"
            "        <div class=\"footer-success-bridge-strip\">\n"
            "          <span class=\"footer-success-bridge-current\">已进入后续沟通</span>\n"
            "          <span class=\"footer-success-bridge-next\">继续回看产品介绍 / 客户评价</span>\n"
            "        </div>\n"
            "      </div>\n"
            if not personal_portfolio_mode
            else ""
        )

        home_sections = (
            "    <section id=\"hero\" class=\"landing-hero\" data-landing=\"Hero\">\n"
            f"{hero_kicker}"
            f"{hero_brand_row}"
            f"{company_brand_posture}"
            f"{hero_brand_grid}"
            "      <div class=\"hero-copy-block\">\n"
            f"        <h1>{hero_title}</h1>\n"
            f"        <p>{hero_subtitle}</p>\n"
            "      </div>\n"
            f"{hero_decision_open}"
            f"{hero_memory_strip}"
            f"{hero_persona_row}"
            f"{hero_signature_strip}"
            "      <div class=\"hero-actions\">\n"
            f"        <button type=\"button\" @click=\"go({cta_primary_target_expr})\">{cta_primary}</button>\n"
            f"        <button type=\"button\" class=\"ghost\" @click=\"go({cta_secondary_target_expr})\">{cta_secondary}</button>\n"
            "      </div>\n"
            f"{hero_decision_close}"
            f"{hero_signal_strip}"
            "    </section>\n"
            f"{about_section}"
            f"{stats_section}"
            f"{logo_section}"
            "    <section id=\"features\" class=\"landing-section\" data-landing=\"FeatureGrid\">\n"
            f"      <h2>{feature_title}</h2>\n"
            f"{features_path_strip}"
            "      <div class=\"pill-grid\">\n"
            "        <article v-for=\"(item, index) in featureItems\" :key=\"`feature-${item}`\">\n"
            "          <strong>{{ item }}</strong>\n"
            "          <span>{{ featureDescriptions[index] || item }}</span>\n"
            "        </article>\n"
            "      </div>\n"
            f"{features_trust_bridge}"
            "    </section>\n"
            f"{team_section}"
            f"{jobs_section}"
            f"{portfolio_section}"
            f"{home_pricing_section}"
            "    <section id=\"testimonials\" class=\"landing-section\" data-landing=\"Testimonial\">\n"
            f"      <h2>{testimonial_title}</h2>\n"
            f"      <p class=\"section-lead\">{testimonial_intro}</p>\n"
            f"{testimonials_path_strip}"
            "      <div class=\"quote-grid\">\n"
            "        <article v-for=\"item in testimonialCards\" :key=\"`quote-${item.quote}-${item.role}`\" class=\"quote-card\">\n"
            "          <span v-if=\"item.context\" class=\"quote-context\">{{ item.context }}</span>\n"
            "          <p class=\"quote-copy\">{{ item.quote }}</p>\n"
            "          <div class=\"quote-meta\">\n"
            "            <strong>{{ item.role }}</strong>\n"
            "            <span>{{ item.result }}</span>\n"
            "          </div>\n"
            "        </article>\n"
            "      </div>\n"
            f"{trust_faq_bridge}"
            "    </section>\n"
            f"{faq_section}"
            f"{home_contact_section}"
            "    <section id=\"cta\" class=\"landing-section cta\" data-landing=\"CTA\">\n"
            f"      <h2>{cta_title}</h2>\n"
            f"{intake_closure_bridge}"
            f"      <p class=\"cta-note\">{cta_note}</p>\n"
            "      <div class=\"cta-capture-strip\">\n"
            "        <span v-for=\"item in ctaCaptureItems\" :key=\"`cta-capture-${item}`\">{{ item }}</span>\n"
            "      </div>\n"
            f"{cta_success_bridge}"
            f"{cta_landing_bridge}"
            f"{cta_close_strip}"
            f"      <button type=\"button\" @click=\"go({cta_button_target_expr})\">{cta_button}</button>\n"
            "    </section>\n"
        )

        about_sections = (
            "    <section class=\"landing-hero\" data-landing=\"Hero\">\n"
            f"      <h1>{hero_title}</h1>\n"
            f"      <p>{hero_subtitle}</p>\n"
            "    </section>\n"
            "    <section class=\"landing-section\">\n"
            "      <h2>我们的使命</h2>\n"
            "      <p>聚焦 AI 产品与效率系统，帮助团队以更低成本交付更高质量结果。</p>\n"
            "    </section>\n"
        )

        feature_sections = (
            "    <section class=\"landing-section\" data-landing=\"FeatureGrid\">\n"
            f"      <h1>{feature_title}</h1>\n"
            "      <div class=\"pill-grid\">\n"
            "        <article v-for=\"item in featureItems\" :key=\"`feature-${item}`\">{{ item }}</article>\n"
            "      </div>\n"
            "    </section>\n"
        )

        pricing_sections = (
            "    <section id=\"pricing\" class=\"landing-section\" data-landing=\"Pricing\">\n"
            f"      <h1>{pricing_title}</h1>\n"
            "      <div class=\"price-grid\">\n"
            "        <article v-for=\"plan in pricingItems\" :key=\"`plan-${plan}`\">\n"
            "          <h3>{{ plan }}</h3>\n"
            "          <p>适合快速验证与稳定增长场景。</p>\n"
            "          <button type=\"button\" @click=\"go('/contact')\">咨询方案</button>\n"
            "        </article>\n"
            "      </div>\n"
            "    </section>\n"
        )

        contact_sections = (
            "    <section id=\"contact\" class=\"landing-section\" data-landing=\"Contact\">\n"
            f"      <h1>{contact_title}</h1>\n"
            "      <div :class=\"['contact-form-shell', { 'contact-form-shell--business': !personalPortfolioMode }]\">\n"
            + (
                "        <div class=\"contact-form-intake\">\n"
                "          <strong>把这三项先发给我们，会更快进入建议阶段</strong>\n"
                "          <div class=\"contact-form-checklist\">\n"
                "            <span>产品现在在什么阶段</span>\n"
                "            <span>最想先讲清的价值差异</span>\n"
                "            <span>希望官网承接什么动作</span>\n"
                "          </div>\n"
                "        </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            + "      <div class=\"contact-form-panel\">\n"
            + "        <form class=\"contact-form\" @submit.prevent=\"submitContact\">\n"
            + f"          <label v-if=\"contactFields.includes('name')\" class=\"contact-field\"><span>怎么称呼你</span><input v-model=\"contactForm.name\" type=\"text\" placeholder=\"{contact_name_placeholder}\" required /></label>\n"
            + f"          <label v-if=\"contactFields.includes('email')\" class=\"contact-field\"><span>联系邮箱</span><input v-model=\"contactForm.email\" type=\"email\" placeholder=\"{contact_email_placeholder}\" required /></label>\n"
            + f"          <label v-if=\"contactFields.includes('message')\" class=\"contact-field\"><span>{'想先讨论什么' if not personal_portfolio_mode else '你想做什么'}</span><textarea v-model=\"contactForm.message\" rows=\"4\" placeholder=\"{contact_message_placeholder}\" required></textarea><small class=\"contact-field-hint\">{'建议直接写产品阶段、首页目标和希望承接的动作，2 到 4 句就足够开始。' if not personal_portfolio_mode else '建议直接写目标、内容范围和时间节奏，先把方向说清楚就够了。'}</small></label>\n"
            + "          <div class=\"contact-form-actions\">\n"
            + f"            <button type=\"submit\" :disabled=\"contactSent\">{{{{ contactSent ? '已收到咨询' : '{contact_submit_label}' }}}}</button>\n"
            + (
                "            <span class=\"contact-submit-hint\">不会直接进入冗长流程，我们通常会先回一版简短建议，再决定下一步怎么推进。</span>\n"
                if not personal_portfolio_mode
                else ""
            )
            + "          </div>\n"
            + "        </form>\n"
            + (
                "        <p class=\"contact-form-note\">收到后我们通常会先回一版建议：先收哪一屏、FAQ 要不要先上、演示入口怎么接。</p>\n"
                if not personal_portfolio_mode
                else ""
            )
            + (
                "        <div v-if=\"contactSent\" class=\"contact-success-card\">\n"
                "          <strong>已收到你的咨询</strong>\n"
                "          <p>我们会先按当前阶段整理一版更短的首页建议，让下一步更容易判断。</p>\n"
                "          <div class=\"contact-success-steps\">\n"
                "            <span v-for=\"item in contactSuccessItems\" :key=\"`contact-success-${item}`\">{{ item }}</span>\n"
                "          </div>\n"
                "        </div>\n"
                if not personal_portfolio_mode
                else ""
            )
            + "      </div>\n"
            + "    </div>\n"
            "      <p v-if=\"contactSent && personalPortfolioMode\" class=\"contact-success\">已收到您的咨询，我们会尽快联系您。</p>\n"
            "    </section>\n"
            + (
                "    <section class=\"landing-section\" data-landing=\"LeadCapture\">\n"
                "      <h2>订阅更新</h2>\n"
                "      <form class=\"contact-form\" @submit.prevent=\"submitLeadCapture\">\n"
                "        <input v-model=\"leadForm.email\" type=\"email\" placeholder=\"输入邮箱，获取更新\" required />\n"
                "        <button type=\"submit\">立即订阅</button>\n"
                "      </form>\n"
                "      <p v-if=\"leadSent\" class=\"contact-success\">邮箱已提交，我们会发送最新动态。</p>\n"
                "    </section>\n"
                if lead_capture_flow
                else ""
            )
        )

        page_sections = home_sections
        if page_path == "/about":
            page_sections = about_sections
        elif page_path == "/features":
            page_sections = feature_sections
        elif page_path == "/pricing":
            page_sections = pricing_sections
        elif page_path == "/contact":
            page_sections = contact_sections

        return (
            "<template>\n"
            f"  <section class=\"landing-page{' personal-portfolio' if personal_portfolio_mode else ''}\">\n"
            "    <header class=\"landing-header\" data-landing=\"Header\">\n"
            f"      <button class=\"brand\" type=\"button\" @click=\"go('/')\">{display_brand}</button>\n"
            f"{personal_header_note}"
            f"{company_header_note}"
            "      <nav>\n"
            "        <button type=\"button\" v-for=\"link in navLinks\" :key=\"`${link.target}-${link.label}`\" @click=\"go(link.target)\">{{ link.label }}</button>\n"
            "      </nav>\n"
            "    </header>\n"
            f"{page_sections}"
            "    <footer id=\"footer\" class=\"landing-footer\" data-landing=\"Footer\">\n"
            f"{footer_success_bridge}"
            f"      <strong>{footer_brand}</strong>\n"
            f"{personal_footer_signoff}"
            f"{company_footer_signoff}"
            "      <div class=\"links\">\n"
            "        <button type=\"button\" v-for=\"item in footerLinks\" :key=\"`footer-${item}`\" @click=\"go(linkToTarget(item))\">{{ item }}</button>\n"
            "      </div>\n"
            f"      <small>© 2026 {display_brand}. All rights reserved.</small>\n"
            "    </footer>\n"
            "  </section>\n"
            "</template>\n\n"
            "<script setup>\n"
            "import { reactive, ref } from 'vue'\n"
            "import { useRouter } from 'vue-router'\n\n"
            "const router = useRouter()\n"
            f"const singlePageLanding = {json.dumps(single_page_landing)}\n"
            f"const navLinks = {json.dumps(nav_links, ensure_ascii=False)}\n"
            f"const aboutHighlights = {json.dumps(about_highlights, ensure_ascii=False)}\n"
            f"const featureItems = {json.dumps(feature_items, ensure_ascii=False)}\n"
            f"const featureDescriptions = {json.dumps(feature_descriptions, ensure_ascii=False)}\n"
            f"const testimonialItems = {json.dumps(testimonial_items, ensure_ascii=False)}\n"
            f"const testimonialCards = {json.dumps(testimonial_cards, ensure_ascii=False)}\n"
            f"const pricingItems = {json.dumps(pricing_items, ensure_ascii=False)}\n"
            f"const contactFields = {json.dumps(contact_fields, ensure_ascii=False)}\n"
            f"const contactResponseItems = {json.dumps(contact_response_items, ensure_ascii=False)}\n"
            f"const contactSuccessItems = {json.dumps(contact_success_items, ensure_ascii=False)}\n"
            f"const contactHandoffCards = {json.dumps(contact_handoff_cards, ensure_ascii=False)}\n"
            f"const ctaCaptureItems = {json.dumps(cta_capture_items, ensure_ascii=False)}\n"
            f"const footerLinks = {json.dumps(footer_links, ensure_ascii=False)}\n"
            f"const personalHeaderItems = {json.dumps(['独立编辑式交付', '案例按判断顺序排布', '先讲清，再讲漂亮'] if personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const personalFooterItems = {json.dumps(['Edited for clarity', 'Built for reuse', 'Kept easy to continue'] if personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const companyHeaderItems = {json.dumps(['少讲形容词', '多讲对象与动作', '首页先收判断'] if not personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const companyFooterItems = {json.dumps(['Fit before hype', 'Proof before promise', 'Action after clarity'] if not personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const singlePageLabelTargets = {json.dumps(single_page_label_targets, ensure_ascii=False)}\n"
            f"const faqItems = {json.dumps(faq_items, ensure_ascii=False)}\n"
            f"const teamMembers = {json.dumps(team_members, ensure_ascii=False)}\n"
            f"const statsItems = {json.dumps(stats_items, ensure_ascii=False)}\n"
            f"const logoItems = {json.dumps(logo_items, ensure_ascii=False)}\n"
            f"const jobsItems = {json.dumps(jobs_items, ensure_ascii=False)}\n"
            f"const heroPersonaItems = {json.dumps(['独立顾问型合作', '内容与产品表达', '结构设计与前端落地'] if personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const heroSignatureItems = {json.dumps([{'label': '工作方法', 'value': '先定语气与结构，再进视觉层'}, {'label': '合作方式', 'value': '像一起编辑一份公开作品，而不是外包接单'}, {'label': '交付判断', 'value': '优先保留可复用、可继续讲的页面骨架'}] if personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const companyBrandPostureItems = {json.dumps([{'label': '判断句', 'value': '先把产品值不值得继续看讲清。'}, {'label': '首页职责', 'value': '先收对象、差异和下一步动作。'}, {'label': '演示方式', 'value': '先让人判断，再决定要不要约演示。'}] if not personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const portfolioItems = {json.dumps(portfolio_items, ensure_ascii=False)}\n"
            f"const portfolioCurationItems = {json.dumps([{'label': '先看判断', 'value': '先放最能说明定位与取舍的案子'}, {'label': '再看表达', 'value': '再看页面怎么把内容讲得更像作者本人'}, {'label': '最后看交付', 'value': '最后看是否真的能继续拿去使用和复用'}] if personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const portfolioMeta = {json.dumps(portfolio_meta, ensure_ascii=False)}\n"
            f"const portfolioDetails = {json.dumps(portfolio_details, ensure_ascii=False)}\n"
            f"const portfolioOutcomes = {json.dumps(portfolio_outcomes, ensure_ascii=False)}\n"
            f"const portfolioDescriptions = {json.dumps(portfolio_descriptions, ensure_ascii=False)}\n"
            f"const portfolioSequenceNotes = {json.dumps(['先把信任感和合作边界讲清。', '先把价值主张和承接动作讲清。', '先把旧内容重组为可继续使用的入口。'] if personal_portfolio_mode else [], ensure_ascii=False)}\n"
            f"const personalPortfolioMode = {json.dumps(personal_portfolio_mode)}\n"
            f"const pageName = {json.dumps(page_name, ensure_ascii=False)}\n"
            f"const contactSectionEnabled = {json.dumps(page_path == '/contact' or (single_page_landing and contact_present))}\n"
            f"const contactFlowEnabled = {json.dumps(bool(contact_submit_flow))}\n"
            f"const contactFlowId = {json.dumps(contact_submit_flow.get('form_id', 'contact_form'), ensure_ascii=False)}\n"
            f"const leadCaptureEnabled = {json.dumps(bool(lead_capture_flow))}\n"
            f"const leadCaptureField = {json.dumps(lead_capture_flow.get('field', 'email'), ensure_ascii=False)}\n"
            "const contactSent = ref(false)\n"
            "const leadSent = ref(false)\n"
            "const contactForm = reactive({ name: '', email: '', message: '' })\n"
            "const leadForm = reactive({ email: '' })\n\n"
            "function linkToTarget(label) {\n"
            "  const text = String(label || '').trim().toLowerCase()\n"
            "  if (singlePageLanding && singlePageLabelTargets[text]) return singlePageLabelTargets[text]\n"
            "  if (text === 'home' || text === '首页') return '/'\n"
            "  if (text === 'about' || text === '关于' || text === '关于我们') return '/about'\n"
            "  if (text === 'features' || text === '功能' || text === '能力') return '/features'\n"
            "  if (text === 'pricing' || text === '价格' || text === '方案') return '/pricing'\n"
            "  if (text === 'contact' || text === '联系我们' || text === '联系') return '/contact'\n"
            "  return '/'\n"
            "}\n\n"
            "function scrollToTarget(target) {\n"
            "  if (!singlePageLanding || !target || !target.startsWith('#')) return false\n"
            "  const node = document.getElementById(target.slice(1))\n"
            "  if (!node) return false\n"
            "  node.scrollIntoView({ behavior: 'smooth', block: 'start' })\n"
            "  if (window.location.hash !== target) {\n"
            "    window.history.replaceState(null, '', target)\n"
            "  }\n"
            "  return true\n"
            "}\n\n"
            "function go(target) {\n"
            "  if (!target) return\n"
            "  if (scrollToTarget(target)) return\n"
            "  router.push(target)\n"
            "}\n\n"
            "function submitContact() {\n"
            "  if (!contactSectionEnabled) return\n"
            "  if (contactFlowEnabled) {\n"
            "    console.log('CONTACT_SUBMIT', { form_id: contactFlowId, payload: { ...contactForm } })\n"
            "  }\n"
            "  contactSent.value = true\n"
            "  contactForm.name = ''\n"
            "  contactForm.email = ''\n"
            "  contactForm.message = ''\n"
            "}\n"
            "\n"
            "function submitLeadCapture() {\n"
            "  if (!leadCaptureEnabled) return\n"
            "  console.log('LEAD_CAPTURE', { field: leadCaptureField, payload: { ...leadForm } })\n"
            "  leadSent.value = true\n"
            "}\n"
            "</script>\n\n"
            "<style scoped>\n"
            ".landing-page { display: grid; gap: 18px; width: min(1120px, calc(100% - 24px)); margin: 0 auto; padding: 18px 0 28px; font-family: 'Avenir Next', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; }\n"
            ".landing-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 16px; padding: 12px 16px; background: rgba(15, 23, 42, 0.94); color: #f8fafc; box-shadow: 0 18px 50px rgba(15, 23, 42, 0.16); backdrop-filter: blur(10px); }\n"
            ".landing-header .brand { border: 0; background: transparent; font-weight: 700; font-size: 18px; letter-spacing: 0.02em; color: inherit; cursor: pointer; }\n"
            ".landing-header nav { display: flex; gap: 8px; flex-wrap: wrap; }\n"
            ".landing-header nav button { border: 1px solid rgba(226, 232, 240, 0.24); background: rgba(255, 255, 255, 0.96); color: #0f172a; border-radius: 999px; padding: 7px 14px; cursor: pointer; font-weight: 600; }\n"
            ".landing-hero { position: relative; overflow: hidden; border: 1px solid #cfe0ff; background: radial-gradient(circle at top left, rgba(255,255,255,0.98), rgba(231,242,255,0.95) 52%, rgba(217,229,255,0.92)); border-radius: 22px; padding: 38px 28px; display: grid; gap: 14px; box-shadow: 0 28px 60px rgba(37, 99, 235, 0.12); }\n"
            ".landing-hero::after { content: ''; position: absolute; right: -40px; top: -60px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(59,130,246,0.22), rgba(59,130,246,0)); pointer-events: none; }\n"
            ".hero-kicker { position: relative; z-index: 1; display: inline-flex; width: fit-content; padding: 6px 10px; border-radius: 999px; background: rgba(15, 23, 42, 0.06); color: #1d4ed8; font-size: 12px; letter-spacing: 0.12em; font-weight: 700; }\n"
            ".landing-hero h1 { position: relative; z-index: 1; margin: 0; max-width: 10ch; font-size: 44px; line-height: 1.05; letter-spacing: -0.03em; color: #eff6ff; text-shadow: 0 1px 0 rgba(15, 23, 42, 0.05); }\n"
            ".landing-page:not(.personal-portfolio) .landing-header { position: relative; overflow: hidden; border-color: rgba(56, 189, 248, 0.28); background: linear-gradient(135deg, rgba(8, 15, 31, 0.99), rgba(11, 31, 58, 0.98) 38%, rgba(15, 23, 42, 0.97)); box-shadow: 0 22px 58px rgba(15, 23, 42, 0.32); }\n"
            ".landing-page:not(.personal-portfolio) .landing-header::before { content: ''; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(103,232,249,0.14), rgba(255,255,255,0) 28%, rgba(96,165,250,0.12) 72%, rgba(255,255,255,0)); pointer-events: none; }\n"
            ".landing-page:not(.personal-portfolio) .landing-header::after { content: ''; position: absolute; left: 16px; right: 16px; bottom: 0; height: 1px; background: linear-gradient(90deg, rgba(103,232,249,0.42), rgba(59,130,246,0.12), rgba(103,232,249,0)); pointer-events: none; }\n"
            ".landing-page:not(.personal-portfolio) .landing-header .brand, .landing-page:not(.personal-portfolio) .landing-footer strong { letter-spacing: 0.16em; text-transform: uppercase; font-size: 12px; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-weight: 800; }\n"
            ".landing-page:not(.personal-portfolio) .landing-header .brand { position: relative; padding-left: 16px; }\n"
            ".landing-page:not(.personal-portfolio) .landing-header .brand::before { content: ''; position: absolute; left: 0; top: 50%; width: 10px; height: 10px; border-radius: 999px; transform: translateY(-50%); background: radial-gradient(circle, rgba(103,232,249,1), rgba(59,130,246,0.92)); box-shadow: 0 0 0 5px rgba(103,232,249,0.16); }\n"
            ".landing-page:not(.personal-portfolio) .landing-header nav button { position: relative; border-color: rgba(125, 211, 252, 0.22); background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(15,23,42,0.18)); color: #e0f2fe; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .landing-header nav button::after { content: ''; position: absolute; inset: 0; border-radius: inherit; background: linear-gradient(90deg, rgba(103,232,249,0.08), rgba(255,255,255,0)); opacity: 0.72; pointer-events: none; }\n"
            ".landing-page:not(.personal-portfolio) .company-header-note { position: relative; z-index: 1; display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; flex: 1; }\n"
            ".landing-page:not(.personal-portfolio) .company-header-note span { display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(8,15,31,0.18)); border: 1px solid rgba(125,211,252,0.22); color: #dbeafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .landing-hero { border-color: rgba(56, 189, 248, 0.28); background: linear-gradient(145deg, rgba(5,10,24,1), rgba(8,47,73,0.98) 28%, rgba(14,116,144,0.94) 56%, rgba(29,78,216,0.94)); box-shadow: 0 46px 100px rgba(10, 18, 34, 0.34); padding: 46px 32px; gap: 18px; }\n"
            ".landing-page:not(.personal-portfolio) .landing-hero::before { content: ''; position: absolute; inset: 0; background: linear-gradient(135deg, rgba(34,211,238,0.08), rgba(255,255,255,0) 42%, rgba(59,130,246,0.14)); pointer-events: none; }\n"
            ".landing-page:not(.personal-portfolio) .landing-hero::after { right: -20px; top: -36px; width: 280px; height: 280px; background: radial-gradient(circle, rgba(103,232,249,0.28), rgba(96,165,250,0)); }\n"
            ".landing-page:not(.personal-portfolio) .landing-hero .hero-kicker::after { content: ''; width: 26px; height: 1px; margin-left: 10px; background: linear-gradient(90deg, rgba(103,232,249,0.9), rgba(255,255,255,0)); }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-row { position: relative; z-index: 1; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-top: -2px; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-mark { display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.16), rgba(15,23,42,0.18)); border: 1px solid rgba(125,211,252,0.26); color: #f8fafc; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-weight: 800; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 10px 24px rgba(8,15,31,0.18); }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-tag { display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 999px; background: rgba(8,15,31,0.24); border: 1px solid rgba(191,219,254,0.2); color: #dbeafe; font-size: 12px; letter-spacing: 0.06em; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-posture { position: relative; z-index: 1; display: grid; gap: 12px; max-width: 760px; padding: 16px; border-radius: 18px; border: 1px solid rgba(125,211,252,0.24); background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(8,15,31,0.16) 42%, rgba(8,47,73,0.22)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 16px 30px rgba(8,15,31,0.18); }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-posture-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(207,250,254,0.14); border: 1px solid rgba(103,232,249,0.28); color: #cffafe; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 800; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-posture strong { color: #f8fafc; font-size: 16px; line-height: 1.7; max-width: 58ch; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-posture-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-posture-card { display: grid; gap: 6px; padding: 12px 14px; border-radius: 16px; border: 1px solid rgba(125,211,252,0.2); background: linear-gradient(180deg, rgba(255,255,255,0.1), rgba(8,15,31,0.14)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-posture-card span { color: #67e8f9; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-posture-card em { color: rgba(224,242,254,0.88); font-style: normal; font-size: 13px; line-height: 1.55; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-grid { position: relative; z-index: 1; display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; max-width: 760px; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-card { display: grid; gap: 7px; border: 1px solid rgba(125,211,252,0.24); border-radius: 16px; padding: 12px 14px; background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(8,15,31,0.16) 42%, rgba(8,47,73,0.22)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 14px 28px rgba(8, 15, 31, 0.16); }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-card span { color: rgba(191, 219, 254, 0.9); font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-card strong { color: #f8fafc; font-size: 14px; line-height: 1.45; font-weight: 700; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-card em { font-style: normal; color: rgba(224, 242, 254, 0.86); font-size: 12px; line-height: 1.45; }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-card--fit { border-color: rgba(103,232,249,0.34); background: linear-gradient(180deg, rgba(207,250,254,0.16), rgba(8,15,31,0.18) 42%, rgba(8,47,73,0.24)); }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-card--scenario { border-color: rgba(147,197,253,0.34); background: linear-gradient(180deg, rgba(219,234,254,0.16), rgba(8,15,31,0.18) 42%, rgba(10,36,79,0.24)); }\n"
            ".landing-page:not(.personal-portfolio) .hero-brand-card--next { border-color: rgba(96,165,250,0.34); background: linear-gradient(180deg, rgba(191,219,254,0.16), rgba(15,23,42,0.2) 42%, rgba(29,78,216,0.22)); }\n"
            ".landing-page:not(.personal-portfolio) .hero-copy-block { position: relative; z-index: 1; display: grid; gap: 12px; max-width: 64ch; margin-top: 2px; padding: 18px 18px 10px 18px; border-top: 1px solid rgba(125,211,252,0.24); border-left: 3px solid rgba(103,232,249,0.7); border-radius: 0 18px 18px 18px; background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(8,15,31,0.04)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }\n"
            ".landing-page:not(.personal-portfolio) .landing-hero h1 { position: relative; color: #f8fafc; text-shadow: none; max-width: 9.3ch; font-size: 60px; line-height: 0.98; letter-spacing: -0.06em; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-weight: 800; padding-bottom: 18px; margin-bottom: 2px; }\n"
            ".landing-page:not(.personal-portfolio) .landing-hero h1::after { content: ''; position: absolute; left: 2px; bottom: 0; width: 104px; height: 6px; border-radius: 999px; background: linear-gradient(90deg, rgba(103,232,249,0.96), rgba(59,130,246,0.92)); box-shadow: 0 0 0 4px rgba(103,232,249,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .landing-hero p { color: rgba(226, 232, 240, 0.92); max-width: 54ch; font-size: 18px; line-height: 1.8; }\n"
            ".landing-page:not(.personal-portfolio) .hero-decision-block { position: relative; z-index: 1; display: grid; gap: 10px; width: fit-content; max-width: 100%; padding: 10px 12px 12px; border-radius: 18px; border: 1px solid rgba(125,211,252,0.22); background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(8,15,31,0.08)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }\n"
            ".landing-page:not(.personal-portfolio) .hero-memory-strip { position: relative; z-index: 1; display: flex; flex-wrap: wrap; gap: 8px; margin-top: -2px; }\n"
            ".landing-page:not(.personal-portfolio) .hero-memory-label { display: inline-flex; align-items: center; min-height: 32px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(34,211,238,0.18), rgba(37,99,235,0.16)); border: 1px solid rgba(103,232,249,0.28); color: #f8fafc; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .hero-memory-strip span { display: inline-flex; align-items: center; min-height: 32px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.14), rgba(8,15,31,0.18)); border: 1px solid rgba(191,219,254,0.22); color: #e0f2fe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .hero-kicker { background: linear-gradient(180deg, rgba(56,189,248,0.16), rgba(59,130,246,0.12)); color: #dbeafe; border: 1px solid rgba(125, 211, 252, 0.24); box-shadow: inset 0 1px 0 rgba(255,255,255,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .hero-actions { gap: 12px; margin-top: 0; align-items: center; }\n"
            ".landing-page:not(.personal-portfolio) .hero-actions button { min-height: 48px; padding: 0 18px; border-radius: 14px; font-size: 14px; font-weight: 700; }\n"
            ".landing-page:not(.personal-portfolio) .hero-actions button:first-child { position: relative; min-height: 52px; padding: 0 48px 0 20px; border-radius: 16px; letter-spacing: 0.01em; background: linear-gradient(135deg, #2563eb, #1d4ed8 58%, #0f4cc7); box-shadow: 0 20px 40px rgba(29, 78, 216, 0.32), inset 0 1px 0 rgba(255,255,255,0.16); }\n"
            ".landing-page:not(.personal-portfolio) .hero-actions button:first-child::after { content: '↗'; position: absolute; right: 14px; top: 50%; transform: translateY(-50%); width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; border-radius: 999px; background: rgba(255,255,255,0.16); color: #eff6ff; font-size: 12px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.2); }\n"
            ".landing-page:not(.personal-portfolio) .hero-actions .ghost { position: relative; min-height: 46px; padding: 0 34px 0 18px; background: linear-gradient(180deg, rgba(15,23,42,0.08), rgba(15,23,42,0.18)); color: rgba(239,246,255,0.92); border-color: rgba(191, 219, 254, 0.18); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); backdrop-filter: blur(6px); }\n"
            ".landing-page:not(.personal-portfolio) .hero-actions .ghost::after { content: '→'; position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: rgba(224,242,254,0.72); font-size: 13px; font-weight: 700; }\n"
            ".landing-page:not(.personal-portfolio) .hero-signal-strip { position: relative; z-index: 1; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 8px; padding-top: 8px; }\n"
            ".landing-page:not(.personal-portfolio) .hero-signal-card { display: flex; gap: 10px; align-items: center; border: 1px solid rgba(125, 211, 252, 0.22); background: linear-gradient(180deg, rgba(255,255,255,0.12), rgba(8,47,73,0.18) 40%, rgba(15,23,42,0.28)); color: #eff6ff; border-radius: 14px; padding: 12px 14px; min-height: 56px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 16px 30px rgba(8, 15, 31, 0.2); }\n"
            ".landing-page:not(.personal-portfolio) .hero-signal-card strong { font-size: 13px; line-height: 1.4; font-weight: 700; letter-spacing: 0.01em; }\n"
            ".landing-page:not(.personal-portfolio) .hero-signal-dot { width: 8px; height: 8px; border-radius: 999px; background: #67e8f9; box-shadow: 0 0 0 5px rgba(103,232,249,0.18); flex: none; }\n"
            ".landing-page:not(.personal-portfolio) .landing-section { position: relative; border-color: rgba(96, 165, 250, 0.18); box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08); }\n"
            ".landing-page:not(.personal-portfolio) .landing-section::before { content: ''; position: absolute; inset: 0 0 auto 0; height: 1px; background: linear-gradient(90deg, rgba(255,255,255,0.76), rgba(255,255,255,0)); opacity: 0.8; pointer-events: none; }\n"
            ".landing-page:not(.personal-portfolio) .section-path-strip { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 18px; }\n"
            ".landing-page:not(.personal-portfolio) .section-path-strip span { display: inline-flex; align-items: center; min-height: 30px; padding: 0 12px; border-radius: 999px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }\n"
            ".landing-page:not(.personal-portfolio) .section-path-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); border: 1px solid rgba(56,189,248,0.22); color: #0f4cc7; box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }\n"
            ".landing-page:not(.personal-portfolio) .section-path-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); border: 1px solid rgba(191,219,254,0.56); color: #1e3a8a; }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge { display: grid; gap: 10px; margin-top: 14px; padding: 14px; border-radius: 18px; border: 1px solid rgba(191,219,254,0.6); background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.92)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.06); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.18); color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.82)); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.65; }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; padding: 0 12px; border-radius: 999px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.18); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; }\n"
            ".landing-page:not(.personal-portfolio) .about-section { border-color: rgba(56, 189, 248, 0.24); background: linear-gradient(160deg, rgba(255,255,255,0.99), rgba(240,249,255,0.97) 54%, rgba(224,242,254,0.93)); }\n"
            ".landing-page:not(.personal-portfolio) #features { border-color: rgba(96, 165, 250, 0.24); background: linear-gradient(160deg, rgba(255,255,255,0.99), rgba(239,246,255,0.97) 48%, rgba(224,231,255,0.93)); }\n"
            ".landing-page:not(.personal-portfolio) #testimonials { border-color: rgba(45, 212, 191, 0.24); background: linear-gradient(165deg, rgba(248,250,252,0.99), rgba(236,253,245,0.96) 50%, rgba(224,242,254,0.94)); }\n"
            ".landing-page:not(.personal-portfolio) #faq { border-color: rgba(251, 191, 36, 0.24); background: linear-gradient(165deg, rgba(255,255,255,0.99), rgba(255,251,235,0.96) 46%, rgba(248,250,252,0.94)); }\n"
            ".landing-page:not(.personal-portfolio) #contact { border-color: rgba(59, 130, 246, 0.22); background: linear-gradient(165deg, rgba(255,255,255,0.99), rgba(248,250,252,0.96) 42%, rgba(239,246,255,0.94)); }\n"
            ".landing-page:not(.personal-portfolio) #cta { border-color: rgba(30, 64, 175, 0.28); background: linear-gradient(160deg, rgba(239,246,255,0.98), rgba(224,231,255,0.96) 38%, rgba(219,234,254,0.94)); }\n"
            ".landing-page:not(.personal-portfolio) #about .section-path-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(14,165,233,0.1)); border-color: rgba(34,211,238,0.28); color: #0f766e; }\n"
            ".landing-page:not(.personal-portfolio) #about .section-path-next { border-color: rgba(125,211,252,0.54); color: #155e75; }\n"
            ".landing-page:not(.personal-portfolio) #features .section-path-current { background: linear-gradient(180deg, rgba(96,165,250,0.18), rgba(37,99,235,0.12)); border-color: rgba(96,165,250,0.3); color: #1d4ed8; }\n"
            ".landing-page:not(.personal-portfolio) #features .section-path-next { border-color: rgba(165,180,252,0.52); color: #3730a3; }\n"
            ".landing-page:not(.personal-portfolio) #testimonials .section-path-current { background: linear-gradient(180deg, rgba(45,212,191,0.18), rgba(16,185,129,0.12)); border-color: rgba(45,212,191,0.3); color: #047857; }\n"
            ".landing-page:not(.personal-portfolio) #testimonials .section-path-next { border-color: rgba(110,231,183,0.52); color: #065f46; }\n"
            ".landing-page:not(.personal-portfolio) #faq .section-path-current { background: linear-gradient(180deg, rgba(251,191,36,0.18), rgba(245,158,11,0.1)); border-color: rgba(251,191,36,0.34); color: #b45309; }\n"
            ".landing-page:not(.personal-portfolio) #faq .section-path-next { border-color: rgba(252,211,77,0.48); color: #92400e; }\n"
            ".landing-page:not(.personal-portfolio) #contact .section-path-current { background: linear-gradient(180deg, rgba(99,102,241,0.14), rgba(59,130,246,0.12)); border-color: rgba(99,102,241,0.3); color: #3730a3; }\n"
            ".landing-page:not(.personal-portfolio) #contact .section-path-next { border-color: rgba(129,140,248,0.42); color: #312e81; }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--about { border-color: rgba(34,211,238,0.34); background: linear-gradient(180deg, rgba(240,249,255,0.98), rgba(224,242,254,0.92)); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--about .section-proof-bridge-label { color: #0f766e; background: linear-gradient(180deg, rgba(204,251,241,0.94), rgba(207,250,254,0.9)); border-color: rgba(45,212,191,0.3); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--about .section-proof-bridge-current { background: linear-gradient(180deg, rgba(45,212,191,0.16), rgba(20,184,166,0.1)); color: #0f766e; border-color: rgba(45,212,191,0.24); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--about .section-proof-bridge-next { color: #155e75; border-color: rgba(125,211,252,0.46); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--features { border-color: rgba(96,165,250,0.34); background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(224,231,255,0.92)); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--features .section-proof-bridge-label { color: #1d4ed8; background: linear-gradient(180deg, rgba(219,234,254,0.94), rgba(224,231,255,0.9)); border-color: rgba(96,165,250,0.28); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--features .section-proof-bridge-current { background: linear-gradient(180deg, rgba(96,165,250,0.16), rgba(37,99,235,0.1)); color: #1d4ed8; border-color: rgba(96,165,250,0.26); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--features .section-proof-bridge-next { color: #3730a3; border-color: rgba(165,180,252,0.46); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--trust { border-color: rgba(45,212,191,0.34); background: linear-gradient(180deg, rgba(236,253,245,0.98), rgba(224,242,254,0.92)); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--trust .section-proof-bridge-label { color: #047857; background: linear-gradient(180deg, rgba(220,252,231,0.94), rgba(204,251,241,0.9)); border-color: rgba(45,212,191,0.3); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--trust .section-proof-bridge-current { background: linear-gradient(180deg, rgba(45,212,191,0.16), rgba(16,185,129,0.1)); color: #047857; border-color: rgba(45,212,191,0.24); }\n"
            ".landing-page:not(.personal-portfolio) .section-proof-bridge--trust .section-proof-bridge-next { color: #065f46; border-color: rgba(110,231,183,0.48); }\n"
            ".landing-page:not(.personal-portfolio) .faq-scan-strip span { background: linear-gradient(180deg, rgba(224,242,254,0.82), rgba(219,234,254,0.7)); color: #0f4cc7; border-color: rgba(56,189,248,0.28); box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }\n"
            ".landing-page:not(.personal-portfolio) .faq-scan-strip span:nth-child(1) { background: linear-gradient(180deg, rgba(254,240,138,0.28), rgba(252,211,77,0.18)); color: #92400e; border-color: rgba(251,191,36,0.28); }\n"
            ".landing-page:not(.personal-portfolio) .faq-scan-strip span:nth-child(2) { background: linear-gradient(180deg, rgba(191,219,254,0.28), rgba(147,197,253,0.18)); color: #1d4ed8; border-color: rgba(96,165,250,0.28); }\n"
            ".landing-page:not(.personal-portfolio) .faq-scan-strip span:nth-child(3) { background: linear-gradient(180deg, rgba(220,252,231,0.32), rgba(187,247,208,0.18)); color: #166534; border-color: rgba(110,231,183,0.28); }\n"
            ".landing-page:not(.personal-portfolio) .faq-copy-block { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(241,245,249,0.94)); border-color: rgba(226,232,240,0.96); }\n"
            ".landing-page:not(.personal-portfolio) .faq-followup-block { background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(224,242,254,0.92)); border-color: rgba(147,197,253,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.86); }\n"
            ".landing-page:not(.personal-portfolio) .faq-contact-bridge { background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(224,242,254,0.92)); border-color: rgba(147,197,253,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .faq-contact-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }\n"
            ".landing-page:not(.personal-portfolio) .faq-contact-bridge strong { color: #0f172a; }\n"
            ".landing-page:not(.personal-portfolio) .faq-contact-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }\n"
            ".landing-page:not(.personal-portfolio) .faq-contact-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }\n"
            ".landing-page:not(.personal-portfolio) .contact-entry-bridge { background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(248,250,252,0.96)); border-color: rgba(191,219,254,0.84); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88); }\n"
            ".landing-page:not(.personal-portfolio) .contact-entry-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }\n"
            ".landing-page:not(.personal-portfolio) .contact-entry-bridge strong { color: #0f172a; }\n"
            ".landing-page:not(.personal-portfolio) .contact-response-strip span { background: linear-gradient(180deg, rgba(224,242,254,0.82), rgba(219,234,254,0.68)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }\n"
            ".landing-page:not(.personal-portfolio) .contact-intake-bridge { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.92)); border-color: rgba(191,219,254,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 16px 28px rgba(15,23,42,0.06); }\n"
            ".landing-page:not(.personal-portfolio) .contact-intake-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }\n"
            ".landing-page:not(.personal-portfolio) .contact-intake-bridge strong { color: #0f172a; }\n"
            ".landing-page:not(.personal-portfolio) .contact-intake-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }\n"
            ".landing-page:not(.personal-portfolio) .contact-intake-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }\n"
            ".landing-page:not(.personal-portfolio) .contact-handoff-card { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(224,242,254,0.92)); border-color: rgba(96,165,250,0.2); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 16px 30px rgba(15, 23, 42, 0.08); }\n"
            ".landing-page:not(.personal-portfolio) .contact-handoff-card span { color: #0f4cc7; }\n"
            ".landing-page:not(.personal-portfolio) .contact-handoff-card strong { color: #0f172a; }\n"
            ".landing-page:not(.personal-portfolio) .intake-closure-bridge { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.92)); border-color: rgba(191,219,254,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .intake-closure-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }\n"
            ".landing-page:not(.personal-portfolio) .intake-closure-bridge strong { color: #0f172a; }\n"
            ".landing-page:not(.personal-portfolio) .intake-closure-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }\n"
            ".landing-page:not(.personal-portfolio) .intake-closure-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }\n"
            ".landing-page:not(.personal-portfolio) .cta-note { color: #1e3a8a; max-width: 48ch; font-weight: 600; }\n"
            ".landing-page:not(.personal-portfolio) .cta-capture-strip span { background: linear-gradient(180deg, rgba(224,242,254,0.82), rgba(219,234,254,0.68)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); box-shadow: inset 0 1px 0 rgba(255,255,255,0.84); }\n"
            ".landing-page:not(.personal-portfolio) .cta-success-bridge { background: linear-gradient(180deg, rgba(236,253,245,0.98), rgba(240,253,250,0.96)); border-color: rgba(110,231,183,0.56); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .cta-success-bridge-label { color: #166534; background: linear-gradient(180deg, rgba(220,252,231,0.96), rgba(209,250,229,0.92)); border-color: rgba(134,239,172,0.72); }\n"
            ".landing-page:not(.personal-portfolio) .cta-success-bridge strong { color: #14532d; }\n"
            ".landing-page:not(.personal-portfolio) .cta-success-bridge-current { background: linear-gradient(180deg, rgba(220,252,231,0.96), rgba(209,250,229,0.9)); color: #166534; border-color: rgba(134,239,172,0.72); }\n"
            ".landing-page:not(.personal-portfolio) .cta-success-bridge-next { background: linear-gradient(180deg, rgba(248,250,252,0.96), rgba(241,245,249,0.9)); color: #166534; border-color: rgba(187,247,208,0.7); }\n"
            ".landing-page:not(.personal-portfolio) .cta-landing-bridge { background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(224,242,254,0.92)); border-color: rgba(147,197,253,0.72); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 32px rgba(15,23,42,0.08); }\n"
            ".landing-page:not(.personal-portfolio) .cta-landing-bridge-label { color: #0f4cc7; background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); border-color: rgba(56,189,248,0.2); }\n"
            ".landing-page:not(.personal-portfolio) .cta-landing-bridge strong { color: #0f172a; }\n"
            ".landing-page:not(.personal-portfolio) .cta-landing-bridge-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }\n"
            ".landing-page:not(.personal-portfolio) .cta-landing-bridge-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }\n"
            ".landing-page:not(.personal-portfolio) .footer-success-bridge { background: linear-gradient(180deg, rgba(240,253,250,0.2), rgba(15,23,42,0.08)); border: 1px solid rgba(134,239,172,0.2); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }\n"
            ".landing-page:not(.personal-portfolio) .footer-success-bridge-label { color: #bbf7d0; background: rgba(34,197,94,0.12); border-color: rgba(134,239,172,0.26); }\n"
            ".landing-page:not(.personal-portfolio) .footer-success-bridge strong { color: #ecfdf5; }\n"
            ".landing-page:not(.personal-portfolio) .footer-success-bridge-current { background: rgba(34,197,94,0.16); color: #dcfce7; border-color: rgba(134,239,172,0.26); }\n"
            ".landing-page:not(.personal-portfolio) .footer-success-bridge-next { background: rgba(255,255,255,0.06); color: #dbeafe; border-color: rgba(191,219,254,0.18); }\n"
            ".landing-page:not(.personal-portfolio) .landing-footer { position: relative; overflow: hidden; border-color: rgba(59,130,246,0.24); background: linear-gradient(145deg, rgba(5,10,24,0.99), rgba(10,25,49,0.98) 40%, rgba(15,23,42,0.97)); box-shadow: 0 24px 48px rgba(8,15,31,0.26); }\n"
            ".landing-page:not(.personal-portfolio) .landing-footer::before { content: ''; position: absolute; inset: 0; background: linear-gradient(120deg, rgba(103,232,249,0.08), rgba(255,255,255,0) 38%, rgba(59,130,246,0.08)); pointer-events: none; }\n"
            ".landing-page:not(.personal-portfolio) .landing-footer::after { content: ''; position: absolute; left: 16px; right: 16px; top: 0; height: 1px; background: linear-gradient(90deg, rgba(103,232,249,0.38), rgba(59,130,246,0.12), rgba(103,232,249,0)); pointer-events: none; }\n"
            ".landing-page:not(.personal-portfolio) .landing-footer .links { position: relative; z-index: 1; }\n"
            ".landing-page:not(.personal-portfolio) .landing-footer button { border-color: rgba(125,211,252,0.2); background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(15,23,42,0.18)); color: #dbeafe; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06); }\n"
            ".landing-page:not(.personal-portfolio) .landing-footer small { color: rgba(191,219,254,0.72); }\n"
            ".landing-page:not(.personal-portfolio) .company-footer-signoff { position: relative; z-index: 1; display: grid; gap: 8px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(125,211,252,0.16); }\n"
            ".landing-page:not(.personal-portfolio) .company-footer-signoff-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(103,232,249,0.12); border: 1px solid rgba(125,211,252,0.22); color: #cffafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }\n"
            ".landing-page:not(.personal-portfolio) .company-footer-signoff-grid { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".landing-page:not(.personal-portfolio) .company-footer-signoff-grid span { display: inline-flex; align-items: center; min-height: 30px; padding: 0 12px; border-radius: 999px; background: linear-gradient(180deg, rgba(255,255,255,0.08), rgba(15,23,42,0.18)); border: 1px solid rgba(191,219,254,0.18); color: #dbeafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }\n"
            ".landing-page:not(.personal-portfolio) #cta .cta-note { color: #1e40af; }\n"
            ".landing-page:not(.personal-portfolio) #cta .cta-capture-strip span:nth-child(1) { background: linear-gradient(180deg, rgba(219,234,254,0.9), rgba(191,219,254,0.74)); color: #1d4ed8; }\n"
            ".landing-page:not(.personal-portfolio) #cta .cta-capture-strip span:nth-child(2) { background: linear-gradient(180deg, rgba(224,231,255,0.92), rgba(199,210,254,0.76)); color: #3730a3; }\n"
            ".landing-page:not(.personal-portfolio) #cta .cta-capture-strip span:nth-child(3) { background: linear-gradient(180deg, rgba(220,252,231,0.92), rgba(187,247,208,0.76)); color: #166534; }\n"
            ".landing-page:not(.personal-portfolio) .cta-close-strip span { box-shadow: inset 0 1px 0 rgba(255,255,255,0.86); }\n"
            ".landing-page:not(.personal-portfolio) .cta-close-current { background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.1)); color: #0f4cc7; border-color: rgba(56,189,248,0.24); }\n"
            ".landing-page:not(.personal-portfolio) .cta-close-next { background: linear-gradient(180deg, rgba(241,245,249,0.96), rgba(226,232,240,0.88)); color: #1e3a8a; border-color: rgba(191,219,254,0.56); }\n"
            ".landing-page:not(.personal-portfolio) .quote-card { border-color: rgba(96, 165, 250, 0.24); border-top: 3px solid rgba(14,165,233,0.9); background: linear-gradient(180deg, rgba(248,250,252,0.98), rgba(239,246,255,0.96)); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.8); }\n"
            ".landing-page:not(.personal-portfolio) .quote-card::before { content: 'TRUST SIGNAL'; display: inline-flex; width: fit-content; padding: 5px 9px; border-radius: 999px; background: linear-gradient(180deg, rgba(34,211,238,0.16), rgba(37,99,235,0.08)); color: #0f4cc7; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; }\n"
            ".landing-page:not(.personal-portfolio) .quote-copy { color: #1e293b; }\n"
            ".landing-page:not(.personal-portfolio) .quote-meta strong { color: #0f172a; }\n"
            ".landing-page:not(.personal-portfolio) .quote-meta span { color: #0f4cc7; }\n"
            ".landing-page:not(.personal-portfolio) .landing-section h2 { position: relative; padding-left: 18px; font-family: 'Avenir Next Condensed', 'Arial Narrow', 'Avenir Next', 'Helvetica Neue', sans-serif; font-size: 28px; letter-spacing: -0.045em; }\n"
            ".landing-page:not(.personal-portfolio) .landing-section h2::before { content: ''; position: absolute; left: 0; top: 4px; width: 6px; height: 24px; border-radius: 999px; background: linear-gradient(180deg, #38bdf8, #2563eb); box-shadow: 0 0 0 4px rgba(59,130,246,0.12); }\n"
            ".landing-page:not(.personal-portfolio) .faq-item { border-left: 3px solid rgba(14,165,233,0.9); }\n"
            ".landing-page:not(.personal-portfolio) .faq-summary-hint { background: linear-gradient(180deg, rgba(224,242,254,0.92), rgba(219,234,254,0.84)); color: #0f4cc7; border: 1px solid rgba(56,189,248,0.18); }\n"
            ".landing-page.personal-portfolio { gap: 22px; }\n"
            ".landing-page.personal-portfolio .landing-header { border-color: rgba(217, 119, 6, 0.16); background: linear-gradient(135deg, rgba(252,248,243,0.98), rgba(255,250,245,0.97)); color: #172554; box-shadow: 0 18px 42px rgba(148, 163, 184, 0.12); }\n"
            ".landing-page.personal-portfolio .landing-header .brand, .landing-page.personal-portfolio .landing-footer strong { letter-spacing: 0.08em; text-transform: uppercase; font-size: 13px; color: #1e3a8a; }\n"
            ".landing-page.personal-portfolio .personal-header-note { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; flex: 1; }\n"
            ".landing-page.personal-portfolio .personal-header-note span { display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,255,255,0.72); border: 1px solid rgba(251,191,36,0.22); color: #9a3412; font-size: 11px; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; }\n"
            ".landing-page.personal-portfolio .landing-header nav button { border-color: rgba(191, 219, 254, 0.55); background: rgba(255,255,255,0.86); color: #1e3a8a; box-shadow: inset 0 1px 0 rgba(255,255,255,0.85); }\n"
            ".landing-page.personal-portfolio .landing-hero { border-color: rgba(251, 191, 36, 0.34); background: linear-gradient(145deg, rgba(255,252,247,0.99), rgba(255,244,232,0.98) 38%, rgba(239,246,255,0.96) 70%, rgba(219,234,254,0.95)); box-shadow: 0 34px 80px rgba(37, 99, 235, 0.12), 0 12px 28px rgba(245, 158, 11, 0.12); }\n"
            ".landing-page.personal-portfolio .landing-hero::before { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 18% 18%, rgba(251,191,36,0.12), rgba(251,191,36,0) 30%), radial-gradient(circle at 84% 22%, rgba(59,130,246,0.12), rgba(59,130,246,0) 26%); pointer-events: none; }\n"
            ".landing-page.personal-portfolio .landing-section h2, .landing-page.personal-portfolio .landing-hero h1 { font-family: 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', 'Songti SC', serif; }\n"
            ".landing-page.personal-portfolio .landing-hero h1 { color: #0f172a; font-size: 56px; max-width: 11ch; text-shadow: none; letter-spacing: -0.045em; }\n"
            ".landing-page.personal-portfolio .landing-hero p { color: #1e293b; max-width: 58ch; font-size: 17px; }\n"
            ".landing-page.personal-portfolio .hero-kicker { background: linear-gradient(180deg, rgba(251,191,36,0.16), rgba(59,130,246,0.08)); color: #92400e; border: 1px solid rgba(245,158,11,0.2); }\n"
            ".landing-page.personal-portfolio .hero-persona-row { position: relative; z-index: 1; display: flex; gap: 10px; flex-wrap: wrap; margin-top: -2px; }\n"
            ".landing-page.personal-portfolio .hero-persona-chip { display: inline-flex; align-items: center; min-height: 34px; padding: 0 12px; border-radius: 999px; background: rgba(255,255,255,0.82); border: 1px solid rgba(251,191,36,0.24); color: #92400e; font-size: 12px; letter-spacing: 0.06em; box-shadow: inset 0 1px 0 rgba(255,255,255,0.8); }\n"
            ".landing-page.personal-portfolio .hero-signature-strip { position: relative; z-index: 1; display: grid; gap: 12px; padding: 16px; border-radius: 18px; background: linear-gradient(180deg, rgba(255,255,255,0.86), rgba(255,250,244,0.92)); border: 1px solid rgba(251,191,36,0.24); box-shadow: 0 14px 28px rgba(245,158,11,0.08); }\n"
            ".landing-page.personal-portfolio .hero-signature-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,237,213,0.92); border: 1px solid rgba(251,191,36,0.3); color: #9a3412; font-size: 11px; letter-spacing: 0.08em; font-weight: 800; text-transform: uppercase; }\n"
            ".landing-page.personal-portfolio .hero-signature-strip strong { color: #3f1d0d; font-size: 15px; line-height: 1.7; max-width: 56ch; }\n"
            ".landing-page.personal-portfolio .hero-signature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }\n"
            ".landing-page.personal-portfolio .hero-signature-card { display: grid; gap: 6px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.9); border: 1px solid rgba(191,219,254,0.34); box-shadow: inset 0 1px 0 rgba(255,255,255,0.85); }\n"
            ".landing-page.personal-portfolio .hero-signature-card span { color: #9a3412; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 800; }\n"
            ".landing-page.personal-portfolio .hero-signature-card em { color: #1e293b; font-style: normal; line-height: 1.6; font-size: 13px; }\n"
            ".landing-page.personal-portfolio .hero-actions button { background: linear-gradient(135deg, #1d4ed8, #2563eb); box-shadow: 0 16px 28px rgba(37, 99, 235, 0.18); }\n"
            ".landing-page.personal-portfolio .hero-actions .ghost { background: rgba(255,255,255,0.8); color: #92400e; border-color: rgba(245,158,11,0.28); }\n"
            ".landing-page.personal-portfolio .about-section { border-color: rgba(245, 158, 11, 0.16); background: linear-gradient(180deg, rgba(255,252,248,0.98), rgba(255,247,237,0.96)); }\n"
            ".landing-page.personal-portfolio .about-note { color: #7c2d12; font-size: 14px; }\n"
            ".landing-page.personal-portfolio .about-points article { border-color: rgba(251,191,36,0.26); background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,247,237,0.92)); box-shadow: 0 10px 22px rgba(245, 158, 11, 0.08); }\n"
            ".landing-page.personal-portfolio .about-point-dot { background: #f59e0b; box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.14); }\n"
            ".landing-page.personal-portfolio .landing-section { border-color: rgba(191, 219, 254, 0.2); box-shadow: 0 16px 38px rgba(15, 23, 42, 0.05); }\n"
            ".landing-page.personal-portfolio .landing-section h2 { position: relative; padding-left: 18px; }\n"
            ".landing-page.personal-portfolio .landing-section h2::before { content: ''; position: absolute; left: 0; top: 5px; width: 6px; height: 22px; border-radius: 999px; background: linear-gradient(180deg, #f59e0b, #f97316); box-shadow: 0 0 0 4px rgba(245,158,11,0.12); }\n"
            ".landing-page.personal-portfolio .portfolio-curation-strip { display: grid; gap: 12px; padding: 16px; border-radius: 18px; background: linear-gradient(180deg, rgba(255,252,248,0.98), rgba(255,245,234,0.94)); border: 1px solid rgba(251,191,36,0.24); box-shadow: 0 14px 30px rgba(245,158,11,0.08); }\n"
            ".landing-page.personal-portfolio .portfolio-curation-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,237,213,0.94); border: 1px solid rgba(251,191,36,0.3); color: #9a3412; font-size: 11px; letter-spacing: 0.08em; font-weight: 800; text-transform: uppercase; }\n"
            ".landing-page.personal-portfolio .portfolio-curation-strip strong { color: #431407; line-height: 1.7; font-size: 15px; max-width: 58ch; }\n"
            ".landing-page.personal-portfolio .portfolio-curation-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }\n"
            ".landing-page.personal-portfolio .portfolio-curation-card { display: grid; gap: 6px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.92); border: 1px solid rgba(251,191,36,0.18); }\n"
            ".landing-page.personal-portfolio .portfolio-curation-card span { color: #9a3412; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 800; }\n"
            ".landing-page.personal-portfolio .portfolio-curation-card em { color: #1e293b; font-style: normal; line-height: 1.6; font-size: 13px; }\n"
            ".landing-page.personal-portfolio .portfolio-card { border-color: rgba(251,191,36,0.22); background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(255,247,237,0.96)); box-shadow: 0 16px 30px rgba(148, 163, 184, 0.08); }\n"
            ".landing-page.personal-portfolio .portfolio-sequence { display: inline-flex; width: fit-content; align-items: center; min-height: 26px; padding: 0 9px; border-radius: 999px; background: rgba(30,64,175,0.08); border: 1px solid rgba(59,130,246,0.18); color: #1e3a8a; font-size: 11px; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }\n"
            ".landing-page.personal-portfolio .portfolio-meta { color: #9a3412; background: rgba(255,237,213,0.95); border-color: rgba(251,191,36,0.3); }\n"
            ".landing-page.personal-portfolio .portfolio-brief span { background: rgba(255,252,248,0.96); border-color: rgba(251,191,36,0.2); }\n"
            ".landing-page.personal-portfolio .portfolio-brief strong { color: #9a3412; }\n"
            ".landing-page.personal-portfolio .portfolio-brief em { color: #7c2d12; }\n"
            ".landing-page.personal-portfolio .portfolio-editor-note { display: inline-flex; width: fit-content; margin-top: auto; padding: 6px 10px; border-radius: 999px; background: rgba(255,250,245,0.96); border: 1px solid rgba(251,191,36,0.18); color: #7c2d12; font-size: 12px; line-height: 1.5; }\n"
            ".landing-page.personal-portfolio .portfolio-detail { color: #7c2d12; background: rgba(255,247,237,0.92); border: 1px solid rgba(251,191,36,0.18); }\n"
            ".landing-page.personal-portfolio .portfolio-outcome { background: rgba(219,234,254,0.75); color: #1e3a8a; }\n"
            ".landing-page.personal-portfolio .landing-footer { border-color: rgba(191, 219, 254, 0.24); background: linear-gradient(135deg, rgba(15,23,42,0.98), rgba(30,41,59,0.96)); }\n"
            ".landing-page.personal-portfolio .footer-signoff-strip { display: grid; gap: 8px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.04); border: 1px solid rgba(191,219,254,0.14); }\n"
            ".landing-page.personal-portfolio .footer-signoff-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,255,255,0.08); border: 1px solid rgba(191,219,254,0.18); color: #dbeafe; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }\n"
            ".landing-page.personal-portfolio .footer-signoff-grid { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".landing-page.personal-portfolio .footer-signoff-grid span { display: inline-flex; align-items: center; min-height: 28px; padding: 0 10px; border-radius: 999px; background: rgba(255,255,255,0.08); border: 1px solid rgba(191,219,254,0.16); color: #dbeafe; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; }\n"
            ".landing-page.personal-portfolio .landing-footer button { border-color: rgba(191,219,254,0.22); background: rgba(255,255,255,0.96); color: #1e3a8a; }\n"
            ".landing-hero p { position: relative; z-index: 1; margin: 0; max-width: 64ch; color: #334155; font-size: 16px; line-height: 1.7; }\n"
            ".hero-actions { position: relative; z-index: 1; display: flex; gap: 10px; flex-wrap: wrap; }\n"
            ".hero-actions button { border: 1px solid #2563eb; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border-radius: 10px; padding: 10px 14px; cursor: pointer; font-weight: 700; box-shadow: 0 12px 26px rgba(37, 99, 235, 0.22); }\n"
            ".hero-actions .ghost { background: rgba(255, 255, 255, 0.92); color: #1d4ed8; box-shadow: none; }\n"
            ".landing-section { border: 1px solid #e5e7eb; background: rgba(255, 255, 255, 0.98); border-radius: 18px; padding: 18px; display: grid; gap: 12px; box-shadow: 0 16px 38px rgba(15, 23, 42, 0.06); }\n"
            ".landing-section h1, .landing-section h2 { margin: 0; }\n"
            ".landing-section h2 { font-size: 24px; letter-spacing: -0.02em; color: #0f172a; }\n"
            ".section-lead { margin: 0; max-width: 64ch; color: #475569; font-size: 14px; line-height: 1.7; }\n"
            ".about-section { background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); }\n"
            ".about-shell { display: grid; gap: 16px; max-width: 940px; grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.9fr); align-items: start; }\n"
            ".about-copy { display: grid; gap: 10px; }\n"
            ".about-shell p { margin: 0; color: #334155; line-height: 1.8; font-size: 15px; }\n"
            ".about-note { color: #475569; font-size: 14px; }\n"
            ".about-points { display: grid; gap: 10px; }\n"
            ".about-points article { border: 1px solid rgba(148, 163, 184, 0.22); background: rgba(241,245,249,0.88); color: #0f172a; border-radius: 14px; padding: 12px 14px; font-size: 13px; font-weight: 600; display: flex; gap: 10px; align-items: center; }\n"
            ".about-point-dot { width: 8px; height: 8px; border-radius: 999px; background: #2563eb; flex: none; box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12); }\n"
            ".pill-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 12px; }\n"
            ".pill-grid article { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 16px; padding: 16px; display: grid; gap: 8px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); min-height: 138px; }\n"
            ".pill-grid article strong { font-size: 15px; color: #0f172a; }\n"
            ".pill-grid article span { color: #475569; font-size: 14px; line-height: 1.5; }\n"
            ".stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; }\n"
            ".stat-card { border: 1px solid #e4e4e7; border-radius: 10px; padding: 14px; display: grid; gap: 6px; text-align: center; }\n"
            ".stat-card strong { font-size: 24px; color: #1d4ed8; }\n"
            ".stat-card span { color: #475569; }\n"
            ".logo-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }\n"
            ".logo-card { border: 1px dashed #cbd5e1; border-radius: 10px; min-height: 72px; display: grid; place-items: center; background: #f8fafc; color: #475569; }\n"
            ".team-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }\n"
            ".team-card { border: 1px solid #e4e4e7; border-radius: 10px; padding: 14px; display: grid; gap: 6px; justify-items: center; text-align: center; }\n"
            ".team-card .avatar { width: 48px; height: 48px; border-radius: 999px; background: #dbeafe; color: #1d4ed8; display: grid; place-items: center; font-weight: 700; }\n"
            ".team-card span { color: #475569; }\n"
            ".jobs-grid, .portfolio-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }\n"
            ".jobs-card, .portfolio-card { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 18px; padding: 16px; display: grid; gap: 8px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); min-height: 146px; }\n"
            ".portfolio-meta { display: inline-flex; width: fit-content; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219, 234, 254, 0.9); border: 1px solid rgba(96, 165, 250, 0.24); border-radius: 999px; padding: 5px 10px; }\n"
            ".jobs-card span { color: #475569; font-size: 14px; }\n"
            ".portfolio-card strong { font-size: 16px; color: #0f172a; }\n"
            ".portfolio-card p { margin: 0; color: #475569; font-size: 14px; line-height: 1.65; }\n"
            ".portfolio-brief { display: grid; gap: 8px; margin-top: auto; }\n"
            ".portfolio-brief span { display: grid; gap: 4px; padding: 8px 10px; border-radius: 12px; background: rgba(248,250,252,0.92); border: 1px solid rgba(148,163,184,0.16); }\n"
            ".portfolio-brief strong { font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: #64748b; }\n"
            ".portfolio-brief em { font-style: normal; font-size: 13px; color: #0f172a; line-height: 1.55; }\n"
            ".portfolio-detail { display: inline-flex; width: fit-content; color: #475569; background: rgba(241,245,249,0.9); border: 1px solid rgba(148,163,184,0.2); border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 600; }\n"
            ".portfolio-outcome { margin-top: auto; display: inline-flex; width: fit-content; color: #0f172a; background: rgba(226, 232, 240, 0.75); border-radius: 999px; padding: 6px 10px; font-size: 12px; font-weight: 600; }\n"
            ".faq-scan-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".faq-scan-strip span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 11px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219,234,254,0.62); border: 1px solid rgba(96,165,250,0.2); }\n"
            ".faq-list { display: grid; gap: 12px; }\n"
            ".faq-item { border: 1px solid #e4e4e7; border-radius: 14px; padding: 12px 14px; background: rgba(255,255,255,0.98); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04); display: grid; gap: 10px; }\n"
            ".faq-item[open] { box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08); }\n"
            ".faq-item summary { cursor: pointer; font-weight: 700; color: #0f172a; list-style: none; display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }\n"
            ".faq-item summary::-webkit-details-marker { display: none; }\n"
            ".faq-question { flex: 1; line-height: 1.55; }\n"
            ".faq-summary-hint { display: inline-flex; align-items: center; border-radius: 999px; padding: 4px 9px; background: rgba(241,245,249,0.9); color: #475569; font-size: 11px; font-weight: 700; white-space: nowrap; }\n"
            ".faq-body { display: grid; gap: 10px; }\n"
            ".faq-context { display: inline-flex; width: fit-content; padding: 5px 10px; border-radius: 999px; background: rgba(219,234,254,0.72); color: #1d4ed8; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }\n"
            ".faq-copy-block, .faq-followup-block { display: grid; gap: 8px; padding: 10px 12px; border-radius: 12px; }\n"
            ".faq-copy-block { background: rgba(248,250,252,0.92); border: 1px solid rgba(226,232,240,0.9); }\n"
            ".faq-followup-block { background: rgba(239,246,255,0.8); border: 1px solid rgba(191,219,254,0.72); }\n"
            ".faq-copy-label, .faq-followup-label { display: inline-flex; width: fit-content; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 700; }\n"
            ".faq-copy-label { color: #64748b; }\n"
            ".faq-followup-label { color: #0f4cc7; }\n"
            ".faq-answer { margin: 0; color: #475569; line-height: 1.7; }\n"
            ".faq-followup { margin: 0; color: #0f172a; line-height: 1.65; font-size: 13px; font-weight: 600; }\n"
            ".faq-contact-bridge { display: grid; gap: 10px; margin-top: 12px; padding: 14px; border-radius: 16px; background: rgba(239,246,255,0.82); border: 1px solid rgba(191,219,254,0.72); }\n"
            ".faq-contact-bridge-label, .contact-entry-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".faq-contact-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }\n"
            ".faq-contact-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".faq-contact-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".faq-contact-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }\n"
            ".faq-contact-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }\n"
            ".quote-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }\n"
            ".quote-card { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 18px; padding: 16px; display: grid; gap: 12px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); min-height: 174px; }\n"
            ".quote-context { display: inline-flex; width: fit-content; padding: 5px 10px; border-radius: 999px; background: rgba(226,232,240,0.72); color: #475569; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }\n"
            ".quote-copy { margin: 0; color: #334155; line-height: 1.75; font-size: 14px; }\n"
            ".quote-meta { margin-top: auto; display: grid; gap: 4px; }\n"
            ".quote-meta strong { color: #0f172a; font-size: 13px; }\n"
            ".quote-meta span { color: #1d4ed8; font-size: 12px; font-weight: 600; }\n"
            ".cta { text-align: center; background: linear-gradient(135deg, rgba(239,246,255,0.98), rgba(219,234,254,0.96)); }\n"
            ".cta-note { margin: 0 auto 10px; max-width: 52ch; color: #475569; font-size: 14px; line-height: 1.65; }\n"
            ".cta-capture-strip { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 0 auto 12px; }\n"
            ".cta-capture-strip span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 11px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219,234,254,0.62); border: 1px solid rgba(96,165,250,0.2); }\n"
            ".cta-success-bridge { display: grid; gap: 10px; margin: 0 auto 12px; max-width: 720px; padding: 14px; border-radius: 16px; background: rgba(236,253,245,0.92); border: 1px solid rgba(110,231,183,0.55); text-align: left; }\n"
            ".cta-success-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(134,239,172,0.7); }\n"
            ".cta-success-bridge strong { color: #14532d; font-size: 14px; line-height: 1.6; }\n"
            ".cta-success-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".cta-success-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(134,239,172,0.7); }\n"
            ".cta-success-bridge-current { color: #166534; background: rgba(220,252,231,0.92); }\n"
            ".cta-success-bridge-next { color: #166534; background: rgba(240,253,244,0.96); }\n"
            ".cta-landing-bridge { display: grid; gap: 10px; margin: 0 auto 12px; max-width: 720px; padding: 14px; border-radius: 16px; background: rgba(248,250,252,0.94); border: 1px solid rgba(191,219,254,0.72); text-align: left; }\n"
            ".cta-landing-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".cta-landing-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }\n"
            ".cta-landing-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".cta-landing-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".cta-landing-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }\n"
            ".cta-landing-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }\n"
            ".cta-close-strip { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 0 auto 14px; }\n"
            ".cta-close-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".cta-close-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }\n"
            ".cta-close-next { color: #334155; background: rgba(241,245,249,0.92); }\n"
            ".cta button { border: 1px solid #2563eb; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border-radius: 10px; padding: 10px 16px; cursor: pointer; font-weight: 700; box-shadow: 0 14px 26px rgba(37, 99, 235, 0.18); }\n"
            ".price-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }\n"
            ".price-grid article { border: 1px solid #e4e4e7; border-radius: 8px; padding: 12px; display: grid; gap: 8px; }\n"
            ".price-grid button { border: 1px solid #0f766e; background: #0f766e; color: #fff; border-radius: 8px; padding: 6px 10px; cursor: pointer; width: fit-content; }\n"
            ".contact-response-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".contact-response-strip span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 11px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #1d4ed8; background: rgba(219,234,254,0.62); border: 1px solid rgba(96,165,250,0.2); }\n"
            ".contact-entry-bridge { display: grid; gap: 8px; margin-bottom: 14px; padding: 12px 14px; border-radius: 16px; background: rgba(239,246,255,0.78); border: 1px solid rgba(191,219,254,0.72); }\n"
            ".contact-entry-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }\n"
            ".contact-intake-bridge { display: grid; gap: 10px; margin: 12px 0 14px; padding: 14px; border-radius: 16px; background: rgba(248,250,252,0.94); border: 1px solid rgba(191,219,254,0.72); }\n"
            ".contact-intake-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".contact-intake-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }\n"
            ".contact-intake-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".contact-intake-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".contact-intake-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }\n"
            ".contact-intake-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }\n"
            ".contact-handoff-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }\n"
            ".contact-handoff-card { border: 1px solid rgba(148,163,184,0.22); border-radius: 16px; padding: 14px; display: grid; gap: 6px; background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98)); }\n"
            ".contact-handoff-card span { font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #64748b; }\n"
            ".contact-handoff-card strong { color: #0f172a; font-size: 14px; line-height: 1.55; }\n"
            ".intake-closure-bridge { display: grid; gap: 10px; margin: 0 auto 14px; max-width: 760px; padding: 14px; border-radius: 16px; background: rgba(248,250,252,0.94); border: 1px solid rgba(191,219,254,0.72); text-align: left; }\n"
            ".intake-closure-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".intake-closure-bridge strong { color: #0f172a; font-size: 14px; line-height: 1.6; }\n"
            ".intake-closure-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".intake-closure-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(96,165,250,0.2); }\n"
            ".intake-closure-bridge-current { color: #1d4ed8; background: rgba(219,234,254,0.7); }\n"
            ".intake-closure-bridge-next { color: #334155; background: rgba(241,245,249,0.92); }\n"
            ".contact-form-shell { display: grid; gap: 12px; max-width: 760px; }\n"
            ".contact-form-shell--business { grid-template-columns: minmax(220px, 0.9fr) minmax(0, 1.15fr); align-items: start; }\n"
            ".contact-form-intake { display: grid; gap: 10px; padding: 14px; border-radius: 16px; background: linear-gradient(180deg, rgba(239,246,255,0.98), rgba(248,250,252,0.96)); border: 1px solid rgba(191,219,254,0.9); }\n"
            ".contact-form-intake strong { color: #0f172a; font-size: 14px; line-height: 1.6; }\n"
            ".contact-form-checklist { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".contact-form-checklist span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #0f4cc7; background: rgba(219,234,254,0.76); border: 1px solid rgba(96,165,250,0.2); }\n"
            ".contact-form-panel { display: grid; gap: 12px; padding: 16px; border-radius: 18px; background: linear-gradient(180deg, rgba(255,255,255,0.99), rgba(248,250,252,0.97)); border: 1px solid rgba(148,163,184,0.18); box-shadow: 0 18px 36px rgba(15,23,42,0.08); }\n"
            ".contact-form { display: grid; gap: 12px; max-width: 640px; }\n"
            ".contact-field { display: grid; gap: 7px; }\n"
            ".contact-field span { color: #334155; font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }\n"
            ".contact-field-hint { color: #64748b; font-size: 12px; line-height: 1.55; }\n"
            ".contact-form input:hover, .contact-form textarea:hover { border-color: rgba(59,130,246,0.32); }\n"
            ".contact-form input, .contact-form textarea { border: 1px solid #cbd5e1; border-radius: 12px; padding: 12px 13px; background: rgba(255,255,255,0.98); color: #0f172a; box-shadow: inset 0 1px 0 rgba(255,255,255,0.8); }\n"
            ".contact-form input:focus, .contact-form textarea:focus { outline: none; border-color: rgba(37,99,235,0.56); box-shadow: 0 0 0 3px rgba(59,130,246,0.14); }\n"
            ".contact-form textarea { min-height: 132px; resize: vertical; }\n"
            ".contact-form input::placeholder, .contact-form textarea::placeholder { color: #94a3b8; }\n"
            ".contact-form-actions { display: grid; gap: 8px; }\n"
            ".contact-form button { border: 1px solid #2563eb; background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; border-radius: 12px; padding: 12px 16px; cursor: pointer; width: 100%; font-weight: 700; box-shadow: 0 14px 26px rgba(37, 99, 235, 0.18); transition: transform 160ms ease, box-shadow 160ms ease, opacity 160ms ease; }\n"
            ".contact-form button:hover { transform: translateY(-1px); box-shadow: 0 18px 30px rgba(37, 99, 235, 0.24); }\n"
            ".contact-form button:disabled { cursor: default; opacity: 0.82; transform: none; box-shadow: 0 10px 20px rgba(37, 99, 235, 0.14); }\n"
            ".contact-submit-hint { color: #64748b; font-size: 12px; line-height: 1.6; }\n"
            ".contact-form-note { margin: 0; color: #475569; font-size: 13px; line-height: 1.7; }\n"
            ".contact-success-card { display: grid; gap: 10px; padding: 14px; border-radius: 16px; background: linear-gradient(180deg, rgba(236,253,245,0.96), rgba(240,253,250,0.96)); border: 1px solid rgba(110,231,183,0.55); }\n"
            ".contact-success-card strong { color: #166534; font-size: 15px; }\n"
            ".contact-success-card p { margin: 0; color: #14532d; line-height: 1.65; font-size: 13px; }\n"
            ".contact-success-steps { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".contact-success-steps span { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 10px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; color: #166534; background: rgba(220,252,231,0.92); border: 1px solid rgba(134,239,172,0.7); }\n"
            ".contact-success { color: #15803d; margin: 0; }\n"
            ".landing-footer { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 16px; padding: 16px; display: grid; gap: 10px; background: rgba(15, 23, 42, 0.96); color: #f8fafc; }\n"
            ".footer-success-bridge { display: grid; gap: 10px; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.04); }\n"
            ".footer-success-bridge-label { display: inline-flex; width: fit-content; align-items: center; min-height: 28px; border-radius: 999px; padding: 0 10px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(134,239,172,0.22); }\n"
            ".footer-success-bridge strong { color: #f8fafc; font-size: 14px; line-height: 1.6; }\n"
            ".footer-success-bridge-strip { display: flex; flex-wrap: wrap; gap: 8px; }\n"
            ".footer-success-bridge-strip span { display: inline-flex; align-items: center; min-height: 30px; border-radius: 999px; padding: 0 12px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid rgba(148,163,184,0.22); }\n"
            ".footer-success-bridge-current { color: #dcfce7; background: rgba(34,197,94,0.16); }\n"
            ".footer-success-bridge-next { color: #dbeafe; background: rgba(255,255,255,0.06); }\n"
            ".landing-footer .links { display: flex; gap: 8px; flex-wrap: wrap; }\n"
            ".landing-footer button { border: 1px solid rgba(226, 232, 240, 0.24); background: rgba(255, 255, 255, 0.96); color: #0f172a; border-radius: 999px; padding: 6px 12px; cursor: pointer; font-weight: 600; }\n"
            ".landing-footer small { color: #94a3b8; }\n"
            "@media (max-width: 900px) { .landing-page { width: min(100%, calc(100% - 16px)); padding: 12px 0 24px; } .landing-header { padding: 12px; } .landing-hero { padding: 26px 18px; } .landing-hero h1 { font-size: 34px; max-width: none; } .landing-page.personal-portfolio .landing-hero h1 { font-size: 42px; } .about-shell { grid-template-columns: 1fr; } .pill-grid, .jobs-grid, .portfolio-grid { grid-template-columns: 1fr; } .contact-form-shell--business { grid-template-columns: 1fr; } }\n"
            "</style>\n"
        )

    def _generate_app_home_view(self, page: dict[str, Any]) -> str:
        topbar_cfgs = self._app_component_props(page, "TopBar")
        bottom_tab_cfgs = self._app_component_props(page, "BottomTab")
        list_cfgs = self._app_component_props(page, "List")
        card_cfgs = self._app_component_props(page, "Card")
        chat_window_cfgs = self._app_component_props(page, "ChatWindow")
        composer_cfgs = self._app_component_props(page, "Composer")
        searchbar_cfgs = self._app_component_props(page, "SearchBar")

        topbar_cfg = topbar_cfgs[0] if topbar_cfgs else {}
        bottom_tab_cfg = bottom_tab_cfgs[0] if bottom_tab_cfgs else {}
        chat_window_cfg = chat_window_cfgs[0] if chat_window_cfgs else {}

        title = topbar_cfg.get("title", "AI Chat")
        tab_items = self._split_pipe_items(
            bottom_tab_cfg.get("items", "chats|contacts|discover|me"),
            ["chats", "contacts", "discover", "me"],
        )

        chats_title = "最近聊天"
        contacts_title = "联系人"
        discover_title = "发现 AI 工具"
        discover_subtitle = "探索更多玩法"
        me_title = "我的资料"
        me_subtitle = "查看个人信息"
        for cfg in card_cfgs:
            tab_name = str(cfg.get("tab", "")).strip().lower()
            if tab_name == "discover":
                discover_title = cfg.get("title", discover_title)
                discover_subtitle = cfg.get("subtitle", discover_subtitle)
            elif tab_name == "me":
                me_title = cfg.get("title", me_title)
                me_subtitle = cfg.get("subtitle", me_subtitle)
        for cfg in list_cfgs:
            tab_name = str(cfg.get("tab", "")).strip().lower()
            if tab_name == "chats":
                chats_title = cfg.get("title", chats_title)
            elif tab_name == "contacts":
                contacts_title = cfg.get("title", contacts_title)

        chat_window_title = chat_window_cfg.get("title", "对话窗口")
        show_input = chat_window_cfg.get("input", "on").strip().lower() == "on"
        composer_cfg = composer_cfgs[0] if composer_cfgs else {}
        composer_title = composer_cfg.get("title", "快速输入")
        composer_placeholder = composer_cfg.get("placeholder", "输入内容（mock）")
        composer_button = composer_cfg.get("button", "保存")
        searchbar_cfg = searchbar_cfgs[0] if searchbar_cfgs else {}
        searchbar_placeholder = searchbar_cfg.get("placeholder", "搜索联系人")

        return (
            "<template>\n"
            "  <section class=\"app-shell\">\n"
            "    <div class=\"phone-frame\">\n"
            "      <header class=\"app-topbar\" data-app=\"TopBar\" data-testid=\"app-topbar\">\n"
            f"        <strong>{title}</strong>\n"
            "        <span>移动端原型</span>\n"
            "      </header>\n"
            "      <main class=\"app-content\">\n"
            "        <section v-if=\"activeTab === 'chats'\" class=\"app-panel\" data-app=\"List\" data-testid=\"panel-chats\">\n"
            f"          <h2>{chats_title}</h2>\n"
            "          <button type=\"button\" class=\"list-card\" v-for=\"item in chats\" :key=\"item.id\" :data-testid=\"`chat-item-${item.id}`\" @click=\"openChat(item)\">\n"
            "            <div>\n"
            "              <strong>{{ item.title }}</strong>\n"
            "              <p>{{ item.last_message }}</p>\n"
            "            </div>\n"
            "            <div class=\"meta\">\n"
            "              <span>{{ item.time }}</span>\n"
            "              <em v-if=\"item.unread > 0\">{{ item.unread }}</em>\n"
            "            </div>\n"
            "          </button>\n"
            "        </section>\n"
            "        <section v-else-if=\"activeTab === 'contacts'\" class=\"app-panel\" data-app=\"List\" data-testid=\"panel-contacts\">\n"
            f"          <h2>{contacts_title}</h2>\n"
            + (
                "          <div class=\"searchbar-panel\" data-app=\"SearchBar\" data-testid=\"app-searchbar\">\n"
                f"            <input v-model=\"contactKeyword\" type=\"text\" placeholder=\"{searchbar_placeholder}\" />\n"
                "          </div>\n"
                if searchbar_cfgs else
                ""
            )
            + "          <article class=\"list-card contact\" v-for=\"item in filteredContacts\" :key=\"item.id\">\n"
            "            <div>\n"
            "              <strong>{{ item.name }}</strong>\n"
            "              <p>{{ item.status }}</p>\n"
            "            </div>\n"
            "          </article>\n"
            "        </section>\n"
            "        <section v-else-if=\"activeTab === 'discover'\" class=\"app-panel\" data-app=\"Card\" data-testid=\"panel-discover\">\n"
            f"          <h2>{discover_title}</h2>\n"
            f"          <article class=\"feature-card\"><strong>{discover_title}</strong><p>{discover_subtitle}</p></article>\n"
            "          <div class=\"mini-grid\">\n"
            "            <article v-for=\"item in discoverItems\" :key=\"item.title\" class=\"mini-card\">\n"
            "              <strong>{{ item.title }}</strong>\n"
            "              <p>{{ item.subtitle }}</p>\n"
            "            </article>\n"
            "          </div>\n"
            "        </section>\n"
            "        <section v-else class=\"app-panel\" data-app=\"Card\" data-testid=\"panel-me\">\n"
            f"          <h2>{me_title}</h2>\n"
            "          <article class=\"feature-card profile-card\">\n"
            "            <strong>{{ profile.name }}</strong>\n"
            "            <p>{{ profile.bio }}</p>\n"
            "          </article>\n"
            f"          <article class=\"feature-card\"><strong>{me_title}</strong><p>{me_subtitle}</p></article>\n"
            "        </section>\n"
            + (
                "        <section class=\"composer-panel\" data-app=\"Composer\" data-testid=\"app-composer\">\n"
                f"          <label>{composer_title}</label>\n"
                "          <div class=\"composer-row\">\n"
                f"            <input v-model=\"composerText\" type=\"text\" placeholder=\"{composer_placeholder}\" />\n"
                f"            <button type=\"button\" @click=\"submitComposer\">{composer_button}</button>\n"
                "          </div>\n"
                "        </section>\n"
                if composer_cfgs else
                ""
            )
            + "      </main>\n"
            "      <nav class=\"app-bottom-tab\" data-app=\"BottomTab\" data-testid=\"app-bottom-tab\">\n"
            "        <button type=\"button\" v-for=\"tab in tabs\" :key=\"tab\" :data-testid=\"`btn-tab-${tab}`\" :class=\"{ active: activeTab === tab }\" @click=\"activeTab = tab\">{{ tab }}</button>\n"
            "      </nav>\n"
            "      <section v-if=\"activeChat\" class=\"chat-overlay\" data-app=\"ChatWindow\" data-testid=\"chat-window\">\n"
            "        <div class=\"chat-window\">\n"
            "          <header>\n"
            f"            <strong>{chat_window_title}</strong>\n"
            "            <button type=\"button\" data-testid=\"btn-close-chat\" @click=\"closeChat\">关闭</button>\n"
            "          </header>\n"
            "          <div class=\"chat-messages\">\n"
            "            <p class=\"bubble user\">{{ activeChat.title }}</p>\n"
            "            <p class=\"bubble ai\">{{ activeChat.last_message }}</p>\n"
            "          </div>\n"
            + (
                "          <footer class=\"chat-input\"><input type=\"text\" placeholder=\"输入消息（mock）\" /><button type=\"button\">发送</button></footer>\n"
                if show_input else
                ""
            )
            + "        </div>\n"
            "      </section>\n"
            "    </div>\n"
            "  </section>\n"
            "</template>\n\n"
            "<script setup>\n"
            "import { computed, ref } from 'vue'\n\n"
            f"const tabs = {json.dumps(tab_items, ensure_ascii=False)}\n"
            f"const chats = {json.dumps([{'id': 'c1', 'title': '产品顾问', 'last_message': '欢迎体验 AI 对话原型', 'time': '09:30', 'unread': 2}, {'id': 'c2', 'title': '项目群', 'last_message': '今天下午同步新需求', 'time': '昨天', 'unread': 0}, {'id': 'c3', 'title': '设计协作', 'last_message': '我已更新新版首页视觉', 'time': '周五', 'unread': 1}], ensure_ascii=False)}\n"
            f"const contacts = {json.dumps([{'id': 'u1', 'name': '林晓', 'status': '在线 · 可随时发起对话'}, {'id': 'u2', 'name': '周宁', 'status': '忙碌 · 下午回复'}, {'id': 'u3', 'name': '产品助手', 'status': '智能助理 · 24h 可用'}], ensure_ascii=False)}\n"
            f"const discoverItems = {json.dumps([{'title': 'AI 会议纪要', 'subtitle': '自动提炼重点'}, {'title': '灵感画布', 'subtitle': '快速组织想法'}, {'title': '团队知识库', 'subtitle': '沉淀常见问题'}], ensure_ascii=False)}\n"
            f"const profile = {json.dumps({'id': 'me', 'name': 'Alex Chen', 'bio': 'AI 产品经理 · 关注效率工具与团队协作'}, ensure_ascii=False)}\n"
            "const activeTab = ref(tabs[0] || 'chats')\n"
            "const activeChat = ref(null)\n"
            "const composerText = ref('')\n"
            "const contactKeyword = ref('')\n"
            "const filteredContacts = computed(() => {\n"
            "  const q = String(contactKeyword.value || '').trim().toLowerCase()\n"
            "  if (!q) return contacts\n"
            "  return contacts.filter((item) =>\n"
            "    String(item.name || '').toLowerCase().includes(q) ||\n"
            "    String(item.status || '').toLowerCase().includes(q)\n"
            "  )\n"
            "})\n\n"
            "function openChat(item) {\n"
            "  activeChat.value = item\n"
            "}\n\n"
            "function closeChat() {\n"
            "  activeChat.value = null\n"
            "}\n"
            + (
                "\nfunction submitComposer() {\n"
                "  if (!composerText.value.trim()) return\n"
                "  console.log('app:Composer mock submit', composerText.value)\n"
                "  composerText.value = ''\n"
                "}\n"
                if composer_cfgs else
                ""
            )
            + "</script>\n\n"
            "<style scoped>\n"
            ".app-shell { min-height: 100vh; display: grid; place-items: center; background: linear-gradient(180deg, #e2e8f0 0%, #f8fafc 100%); padding: 20px; }\n"
            ".phone-frame { width: 100%; max-width: 420px; min-height: 780px; background: #0f172a; color: #e2e8f0; border-radius: 28px; border: 1px solid #1e293b; overflow: hidden; position: relative; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.28); }\n"
            ".app-topbar { height: 64px; padding: 14px 18px; display: flex; align-items: center; justify-content: space-between; background: rgba(15, 23, 42, 0.96); border-bottom: 1px solid #1e293b; position: sticky; top: 0; z-index: 5; }\n"
            ".app-topbar span { color: #94a3b8; font-size: 13px; }\n"
            ".app-content { min-height: calc(780px - 128px); padding: 18px; background: linear-gradient(180deg, #111827 0%, #0f172a 100%); }\n"
            ".app-panel { display: grid; gap: 12px; }\n"
            ".app-panel h2 { margin: 0; font-size: 18px; }\n"
            ".composer-panel { display: grid; gap: 8px; margin-top: 14px; padding: 12px; border: 1px solid #1f2937; border-radius: 18px; background: rgba(15, 23, 42, 0.72); }\n"
            ".searchbar-panel { display: grid; gap: 8px; margin-bottom: 4px; }\n"
            ".searchbar-panel input { border: 1px solid #334155; border-radius: 12px; padding: 10px 12px; background: #020617; color: #e2e8f0; }\n"
            ".composer-panel label { color: #cbd5e1; font-size: 13px; }\n"
            ".composer-row { display: grid; grid-template-columns: 1fr auto; gap: 8px; }\n"
            ".composer-row input { border: 1px solid #334155; border-radius: 12px; padding: 10px 12px; background: #020617; color: #e2e8f0; }\n"
            ".composer-row button { border: 1px solid #38bdf8; background: #38bdf8; color: #082f49; border-radius: 12px; padding: 10px 14px; cursor: pointer; font-weight: 700; }\n"
            ".list-card, .feature-card, .mini-card { border: 1px solid #1f2937; background: rgba(15, 23, 42, 0.86); border-radius: 18px; padding: 14px; color: inherit; }\n"
            ".list-card { width: 100%; display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; text-align: left; cursor: pointer; }\n"
            ".list-card p, .feature-card p, .mini-card p { margin: 4px 0 0; color: #94a3b8; font-size: 13px; }\n"
            ".meta { display: grid; gap: 8px; justify-items: end; color: #94a3b8; font-size: 12px; }\n"
            ".meta em { min-width: 22px; height: 22px; display: grid; place-items: center; border-radius: 999px; background: #22c55e; color: #052e16; font-style: normal; font-weight: 700; }\n"
            ".mini-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }\n"
            ".profile-card { background: linear-gradient(135deg, #1d4ed8 0%, #0f172a 100%); }\n"
            ".app-bottom-tab { height: 64px; padding: 10px 12px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; background: rgba(15, 23, 42, 0.98); border-top: 1px solid #1e293b; }\n"
            ".app-bottom-tab button { border: 1px solid transparent; background: transparent; color: #94a3b8; border-radius: 14px; font-size: 13px; cursor: pointer; }\n"
            ".app-bottom-tab button.active { background: #22c55e; color: #052e16; font-weight: 700; }\n"
            ".chat-overlay { position: absolute; inset: 0; background: rgba(2, 6, 23, 0.72); display: grid; place-items: end center; padding: 18px; }\n"
            ".chat-window { width: 100%; background: #f8fafc; color: #0f172a; border-radius: 24px 24px 18px 18px; padding: 16px; display: grid; gap: 12px; }\n"
            ".chat-window header { display: flex; justify-content: space-between; align-items: center; }\n"
            ".chat-window header button { border: 1px solid #cbd5e1; background: white; border-radius: 10px; padding: 6px 10px; cursor: pointer; }\n"
            ".chat-messages { display: grid; gap: 10px; }\n"
            ".bubble { margin: 0; padding: 10px 12px; border-radius: 14px; max-width: 80%; }\n"
            ".bubble.user { background: #dcfce7; justify-self: end; }\n"
            ".bubble.ai { background: #e2e8f0; }\n"
            ".chat-input { display: grid; grid-template-columns: 1fr auto; gap: 8px; }\n"
            ".chat-input input { border: 1px solid #cbd5e1; border-radius: 12px; padding: 10px 12px; }\n"
            ".chat-input button { border: 1px solid #22c55e; background: #22c55e; color: #052e16; border-radius: 12px; padding: 10px 14px; cursor: pointer; font-weight: 700; }\n"
            "@media (max-width: 520px) { .app-shell { padding: 0; } .phone-frame { max-width: 100%; min-height: 100vh; border-radius: 0; } .app-content { min-height: calc(100vh - 128px); } }\n"
            "</style>\n"
        )


    def _generate_vue_view(self, page: dict[str, Any]) -> str:
        page_name = str(page.get("name", "")).strip().lower()
        page_path = str(page.get("path", "")).strip()
        if self._is_app_page(page):
            return self._generate_app_home_view(page)
        if self._is_landing_page(page):
            return self._generate_landing_view(page)
        if self._is_ecom_page(page):
            if page_path == "/":
                return self._generate_ecom_home_view(page)
            if page_path == "/product/:id":
                return self._generate_ecom_product_view(page)
            if page_path == "/cart":
                return self._generate_ecom_cart_view(page)
            if page_path == "/checkout":
                return self._generate_ecom_checkout_view(page)
            if page_path == "/category/:name":
                return self._generate_ecom_category_view(page)
            if page_path == "/shop/:id":
                return self._generate_ecom_shop_view(page)
            if page_path == "/search":
                return self._generate_ecom_search_view(page)
            if page_path == "/after-sales":
                return self._generate_ecom_after_sales_view(page)
        if page_name == "tools" and page_path == "/tools" and self._has_tools_api():
            return self._generate_tools_vue_view()
        if page_name == "forbidden" or page_path == "/403":
            return (
                "<template>\n"
                "  <section class=\"forbidden-page\">\n"
                "    <h2>403 Forbidden</h2>\n"
                "    <p>You don't have permission</p>\n"
                "    <router-link class=\"home-btn\" to=\"/\">Back to Home</router-link>\n"
                "  </section>\n"
                "</template>\n\n"
                "<script setup>\n"
                "</script>\n\n"
                "<style scoped>\n"
                ".forbidden-page { display: grid; gap: 10px; max-width: 420px; }\n"
                ".home-btn { display: inline-block; width: fit-content; padding: 8px 12px; border: 1px solid #3f3f46; border-radius: 8px; color: #f4f4f5; text-decoration: none; }\n"
                "</style>\n"
            )
        if page_name == "admin" or page_path == "/admin":
            return (
                "<template>\n"
                "  <section class=\"admin-page\">\n"
                "    <h2>Admin Page</h2>\n"
                "  </section>\n"
                "</template>\n\n"
                "<script setup>\n"
                "</script>\n\n"
                "<style scoped>\n"
                ".admin-page { display: grid; gap: 12px; }\n"
                "</style>\n"
            )
        return super()._generate_vue_view(page)

    def build_project(self) -> Path:
        project_root = self.base_dir / self.system_name
        backend_dir = project_root / "backend"
        frontend_dir = project_root / "frontend"

        try:
            backend_dir.mkdir(parents=True, exist_ok=True)
            project_root.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeError(f"Failed to create project directories under {project_root}: {exc}") from exc

        self._ensure_primary_keys()
        backend_main_content = self._generate_backend_main_py()
        self._safe_write_text(backend_dir / "main.py", backend_main_content)
        db_path = project_root / "backend" / "ail_data.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_abs_path = db_path.resolve()
        if not db_path.exists():
            db_path.touch()
            print(f"DB_TOUCH=1 path={db_abs_path}")
        else:
            print(f"DB_TOUCH=0 path={db_abs_path}")

        template_path = self._resolve_template_dir()
        if not frontend_dir.exists():
            try:
                shutil.copytree(template_path, frontend_dir, dirs_exist_ok=True, symlinks=True)
            except OSError as exc:
                raise RuntimeError(
                    f"Failed to clone frontend template from {template_path} to {frontend_dir}: {exc}"
                ) from exc
        self._api_client_import = self._resolve_api_client_import(frontend_dir)
        self._ensure_vite_api_proxy(frontend_dir)
        self._reset_frontend_managed_zones(frontend_dir)
        self._ensure_override_scaffold(frontend_dir)
        self._write_managed_system_files(project_root, frontend_dir)
        self._write_frontend_entry_files(project_root, frontend_dir)

        views_dir = frontend_dir / "src" / "views"
        managed_views_dir = frontend_dir / "src" / "ail-managed" / "views"
        try:
            views_dir.mkdir(parents=True, exist_ok=True)
            managed_views_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RuntimeError(f"Failed to create views directory {views_dir}: {exc}") from exc

        pages = self._ensure_forbidden_page(self._frontend_pages())
        hook_catalog_entries: list[dict[str, Any]] = []
        for page in pages:
            page_name = self._sanitize_file_stem(str(page.get("name", "Page")))
            view_path = views_dir / f"{page_name}.vue"
            managed_view_path = managed_views_dir / f"{page_name}.vue"
            content = self._inject_page_slot_hosts(page, self._generate_vue_view(page))
            content = self._inject_section_slot_hosts(page, content)
            content = self._inject_slot_slot_hosts(page, content)
            hook_catalog_entries.append(self._page_hook_catalog_entry(page, content))
            self._safe_write_managed_text(project_root, view_path, content)
            self._safe_write_managed_text(project_root, managed_view_path, content)

        home_page = self._pick_home_page(pages)
        if home_page is not None:
            if self._has_login_page() or self._has_tools_page():
                home_content = self._generate_home_dashboard_view()
            else:
                home_content = self._inject_page_slot_hosts(home_page, self._generate_vue_view(home_page))
                home_content = self._inject_section_slot_hosts(home_page, home_content)
                home_content = self._inject_slot_slot_hosts(home_page, home_content)
            self._safe_write_managed_text(project_root, views_dir / "Home.vue", home_content)
            self._safe_write_managed_text(project_root, managed_views_dir / "Home.vue", home_content)
        if self._has_login_api():
            login_page = {"name": "Login", "path": "/login"}
            login_content = self._inject_page_slot_hosts(login_page, self._generate_login_vue_view())
            login_content = self._inject_section_slot_hosts(login_page, login_content)
            login_content = self._inject_slot_slot_hosts(login_page, login_content)
            hook_catalog_entries.append(self._page_hook_catalog_entry(login_page, login_content))
            self._safe_write_managed_text(project_root, views_dir / "Login.vue", login_content)
            self._safe_write_managed_text(project_root, managed_views_dir / "Login.vue", login_content)

        self._write_generated_routes(project_root, frontend_dir, pages)
        self._write_generated_roles(project_root, frontend_dir, pages)
        self._write_router_index_with_guard(project_root, frontend_dir, pages)
        self._write_hook_catalog(project_root, hook_catalog_entries)
        self._write_local_rebuild_backup_summary(project_root)
        self._write_start_script(project_root)
        self._write_verify_api_script(project_root, self._extract_openapi_paths_from_main(backend_main_content))
        return project_root


if __name__ == "__main__":
    ail_code = (
        "^SYS[BlogV5]"
        "~#LIB[shadcn-vue]"
        "~>DB_TABLE[users]{username:str,password_hash:str}"
        "~>DB_TABLE[posts]{title:str,content:text}"
        "~>DB_REL[users(1)->posts(N)]"
        "~@API[AUTH,/api/login]{>DB_AUTH[users]}"
        "~@API[POST,/api/posts]{>DB_INS[posts]*AUTH}"
        "~@API[GET,/api/posts]{>DB_SEL[posts]*AUTH}"
        "~@PAGE[Home,/]"
        "~#UI[shadcn:Navbar]{theme:dark}"
        "~#UI[shadcn:Card]{layout:grid}"
    )

    parser = AILParserV5(ail_code)
    ast = parser.parse()
    print(json.dumps(ast, indent=4, ensure_ascii=False))

    generator = AILProjectGeneratorV5(ast)
    output_path = generator.build_project()
    print(f"Generated project: {output_path}")
