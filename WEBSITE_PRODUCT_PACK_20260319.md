# Website Product Pack 2026-03-19

## Purpose

This document packages the current supported website-oriented product surface into a form that is easier to use for:

- internal delivery decisions
- demos
- first-user trials
- future sales or positioning language

It is not a replacement for the broader planning documents. It is the operational pack for the website surface that is already closest to product-ready.

Use this together with:

- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`
- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`

## Current Website Product Truth

As of 2026-03-19, the current formal website product surface is:

- personal independent site
- company introduction site
- product marketing site
- enterprise or brand website
- ecommerce independent storefront
- after-sales service website

Partial only:

- personal blog-style site

Out of scope:

- full blog or CMS platform
- full ecommerce platform
- application or dashboard product

## Pack Structure

The current website product pack is best understood as four formal packs plus one partial pack:

1. Personal Independent Site Pack
2. Company / Product Website Pack
3. Ecommerce Independent Storefront Pack
4. After-Sales Service Website Pack
5. Personal Blog-Style Site Pack (Partial)

## Pack 1. Personal Independent Site

### Current Status

- Supported

### Best-Fit Profile

- `landing`

### Best-Fit Outcomes

- personal homepage
- creator site
- freelancer site
- portfolio-like presentation site
- consultant or service introduction site

### Canonical Requirement

```text
做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。
```

### Stronger Demo Requirement

```text
做一个设计师个人网站，包含首页、自我介绍、作品集、客户评价、FAQ、联系方式、立即预约。
```

### Best Demo Entry

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。" --base-url embedded://local --json
```

### What To Expect

- `landing` profile
- homepage-led structure
- simple multi-section presentation
- no app-style authenticated workflows

### Safe Positioning

Use wording like:

- supported as a personal independent site
- strong fit for creator, freelancer, and portfolio-like websites

Avoid wording like:

- blog platform
- creator dashboard
- account-based personal product

## Pack 2. Company / Product Website

### Current Status

- Supported

### Best-Fit Profile

- `landing`

### Best-Fit Outcomes

- company introduction site
- SaaS landing site
- product marketing website
- startup website
- brand presentation site

### Canonical Requirement

```text
做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。
```

### Stronger Demo Requirement

```text
做一个企业产品官网，包含首页、产品优势、团队介绍、客户评价、FAQ、数据展示、合作伙伴 Logo、联系我们。
```

### Best Demo Entry

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario landing --base-url embedded://local --json
```

### What To Expect

- `landing` profile
- feature and CTA oriented structure
- FAQ / contact / stats / logo wall style sections
- no admin workflows or full business systems

### Safe Positioning

Use wording like:

- supported as a company introduction and product website
- strongest current website surface

Avoid wording like:

- complete business system
- internal enterprise portal
- application dashboard

## Pack 3. Ecommerce Independent Storefront

### Current Status

- Supported

### Best-Fit Profile

- `ecom_min`

### Best-Fit Outcomes

- minimal storefront homepage
- product list and product detail
- cart
- checkout
- category or shop navigation

### Canonical Requirement

```text
做一个数码商城，包含首页商品列表、商品详情、购物车、结算。
```

### Stronger Demo Requirement

```text
做一个服装独立站，包含首页横幅、分类导航、商品列表、商品详情、购物车、结算。
```

### Best Demo Entry

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario ecom_min --base-url embedded://local --json
```

### What To Expect

- `ecom_min` profile
- storefront-style browsing funnel
- simple product/cart/checkout flow
- category and shop coverage where requested

### Safe Positioning

Use wording like:

- supported as a minimal ecommerce independent storefront
- strong fit for simple store funnel generation

Avoid wording like:

- ecommerce platform
- merchant backend
- inventory, operations, and payment platform

## Pack 4. After-Sales Service Website

### Current Status

- Supported

### Best-Fit Profile

- `after_sales`

### Best-Fit Outcomes

- refund request site
- exchange request site
- complaint submission surface
- support intake page

### Canonical Requirement

```text
做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。
```

### Stronger Demo Requirement

```text
做一个品牌售后服务网站，包含退款申请、换货申请、投诉提交、进度查询说明、联系客服。
```

### Best Demo Entry

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario after_sales --base-url embedded://local --json
```

### What To Expect

- `after_sales` profile
- intake-oriented flow
- support and complaint handling surface
- not a full service operations platform

### Safe Positioning

Use wording like:

- supported as an after-sales service website
- strong fit for refund, exchange, complaint, and support intake

Avoid wording like:

- customer service system
- full CRM or ticket platform

## Pack 5. Personal Blog-Style Site

### Current Status

- Partial

### Best-Fit Profile

- `landing`

### Best-Fit Outcomes

- content-forward homepage
- article-list style presentation
- author page
- content-brand website

### Canonical Requirement

```text
做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。
```

### Safe Demo Entry

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。" --base-url embedded://local --json
```

### What To Expect

- content-site presentation
- landing-like structure
- no post-management backend
- no CMS workflow
- no comment or editorial system

### Safe Positioning

Use wording like:

- partial support for blog-style personal sites
- supported as a content-forward website, not a full blog platform

Avoid wording like:

- blog generator
- CMS site builder
- publishing platform

## Recommended Demo Set

If we want one compact website-oriented demo pack today, the best set is:

1. `landing` company/product site
2. `landing` personal independent site
3. `ecom_min` independent storefront
4. `after_sales` service site

This set shows:

- strongest current marketing-site surface
- strongest current personal-site surface
- strongest current commerce-site surface
- strongest current workflow-intake website surface

## Delivery Language

If we need a short delivery-facing statement today, the safest wording is:

The current AIL CLI-first product can reliably support:

- personal independent websites
- company introduction and product websites
- minimal ecommerce independent storefronts
- after-sales service websites

It can partially support:

- blog-style personal websites

It should not yet be sold or positioned as:

- a full blog platform
- a full ecommerce platform
- a general application generator

## Product Packaging Implication

This pack suggests the near-term productization effort should focus on:

- making the website packs easier to demo and hand off
- improving preview and artifact consumption for these packs
- preserving a clean distinction between supported website packs and experimental app work

## One-Line Conclusion

The current product is already strong enough to be treated as a website-oriented CLI-first system with four formal delivery packs and one partial blog-style pack; future work should deepen that website product surface rather than blur it with application promises.
