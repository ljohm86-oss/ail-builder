# Alias / Drift Whitelist

This document defines the current single source of truth for normalized AIL alias and drift forms.

Source file:

- `/Users/carwynmac/ai-cl/language/alias_drift_whitelist_v1.json`

## Component Aliases

- `landing:Testimonials` -> `landing:Testimonial`
- `ecom:Search` -> `ecom:SearchResultGrid`

## Flow Aliases

- `SUBMIT_CONTACT` -> `CONTACT_SUBMIT`
- `ADD_CART` -> `ADD_TO_CART`
- `SUPPORT_ESCALATE` -> `COMPLAINT_DEESCALATE`

## Intent

- Keep alias and drift rules out of scattered local constants.
- Ensure testing runners normalize the same way.
- Ensure dictionary evolution does not report these as new token gaps.
