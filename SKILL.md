---
name: ail-builder
description: Use this skill when working inside the AIL Builder repository or a cloned proof baseline to operate its CLI-first website generation, durable customization, and handoff workflows. Best for choosing the right `website`, `workspace`, `project hook-guide`, `hook-init`, and `hook-continue` commands, inspecting current state before edits, and staying inside managed/unmanaged override boundaries instead of editing managed files directly.
---

# AIL Builder Skill

Use this skill when the task is about operating AIL Builder itself, or when an agent or IDE should use this repository as a structured workflow surface instead of guessing commands.

## Use This Skill For

- understanding the current AIL Builder repository state
- checking whether a website request fits the current supported surface
- navigating repo-root and project-level CLI entrypoints
- starting or continuing durable customization safely
- inspecting proof baselines before changing anything

## Do Not Use This Skill For

- editing managed generated Vue files directly when a hook workflow exists
- claiming a stable MCP or plugin contract
- treating proof baselines as guarantees of all future outputs

## Core Rules

1. Prefer overview before execution when context is unclear.
2. Prefer `--dry-run`, `--text-compact`, or `--explain` before write paths.
3. Prefer `hook-guide`, `hook-init`, and `hook-continue` over manual path reconstruction.
4. Keep changes inside durable overrides whenever possible.
5. Treat the CLI as the source of truth; this skill is a coordination layer, not a replacement.

## Fastest Safe Paths

### 1. Repository Overview

Use when you need a high-level view first.

```bash
PYTHONPATH="$PWD" python3 -m cli workspace summary --base-url embedded://local
```

### 2. Website Requirement Check

Use when you want to know whether one website request fits the current supported surface.

```bash
PYTHONPATH="$PWD" python3 -m cli website check '做一个企业产品官网，包含首页、功能介绍、FAQ、联系我们。' --base-url embedded://local --json
```

### 3. Repo-Root Customization Guidance

Use when you are at repo root and want the safest durable customization entry.

```bash
PYTHONPATH="$PWD" python3 -m cli workspace hook-guide --json
```

### 4. Project-Level Customization Guidance

Use when you are already inside one generated project or proof baseline.

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli project hook-guide --json
```

### 5. Safe Preview Before Writing

Use when you already know a hook and want to preview the next step.

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli project hook-init home.before --dry-run --explain
```

Or from repo root:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli workspace hook-continue --dry-run --text-compact
```

## Working Modes

### Overview

Start here when the user is new, the repo context is unclear, or you need to orient before acting.

- `workspace summary`
- `website summary`

### Discover

Start here when the user wants the right hook or customization surface.

- `project hook-guide`
- `workspace hook-guide`
- `project hooks`
- `workspace hooks`

### Preview

Use before writing files.

- `project hook-init ... --dry-run`
- `workspace hook-init ... --dry-run`
- `workspace hook-continue --dry-run`

### Explain

Use when the user needs the route, target, or next-step reasoning.

- `project hook-init ... --dry-run --explain`
- `workspace hook-init ... --dry-run --explain`
- `workspace hook-continue --dry-run --explain`

### Execute

Use only after preview or when the user is already aligned on the path.

- `project hook-init ... --json`
- `workspace hook-init ... --json`
- `workspace hook-continue --json`

## Recommended Proof Baselines

Use these when you need concrete sample truth:

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandPostureReview`
- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteSignatureReview`

These are good for:

- inspecting durable overrides
- understanding current brand-distinction work
- testing hook-based customization flows

## Read These Docs When Needed

- `/Users/carwynmac/ai-cl/README.md`
- `/Users/carwynmac/ai-cl/OPEN_SOURCE_STATUS.md`
- `/Users/carwynmac/ai-cl/QUICKSTART_OPEN_SOURCE.md`
- `/Users/carwynmac/ai-cl/KNOWN_LIMITATIONS.md`
- `/Users/carwynmac/ai-cl/SKILL_PACKAGING_PLAN_20260418.md`
- `/Users/carwynmac/ai-cl/PROJECT_CONTEXT.md`

## Current Positioning Reminder

AIL Builder is currently best understood as:

- an alpha / builder preview
- a CLI-first workflow engine
- a skill-ready workflow surface

It is not yet best understood as:

- a stable public API
- a stable multi-IDE plugin layer
- a mature MCP product
