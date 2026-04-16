# AIL CLI Commands

## Overview

This document defines the core CLI commands expected in an AIL-based workflow.

## Command Summary

| Command | Purpose |
| --- | --- |
| `ail init` | Initialize an AIL project |
| `ail generate` | Generate AIL from a requirement |
| `ail diagnose` | Validate AIL against current system rules |
| `ail repair` | Repair near-valid AIL |
| `ail compile` | Compile AIL into generated artifacts |
| `ail sync` | Sync cloud-generated files into managed zones |
| `ail conflicts` | Inspect conflict state and resolution options |

## `ail init`

### Purpose

Initialize project structure, `.ail/` metadata directory, and default managed/custom zones.

### Example

```bash
ail init
```

### Usage Scenario

- starting a new AIL-managed project
- preparing an existing repo for cloud compile and sync

## `ail generate`

### Purpose

Generate or update `.ail/source.ail` from requirement input.

### Example

```bash
ail generate --from requirements.md
```

### Usage Scenario

- turning product requirements into AIL source
- iterating on feature intent before compile

## `ail diagnose`

### Purpose

Run AIL validation against current profile and token boundaries.

### Example

```bash
ail diagnose .ail/source.ail
```

### Usage Scenario

- checking whether AIL is compile-safe
- catching unsupported components or flow drift before compile

## `ail repair`

### Purpose

Repair an almost-valid AIL program into a system-supported form.

### Example

```bash
ail repair .ail/source.ail
```

### Usage Scenario

- fixing wrapper noise
- collapsing multiple profiles into one valid target
- normalizing alias or drifted tokens

## `ail compile`

### Purpose

Compile AIL into generated artifacts.

### Example

```bash
ail compile --cloud
```

### Usage Scenario

- performing full cloud compile
- refreshing generated views, routes, and backend managed output

## `ail sync`

### Purpose

Apply cloud-generated files and manifest updates into local managed zones.

### Example

```bash
ail sync
```

### Usage Scenario

- pulling latest cloud build into the local project
- updating managed files after conflict checks pass

## `ail conflicts`

### Purpose

Inspect sync conflicts and provide resolution actions.

### Example

```bash
ail conflicts
```

### Usage Scenario

- reviewing local drift in generated files
- deciding whether to overwrite, preserve, or cancel sync

## Recommended Workflow

```bash
ail init
ail generate
ail diagnose .ail/source.ail
ail repair .ail/source.ail
ail compile --cloud
ail sync
ail conflicts
```

## Notes

- `ail compile` and `ail sync` should respect the managed zone boundary.
- `ail diagnose` and `ail repair` should be used before compile when AIL quality is uncertain.
- `ail conflicts` should be part of any IDE or CLI-based sync workflow that touches managed files.
