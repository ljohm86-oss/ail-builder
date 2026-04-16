# Frozen Profile Examples v1

## Purpose

This document provides the first supported example set for the frozen AIL v1 profiles.

Use it together with:

- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`

The goal is simple:

- help a user choose a good first requirement
- make the expected outcome predictable
- reduce first-run ambiguity

## Frozen Profiles Covered

The frozen profiles for v1 are:

- `landing`
- `ecom_min`
- `after_sales`

`app_min` is intentionally excluded from this example pack because it remains experimental.

## How To Use These Examples

Recommended usage:

1. choose one profile below
2. copy the recommended requirement
3. run the CLI golden path from `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
4. compare the generated result to the expected profile and expected AIL characteristics

## Example 1: Landing

### Use Case

AI SaaS or company website with standard marketing sections.

### Recommended Requirement

```text
做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。
```

### Expected Profile

- `landing`

### Expected AIL Characteristics

The generated or repaired AIL should usually include:

- `#PROFILE[landing]`
- `@PAGE[Home,/]`
- `landing:Header`
- `landing:Hero`
- `landing:FeatureGrid`
- `landing:FAQ`
- `landing:Contact`
- `landing:CTA`
- `landing:Footer`
- `#FLOW[CONTACT_SUBMIT]`

### Expected Outcome

After `compile --cloud` and `sync`, the project should behave like a standard marketing/landing site.

Expected traits:

- homepage-oriented structure
- feature presentation
- FAQ block
- contact block
- contact submit flow in supported boundary

### Good Fit Signals

This example is a good fit if the user wants:

- product site
- company site
- marketing site
- landing page

### Poor Fit Signals

This example is not a good fit if the user actually wants:

- product catalog and checkout flow
- after-sales workflow
- app-style mobile prototype

## Example 2: Landing With Richer Coverage

### Use Case

Marketing site that needs more than the minimum landing skeleton.

### Recommended Requirement

```text
做一个 AI 自动化平台官网，包含首页、功能介绍、客户评价、团队、FAQ、联系我们、立即开始。
```

### Expected Profile

- `landing`

### Expected AIL Characteristics

The generated or repaired AIL should usually include:

- `landing:Header`
- `landing:Hero`
- `landing:FeatureGrid`
- `landing:Testimonial`
- `landing:Team`
- `landing:FAQ`
- `landing:Contact`
- `landing:CTA`
- `landing:Footer`
- `#FLOW[CONTACT_SUBMIT]`

### Expected Outcome

This should produce a richer landing experience than the minimum example, while still remaining clearly inside the `landing` profile boundary.

## Example 3: E-commerce

### Use Case

Minimum store flow with product browsing, cart, and checkout.

### Recommended Requirement

```text
做一个数码商城，包含首页商品列表、商品详情、购物车、结算。
```

### Expected Profile

- `ecom_min`

### Expected AIL Characteristics

The generated or repaired AIL should usually include:

- `#PROFILE[ecom_min]`
- `@PAGE[Home,/]`
- `@PAGE[Product,/product/:id]`
- `@PAGE[Cart,/cart]`
- `@PAGE[Checkout,/checkout]`
- `ecom:Header`
- `ecom:ProductGrid`
- `ecom:ProductDetail`
- `ecom:CartPanel`
- `ecom:CheckoutPanel`
- `#FLOW[ADD_TO_CART]`
- `#FLOW[CHECKOUT_SUBMIT]`

### Expected Outcome

After `compile --cloud` and `sync`, the project should behave like a minimal store flow.

Expected traits:

- product listing
- product detail
- cart
- checkout

### Good Fit Signals

This example is a good fit if the user wants:

- a lightweight catalog
- single-store flow
- basic checkout path

### Poor Fit Signals

This example is not a good fit if the user wants:

- marketplace complexity
- deep account system
- advanced promotions
- custom backend commerce logic outside the current boundary

## Example 4: E-commerce With Search / Shop Coverage

### Use Case

Store flow with additional supported catalog navigation.

### Recommended Requirement

```text
做一个店铺型电商网站，包含首页、店铺页、商品详情、购物车、结算。
```

### Expected Profile

- `ecom_min`

### Expected AIL Characteristics

The generated or repaired AIL should usually include:

- `ecom:ShopHeader`
- `ecom:ProductGrid`
- `ecom:ProductDetail`
- `ecom:CartPanel`
- `ecom:CheckoutPanel`
- `#FLOW[ADD_TO_CART]`
- `#FLOW[CHECKOUT_SUBMIT]`
- `#FLOW[ORDER_PLACE]`

### Expected Outcome

This should still remain inside `ecom_min`, but exercise more of the supported page/navigation surface than the minimum store example.

## Example 5: After Sales

### Use Case

Refund / exchange / complaint intake within the supported after-sales boundary.

### Recommended Requirement

```text
做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。
```

### Expected Profile

- `after_sales`

### Expected AIL Characteristics

The generated or repaired AIL should usually include:

- `#PROFILE[after_sales]`
- `@PAGE[AfterSales,/after-sales]`
- `after_sales:Entry`
- `after_sales:Refund`
- `after_sales:Exchange`
- `after_sales:Complaint`
- `after_sales:Support`
- `#FLOW[REFUND_FLOW]`
- `#FLOW[EXCHANGE_FLOW]`
- `#FLOW[COMPLAINT_DEESCALATE]`

### Expected Outcome

After `compile --cloud` and `sync`, the project should behave like a structured after-sales intake surface.

Expected traits:

- request entry
- refund path
- exchange path
- complaint path
- support/contact expression inside current boundary

### Good Fit Signals

This example is a good fit if the user wants:

- refund
- exchange
- complaint intake
- customer support entry

### Poor Fit Signals

This example is not a good fit if the user wants:

- full CRM
- complex support ticketing backend
- arbitrary workflow engine behavior

## Example 6: After Sales Minimal

### Use Case

Smaller support-oriented after-sales page that still fits the supported profile.

### Recommended Requirement

```text
做一个售后页面，用户可以申请退款并联系客服。
```

### Expected Profile

- `after_sales`

### Expected AIL Characteristics

The generated or repaired AIL should usually include:

- `after_sales:Entry`
- `after_sales:Refund`
- `after_sales:Support`
- `#FLOW[REFUND_FLOW]`

### Expected Outcome

This is a smaller but cleaner after-sales example and is often a better first run than trying to exercise every supported block at once.

## Profile Selection Guide

Use this table when deciding which frozen profile to start with.

| If the user wants... | Start with... |
| --- | --- |
| company site, product site, marketing site | `landing` |
| product list, product detail, cart, checkout | `ecom_min` |
| refund, exchange, complaint, customer support entry | `after_sales` |

## What To Avoid In First Runs

To keep the first experience reliable, avoid these on the first attempt:

- experimental `app_min`
- multi-business system prompts
- auth-heavy requests
- requests that combine website, store, and after-sales into one project
- prompts that ask for unsupported backend logic

## What Success Looks Like

A successful first run should produce:

- the expected frozen profile
- an AIL program that diagnose accepts or repair can quickly recover
- a successful `compile --cloud`
- a successful `sync`
- generated files only in managed zones

## One-Line Recommendation

If you want the highest probability of a good first experience, start with the minimum landing example or the minimum after-sales example before trying broader prompts.
