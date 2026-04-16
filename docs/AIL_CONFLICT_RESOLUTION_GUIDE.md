# AIL Conflict Resolution Guide

## 1. Overview

This guide defines how IDEs and CLI tooling should detect, classify, surface, and resolve conflicts during AIL cloud sync.

It is a practical companion to:

- `/Users/carwynmac/ai-cl/docs/AIL_CLOUD_SYNC_PROTOCOL_V1.md`
- `/Users/carwynmac/ai-cl/docs/AIL_MANIFEST_SPEC_V1.md`

The goal is to prevent silent loss of local work while preserving the rule that AIL remains the single source of truth.

## 2. Core Principle

```text
Never silently overwrite locally modified managed files.
```

Managed files are rebuildable, but local edits inside managed zones may still exist. The system must detect and surface those edits before replacement.

## 3. Conflict Detection Rule

A conflict exists when:

```text
local_sha != manifest_sha
AND
cloud wants to update same file
```

Where:

- `manifest_sha` is the last synced hash recorded in `.ail/manifest.json`
- `local_sha` is the hash of the current local file
- `cloud wants to update same file` means the file appears in the incoming cloud file list or delete list

## 4. Conflict Levels

### Level 1 — Safe Overwrite

Condition:

- local file exists
- local hash matches manifest hash
- cloud provides new content for same path

Action:

- overwrite automatically
- update manifest

### Level 2 — Local Drift Detected

Condition:

- local file differs from manifest
- file is still inside a managed zone
- change is recoverable by saving a local copy

Action:

- prompt user
- allow overwrite with backup
- offer cancel

### Level 3 — Hard Conflict

Condition:

- local drift exists
- incoming cloud change is destructive, structural, or likely to invalidate local work
- file delete or major route/page replacement is involved

Action:

- block silent sync
- require explicit resolution
- preserve local copy before any destructive step

## 5. Resolution Options

The IDE or CLI must provide three options.

| Option | Description |
| --- | --- |
| Overwrite local version | Accept cloud output and replace managed file |
| Keep local backup | Save local copy under `.ail/conflicts/<build_id>/...` before overwrite |
| Cancel sync | Abort sync and keep local state unchanged |

### Backup Path Convention

Recommended backup location:

```text
.ail/conflicts/<build_id>/src/views/generated/Home.local.vue
```

This preserves both build context and original relative path.

## 6. Recommended IDE Behavior

The IDE should:

1. detect conflict before file write
2. show file path and conflict level
3. explain why the conflict happened
4. offer explicit choices
5. never auto-resolve Level 2 or Level 3 by silent overwrite

### Suggested IDE Prompt

```text
Local changes were detected in a compiler-managed file.
Choose how to proceed:
- overwrite with cloud output
- keep a local backup and continue
- cancel sync
```

## 7. Recommended CLI Behavior

The CLI should expose conflicts with clear status lines.

Example:

```bash
ail sync
```

Possible output:

```text
Conflict detected: src/views/generated/Home.vue
Level: 2 (local drift detected)
Available actions:
  1. overwrite
  2. backup-and-overwrite
  3. cancel
```

Batch-friendly flags may include:

```bash
ail sync --overwrite-safe
ail sync --backup-conflicts
ail sync --abort-on-conflict
```

## 8. Conflict Decision Matrix

| Situation | Recommended Default |
| --- | --- |
| safe overwrite in managed zone | overwrite |
| local drift in managed file | backup and prompt |
| hard conflict or deletion with drift | cancel until explicit choice |
| user-zone file touched | never cloud-overwrite |

## 9. Managed Zone vs User Zone

Conflict rules only apply to managed files.

| Zone Type | Example | Cloud May Overwrite? |
| --- | --- | --- |
| Managed zone | `src/views/generated/` | yes, with conflict rules |
| User zone | `src/custom/` | no |
| User zone | `backend/custom/` | no |

If cloud output attempts to write into a user zone, that should be treated as protocol invalidity, not a normal conflict.

## 10. Delete Conflicts

Delete conflicts require special care.

If cloud requests deletion of a managed file and the local file has drifted from manifest:

- classify at least as Level 3
- offer backup before delete
- never delete silently

## 11. Manifest Update Rules During Conflict

The manifest must only be updated after conflict resolution is accepted and file operations succeed.

Do not update the manifest when:

- user cancels sync
- overwrite fails
- backup fails
- unresolved hard conflict remains

## 12. Logging Recommendations

The system should log:

- `build_id`
- conflicting file path
- conflict level
- selected resolution
- backup path if created
- final sync outcome

This is useful for support, audit, and rollback-oriented tooling.

## 13. Non-Goals

This guide does not define:

- automatic 3-way merge
- semantic merge of generated files
- collaborative live conflict resolution
- reverse-compilation from code back to AIL

## 14. Future Extensions

Possible v2 additions:

- conflict preview diff
- per-file resolution policies
- team approval workflows
- rollback to previous manifest/build pair

## 15. Guide Summary

Conflict resolution in AIL sync must be:

- explicit
- manifest-based
- safe for local work
- strict about managed vs user zones
- resistant to silent overwrite
