# Website + Context Workflow 2026-04-29

## Goal

Define one practical workflow that combines:

- website generation
- project styling handoff
- context compression
- patch replay

This workflow is for situations where a generated website or storefront project has already grown large enough that handing the raw source tree to another AI or IDE is inefficient or brittle.

The combined pattern is:

1. generate or select a website project
2. compress the project tree into an AI-facing MCP skeleton
3. hand the skeleton to an external model or IDE
4. validate the edited project against the original structure
5. export a patch or replay the patch safely

## Best Fit

This workflow is strongest for:

- generated static presentation sites
- company/product website baselines
- portfolio sites
- experimental ecommerce storefront baselines
- styling, restructuring, or frontend implementation passes done by external agents

It is especially useful when:

- the project directory is already too large for one prompt
- you want a reversible handoff instead of pasting raw files
- you want to check that edits did not drift away from the original architecture

## Branch Roles

### Website / Project Surface

Use the website and project commands when you want:

- requirement evaluation
- project generation
- project preview
- style handoff
- style safety checks

Core commands:

- `website check`
- `trial-run --scenario ecom_min`
- `project serve`
- `project style-brief`
- `project style-apply-check`

### Context Surface

Use the context commands when you want:

- large project-tree compression
- exact restore
- AI-facing structural skeletons
- patch export
- patch replay
- structural drift checks

Core commands:

- `context compress`
- `context inspect`
- `context apply-check`
- `context patch`
- `context patch-apply`
- `context bundle`
- `context restore`

## Canonical Workflow

### Step 1. Start from a generated or existing website project

You can begin with:

- a static website validation project
- an experimental ecommerce project
- an existing generated baseline in `output_projects`

Static site example:

```bash
REPO_ROOT="$PWD"
PYTHONPATH="$REPO_ROOT" python3 -m cli website check 'Create a company product website with a home page, features, FAQ, and contact page.' --base-url embedded://local --project-dir /absolute/path/to/project --json
```

Experimental ecommerce example:

```bash
REPO_ROOT="$PWD"
PYTHONPATH="$REPO_ROOT" python3 -m cli trial-run --scenario ecom_min --base-url embedded://local --project-dir /absolute/path/to/project --json
```

At this point you already have a real project tree.

### Step 2. Preview the project locally first

Before compressing, verify that the baseline actually runs.

```bash
cd /absolute/path/to/project
PYTHONPATH="$REPO_ROOT" python3 -m cli project serve --dry-run --json
PYTHONPATH="$REPO_ROOT" python3 -m cli project serve --install-if-needed
```

This matters because:

- a broken baseline should not be treated as a stable handoff source
- compression is not a substitute for checking that the generated project still builds and previews

### Step 3. Generate the style handoff brief

If the next AI pass is mostly visual or frontend polish, start with:

```bash
cd /absolute/path/to/project
PYTHONPATH="$REPO_ROOT" python3 -m cli project style-brief --base-url embedded://local --json
```

Or directly emit a prompt:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli project style-brief --base-url embedded://local --emit-prompt
```

This tells the downstream model:

- what the project is
- what not to break
- which paths are safe to edit
- which managed paths should not be edited directly

### Step 4. Compress the project tree into a context bundle

Now create the AI-facing structural bundle.

Static website emphasis:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context compress \
  --preset website \
  --input-dir /absolute/path/to/project \
  --output-dir /absolute/path/to/context-bundle \
  --json
```

Experimental storefront emphasis:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context compress \
  --preset ecommerce \
  --input-dir /absolute/path/to/project \
  --output-dir /absolute/path/to/context-bundle \
  --json
```

Optional tokenizer-backed metrics:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context compress \
  --preset website \
  --tokenizer-backend tiktoken \
  --tokenizer-model cl100k_base \
  --input-dir /absolute/path/to/project \
  --output-dir /absolute/path/to/context-bundle \
  --json
```

This produces:

- `context_manifest.json`
- `context_skeleton.mcp`
- `context_restore.json`
- `README.txt`

### Step 5. Inspect the bundle before handing it off

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context inspect \
  --package-file /absolute/path/to/context-bundle/context_manifest.json \
  --emit-summary
```

Check:

- `preset_id`
- `compression_mode`
- `source_kind`
- `tree_preview`
- `metrics`

For websites, the inspect step is where you confirm the project tree still looks like:

- routes
- pages
- sections
- generated frontend structure

and not like a random truncated subset.

### Step 6. Hand only the skeleton to the external AI

Use:

- `/absolute/path/to/context-bundle/context_skeleton.mcp`

Keep:

- `/absolute/path/to/context-bundle/context_manifest.json`
- `/absolute/path/to/context-bundle/context_restore.json`

The downstream model should reason over:

- page map
- component roles
- route wiring
- frontend structure

without forcing the full raw project tree into its prompt window.

### Step 7. Save the edited project copy

After the external model or IDE makes changes, keep the edited project as a separate candidate directory.

For example:

- original: `/absolute/path/to/project`
- edited: `/absolute/path/to/project-edited`

This separation is important because the context tools work best when the candidate is clearly distinct from the original source bundle.

## Validation Layer

### Step 8. Run context apply-check on the edited project tree

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context apply-check \
  --package-file /absolute/path/to/context-bundle/context_manifest.json \
  --input-dir /absolute/path/to/project-edited \
  --emit-summary
```

This answers:

- did the edited project preserve the main tree structure?
- did page roles or file roles drift too far?
- did the candidate drop too much of the original surface?

Interpretation:

- `status = ok`
  - acceptable structural continuity
- `status = warning`
  - material project drift, review needed before reuse

### Step 9. Run project style-apply-check on the edited project

This is the website-specific safety gate.

From the edited project root:

```bash
cd /absolute/path/to/project-edited
PYTHONPATH="$REPO_ROOT" python3 -m cli project style-apply-check --base-url embedded://local --emit-summary
```

Use it when you want to confirm:

- managed boundary integrity
- route wiring continuity
- preview-readiness

The combined interpretation is:

- `context apply-check` asks whether the larger project structure survived
- `project style-apply-check` asks whether the styling/editing pass stayed inside the operational website boundary

## Recommended Combined Flows

### Flow A. Static website restyling

1. `website check` or use an existing proof baseline
2. `project serve`
3. `project style-brief`
4. `context compress --preset website`
5. external AI edits a project copy
6. `context apply-check`
7. `project style-apply-check`
8. `context patch` or `context bundle`

### Flow B. Experimental ecommerce storefront refinement

1. `trial-run --scenario ecom_min`
2. `project serve`
3. `project style-brief`
4. `context compress --preset ecommerce`
5. external AI edits a storefront copy
6. `context apply-check`
7. `project style-apply-check`
8. `context patch`
9. optional `context patch-apply`

This is especially useful because ecommerce skeletons involve:

- browse
- search
- product
- cart
- checkout
- account shell

and those surfaces are easy to distort if an external model edits them blindly.

### Flow C. Full shareable context handoff package

If you want one shareable project package:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context bundle \
  --preset website \
  --input-dir /absolute/path/to/project \
  --candidate-input-dir /absolute/path/to/project-edited \
  --zip \
  --output-dir /absolute/path/to/context-bundle \
  --json
```

This gives:

- compression bundle
- inspect output
- apply-check output
- optional zip

## Patch Replay Workflow

When you want a replayable diff package instead of a full edited tree:

### Export the patch

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context patch \
  --package-file /absolute/path/to/context-bundle/context_manifest.json \
  --input-dir /absolute/path/to/project-edited \
  --zip \
  --output-dir /absolute/path/to/context-patch \
  --json
```

### Replay into a safe target

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context patch-apply \
  --patch-file /absolute/path/to/context-patch/patch_manifest.json \
  --source-package-file /absolute/path/to/context-bundle/context_manifest.json \
  --output-dir /absolute/path/to/replayed-project \
  --json
```

This is useful when:

- you want a replayable external edit
- you want to avoid mutating the original generated tree in place
- you want a clean review target

## Decision Guide

### Choose `project style-brief` first when:

- the next AI pass is mainly visual
- you need managed/unmanaged file boundaries
- you want a prompt-ready design handoff

### Choose `context compress` first when:

- the project tree is too large for comfortable prompting
- you need exact restore
- you want a reusable bundle or patch package

### Choose both when:

- the project is large
- the next AI pass is not trivial
- you need both:
  - website-safe editing boundaries
  - large-context structural transport

## What This Workflow Solves

This combined path is designed to reduce:

- oversized frontend prompt dumps
- route or page drift during external AI edits
- brittle style-only workflows that ignore project structure
- hard-to-review large diffs
- lossy handoffs between IDEs and AI tools

It is not a guarantee that an AI will never break a site.
It is a workflow that makes structural drift easier to detect and edited outputs easier to replay safely.

## Practical Boundary

This workflow is strongest when:

- the project has enough files that raw prompting is becoming expensive
- the editing task is structural, visual, or page-level
- you want a controlled replay step

It is weaker when:

- the project is tiny
- the task is just one trivial CSS tweak
- the model already has enough room to read the actual files directly

## Recommended Minimal Commands

If you want the shortest useful combined path, start here:

```bash
python3 -m cli project style-brief --base-url embedded://local --emit-prompt
python3 -m cli context compress --preset website --input-dir /absolute/path/to/project --output-dir /absolute/path/to/context-bundle --json
python3 -m cli context inspect --package-file /absolute/path/to/context-bundle/context_manifest.json --emit-summary
python3 -m cli context apply-check --package-file /absolute/path/to/context-bundle/context_manifest.json --input-dir /absolute/path/to/project-edited --emit-summary
python3 -m cli project style-apply-check --base-url embedded://local --emit-summary
```

## Final Judgment

Recommended positioning:

- `website/project` commands define what may change safely
- `context` commands carry and validate the large project structure
- together they form a practical low-token website collaboration workflow for external AI and IDE agents
