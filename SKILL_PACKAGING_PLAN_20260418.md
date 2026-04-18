# AIL Builder Skill Packaging Plan

## Current Recommendation

AIL Builder should now be positioned not only as a CLI-first alpha builder preview, but also as a **skill-ready workflow surface** for agent and IDE environments.

The safest next packaging step is:

- keep the CLI as the system of record
- package the current workflow as a skill-oriented entry surface
- treat MCP exposure as the next layer, not the first one

This is the lowest-risk path for environments such as Codex, OpenCode, Antigravity, Trae, and similar IDE or agent hosts that can load structured instructions, workflow packs, or tool-guidance layers.

## Why Skill-First Is The Right Next Step

AIL Builder's strongest current truth is not just page output.
It is the workflow surface around:

- inspection
- preview
- handoff
- durable customization
- guided next-step execution

That makes it a good fit for skill-style packaging because a skill can teach an agent or IDE:

- which command to run first
- how to inspect current workspace state
- how to stay inside durable customization paths
- when to prefer preview vs. execute
- how to keep users out of managed-file edits

This can be done without rewriting the product surface.

## What Already Exists That Supports A Skill Surface

The current repository already has stable CLI entrypoints that map well to a skill layer.

### 1. Website Evaluation

- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website check ... --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website summary --json`

These support requirement evaluation, deliverability judgment, and website-level overview.

### 2. Workspace Guidance

- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace summary --base-url embedded://local`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --json`

These support repo-root orientation, guided customization entry, and durable continuation.

### 3. Project-Level Durable Customization

- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init <hook_name> --json`

These support guided hook discovery, preview, inspect, handoff, and scaffold execution inside one generated project.

### 4. Proof Baselines

- `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandPostureReview`
- `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteSignatureReview`

These give a skill package something concrete to point at when teaching operators how to inspect sample truth.

## Recommended Skill Positioning

The skill should not be presented as:

- a replacement for the CLI
- a broad autonomous website agent
- a stable cross-IDE contract

It should be presented as:

- a structured operating guide for AIL Builder
- a command-selection and workflow-coordination layer
- a safe way for agents to use existing CLI surfaces consistently

## Recommended Skill Surface

The first skill version should teach these workflows.

### Overview

Use when the user wants to understand the repository or current AIL Builder state.

Primary commands:

- `website summary`
- `workspace summary`

### Discover

Use when the user wants to find the right hook or customization surface.

Primary commands:

- `project hook-guide`
- `workspace hook-guide`
- `project hooks`
- `workspace hooks`

### Preview

Use when the user wants to see what would happen without writing files.

Primary commands:

- `project hook-init ... --dry-run`
- `workspace hook-init ... --dry-run`
- `workspace hook-continue --dry-run`

### Explain

Use when the user wants the reasoning behind one route or target.

Primary commands:

- `project hook-init ... --dry-run --explain`
- `workspace hook-init ... --dry-run --explain`
- `workspace hook-continue --dry-run --explain`

### Handoff

Use when the user wants the next command, target path, or inspect path.

Primary commands:

- `--emit-shell`
- `--copy-command`
- `--emit-target-bundle`
- `--emit-open-shell`

### Execute

Use when the user has already previewed and wants to commit the next step.

Primary commands:

- `project hook-init ... --json`
- `workspace hook-init ... --json`
- `workspace hook-continue --json`
- confirm-gated `--run-command --yes`
- confirm-gated `--run-open-command --yes`

## Recommended First Skill Deliverable

The first external-skill deliverable should be small and explicit:

1. one `SKILL.md`
2. one short "when to use AIL Builder" section
3. one short "safe first commands" section
4. one short "do not edit managed files directly" rule
5. links to:
   - `README.md`
   - `OPEN_SOURCE_STATUS.md`
   - `QUICKSTART_OPEN_SOURCE.md`
   - `KNOWN_LIMITATIONS.md`

## Suggested Skill Messaging

The first public wording should be close to:

> AIL Builder is a CLI-first workflow engine for structured website generation, durable customization, and guided handoff. This skill helps an agent or IDE choose the right AIL Builder commands, inspect current state, and stay inside durable override workflows.

## What The Skill Should Explicitly Teach

The skill should teach these operating rules:

- start with overview before execution when context is unclear
- prefer `--dry-run` before writes
- prefer guided entrypoints over manual path reconstruction
- use hook workflows instead of editing managed files directly
- treat proof baselines as inspectable examples, not fixed promises of all outputs

## Non-Goals For The First Skill Version

Do not try to solve these in version one:

- direct MCP tool exposure
- IDE-specific UI integration
- a stable automation surface across all hosts
- replacement of current README / Quickstart docs
- autonomous end-to-end site generation without operator review

## Recommended Next Step After Skill Packaging

After the skill-oriented package exists and has been tested, the next worthwhile layer is a thin MCP surface that mirrors the current CLI semantics instead of inventing new ones.

The right order is:

1. CLI mainline
2. skill packaging
3. MCP surface
4. host-specific IDE integrations

## Current Judgment

AIL Builder is ready for a **skill-first open-source story** today.

It is not yet ready for:

- a broad "works everywhere as an MCP product" claim
- a stable multi-IDE integration contract

The strongest honest statement today is:

- the repository already has enough workflow structure to be loaded and used as a skill
- MCP packaging should come next, after the skill surface is made explicit
