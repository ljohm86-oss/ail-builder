# Project State Review 2026-04-06

## Purpose

This document is the current short reality check for AIL after the ongoing Customization UX Phase improvements that followed the 2026-04-03 website-first closeout and managed / unmanaged milestone.

It exists to answer:

- where overall project completion stands now
- how far the current Customization UX Phase has progressed
- what the current ecommerce storefront baseline implies about generation workload size
- how the current AIL ecommerce workflow likely compares with direct-code generation in token and cost terms

## Short Answer

The project still has one clearly completed phase and one clearly active phase.

The cleanest current interpretation is:

- the website-first phase is already complete
- the Customization UX Phase is now materially beyond early viability and into workflow refinement
- the next remaining leverage is less about rescuing capability and more about reducing user friction

The most important new practical truth since the 2026-04-03 review is:

- repo-root durable-hook continuation is now much more ergonomic
- the CLI can not only discover, suggest, scaffold, inspect, and continue hooks
- it can now also preview, open, copy, and confirm the next step in more guided ways

## Current Supported Frontier

Formal supported profiles:

- `landing`
- `ecom_min`
- `after_sales`

Experimental only:

- `app_min`

Safest product truth:

- websites are supported
- apps are still not part of the formal delivery promise

## Stable Website Baselines

### 1. Personal Independent Site

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteSignatureReview`

Current judgment:

- strongest authored-polish and signature line

### 2. Company / Product Website

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandPostureReview`

Current judgment:

- strongest mainstream homepage and brand-posture line

### 3. Ecommerce Independent Storefront

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/EcomDiscoveryShopBoardReview`

Current judgment:

- strongest structural and runtime continuity line

Key reality:

- this is still the clearest proof that AIL can support a believable multi-page storefront frontstage
- discovery now reads more clearly across:
  - home
  - search/category
  - shop
  - direct product entry
- purchase continuity still remains strongest across:
  - product
  - cart
  - checkout
  - completion / continue browsing

### 4. After-Sales Service Website

Current baseline:

- `/Users/carwynmac/ai-cl/output_projects/AfterSalesFooterClosureReview`

Current judgment:

- strongest bounded tracked-case / operational-surface line

## Current Product Truth

The clearest current product truth is now:

- Personal remains the strongest authored-polish proof.
- Company/Product remains the strongest mainstream homepage proof.
- Ecommerce remains the strongest interaction and continuity proof.
- After-sales remains the strongest bounded operational-surface proof.
- Managed / unmanaged + hooks remain the strongest proof that AIL can support durable post-generation customization without pretending to solve full round-trip editing.

## Completion Estimate

### Website-First Phase

Current judgment:

- complete

This should no longer be described as "almost complete."

The supported website mainline already has:

- four strong baselines
- broad runtime proof
- stable high-level milestone and closeout docs

### Customization UX Phase

Current judgment:

- about `60%` to `70%` complete

Why this is the right range:

- the boundary itself is already landed
- hook discovery is already landed
- hook scaffolding is already landed
- repo-root continuation is already landed
- confirm/copy/open/run ergonomics are now materially stronger

What is now already true:

- `project hooks`
- `workspace hooks`
- `project hook-init`
- `workspace hook-init`
- `workspace hook-continue`
- repo-root `--dry-run`, `--text-compact`, `--explain`
- `--inspect-target`, `--open-target`, `--open-now`
- `--emit-shell`, `--emit-open-shell`
- `--copy-command`, `--copy-open-command`, `--copy-confirm-command`
- `--run-command --yes`
- `--run-open-command --yes`

What still remains before this phase feels closed:

- stronger misuse guidance and operator-facing explanation layers
- more explicit documentation normalization around the new repo-root customization surfaces
- potentially a cleaner grouping of "continue / inspect / open / run" paths so first-time users need less command discovery

### Overall Product Maturity

Current judgment:

- about `70%` to `78%` complete

Why:

- the strongest website product surface is already real
- durable customization is now real product value, not an internal mechanism
- but the next higher-order phase choices are still open:
  - stronger brand distinction
  - deeper customization UX
  - broader platform scope

## Ecommerce Workload Size Reality

The current ecommerce baseline provides a practical size anchor for estimating model workload.

Measured on:

- `/Users/carwynmac/ai-cl/output_projects/EcomDiscoveryShopBoardReview`

Local measured size:

- managed ecommerce view files (`frontend/src/ail-managed/views/*.vue`)
  - about `306,452` chars
  - about `76,613` tokens using a simple `chars / 4` approximation
- broader frontend source under `frontend/src` (`.vue/.js/.ts/.css`)
  - about `639,996` chars
  - about `159,999` tokens using the same approximation

What this means:

- direct multi-page code generation is expensive mainly because the output surface is large
- AIL’s structural advantage is that the model does not need to emit all of that front-end code directly
- the compiler absorbs most of the code expansion

## Ecommerce Token / Cost Estimate

### Important Assumption

These are practical planning estimates, not exact billing records.

They are based on:

- the observed size of the current ecommerce storefront baseline
- the fact that AIL uses a structured-source-to-compiled-code workflow
- the fact that direct-code generation must emit much more literal front-end output

### Estimated Token Shape

#### AIL Workflow

Meaning:

- model produces requirement interpretation plus structured AIL/source-like output
- compiler expands that structure into the final multi-page storefront code

Working estimate:

- input: about `70k` tokens
- output: about `25k` tokens
- total: about `95k` tokens

#### Direct-Code Workflow

Meaning:

- model directly emits the multi-page storefront front-end code
- revisions and continuity fixes happen at the code level

Working estimate:

- input: about `140k` tokens
- output: about `90k` tokens
- total: about `230k` tokens

### Comparative Interpretation

The practical takeaway is:

- AIL is likely to reduce total model-token consumption by roughly `2x` to `3x` for a storefront at the current `EcomDiscoveryShopBoardReview` level

That reduction mostly comes from:

- less direct code emission
- less repeated re-output of full page code
- a tighter structural source of truth

It does **not** mainly come from one vendor being unusually cheap.

## Official Pricing Anchors

Pricing references used for the rough cost comparison:

- OpenAI API pricing:
  - [OpenAI API Pricing](https://openai.com/api/pricing/)
- Anthropic API pricing:
  - [Claude API Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Google Gemini API pricing:
  - [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)

Current official anchor points observed on 2026-04-06:

- OpenAI `GPT-5.4`
  - input: `$2.50 / 1M`
  - output: `$15.00 / 1M`
- Anthropic `Claude Sonnet 4.5`
  - input: `$3 / 1M`
  - output: `$15 / 1M`
- Google `Gemini 2.5 Pro`
  - input: `$1.25 / 1M` for prompts `<= 200k`
  - output: `$10.00 / 1M` for prompts `<= 200k`

## Rough Cost Comparison

### AIL Workflow Estimate

Assumed workload:

- `70k` input
- `25k` output

Estimated cost:

- `GPT-5.4`
  - about `$0.55`
- `Claude Sonnet 4.5`
  - about `$0.59`
- `Gemini 2.5 Pro`
  - about `$0.34`

### Direct-Code Workflow Estimate

Assumed workload:

- `140k` input
- `90k` output

Estimated cost:

- `GPT-5.4`
  - about `$1.70`
- `Claude Sonnet 4.5`
  - about `$1.77`
- `Gemini 2.5 Pro`
  - about `$1.08`

## Best Current Interpretation

As of 2026-04-06:

- the website-first phase should be treated as complete
- the Customization UX Phase is already strong enough to be a serious productization effort, not a speculative branch
- the current ecommerce storefront baseline is large enough that direct code generation remains meaningfully more expensive than the AIL compile workflow
- AIL’s practical token advantage for current storefront-grade work is likely in the `2x` to `3x` range

## One-Line Conclusion

As of 2026-04-06, AIL looks like a project with a completed website-first phase, a materially advancing Customization UX Phase, and a real cost-structure advantage for storefront generation because the model is generating compact structured intent instead of re-emitting the full front-end codebase every time.
