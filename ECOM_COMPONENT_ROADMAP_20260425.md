# Ecommerce Component Roadmap

Date: 2026-04-25

## Goal

Turn the current `ecom_min` experimental lane from page-level storefront output into a more durable componentized ecommerce frontend surface.

This roadmap keeps the current public product boundary intact:

- stable public mainline: static presentation-style websites
- experimental dynamic lane: minimal storefront exploration
- not yet supported as production behavior:
  - login or account systems
  - real payment capture
  - merchant backend
  - order-management platform
  - database-backed commerce workflows

## Current Reality

The repository already supports a real `ecom_min` page loop:

- home
- category
- search
- shop
- product detail
- cart
- checkout

Current generator-level ecommerce UI tokens:

- `ecom:Header`
- `ecom:Banner`
- `ecom:CategoryNav`
- `ecom:ProductGrid`
- `ecom:ProductDetail`
- `ecom:CartPanel`
- `ecom:CheckoutPanel`
- `ecom:ShopHeader`
- `ecom:SearchResultGrid`

Current limitation:

- the system is still stronger at rendering page-sized ecommerce surfaces
- it is not yet organized as a reusable component library with stable internal composition boundaries

## Component Layers

### A. System Layer

These are required before expanding page modules too far:

1. design tokens
2. shared layout shell
3. shared mock data contracts
4. state feedback primitives

Concrete pieces:

- color, spacing, radius, shadow, typography tokens
- button, input, select, tag, chip, badge, card, section header primitives
- loading, empty, error, skeleton, toast states
- typed mock contracts for:
  - product
  - category
  - cart line
  - checkout summary
  - testimonial
  - review
  - shop
  - order receipt

### B. Global Shared Ecommerce Shell

These should be built once and reused across all storefront pages:

1. top navigation bar
2. announcement bar
3. floating side tools
4. footer
5. global storefront CSS base

### C. Homepage Modules

1. hero banner
2. category shortcuts
3. hot-sale product section
4. new-arrivals section
5. promo strip
6. brand or factory story section
7. testimonial carousel
8. logistics and payment trust strip

### D. Listing and Discovery Modules

1. filter bar
2. sort bar
3. product card grid
4. pagination
5. empty state

### E. Product Detail Modules

1. media gallery
2. product info panel
3. variant selector
4. quantity stepper
5. purchase actions
6. rich detail content
7. specs table
8. related products
9. review list
10. after-sales assurance strip

### F. Transaction Skeleton Modules

These stay static-first for now:

1. cart list
2. order summary
3. address selector skeleton
4. payment method selector skeleton
5. order success page

### G. Auxiliary Static Pages

1. about page
2. contact page
3. privacy and policy pages

### H. Member Center Skeleton

Only static structure for now:

1. profile card
2. order entry navigation
3. address manager shell
4. saved-items shell
5. account-security shell

Important note:

- this section must not be positioned as live auth or user-account support yet

## Gap Mapping Against Current `ecom_min`

### Already Present At Page Level

- header-like shell
- banner-like homepage surface
- category and search routing
- product grid
- product detail purchase surface
- cart page
- checkout page
- shop page

### Missing As Stable Reusable Components

- announcement bar
- floating tools
- footer
- global tokenized storefront theme base
- reusable product card variants
- reusable filter bar
- reusable sort bar
- reusable pagination
- reusable empty state
- reusable gallery module
- reusable variant selector
- reusable quantity stepper
- reusable related-products module
- reusable reviews module
- reusable assurance strip
- reusable address selector shell
- reusable payment selector shell
- reusable order-success module
- reusable about, contact, policy page modules

## Recommended Delivery Order

### Phase 1: Storefront Foundation

Ship first:

1. storefront theme tokens
2. top navigation bar
3. announcement bar
4. footer
5. floating tools
6. reusable product card

Why first:

- these affect every ecommerce page
- they create a visual system instead of one-off page patches
- later homepage, listing, and detail work can reuse them directly

### Phase 2: Homepage Composition

Ship next:

1. hero banner
2. category shortcuts
3. hot-sale section
4. new-arrivals section
5. promo strip
6. brand story section
7. trust strip

Keep optional:

- testimonial carousel can land late in this phase

### Phase 3: Discovery Surfaces

Ship next:

1. filter bar
2. sort bar
3. grid card variants
4. empty state
5. pagination

This phase should unify:

- home product sections
- category page
- search page
- shop page

### Phase 4: Product Detail Depth

Ship next:

1. media gallery
2. info panel
3. variant selector
4. quantity stepper
5. purchase actions
6. specs table
7. related products
8. review list
9. assurance strip

This is likely the highest-value conversion phase.

### Phase 5: Cart And Checkout Skeleton Upgrade

Ship next:

1. cart list module
2. order summary module
3. address selector shell
4. payment selector shell
5. order success page

Keep this phase static-first:

- structure first
- later backend integration can bind into the same shell

### Phase 6: Auxiliary And Account Skeleton Pages

Ship next:

1. about page
2. contact page
3. privacy or policy page
4. member center skeleton

## Suggested AIL Token Evolution

Current generator tokens are too coarse for the target component system.

Recommended next-step token split:

- `ecom:TopNav`
- `ecom:AnnouncementBar`
- `ecom:Footer`
- `ecom:FloatingTools`
- `ecom:HeroBanner`
- `ecom:CategoryShortcut`
- `ecom:ProductSection`
- `ecom:PromoStrip`
- `ecom:BrandStory`
- `ecom:TrustStrip`
- `ecom:FilterBar`
- `ecom:SortBar`
- `ecom:ProductCard`
- `ecom:Pagination`
- `ecom:EmptyState`
- `ecom:MediaGallery`
- `ecom:ProductInfo`
- `ecom:VariantSelector`
- `ecom:QuantityStepper`
- `ecom:PurchaseActions`
- `ecom:SpecsTable`
- `ecom:RelatedProducts`
- `ecom:ReviewList`
- `ecom:AssuranceStrip`
- `ecom:CartList`
- `ecom:OrderSummary`
- `ecom:AddressSelector`
- `ecom:PaymentSelector`
- `ecom:OrderSuccess`

These do not all need to become generator tokens immediately.

Recommended implementation sequence:

1. build Vue component layer first
2. update page generators to compose from those components
3. only then decide which pieces deserve first-class AIL tokens

## Immediate Next Step

Start with `Phase 1: Storefront Foundation`.

Concrete first implementation slice:

1. storefront theme token block
2. top navigation bar
3. announcement bar
4. footer
5. floating side tools
6. reusable product card

This is the best first slice because it upgrades every ecommerce page without pulling the project into login, payment, or backend territory.
