# AIL Manifest Spec v1

## 1. Overview

This document defines the canonical structure and lifecycle rules for `.ail/manifest.json` in an AIL-managed project.

The manifest is the synchronization contract between:

- AIL source
- cloud compile output
- IDE sync behavior
- local managed files

It exists to support:

- generated file ownership tracking
- conflict detection
- build identity and version history
- deterministic managed-zone synchronization

## 2. Design Goals

The manifest must provide:

| Goal | Description |
| --- | --- |
| Traceability | Identify which build produced which managed files |
| Safety | Detect local drift before overwrite |
| Determinism | Ensure sync decisions are based on explicit file state |
| Isolation | Separate managed files from custom code |
| Recoverability | Support deletion, rebuild, and rollback-oriented workflows |

## 3. File Location

The manifest file lives at:

```text
.ail/manifest.json
```

Related files commonly include:

```text
.ail/source.ail
.ail/last_build.json
.ail/patches/
```

## 4. Ownership Rules

The manifest applies only to managed zones.

Typical managed roots:

```text
src/views/generated/
src/router/generated/
backend/generated/
src/ail_generated/
```

The manifest must not claim ownership of user zones such as:

```text
src/custom/
src/extensions/
src/theme/
backend/custom/
```

## 5. Canonical Structure

A minimal manifest structure is:

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

## 6. Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | string | yes | Stable cloud/local project identifier |
| `manifest_version` | integer | yes | Monotonic manifest revision number |
| `current_build_id` | string | yes | Build that produced the current managed state |
| `managed_roots` | string[] | yes | Root directories controlled by compiler sync |
| `managed_files` | object | yes | File-level state for all managed artifacts |

## 7. Managed File Entry Schema

Each entry in `managed_files` should use the relative project path as the key.

Recommended structure:

```json
{
  "src/views/generated/Home.vue": {
    "sha256": "abc123",
    "build_id": "build_20260316_001",
    "generated_at": "2026-03-16T10:15:00Z",
    "kind": "view"
  }
}
```

### Recommended File Entry Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `sha256` | string | yes | Hash of synced file content |
| `build_id` | string | recommended | Build that most recently produced the file |
| `generated_at` | string | recommended | UTC timestamp of generation |
| `kind` | string | optional | Logical artifact type such as `view`, `router`, `backend` |

## 8. Manifest Lifecycle

The manifest is updated when:

1. a full compile succeeds
2. a patch compile succeeds and sync is accepted
3. managed files are deleted as part of cloud output
4. a rollback restores a previous manifest snapshot

The manifest should not be updated when:

- compile fails
- sync is cancelled
- conflicts are detected and unresolved
- only user-zone files change

## 9. Sync Semantics

During sync, the manifest is used to answer three questions:

1. Which files are compiler-managed?
2. What content is expected locally before overwrite?
3. Which files must be updated, added, or deleted?

### Sync Decision Table

| Condition | Action |
| --- | --- |
| file not present in local manifest and sent by cloud | add managed file |
| file present and local hash matches manifest hash | safe overwrite |
| file present and local hash differs from manifest hash | conflict detection required |
| file listed in `deleted_files` and still manifest-owned | delete from managed zone |

## 10. Conflict Detection Rule

A conflict exists when:

```text
local_sha != manifest_sha
AND
cloud wants to update same file
```

This means the local file has drifted from the last known synced state.

## 11. Versioning Rules

`manifest_version` must be monotonic.

Recommended behavior:

- increment on every accepted sync
- never decrement during normal operation
- preserve previous manifest snapshot in build metadata if rollback is supported later

## 12. Relationship To Build Metadata

The manifest is not a full build log.

Use separation of concerns:

| File | Purpose |
| --- | --- |
| `.ail/manifest.json` | current sync contract |
| `.ail/last_build.json` | most recent build summary |
| cloud build history | long-term historical record |

## 13. Validation Rules

A valid v1 manifest should satisfy:

- `project_id` exists
- `manifest_version` is an integer
- `current_build_id` exists
- `managed_roots` contains only managed directories
- every `managed_files` key is inside a managed root
- every managed file entry contains `sha256`
- no user-zone path appears in `managed_files`

## 14. Non-Goals

This spec does not define:

- AST-level merge
- collaborative locking
- bi-directional code to AIL recovery
- semantic ownership inference outside managed roots

## 15. Future Extensions

Possible v2 additions:

- file ownership classes
- page-level patch lineage
- rollback snapshots
- conflict fingerprints
- multi-user sync metadata

## 16. Spec Summary

The manifest is the local synchronization contract for compiler-managed artifacts.

It must remain:

- explicit
- deterministic
- limited to managed zones
- safe for conflict-aware overwrite behavior
