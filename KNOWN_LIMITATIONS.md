# AIL Builder Known Limitations

## Current Positioning

AIL Builder should currently be treated as an **alpha / builder preview**.

It is already useful for testing and contribution.
It is not yet packaged as a polished, general-audience product.

## Main Limitations

### 1. Current Website Generation Scope Is Static And Presentation-Oriented

AIL Builder currently works best for:

- personal portfolio / resume-style pages
- company product pages
- simple landing pages
- static brochure-style websites

It does not currently support:

- ecommerce cart / checkout flows
- order, refund, exchange, or after-sales workflow handling
- login or authentication systems
- dashboards or admin panels
- CMS or publishing-system behavior
- database-backed applications

Requests that cross into app, platform, CMS, ecommerce, or back-office behavior may be rejected by the current website boundary checks.

### 2. Blog Support Is Partial

Blog-like requests may be classified as a blog-style site, but AIL Builder does not currently generate a real blog publishing system.

Current blog support should be understood as:

- blog-like presentation: partial
- CMS, post editor, archive, publishing backend: out of scope

### 3. Generated Sites Are Usually Single-Page Presentation Structures

Requests for pages such as `features`, `pricing`, `about`, or `blog` may be represented as page sections rather than independent routes.

The generated frontend may only include basic routes such as `/` and `/403`.

This is now called out directly in `website check`, so operators can see the routing expectation before over-promising multi-page behavior.

### 4. Onboarding Is Still Too Internal In Places

The repository is much more understandable than before, but some commands, docs, and workflows still assume internal project context.

### 5. Brand Distinction Is Mid-Phase, Not Finished

Current reference:

- `BRAND_DISTINCTION_PHASE_REVIEW_20260417.md`

Current judgment:

- roughly `52%` to `62%` complete

That means the direction is proven, but broader normalization and closeout are still ahead.

### 6. The Strongest Proof Is Still Sample-Led

The repository has strong proof baselines, especially:

- `output_projects/CompanyProductSiteBrandPostureReview`
- `output_projects/PersonalIndependentSiteSignatureReview`

But some of the strongest distinction work still lives in sample-level overrides rather than broader generator-level normalization.

### 7. Public API / Behavior Stability Is Not Guaranteed

CLI surfaces are real and tested, but this repository is still evolving quickly.

You should expect:

- command behavior to continue changing
- docs to tighten over time
- some flows to be renamed or simplified later

### 8. Setup Is More Comfortable For Technical Testers

The current repo is better suited to:

- CLI-friendly builders
- contributors
- technically comfortable testers

than to fully non-technical users.

### 9. Cross-Platform Support Is Improving, Not Finished

The repository is no longer tied to one developer macOS path, and the main CLI flows now resolve the repo root dynamically.

We now also have a confirmed Windows success path for:

- `workspace summary`
- `website check`

That said, Windows and broader cross-platform usage should still be treated as actively improving rather than fully normalized.

The most useful reports here are:

- remaining path assumptions
- shell-specific setup friction
- places where PowerShell or Windows behavior still diverges from the documented Quickstart
- managed-file drift edge cases where users need help choosing whether to preserve or overwrite local generated-file changes

### 10. Local Preview Is Project-Level, Not Yet One-Step From A Prompt

AIL Builder now includes a project-level frontend serve command:

```bash
python3 -m cli project serve --install-if-needed
```

Run it from a generated project directory after `website check` has created output under `output_projects/`.

AIL Builder does not yet provide one command that takes a raw website prompt, generates the project, and serves it automatically.

If needed, users can still run the frontend manually:

```bash
cd output_projects/<generated-project>/frontend
npm install
npm run dev
```

Opening the generated `index.html` directly may show a blank page because the frontend is a Vite SPA.

### 11. Localization And Content Variation Are Still Limited

Some generated or customized pages may contain mixed-language labels, especially in brand-posture or distinction sections.

Generated content can also still feel template-like across different sites. More design and content variation is future work.

### 12. This Is Still An Alpha, Even With A License

The repository now includes a source-available noncommercial license, so the publishing posture is clearer than before.

That does not make the repository OSI open source.

The remaining limitations are still mostly product and onboarding limitations, but users should also understand the current usage boundary:

- learning, research, evaluation, and personal noncommercial use are allowed
- enterprise or commercial use requires separate authorization
- third-party dependencies may carry their own licenses

## What Is Stable Enough To Trust

These are currently strong enough to rely on for testing:

- `testing/results/cli_smoke_results.json`
  - `status = ok`
  - `207 / 207` checks passing
- website-oriented CLI mainline
- static presentation-site generation for portfolio, company/product, and landing-style pages
- durable customization workflow
- proof baselines for company and personal distinction work

## What Feedback Is Most Useful Right Now

The highest-value external feedback is:

- setup friction
- confusing CLI flows
- places where docs still read like internal notes
- whether the proof baselines feel meaningfully distinctive
- whether the customization workflow feels understandable and durable
