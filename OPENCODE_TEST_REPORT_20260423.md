# Opencode Test Report - 2026-04-23

## Summary

This report captures an external opencode test pass against AIL Builder after the Windows path and frontend-template fixes.

The most accurate current positioning is:

- AIL Builder can generate static presentation-style website projects.
- It is strongest for landing pages, company product pages, and personal portfolio pages.
- It is not currently a full website/app builder for ecommerce, CMS, authentication, dashboards, or database-backed workflows.

In short:

> AIL Builder is currently a fast static presentation-site generator with durable customization workflows, not a universal website or app builder.

## Tested Scenarios

| Scenario | Result | Current Support |
| --- | --- | --- |
| Personal portfolio website | Passed | Supported |
| Company product website | Passed | Supported |
| Blog-style website | Partial | Partial support only; CMS/publishing behavior is out of scope |
| Ecommerce website | Failed by boundary guard | Not supported |

## Confirmed Strengths

- Fast generation: typical runs complete quickly.
- High token efficiency from the current AIL workflow.
- Structured source output through `.ail/source.ail`.
- Local generation path can run without relying on an external AI API in fallback mode.
- Windows main path now works for `workspace summary` and `website check`.
- Fresh clones now include the required frontend template baseline at `output_projects/ail_vue_base`.

## Confirmed Limitations

### Static Presentation Scope

The current website surface is designed around static presentation pages and landing-style sites.

Currently supported:

- personal portfolio / resume-style pages
- company product pages
- simple static company websites
- landing-page-like brochure sites

Currently out of scope:

- ecommerce checkout and cart flows
- authentication / login systems
- dashboards and admin panels
- CMS or publishing-system behavior
- database-backed application workflows

### Blog Support Is Partial

Blog-like requests may be classified into a blog-style website pack, but this does not mean AIL Builder currently implements a CMS, publishing flow, post editor, archive system, or dynamic blog backend.

The current behavior should be described as:

- blog-style presentation support: partial
- real blog/CMS support: out of scope

### Single-Page Routing Bias

Generated websites currently tend to produce a single-page presentation structure plus basic fallback routes such as `/403`.

Requests for separate pages such as `features`, `pricing`, `about`, or `blog` may be represented as sections rather than independent application routes.

This should be made clearer in public docs and CLI messaging.

### Localization And Mixed-Language Output

Some generated or customized pages can contain mixed English and non-English labels.

Examples include English posture labels such as:

- `BRAND POSTURE`
- `PRODUCT SITE / FIT / TRUST`

These labels are currently part of the distinction / posture layer and are not fully localized.

### Managed-File Drift Messaging

First-generation runs can report managed-file drift or local drift warnings.

The current behavior does not necessarily block generation, but the messaging still feels too internal for new users.

This should be clarified or softened in future UX work.

### Local Preview Requires A Frontend Server

Generated frontend projects are SPA-style Vite projects.

Opening `index.html` directly can show a blank page. Users should run the frontend through Vite:

```bash
cd output_projects/<generated-project>/frontend
npm install
npm run dev
```

or:

```bash
npm run build
npm run preview
```

AIL Builder does not yet provide a single CLI command that both generates and serves the website.

## Recommended Next Fixes

1. Add a direct preview / serve workflow.
   - Suggested first command: `project serve`
   - Later command: `website serve`
2. Improve first-run managed-file drift messaging.
3. Make static presentation-page scope clearer in `website check` output.
4. Make blog/CMS boundaries more explicit.
5. Improve localization of posture labels.
6. Clarify single-page versus multi-route behavior.
7. Add more variation to generated content and section structure over time.

## Current Public Positioning

Recommended public wording:

> AIL Builder is an alpha CLI-first builder for static presentation-style websites, durable customization workflows, and agent/IDE handoff surfaces.

Avoid claiming:

- full ecommerce support
- CMS/blog publishing support
- app/dashboard generation
- production-ready full-stack website generation
- one-command local website serving
