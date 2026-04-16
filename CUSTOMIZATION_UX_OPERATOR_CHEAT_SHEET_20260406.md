# Customization UX Operator Cheat Sheet 2026-04-06

## Purpose

This is the shortest practical command guide for the current durable-hook workflow.

Use it when you do not want to re-read the longer managed / unmanaged phase docs or full CLI help.

## Fastest Safe Paths

If you are not sure where to start, use one of these first:

- repo-root start:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --json`
- current-project start:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --json`
- continue the last repo-root hook surface:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --text-compact`

Use the longer sections below only when you need a more specific helper path.

If you want the grouped CLI help first:

- current-project help:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --help`
- repo-root help:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --help`
- continue help:
  - `PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --help`

## Operator Vocabulary

The current CLI surfaces now mostly use one shared set of words:

- `overview`
  - show the current guide or current hook surface
- `discover`
  - list or suggest possible hook targets
- `preview`
  - dry-run the chosen path before writing
- `explain`
  - explain why this path and target were selected
- `handoff`
  - emit or copy the next command or target helper
- `execute`
  - actually run the selected next command
- `inspect`
  - inspect the resolved target file or nearby hook surface

If two commands look similar, prefer the one whose label matches the step you are currently in.

## 1. Find Hook Surfaces

Inspect one current project:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hooks --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hooks home --json
```

Inspect all generated projects from the repo root:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hooks --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace summary --json
```

Use this when you need:

- available page / section / slot hooks
- one recommended next `hook-init` command
- the current recommended or recent workspace project

Shortcut guide:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --emit-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --copy-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --run-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --run-command --yes --json
```

## 2. Scaffold A Live Hook In The Current Project

Use this order when you already know you want to stay inside the current project:

- `overview`
- `preview`
- `explain`
- `handoff`
- `execute`

Current-project overview / handoff:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --emit-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --copy-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --run-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-guide --run-command --yes --json
```

Current-project preview / explain / handoff:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --text-compact
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --explain
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-confirm-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-confirm-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-target-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-target-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-target-dir
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-target-dir
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-target-project-root
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-target-project-root
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-target-project-name
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-target-project-name
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-target-relative-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-target-relative-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-target-bundle
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-target-bundle
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --inspect-target --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --inspect-target --text-compact
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --open-target --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --open-now --text-compact
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --emit-open-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --copy-open-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --run-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --run-command --yes --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --run-open-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home.before --dry-run --run-open-command --yes --json
```

Current-project discover:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home --suggest --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home --suggest --page-key home --section-key hero --slot-key hero-actions --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init home --suggest --page-key home --section-key hero --slot-key hero-actions --pick-recommended --json
```

Reuse the last narrowed suggestion set:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init --last-suggest --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init --reuse-last-suggest --pick-recommended --json
```

Open the project-local hook catalog:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli project hook-init --open-catalog --json
```

## 3. Scaffold A Live Hook From Repo Root

Use this order when you want to stay at repo root:

- `overview`
- `preview`
- `explain`
- `handoff`
- `execute`

Repo-root overview / handoff:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --emit-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --copy-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --run-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-guide --run-command --yes --json
```

Repo-root preview / explain / handoff:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init --follow-recommended --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --text-compact
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --explain
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-confirm-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-confirm-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-target-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-dir
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-target-dir
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-project-root
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-target-project-root
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-project-name
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-target-project-name
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-relative-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-target-relative-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-target-bundle
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-target-bundle
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --inspect-target --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --inspect-target --text-compact
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --open-target --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --open-now --text-compact
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --emit-open-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --copy-open-command
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --run-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --run-command --yes --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --run-open-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --dry-run --run-open-command --yes --json
```

Repo-root discover / reuse:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init --use-last-project --suggest --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init --use-last-project --pick-recommended --json
```

Repo-root explicit project targeting:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-init home.before --project-name HookExampleGenerated --json
```

## 4. Continue The Last Hook Surface From Repo Root

Use the current recent-vs-recommended resolver:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --json
```

Use this when you want the CLI to:

- prefer the recent workspace project if it exists
- otherwise fall back to the recommended workspace path
- carry forward remembered page / section / slot filters when available

## 5. Preview Before Writing

Short preview:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --text-compact
```

Decision explanation:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --explain
```

Inspect the resolved target and nearby files:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --inspect-target --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --inspect-target --text-compact
```

Open the resolved target inside the current payload:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --open-now --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --open-now --text-compact
```

## 6. Broaden A Too-Narrow Continue Path

Step back to section or page:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --broaden-to section --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --broaden-to page --json
```

Let the CLI auto-fallback when the exact slot is blocked:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --broaden-to auto --json
```

## 7. Get The Next Command

Print the best next command:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-shell
```

Print the confirm command only:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-confirm-shell
```

Copy the confirm command:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-confirm-command
```

Run the next command with an explicit confirmation boundary:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --run-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --run-command --yes --json
```

## 8. Get The Target File, Dir, Project, Or Bundle

Print raw target fields:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-target-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-target-dir
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-target-project-root
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-target-project-name
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-target-relative-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-target-bundle
```

Copy those same values:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-target-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-target-dir
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-target-project-root
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-target-project-name
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-target-relative-path
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-target-bundle
```

Use the bundle when you want one compact payload containing:

- `target_path`
- `target_dir`
- `target_project_root`
- `target_project_name`
- `target_relative_path`
- `open_command`
- `confirm_command`

## 9. Open The Resolved Target

Print or copy the open command:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --emit-open-shell
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --copy-open-command
```

Stage or execute the open-target inspection:

```bash
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --run-open-command --json
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli workspace hook-continue --dry-run --run-open-command --yes --json
```

## 10. Short Recommendations

If you are not sure where to start:

1. Run `workspace hooks --json`
2. Run `workspace hook-init --follow-recommended --json`
3. Use `workspace hook-continue --dry-run --text-compact`

If you are already in one project and just need the next durable insert:

1. Run `project hook-init --open-catalog --json`
2. Run `project hook-init <query> --suggest ... --json`
3. Run `project hook-init ... --pick-recommended --json`

If you are returning to unfinished hook work from the repo root:

1. Run `workspace hook-continue --dry-run --text-compact`
2. If the target feels too narrow, run `workspace hook-continue --broaden-to auto --json`
3. If the preview looks right, use the emitted or copied confirm command
