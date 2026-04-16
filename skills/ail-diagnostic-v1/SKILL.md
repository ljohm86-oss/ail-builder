---
name: ail-diagnostic-v1
description: Use when the user provides a Requirement section and an AIL Program section and wants diagnosis only. This skill validates whether the AIL complies with current system boundaries for landing, ecom_min, after_sales, and experimental app_min, and returns a fixed diagnostic report without generating or rewriting AIL.
---

# AIL Diagnostic Skill v1

Act as an AIL validator and diagnostic engine.

Do not generate AIL.
Do not rewrite the program unless the user explicitly asks.
Only diagnose.

## Input

Expect two sections from the user:

- `Requirement`
- `AIL Program`

Analyze whether the AIL is valid for the current system.

## Supported Profiles

### `landing`

`#PROFILE[landing]`

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

`#PROFILE[ecom_min]`

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

`#PROFILE[after_sales]`

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

### `app_min` (experimental)

`#PROFILE[app_min]`

Allowed UI blocks:

- `app:TopBar`
- `app:BottomTab`
- `app:List`
- `app:Card`
- `app:ChatWindow`
- `app:Composer`
- `app:SearchBar`

Important constraints:

- `app_min` is experimental
- no login or auth flows
- no complex backend APIs
- usually a single-page mobile-style prototype

## Validation Rules

A valid AIL program must satisfy:

1. Only one `#PROFILE`
2. Only supported UI tokens
3. Only supported flows
4. No HTML, React, or Vue code
5. Reasonable structure order

Known alias / drift forms should be treated as repairable normalization candidates, not as novel token proposals.

Canonical source:

- `/Users/carwynmac/ai-cl/language/alias_drift_whitelist_v1.json`

Normalize conceptually to the formal names below:

- `landing:Testimonials` -> `landing:Testimonial`
- `ecom:Search` -> `ecom:SearchResultGrid`
- `SUBMIT_CONTACT` -> `CONTACT_SUBMIT`
- `ADD_CART` -> `ADD_TO_CART`
- `SUPPORT_ESCALATE` -> `COMPLAINT_DEESCALATE`

Expected order:

1. `#PROFILE`
2. optional DB tables
3. API definitions
4. `@PAGE` definitions
5. `#UI` blocks
6. `#FLOW` blocks

## Error Types

Classify problems into:

- `multiple_profile`
- `unknown_component`
- `unknown_flow`
- `structure_invalid`
- `profile_mismatch`
- `boundary_exceeded`

## Root Cause Classification

For each result classify root cause as:

- `model_output_issue`
- `dictionary_gap`
- `compiler_gap`
- `unsupported_by_current_system`

## Diagnostic Procedure

1. Detect all `#PROFILE[...]` declarations.
2. Determine whether profile count is zero, one, or multiple.
3. Extract all `#UI[source:Token]` usages.
4. Extract all `#FLOW[NAME]` usages.
5. Check whether all tokens belong to the detected profile.
6. Check whether the program exceeds the profile boundary.
7. Check structure order.
8. Check for unsupported constructs such as raw HTML, React JSX, Vue SFC markup, or direct component framework code.
9. Decide whether compile is recommended.

## Compile Recommendation Rule

Set `compile_recommended: yes` only if:

- profile is singular and supported
- no unknown components
- no unknown flows
- no boundary exceeded issue
- no fatal structure issue

Otherwise set `compile_recommended: no`.

If a program only fails because of alias / drift naming, diagnose it as not ready to compile directly, but treat it as a high-confidence repairable candidate that should resolve to the formal token or flow.

## Confidence Rule

- `high`: profile is clear and all violations are explicit
- `medium`: profile is clear but some constructs are ambiguous
- `low`: profile is missing, mixed, or the input is incomplete

## Required Output

Always output exactly this structure:

```text
Diagnosis Summary
- valid: yes | no
- compile_recommended: yes | no
- confidence: high | medium | low

Profile Check
- detected_profile: ...
- profile_match: yes | no
- multiple_profiles: yes | no

Structure Check
- structure_valid: yes | no
- notes: ...

Token Check
- unknown_components: [...]
- unknown_flows: [...]
- unsupported_constructs: [...]

Boundary Check
- boundary_exceeded: yes | no
- boundary_reason: ...

Issue Classification
- model_output_issue: yes | no
- dictionary_gap: yes | no
- compiler_gap: yes | no
- unsupported_by_current_system: yes | no

Short Conclusion
- ...
```

## Final Rule

Always produce the diagnostic report in the exact structure above.
