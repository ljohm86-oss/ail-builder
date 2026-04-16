# Website Demo Pack 2026-03-19

## Purpose

This document packages the current website-oriented product surface into a practical demo guide.

Use it to answer:

- which website cases are best suited for demos right now
- what requirement should be used for each case
- what command should be run
- what success signals should be highlighted
- what language should be used during the demo

Use this together with:

- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_PRODUCT_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_DELIVERY_CHECKLIST_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_REQUIREMENT_TEMPLATES_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.md`

## Demo Truth

Current best-fit website demo surface:

- personal independent site
- company or product website
- ecommerce independent storefront
- after-sales service website

Usable but secondary:

- blog-style personal site (`Partial`)

Do not demo as formal current promise:

- full application or dashboard
- full ecommerce platform
- full CMS or blog platform

## Preferred Demo Order

Use this order for the strongest current story:

1. Company / Product Website
2. Personal Independent Site
3. Ecommerce Independent Storefront
4. After-Sales Service Website
5. Blog-Style Personal Site (`Partial`, optional)

This order is intentional:

- it starts with the strongest `landing` surface
- then shows a second `landing` variant with a more personal outcome
- then demonstrates `ecom_min`
- then demonstrates `after_sales`
- and only then shows the `Partial` blog-style case if needed

## Canonical Demo Flow

Recommended demo flow:

```text
trial-run -> project go -> project preview -> project export-handoff
```

Recommended base command pattern:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "<requirement>" --base-url embedded://local --json
```

Then follow with:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project go --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project preview --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project export-handoff --base-url embedded://local --json
```

## Pack 1. Company / Product Website

### Why Start Here

- strongest current website-oriented surface
- richest stable `landing` result
- easy to explain to new users

### Demo Requirement

```text
做一个企业产品官网，包含首页、产品优势、团队介绍、客户评价、FAQ、数据展示、合作伙伴 Logo、联系我们。
```

### Best Command

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个企业产品官网，包含首页、产品优势、团队介绍、客户评价、FAQ、数据展示、合作伙伴 Logo、联系我们。" --base-url embedded://local --json
```

### What To Highlight

- `detected_profile = landing`
- first-pass success without repair
- `project_go_route = project_continue_diagnose_compile_sync`
- `preview_primary_target = artifact_root`
- `export_primary_target_label = artifact_root`

### Safe Demo Language

- company introduction website
- product marketing website
- enterprise or brand website

Avoid:

- enterprise portal
- dashboard
- internal business system

## Pack 2. Personal Independent Site

### Why It Matters

- shows that the same website surface is not limited to corporate positioning
- helps explain creator, freelancer, and service-site use cases

### Demo Requirement

```text
做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。
```

### Best Command

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。" --base-url embedded://local --json
```

### What To Highlight

- `detected_profile = landing`
- website-oriented structure without app drift
- portfolio/service/intro style fit
- stable preview and export handoff

### Safe Demo Language

- personal independent site
- creator or freelancer website
- portfolio-like website

Avoid:

- creator dashboard
- member area
- content management product

## Pack 3. Ecommerce Independent Storefront

### Why It Matters

- proves the product is not only a marketing-site generator
- shows current `ecom_min` boundary clearly

### Demo Requirement

```text
做一个服装独立站，包含首页横幅、分类导航、商品列表、商品详情、购物车、结算。
```

### Best Command

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个服装独立站，包含首页横幅、分类导航、商品列表、商品详情、购物车、结算。" --base-url embedded://local --json
```

### What To Highlight

- `detected_profile = ecom_min`
- storefront funnel is present
- category or shop-oriented structure is present
- stable compile, sync, preview, and export handoff

### Safe Demo Language

- minimal ecommerce independent storefront
- storefront-style website
- simple store funnel

Avoid:

- ecommerce platform
- merchant admin
- inventory and operations system

## Pack 4. After-Sales Service Website

### Why It Matters

- demonstrates a non-marketing, service-intake website surface
- shows `after_sales` as a formal supported profile

### Demo Requirement

```text
做一个品牌售后服务网站，包含退款申请、换货申请、投诉提交、进度查询说明、联系客服。
```

### Best Command

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个品牌售后服务网站，包含退款申请、换货申请、投诉提交、进度查询说明、联系客服。" --base-url embedded://local --json
```

### What To Highlight

- `detected_profile = after_sales`
- intake-oriented structure instead of app-style workflow sprawl
- stable project go / preview / export handoff

### Safe Demo Language

- after-sales service website
- refund, exchange, and complaint intake website

Avoid:

- support operations platform
- CRM
- internal service console

## Pack 5. Blog-Style Personal Site (`Partial`)

### When To Show It

- only if someone explicitly asks whether blog-style output is possible
- do not use as the opening demo

### Demo Requirement

```text
做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。
```

### Best Command

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。" --base-url embedded://local --json
```

### What To Highlight

- `detected_profile = landing`
- current output is content-forward and website-oriented
- it remains inside the current website boundary

### Safe Demo Language

- blog-style personal site
- content-forward personal website

Avoid:

- blog platform
- CMS
- publishing backend

## Success Signals

Across all supported website demos, look for:

- expected frozen profile detected
- `trial-run` succeeds
- `repair_used = false` in the normal path
- `project go` succeeds
- `project preview` resolves to `artifact_root`
- `project export-handoff` resolves `artifact_root`
- no app, dashboard, CMS, or platform drift in the language or output

## What Not To Do In A Demo

Do not:

- pitch `app_min` as a current product surface
- mix website asks with dashboard or admin asks
- promise full ecommerce or CMS behavior
- open with the partial blog case
- imply IDE or Studio is the primary product truth

## One-Line Summary

The current strongest demo surface is a CLI-first website product story built around company/product sites, personal independent sites, minimal ecommerce storefronts, and after-sales service websites, with blog-style sites shown only as a partial extension.
