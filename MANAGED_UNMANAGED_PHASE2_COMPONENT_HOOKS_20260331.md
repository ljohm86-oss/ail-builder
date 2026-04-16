# Managed / Unmanaged Phase 2 Component Hooks 2026-03-31

## Purpose

This document captures the second practical step of the managed / unmanaged frontend boundary:

- unmanaged component hooks now have a real runtime connection into generated pages
- users can place durable Vue components or HTML partials in one stable folder
- rebuilds preserve those hook files

## Current Hook Model

Generated frontend projects now ship a managed host component:

- `frontend/src/ail-managed/system/AILSlotHost.vue`

The frontend entry now globally registers:

- `AILSlotHost`

Every generated page now receives two default page-level hook points:

- `page.<page-key>.before`
- `page.<page-key>.after`

Example for a home page:

- `page.home.before`
- `page.home.after`

Phase 2 now also includes the first shipped section-level hook batch.

Phase 2 now also includes the first shipped slot-level hook batch for selected high-value ecom subareas.

Current managed section hook coverage:

- landing / homepage-style pages:
  - `page.home.section.hero.before|after`
  - `page.home.section.about.before|after`
  - `page.home.section.features.before|after`
  - `page.home.section.portfolio.before|after`
  - `page.home.section.pricing.before|after`
  - `page.home.section.testimonials.before|after`
  - `page.home.section.faq.before|after`
  - `page.home.section.contact.before|after`
  - `page.home.section.cta.before|after`
  - `page.home.section.footer.before|after`

- after-sales tracked-case pages:
  - `page.aftersales.section.context.before|after`
  - `page.aftersales.section.case-status.before|after`
  - `page.aftersales.section.case-flow.before|after`
  - `page.aftersales.section.case-ops.before|after`
  - `page.aftersales.section.case-history.before|after`
  - `page.aftersales.section.actions.before|after`
  - `page.aftersales.section.active-panel.before|after`
  - `page.aftersales.section.timeline.before|after`
  - `page.aftersales.section.materials.before|after`
  - `page.aftersales.section.footer-actions.before|after`

- ecom discovery / purchase pages:
  - `page.home.section.header.before|after`
  - `page.home.section.banner.before|after`
  - `page.home.section.service-strip.before|after`
  - `page.home.section.filters.before|after`
  - `page.home.section.hot-products.before|after`
  - `page.home.section.recommend-products.before|after`
  - `page.home.section.shops.before|after`
  - `page.search.section.hero.before|after`
  - `page.search.section.surface.before|after`
  - `page.category.section.hero.before|after`
  - `page.category.section.surface.before|after`
  - `page.shop.section.hero.before|after`
  - `page.shop.section.surface.before|after`
  - `page.shop.section.discovery-bridge.before|after`
  - `page.shop.section.shop-products.before|after`
  - `page.shop.section.recommendations.before|after`
  - `page.product.section.topbar.before|after`
  - `page.product.section.media.before|after`
  - `page.product.section.source-shop.before|after`
  - `page.product.section.purchase.before|after`
  - `page.product.section.add-feedback.before|after`
  - `page.product.section.detail.before|after`
  - `page.product.section.related.before|after`
  - `page.cart.section.hero.before|after`
  - `page.cart.section.steps.before|after`
  - `page.cart.section.service-strip.before|after`
  - `page.cart.section.product-handoff.before|after`
  - `page.cart.section.discovery-memory.before|after`
  - `page.cart.section.purchase-axis.before|after`
  - `page.cart.section.cart-layout.before|after`
  - `page.cart.section.summary-panel.before|after`
  - `page.checkout.section.hero.before|after`
  - `page.checkout.section.steps.before|after`
  - `page.checkout.section.service-strip.before|after`
  - `page.checkout.section.checkout-handoff.before|after`
  - `page.checkout.section.discovery-memory.before|after`
  - `page.checkout.section.purchase-axis.before|after`
  - `page.checkout.section.completion-banner.before|after`
  - `page.checkout.section.return-axis.before|after`
  - `page.checkout.section.followup.before|after`
  - `page.checkout.section.address.before|after`
  - `page.checkout.section.payment.before|after`
  - `page.checkout.section.summary-panel.before|after`
  - `page.checkout.section.summary-footer.before|after`

Current managed slot hook coverage:

- ecom product purchase panel:
  - `page.product.section.purchase.slot.purchase-strip.before|after`
  - `page.product.section.purchase.slot.field-grid.before|after`
  - `page.product.section.purchase.slot.decision-grid.before|after`
  - `page.product.section.purchase.slot.actions.before|after`

- ecom checkout completion / return path:
  - `page.checkout.section.return-axis.slot.return-flow.before|after`
  - `page.checkout.section.followup.slot.followup-actions.before|after`

- after-sales tracked-case path:
  - `page.aftersales.section.actions.slot.entry-strip.before|after`
  - `page.aftersales.section.actions.slot.cards.before|after`
  - `page.aftersales.section.active-panel.slot.panel-head.before|after`
  - `page.aftersales.section.active-panel.slot.panel-support-strip.before|after`
  - `page.aftersales.section.timeline.slot.timeline-grid.before|after`
  - `page.aftersales.section.materials.slot.materials-grid.before|after`
  - `page.aftersales.section.footer-actions.slot.support-footer-strip.before|after`

- landing / company-homepage path:
  - `page.home.section.hero.slot.brand-grid.before|after`
  - `page.home.section.hero.slot.hero-actions.before|after`
  - `page.home.section.testimonials.slot.quote-grid.before|after`
  - `page.home.section.faq.slot.scan-strip.before|after`
  - `page.home.section.cta.slot.capture-strip.before|after`
  - `page.home.section.cta.slot.close-strip.before|after`
  - `page.home.section.footer.slot.success-bridge.before|after`

Phase 2 now also includes lightweight hook context payloads.

Current generated hook context fields:

- page hooks:
  - `pageKey`
  - `pageName`
  - `pagePath`
  - `profiles`
  - `hookScope`
- section hooks:
  - all page-hook fields above
  - `sectionKey`

Selected landing and after-sales surfaces now also ship small runtime summaries inside `context.runtime`:

- landing / homepage-style pages:
  - `singlePageLanding`
  - `navCount`
  - `faqCount`
  - `contactEnabled`
  - `contactSent`
  - `leadSent`
  - `portfolioMode`
- after-sales:
  - `hasOrderContext`
  - `activePanel`
  - `hasActivePanel`
  - `trackedCaseOwner`
  - `trackedCaseFocus`
  - `caseStepCount`

The first ecom runtime-state extension now also ships inside `context.runtime` for selected surfaces:

- search:
  - `keyword`
  - `activeCategory`
  - `resultCount`
- category:
  - `categoryName`
  - `sortBy`
  - `resultCount`
- shop:
  - `shopId`
  - `shopName`
  - `shopProductCount`
  - `recommendedCount`
  - `hasDiscoverySource`
- product:
  - `hasShopSource`
  - `hasDiscoverySource`
  - `spec`
  - `quantity`
  - `cartCount`
  - `hasAddFeedback`
- cart:
  - `itemCount`
  - `grandTotal`
  - `hasProductSource`
  - `hasDiscoverySource`
  - `hasShopSource`
- checkout:
  - `displayItemCount`
  - `displayGrandTotal`
  - `paymentLabel`
  - `hasProductSource`
  - `hasDiscoverySource`
  - `hasRecentOrder`

## Durable User Hook Folder

Users should place durable hook files in:

- `frontend/src/ail-overrides/components/`

Supported file types in Phase 2:

- Vue components:
  - `page.home.before.vue`
  - `page.contact.after.vue`
- HTML partials:
  - `page.home.after.html`

The filename without extension becomes the hook name.

Nested folders are allowed. Their relative path becomes a dotted hook key.

Example:

- `frontend/src/ail-overrides/components/marketing/banner.vue`

maps to:

- `marketing.banner`

## Runtime Behavior

At runtime, `AILSlotHost` resolves hook files in this order:

1. matching Vue component by hook name
2. matching HTML partial by hook name
3. nothing if no matching hook exists

This means generated pages can expose stable hook points without requiring the user to edit managed views directly.

Phase 3 now also adds a generated per-project hook catalog under `.ail/hook_catalog.md` and `.ail/hook_catalog.json`, so operators can inspect the available page / section / slot hooks and the current `context.runtime` coverage without reading managed Vue files directly.

For Vue hook components, `AILSlotHost` now passes:

- `context`
- `hookName`

For HTML partial hooks, `AILSlotHost` now renders wrapper data attributes:

- `data-ail-hook`
- `data-ail-context`

## Verified Outcomes

Reference validation sample:

- `/Users/carwynmac/ai-cl/output_projects/ManagedHookSmoke`
- `/Users/carwynmac/ai-cl/output_projects/SectionHookLandingSmoke`
- `/Users/carwynmac/ai-cl/output_projects/SectionHookAfterSalesSmoke`
- `/Users/carwynmac/ai-cl/output_projects/ContextHookSmoke`
- `/Users/carwynmac/ai-cl/output_projects/ContextAfterSalesSmoke`
- `/Users/carwynmac/ai-cl/output_projects/LandingRuntimeContextReview`
- `/Users/carwynmac/ai-cl/output_projects/AfterSalesRuntimeContextReview`
- `/Users/carwynmac/ai-cl/output_projects/EcomSectionHookReview`
- `/Users/carwynmac/ai-cl/output_projects/EcomRuntimeContextReview`
- `/Users/carwynmac/ai-cl/output_projects/EcomChildSlotReview`
- `/Users/carwynmac/ai-cl/output_projects/AfterSalesChildSlotReview`
- `/Users/carwynmac/ai-cl/output_projects/LandingChildSlotReview`

The following were rechecked:

- generated views now contain:
  - `<AILSlotHost name="page.home.before" />`
  - `<AILSlotHost name="page.home.after" />`
- generated managed system files now contain:
  - `frontend/src/ail-managed/system/AILSlotHost.vue`
- unmanaged hook guidance now exists in:
  - `frontend/src/ail-overrides/components/README.md`
- a user-added:
  - `frontend/src/ail-overrides/components/page.home.before.vue`
  - `frontend/src/ail-overrides/components/page.home.after.html`
  survived a rebuild
- landing section hooks were generated into:
  - `/Users/carwynmac/ai-cl/output_projects/SectionHookLandingSmoke/frontend/src/ail-managed/views/Home.vue`
- after-sales section hooks were generated into:
  - `/Users/carwynmac/ai-cl/output_projects/SectionHookAfterSalesSmoke/frontend/src/ail-managed/views/AfterSales.vue`
- the rebuilt sample still completed:
  - `npm run build`
- the section-hook landing sample completed:
  - `npm run build`
- the section-hook after-sales sample completed:
  - `npm run build`
- context-hook samples now also contain:
  - `:context='...'`
- the managed hook host now forwards:
  - `:context="props.context"`
  - `:hook-name="props.name"`
- HTML partial hooks now also receive:
  - `data-ail-hook`
  - `data-ail-context`
- the context landing sample completed:
  - `npm run build`
- the context after-sales sample completed:
  - `npm run build`
- the landing runtime-context sample now also contains:
  - `context.runtime`
  - landing runtime summaries
- the landing runtime-context sample completed:
  - `npm run build`
- the after-sales runtime-context sample now also contains:
  - `context.runtime`
  - tracked-case runtime summaries
- the after-sales runtime-context sample completed:
  - `npm run build`
- the ecom section-hook sample now also contains:
  - discovery hooks
  - purchase-path hooks
  - completion-path hooks
- the ecom section-hook sample completed:
  - `npm run build`
- the ecom runtime-context sample now also contains:
  - `context.runtime`
  - search/category/shop/product/cart/checkout runtime summaries
- the ecom runtime-context sample completed:
  - `npm run build`
- the ecom child-slot sample now also contains:
  - product purchase child slots
  - checkout completion / followup child slots
- the ecom child-slot sample completed:
  - `npm run build`
- the after-sales child-slot sample now also contains:
  - tracked-case action / panel / support child slots
- the after-sales child-slot sample completed:
  - `npm run build`
- the landing child-slot sample now also contains:
  - hero / FAQ / CTA / footer child slots
- the landing child-slot sample completed:
  - `npm run build`

## Current Truth

Phase 2 component hooks do **not** mean full arbitrary component override for every generated section.

The current truth is:

- page-level before/after hooks are real and durable
- the first landing / after-sales section-level hooks are real and durable
- the first ecom discovery / purchase section-level hooks are now real and durable
- the first ecom child-slot hooks are now real and durable for selected product / checkout subareas
- the first after-sales child-slot hooks are now real and durable for selected tracked-case subareas
- the first landing / company-homepage child-slot hooks are now real and durable for selected hero / FAQ / CTA / footer subareas
- those page-level and section-level hooks now also carry lightweight context
- selected landing and after-sales hooks now also carry small runtime summaries
- selected ecom hooks now also carry small runtime summaries instead of name-only context
- the hook folder is now part of the intended user workflow
- rebuilds preserve hook files
- `AIL/source` is still the place for durable structure/content changes
- hook coverage is still selective rather than universal

## Next Recommended Step

The safest follow-up from here is:

1. decide which generated surfaces deserve section-level hooks next
2. decide whether the current lightweight context should be expanded with richer runtime state for selected surfaces
