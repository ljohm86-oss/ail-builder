# AIL Builder MCP Tool Surface Spec

## Purpose

This document defines the **first thin MCP surface** that AIL Builder could expose after the current skill packaging step.

The goal is not to invent a second product surface.

The goal is to expose the current CLI semantics through a smaller set of stable, tool-friendly operations that agent and IDE hosts can call without reconstructing command lines manually.

## Current Recommendation

If AIL Builder adds MCP exposure, the first version should be:

- thin
- CLI-backed
- read-heavy by default
- explicit about preview vs. execution
- narrower than the full CLI

The first MCP layer should mirror current product truth instead of trying to expose every flag immediately.

## Non-Goals

The first MCP version should **not** attempt to be:

- a replacement for the CLI
- a stable public API guarantee
- a complete export of every existing command flag
- a host-specific IDE plugin
- an autonomous website-generation agent

## Design Principles

### 1. CLI Remains The Source Of Truth

Each MCP tool should map to one current CLI surface or one small CLI-backed orchestration layer.

The MCP layer should not create a new logic fork.

### 2. Separate Read / Preview / Execute

The first MCP layer should keep these modes distinct:

- overview and discovery
- preview and explain
- execution

This is important because AIL Builder already has a meaningful distinction between:

- inspect
- dry-run
- explain
- write / run

### 3. Prefer Fewer, Broader Tools

The first tool set should be small.

It is better to expose a small set of coherent tools than 40 thin one-flag wrappers.

### 4. Preserve Managed / Unmanaged Boundaries

Tools should bias callers toward:

- `hook-guide`
- `hook-init`
- `hook-continue`

and away from direct managed-file edits.

## Proposed First MCP Tool Set

## 1. `website_check`

### Use For

- evaluating whether one website request fits the current supported surface

### CLI Mapping

```bash
python3 -m cli website check <requirement> --base-url embedded://local --json
```

### Input

- `requirement_text`
- optional `base_url`

### Output

- current deliverability judgment
- supported pack hints
- evaluation payload already exposed by the CLI

## 2. `website_summary`

### Use For

- getting one website-oriented overview of current deliverable surface

### CLI Mapping

```bash
python3 -m cli website summary --json
```

### Output

- website frontier overview
- delivery-asset state
- current recommended website action

## 3. `workspace_summary`

### Use For

- getting a repo-root orientation view before any customization or execution work

### CLI Mapping

```bash
python3 -m cli workspace summary --base-url embedded://local
```

### Output

- current workspace overview
- current recommended next paths
- high-level state for agents and IDEs

## 4. `workspace_hook_guide`

### Use For

- finding the safest repo-root durable customization entrypoint

### CLI Mapping

```bash
python3 -m cli workspace hook-guide --json
```

### Output

- recommended project
- recommended hook path
- human next command
- runnable next command

## 5. `project_hook_guide`

### Use For

- getting the right durable customization entry while already inside one project

### CLI Mapping

```bash
python3 -m cli project hook-guide --json
```

### Output

- current project guidance
- recommended hook
- human next command
- runnable next command

## 6. `hook_preview`

### Use For

- previewing a hook-init or hook-continue path without writing files

### CLI Mapping

One of:

```bash
python3 -m cli project hook-init <hook_name> --dry-run --json
python3 -m cli workspace hook-init ... --dry-run --json
python3 -m cli workspace hook-continue --dry-run --json
```

### Input

- `mode`
  - `project_hook_init`
  - `workspace_hook_init`
  - `workspace_hook_continue`
- route-specific args such as `hook_name` or `project_name`

### Output

- target path
- target relative path
- summary
- reason
- next commands

## 7. `hook_explain`

### Use For

- explaining the route, target, and next step in a more human-readable form

### CLI Mapping

One of:

```bash
python3 -m cli project hook-init <hook_name> --dry-run --explain
python3 -m cli workspace hook-init ... --dry-run --explain
python3 -m cli workspace hook-continue --dry-run --explain
```

### Output

- route explanation
- target explanation
- next-step explanation
- current message / blocker if any

## 8. `hook_target_bundle`

### Use For

- retrieving a compact target bundle for handoff into IDE or agent tooling

### CLI Mapping

One of:

```bash
python3 -m cli project hook-init <hook_name> --dry-run --emit-target-bundle
python3 -m cli workspace hook-init ... --dry-run --emit-target-bundle
python3 -m cli workspace hook-continue --dry-run --emit-target-bundle
```

### Output

- `target_path`
- `target_dir`
- `target_project_root`
- `target_project_name`
- `target_relative_path`
- `open_command`
- `confirm_command`

## 9. `hook_inspect_target`

### Use For

- inspecting the current target file and nearby state before writing

### CLI Mapping

One of:

```bash
python3 -m cli project hook-init <hook_name> --dry-run --inspect-target --json
python3 -m cli workspace hook-init ... --dry-run --inspect-target --json
python3 -m cli workspace hook-continue --dry-run --inspect-target --json
```

### Output

- target inspection
- parent inspection
- nearby entries where available

## 10. `hook_execute`

### Use For

- executing a previously previewed hook step

### CLI Mapping

One of:

```bash
python3 -m cli project hook-init <hook_name> --json
python3 -m cli workspace hook-init ... --json
python3 -m cli workspace hook-continue --json
```

### Input

- route-specific args
- optional explicit confirmation flag in the MCP layer

### Output

- execution result payload
- written target information
- follow-up state

## 11. `hook_run_next`

### Use For

- executing a confirmed next command from a guided flow

### CLI Mapping

One of:

```bash
python3 -m cli project hook-guide --run-command --yes --json
python3 -m cli workspace hook-guide --run-command --yes --json
python3 -m cli project hook-init ... --run-command --yes --json
python3 -m cli workspace hook-init ... --run-command --yes --json
python3 -m cli workspace hook-continue --run-command --yes --json
```

### Reason To Keep Separate

This tool is not the same as `hook_execute`.

`hook_execute` means "perform the current route."

`hook_run_next` means "execute the guided next command already suggested by the system."

## 12. `project_serve`

### Use For

- starting or dry-running the local frontend dev server for one generated project

### CLI Mapping

```bash
python3 -m cli project serve --dry-run --json
python3 -m cli project serve --install-if-needed --json
```

### Input

- optional `host`
- optional `port`
- optional `install_if_needed`
- optional `dry_run`

### Output

- project root
- frontend root
- local URL
- command
- npm/dependency status
- pid and log path when a server is started

## Suggested Tool Groups

The first MCP tool menu should be grouped like this:

### Website

- `website_check`
- `website_summary`

### Workspace

- `workspace_summary`
- `workspace_hook_guide`

### Project

- `project_hook_guide`
- `project_serve`

### Hook Preview And Explain

- `hook_preview`
- `hook_explain`
- `hook_target_bundle`
- `hook_inspect_target`

### Hook Execution

- `hook_execute`
- `hook_run_next`

## Tools To Avoid In Version One

Avoid exposing these directly at first:

- one tool per `emit-*` helper
- one tool per `copy-*` helper
- one tool per individual target path field
- raw shell-command emitters
- open-command wrappers that only mirror local shell ergonomics

Those helpers are useful in the CLI, but they are too low-level and shell-shaped for a first MCP pass.

## Execution Safety Recommendation

The first MCP execution tools should follow these rules:

- preview-first by default
- explicit execute step
- no hidden writes
- no silent managed-file edits

If a host supports confirmation or human approval, execution tools should take advantage of it.

## Suggested Output Style

The MCP layer should prefer structured payloads that already exist in JSON mode.

Avoid tool outputs that are:

- shell-only
- clipboard-only
- formatted primarily for human terminal reading

The right first MCP style is:

- JSON-backed
- IDE-readable
- stable enough for experiments

## Recommended Next Step

After this spec, the next worthwhile implementation step is:

1. one thin experimental MCP adapter
2. backed by existing CLI commands
3. starting with read-heavy tools first

That means:

- `website_check`
- `website_summary`
- `workspace_summary`
- `workspace_hook_guide`
- `project_hook_guide`

should likely be implemented before any write-capable tools.

## Current Judgment

AIL Builder is now ready for an **experimental MCP tool-surface design**.

It is not yet ready for:

- a broad "stable MCP product" claim
- full CLI parity through MCP
- host-specific plugin promises
