# Writing + Context Workflow 2026-04-29

## Goal

Define one practical workflow that combines the `writing` branch and the `context` branch.

This workflow is for situations where:

- the original writing context is already too large for a comfortable prompt
- you want an AI to continue, revise, or critique that work
- you want a reversible path instead of a one-way lossy summary
- you want a post-edit continuity check before treating the new draft as safe

The core idea is simple:

1. compress the long source into an MCP skeleton plus exact restore package
2. hand the skeleton to an AI model
3. capture the edited draft
4. check whether the edited draft still respects the original structure
5. bundle or patch the result for reuse

## Best Fit

This combined workflow is strongest for:

- book planning
- long nonfiction outlines
- multi-section articles
- large copy systems
- story scaffolds that have already outgrown one prompt window

It is less useful for:

- tiny notes
- already-short prompts
- one-paragraph copy asks where the skeleton overhead may outweigh the benefit

## Branch Roles

The two branches play different roles:

### `writing`

Use `writing` when you want:

- pack detection
- scaffold generation
- brief generation
- controlled draft expansion
- writing-specific review

### `context`

Use `context` when you want:

- high-density structural compression
- exact restore
- candidate drift checks against the original structure
- replayable patch and bundle export

The combined pattern works best when `writing` owns the creative scaffold and `context` owns the large-context transport and validation layer.

## Canonical Workflow

### Step 1. Start with the original long source

Example source types:

- `manuscript.md`
- `book-outline.md`
- `campaign-copy.md`

If the source is already too large for a comfortable AI prompt window, do not hand the full raw text to the model first.

### Step 2. Compress the source into a context bundle

Unix shell:

```bash
REPO_ROOT="$PWD"
PYTHONPATH="$REPO_ROOT" python3 -m cli context compress \
  --preset writing \
  --text-file /absolute/path/to/manuscript.md \
  --output-dir /absolute/path/to/context-bundle \
  --json
```

Windows PowerShell:

```powershell
$env:REPO_ROOT = $PWD.Path
$env:PYTHONPATH = $env:REPO_ROOT
py -3 -m cli context compress `
  --preset writing `
  --text-file C:\absolute\path\to\manuscript.md `
  --output-dir C:\absolute\path\to\context-bundle `
  --json
```

Optional tokenizer-backed metrics:

```powershell
py -3 -m pip install tiktoken
py -3 -m cli context compress `
  --preset writing `
  --tokenizer-backend tiktoken `
  --tokenizer-model cl100k_base `
  --text-file C:\absolute\path\to\manuscript.md `
  --output-dir C:\absolute\path\to\context-bundle `
  --json
```

Expected artifacts:

- `context_manifest.json`
- `context_skeleton.mcp`
- `context_restore.json`
- `README.txt`

### Step 3. Inspect the bundle before handing it off

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context inspect \
  --package-file /absolute/path/to/context-bundle/context_manifest.json \
  --emit-summary
```

This is the fast operator check.
You should confirm:

- the `preset_id` is correct
- the source kind is what you expected
- the skeleton is not suspiciously tiny or suspiciously huge
- the metrics look plausible for the sample

### Step 4. Feed only the skeleton to the downstream AI

Use:

- `/absolute/path/to/context-bundle/context_skeleton.mcp`

Keep:

- `/absolute/path/to/context-bundle/context_manifest.json`
- `/absolute/path/to/context-bundle/context_restore.json`

The AI should read the skeleton, not the raw long source.

This is the actual context-reduction move.

### Step 5. Save the edited result as a candidate text file

For example:

- `/absolute/path/to/edited-manuscript.md`

This edited result might come from:

- ChatGPT
- `opencode`
- `minimax`
- `codex`
- another IDE agent

### Step 6. Run context apply-check on the edited draft

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context apply-check \
  --package-file /absolute/path/to/context-bundle/context_manifest.json \
  --text-file /absolute/path/to/edited-manuscript.md \
  --emit-summary
```

What this tells you:

- did the edited draft remain aligned with the original structure?
- did it drift too far from the original topic anchors, section anchors, or density?

Interpretation:

- `status = ok`
  - acceptable structural continuity
- `status = warning`
  - drift is material enough that the draft should not be treated as a clean continuation yet

### Step 7. If you want a writing-specific review, run writing apply-check too

This is the layer where `writing` and `context` become complementary.

Use `context apply-check` when you want:

- structural continuity against the original long source

Use `writing apply-check` when you want:

- drift detection relative to the original writing brief / scaffold intent

Example:

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli writing apply-check \
  '写一个长篇奇幻小说提纲和角色设定，包含主要冲突和章节结构。' \
  --text-file /absolute/path/to/edited-manuscript.md \
  --emit-summary
```

Recommended reading:

- `context apply-check` answers: "did the large source structure survive?"
- `writing apply-check` answers: "did the editorial or narrative intent survive?"

## Recommended Combined Flows

### Flow A. Long manuscript continuation

Use this when the source document is already large.

1. `context compress --preset writing`
2. hand `context_skeleton.mcp` to the AI
3. save the AI continuation
4. `context apply-check`
5. optional `writing review` or `writing apply-check`
6. `context patch` or `context bundle`

### Flow B. Writing scaffold first, compression second

Use this when you start from a structured writing prompt.

1. `writing scaffold`
2. `writing brief`
3. `writing expand`
4. once the draft becomes large, move to:
   - `context compress --preset writing`
5. feed the skeleton to another AI
6. `context apply-check`
7. `context patch` or `context bundle`

This is often the best path for books, long articles, and large content systems.

### Flow C. Full external handoff package

Use this when another person or agent needs everything in one shareable artifact.

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context bundle \
  --preset writing \
  --text-file /absolute/path/to/manuscript.md \
  --candidate-text-file /absolute/path/to/edited-manuscript.md \
  --zip \
  --output-dir /absolute/path/to/context-bundle \
  --json
```

This gives you:

- source bundle
- inspect output
- apply-check output
- optional zip

## Patch Replay Workflow

When you want the edited draft as a replayable change package:

### Export a patch

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context patch \
  --package-file /absolute/path/to/context-bundle/context_manifest.json \
  --text-file /absolute/path/to/edited-manuscript.md \
  --output-dir /absolute/path/to/context-patch \
  --json
```

### Replay the patch safely

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli context patch-apply \
  --patch-file /absolute/path/to/context-patch/patch_manifest.json \
  --output-file /absolute/path/to/replayed-manuscript.md \
  --json
```

This is useful when:

- you want reproducible replay
- you do not want to mutate the original working copy directly
- you want a clean handoff artifact for another operator

## Decision Guide

### Choose `writing` first when:

- you are still figuring out the content shape
- you need a scaffold, brief, or draft pass
- the source is not yet too large

### Choose `context` first when:

- the source is already too large for comfortable prompting
- you need exact restore
- you need one portable bundle across tools or IDEs
- you need a drift check against the original long source

### Choose both when:

- the source is large
- the work is editorially structured
- you want both:
  - content intent continuity
  - source-structure continuity

## What This Workflow Solves

This combined path is meant to reduce:

- prompt-window overflow
- crude truncation
- lossy manual summarization
- follow-up hallucinations caused by missing structural anchors
- brittle cross-tool handoffs

It is not a guarantee that an AI will never hallucinate.
It is a workflow that preserves much more of the useful structure while keeping exact restoration possible.

## Practical Boundary

This workflow is strongest when:

- the original source is large enough to justify compression
- the downstream model is meant to reason over structure, not every original sentence at once

It is weaker when:

- the source is already tiny
- you need literal sentence-by-sentence preservation inside the prompt itself

In those cases, the skeleton may be larger than the source or simply not worth the extra step.

## Recommended Minimal Commands

If you want the shortest useful combined path, start here:

```bash
python3 -m cli context compress --preset writing --text-file /absolute/path/to/manuscript.md --output-dir /absolute/path/to/context-bundle --json
python3 -m cli context inspect --package-file /absolute/path/to/context-bundle/context_manifest.json --emit-summary
python3 -m cli context apply-check --package-file /absolute/path/to/context-bundle/context_manifest.json --text-file /absolute/path/to/edited-manuscript.md --emit-summary
python3 -m cli writing apply-check '写一本非虚构商业书目录和章节目标，帮助创业者搭建销售系统。' --text-file /absolute/path/to/edited-manuscript.md --emit-summary
```

## Final Judgment

Recommended positioning:

- `writing` gives the structured creative lane
- `context` gives the large-context transport and replay lane
- together they form a practical low-token long-form workflow for external AI collaboration
