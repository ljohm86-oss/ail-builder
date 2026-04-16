# AIL Cloud Sync Protocol v1

## 1. Overview

This protocol defines how AIL cloud compilation, IDE synchronization, and CLI workflows operate as one consistent engineering system.

Its purpose is to:

- solve synchronization between cloud-compiled AIL output and local projects
- prevent generated file conflicts
- keep lifecycle ownership of generated artifacts explicit
- preserve a stable separation between compiler-managed code and user-owned code

### Core Principles

- AIL is the single source of truth.
- Generated files are rebuildable artifacts.
- User custom code must live outside managed zones.

### Design Intent

| Topic | Protocol Position |
| --- | --- |
| Source of truth | `.ail/source.ail` |
| Generated code | Disposable, reproducible, overwriteable in managed zones |
| User code | Must live in custom zones |
| Synchronization | Controlled by manifest and conflict detection |
| IDE behavior | Must respect managed vs user zones |

## 2. Architecture Overview

```text
User Requirement
      ↓
IDE / CLI
      ↓
AIL Source
      ↓
Cloud Compiler
      ↓
Generated Files + Manifest
      ↓
IDE Sync
      ↓
Local Project
```

### Responsibility Split

| Component | Responsibility |
| --- | --- |
| IDE | Capture user intent, manage sync, detect conflicts, protect user zones |
| CLI | Execute repeatable project actions, compile, sync, diagnose, repair |
| AIL Source | Canonical program defining project structure and compiler intent |
| Cloud Compiler | Produce managed artifacts, manifest, build metadata, and diff summary |
| Local Project | Host generated artifacts plus user-owned extensions and custom code |

### Operational Model

- The IDE or CLI submits AIL source to the cloud compiler.
- The cloud compiler returns generated files plus a manifest.
- The IDE sync engine applies changes only inside managed zones.
- User-owned code remains isolated and must not be overwritten by cloud output.

## 3. Project Directory Layout

```text
project/
 ├─ src/
 │   ├─ views/
 │   │   └─ generated/
 │   ├─ router/
 │   │   └─ generated/
 │   ├─ custom/
 │   ├─ extensions/
 │   └─ theme/
 ├─ backend/
 │   ├─ generated/
 │   └─ custom/
 ├─ .ail/
 │   ├─ source.ail
 │   ├─ manifest.json
 │   ├─ last_build.json
 │   └─ patches/
```

### Managed Zones

Managed zones are compiler-controlled paths.

```text
src/views/generated/
src/router/generated/
backend/generated/
src/ail_generated/
```

Characteristics:

- may be overwritten
- may be deleted
- are fully rebuildable on every compile
- must be tracked by manifest

### User Zones

User zones are user-controlled paths.

```text
src/custom/
src/extensions/
src/theme/
backend/custom/
```

Characteristics:

- must never be overwritten by cloud sync
- are freely editable by users
- are outside compiler ownership
- may import or wrap generated content, but are not generated themselves

### Zone Summary

| Zone Type | Examples | Compiler May Overwrite | Compiler May Delete |
| --- | --- | --- | --- |
| Managed | `src/views/generated/` | Yes | Yes |
| Managed | `src/router/generated/` | Yes | Yes |
| Managed | `backend/generated/` | Yes | Yes |
| User | `src/custom/` | No | No |
| User | `src/extensions/` | No | No |
| User | `src/theme/` | No | No |
| User | `backend/custom/` | No | No |

## 4. Source of Truth Rules

The system follows these rules:

1. `.ail/source.ail` is the only source of truth.
2. Generated files are compiler artifacts, not canonical source.
3. IDEs must not allow direct editing of generated files as if they were user-owned files.
4. User-authored logic must live in custom zones.

### Interpretation

| Rule | Required Behavior |
| --- | --- |
| AIL is canonical | Rebuild from AIL, not from generated code |
| Generated files are disposable | Safe to replace within managed zones |
| Direct generated edits are unsupported | IDE should warn or make these files read-only |
| Custom code must be isolated | Extensions and overrides must live outside managed zones |

## 5. Cloud Compile API

The cloud compiler exposes compile modes for full regeneration and scoped patch compilation.

### Full Compile

Request example:

```json
{
  "project_id": "proj_001",
  "mode": "full",
  "ail_source": "...",
  "client_manifest_version": 3
}
```

### Patch Compile

Request example:

```json
{
  "project_id": "proj_001",
  "mode": "patch",
  "target": {
    "type": "page",
    "name": "Home"
  },
  "ail_patch": "..."
}
```

### API Semantics

| Field | Meaning |
| --- | --- |
| `project_id` | Stable cloud-side project identifier |
| `mode` | Compile mode, such as `full` or `patch` |
| `ail_source` | Canonical full AIL input |
| `client_manifest_version` | Local manifest version known by the client |
| `target` | Scope of patch compilation |
| `ail_patch` | Partial AIL delta or scoped replacement input |

## 6. Cloud Response Format

The cloud response must include:

1. build metadata
2. generated files
3. manifest
4. diff summary

Example:

```json
{
  "build_id": "build_20260316_001",
  "files": [
    {
      "path": "src/views/generated/Home.vue",
      "content": "...",
      "sha256": "abc123"
    }
  ],
  "deleted_files": [],
  "manifest": {},
  "diff_summary": {}
}
```

### Response Contract

| Field | Required | Meaning |
| --- | --- | --- |
| `build_id` | Yes | Unique identifier of this cloud build |
| `files` | Yes | Generated files to write into managed zones |
| `deleted_files` | Yes | Managed files that should be removed locally |
| `manifest` | Yes | Updated synchronization manifest |
| `diff_summary` | Yes | Human-readable or machine-readable summary of changes |

## 7. Manifest Structure

The manifest defines synchronization ownership and version tracking.

```json
{
  "project_id": "proj_001",
  "manifest_version": 4,
  "current_build_id": "build_20260316_001",
  "managed_roots": [
    "src/views/generated/",
    "src/router/generated/"
  ],
  "managed_files": {
    "src/views/generated/Home.vue": {
      "sha256": "abc123"
    }
  }
}
```

### Manifest Purpose

- synchronization control
- conflict detection
- version tracking
- file ownership declaration

### Recommended Manifest Fields

| Field | Meaning |
| --- | --- |
| `project_id` | Stable project identity |
| `manifest_version` | Local sync generation counter |
| `current_build_id` | Last accepted cloud build |
| `managed_roots` | Root directories controlled by cloud compile |
| `managed_files` | File-level ownership and checksum map |

## 8. Conflict Detection

Before sync, the IDE or CLI must detect conflicts.

Conflict rule:

```text
if local_sha != manifest_sha
AND cloud wants to update same file
then conflict = true
```

### Conflict Levels

| Level | Name | Meaning |
| --- | --- | --- |
| 1 | safe overwrite | Local file matches manifest or only cloud-owned state changed |
| 2 | local drift detected | Local managed file changed outside accepted cloud state |
| 3 | hard conflict | Local drift plus cloud update targets the same managed file |

### Detection Inputs

- local file content hash
- last accepted manifest hash
- incoming cloud file hash
- managed root ownership map

## 9. IDE Conflict Resolution

The IDE must provide three operations:

1. Overwrite local version
2. Preserve local copy in conflict storage
3. Cancel sync

### Preserve Local Copy Example

```text
.ail/conflicts/<build_id>/Home.local.vue
```

### Default Rule

Never silently overwrite locally modified managed files.

### Resolution Matrix

| Conflict Level | Default IDE Action | User Choice Required |
| --- | --- | --- |
| Level 1 | Apply sync | No |
| Level 2 | Warn and offer backup | Yes |
| Level 3 | Block automatic overwrite | Yes |

## 10. Sync Workflow

```text
User edits requirement
      ↓
Generate AIL
      ↓
Send to cloud compile
      ↓
Receive files + manifest
      ↓
Detect conflicts
      ↓
Sync managed zone
      ↓
Update local manifest
```

### Workflow Notes

- sync only touches managed zones
- manifest update happens only after successful conflict-aware sync
- canceled sync must not partially update manifest state
- failed sync should preserve last accepted manifest until recovery completes

## 11. CLI Commands

The protocol assumes a companion CLI.

| Command | Purpose |
| --- | --- |
| `ail init` | Initialize project structure and `.ail/` directory |
| `ail generate` | Generate or update AIL source from requirement input |
| `ail diagnose` | Analyze AIL validity against current system rules |
| `ail repair` | Repair near-valid AIL into compile-safe form |
| `ail compile` | Invoke compile workflow |
| `ail sync` | Apply cloud build outputs into local managed zones |
| `ail conflicts` | Inspect and resolve managed file conflicts |

Examples:

```bash
ail compile --cloud
ail sync
```

## 12. Non Goals (v1)

Version 1 does not support:

- bidirectional reverse-engineering from generated code back into AIL
- automatic merge of generated files
- multi-user collaborative editing
- AST merge across local and cloud versions

## 13. Future Evolution (v2)

Potential v2 extensions:

- patch compile
- page-level compile
- cloud build history
- rollback
- collaborative editing

## 14. Protocol Principles

- AIL is the single source of truth.
- Generated code is disposable.
- Manifest controls synchronization.
- Custom code must be isolated.
