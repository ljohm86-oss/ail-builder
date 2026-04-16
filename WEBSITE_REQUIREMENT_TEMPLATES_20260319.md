# Website Requirement Templates 2026-03-19

## Purpose

This document provides stable requirement templates for the current website-oriented supported surface.

It exists to reduce prompt drift and make these tasks easier to:

- demo
- trial
- deliver
- benchmark informally

Use this together with:

- `/Users/carwynmac/ai-cl/WEBSITE_PRODUCT_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`
- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`

## Current Scope

These templates are for:

- personal independent site
- company or product website
- ecommerce independent storefront
- after-sales service website
- blog-style personal site (`Partial`)

They are not for:

- full blog or CMS platform
- full ecommerce platform
- application or dashboard generation

## How To Use These Templates

Recommended order:

1. choose the closest website pack
2. start from the canonical template
3. only add one or two richer supported sections at a time
4. avoid mixing website asks with app-like asks
5. run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "<your requirement>" --base-url embedded://local --json
```

## 1. Personal Independent Site

### Canonical Template

```text
做一个个人独立站，包含首页、个人介绍、服务介绍、作品展示、联系方式。
```

### Safer Variation

```text
做一个自由职业者个人网站，包含首页、自我介绍、服务内容、作品展示、联系方式、立即咨询。
```

### Richer Supported Variation

```text
做一个设计师个人网站，包含首页、自我介绍、作品集、客户评价、FAQ、联系方式、立即预约。
```

### Good Additions

- 客户评价
- FAQ
- 联系方式
- CTA
- 作品展示

### Avoid Adding

- 登录
- 用户中心
- 后台管理
- 内容管理
- 发布系统

## 2. Company Introduction Site

### Canonical Template

```text
做一个企业官网，包含首页、公司介绍、团队介绍、FAQ、联系我们。
```

### Safer Variation

```text
做一个品牌官网，包含首页、品牌介绍、核心优势、团队介绍、联系我们。
```

### Richer Supported Variation

```text
做一个企业产品官网，包含首页、产品优势、团队介绍、客户评价、FAQ、数据展示、合作伙伴 Logo、联系我们。
```

### Good Additions

- 团队介绍
- FAQ
- 联系方式
- 数据展示
- 合作伙伴 Logo

### Avoid Adding

- 内部门户
- 员工系统
- 审批流
- 仪表盘

## 3. Product Marketing Website

### Canonical Template

```text
做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。
```

### Safer Variation

```text
做一个产品介绍网站，包含首页、核心功能、产品优势、FAQ、联系我们、立即开始。
```

### Richer Supported Variation

```text
做一个 AI 自动化平台官网，包含首页、功能介绍、客户评价、团队、FAQ、联系我们、立即开始。
```

### Good Additions

- 功能介绍
- 客户评价
- FAQ
- 联系方式
- CTA
- 团队

### Avoid Adding

- 登录后工作台
- 权限系统
- API 控制台
- 用户管理

## 4. Ecommerce Independent Storefront

### Canonical Template

```text
做一个数码商城，包含首页商品列表、商品详情、购物车、结算。
```

### Safer Variation

```text
做一个电商独立站，包含首页商品列表、商品详情、购物车、结算、联系我们。
```

### Richer Supported Variation

```text
做一个服装独立站，包含首页横幅、分类导航、商品列表、商品详情、购物车、结算。
```

### Shop-Oriented Variation

```text
做一个店铺型电商网站，包含首页、店铺页、商品详情、购物车、结算。
```

### Good Additions

- 首页横幅
- 分类导航
- 店铺页
- 商品列表
- 商品详情
- 购物车
- 结算

### Avoid Adding

- 商家后台
- 订单管理系统
- 库存管理
- 多角色运营后台
- 复杂会员体系

## 5. After-Sales Service Website

### Canonical Template

```text
做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。
```

### Safer Variation

```text
做一个售后服务网站，包含退款申请、换货申请、投诉提交、联系客服、售后说明。
```

### Richer Supported Variation

```text
做一个品牌售后服务网站，包含退款申请、换货申请、投诉提交、进度查询说明、联系客服。
```

### Good Additions

- 客服联系
- 售后说明
- 投诉提交
- 退款申请
- 换货申请

### Avoid Adding

- 工单后台
- 客服控制台
- CRM
- 复杂进度系统
- 内部运营面板

## 6. Personal Blog-Style Site (`Partial`)

### Canonical Template

```text
做一个个人博客风格网站，包含首页、文章列表、关于我、联系方式。
```

### Safer Variation

```text
做一个内容风格的个人网站，包含首页、文章列表、作者介绍、联系方式。
```

### Richer Partial Variation

```text
做一个个人内容网站，包含首页、文章列表、精选内容、关于我、FAQ、联系方式。
```

### Good Additions

- 文章列表
- 精选内容
- 作者介绍
- FAQ
- 联系方式

### Avoid Adding

- 发文后台
- 标签管理
- 评论系统
- 搜索系统
- CMS

## Prompt Hygiene Rules

To stay inside the strongest current website surface:

- keep one clear website intent
- name sections explicitly
- prefer homepage-led language
- avoid mixing platform, dashboard, backend, auth, and CMS requirements into the same prompt

Good:

```text
做一个企业产品官网，包含首页、功能介绍、FAQ、联系我们、客户评价。
```

Bad:

```text
做一个产品官网，同时要有登录、用户后台、文章管理、订单管理、数据看板。
```

## Recommended Demo Order

If we want the most stable sequence for demos or first-user runs:

1. company or product website
2. personal independent site
3. ecommerce independent storefront
4. after-sales service website
5. blog-style personal site (`Partial`)

## One-Line Conclusion

The best way to keep website generation stable today is to use one clear website intent, explicit supported sections, and templates that stay inside `landing`, `ecom_min`, or `after_sales` without drifting into app, CMS, or platform language.
