# Profile Verify Entry

This document defines the minimal regression entry for frozen profiles.

## Entry Scripts

- `bash /Users/carwynmac/ai-cl/verify_landing_profile.sh`
- `bash /Users/carwynmac/ai-cl/verify_ecom_profile.sh`
- `bash /Users/carwynmac/ai-cl/verify_after_sales_profile.sh`
- `bash /Users/carwynmac/ai-cl/verify_profiles.sh` (run all three)
- `bash /Users/carwynmac/ai-cl/verify_app_profile.sh` (technical probe, not part of frozen profile gate)
- `bash /Users/carwynmac/ai-cl/verify_app_profile_smoke.sh` (technical probe interaction smoke, not part of frozen profile gate)

## Pass Criteria

### landing
- `/compile` status is `ok`
- `summary.profiles_used` includes `landing`
- `summary.profile_resolution` is `explicit`
- generated routes include: `/`, `/about`, `/features`, `/pricing`, `/contact`
- generated routes exclude: `/product/:id`, `/cart`, `/checkout`, `/shop/:id`, `/search`, `/after-sales`
- runtime route check (if enabled) returns 200 for landing routes

### ecom_min
- `/compile` status is `ok`
- `summary.profiles_used` includes `ecom_min`
- `summary.profile_resolution` is `explicit`
- generated routes include:
  - `/`
  - `/product/:id`
  - `/cart`
  - `/checkout`
  - `/category/:name`
  - `/shop/:id`
  - `/search`
- pure `ecom_min` run should not auto-include `/after-sales`

### after_sales
- `/compile` status is `ok`
- `summary.profiles_used` includes `after_sales`
- `summary.profile_resolution` is `explicit`
- generated routes include `/after-sales`
- generated routes exclude ecom main routes (`/product/:id`, `/cart`, `/checkout`, `/shop/:id`, `/search`)

### app_min (probe)
- `/compile` status is `ok`
- `summary.profiles_used` includes `app_min`
- `summary.profile_resolution` is `explicit`
- generated routes include only `/` (plus internal `/403` if engine injects it)
- generated Home view contains `TopBar`, `BottomTab`, `ChatWindow`
- runtime root route `/` returns 200

### app_min interaction smoke (probe)
- `verify_app_profile.sh` passes first
- browser smoke confirms:
  - `app-topbar` visible
  - `app-bottom-tab` visible
  - default `panel-chats` visible
  - tabs switch to `panel-contacts`, `panel-discover`, `panel-me`
  - `chat-window` opens from a chat item and closes again
