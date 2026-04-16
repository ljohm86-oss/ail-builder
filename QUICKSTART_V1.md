# Quickstart v1

## Purpose

This guide is the shortest supported path to experience AIL v1.

Use this if you want to go from:

- requirement

to:

- `.ail/source.ail`
- cloud compile result
- synced local generated project

without reading the full protocol and implementation docs first.

## What v1 Supports

The recommended v1 experience is built around the frozen profiles:

- `landing`
- `ecom_min`
- `after_sales`

`app_min` exists, but it is still experimental and is not part of the formal release baseline.

## Before You Start

You should have:

- Python 3 available
- this repository checked out at:
  - `/Users/carwynmac/ai-cl`
- a working local AIL mothership compile path

If you are working inside this repo, the safest validation command is:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
```

If this passes, the CLI path is healthy enough for the quickstart flow.

## Fastest Entry

If you want the shortest supported frozen-profile path, use:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --requirement "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。" --base-url embedded://local
```

Or use one of the built-in frozen-profile scenarios:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario landing --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario ecom_min --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario after_sales --base-url embedded://local
```

Thin wrapper also exists:

```bash
bash /Users/carwynmac/ai-cl/demo_v1.sh --scenario landing
```

`python3 -m cli trial-run` is now the preferred frozen-profile first-user entry. The shell wrapper delegates to the same path.

The command wraps the canonical CLI flow:

```text
init
  -> generate
  -> diagnose
  -> repair if needed
  -> compile --cloud
  -> sync
```

It prints:

- the created project path
- the detected profile
- whether repair was needed
- where the generated managed files were written

If you use `--json`, it now also includes:

- `cloud_status`
- `preview_handoff`
- `preview_hint`
- `open_targets`

This means a single `trial-run --json` result now tells you:

- what was built
- which cloud queries succeeded
- what the primary preview target is
- which directory to inspect first
- which files and folders are the most useful next open targets

The same preview handoff shape is now also exposed by:

- `python3 -m cli cloud status --json`
- `python3 -m cli build artifact <build_id> --json`
- `python3 -m cli project summary --json`
- `python3 -m cli project preview --json`

If you are already inside an initialized AIL project and want a project-oriented overview, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project summary --base-url embedded://local --json
```

If you specifically want the shortest project-level preview handoff, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project preview --base-url embedded://local --json
```

If you already have the preview handoff and want the CLI to resolve one concrete target for inspection, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project open-target --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project open-target source_of_truth --base-url embedded://local --json
```

`project open-target` now gives you a single resolved preview target plus an `inspect_command`, so agents and operators do not need to manually pick through `open_targets`.

If you want the CLI to inspect that resolved target directly, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project inspect-target --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project inspect-target source_of_truth --base-url embedded://local --json
```

`project inspect-target` now reads the resolved file or directory target and returns a structured inspection payload, so you can move from preview handoff to actual content inspection without adding another tool.

If you want the CLI to execute that preview inspection step directly, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project run-inspect-command --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project run-inspect-command source_of_truth --base-url embedded://local --json
```

`project run-inspect-command` now executes the implied preview inspection path and returns the resulting structured inspection payload in one step.

If you want a higher-level workspace overview that decides whether you should start a new trial flow or continue inside the current project, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace status --base-url embedded://local --json
```

If you want a shorter workspace-level operator view, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace summary --base-url embedded://local --json
```

`workspace status --json` now tells you:

- whether the current directory is already inside an AIL project
- the current project summary when one is available
- the latest readiness and RC signals
- the latest recorded trial batch summary
- the recommended workspace-level next action

`workspace summary --json` gives the same workspace layer in a more compact operator-oriented shape:

- product surface
- current project summary when applicable
- readiness summary
- RC summary
- latest trial batch summary
- recommended workspace action

If you specifically want the shortest workspace-level preview handoff, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace preview --base-url embedded://local --json
```

If you want the CLI to resolve one concrete workspace-level preview target for inspection, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace open-target --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace open-target project_context --base-url embedded://local --json
```

`workspace open-target` now gives you a single resolved repo-level or delegated project-level preview target plus an `inspect_command`.

If you want the CLI to execute that workspace inspection step directly, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace run-inspect-command --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace run-inspect-command project_context --base-url embedded://local --json
```

`workspace run-inspect-command` now executes the implied workspace inspection path and returns the resulting inspection payload in one step.

If you want one consolidated machine-readable workspace handoff bundle, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace export-handoff --base-url embedded://local --json
```

`workspace export-handoff --json` now combines workspace summary, preview, primary target resolution, and primary target inspection into one bundle.

If you want the CLI to execute that workspace-level next action directly, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace go --base-url embedded://local --json
```

`workspace go` now acts as the unified workspace entrypoint:

- in repo/root context, it follows the current frozen-profile trial entry
- inside an initialized AIL project, it routes into `project go`

If you want the default high-frequency workspace follow-up path, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace continue --base-url embedded://local --json
```

`workspace continue` now acts as the narrow follow-up entry:

- inside an initialized AIL project, it routes into `project continue --diagnose-compile-sync`
- in repo/root context, it falls back to the current workspace-level execution or recovery path

If you want a workspace-level recovery-oriented diagnosis before choosing the next repo-level or project-level entry, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace doctor --base-url embedded://local --json
```

`workspace doctor` now acts as the recovery entrypoint for the workspace layer:

- in repo/root context, it tells you whether the workspace is healthy enough for the canonical trial path or whether you should refresh RC/readiness first
- inside an initialized AIL project, it delegates to `project doctor --fix-plan`

If you want a single CLI view of the current RC and readiness state, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli rc-check --base-url embedded://local --json
```

`rc-check --json` now summarizes:

- current RC result
- current readiness result
- frozen release-baseline benchmark signals
- latest trial batch summary
- current workspace recommendation

If you want `rc-check` to refresh readiness before reading the current state, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli rc-check --refresh --base-url embedded://local --json
```

`--refresh` currently refreshes readiness safely without forcing the heavier benchmark tail back into every CLI call.

If you want the CLI to execute the current RC-level recommended action directly, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli rc-go --base-url embedded://local --json
```

If you want the same entrypoint after refreshing readiness first, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli rc-go --refresh --base-url embedded://local --json
```

`project summary --json` now also includes:

- `recommended_primary_action`
- `recommended_primary_command`
- `recommended_primary_reason`

This lets an IDE, agent, or operator decide whether the safest next move is to inspect, recover, or continue iteration.

`trial-run --json` now carries the same primary-action recommendation fields, so a successful first run and a later project summary speak the same workbench language.

If you want the CLI to execute that currently recommended primary workbench action for the project, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project go --base-url embedded://local --json
```

`project go` now acts as the unified project workbench entrypoint. On a healthy project it follows the converged default path, and on a repair or conflict state it routes into the appropriate recovery-oriented workbench action instead of forcing you to choose manually first.

`project go --json` now also includes:

- `route_taken`
- `route_reason`

So an IDE, agent, or automation consumer can see both the recommended primary action and the exact route that was actually executed for this run.

If you are already inside an initialized AIL project and want a non-destructive health check before continuing work, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project check --base-url embedded://local --json
```

If you want the CLI to summarize the current problem and point you at the most likely recovery action, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --base-url embedded://local --json
```

If you want the same diagnosis plus a structured recovery plan, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --fix-plan --base-url embedded://local --json
```

If you want the CLI to apply low-risk fixes before handing you back the next recommended step, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --apply-safe-fixes --base-url embedded://local --json
```

If you want the CLI to apply those safe fixes and continue directly into compile and sync when the resulting state is safe, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --apply-safe-fixes --and-continue --base-url embedded://local --json
```

If you are already inside an initialized AIL project and want the narrowest high-frequency follow-up action, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project continue --compile-sync --base-url embedded://local --json
```

If you want the same follow-up path but want the CLI to verify the current source is already a compile candidate first, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project continue --diagnose-compile-sync --base-url embedded://local --json
```

If you want the CLI to auto-repair a recoverable source before continuing through compile and sync, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project continue --auto-repair-compile-sync --base-url embedded://local --json
```

## The Golden Path

The canonical v1 path is:

```text
ail init
  -> ail generate
  -> ail diagnose
  -> repair if needed
  -> ail compile --cloud
  -> ail sync
```

For the frozen profiles (`landing`, `ecom_min`, `after_sales`), the current expected behavior is:

- `generate -> diagnose` should usually pass on the first try for the standard example prompts
- `repair` remains available for noisy or drifted AIL, but it is no longer treated as a mandatory first-run step for the canonical examples

## Step 1. Create a New Project

From the repo root:

```bash
cd /Users/carwynmac/ai-cl
python3 -m cli init /tmp/my_ail_project
cd /tmp/my_ail_project
```

This creates:

- `.ail/source.ail`
- `.ail/manifest.json`
- `.ail/last_build.json`
- managed and custom project directories

## Step 2. Generate AIL from a Requirement

Example for a frozen profile:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli generate "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。"
```

This writes the generated result into:

- `.ail/source.ail`

At this point, AIL is the source of truth.

Do not manually treat generated frontend/backend files as the source of truth.

You may also see non-blocking notes like:

```text
note: used local fallback generator because cloud generate was unavailable
note: removed compiler-only ^SYS metadata before saving user source
```

These notes do not mean generation failed.

They mean:

- the CLI used the current local fallback generation path
- the CLI saved a diagnose-compatible user source shape into `.ail/source.ail`

## Step 3. Diagnose the Current AIL

Run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli diagnose .ail/source.ail --requirement "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。"
```

If you want machine-readable output:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli diagnose .ail/source.ail --requirement "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。" --json
```

What to look for:

- detected profile
- whether compile is recommended
- whether the AIL is under-specified or invalid

## Step 4. Repair If Needed

If diagnosis says the AIL is not yet a compile candidate, repair it:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli repair .ail/source.ail --requirement "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。" --write
```

This rewrites:

- `.ail/source.ail`

Recommended follow-up:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli diagnose .ail/source.ail --requirement "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。"
```

For the standard frozen-profile example prompts, you should now expect this step to be optional rather than automatic.

## Step 5. Compile Through the Cloud Path

If you are using the embedded local compatibility path:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl AIL_CLOUD_BASE_URL=embedded://local python3 -m cli compile --cloud
```

If you want JSON output:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl AIL_CLOUD_BASE_URL=embedded://local python3 -m cli compile --cloud --json
```

This stores the latest build in:

- `.ail/last_build.json`

Important:

- `compile --cloud` caches the build result
- it does not sync generated files into the project yet

You may also see a non-blocking note like:

```text
note: added compiler-only ^SYS metadata during compile compatibility normalization
```

This does not indicate a failed compile.

It means the CLI added compiler-facing compatibility metadata during the compile step, without changing `.ail/source.ail` as the user-owned source of truth.

## Step 6. Sync Managed Files Into the Project

Run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli sync
```

Or for machine-readable output:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli sync --json
```

This:

- writes generated files only into managed zones
- updates `.ail/manifest.json`
- refuses silent overwrite if managed files have local drift

## Step 7. Check for Conflicts

If sync refuses to overwrite locally modified managed files, inspect conflicts:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli conflicts
```

JSON form:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli conflicts --json
```

If you explicitly want to preserve the local managed copy and then apply the new build:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli sync --backup-and-overwrite
```

This stores backups under:

- `.ail/conflicts/<build_id>/`

## Recommended First Requirements

Start with one of these.

### Landing

```text
做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。
```

### E-commerce

```text
做一个数码商城，包含首页商品列表、商品详情、购物车、结算。
```

### After-sales

```text
做一个售后页面，包含退款申请、换货申请、投诉提交、联系客服。
```

## What “Success” Looks Like

For a successful quickstart run, you should end up with:

- a valid `.ail/source.ail`
- a cached `.ail/last_build.json`
- a populated `.ail/manifest.json`
- generated files inside managed zones
- no writes to custom zones

## Managed vs Custom

Managed zones are compiler-controlled.

Examples:

- `src/views/generated/`
- `src/router/generated/`
- `backend/generated/`

Custom zones are user-controlled.

Examples:

- `src/custom/`
- `src/extensions/`
- `src/theme/`
- `backend/custom/`

Do not treat managed files as your long-term hand-edited source.

## Common Notes

### 1. If `compile --cloud` fails

Check:

- whether the cloud path is reachable
- whether you are using the local embedded mode for repo-local testing

Example:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl AIL_CLOUD_BASE_URL=embedded://local python3 -m cli compile --cloud --json
```

### 2. If `sync` reports conflicts

That is the expected safety behavior.

By default, managed files with local drift are not silently overwritten.

### 3. If output looks incomplete

Use:

- `ail diagnose`
- `ail repair`

before trying to compile again.

### 4. If `generate -> diagnose` already passes

That is now the expected happy path for the standard frozen-profile examples.

You can continue directly to:

- `ail compile --cloud`
- `ail sync`

### 5. If you see `note:` lines during a successful run

Treat them as informational.

Current `note:` lines on the happy path usually mean:

- fallback generation was used in the local environment
- compile applied a compatibility normalization for the current compiler

They are not the same thing as:

- `error: ...`
- `validation_failed`

## Minimal Validation Commands

If you want to confirm the platform is still healthy before or after your first run:

```bash
bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

## Next Reading

After this quickstart, the most useful follow-up documents are:

1. `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md` once available
2. `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md` once available
3. `/Users/carwynmac/ai-cl/docs/AIL_CLI_IMPLEMENTATION_GUIDE.md`
4. `/Users/carwynmac/ai-cl/docs/AIL_CLOUD_SYNC_PROTOCOL_V1.md`

## One-Line Summary

If you only remember one thing: use the CLI to keep `.ail/source.ail` as the source of truth, and treat compile + sync as a managed, conflict-safe path for frozen profiles.


If you want one consolidated machine-readable project handoff bundle for IDEs, agents, or operators, run:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project export-handoff --base-url embedded://local --json
```
