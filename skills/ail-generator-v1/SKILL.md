# AIL Generator Skill v1.1

This skill converts product requirements into valid AIL (Application Intermediate Language).

The output MUST be valid AIL code that can be compiled by the AIL compiler.

This version emphasizes **requirement coverage**, not just minimal compile-safe skeletons.

---

# Output Rules

The assistant must follow these rules strictly:

1. Output ONLY AIL code.
2. Do NOT explain anything.
3. Do NOT output HTML, React, Vue, or other code.
4. Do NOT include markdown formatting.
5. Do NOT include comments.
6. Do NOT describe the design.
7. Return only the final AIL program.

---

# Critical Rules

1. Only ONE profile is allowed in a single AIL program.
2. Do NOT mix multiple profiles.
3. Do NOT output unsupported components.
4. Do NOT output unsupported flows.
5. Prefer a complete profile-aligned structure over an overly thin skeleton.

Invalid example:

#PROFILE[landing]
...
#PROFILE[ecom_min]

---

# Supported Profiles

## landing

#PROFILE[landing]

Used for:
- SaaS websites
- company websites
- product landing pages
- marketing websites

Allowed UI blocks:

landing:Header
landing:Hero
landing:FeatureGrid
landing:Stats
landing:LogoCloud
landing:Team
landing:FAQ
landing:Pricing
landing:CTA
landing:Contact
landing:Footer

Allowed flows:

CONTACT_SUBMIT
LEAD_CAPTURE

---

## ecom_min

#PROFILE[ecom_min]

Used for:
- small ecommerce stores
- product showcase stores
- lightweight shopping sites

Allowed UI blocks:

ecom:Header
ecom:Banner
ecom:CategoryNav
ecom:ProductGrid
ecom:ProductDetail
ecom:CartPanel
ecom:CheckoutPanel
ecom:ShopHeader
ecom:SearchResultGrid

Allowed flows:

ADD_TO_CART
CHECKOUT_SUBMIT
ORDER_PLACE

---

## after_sales

#PROFILE[after_sales]

Used for:
- refund portals
- exchange pages
- complaint / support pages

Allowed UI blocks:

after_sales:Entry
after_sales:Refund
after_sales:Exchange
after_sales:Complaint

Allowed flows:

REFUND_FLOW
EXCHANGE_FLOW
COMPLAINT_DEESCALATE

---

## app_min

#PROFILE[app_min]

Used for:
- simple mobile-style web app prototypes
- single-page app-like interfaces

Allowed UI blocks:

app:TopBar
app:BottomTab
app:List
app:Card
app:ChatWindow

Important constraints:
- app_min is experimental
- do NOT include auth/login/protected API/business backend logic
- prefer a single-page mobile-style structure
- do NOT expand into a multi-page business system

---

# Structure Rules

The generated AIL program must follow this order:

#PROFILE

optional database tables

API definitions

@PAGE definitions

#UI blocks

#FLOW blocks

---

# Requirement Coverage Rules

The assistant must not under-specify obvious requested sections.

If the user explicitly asks for a section, the AIL must include a matching supported UI block whenever possible.

## landing coverage mapping

If requirement mentions:
- homepage / 首页 / hero / 主视觉 -> include `landing:Hero`
- feature / 功能 / 功能介绍 -> include `landing:FeatureGrid`
- team / 团队 / 成员介绍 -> include `landing:Team`
- faq / 常见问题 -> include `landing:FAQ`
- pricing / 价格 -> include `landing:Pricing`
- contact / 联系我们 / 联系表单 -> include `landing:Contact`
- customer logos / partners / 客户 logo / 合作伙伴 -> include `landing:LogoCloud`
- statistics / numbers / 数据展示 -> include `landing:Stats`
- conversion / call to action / 立即开始 / 预约演示 -> include `landing:CTA`

For landing tasks:
- do NOT reduce everything to only Header + Hero + Footer
- if 4 or more explicit sections are requested, include those sections explicitly

If contact / lead / demo request is mentioned:
- include one of:
  - `#FLOW[CONTACT_SUBMIT]`
  - `#FLOW[LEAD_CAPTURE]`
depending on which is more suitable

## ecom_min coverage mapping

If requirement mentions:
- product list / 商品列表 / 首页商品 -> include `ecom:ProductGrid`
- product detail / 商品详情 -> include `ecom:ProductDetail`
- cart / 购物车 -> include `ecom:CartPanel`
- checkout / 结算 -> include `ecom:CheckoutPanel`
- category / 分类 -> include `ecom:CategoryNav`
- store / shop / 店铺 -> include `ecom:ShopHeader`
- search result / 搜索结果 -> include `ecom:SearchResultGrid`

If shopping actions are implied:
- include appropriate flows:
  - `#FLOW[ADD_TO_CART]`
  - `#FLOW[CHECKOUT_SUBMIT]`
  - `#FLOW[ORDER_PLACE]`

## after_sales coverage mapping

If requirement mentions:
- refund / 退款 -> include `after_sales:Refund` and/or `#FLOW[REFUND_FLOW]`
- exchange / 换货 -> include `after_sales:Exchange` and/or `#FLOW[EXCHANGE_FLOW]`
- complaint / 投诉 / escalation -> include `after_sales:Complaint` and/or `#FLOW[COMPLAINT_DEESCALATE]`
- service entry / 售后入口 -> include `after_sales:Entry`

## app_min coverage mapping

If requirement mentions:
- chat / 聊天 -> include `app:ChatWindow`
- list / 列表 / 联系人 / 项目列表 -> include `app:List`
- cards / 卡片 / overview -> include `app:Card`
- top bar / header -> include `app:TopBar`
- tab / tabs / bottom navigation -> include `app:BottomTab`

For app_min:
- prefer one main page
- do NOT invent auth/login/API system
- do NOT create a full business workflow app

---

# Coverage Priority Rule

When there is tension between:
- minimal skeleton
- requirement coverage

prefer:
- requirement coverage
as long as the output stays within supported profile boundaries.

The goal is:
- valid AIL
- compile-safe
- but not overly thin

---

# Fallback Rule

If the user asks for unsupported features:
- stay within the nearest supported profile
- preserve the core intent
