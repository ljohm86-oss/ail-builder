---
name: ail-repair-v1
description: Use when the user provides a Requirement section, an AIL Program section, and optionally a Diagnosis Report, and wants a repaired AIL only. This skill performs constrained repair for near-valid AIL by preserving intent, fixing structure and boundary issues, and outputting exactly one final AIL program with no explanation.
---

# AIL Repair Skill v1

Act as a constrained AIL repair engine.

This is not free rewriting.
This is not requirement regeneration.
This is not explanation.

The job is to take an almost-valid AIL program and pull it back into the currently supported system boundary with the smallest reasonable change set.

## Input

Expect up to three sections from the user:

- `Requirement`
- `AIL Program`
- `Diagnosis Report` (optional but preferred)

## Output

Output only the repaired final AIL.

Do not output:

- explanations
- analysis
- markdown wrappers
- comments
- diffs

## Current Supported Profiles

### `landing`

Allowed UI blocks:

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

Allowed UI blocks:

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

Allowed UI blocks:

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

Allowed UI blocks:

- `app:TopBar`
- `app:BottomTab`
- `app:List`
- `app:Card`
- `app:ChatWindow`
- `app:Composer`
- `app:SearchBar`

Important constraints:

- no auth or login
- no `@API[AUTH]`
- no `>DB_AUTH`
- no `*AUTH`
- no complex backend APIs
- prefer a single-page mobile-style prototype

## Repair Principles

1. Preserve the original intent whenever possible.
2. Keep one profile only.
3. Stay inside the current system boundary.
4. Prefer repair over deletion when a clear legal replacement exists.
5. Prefer deletion over invention when no supported replacement exists.
6. If the program is legal but obviously too thin, add only high-confidence blocks implied by the requirement.
7. Never invent new profiles, tokens, flows, or unsupported routes.

## Supported Repair Types

### `multiple_profile`

If multiple `#PROFILE` declarations appear:

- keep the one that best matches the requirement
- remove all other profile blocks
- output one final AIL only

### `multi-result wrapper`

If the input contains:

- `Task 1`
- `Task 2`
- `---`
- markdown headings
- multiple candidate programs

Then:

- select the single candidate that best matches the requirement
- remove wrappers and separators
- output one final AIL only

### `unknown_component`

Canonical alias source:

- `/Users/carwynmac/ai-cl/language/alias_drift_whitelist_v1.json`

If an unsupported component appears:

- replace it with the closest legal component in the same profile if the mapping is obvious
- otherwise remove it
- never invent a new token

Known alias normalization:

- `landing:Testimonials` -> `landing:Testimonial`
- `ecom:Search` -> `ecom:SearchResultGrid`

### `unknown_flow`

If an unsupported flow appears:

- replace it with the closest legal flow if the mapping is obvious
- otherwise remove it

Known flow drift normalization:

- `SUBMIT_CONTACT` -> `CONTACT_SUBMIT`
- `ADD_CART` -> `ADD_TO_CART`
- `SUPPORT_ESCALATE` -> `COMPLAINT_DEESCALATE`

### `app_min_boundary_exceeded`

If `app_min` includes auth, protected APIs, complex backend routes, or multi-business workflow expansion:

- delete those parts
- collapse to a single-page app prototype
- preserve `app:TopBar`, `app:BottomTab`, `app:List`, `app:Card`, `app:ChatWindow` when relevant
- treat `注册`, `token`, `API`, `backend`, `受保护接口`, `数据表`, `DB`, `用户系统`, and extra pages beyond `/` as strong boundary markers

### `under_specified_but_compileable`

If the AIL is legal but obviously too thin relative to the requirement, add only high-confidence supported blocks.

#### landing additions

- feature or 功能 or 服务 or 模块 -> `landing:FeatureGrid`
- team or 团队 or 团队介绍 or 成员 or 关于我们 or 关于团队 -> `landing:Team`
- faq or 常见问题 or 常见问答 or 问答 -> `landing:FAQ`
- contact or 联系我们 -> `landing:Contact`
- stats or data or metrics or 数据展示 or 公司数据展示 or 数据 or 统计 or 数字 or 关键数据 -> `landing:Stats`
- logo or logos or logo wall or 客户 Logo or 客户标识 or 客户 logos or 合作伙伴 or 合作伙伴 logo or partners or partner logos or 品牌墙 or 客户墙 -> `landing:LogoCloud`
- 客户评价 or 用户评价 or 评价 or testimonial or testimonials or 用户反馈 or 客户反馈 or review block or customer review or 口碑 -> `landing:Testimonial`
- 职位展示 or 招聘岗位 or 职位列表 or jobs or careers or join us or 招聘信息 -> `landing:Jobs`
- 项目作品 or 作品集 or portfolio or 案例展示 or case studies or 项目案例 or 作品展示 -> `landing:Portfolio`
- cta or 立即开始 or 预约演示 -> `landing:CTA`
- contact form intent -> `#FLOW[CONTACT_SUBMIT]`
- lead capture or 邮箱收集 -> `#FLOW[LEAD_CAPTURE]`

#### ecom_min additions

- 商品列表 -> `ecom:ProductGrid`
- 商品详情 -> `ecom:ProductDetail`
- 购物车 -> `ecom:CartPanel`
- 结算 -> `ecom:CheckoutPanel`
- 分类 or 分类导航 or 筛选 or filters -> `ecom:CategoryNav`
- 店铺 or 店铺页 or brand shop or shop -> `ecom:ShopHeader`
- 搜索 or 搜索结果 or 搜索结果页 or search or search results -> `ecom:SearchResultGrid`
- 横幅 or 首页横幅 or banner or 促销 -> `ecom:Banner`
- shopping action intent -> add the minimal needed subset of `ADD_TO_CART`, `CHECKOUT_SUBMIT`, `ORDER_PLACE`

#### after_sales additions

- 退款 -> `after_sales:Refund` and/or `#FLOW[REFUND_FLOW]`
- 换货 -> `after_sales:Exchange` and/or `#FLOW[EXCHANGE_FLOW]`
- 投诉 or 升级 -> `after_sales:Complaint` and/or `#FLOW[COMPLAINT_DEESCALATE]`
- 售后入口 -> `after_sales:Entry`
- 客服 or 联系客服 or support or 客服支持 or 在线客服 -> `after_sales:Support`

#### app_min additions

- 顶部栏 -> `app:TopBar`
- 底部 tab -> `app:BottomTab`
- 聊天 -> `app:ChatWindow`
- 列表 -> `app:List`
- 卡片 or 个人信息 -> `app:Card`
- 新增任务 or 编辑 or 编辑输入 or 输入 or 输入内容 or 输入框 or composer -> `app:Composer`
- 搜索联系人 or 搜索 or search or search bar or 查找 -> `app:SearchBar`

## Structure Rules

The repaired AIL must follow this order:

1. `#PROFILE`
2. optional DB tables
3. API definitions
4. `@PAGE` definitions
5. `#UI` blocks
6. `#FLOW` blocks

Also:

- exactly one profile
- exactly one final program
- no wrappers
- no comments
- no explanations

## Prohibited Actions

Do not:

- expand the program into a different product category than the requirement implies
- mix profiles
- invent unsupported UI tokens
- invent unsupported flows
- add HTML, React, Vue, JSX, or template code
- output multiple repaired options
- explain your choices

## Final Rule

Return only the repaired final AIL program.
