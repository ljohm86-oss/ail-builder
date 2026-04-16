# Project State Review 2026-04-09

## Purpose

This document records the current state of AIL after another focused round of `Customization UX Phase` simplification work.

It exists to answer four practical questions:

- how far the current customization workflow has actually progressed
- what changed during the latest operator-surface normalization pass
- what remains before the phase feels cleanly closed
- what files should now be treated as the current reset point

## Short Answer

The current project state is best read as:

- `website-first` remains complete
- `Customization UX` is now in late-stage closure work, not capability rescue
- the highest-leverage work is now simplification, normalization, and handoff quality

The newest practical truth is:

- the CLI now has enough power
- the remaining challenge is making the shortest safe path easier to read, remember, and trust

## Current Completion Estimate

### Website-First Phase

Current judgment:

- complete

This remains unchanged.

### Customization UX Phase

Current judgment:

- about `82%` to `90%` complete

Why this estimate moved forward from the 2026-04-08 review:

- `hook-guide`, `hook-init`, and `hook-continue` have now gone through another round of text-mode normalization
- the default text views now behave more like operator surfaces and less like state dumps
- explain views now better align with the real fixture semantics used by smoke
- smoke and output semantics were re-aligned after the latest dry-run text/explain changes
- the current full smoke anchor is green again after those adjustments

The clearest new practical truth is:

- the customization workflow is no longer mainly growing sideways
- it is increasingly being compressed into a smaller, clearer operator-facing shape

### Overall Product Maturity

Current judgment:

- about `80%` to `87%` complete

Why this is the right range:

- the website surface is already complete enough to treat as a finished phase
- the customization surface is already broad and real
- the remaining work is now mostly about reducing friction and improving closure quality

## What Changed In The Latest Normalization Pass

This round did not primarily add new raw capability.
It improved the readability and consistency of the current CLI surfaces.

### 1. Hook-Guide Entry Surfaces Became Clearer

The `hook-guide` entrypoints now do a better job separating:

- the human-recommended next command
- the machine-safe runnable next command
- why those two can differ

This makes the guide surface feel more like an operator starting point and less like a command listing.

### 2. Hook-Init Text And Explain Views Were Tightened

The `hook-init` path now has a cleaner distinction between:

- default text output
- compact output
- explain output

The most useful default fields now lean toward:

- target summary
- target reason
- runnable next command
- concise message

And lean away from:

- redundant absolute paths when the relative path already carries the intent
- overly internal-feeling status noise in dry-run views

### 3. Workspace Hook-Continue Default Output Was Compressed Further

The default `workspace hook-continue --dry-run` surface now does a better job of:

- showing the target summary and reason once
- showing the human / runnable / force commands once
- keeping `Next:` for truly additional actions, especially `inspect <target_path>`

This is a small change, but it matters. It reduces the feeling that the CLI is repeating itself while preserving the shortest safe path.

### 4. Smoke Was Re-Aligned With Real Fixture Semantics

During the latest normalization pass, one important mismatch surfaced:

- the smoke fixture for `project hook-init --dry-run --explain` deletes the target hook file before probing
- the correct dry-run message in that case is:
  - `Dry run only. No hook file was written.`
- not:
  - `Target hook file already exists. Re-run with --force to overwrite it.`

That mismatch is now fixed.

The other relevant smoke fix was:

- dry-run text/explain probes that intentionally return non-zero in warning-like situations are now consumed as output probes
- they no longer cause premature smoke aborts under `set -e`

## Current Stable Customization Surface

The following are now strong enough to treat as current product truth.

### Discovery

- `project hooks`
- `workspace hooks`
- `project hook-guide`
- `workspace hook-guide`

### Scaffolding

- `project hook-init`
- `workspace hook-init`

### Continuation

- `workspace hook-continue`

### Common Guided Layers

Across the current hook workflow, the following are now materially established:

- `--dry-run`
- `--text-compact`
- `--explain`
- `--emit-shell`
- `--copy-command`
- `--emit-confirm-shell`
- `--copy-confirm-command`
- target path / dir / project / relative path helpers
- compact target bundles
- `--inspect-target`
- `--open-target`
- `--open-now`
- confirm-gated `--run-command --yes`
- confirm-gated `--run-open-command --yes`

### Validation Status

Current validation anchor:

- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`

Current state:

- `status = ok`

The current important interpretation is:

- the latest simplification pass did not break the main customization workflow
- smoke now reflects the current operator-facing semantics again

## What Still Remains Before This Phase Feels Closed

The remaining work is now narrower and more concrete.

### 1. Final Surface Simplification

What remains:

- continue trimming duplicated intent between default text, compact, and explain views
- keep the shortest safe path visible without printing the same command twice
- decide which fields are truly operator-facing and which are still builder-facing

### 2. Documentation Closure

What remains:

- finish thinning overlapping customization docs
- keep the cheat sheet short and action-first
- keep phase-history docs separate from day-to-day operator docs

### 3. Top-Level Operator Story

What remains:

- make the discover -> preview -> confirm -> inspect -> write story even easier to follow
- keep `hook-guide`, `hook-init`, and `hook-continue` feeling like one family of entrypoints

### 4. Optional Smoke Tail Simplification

What remains:

- the smoke harness is now healthier than before
- but the heavy tail is still expensive
- splitting or lightening the heaviest post-customization branches would still improve iteration speed

## Time Estimate To Close This Phase

If the goal is:

- close the current `Customization UX Phase` cleanly
- without opening a broader new product direction

Then the current estimate is:

- about `2` to `4` focused work days

If the goal expands to:

- make the customization workflow feel clearly polished for handoff or external demo

Then the safer estimate is:

- about `1` focused week

## Practical Recommendation

The current best move is still not to add helper flags indefinitely.

The highest-leverage next step remains:

1. continue operator-surface simplification
2. finish documentation normalization
3. optionally reduce the smoke heavy tail
4. then decide whether to formally close `Customization UX Phase`

## Current Anchor Files

Most useful current references:

- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260408.md`
- `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_OPERATOR_CHEAT_SHEET_20260406.md`
- `/Users/carwynmac/ai-cl/MANAGED_UNMANAGED_PHASE3_HOOK_CATALOG_20260402.md`
- `/Users/carwynmac/ai-cl/PROJECT_CONTEXT.md`
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`
