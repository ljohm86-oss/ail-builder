# Cross Workflow Map 2026-04-29

## Goal

Provide one high-level map for the four main AIL Builder workflow surfaces:

- `website`
- `writing`
- `style`
- `context`

This document is intentionally higher-level than the detailed workflow specs.
It is meant to answer:

- which workflow should we start with?
- when should we combine them?
- which command family owns which problem?

## The Four Workflow Lines

### 1. `website`

Primary job:

- generate, classify, preview, and validate website-shaped projects

Use `website` when the task begins with:

- a site requirement
- a landing page ask
- a portfolio or company-site ask
- an experimental storefront ask

Core commands:

- `website check`
- `trial-run --scenario ecom_min`
- `project serve`

Owns:

- project generation
- generation boundary decisions
- previewable site baselines

### 2. `style`

Primary job:

- hand the generated site to an external design model safely

Use `style` when the project already exists and the next step is:

- visual refinement
- token-safe design handoff
- route-safe CSS / component overrides

Core commands:

- `project style-intent`
- `project style-brief`
- `project style-apply-check`

Owns:

- design intent capture
- model-ready styling brief
- override-safe boundary validation

### 3. `writing`

Primary job:

- provide scaffold-first low-token content creation workflows

Use `writing` when the task begins with:

- copy asks
- story planning
- book planning
- structured long-form writing

Core commands:

- `writing check`
- `writing scaffold`
- `writing brief`
- `writing expand`
- `writing review`
- `writing apply-check`
- `writing bundle`

Owns:

- content-lane classification
- scaffold generation
- draft expansion
- writing-specific drift checks

### 4. `context`

Primary job:

- carry oversized code or text context through AI workflows without raw prompt dumping

Use `context` when:

- the source tree is too large
- the long document is too large
- exact restore matters
- replayable patch or bundle artifacts matter

Core commands:

- `context preset`
- `context compress`
- `context inspect`
- `context apply-check`
- `context patch`
- `context patch-apply`
- `context bundle`
- `context restore`

Owns:

- structural compression
- exact restore
- replayable patch export
- bundle packaging
- large-context drift checking

## One-Line Positioning

If you only remember one sentence per line:

- `website` creates the project
- `style` safely restyles the project
- `writing` shapes the content
- `context` carries oversized structure across AI hops

## Starting-Point Decision Map

### Start with `website` when:

- you do not yet have a project
- the user is asking for a site or storefront
- you need a real generated baseline first

### Start with `style` when:

- you already have a generated project
- the next task is visual, not architectural
- you need to involve an external design model safely

### Start with `writing` when:

- the task begins as copy, story, or book work
- the primary problem is content shape, not frontend implementation

### Start with `context` when:

- the source is already too large for comfortable prompting
- exact restore matters
- you need a replayable artifact instead of raw pasted context

## Combination Map

These are the combinations that make the most sense today.

### `website + style`

Use when:

- a generated site needs visual refinement

Shortest path:

1. generate or open the website project
2. run `project style-brief`
3. let an external model edit override-safe files
4. run `project style-apply-check`
5. preview with `project serve`

### `website + context`

Use when:

- a generated project is too large to hand directly to another model
- you still want architectural continuity checks

Shortest path:

1. generate or open the project
2. run `context compress --preset website`
3. hand off `context_skeleton.mcp`
4. run `context apply-check`
5. optionally export `context patch` or `context bundle`

Reference:

- `/Users/carwynmac/ai-cl/WEBSITE_CONTEXT_WORKFLOW_20260429.md`

### `writing + context`

Use when:

- the writing source is already too large for one prompt
- you still want low-token continuity and exact restore

Shortest path:

1. run `context compress --preset writing`
2. hand off `context_skeleton.mcp`
3. run `context apply-check`
4. optionally run `writing apply-check`
5. export `context patch` or `context bundle`

Reference:

- `/Users/carwynmac/ai-cl/WRITING_CONTEXT_WORKFLOW_20260429.md`

### `website + style + context`

Use when:

- a generated website is large
- the next pass is both structural and visual
- an external AI or IDE needs a safe, compressed handoff

Shortest path:

1. generate or open the project
2. run `project style-brief`
3. run `context compress --preset website`
4. hand off:
   - `style-brief`
   - `context_skeleton.mcp`
5. apply edits on a copied project tree
6. run:
   - `context apply-check`
   - `project style-apply-check`
7. export:
   - `context patch`
   - or `context bundle`

### `writing + context + website`

Use when:

- content and site structure are both evolving
- a large writing source needs to flow into a website project safely

Typical pattern:

1. build or refine the content with `writing`
2. compress the content with `context`
3. feed the content skeleton into the site implementation pass
4. validate the edited result with:
   - `writing apply-check`
   - `context apply-check`
   - website/project checks where relevant

## Ownership Map

This is the cleanest way to think about responsibility.

### `website` owns:

- site generation
- site boundary classification
- baseline previewability

### `style` owns:

- design intent
- safe visual handoff
- managed/unmanaged edit boundaries

### `writing` owns:

- content-lane structure
- creative scaffolds
- editorial drift checks

### `context` owns:

- large-context transport
- exact restore
- replayable patch and bundle artifacts
- structure-level drift checks

## Common Operator Questions

### "I have a project, and I want another AI to restyle it safely. What do I use?"

Use:

- `project style-brief`
- optionally `context compress --preset website`
- then `project style-apply-check`

### "I have a giant book outline, and I want another AI to continue it without dumping the whole file."

Use:

- `context compress --preset writing`
- optionally `writing apply-check` after the edit

### "I want a replayable artifact instead of just a pasted answer."

Use:

- `context patch`
- `context patch-apply`
- or `context bundle`

### "I only need a scaffold, not compression."

Use:

- `writing scaffold`
- `writing brief`

### "I only need a generated site baseline, not a cross-AI handoff."

Use:

- `website check`
- or `trial-run --scenario ecom_min`
- then `project serve`

## What Not To Overlap

These boundaries help keep the system understandable.

- do not use `context` as a replacement for `website` generation
- do not use `writing` as a replacement for `context` restore or replay
- do not use `style` as a replacement for project-tree validation
- do not use `website` as a replacement for long-form editorial checking

Each line is stronger when it keeps its own role.

## Suggested First Commands By Task

### Static website generation

```bash
python3 -m cli website check 'Create a company product website with a home page, features, FAQ, and contact page.' --base-url embedded://local --json
```

### Experimental storefront generation

```bash
python3 -m cli trial-run --scenario ecom_min --base-url embedded://local --json
```

### Safe design handoff

```bash
python3 -m cli project style-brief --base-url embedded://local --emit-prompt
```

### Writing scaffold

```bash
python3 -m cli writing scaffold '写一本非虚构商业书目录和章节目标，帮助创业者搭建销售系统。' --json
```

### Large-context writing compression

```bash
python3 -m cli context compress --preset writing --text-file /absolute/path/to/manuscript.md --output-dir /absolute/path/to/context-bundle --json
```

### Large-context website compression

```bash
python3 -m cli context compress --preset website --input-dir /absolute/path/to/project --output-dir /absolute/path/to/context-bundle --json
```

## Recommended Reading Order

For the broadest orientation:

1. `/Users/carwynmac/ai-cl/README.md`
2. `/Users/carwynmac/ai-cl/DESIGN_HANDOFF_SPEC_20260426.md`
3. `/Users/carwynmac/ai-cl/WRITING_CONTEXT_WORKFLOW_20260429.md`
4. `/Users/carwynmac/ai-cl/WEBSITE_CONTEXT_WORKFLOW_20260429.md`
5. `/Users/carwynmac/ai-cl/CONTEXT_COMPRESSION_SPEC_20260428.md`

## Final Judgment

The current mainline is best understood as a layered system:

- `website` creates structure
- `style` manages safe visual collaboration
- `writing` manages scaffold-first content collaboration
- `context` makes large-context collaboration portable, checkable, and replayable

That is the cleanest map of the project today.
