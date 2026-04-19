# AIL Builder Known Limitations

## Current Positioning

AIL Builder should currently be treated as an **alpha / builder preview**.

It is already useful for testing and contribution.
It is not yet packaged as a polished, general-audience product.

## Main Limitations

### 1. Onboarding Is Still Too Internal In Places

The repository is much more understandable than before, but some commands, docs, and workflows still assume internal project context.

### 2. Brand Distinction Is Mid-Phase, Not Finished

Current reference:

- `BRAND_DISTINCTION_PHASE_REVIEW_20260417.md`

Current judgment:

- roughly `52%` to `62%` complete

That means the direction is proven, but broader normalization and closeout are still ahead.

### 3. The Strongest Proof Is Still Sample-Led

The repository has strong proof baselines, especially:

- `output_projects/CompanyProductSiteBrandPostureReview`
- `output_projects/PersonalIndependentSiteSignatureReview`

But some of the strongest distinction work still lives in sample-level overrides rather than broader generator-level normalization.

### 4. Public API / Behavior Stability Is Not Guaranteed

CLI surfaces are real and tested, but this repository is still evolving quickly.

You should expect:

- command behavior to continue changing
- docs to tighten over time
- some flows to be renamed or simplified later

### 5. Setup Is More Comfortable For Technical Testers

The current repo is better suited to:

- CLI-friendly builders
- contributors
- technically comfortable testers

than to fully non-technical users.

### 6. Cross-Platform Support Is Improving, Not Finished

The repository is no longer tied to one developer macOS path, and the main CLI flows now resolve the repo root dynamically.

We now also have a confirmed Windows success path for:

- `workspace summary`
- `website check`

That said, Windows and broader cross-platform usage should still be treated as actively improving rather than fully normalized.

The most useful reports here are:

- remaining path assumptions
- shell-specific setup friction
- places where PowerShell or Windows behavior still diverges from the documented Quickstart
- managed-file drift messaging that may still feel too internal on first generation

### 7. This Is Still An Alpha, Even With A License

The repository now includes an MIT license, so the main legal packaging blocker has been removed.

The remaining limitations are product and onboarding limitations, not licensing uncertainty.

## What Is Stable Enough To Trust

These are currently strong enough to rely on for testing:

- `testing/results/cli_smoke_results.json`
  - `status = ok`
  - `207 / 207` checks passing
- website-oriented CLI mainline
- durable customization workflow
- proof baselines for company and personal distinction work

## What Feedback Is Most Useful Right Now

The highest-value external feedback is:

- setup friction
- confusing CLI flows
- places where docs still read like internal notes
- whether the proof baselines feel meaningfully distinctive
- whether the customization workflow feels understandable and durable
