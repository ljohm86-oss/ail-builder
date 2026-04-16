---
name: ail-generator-v1.2
description: Use when converting product requirements into a single compile-safe AIL program with stronger anti-wrapper rules, stricter single-profile guarantees, and better minimum coverage for landing, ecom_min, after_sales, and experimental app_min.
---

# AIL Generator Skill v1.2

Convert a product requirement into exactly one valid AIL program.

Return only AIL.

Do not explain.
Do not output markdown.
Do not output HTML, React, Vue, JSX, or comments.

## Hard Output Rules

1. Output exactly one AIL program.
2. Output exactly one `#PROFILE[...]`.
3. Do not output `Task 1`, `Task 2`, or any wrapper text.
4. Do not output `---`.
5. Do not invent tokens.
6. Do not mix profiles.
7. Stay inside current system boundaries.
8. Do not output alias or drift names when a formal token already exists.

## Supported Profiles

### `landing`

Allowed UI:

- `landing:Header`
- `landing:Hero`
- `landing:FeatureGrid`
- `landing:Stats`
- `landing:LogoCloud`
- `landing:Team`
- `landing:Testimonial`
- `landing:Jobs`
- `landing:Portfolio`
- `landing:FAQ`
- `landing:Pricing`
- `landing:CTA`
- `landing:Contact`
- `landing:Footer`

Allowed flows:

- `CONTACT_SUBMIT`
- `LEAD_CAPTURE`

### `ecom_min`

Allowed UI:

- `ecom:Header`
- `ecom:Banner`
- `ecom:CategoryNav`
- `ecom:ProductGrid`
- `ecom:ProductDetail`
- `ecom:CartPanel`
- `ecom:CheckoutPanel`
- `ecom:ShopHeader`
- `ecom:SearchResultGrid`

Allowed flows:

- `ADD_TO_CART`
- `CHECKOUT_SUBMIT`
- `ORDER_PLACE`

### `after_sales`

Allowed UI:

- `after_sales:Entry`
- `after_sales:Refund`
- `after_sales:Exchange`
- `after_sales:Complaint`
- `after_sales:Support`

Allowed flows:

- `REFUND_FLOW`
- `EXCHANGE_FLOW`
- `COMPLAINT_DEESCALATE`

### `app_min`

Allowed UI:

- `app:TopBar`
- `app:BottomTab`
- `app:List`
- `app:Card`
- `app:ChatWindow`
- `app:Composer`
- `app:SearchBar`

Constraints:

- single-page mobile-style prototype only
- no `DB_TABLE`
- no `@API`
- no auth/login
- no protected backend workflow
- no multi-page business app

## Profile Selection Rule

Pick one profile only.

- `landing`: 官网、公司站、品牌站、SaaS 站、营销页、落地页
- `ecom_min`: 商城、商品、购物车、结算、店铺、分类、搜索结果
- `after_sales`: 售后、退款、换货、投诉、客服升级
  - if support/contact intent appears, prefer explicit support coverage instead of complaint-only approximation
- `app_min`: app 原型、单页移动端、顶部栏、底部 tab、聊天、联系人

When uncertain, choose the closest existing profile instead of inventing structure.

## Landing Coverage Rules

For `landing`, always include this minimum structure:

- `landing:Header`
- `landing:Hero`
- `landing:FeatureGrid`
- `landing:CTA`
- `landing:Footer`

If requirement mentions:

- `team` / `团队介绍` / `成员` / `关于我们` / `关于团队` -> add `landing:Team`
- `FAQ` / `常见问题` / `常见问答` / `问答` -> add `landing:FAQ`
- `客户评价` / `用户评价` / `评价` / `testimonial` / `testimonials` / `用户反馈` / `客户反馈` / `review block` / `customer review` / `口碑` -> add `landing:Testimonial`
- `职位展示` / `招聘岗位` / `职位列表` / `jobs` / `careers` / `join us` / `招聘信息` -> add `landing:Jobs`
- `项目作品` / `作品集` / `portfolio` / `案例展示` / `case studies` / `项目案例` / `作品展示` -> add `landing:Portfolio`
- `contact` / `联系我们` / `联系方式` -> add `landing:Contact` and `#FLOW[CONTACT_SUBMIT]`
- `stats` / `data` / `metrics` / `数据` / `统计` / `数字` / `数据展示` / `公司数据展示` / `关键数据` -> add `landing:Stats`
- `logo` / `logos` / `logo wall` / `客户 Logo` / `客户标识` / `客户 logos` / `合作伙伴` / `合作伙伴 logo` / `partners` / `partner logos` / `品牌墙` / `客户墙` -> add `landing:LogoCloud`
- `pricing` / `价格` -> add `landing:Pricing`
- `lead` / `留资` / `预约演示` / `试用` -> add `#FLOW[LEAD_CAPTURE]`

Use these pages when clearly implied:

- `@PAGE[Home,/]`
- `@PAGE[About,/about]` for 关于我们 / 关于我 / 品牌故事
- `@PAGE[Features,/features]` for 功能 / 服务 / 模块 / 案例
- `@PAGE[Pricing,/pricing]` for 价格
- `@PAGE[Contact,/contact]` for 联系

## Ecom Rules

For `ecom_min`, always generate these pages:

- `@PAGE[Home,/]`
- `@PAGE[Product,/product/:id]`
- `@PAGE[Cart,/cart]`
- `@PAGE[Checkout,/checkout]`

Always include these minimum UI blocks:

- `ecom:Header`
- `ecom:ProductGrid`
- `ecom:ProductDetail`
- `ecom:CartPanel`
- `ecom:CheckoutPanel`

Always include these minimum flows:

- `ADD_TO_CART`
- `CHECKOUT_SUBMIT`

Add when implied:

- 分类 / 分类导航 / 筛选 / filters -> `ecom:CategoryNav`
- 店铺 / 店铺页 / brand shop / shop -> `ecom:ShopHeader`
- 搜索 / 搜索结果 / 搜索结果页 / search / search results -> `ecom:SearchResultGrid`
- 横幅 / 首页横幅 / banner / 促销 -> `ecom:Banner`
- 下单完成语义 -> `ORDER_PLACE`
- `@PAGE[Category,/category/:name]` for 分类 / 分类导航 / 分类页
- `@PAGE[Shop,/shop/:id]` for 店铺 / 店铺页 / brand shop
- `@PAGE[Search,/search]` for 搜索 / 搜索结果 / 搜索结果页

## After Sales Rules

For `after_sales`, always generate:

- `@PAGE[AfterSales,/after-sales]`
- `after_sales:Entry`

Add by intent:

- 退款 -> `after_sales:Refund` and `REFUND_FLOW`
- 换货 -> `after_sales:Exchange` and `EXCHANGE_FLOW`
- 投诉 / 升级 -> `after_sales:Complaint` and `COMPLAINT_DEESCALATE`
- 客服 / 联系客服 / support / 客服支持 / 在线客服 -> `after_sales:Support`
- if requirement mentions `退款 + 客服`, prefer `after_sales:Refund + after_sales:Support`
- if requirement mentions `换货 + 客服`, prefer `after_sales:Exchange + after_sales:Support`

## App Rules

For `app_min`, generate only:

- `@PAGE[Home,/]`

Always include:

- `app:TopBar`
- `app:BottomTab`

Add by intent:

- 列表 / 联系人 / 任务 / 笔记 -> `app:List`
- 卡片 / 我的 / 个人信息 / 发现 -> `app:Card`
- 聊天 / 消息 -> `app:ChatWindow`
- 新增任务 / 编辑 / 编辑输入 / 输入 / 输入内容 / 输入框 / composer -> `app:Composer`
- 搜索联系人 / 搜索 / search / search bar / 查找 -> `app:SearchBar`

Never add:

- login
- auth
- 注册
- token
- `DB_TABLE`
- `@API`
- backend
- 用户系统
- 数据表
- DB
- second page
- multi-page business flow

## Unknown Token Mapping Rule

If the requirement implies an unsupported component, map it to the nearest legal token instead of inventing a new one.

Examples:

- testimonials / testimonial / 用户评价 / 用户反馈 / customer review -> `landing:Testimonial`
- jobs / careers / join us / 职位展示 / 招聘岗位 -> `landing:Jobs`
- portfolio / case studies / 项目作品 / 项目案例 / 作品展示 -> `landing:Portfolio`
- filters -> `ecom:CategoryNav`
- support entry -> `after_sales:Support`
- profile card -> `app:Card`
- input bar / task composer -> `app:Composer`
- contact search / people search -> `app:SearchBar`

## Alias / Drift Normalization Rule

Canonical source:

- `/Users/carwynmac/ai-cl/language/alias_drift_whitelist_v1.json`

Never output these alias names in final AIL.

Always normalize to the formal names below:

- `landing:Testimonials` -> `landing:Testimonial`
- `ecom:Search` -> `ecom:SearchResultGrid`
- `SUBMIT_CONTACT` -> `CONTACT_SUBMIT`
- `ADD_CART` -> `ADD_TO_CART`
- `SUPPORT_ESCALATE` -> `COMPLAINT_DEESCALATE`

## Structure Rule

Output order must be:

1. `#PROFILE`
2. optional `DB_TABLE`
3. optional `@API`
4. `@PAGE`
5. `#UI`
6. `#FLOW`

Use repeated page-local blocks if needed:

- `@PAGE[...]`
- page-local `#UI[...]`
- next `@PAGE[...]`
- page-local `#UI[...]`
- final `#FLOW[...]`

## Final Rule

Return one compile-safe AIL program only.
