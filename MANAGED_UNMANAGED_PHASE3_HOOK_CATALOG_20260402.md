# Managed / Unmanaged Phase 3 Hook Catalog 2026-04-02

## Purpose

This document captures the next practical step of the managed / unmanaged frontend boundary:

- generated projects now emit a hook inventory automatically
- users no longer need to guess which page / section / slot hooks exist
- the hook inventory also shows the lightweight context/runtime fields available at each hook scope

Short operator companion:

- `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_OPERATOR_CHEAT_SHEET_20260406.md`

Normalization note as of 2026-04-08:

- treat this document as phase-history and capability detail
- use `/Users/carwynmac/ai-cl/CUSTOMIZATION_UX_OPERATOR_CHEAT_SHEET_20260406.md` for day-to-day commands
- use `/Users/carwynmac/ai-cl/PROJECT_STATE_REVIEW_20260408.md` for current completion and priority judgment

## Current Phase-3 Behavior

Generated projects now also write:

- `.ail/hook_catalog.json`
- `.ail/hook_catalog.md`

These files are generated on rebuild and act as the project-local hook inventory.

## What The Hook Catalog Contains

For each generated page, the catalog now lists:

- `pageKey`
- `pageName`
- `pagePath`
- available page hooks
- available section hooks
- available slot hooks
- page / section / slot context fields
- currently available `context.runtime` fields

This means a user can now answer:

- which hook names actually exist in this project
- which section keys and slot keys are usable
- whether a given page exposes runtime summaries at all
- what data a durable override component can rely on before opening generated views

## Why This Matters

Phase 1 made durable override folders real.
Phase 2 made hooks real.
Phase 3 makes hooks discoverable.

That is a meaningful productization step because the system no longer depends on users reverse-engineering generated page files to find insertion points.

## Verified Outcome

Reference validation sample:

- `/Users/carwynmac/ai-cl/output_projects/HookCatalogSmoke`

Verified generated files:

- `/Users/carwynmac/ai-cl/output_projects/HookCatalogSmoke/.ail/hook_catalog.md`
- `/Users/carwynmac/ai-cl/output_projects/HookCatalogSmoke/.ail/hook_catalog.json`

Verified content characteristics:

- page-level hooks are listed
- section-level hooks are listed
- slot-level hooks are listed
- `context.runtime` keys are listed when present
- landing/company homepage hook coverage is visible without reading managed Vue files

## Current Truth

The durable customization path is now easier to use in practice:

- structure/content still belongs in `.ail/source.ail`
- theme still belongs in `frontend/src/ail-overrides/theme.tokens.css`
- local CSS still belongs in `frontend/src/ail-overrides/custom.css`
- durable Vue/HTML inserts still belong in `frontend/src/ail-overrides/components/**`
- and the current hook surface can now be discovered from `.ail/hook_catalog.md`

## CLI Entry

The hook catalog is now also exposed through the CLI:

- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hooks --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hooks home --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hooks --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home --suggest --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home --suggest --page-key home --section-key hero --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home --suggest --page-key home --section-key hero --slot-key hero-actions --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --suggest --pick --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home --suggest --page-key home --section-key hero --slot-key hero-actions --pick-index 2 --json`
- `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init --open-catalog --json`

This means users can now:

- inspect the whole hook surface without opening managed Vue files
- filter by one page key such as `home`, `product`, or `checkout`
- discover the generated catalog paths directly from `project summary`
- aggregate generated hook catalogs across `/Users/carwynmac/ai-cl/output_projects/*` from one workspace-level entry
- scaffold one live override file directly from a starter example without manually copying files around
- use shorthand hook names like `home.before` or `home.section.hero.after`
- let the helper auto-pick `vue` vs `html` when `--template auto` is left at the default
- ask the CLI for matching hook suggestions before choosing one
- see those suggestions with stable numbering that matches `--pick-index`
- see page / section / slot metadata and a ready-to-copy `--pick-index` command beside each suggestion
- get a top-level recommended next command in broader multi-suggestion cases
- narrow those suggestions to one page or one section when the hook surface is already large
- narrow them one step further to one slot key when section-level suggestions are still too broad
- immediately scaffold a live hook when suggestion mode has already narrowed to one safe target
- scaffold one numbered suggestion directly when a filtered suggestion list is still larger than one item
- jump straight to the current project catalog paths from the same helper entrypoint

## Starter Override Examples

Generated frontend projects now also include starter override examples under:

- `frontend/src/ail-overrides/components/examples/README.md`
- `frontend/src/ail-overrides/components/examples/page.home.before.example.vue`
- `frontend/src/ail-overrides/components/examples/page.home.section.hero.after.example.html`

These files are intentionally non-active:

- `.example.vue` and `.example.html` do not match live hook names
- users can copy one file into `frontend/src/ail-overrides/components/`
- then rename it to a real hook such as `page.home.before.vue`

This means a new project now gives the user:

- hook inventory
- context/runtime visibility
- one Vue example
- one HTML partial example

without forcing any demo block into the live page by default

## Validation Notes

The new CLI entry was verified against:

- `/Users/carwynmac/ai-cl/output_projects/HookCatalogSmoke`

Confirmed behavior:

- `project hooks --json` returns catalog counts and available page keys
- `project hooks home --json` returns the selected page plus its page/section/slot hooks
- `project hooks` now also returns one recommended `project hook-init ... --suggest ...` command based on the current or selected page key
- `project summary --json` now includes a `hook_catalog` summary block
- `workspace hooks --json` returns workspace-level project counts plus per-project hook catalog summaries
- `workspace hooks --json` now also returns one recommended project plus one recommended `project hook-init ... --suggest ...` command so users can jump from workspace-wide hook discovery into one concrete project-level customization path
- `workspace hooks --json` and `workspace summary --json` now also return repo-root `workspace hook-init ...` recommendations, so users can stay at the workspace root while starting the same durable-hook flow
- `workspace hook-init ... --project-name <name> --json` now lets users scaffold one live hook file directly from the repo root without manually `cd`-ing into the target project first
- `workspace hook-init --use-recommended-project ... --json` now makes the repo-root recommended-project path explicit when users want that auto-selection to be visible and intentional
- `workspace hook-init --use-recommended-project --suggest --json` and `workspace hook-init --use-recommended-project --pick-recommended --json` now auto-seed the selected project's recommended page key when no hook name or filters were given, so the repo-root recommended path starts from one focused page rather than the whole catalog
- those workspace-level recommended routes now also return one workspace-native `recommended_next_command`, so text-mode users can keep following the repo-root path without rewriting a project-level suggestion by hand
- `workspace hook-init --follow-recommended --json` now acts as the shortest repo-root one-step path: it picks the current recommended workspace project, seeds the recommended page query, and scaffolds the first recommended live hook without asking the user to restate project or page filters
- `workspace hook-init --use-last-project --suggest --json` and `workspace hook-init --use-last-project --pick-recommended --json` now reuse a repo-root memory file under `/Users/carwynmac/ai-cl/.workspace_ail/last_workspace_hook_init.json`, so returning users can keep working in the most recent workspace hook project without retyping `--project-name`
- when that last-used workspace project also has `/.ail/last_hook_suggestions.json`, the repo-root `--use-last-project` path now prefers the remembered page/section/slot query instead of falling back to the first page key, so customization can continue from the user's most recent narrowed hook surface
- `workspace hooks` and `workspace summary` now expose one `preferred_workspace_hook_command` and `preferred_workspace_hook_reason`, so the text-mode and JSON summaries can clearly tell users whether they should continue from the recent-project path or jump to the current recommended one-step path
- `workspace hook-continue --json` now wraps that same decision tree into one repo-root action name: it prefers the recent-project path when recent memory exists, and otherwise falls back to the current `--follow-recommended` shortcut
- `workspace hook-continue` now also explains the selected path, the alternate path, and the most useful next command in both text and JSON output, so repo-root users can keep moving without decoding the delegated project-level result by hand
- when repo-root recent workspace memory includes a narrowed page/section/slot surface, `workspace hook-continue` now carries that exact remembered surface forward as well, so continuing work is closer to “resume the last hook area” than merely “resume the last project”
- `workspace hook-continue --broaden-to section|page --json` now gives repo-root users one explicit way to back out from the last remembered slot-level surface before continuing, so the “resume work” path can also intentionally widen back to one section or one page
- `workspace hook-continue --broaden-to auto --json` now tries the exact remembered surface first and automatically falls back to section, then page, when that narrower path is blocked, so repo-root continuation can recover without forcing the user to reason through each fallback manually
- `workspace hook-continue --dry-run --json` now previews that same continue decision tree and the target live hook path without writing any override file, so users can inspect the next move before committing to it
- `workspace hook-continue --dry-run --inspect-target --json` now inspects both the resolved target hook file path and its parent overrides directory, so repo-root users can preview whether that exact target already exists and what sits beside it before they confirm the write
- `workspace hook-continue --dry-run --open-target --json` now returns a direct open-target payload plus one `inspect <target_path>` command for that resolved hook file, so repo-root users can jump from the continue preview straight into the target file without reconstructing the path by hand
- `workspace hook-continue --dry-run --open-now --json` now inspects that same resolved target hook file inline and returns the inspection payload directly, so repo-root users can preview the file state in one step without leaving the current continue payload
- `workspace hook-continue --dry-run --open-now --text-compact` now trims that inline file inspection down to target path, existence, and line count, so operators can scan the exact file state in a few lines
- when that target file already exists, the compact open-now view now also prints one short `open_now_preview` line, so repo-root users can recognize the current file contents at a glance without opening the fuller JSON payload
- `workspace hook-continue --dry-run --inspect-target --text-compact` now also prints a short parent-directory summary and a small `nearby_entries` list, so shell-first operators can quickly judge the local hook neighborhood without opening the fuller JSON inspection payload
- that dry-run preview now also includes a short summary, a target-selection reason, and one explicit confirm command to rerun without `--dry-run`, so the repo-root preview path is easier to read and act on in text mode
- `workspace hook-continue --dry-run --text-compact` now trims that preview down to a short operator-oriented text view, so users who already trust the flow can scan the target and confirm command without reading the full field list
- `workspace hook-continue --dry-run --explain` now prints a structured strategy/memory/resolution/target/followup explanation, so users who want to understand the decision tree can read it in text mode without opening the JSON payload
- `workspace hook-continue --dry-run --emit-shell` now prints only the single best next command, so repo-root operators can pipe or copy the follow-up step without parsing the fuller preview output
- `workspace hook-continue --dry-run --emit-confirm-shell` now prints only the most relevant confirm command for the current continue mode, so repo-root operators can jump straight to the confirmation step without reconstructing it from the fuller preview payload
- `workspace hook-continue --dry-run --emit-target-path` now prints only the resolved hook file path itself, so repo-root users can hand that exact path to other tools without first stripping it back out of an `inspect ...` command
- `workspace hook-continue --dry-run --emit-target-dir` now prints the parent overrides directory of that resolved hook file, so repo-root users can hand the whole hook workspace directory to other tools when file-level precision is not necessary
- `workspace hook-continue --dry-run --emit-target-project-root` now prints the generated project root that owns that resolved hook file, so repo-root users can jump straight into the project that contains the current durable hook target
- `workspace hook-continue --dry-run --emit-target-project-name` now prints the generated project folder name that owns that resolved hook file, so repo-root users can reference the target project in shorter handoff notes or command templates without carrying the full absolute path
- `workspace hook-continue --dry-run --emit-target-relative-path` now prints the resolved hook file path relative to that generated project root, so repo-root users can hand a shorter project-local path to docs, scripts, or teammates without losing the exact hook location
- `workspace hook-continue --dry-run --emit-target-bundle` now prints one compact JSON bundle containing the resolved hook file path, parent directory, project root, project name, project-relative path, open command, and confirm command, so repo-root users can hand one reusable target payload to scripts or other operators
- `workspace hook-continue --dry-run --emit-open-shell` now prints only the direct `inspect <target_path>` command for the resolved hook file, so repo-root operators can jump straight into the target file without reconstructing the path from the fuller preview payload
- `workspace hook-continue --dry-run --copy-open-command` now copies that same resolved `inspect <target_path>` command into the macOS clipboard, so repo-root operators can jump from preview to opening the target file without manual copy/paste
- `workspace hook-continue --copy-confirm-command` now copies the most relevant confirm command for the current continue mode, so repo-root users can move from preview or staged execution into the actual confirm step without reconstructing or retyping that command
- `workspace hook-continue --dry-run --copy-target-path` now copies that same resolved hook file path into the macOS clipboard, so repo-root users can paste the raw path directly into editors, scripts, or other shell helpers
- `workspace hook-continue --dry-run --copy-target-dir` now copies the parent overrides directory of that resolved hook file into the macOS clipboard, so repo-root users can paste the working hook directory directly into editors, shells, or file-open dialogs
- `workspace hook-continue --dry-run --copy-target-project-root` now copies the generated project root that owns the resolved hook file into the macOS clipboard, so repo-root users can jump straight into the right generated project without reconstructing it from the hook path
- `workspace hook-continue --dry-run --copy-target-project-name` now copies the generated project folder name that owns the resolved hook file into the macOS clipboard, so repo-root users can paste a shorter project identifier directly into notes, commands, or handoff tools
- `workspace hook-continue --dry-run --copy-target-relative-path` now copies the resolved hook file path relative to the generated project root into the macOS clipboard, so repo-root users can paste a shorter project-local hook path directly into notes, scripts, or handoff tools
- `workspace hook-continue --dry-run --copy-target-bundle` now copies that same seven-field JSON bundle into the macOS clipboard, so repo-root users can paste one reusable target payload directly into scripts, notes, or handoff tools
- `workspace hook-continue --dry-run --run-open-command --json` now stages that same resolved open-target inspection step behind an explicit confirmation boundary, and `--yes` executes the target inspection inline and returns the inspection payload, so repo-root users can turn the preview into a one-step file inspection without leaving the continue surface
- `workspace hook-continue --dry-run --copy-command` now copies that same best next command into the macOS clipboard, so shell-first operators can jump from preview to execution without manual copy/paste
- `workspace hook-continue --dry-run --run-command --json` now stages that same best next command behind an explicit confirmation step, and `--yes` executes it and returns the nested JSON result, so repo-root users can turn a preview into a one-step continue action without losing the safety of a visible confirmation boundary
- `workspace hook-continue` now also prints explicit repo-root next commands for exact, section, page, and auto-broaden follow-ups, so text-mode users can keep steering the continue path without reconstructing those commands by hand
- `workspace hook-continue` now also marks one `preferred_followup_command` plus a short reason, so the text-mode continue flow does not just list options but also surfaces the most sensible default next step
- `workspace summary --json` now includes a compact `hook_catalogs` aggregate block
- `project hook-init home.before --json` normalizes to `page.home.before` and copies the Vue starter example into a live hook file
- `project hook-guide --json` now returns one short current-project hook workflow guide with recommended catalog, suggest, dry-run, and explain commands
- `project hook-guide --emit-shell` now prints the preferred current-project next command from that guide, and `--copy-command` copies it to the macOS clipboard
- `project hook-guide --run-command` now stages that preferred current-project next command behind an explicit confirmation boundary, and `--run-command --yes` executes it and returns the nested result inline
- `project hook-init home.section.hero.after --json` normalizes to `page.home.section.hero.after` and auto-selects the HTML starter example
- `project hook-init home --suggest --json` returns matching page/section/slot hook suggestions plus default template hints
- `project hook-init home --suggest --page-key home --section-key hero --json` narrows the suggestions to the `home` page and `hero` section
- `project hook-init home --suggest --page-key home --section-key hero --slot-key hero-actions --json` narrows the suggestions all the way down to the `hero-actions` child slot
- `project hook-init home.before --suggest --pick --json` auto-scaffolds the live hook file when suggestion mode has already narrowed to one exact match
- `project hook-init home --suggest --page-key home --section-key hero --slot-key hero-actions --pick-recommended --json` scaffolds the first recommended suggestion directly from the filtered suggestion list
- `project hook-init home --suggest --page-key home --section-key hero --slot-key hero-actions --pick-index 2 --json` scaffolds the second numbered suggestion directly from the filtered suggestion list
- broader `project hook-init ... --suggest` responses now also include one recommended `--pick-index` command so text-mode users can keep moving without reconstructing the next command by hand
- `project hook-init` now remembers the most recent suggestion query in `/.ail/last_hook_suggestions.json`, so a follow-up `project hook-init --pick-index N --json` can reuse that narrowed suggestion set without retyping the same filters
- `project hook-init --last-suggest --json` lets users inspect that saved suggestion memory before deciding whether to reuse it
- `project hook-init --reuse-last-suggest --pick-index N --json` makes that reuse path explicit for users who want a clearer, less implicit follow-up command
- `project hook-init --reuse-last-suggest --pick-recommended --json` now gives that reuse path a shorter default follow-up when the user simply wants the first recommended live target
- `project hook-init --open-catalog --json` returns the current project catalog paths and next-step guidance
- `project hook-init home.before --dry-run --text-compact` now gives one short preview of the direct scaffold target plus the exact confirm command to rerun without `--dry-run`
- `project hook-init home.before --dry-run --explain` now prints a structured explanation of the scaffold selection, resolved template, target path, and recommended follow-up command
- `project hook-init home.before --dry-run --emit-shell` now prints that single best next command directly, and `--copy-command` copies the same command to the macOS clipboard
- `project hook-init home.before --dry-run --emit-confirm-shell` now prints only that confirm command, and `--copy-confirm-command` copies it to the macOS clipboard
- `project hook-init home.before --dry-run --emit-target-path` now prints only the resolved live hook target path, and `--copy-target-path` copies it to the macOS clipboard
- `project hook-init home.before --dry-run --emit-target-dir` now prints the parent overrides directory for that target, and `--copy-target-dir` copies it to the macOS clipboard
- `project hook-init home.before --dry-run --emit-target-project-root` now prints the generated project root that owns that target, and `--copy-target-project-root` copies it to the macOS clipboard
- `project hook-init home.before --dry-run --emit-target-project-name` now prints the generated project folder name that owns that target, and `--copy-target-project-name` copies it to the macOS clipboard
- `project hook-init home.before --dry-run --emit-target-relative-path` now prints that same target relative to the project root, and `--copy-target-relative-path` copies that relative path to the macOS clipboard
- `project hook-init home.before --dry-run --emit-target-bundle` now prints one compact JSON bundle containing the target path, directory, project root, project name, relative path, open command, and confirm command, and `--copy-target-bundle` copies that same bundle to the macOS clipboard
- `project hook-init home.before --dry-run --inspect-target` now inspects the resolved hook-init target path and its parent directory inline, `--inspect-target --text-compact` surfaces the same target plus nearby sibling entries in one short operator view, `--open-target` returns the direct open-target payload for that same file, and `--open-now` inspects the resolved target inline without an extra command
- `project hook-init home.before --dry-run --emit-open-shell` now prints the direct `inspect <target_path>` command for that resolved hook target, and `--copy-open-command` copies that same open command to the macOS clipboard
- `project hook-init home.before --dry-run --run-command` now stages the single best next hook-init command behind an explicit confirmation boundary, and `--run-command --yes` executes that scaffold step immediately and returns the nested scaffold result inline
- `project hook-init home.before --dry-run --run-open-command` now returns a confirm-gated inspect execution payload for that same target, and `--run-open-command --yes` executes the target inspection immediately and returns the inspection result inline
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --text-compact` now gives that same compact preview from the repo root, while also showing which generated project route was selected
- `workspace hook-guide --json` now returns one short repo-root hook workflow guide with the current recommended workspace project, suggest path, continue path, and explain path
- `workspace hook-guide --emit-shell` now prints the preferred repo-root next command from that guide, and `--copy-command` copies it to the macOS clipboard
- `workspace hook-guide --run-command` now stages that preferred repo-root next command behind an explicit confirmation boundary, and `--run-command --yes` executes it and returns the nested result inline
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --explain` now prints the delegated route, selected hook query, resolved target, and recommended follow-up in one structured operator view
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-shell` now prints the delegated best-next command from the repo root, and `--copy-command` copies it to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-confirm-shell` now prints the delegated confirm command from the repo root, and `--copy-confirm-command` copies it to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-path` now prints the delegated live hook target path from the repo root, and `--copy-target-path` copies it to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-dir` now prints the delegated overrides directory from the repo root, and `--copy-target-dir` copies it to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-project-root` now prints the delegated generated project root from the repo root, and `--copy-target-project-root` copies it to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-project-name` now prints the delegated generated project folder name from the repo root, and `--copy-target-project-name` copies it to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-relative-path` now prints that delegated target relative to the selected project root, and `--copy-target-relative-path` copies it to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-bundle` now prints the delegated target bundle from the repo root, and `--copy-target-bundle` copies that bundle to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --inspect-target` now inspects the delegated hook-init target path and its parent directory inline, `--inspect-target --text-compact` surfaces the same delegated target plus nearby sibling entries in one short operator view, `--open-target` returns the delegated open-target payload, and `--open-now` inspects that delegated target inline without an extra command
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-open-shell` now prints the delegated `inspect <target_path>` command from the repo root, and `--copy-open-command` copies that same open command to the macOS clipboard
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --run-command` now stages the same delegated best-next scaffold command from the repo root behind an explicit confirmation boundary, and `--run-command --yes` executes that scaffold step immediately and returns the nested scaffold result inline
- `workspace hook-init home.before --project-name HookExampleGenerated --dry-run --run-open-command` now returns the same confirm-gated inspect execution payload from the repo root, and `--run-open-command --yes` executes the delegated target inspection immediately and returns that inspection result inline
- `project hook-init` rejects unknown hook names when a hook catalog is present
- `project hook-init` refuses to overwrite an existing file unless `--force` is passed
- `project hook-init ... --force` overwrites an existing live hook file when the user explicitly asks for it

Full repository smoke was attempted again after the CLI change, but the run hit an environment-level disk-capacity failure while cloning the frontend template during later website trial checks. The new `project hooks` command itself was validated successfully in a real initialized project before that capacity failure occurred.

That capacity issue was later resolved by clearing generated sample `frontend/node_modules` directories, and the smoke suite was rerun successfully.

One later validation pass on 2026-04-03 ran into a different problem that looked like product breakage at first, but turned out to be execution-environment overload inside the Codex session pool. The concrete symptom was that fresh `python3 -m cli init` and related smoke entrypoints started failing while Python extension modules such as `_posixsubprocess` were being denied or hanging under system policy checks. After restarting Codex and re-running from a clean session pool on 2026-04-04, fresh compile and fresh full CLI smoke both returned to green.

Current validation truth:

- fresh compile passed again on 2026-04-04
- fresh `/Users/carwynmac/ai-cl/testing/cli_smoke.sh` passed again on 2026-04-04
- `/Users/carwynmac/ai-cl/testing/results/cli_smoke_results.json` is the current fresh-green reference again

Reference starter-example validation sample:

- `/Users/carwynmac/ai-cl/output_projects/HookExampleGenerated`

Verified outcomes:

- the example files are scaffolded automatically
- they do not render by default
- the generated frontend still passes `npm run build`

## Best Next Step

If we continue this line, the next highest-value follow-up is:

1. add one optional CLI helper that copies an example into a live hook name for the user
2. or add light filtering to `workspace hooks`, for example by project name or page key
