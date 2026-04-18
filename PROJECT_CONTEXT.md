# Project Context

## Purpose

This file is the rolling project context checkpoint for active AIL platform development.

It exists to reduce context explosion, avoid repeated rediscovery, and keep future work anchored to the current product state instead of stale assumptions.

When the project reaches a new stable phase, this file should be updated.

Current packaging and review reference:

- `/Users/carwynmac/ai-cl/SKILL.md`
- `/Users/carwynmac/ai-cl/SKILL_PACKAGING_PLAN_20260418.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PHASE_REVIEW_20260417.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PHASE_REVIEW_20260416.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PHASE_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PERSONAL_SLICE_EVALUATION_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_COMPANY_SLICE_EVALUATION_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_IMPLEMENTATION_PLAN_20260409.md`
- `/Users/carwynmac/ai-cl/NEXT_PHASE_RECOMMENDATION_20260409.md`
- `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_PHASE_CLOSEOUT_20260409.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260408.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260406.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260403.md`
- `/Users/carwynmac/ai-cl/WEBSITE_PRIORITY_REVIEW_20260403.md`
- `/Users/carwynmac/ai-cl/NEXT_PHASE_OPTIONS_RFC_20260403.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260328.md`
- `/Users/carwynmac/ai-cl/WEBSITE_PRIORITY_REVIEW_20260328.md`
- `/Users/carwynmac/ai-cl/SAFE_SPLIT_REVIEW_20260328.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260319.md`
- `/Users/carwynmac/ai-cl/SYSTEM_VS_TEST_HELPER_BOUNDARY_20260322.md`
- `/Users/carwynmac/ai-cl/SYSTEM_VS_TEST_HELPER_DETAILED_MATRIX_20260322.md`
- `/Users/carwynmac/ai-cl/testing/results/website_real_validation_review_20260320.md`
- `/Users/carwynmac/ai-cl/testing/results/website_real_validation_review_20260320.json`
- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_FRONTIER_SUMMARY_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_PRODUCT_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_DEMO_PACK_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_DELIVERY_CHECKLIST_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_REQUIREMENT_TEMPLATES_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_SALES_POSITIONING_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_NEXT_TASKS_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/website_delivery_validation_20260319.md`
- `/Users/carwynmac/ai-cl/testing/results/website_delivery_assets_20260319.md`
- `/Users/carwynmac/ai-cl/testing/run_website_demo_pack.sh`
- `/Users/carwynmac/ai-cl/testing/build_website_delivery_assets.sh`

Current website-oriented delivery entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website check '做一个企业产品官网，包含首页、功能介绍、FAQ、联系我们。' --base-url embedded://local --json
```

This is now the thinnest CLI entry for evaluating whether one requirement stays inside the current supported website surface, which pack it belongs to, and whether the canonical trial flow validates it as deliverable.

Current website-oriented asset consumption entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website assets --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website assets company_product --json
```

This is now the thinnest CLI entry for consuming the reusable website delivery assets that were built from the validated website packs. It can return the full asset manifest or one pack-specific bundle without reopening trial, preview, or export logic.

Current website-oriented asset target resolution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website open-asset --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website open-asset company_product --json
```

This now resolves one concrete website delivery asset target. By default it points at the website delivery asset summary Markdown, and with a pack id it points at that pack's JSON asset while also exposing the related Markdown and evidence files.

Current website-oriented asset inspection entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website inspect-asset --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website inspect-asset company_product --json
```

This now inspects one concrete website delivery asset target directly. By default it reads the website delivery asset summary Markdown, and with a pack id it reads that pack's JSON asset through the same stable asset-resolution path exposed by `website open-asset`.

Current website-oriented preview entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website preview --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website preview company_product --json
```

This now gives one website-level preview and handoff view. By default it previews the website frontier asset surface, and with a pack id it previews one validated website pack bundle while preserving the same open/inspect/export semantics used by the rest of the website asset flow.

Current website-oriented handoff export entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website export-handoff --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website export-handoff company_product --json
```

This now exports one consolidated website-oriented handoff bundle. By default it exports the website summary handoff, and with a pack id it exports one pack-specific bundle that combines website summary, assets, resolved target, and inspected target into one payload for operators, IDEs, and agents.

Current website-oriented inspection execution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website run-inspect-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website run-inspect-command company_product --json
```

This now executes the exact website asset inspection step implied by the current website handoff, without inventing a second inspection model. By default it executes the summary-asset inspection path, and with a pack id it executes that pack's asset inspection path.

Current website-oriented summary entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website summary --json
```

This now gives one website-level overview of the current frontier, reusable delivery assets, delivery validation, and demo-pack state, plus the current recommended website-oriented next action.

Current website-oriented execution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli website go --json
```

This now executes the current recommended website-oriented action directly. In the current healthy website state, that means routing to `website assets` so operators, IDEs, and agents can consume the reusable validated website bundles without manually stitching the next step.

Reusable website delivery asset build entry:

```bash
bash /Users/carwynmac/ai-cl/testing/build_website_delivery_assets.sh
```

This now turns the validated website packs into reusable delivery assets. The script emits one summary JSON, one summary Markdown file, and per-pack JSON/Markdown bundles containing canonical requirement, expected profile, expected primary route, expected primary preview target, safe talking points, and linked validation evidence.

The website task track now reflects that Priorities 1 through 4 are substantially complete. The remaining website mainline discipline is to keep `app_min` out of scope and move the next work toward consuming the new website delivery assets instead of reopening website-boundary definition.

The main engine file has now crossed the point where editor inline rendering can fail due to size alone. The latest safe split review concludes:

- first split should target the `ecom` / `after_sales` view-generation cluster
- `landing` should be the second-stage split, not the first cut
- parser/build orchestration should stay in place during the first extraction

That first extraction is now implemented:

- `/Users/carwynmac/ai-cl/ail_engine_v5_ecom.py` now holds the ecom / after-sales view-generation cluster
- `/Users/carwynmac/ai-cl/ail_engine_v5.py` now delegates through `AILEcomGeneratorMixin`
- remaining ecom page-detection and component-prop helpers also now live in the extracted module
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json` remains `status = ok`
- this is now the preferred pause point before any second-stage `landing` split

Fresh validation note as of 2026-04-04:

- a later fresh smoke interruption after the 2026-04-03 customization UX work was traced to Codex exec/session-pool overload, not to CLI logic regression
- after restarting Codex, fresh compile succeeded again
- after restarting Codex, fresh `/Users/carwynmac/ai-cl/testing/cli_smoke.sh` also succeeded again
- current reality has returned to:
  - `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`
  - `status = ok`

The managed / unmanaged productization track has now moved past basic viability and into workflow closure.

Current concise truth:

- generated projects emit:
  - `/.ail/hook_catalog.json`
  - `/.ail/hook_catalog.md`
- current hook discovery entrypoints are:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hooks --json`
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hooks --json`
- current guided entrypoints are:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --json`
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --json`
- current grouped help entrypoints are:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --help`
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --help`
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --help`
- current scaffolding entrypoints are:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init <hook_name> --json`
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init --follow-recommended --json`
- current repo-root continuation entrypoint is:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --json`

What is already true:

- durable hooks are discoverable without opening managed Vue files
- repo-root users can now start, preview, inspect, continue, and confirm durable hook work without manually reconstructing paths
- `hook-init`, `hook-continue`, and `hook-guide` now all expose guided dry-run / explain / shell / clipboard / target / inspect / open / confirm layers
- the customization workflow is now strong enough to treat as a real product surface, not an internal mechanism

For day-to-day use, the shortest references are now:

- `/Users/carwynmac/ai-cl/SKILL.md`
- `/Users/carwynmac/ai-cl/SKILL_PACKAGING_PLAN_20260418.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PHASE_REVIEW_20260417.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PHASE_REVIEW_20260416.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PHASE_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_PERSONAL_SLICE_EVALUATION_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_COMPANY_SLICE_EVALUATION_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_IMPLEMENTATION_PLAN_20260409.md`
- `/Users/carwynmac/ai-cl/NEXT_PHASE_RECOMMENDATION_20260409.md`
- `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_PHASE_CLOSEOUT_20260409.md`
- `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_OPERATOR_CHEAT_SHEET_20260406.md`
- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json`
  - `status = ok`

Current managed / unmanaged milestone reference:

- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_REVIEW_20260409.md`
- `/Users/carwynmac/ai-cl/BRAND_DISTINCTION_IMPLEMENTATION_PLAN_20260409.md`
- `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_PHASE_CLOSEOUT_20260409.md`
- `/Users/carwynmac/ai-cl/NEXT_PHASE_RECOMMENDATION_20260409.md`
- `/Users/carwynmac/ai-cl/MANAGED_UNMANAGED_MILESTONE_20260403.md`
- `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_OPERATOR_CHEAT_SHEET_20260406.md`

## Current Date Anchor

- 2026-04-18

## Current Product Stage

The project is currently in:

- frozen-profile product closure

This means:

- the mainline CLI path is already coherent
- frozen profiles are the current product surface
- the next work should prioritize product entry, packaging, and repeatable first-user flows
- the next work should not drift back into low-yield patch churn unless a real regression appears

## Current Supported Product Surface

Formal frozen profiles:

- `landing`
- `ecom_min`
- `after_sales`

Experimental only:

- `app_min`

`app_min` is not part of the formal v1 product promise.

## Current Main User Path

Canonical CLI path:

```text
ail init
  -> ail generate
  -> ail diagnose
  -> repair if needed
  -> ail compile --cloud
  -> ail sync
```

Current expected frozen-profile behavior:

- first-pass `generate -> diagnose` should usually succeed on the standard frozen-profile examples
- `repair` remains available as recovery, not as the expected first step

## Current Fastest Entry

Primary entrypoint for first-user trials:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario landing --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario ecom_min --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli trial-run --scenario after_sales --base-url embedded://local
```

Shell wrapper also exists:

```bash
bash /Users/carwynmac/ai-cl/demo_v1.sh --scenario landing
```

The shell wrapper is intentionally thin and delegates to the CLI subcommand.

Batch trial/RC entry check:

```bash
bash /Users/carwynmac/ai-cl/testing/run_trial_entry_checks.sh
```

Unified RC entry:

```bash
bash /Users/carwynmac/ai-cl/testing/run_rc_checks.sh
```

Latest RC outputs:

- `/Users/carwynmac/ai-cl/testing/results/rc_checks_results.json`
- `/Users/carwynmac/ai-cl/testing/results/rc_checks_report.md`

The RC aggregate now explicitly includes project-workbench signals from CLI smoke:

- `project_check_json_ok`
- `project_check_conflict_json_ok`
- `project_doctor_json_ok`
- `project_doctor_validation_json_ok`
- `project_go_json_ok`
- `project_go_repair_json_ok`
- `project_go_conflict_json_ok`

Readiness snapshot entry:

```bash
bash /Users/carwynmac/ai-cl/testing/run_readiness_snapshot.sh
```

Latest readiness outputs:

- `/Users/carwynmac/ai-cl/testing/results/readiness_snapshot.json`
- `/Users/carwynmac/ai-cl/testing/results/readiness_snapshot.md`

The readiness snapshot now also tracks:

- `project_workbench_ok`
- `project_check_smoke_ok`
- `project_check_conflict_smoke_ok`
- `project_doctor_smoke_ok`
- `project_doctor_validation_smoke_ok`
- `project_doctor_apply_safe_noop_smoke_ok`
- `project_doctor_apply_safe_repair_smoke_ok`
- `project_doctor_apply_safe_continue_noop_smoke_ok`
- `project_doctor_apply_safe_continue_repair_smoke_ok`
- `project_continue_auto_repair_smoke_ok`
- `project_continue_auto_no_repair_smoke_ok`
- `project_go_smoke_ok`
- `project_go_repair_smoke_ok`
- `project_go_conflict_smoke_ok`

Recorded trial entry:

```bash
bash /Users/carwynmac/ai-cl/testing/run_trial_recording.sh --scenario landing --base-url embedded://local
```

This now auto-generates:

- `first_user_trial_capture_<id>.json`
- `first_user_trial_results_<id>.md`

Recorded trial batch entry:

```bash
bash /Users/carwynmac/ai-cl/testing/run_trial_batch_recording.sh --base-url embedded://local
```

This now auto-generates:

- multiple `first_user_trial_results_<id>.md`
- a batch JSON summary
- a batch Markdown summary

`trial-run --json` now also includes a `cloud_status` summary payload so a single run can feed:

- first-user trial logging
- RC checks
- automation and agent consumption

`trial-run` now also includes preview handoff signals:

- `preview_handoff`
- `preview_hint`
- `open_targets`

This means a successful run now tells the user what to inspect first instead of only saying that the workflow succeeded.

That preview handoff shape is now also aligned across:

- `python3 -m cli cloud status --json`
- `python3 -m cli build artifact <build_id> --json`
- `python3 -m cli project summary --json`
- `python3 -m cli project preview --json`

The latest CLI smoke now explicitly guards:

- `cloud_status_preview_json_ok`
- `build_artifact_preview_json_ok`
- `project_preview_json_ok`
- `project_preview_conflict_json_ok`
- `project_open_target_json_ok`
- `project_open_target_default_json_ok`
- `project_inspect_target_json_ok`
- `project_inspect_target_default_json_ok`
- `project_export_handoff_json_ok`
- `project_export_handoff_conflict_json_ok`
- `workspace_preview_repo_json_ok`
- `workspace_preview_project_json_ok`
- `workspace_open_target_repo_json_ok`
- `workspace_open_target_project_json_ok`
- `workspace_inspect_target_repo_json_ok`
- `workspace_inspect_target_project_json_ok`

RC and readiness now also consume those preview smoke signals directly, so the preview handoff surface is no longer only smoke-covered; it is now part of the higher-level stage judgment as well.

Project-oriented overview entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project summary --base-url embedded://local
```

This is now the preferred CLI handoff once a user is already inside an initialized project and wants a higher-level local-plus-cloud overview.

Project-level preview handoff entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project preview --base-url embedded://local
```

This is now the shortest CLI entry when a user already has a project and mainly needs to know which artifact or generated surface to inspect first.

Project-level preview-target resolution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project open-target --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project open-target source_of_truth --base-url embedded://local
```

This now resolves one concrete preview target out of the project-level preview handoff, so higher-level consumers can move directly from "which surface should I inspect?" to "give me the exact file or directory target to inspect now."

Project-level preview-target inspection entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project inspect-target --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project inspect-target source_of_truth --base-url embedded://local
```

This now reads the resolved preview target directly and returns a structured file or directory inspection payload, so project-level preview handoff can continue all the way into concrete inspection without another manual step.

Project-level preview-target execution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project run-inspect-command --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project run-inspect-command source_of_truth --base-url embedded://local --json
```

This now executes the implied project preview inspection step directly and returns the resulting inspection payload in one machine-readable response.

Project-level export handoff entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project export-handoff --base-url embedded://local --json
```

This now exports one consolidated project handoff bundle that combines summary, preview, primary target resolution, and primary target inspection into a single machine-readable payload.

Website-oriented preview consumption is now stronger across:

- `project preview`
- `project export-handoff`
- `cloud status`
- `build artifact`

The shared preview handoff now exposes website-oriented display labels, a stable website target ordering, and a structured `website_delivery_summary` so downstream consumers can treat generated pages, routes, backend stubs, source-of-truth, manifest, and the latest artifact/build state as a website delivery surface instead of a generic artifact blob.

Workspace-level preview handoff entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace preview --base-url embedded://local
```

This is now the shortest CLI entry when a user is not inside an active project and mainly needs to know which repo-level readiness, RC, or trial artifact to inspect first.

Workspace-level preview-target resolution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace open-target --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace open-target project_context --base-url embedded://local
```

Workspace-level preview-target inspection entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace inspect-target --base-url embedded://local
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace inspect-target project_context --base-url embedded://local
```

This now resolves one concrete target out of the workspace-level preview handoff, so repo-level operators and agents can move directly from a workspace preview summary to one exact file target to inspect.

Workspace-level preview-target execution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace run-inspect-command --base-url embedded://local --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace run-inspect-command project_context --base-url embedded://local --json
```

This now executes the implied workspace inspection step directly and returns the resulting inspection payload in one machine-readable response.

Workspace-level export handoff entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace export-handoff --base-url embedded://local --json
```

This now exports one consolidated workspace handoff bundle that combines workspace summary, preview, primary target resolution, and primary target inspection into a single machine-readable payload.

Workspace-level website preview consumption is also more explicit now. Repo-level preview/export handoff uses website-facing labels for trial, readiness, and RC artifacts, while project-level delegation carries through the same `website_delivery_summary` surface used by the project handoff. Repo-root export now also includes a `website_surface_summary` that names the supported and partial website packs plus the recommended validation flow.

`project summary --json` now also includes:

- `recommended_primary_action`
- `recommended_primary_command`
- `recommended_primary_reason`

This means the project-level overview can now tell higher-level consumers which workbench entry should be treated as the primary next move.

Readiness snapshot now also records the current healthy-project default workbench handoff by probing:

- `recommended_primary_action`
- `recommended_primary_command`
- `recommended_primary_reason`

This gives the phase-level snapshot a concrete answer to "what should a healthy project do next by default?" instead of only reporting green/red status.

RC aggregation now mirrors that same primary-action probe, so release review and readiness review both point at the same default workbench handoff.

`trial-run --json` now also exposes the same primary-action recommendation fields, so trial entry, project summary, RC, and readiness all converge on one default next-step language.

Recorded trial capture now also promotes that same recommendation layer into the generated Markdown result, so trial history can be reviewed without reopening the raw JSON payload.

Recorded trial batch summaries now also aggregate `recommended_primary_action_distribution`, so we can see whether a batch of healthy projects is converging on the same default workbench path.

Recorded trial entries and trial batch summaries now also preserve `route_taken` and `route_reason`, so we can distinguish between the system's recommended next workbench action and the actual execution surface used for first-user trial runs.

RC and readiness now also track whether the first-user trial entry surface itself has converged on a single actual route. The current expected route is:

- `trial_run_canonical_flow`

This complements the existing `recommended_primary_action` convergence signal by separately telling us whether the trial execution surface itself is behaving consistently across the latest recorded frozen-profile batch.

RC and readiness now also track whether that primary action is actually converged across the latest recorded frozen-profile batch, instead of only listing the current default action.

RC and readiness now also treat `project go` as a first-class protected workbench entry instead of leaving it as an uncovered convenience command. This means the unified workbench execution path is now part of the same stage judgement surface as `project check`, `project doctor`, and the existing continue flows.

Unified project workbench execution entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project go --base-url embedded://local
```

`project go` now executes the currently recommended primary workbench action instead of only reporting it. This means a healthy project, a repairable project, and a conflict project can all be routed through one higher-level CLI entrypoint while still preserving the existing safety boundaries around conflicts and overwrite decisions.

`project go --json` now also emits:

- `route_taken`
- `route_reason`

This makes the unified workbench execution path easier for higher-level consumers to interpret, because they no longer need to infer the actual chosen route only from nested result fields.

Project-oriented non-destructive health entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project check --base-url embedded://local
```

This is now the preferred CLI check entry once a user is already inside an initialized project and wants to verify:

- whether source, manifest, and last build are present
- whether cloud status is currently queryable
- whether sync conflicts are already waiting
- whether the project is ready for a narrow compile-and-sync follow-up

Project-oriented recovery diagnosis entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --base-url embedded://local
```

This is now the preferred CLI recovery-oriented entry when the user wants one command to answer:

- whether the current issue is local project state, source validity, or sync drift
- which recovery action is most appropriate next
- whether to repair source, resolve conflicts, or continue iteration normally

Structured recovery-plan entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --fix-plan --base-url embedded://local
```

This now returns a step-by-step guided recovery plan for the current recommended action instead of only a diagnosis summary.

Safe recovery-application entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --apply-safe-fixes --base-url embedded://local
```

This now applies low-risk local recovery steps when the current recommendation is safe to automate, while still leaving conflict-resolution and overwrite decisions explicit.

Safe recovery-and-continue entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project doctor --apply-safe-fixes --and-continue --base-url embedded://local
```

This now lets project doctor apply low-risk fixes first and then continue directly into compile and sync when the resulting state is safe to proceed.

High-frequency project follow-up entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project continue --compile-sync --base-url embedded://local
```

This is now the preferred narrow project-level action when the user already has a project and simply wants to recompile the current source and sync the latest managed output.

Safer project follow-up entry:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project continue --diagnose-compile-sync --base-url embedded://local
```

This is now the preferred narrow project-level action when the user wants the CLI to diagnose the current source first and only continue into compile-and-sync if the source is already a compile candidate.

The project-level workbench is now effectively:

- `project go`
- `project summary`
- `project preview`
- `project open-target`
- `project inspect-target`
- `project check`
- `project doctor`
- `project doctor --fix-plan`
- `project doctor --apply-safe-fixes`
- `project doctor --apply-safe-fixes --and-continue`
- `project continue --compile-sync`
- `project continue --diagnose-compile-sync`
- `project continue --auto-repair-compile-sync`

## Current Key Runtime Files

- `/Users/carwynmac/ai-cl/ail_engine_v4.py`
- `/Users/carwynmac/ai-cl/ail_engine_v5.py`
- `/Users/carwynmac/ai-cl/ail_server_v5.py`
- `/Users/carwynmac/ai-cl/cli/ail_cli.py`
- `/Users/carwynmac/ai-cl/cli/cloud_client.py`
- `/Users/carwynmac/ai-cl/cli/sync_engine.py`

## Current Key Product Docs

- `/Users/carwynmac/ai-cl/PRODUCT_FUNCTION_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/V1_EXECUTION_PLAN.md`
- `/Users/carwynmac/ai-cl/NEXT_FRONTIER_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/WEBSITE_SUPPORT_MATRIX_20260319.md`
- `/Users/carwynmac/ai-cl/APP_MIN_STRATEGY_REVIEW_20260319.md`
- `/Users/carwynmac/ai-cl/SECONDARY_SURFACE_STRATEGY_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_CONSUMPTION_PLAN_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_PANEL_CONTRACT_V1_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_PANEL_STATE_MODEL_V1_20260319.md`
- `/Users/carwynmac/ai-cl/IDE_ACTION_MAPPING_V1_20260319.md`
- `/Users/carwynmac/ai-cl/QUICKSTART_V1.md`
- `/Users/carwynmac/ai-cl/FROZEN_PROFILE_EXAMPLES_V1.md`
- `/Users/carwynmac/ai-cl/V1_RELEASE_GATE.md`
- `/Users/carwynmac/ai-cl/FIRST_USER_TRIAL_PLAN.md`
- `/Users/carwynmac/ai-cl/FIRST_USER_TRIAL_OPERATOR_GUIDE.md`
- `/Users/carwynmac/ai-cl/V1_PROGRESS_REVIEW_20260317.md`

## Current Validation Baseline

Latest stable signals:

- `/Users/carwynmac/ai-cl/testing/run_cli_checks.sh` passes
  - and now covers:
    - `project check` happy-path JSON
    - `project check` conflict-path JSON
    - `project doctor` happy-path JSON
    - `project doctor` validation-path JSON
    - `project doctor --apply-safe-fixes` no-op JSON
    - `project doctor --apply-safe-fixes` repair JSON
    - `project doctor --apply-safe-fixes --and-continue` no-op JSON
    - `project doctor --apply-safe-fixes --and-continue` repair JSON
    - `project continue --auto-repair-compile-sync` no-repair path JSON
    - `project continue --auto-repair-compile-sync` repair path JSON
    - `project go` healthy-path JSON
    - `project go` repair-path JSON
    - `project go` conflict-path JSON
- `/Users/carwynmac/ai-cl/testing/run_raw_model_outputs.sh` reports:
  - `total_samples=50`
  - `initial_compile_rate=60.0`
  - `repair_success_rate=100.0`
  - `final_compile_rate=100.0`
- `/Users/carwynmac/ai-cl/testing/run_evolution_loop.sh` reports:
  - `total_candidates=0`
  - `active_suggested_tokens=0`
  - `active_patch_pressure=[]`
- `/Users/carwynmac/ai-cl/benchmark/run_benchmark.sh` remains at:
  - `BENCHMARK_DONE total=20 passed=16 failed=4`

This benchmark state is the current known baseline, not a newly introduced regression.

For v1 frozen-profile RC decisions, the operative benchmark signal is:

- `benchmark_results.release_baseline.ok = true`

The global benchmark `release_decision` may still be `fail` because experimental or auxiliary gates remain outside the frozen v1 product promise.

## Important Recent Fixes Already Landed

### 1. First-pass CLI generate/diagnose mismatch fixed

The `^SYS[...]` mismatch that previously caused first-pass frozen-profile diagnose failure was fixed.

Current result:

- frozen-profile standard prompts now first-pass diagnose successfully in the mainline CLI path

### 2. Frozen-profile richer coverage tightened

The following richer supported sections were tightened and should not be treated as active blocker work now:

- landing:
  - `landing:Team`
  - `landing:FAQ`
  - `landing:Stats`
  - `landing:LogoCloud`
- ecom_min:
  - `ecom:Banner`
  - `ecom:CategoryNav`
  - `ecom:ShopHeader`

### 3. One-command frozen-profile entry now exists

- `python3 -m cli trial-run`
- `bash /Users/carwynmac/ai-cl/demo_v1.sh`

### 4. Cloud compile path now exposes compatibility mode

The CLI cloud compile path now surfaces which cloud compile variant was used.

Current behavior:

- embedded/local mode now prefers `v1_compile` via `/api/v1/compile`
- legacy `/compile` remains available only as a compatibility fallback
- `trial-run --json` and `compile --json` now return:
  - `cloud.base_url`
  - `cloud.api_variant`
  - `cloud.endpoint`
- the client is prepared to negotiate between current legacy compile behavior and a future `/api/v1/compile` path

### 5. Cloud build query exists in v1 form

The server now supports:

- `POST /api/v1/compile`
- `GET /api/v1/build/{build_id}`
- `GET /api/v1/project/{project_id}`
- `GET /api/v1/project/{project_id}/builds`
- `GET /api/v1/build/{build_id}/artifact`

Current status:

- compile persists v1 build metadata records
- build query returns:
  - `build_id`
  - `project_id`
  - `mode`
  - `status`
  - `created_at`
  - `diff_summary`
  - `artifact_available`
  - `manifest_version`
- CLI now exposes build query directly as:
  - `python3 -m cli build show <build_id> --base-url ...`
- CLI now exposes build artifact query directly as:
  - `python3 -m cli build artifact <build_id> --base-url ...`
- CLI now exposes project query directly as:
  - `python3 -m cli project show [project_id] --base-url ...`
  - `python3 -m cli project builds [project_id] --base-url ...`
- CLI now exposes a summary cloud status entrypoint directly as:
  - `python3 -m cli cloud status [project_id] --base-url ...`
- project build list returns:
  - ordered build items
  - `limit`
  - `cursor`
  - `mode` filter
- project metadata returns:
  - `project_id`
  - `latest_build_id`
  - `latest_manifest_version`
  - `created_at`
  - `updated_at`
- artifact descriptor returns:
  - `artifact_id`
  - `build_id`
  - `download_url`
  - `expires_at`
  - `sha256`
  - `format`
  - `local_path`
- embedded/local CLI compile now prefers the v1 compile route

## Things That Should Not Be Reopened Without New Evidence

Do not reopen these as primary workstreams unless a real regression or new user evidence appears:

- new token patching
- alias patching
- more frozen-profile richer coverage patching
- profile expansion
- compiler rewrite
- broad `app_min` hardening for v1
- benchmark policy changes
- more cleanup / archive work

## Current Best Next Development Focus

Current priority:

- keep the frozen-profile CLI path as the primary product surface
- continue turning the v1 cloud query surface into a usable CLI-facing product layer
- focus on product packaging, query usability, and guided first-user flow

Most likely near-term next steps:

1. make cloud status and query paths easier to use in trial and RC workflows
2. keep extending CLI consumption of v1 cloud APIs beyond compile
3. add a lightweight preview/open-next-step handoff
4. use the trial entrypoint and cloud queries together for repeatable controlled trial batches

## Current Secondary Areas

These remain secondary for now:

- Studio as primary entrypoint
- IDE implementation work
- app_min productization
- broad user-facing expansion outside the frozen profiles

## Update Rule

Update this file when one of these happens:

- the main user path changes
- supported v1 profiles change
- a major blocker is resolved
- a new entrypoint becomes primary
- release gate assumptions materially change
- the next development focus changes

## One-Line Current Summary

AIL is currently past the patch-chasing phase for frozen profiles and is now productizing a stable CLI-first entrypoint plus a usable v1 cloud query and status surface.

## New Stable Stage: Workspace Status Entry

The CLI now exposes a higher-level workspace entrypoint:

- `python3 -m cli workspace status --base-url ...`
- `python3 -m cli workspace summary --base-url ...`
- `python3 -m cli workspace go --base-url ...`
- `python3 -m cli workspace doctor --base-url ...`
- `python3 -m cli workspace continue --base-url ...`
- `python3 -m cli rc-check --base-url ...`
- `python3 -m cli rc-go --base-url ...`

This entrypoint is intentionally above `trial-run`, `project summary`, and `project go`.

It now reports:

- whether the current directory is already inside an initialized AIL project
- the current project summary when available
- the latest readiness snapshot
- the latest RC aggregate
- the latest recorded frozen-profile trial batch summary
- a recommended workspace-level next action and command

`workspace summary` now provides the same workspace layer in a more compact operator-oriented envelope:

- product surface
- current project high-level state when applicable
- readiness summary
- RC summary
- latest recorded trial batch summary
- recommended workspace action

`rc-check` now lifts the release-facing shell/report layer into the CLI itself:

- RC status
- readiness status
- frozen release-baseline benchmark signals
- latest trial batch summary
- current workspace recommendation

`rc-check --refresh` now adds a safe refresh step ahead of that summary:

- refreshes readiness snapshot
- then reads the latest RC/readiness artifacts
- intentionally does not force the full benchmark slow tail into every CLI invocation

`rc-go` now turns that release-facing layer into an execution entrypoint:

- if RC and readiness are green, it routes into `workspace go`
- if they are not green, it stops with a release-facing attention result instead of silently overreaching

Current default behavior:

- in repo/root context:
  - recommend `trial-run` when readiness is green
- inside an initialized project:
  - recommend `project go`

`workspace go` now executes that converged workspace-level route directly:

- repo/root context:
  - runs the current canonical frozen-profile trial entry
- inside an initialized project:
  - runs `project go`

`workspace status`, `workspace summary`, `workspace doctor`, `workspace continue`, `workspace go`, and `rc-check` are now part of CLI smoke coverage:

- repo-level usage
- project-level usage

This means the workspace layer is no longer only a convenience view; it is now a protected product entry and execution surface.

RC and readiness now also track the workspace recovery entry, not just the workspace execution entry. That means the workspace layer is now judged across:

- overview
- recovery diagnosis
- high-frequency follow-up
- execution

instead of only exposing those paths as uncovered convenience commands.

2026-03-20 website runtime validation moved from broad pack-level confirmation into targeted quality improvement on two supported website surfaces:

- personal independent site:
  - single-page anchor navigation was fixed (`#about`, `#features`, `#portfolio`, `#contact`)
  - fallback brand naming no longer leaks generated project directory names
  - hero, about, services, and portfolio cards now read more like a real personal portfolio site
  - portfolio cards now include meta and outcome layers instead of repeated placeholder copy
- company / product website:
  - fallback visible brand no longer leaks generated project directory names and now normalizes to `品牌官网` when needed
  - hero, CTA, and navigation now use product-site language (`产品介绍`, `产品能力`, `客户评价`, `联系我们`, `预约演示`, `查看能力`)
  - homepage now renders a real product-introduction section for single-page product sites
  - FAQ defaults now fill in product-site questions when FAQ is requested but no explicit items are provided
  - testimonial output now renders trust-oriented quote cards with quote / role / result structure instead of only short keyword lists
  - the `产品能力` single-page nav target bug was fixed so it now lands on `#features` instead of falling back to `#hero`

Real runtime-backed review now lives in:

- `/Users/carwynmac/ai-cl/testing/results/website_real_validation_review_20260320.md`
- `/Users/carwynmac/ai-cl/testing/results/website_real_validation_review_20260320.json`

Current pack-level truth after those checks:

- personal independent site is the strongest quality surface right now
- company / product website is structurally much stronger than before and now has a more complete product-story arc
- ecommerce storefront remains the most explicit frontstage interaction loop (`/`, product, cart, checkout) and now also has a cleaner storefront shell plus safer no-backend defaults
- after-sales is now stronger as a service-center website surface, while still not being a full support operations system

Further personal independent site quality work on 2026-03-20 strengthened both the visual identity and the portfolio/case layer:

- the warmed-up visual treatment now reads more like a real portfolio surface
- the hero now also carries a clearer persona layer, so the page explains what kind of independent collaborator this is before the case studies start
- the about and collaboration-feedback copy now reads more like a real independent-consultant working method instead of a neutral self-introduction
- portfolio cards now include more specific case-detail lines instead of only title/description/outcome
- portfolio cards are now more clearly separated into different case types instead of reading like one repeated showcase pattern
- portfolio cards now also read more like compact project cards by exposing project type, delivery scope, and result
- the hero now also carries a stronger authored entrance through an `AUTHOR SIGNATURE` strip
- the portfolio area now also reads more like a chosen project shelf through a `CURATED SHELF` layer before the grid
- the default hero, about, feedback, and contact copy now also read more like one authored personal voice instead of a slightly safer multi-section template voice
- the strengthened runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/PersonalIndependentSiteSignatureReview`
- the latest signature pass now also adds:
  - a lighter editorial header-note strip before the hero claim
  - ordered case-sequence markers with short editor notes in the portfolio shelf
  - a compact footer signoff strip that makes the ending feel more intentionally authored

Personal runtime proof was refreshed again on 2026-04-01 so the line is no longer lagging the other three website baselines in closeout evidence:

- runtime screenshots:
  - `/Users/carwynmac/ai-cl/output/playwright/personal_signature_review_runtime.png`
  - `/Users/carwynmac/ai-cl/output/playwright/personal_story_review_submit_runtime.png`
- the current baseline now has fresh delivery-state proof for:
  - the full-page personal portfolio render with stronger authored-signature, curated-shelf treatment, a more recognizably personal voice, and clearer header/portfolio/footer signature framing
  - the contact-submit success state remains previously runtime-verified (`已收到您的咨询，我们会尽快联系您。`)

Further company / product website quality work on 2026-03-20 strengthened the product-site default narrative, brand treatment, and sentence-level copy again:

- product-introduction copy now emphasizes fit, scenario, and value-difference more explicitly
- feature cards now read more like product-positioning support instead of generic marketing bullets
- testimonial output now behaves like a trust section with richer quote text plus role/result metadata
- testimonial cards now also carry clearer scenario context, so they read more like real team retrospectives
- FAQ items now also carry clearer scenario context and short follow-up guidance, so they read more like pre-sales handling notes
- FAQ now also has a visible scan strip and clearer per-item `查看建议` affordances, so the section is easier to scan as a decision layer
- expanded FAQ answers now separate `核心判断` from `下一步建议`, so the open state reads more like a guided pre-sales answer
- hero, introduction, and CTA copy now read more like first-visit product judgment language
- hero now also carries a clearer brand-row layer between the kicker and headline
- hero first-screen rhythm is now stronger through larger title scale, roomier spacing, and more assertive CTA sizing
- hero now also includes a compact brand-grid layer that exposes fit / scenario / next-step metadata more directly
- hero title is now shorter and cleaner, reads more like a homepage claim, and the generic fallback path now stands more cleanly without a clumsy brand-prefix title
- contact and CTA now read more like a real demo/contact handoff instead of a generic closing form
- hero and CTA now also read more like a compact homepage claim plus first-step browse action, instead of a slightly longer explanation-led entrance, and the brand row now carries a shorter memory cue instead of a generic system label, while the three first-screen brand cards now read more like a sequenced entrance layer
- the mid-page sequence now also carries clearer proof bridges between product introduction, features, trust, and FAQ, so the center of the homepage reads more like one proof-and-decision path instead of loosely adjacent sections
- the strengthened runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteClosureLandingReview`

That latest sample confirms:

- clearer current handling-flow track (`CASE FLOW`, `当前处理流`)
- clearer section bridges between flow, ops, and history (`case-path-strip`)
- new visual bridge cards now connect flow, ops, and history (`case-bridge`, `NEXT BOARD`)
- the lower half now also bridges history into action cards and the active panel (`根据最近记录选择下一步动作`, `选择动作后会在这里展开当前说明`)
- the final section now also bridges the active panel into footer actions (`FINAL STEP`)
- the active panel now appears before service timeline and prep checklist, with a dedicated support bridge after it (`case-bridge--support`)
- footer now stays inside the after-sales route (`回到售后入口`)
- `为什么这类官网更容易把产品讲明白`
- `这尤其适合还在持续验证定位`
- `适合对象先讲透`
- `关键场景更容易代入`
- `先把产品价值讲明白`
- clearer hero brand-row / brand-mark entrance
- `定位清楚，演示更顺`
- `01 适合对象`
- `02 场景线索`
- `03 下一步动作`
- `先看是否相关`
- `先看问题是否成立`
- `先看怎么继续`
- `hero-copy-block`
- `hero-decision-block`
- `.landing-page:not(.personal-portfolio) .landing-hero h1::after`
- `.landing-page:not(.personal-portfolio) .hero-actions button:first-child::after`
- `.landing-page:not(.personal-portfolio) .hero-actions .ghost::after`
- stronger first-screen tension and CTA presence
- `faq-contact-bridge`
- `FAQ TO CONTACT`
- `带着当前判断进入预约演示 / 联系我们`
- `contact-entry-bridge`
- `FROM FAQ`
- FAQ now closes with a clearer bridge into contact, and contact now opens with a matching short intake-oriented entry cue
- `contact-intake-bridge`
- `DECISION TO INTAKE`
- `当前：带着判断进入`
- `下一步：发阶段 / 目标 / 动作`
- contact now also opens with a clearer decision-to-intake bridge, so the page no longer drops straight from FAQ judgment into raw intake fields
- the lower closing path now also carries a clearer intake-to-closure bridge, so the CTA section no longer drops straight from the form into generic capture copy
- the submitted-state closing path now also carries a clearer closure-to-landing bridge, so the CTA area no longer jumps straight from success language into the footer
- `cta-success-bridge`
- `POST SUBMIT`
- `已收到当前阶段与目标`
- `先看首页建议`
- `再决定是否继续推进`
- submitted contact state now also bridges back into the same CTA closing path
- `footer-success-bridge`
- `FINAL LANDING`
- `已进入后续沟通`
- `继续回看产品介绍 / 客户评价`
- submitted state now also lands more naturally into the footer instead of dropping straight into a generic ending
- `产品团队 / 创业团队`
- `定位澄清 / 价值承接`
- `FAQ / 演示 / 联系入口`
- `如果团队还在反复解释产品适合谁，官网最先应该讲清什么？`
- `产品还在持续迭代，这样的官网会不会很快过时？`
- `如果销售和演示还很依赖人工解释，这页实际能帮到什么？`
- `如果团队还在早期阶段、客户案例不多，这样的官网也值得先上线吗？`
- `定位澄清 / 首次访问承接`
- `销售前置 / 演示承接`
- `最稳的起点 usually 是：首页主张、产品介绍和 FAQ 用同一套判断逻辑。`
- `faq-scan-strip`
- `faq-summary-hint`
- `faq-copy-block`
- `faq-copy-label`
- `faq-followup-block`
- `faq-followup-label`
- `核心判断`
- `下一步建议`
- `上线准备`
- `预约演示 / 联系我们`
- `先看适用场景`
- `24 小时内回复`
- `定位 / FAQ / 演示承接可拆分讨论`
- `先对齐目标，再进入页面制作`
- `更适合：官网重写 / 首次上线 / 预约演示前置页`
- `contact-response-strip`
- `contact-handoff-grid`
- `contact-handoff-card`
- `contact-form-intake`
- `contact-form-checklist`
- `把这三项先发给我们，会更快进入建议阶段`
- `怎么称呼你`
- `联系邮箱`
- `想先讨论什么`
- `发送咨询信息`
- `contact-form-shell--business`
- `contact-form-panel`
- `contact-form-actions`
- `contact-submit-hint`
- `contact-field-hint`
- `已收到咨询`
- `contact-success-card`
- `contact-success-steps`
- `hero-memory-strip`
- `首页判断法`
- `先定对象`
- `再亮差异`
- `后接动作`
- `contact-form-note`
- `cta-note`
- `cta-capture-strip`
- `回复节奏`
- `讨论范围`
- `推进方式`
- clearer visual linkage between the brand-grid layer and the hero headline/subtitle block
- cleaner decision-band grouping between the hero rule-strip and CTA actions
- slightly clearer title lockup through a lightweight hero headline underline accent
- stronger primary-action emphasis through a clearer CTA treatment and forward cue
- calmer browse-secondary treatment through a quieter ghost button and browse-arrow cue
- secondary CTA now feels more like a true browse-next path than a competing half-primary action
- clearer below-the-fold section rhythm through:
  - `section-path-strip`
  - `01 产品介绍`
  - `02 产品能力`
  - `03 客户评价`
  - `04 常见问题`
  - `05 预约演示 / 联系我们`
  - explicit “下一步” cues between the main sections
- clearer ending-loop guidance through:
  - `cta-close-strip`
  - `01 发来当前阶段与目标`
  - `02 收到首页建议`
  - `03 再决定怎么推进`
- trust-card quote / role / result content
- `官网重写 / 销售前置页 / 首次访问承接`
- `早期产品 / 定位澄清 / 预约演示入口`
- `服务转化 / FAQ 承接 / 联系动作收口`
- stronger condensed heading treatment
- branded dark navigation pills
- stronger trust-card and FAQ edge accents
- `产品能力` single-page nav target now resolves to `#features`

Further ecommerce storefront quality work on 2026-03-21 and 2026-03-23 strengthened both the storefront shell and the default runtime behavior:

- the storefront surface now reads more like a coherent shopping frontend instead of floating components on a dark host background
- home and product detail now share a warmer storefront shell and clearer card framing
- the ecom homepage no longer renders a broken `售后` link when the generated profile is only `ecom_min`
- generated ecom storefront views now default to `API_SOURCE = ""`, so the frontend no longer proxies `/api/products` by default when no backend source exists
- generated checkout now defaults to `SUBMIT_API = ""` and keeps mock-order completion inside the storefront flow instead of hard-jumping to `/after-sales`
- checkout now has a clearer confirm-and-complete flow layer with:
  - `checkout-step-strip`
  - `FINAL CHECK`
  - `FINAL REVIEW`
- cart now has a denser pre-checkout surface with:
  - `结算准备`
  - `READY CHECK`
  - `summary-hint`
  - a stronger left-confirm / right-summary rhythm
- cart and checkout now also carry a clearer bridge between stages:
  - `下一步：确认地址与支付方式`
  - `CURRENT STEP`
  - `已承接购物车金额复核`
- checkout now also keeps a stronger storefront completion state with:
  - `ORDER STORED`
  - retained order id / status / payment chips
  - `继续浏览`
  - `清除摘要`
- product detail now also keeps a stronger add-feedback layer with:
  - `ITEM STORED`
  - `已加入购物车`
  - `去看购物车`
  - `继续去结算`
- product detail now also keeps a stronger purchase surface with:
  - `PRODUCT PICK`
  - `purchase-strip`
  - `cover-shell`
  - system-owned SVG mock product imagery instead of external placeholder dependencies
- homepage product cards now also keep a clearer continuity layer with:
  - `card-kicker`
  - `PRODUCT PICK`
  - `card-flow`
  - `先看详情`
  - `再决定是否加入购物车`
- the homepage itself now also keeps a stronger rhythm layer with:
  - `banner-flow`
  - `01 先逛热销`
  - `section-lead`
- the homepage now also keeps a clearer filter surface with:
  - `分类与快速筛选`
  - `CURRENT FILTER`
  - `可见商品`
  - `打开搜索结果页`
  - `filter-surface`
- the ecom discovery routes now also stay available in generated route truth with:
  - `/search`
  - `/category/:name`
  - `/shop/:id`
- search and category pages now also keep the same storefront browsing language with:
  - `SEARCH RESULT`
  - `CURRENT FILTER`
  - `QUICK NARROW`
  - `CATEGORY VIEW`
  - `SORT RULE`
  - `RESULT COUNT`
  - `CURRENT CATEGORY`
- the strengthened runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/EcomDiscoveryShopBoardReview`

That latest sample confirms:

- `新季精选上架`
- `满 199 包邮`
- `48 小时内发货`
- `7 天无忧售后`
- `热销商品`
- `推荐商品`
- `店铺精选区`
- no broken `/after-sales` homepage entry for `ecom_min`
- `API_SOURCE = ""`
- `SUBMIT_API = ""`
- checkout stays inside the storefront flow instead of hard-jumping to `/after-sales`
- checkout now reads more like a confirm-and-complete purchase page
- cart now reads more like a real pre-checkout storefront page
- cart and checkout now read more like connected stages of one purchase flow
- checkout now also reads more like a retained in-storefront completion page after submission
- product detail now reads more like a real storefront detail page after add-to-cart instead of silently mutating cart state
- cart now keeps DISCOVERY MEMORY from search/category entry instead of only remembering product/shop handoff
- checkout now keeps that same DISCOVERY MEMORY layer and return-to-search/category action through final confirmation
- a real search -> shop -> product -> cart -> checkout -> completion flow now keeps q/category/discovery visible all the way into the retained completion state
- product detail now also reads more like a stable storefront purchase surface instead of depending on flaky external imagery
- homepage product cards now also read more like the first step of the same purchase language used on product detail
- the homepage itself now also gives a clearer read path from hero to products to shops instead of behaving like a flat storefront grid
- the homepage now also reads more like a real storefront filtering surface between search, category narrowing, visible product counts, and product sections
- search and category pages now also read more like the same storefront browsing system instead of disconnected utility screens
- the shop page now also reads more like the same storefront browsing system instead of a disconnected store stub
- search/category now also surface a clearer pre-shop decision layer before the product grid, so store entry feels more intentional instead of being buried inside the card list
- latest runtime proof set now also includes the homepage filtering surface, so the front-half browse chain is evidenced as `/ -> search/category -> shop` instead of only from search/category onward
- search/category entry into the shop page now also keeps clearer discovery continuity with:
  - `DISCOVERY CONTINUITY`
  - `来自分类浏览：女装`
  - `回到分类页`
  - `来自搜索结果：短袖 / 女装`
  - `回到搜索结果`
- product detail now also keeps clearer in-shop continuity with:
  - `SHOP CONTINUITY`
  - `回到店内继续看`
  - `同店继续看`
- product detail now also keeps clearer discovery-memory continuity with:
  - `DISCOVERY MEMORY`
  - `来自搜索结果：短袖 / 女装`
  - `回到搜索结果`
  - a product URL that still keeps `q`, `category`, and `discovery=search` after entering from the shop page
  - direct search/category entry into product detail now also keeps `discovery=search|category` instead of dropping discovery context unless users enter through the shop page first
  - latest runtime review also confirmed direct `product` URLs with `discovery=search` and `discovery=category` keep that same continuity live in delivery output
- shop and product now also share a clearer in-store browse-to-buy rhythm with:
  - `01 先定店铺`
  - `02 再看店内商品`
  - `03 最后进详情`
  - `01 店内继续看`
  - `02 复核价格与规格`
  - `03 决定下一步`
- product and cart now also share a clearer purchase-decision bridge with:
  - `PRODUCT HANDOFF`
  - `01 详情已确认`
  - `02 购物车统一比对`
  - `03 带着来源去结算`
  - a checkout CTA that keeps the same `from=product` source path alive
- cart and checkout now also share a clearer final-confirm bridge with:
  - `CHECKOUT HANDOFF`
  - `01 购物车已复核`
  - `02 最后确认地址与支付`
  - `03 提交后保留摘要`
  - a summary hint that keeps the previous cart-review context visible into final confirm
- product detail now also keeps a clearer purchase-decision layer with:
  - `CURRENT PICK`
  - `PRICE CHECK`
  - `NEXT MOVE`
- product detail now also keeps a fuller media-side and related-picks layer with:
  - `STYLE VIEW`
  - `SHOP SIGNAL`
  - `NEXT PICKS`
  - `CONTINUE PICK`
- search/category now also keep a clearer shared browse-language layer with:
  - `01 先搜关键词`
  - `01 先看分类`
  - `CONTINUE PICK`
  - `SHOP SNAPSHOT`
  - `STORE DIRECTION`
  - `带着结果进店`
  - `带着分类进店`
- search/category low-result pages now also hold a fuller result-card layout instead of collapsing into narrow left-column cards
- cart now also keeps clearer product-origin continuity with:
  - `PRODUCT HANDOFF`
  - `来自 橙选服饰`
  - `回到商品详情`
  - `回到店内`
- checkout now also keeps clearer product-origin continuity with:
  - `CHECKOUT HANDOFF`
  - `来自 橙选服饰`
  - `回到商品详情`
  - `回到店内`
  - `已承接详情页与购物车复核`
- checkout completion now also keeps a clearer purchase-to-return bridge with:
  - `RETURN AXIS`
  - `01 收住购买主轴`
  - `02 带着来源继续逛`
  - `03 保留订单摘要`
  - purchase closure, retained order summary, and continue-browsing routes now read more like one continuous post-submit path
  - latest runtime check confirmed this return-axis layer after a real product -> cart -> checkout -> submit flow
- the retained checkout completion state now also keeps clearer product-origin continuity with:
  - `ORDER STORED`
  - `CHECKOUT HANDOFF`
  - `来自 橙选服饰`
  - `回到商品详情`
  - `回到店内`
- the retained checkout completion state now also keeps clearer return-to-browsing continuity with:
  - `CONTINUE BROWSING`
  - `回到店内继续看`
  - `继续看同类商品`
  - `回到首页热销区`
  - `01 保留来源`
  - `02 回到继续逛的路径`
  - `03 保留订单摘要`
  - `这笔订单仍然记得来自 橙选服饰`
  - `先回到 女装 分类，再决定要不要回到店内继续看。`

Further after-sales quality work on 2026-03-22 strengthened the runtime result from a minimal support-entry page into a more complete service-center surface, then into an early handling-flow page, and now into a clearer in-progress handling surface with a recent-updates / case-history layer:

- the after-sales page now opens with a clearer service-center hero instead of only a title and intro line
- it now exposes visible service context blocks for:
  - response timing
  - progress visibility
  - contact routes
- the order area now reads more like a current-order context section with:
  - order id
  - order amount
  - item summary
  - recommended next step
- the main action area now reads more like service routing:
  - refund
  - exchange
  - support
  - escalation
- the page now also renders a clearer service timeline instead of stopping at action cards
- the page now also renders:
  - a current case-status layer
  - a pre-submit preparation checklist
- the strengthened runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesSupportBridgeReview`

That latest sample confirms:

- `售后服务中心`
- `响应时效`
- `进度可见`
- `联系渠道`
- `ORDER CONTEXT`
- `当前订单`
- `推荐动作`
- `退款申请`
- `换货申请`
- `联系客服`
- `投诉与升级`
- `处理节奏`
- `当前处理状态`
- `提交前准备`
- `CASE OPS`
- `当前跟进信息`
- `最新进展`
- `下一步动作`
- `当前责任归属`
- `建议准备材料`

After-sales runtime work on 2026-03-27 also strengthened the action-selection state itself:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesSelectionReview`
- the chosen action card now renders a clearer selected state with:
  - `card-selected`
  - `card-selected-badge`
  - `当前已选`
  - `查看当前说明`
- after clicking `立即申请`, the page now reads more clearly as:
  - choose action
  - confirm current path
  - read current instructions
  - continue into timeline and checklist

After-sales runtime work on 2026-03-28 also strengthened the no-order default entry state:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesIntakeReview`
- the default `/after-sales` entry now renders a clearer intake layer with:
  - `CASE INTAKE`
  - `先补这三项，再进入售后动作`
  - `当前：准备 intake`
  - `下一步：选择售后动作`
- this means the route now reads more like:
  - arrive without order context
  - understand what to prepare
  - choose the right action path
  - then continue into the existing case-flow boards

After-sales runtime work on 2026-03-28 also made the two entry modes easier to distinguish:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesModeReview`
- the page now uses a clearer mode split between:
  - `ENTRY MODE` for the default no-order intake route
  - `CASE MODE` for the order-carried tracked-case route
- this means users can now tell more quickly whether they are:
  - still preparing intake
  - or already inside a tracked handling path

After-sales runtime work on 2026-03-28 also strengthened the tracked-case route itself:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesCaseBoardReview`
- once an order is carried in, the page now also renders a clearer tracked-case snapshot with:
  - `CASE SNAPSHOT`
  - `当前节点`
  - `当前负责人`
  - `处理时效`
- this means the order-carried route now reads more like:
  - current case node
  - current owner
  - handling SLA
  - next move

After-sales runtime work on 2026-03-28 also tightened the tracked-case board axis:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesBoardSummaryReview`
- the tracked route now also inserts:
  - `CASE BOARD`
  - `带着当前快照继续看状态与处理流`
  - `当前：状态层`
  - `下一步：查看处理流`
- this means the order-carried route now reads more like:
  - CASE SNAPSHOT
  - CASE STATUS
  - CASE FLOW
  as one continuous case-board axis instead of one snapshot box followed by two looser boards

After-sales runtime work on 2026-03-28 also tightened the tracked-case board summary itself:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesBoardSummaryReview`
- the tracked route now also inserts:
  - `BOARD SUMMARY`
  - `负责人：`
  - `当前焦点：`
  - `下一步：`
  - `tracked-board-strip`
- this means the order-carried route now also aligns:
  - current owner
  - current focus
  - next move
  before the user continues into CASE STATUS and CASE FLOW

After-sales runtime work on 2026-03-28 also tightened the middle handling axis:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesFlowOpsStripReview`
- the tracked route now also inserts:
  - `STATUS TO FLOW`
  - `先把当前状态和处理轨道对齐，再进入跟进摘要`
  - `带着状态层和处理轨道进入跟进摘要`
- this means the order-carried route now reads more like:
  - CASE STATUS
  - CASE FLOW
  - CASE OPS
  as one clearer handling axis instead of three sequential but looser boards

After-sales generator work on 2026-03-28 also tightened the flow-to-ops continuity strip:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesOpsHistoryStripReview`
- the tracked route now also inserts:
  - `flow-ops-strip`
  - `当前负责人：`
  - `处理时效：`
  - `跟进焦点：`
- this means the order-carried route now keeps:
  - owner
  - SLA
  - current focus
  visible between CASE FLOW and CASE OPS instead of dropping straight from the flow board into the ops board

After-sales generator work on 2026-03-28 also tightened the ops-to-history continuity strip:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesOpsHistoryStripReview`
- the tracked route now also inserts:
  - `ops-history-strip`
  - `最新进展：`
  - `当前负责人：`
  - `下一步记录：`
- this means the order-carried route now keeps:
  - latest update
  - current owner
  - next record hint
  visible before CASE HISTORY instead of dropping straight from the ops board into the history list

After-sales generator work on 2026-03-28 also tightened the history-to-actions continuity strip:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesActionEntryReview`
- the tracked route now also inserts:
  - `action-entry-strip`
  - `记录锚点：`
  - `当前建议：`
  - `接下来：`
- this means the order-carried route now keeps:
  - record anchor
  - current suggestion
  - next step
  visible before the action cards instead of dropping straight from CASE HISTORY into raw action choice

After-sales generator work on 2026-03-28 also tightened the actions-to-panel continuity strip:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesActionPanelReview`
- the tracked route now also inserts:
  - `action-panel-strip`
  - `当前动作：`
  - `当前建议：`
  - `接下来：`
- this means the order-carried route now keeps:
  - chosen action
  - current suggestion
  - next step
  visible before the active instructions instead of dropping straight from action selection into the panel

After-sales generator work on 2026-03-28 also tightened the panel-to-support continuity strip:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesPanelSupportReview`
- the tracked route now also inserts:
  - `panel-support-strip`
  - `当前说明：`
  - `处理时效：`
  - `接下来：`
- this means the order-carried route now keeps:
  - current instruction
  - current SLA
  - next step
  visible before the timeline and prep boards instead of dropping straight from the active panel into downstream guidance

After-sales generator work on 2026-03-28 also tightened the support-to-footer continuity strip:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesFooterClosureReview`
- the tracked route now also inserts:
  - `support-footer-strip`
  - `当前准备：`
  - `当前负责人：`
  - `接下来：`
- this means the order-carried route now keeps:
  - current preparation
  - current owner
  - next move
  visible before the final footer actions instead of dropping straight from the support boards into raw navigation

After-sales runtime work on 2026-03-28 also tightened the lower handling axis:

- the latest runtime-backed sample is:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesOpsAxisReview`
- the tracked route now also inserts:
  - `OPS TO HISTORY`
  - `先把当前跟进和最近记录对照，再决定具体动作`
  - `HISTORY TO ACTIONS`
  - `带着当前跟进和最近记录进入具体动作`
  - `当前：动作选择`
  - `下一步：查看当前说明`
- this means the order-carried route now reads more like:
  - CASE OPS
  - CASE HISTORY
  - actions
  as one clearer lower-half handling axis instead of three sequential but looser sections



Company/product runtime work on 2026-03-30 also confirmed the lower closure path in a real submit flow:

- runtime proof image:
  - `/Users/carwynmac/ai-cl/output/playwright/company_closure_landing_runtime.png`
- the current company baseline now also has runtime-confirmed:
  - `POST SUBMIT`
  - `CLOSURE TO LANDING`
  - `FINAL LANDING`
- this means the company closing path is no longer only generated structure; it has runtime evidence after a real contact submission flow

Current short review anchors as of 2026-03-30:

- `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260402.md`
- `/Users/carwynmac/ai-cl/WEBSITE_PRIORITY_REVIEW_20260402.md`


After-sales runtime proof on 2026-03-30 also reconfirmed the current final baseline in delivery-state output:

- intake runtime proof image:
  - `/Users/carwynmac/ai-cl/output/playwright/after_sales_footer_closure_intake_runtime.png`
- tracked runtime proof image:
  - `/Users/carwynmac/ai-cl/output/playwright/after_sales_footer_closure_tracked_runtime.png`
- the latest runtime pass reconfirmed:
  - `ENTRY MODE`
  - `CASE INTAKE`
  - `CASE MODE`
  - `CASE SNAPSHOT`
  - `CASE BOARD`
  - `当前已选`
  - `查看当前说明`
  - `panel-support-strip`
  - `support-footer-strip`
- this means the current after-sales baseline is no longer only generator-backed; both entry-mode separation and the lower-half handling closure now also have fresh runtime evidence


Current milestone anchor as of 2026-04-03:

- `/Users/carwynmac/ai-cl/WEBSITE_PHASE_MILESTONE_20260403.md`

- `/Users/carwynmac/ai-cl/WEBSITE_PHASE_CLOSEOUT_20260403.md`

Managed / unmanaged hook discoverability work on 2026-04-02 also strengthened the current customization frontier:

- reference anchor:
  - `/Users/carwynmac/ai-cl/MANAGED_UNMANAGED_PHASE3_HOOK_CATALOG_20260402.md`
- generated projects now also emit:
  - `.ail/hook_catalog.md`
  - `.ail/hook_catalog.json`
- this means operators and users can now discover page / section / slot hook names and available `context.runtime` fields without reading managed Vue files directly



Company/product visual rhythm work on 2026-03-31 also strengthened the current company baseline:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandSignatureReview`
- runtime proof image:
  - `/Users/carwynmac/ai-cl/output/playwright/company_brand_stage_review_runtime.png`
- the current company line now also differentiates:
  - about
  - features
  - trust
  - FAQ
  - contact
  - closure
  more clearly through section-tone shifts and proof-bridge accents
- this means the company homepage now reads less like one repeated blue system and more like a staged product-site brand path while keeping the existing proof / intake / closure structure intact


Company/product signature work on 2026-03-31 also strengthened the current company baseline:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandSignatureReview`
- runtime proof image:
  - `/Users/carwynmac/ai-cl/output/playwright/company_brand_signature_review_runtime.png`
- the current company line now also gives:
  - header
  - hero
  - footer
  a slightly stronger shared signature through branded rail accents and clearer top/bottom framing
- this means the company homepage now feels more like a branded entry-and-landing surface while keeping the stronger staged proof / intake / closure path intact

Company/product brand-posture work on 2026-04-02 strengthened the current company baseline again:

- the latest generated sample is:
  - `/Users/carwynmac/ai-cl/output_projects/CompanyProductSiteBrandPostureReview`
- runtime proof image:
  - `/Users/carwynmac/ai-cl/output/playwright/company_brand_posture_review_runtime.png`
- the current company line now also gives:
  - header
  - hero
  - footer
  a clearer shared point of view through:
  - a short header brand-note strip
  - a dedicated `BRAND POSTURE` block in the hero
  - a `FINAL BRAND LINE` signoff strip in the footer
- this means the company homepage now feels less like a safe branded shell and more like a team with a recognisable explanation posture, while still keeping the stronger proof / intake / closure path intact


Managed / unmanaged frontend boundary work on 2026-03-31 shipped a first real implementation step:

- reference anchor:
  - `/Users/carwynmac/ai-cl/MANAGED_UNMANAGED_PHASE1_20260331.md`
- generated frontend projects now scaffold:
  - `frontend/src/ail-managed/`
  - `frontend/src/ail-overrides/`
  - `frontend/public/ail-overrides/`
- the stable entry path now imports:
  - `frontend/src/ail-overrides/theme.tokens.css`
  - `frontend/src/ail-overrides/custom.css`
- rebuild validation also confirmed that a user marker placed in:
  - `frontend/src/ail-overrides/theme.tokens.css`
  survives a second rebuild
- local rebuild validation also confirmed that a user marker placed in:
  - `frontend/src/ail-managed/views/Home.vue`
  is backed up before the rebuild replaces it
- local rebuild protection now writes:
  - `.ail/local_rebuild_backups/<timestamp>/summary.md`
- sync conflict protection now also writes:
  - `.ail/conflicts/<build_id>/summary.md`

This means AIL still owns the structural source of truth, but generated frontend projects now have a clearer durable customization zone instead of forcing all edits into generated views.

Managed / unmanaged frontend boundary work on 2026-03-31 now also has a real phase-2 hook path:

- reference anchor:
  - `/Users/carwynmac/ai-cl/MANAGED_UNMANAGED_PHASE2_COMPONENT_HOOKS_20260331.md`
- generated frontend projects now also ship:
  - `frontend/src/ail-managed/system/AILSlotHost.vue`
- unmanaged hook files now belong in:
  - `frontend/src/ail-overrides/components/`
- generated pages now expose stable page-level hooks:
  - `page.<page-key>.before`
  - `page.<page-key>.after`
- generated pages now also expose the first shipped section-level hooks for:
  - landing / homepage sections
  - after-sales tracked-case sections
  - ecom discovery / purchase sections
- generated pages now also expose the first shipped slot-level hooks for:
  - landing / company-homepage subareas
  - ecom product purchase subareas
  - ecom checkout completion / followup subareas
  - after-sales tracked-case subareas
- those page-level and section-level hooks now also carry lightweight context:
  - `pageKey`
  - `pageName`
  - `pagePath`
  - `profiles`
  - `hookScope`
  - `sectionKey` for section hooks
- selected landing and after-sales hooks now also carry `context.runtime` summaries for:
  - landing / homepage-style pages
  - after-sales tracked-case pages
- selected ecom hooks now also carry `context.runtime` summaries for:
  - search
  - category
  - shop
  - product
  - cart
  - checkout
- Vue hook components now receive:
  - `context`
  - `hookName`
- HTML partial hooks now also receive wrapper attributes:
  - `data-ail-hook`
  - `data-ail-context`
- validation sample:
  - `/Users/carwynmac/ai-cl/output_projects/ManagedHookSmoke`
- section-hook validation samples:
  - `/Users/carwynmac/ai-cl/output_projects/SectionHookLandingSmoke`
  - `/Users/carwynmac/ai-cl/output_projects/SectionHookAfterSalesSmoke`
- ecom section-hook validation sample:
  - `/Users/carwynmac/ai-cl/output_projects/EcomSectionHookReview`
- ecom runtime-context validation sample:
  - `/Users/carwynmac/ai-cl/output_projects/EcomRuntimeContextReview`
- ecom child-slot validation sample:
  - `/Users/carwynmac/ai-cl/output_projects/EcomChildSlotReview`
- after-sales child-slot validation sample:
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesChildSlotReview`
- landing child-slot validation sample:
  - `/Users/carwynmac/ai-cl/output_projects/LandingChildSlotReview`
- context-hook validation samples:
  - `/Users/carwynmac/ai-cl/output_projects/ContextHookSmoke`
  - `/Users/carwynmac/ai-cl/output_projects/ContextAfterSalesSmoke`
- landing / after-sales runtime-context validation samples:
  - `/Users/carwynmac/ai-cl/output_projects/LandingRuntimeContextReview`
  - `/Users/carwynmac/ai-cl/output_projects/AfterSalesRuntimeContextReview`
- validation confirmed that:
  - a user-added `page.home.before.vue`
  - and `page.home.after.html`
  survived rebuild and the sample still completed `npm run build`
- landing and after-sales section-hook samples also completed `npm run build`
- the ecom section-hook sample also completed `npm run build`
- the ecom runtime-context sample also completed `npm run build`
- the ecom child-slot sample also completed `npm run build`
- the after-sales child-slot sample also completed `npm run build`
- the landing child-slot sample also completed `npm run build`
- landing and after-sales context-hook samples also completed `npm run build`
- landing and after-sales runtime-context samples also completed `npm run build`

This means AIL now has a more sustainable frontend customization path than raw CSS overrides alone: users can keep durable theme tokens, durable custom CSS, and durable hook components with lightweight page/section/selected-slot context plus selected landing, after-sales, and ecom runtime summaries across landing, after-sales, and the first ecom discovery / purchase surfaces, without editing managed views directly.
