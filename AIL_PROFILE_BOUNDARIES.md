# AIL Profile Boundaries (Freeze)

Version: v1.0  
Scope: AIL V5 Beta

## 1. Supported Profiles

Only these profiles are supported and frozen:

- `ecom_min`
- `after_sales`
- `landing`

No new profile names are accepted in this freeze window.

## 2. Priority Rules (Deterministic)

1. If `#PROFILE[...]` is explicitly declared in AIL, profile behavior is driven by the declared profile list.
2. If no explicit profile is declared, keyword-based fallback inference remains enabled for backward compatibility.
3. Explicit profile always has higher priority than fallback inference.

## 3. `ecom_min` Boundary

`ecom_min` enables only the current e-commerce frontend baseline:

- Routes/pages set:
  - `/`
  - `/product/:id`
  - `/cart`
  - `/checkout`
  - `/category/:name`
  - `/shop/:id`
  - `/search`
- Existing ecom component family already implemented in engine/templates.
- Existing cart/checkout mock-flow behavior only.

Out of scope in this profile:

- merchant backend
- payment gateway
- recommendation algorithms
- OMS/WMS/ERP integration
- new page families beyond current baseline

## 4. `after_sales` Boundary

`after_sales` is an enhancement pack, not a standalone full-commerce preset.

Enabled scope:

- `/after-sales`
- existing after-sales entry component/flow
- checkout success linkage to after-sales (when available in current templates)

Constraint:

- `after_sales` alone must not auto-expand into a full e-commerce site.

## 5. Compatibility Contract

- Existing generate -> compile -> run behavior remains unchanged.
- Existing keyword fallback behavior remains unchanged when no explicit profile exists.
- Existing outputs are only enhanced by additional observability (`summary.profiles_used`).

## 6. `landing` Boundary

`landing` enables only the current standalone-site frontend baseline:

- Routes/pages set:
  - `/`
  - `/about`
  - `/features`
  - `/pricing`
  - `/contact`
- `landing:*` component family only (Header/Hero/FeatureGrid/Testimonial/Pricing/CTA/Contact/Footer).
- Static/mock frontend interactions only.

Out of scope in this profile:

- cart/order/checkout/ecom flows
- after-sales workflow injection
- auth/admin/backend orchestration

## 7. Observability Contract

`/compile` response summary includes:

```json
"profiles_used": ["ecom_min", "after_sales"]
```

Rules:

- Source: parsed AST profile list.
- Normalization: lowercase.
- Deduplication: first-seen order.
- Missing profile declarations: empty list `[]`.
- `profile_resolution`:
  - `explicit` when at least one `#PROFILE[...]` is present
  - `fallback` when no explicit profile is present

## 8. Change Control

Any change to profile set, boundaries, priority, or `/compile` summary contract is breaking and requires explicit approval plus regression rerun.

## 9. Regression Entry (Frozen)

Use these scripts as the fixed profile regression entry:

- `bash /Users/carwynmac/ai-cl/verify_landing_profile.sh`
- `bash /Users/carwynmac/ai-cl/verify_ecom_profile.sh`
- `bash /Users/carwynmac/ai-cl/verify_after_sales_profile.sh`
- `bash /Users/carwynmac/ai-cl/verify_profiles.sh` (all-in-one)

Pass criteria:

- `landing`:
  - `summary.profiles_used` includes `landing`
  - `summary.profile_resolution` is `explicit`
  - routes: `/`, `/about`, `/features`, `/pricing`, `/contact`
  - no ecom routes injected
- `ecom_min`:
  - `summary.profiles_used` includes `ecom_min`
  - `summary.profile_resolution` is `explicit`
  - routes: `/`, `/product/:id`, `/cart`, `/checkout`, `/category/:name`, `/shop/:id`, `/search`
- `after_sales`:
  - `summary.profiles_used` includes `after_sales`
  - `summary.profile_resolution` is `explicit`
  - route `/after-sales` exists
  - no ecom main routes injected
