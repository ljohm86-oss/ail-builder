# AIL Builder Design Handoff Spec

## Purpose

This document defines a practical collaboration model for:

- `AIL Core` as the architecture-first generator
- an external LLM or design-capable IDE agent as the visual design layer

The goal is not to replace AIL with another freeform generator.

The goal is to let AIL keep ownership of stable structure while letting stronger visual models handle:

- style direction
- typography
- color systems
- section mood
- local layout polish
- brand-specific visual language

## Core Position

AIL Builder should not try to be the system that fully owns:

- architecture
- visual design
- content voice
- illustration direction
- animation detail
- conversion copy

That leads to template explosion and brittle maintenance.

AIL Builder is better positioned as:

- architecture-first website builder
- structured scaffold generator
- durable customization host
- model-ready handoff surface

In this model:

- `AIL Core` generates the site contract
- an external model styles and refines the presentation layer
- AIL validates that the styled result still respects the generated architecture

## System Split

### AIL Core Owns

AIL should remain authoritative for:

- page map
- route structure
- major section ordering
- component topology
- primary interaction flow
- data shape expectations
- generated managed files
- hook locations
- override boundaries
- preview / validation / handoff workflow

### External Model Owns

The external model should own:

- brand direction
- visual hierarchy
- theme tokens
- component skinning
- typography pairing
- color choices
- section-level visual rhythm
- motion suggestions
- surface-level copy polish

### Shared Zone

These are shared, but AIL should define the safe boundary:

- slot-level replacement
- override components
- theme token overrides
- local CSS polish
- decorative assets

## Existing Repo Primitives To Reuse

This direction already fits the repository's current structure.

The most important existing primitives are:

- `python3 -m cli project style-brief --base-url embedded://local --json`
- `python3 -m cli project export-handoff --json`
- `python3 -m cli project hook-guide --json`
- `frontend/src/ail-overrides/theme.tokens.css`
- `frontend/src/ail-overrides/custom.css`
- `frontend/src/ail-overrides/components/`
- `frontend/src/ail-overrides/assets/`
- `frontend/public/ail-overrides/`

These already provide the right split:

- generated structure stays in managed zones
- durable visual customization stays in override zones

Current shortest operator path:

1. run `python3 -m cli project style-brief --base-url embedded://local --json`
2. inspect the override-safe write scope and recommended commands
3. hand that brief to the external model before any design edits begin

## Managed / Unmanaged Rule

This rule should stay strict:

- external models should not be asked to edit `frontend/src/ail-managed/**`
- external models should not be asked to rewrite generated router structure unless explicitly authorized
- design-layer edits should prefer unmanaged override paths first

Recommended external-model write scope:

- `frontend/src/ail-overrides/theme.tokens.css`
- `frontend/src/ail-overrides/custom.css`
- `frontend/src/ail-overrides/components/**`
- `frontend/src/ail-overrides/assets/**`
- `frontend/public/ail-overrides/**`

## Proposed Handoff Contract

AIL should hand an external model a compact design bundle containing:

### 1. Architecture Summary

- project type
- current profile
- route list
- page purpose summary
- section inventory
- continuity surfaces

### 2. Safe Write Scope

- allowed files
- discouraged files
- forbidden managed roots

### 3. Design Targets

- audience
- brand posture
- desired tone
- visual constraints
- localization constraints
- mobile / desktop expectations

### 4. Existing Theme Surface

- current token files
- current override components
- relevant assets

### 5. Validation Checklist

- do routes still work
- do pages still render
- did the model stay outside managed roots
- did the project still preview successfully

## Recommended Handoff Payload Shape

The future machine-readable handoff payload should be shaped roughly like:

```json
{
  "entrypoint": "project-style-brief",
  "project_root": "...",
  "profile": "landing | ecom_min | after_sales",
  "architecture_contract": {
    "routes": [],
    "pages": [],
    "section_inventory": [],
    "continuity_rules": []
  },
  "design_intent": {
    "audience": "",
    "brand_keywords": [],
    "tone_keywords": [],
    "style_direction": "",
    "localization_mode": ""
  },
  "write_contract": {
    "allowed_paths": [],
    "discouraged_paths": [],
    "forbidden_paths": []
  },
  "override_surface": {
    "theme_tokens_path": "",
    "custom_css_path": "",
    "override_components_root": "",
    "override_assets_root": ""
  },
  "validation_contract": {
    "preview_command": "",
    "smoke_expectations": [],
    "managed_boundary_rule": ""
  }
}
```

## Recommended Human Prompt Shape

AIL should eventually be able to generate a human-readable prompt for another model.

The prompt should contain:

1. what the site is for
2. who it is for
3. what not to break
4. which files are safe to edit
5. what level of visual freedom is allowed
6. how to keep changes durable

Example shape:

```text
You are styling an AIL Builder project.

Keep the architecture, routes, and major interaction flows intact.
Do not edit managed files under frontend/src/ail-managed/.

You may edit:
- frontend/src/ail-overrides/theme.tokens.css
- frontend/src/ail-overrides/custom.css
- frontend/src/ail-overrides/components/**
- frontend/src/ail-overrides/assets/**
- frontend/public/ail-overrides/**

Target:
- make the site feel like [brand direction]
- keep it readable on mobile and desktop
- preserve current page purpose and continuity
- do not introduce fake backend or auth claims
```

## Recommended Workflow

The near-term workflow should be:

1. AIL generates the base project
2. operator runs `project export-handoff --json`
3. operator runs `project hook-guide --json`
4. AIL or another wrapper produces a style brief
5. external model edits only override-safe files
6. operator runs `project serve --install-if-needed`
7. AIL verifies preview and boundary safety

Recommended command flow:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli trial-run --scenario ecom_min --base-url embedded://local --project-dir "$PROJECT_DIR" --json
cd "$PROJECT_DIR"
PYTHONPATH="$REPO_ROOT" python3 -m cli project export-handoff --base-url embedded://local --json
PYTHONPATH="$REPO_ROOT" python3 -m cli project hook-guide --json
PYTHONPATH="$REPO_ROOT" python3 -m cli project style-brief --base-url embedded://local --json
PYTHONPATH="$REPO_ROOT" python3 -m cli project style-apply-check --base-url embedded://local --json
PYTHONPATH="$REPO_ROOT" python3 -m cli project serve --install-if-needed
```

## Future CLI Additions

The most useful next commands are likely:

### `project style-brief`

Purpose:

- generate a compact model-facing design brief for the current project

Output should include:

- architecture summary
- saved style intent when available
- design intent placeholders
- allowed write scope
- suggested override targets
- validation instructions

Current implementation notes:

- `project style-brief --json` now includes `model_prompt`
- `project style-brief --emit-prompt` prints a prompt-ready text block for external styling models

### `project style-apply-check`

Purpose:

- verify that a model-styled project did not violate managed boundaries

Checks should include:

- unmanaged-only write verification
- preview still starts
- route file still intact
- generated core files not unexpectedly changed

Current implementation notes:

- verifies managed mirror integrity for runtime view and router copies
- verifies router wiring still points at `frontend/src/ail-managed/**`
- runs a preview dry-run readiness check without starting the dev server
- falls back to local project validation even when no cloud project record exists

### `project style-intent`

Purpose:

- save or refresh operator-specified brand/style intent

Example fields:

- audience
- tone
- style keywords
- localization
- visual constraints

Current implementation notes:

- persists to `.ail/style_intent.json`
- supports read, write, and reset flows
- is automatically included inside `project style-brief`

## Profile-Specific Notes

### Landing

External models should have broad freedom on:

- hero treatment
- typography
- brand presentation
- section transitions

But should not change:

- the underlying page contract
- the generated continuity logic

### `ecom_min`

External models should have freedom on:

- storefront tone
- card styling
- merchandising emphasis
- brand atmosphere
- account-shell polish

But should not claim:

- real payment capture
- real auth product readiness
- real merchant backend

### `after_sales`

External models can improve:

- support clarity
- case-state hierarchy
- escalation surface readability

But should not imply:

- real case-management backends
- live SLA enforcement

## Why This Is Better Than Template Expansion

This model reduces pressure to keep adding more generator-native templates.

Instead of:

- one template per visual style
- one template per brand posture
- one template per industry mood

AIL can maintain:

- one strong architecture line
- one durable override system
- one model-facing design contract

That is easier to scale across:

- Codex
- OpenCode
- MiniMax-backed workflows
- Trae
- Antigravity
- future IDE-hosted design agents

## Immediate Recommendation

Do not start by building a large style engine inside AIL.

Start with:

1. a documented handoff contract
2. a `project style-brief` CLI surface
3. a `project style-apply-check` validation surface

That sequence keeps the architecture stable while making the design layer more powerful.
