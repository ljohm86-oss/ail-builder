# AIL Builder Source-Available Status

## Current Recommendation

AIL Builder is ready to be shared as a **public alpha / builder preview** in a source-available form.

It is not yet ready to be positioned as a stable, polished, broadly self-serve product.

It is also now reasonable to position it as a **skill-ready workflow surface** for agent and IDE environments, as long as that claim stays narrower than a full MCP or plugin product promise.

It should not be described as an OSI-approved open-source release, because the repository license now restricts commercial use.

The repository now also includes a first repository-level skill entry:

- `SKILL.md`

And an initial MCP design reference:

- `MCP_TOOL_SURFACE_SPEC_20260418.md`

## Why It Is Ready For Alpha

The repository already has:

- a committed git baseline
- committed proof baselines for the strongest sample lines
- a healthy main CLI validation snapshot
- a closed customization UX phase for the current scope
- active brand-distinction work with dual-line proof and consolidation

Current validation anchor:

- `testing/results/cli_smoke_results.json`
  - `status = ok`
  - `207 / 207` checks passing

## What External Testers Can Realistically Do

External testers can already:

- run core CLI entrypoints
- inspect website-oriented evaluation flows
- generate static presentation-style site projects
- serve a generated project's frontend locally with `project serve`
- explore durable customization workflows
- inspect proof baselines for company and personal distinction work
- build the bundled proof frontends locally
- load the repository as a structured workflow reference for skill-style agent or IDE usage

The strongest supported generation cases today are:

- personal portfolio / resume-style pages
- company product pages
- simple landing pages

The current website surface should not be presented as ecommerce, CMS, dashboard, authentication, or database-backed app generation.

## What This Release Should Be Called

Recommended wording:

- alpha
- builder preview
- experimental source-available release
- skill-ready workflow surface

Avoid claiming:

- stable release
- production-ready platform
- fully documented public API

## Current Strong Areas

### 1. Website-Oriented CLI Mainline

The repository already supports meaningful website-oriented checks, summaries, previews, and handoff surfaces.

The most reliable generation scope today is static presentation-style websites, not full-stack web applications.

### 2. Durable Customization

The managed / unmanaged customization workflow is no longer just internal infrastructure.
It is now a real CLI product surface.

### 3. Brand Distinction Proof

Current phase review:

- `BRAND_DISTINCTION_PHASE_REVIEW_20260417.md`

Current judgment:

- `Brand Distinction Phase` is roughly `52%` to `62%` complete

That means the repository already has real distinction proof, but not full product-wide normalization.

## What Still Needs To Happen Before A More Mature Release

Before a later beta-like release, the repo will still need:

- a cleaner GitHub-first README experience
- broader product normalization for brand distinction
- clearer public support boundaries
- a more explicit skill package and then MCP packaging pass
- more explicit public contribution expectations

## Current Publishing Advice

If you want to publish soon, the safest framing is:

- publish now as alpha
- invite technical testers and contributors
- invite agent / IDE experimenters to use the repo as a skill-oriented workflow layer
- ask for setup, workflow, and clarity feedback
- avoid promising stability or completeness

## License Note

The repository now includes **PolyForm Noncommercial 1.0.0** plus an additional commercial-use note.

That means:

- personal learning and noncommercial use are allowed
- commercial and enterprise use require separate authorization
- public GitHub publishing is still fine
- the correct legal description is source-available, not OSI open source
