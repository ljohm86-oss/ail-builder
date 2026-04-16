# AIL IDE Sync Implementation Checklist

## 1. Purpose

This document is an implementation checklist for IDE, plugin, and agent-integration developers.

Its purpose is to make `AIL Cloud Sync Protocol v1` executable inside an IDE environment rather than leaving it as a purely conceptual protocol.

This checklist should be used as:

- an IDE integration execution guide
- a code review checklist
- an implementation task breakdown
- a release-readiness checklist for sync-related IDE features

### Core Principles

- AIL is the single source of truth.
- The IDE syncs only managed zones.
- Custom zones must never be overwritten by cloud sync.
- Generated files are rebuildable artifacts.
- Conflict handling must be explicit and safe.

## 2. Scope

### In Scope

- read `.ail/source.ail`
- call cloud compile API
- receive `files`, `deleted_files`, `manifest`, and `diff_summary`
- compare local manifest and cloud manifest
- detect conflicts before write
- sync generated files into managed zones
- surface conflict actions to user
- update local manifest after accepted sync
- refresh IDE project view and diagnostics

### Out of Scope

- code-to-AIL reverse sync
- AST merge
- collaborative editing
- automatic migration of user code from custom zones
- cloud compiler server implementation
- semantic merge of generated files

## 3. IDE Integration Architecture

```text
User edits requirement / AIL
      ↓
IDE prepares source
      ↓
Cloud compile request
      ↓
Receive files + manifest + diff_summary
      ↓
Local manifest compare
      ↓
Conflict detection
      ↓
Apply managed file sync
      ↓
Refresh IDE state
```

### Responsibility Split

| Layer | Responsibility |
| --- | --- |
| User | Edits requirement or AIL source, resolves explicit conflicts |
| IDE | Reads source, calls API, compares manifest, detects conflicts, applies managed sync |
| Cloud Compiler | Compiles AIL, returns managed files, manifest, and diff summary |
| Local Project | Stores managed artifacts, custom code, and `.ail` state |

## 4. Preconditions Checklist

Before implementing sync, confirm the IDE integration can do the following.

- [ ] Read project-local files under `.ail/`
- [ ] Detect whether `.ail/source.ail` exists
- [ ] Read and parse `.ail/manifest.json` if present
- [ ] Resolve project root consistently
- [ ] Distinguish managed zones from user zones
- [ ] Write files only after conflict checks complete
- [ ] Refresh file tree and editor state after sync
- [ ] Surface blocking errors clearly to the user

## 5. Directory and Ownership Checklist

The IDE must understand the standard AIL project ownership model.

### Managed Zones

Compiler-managed paths typically include:

```text
src/views/generated/
src/router/generated/
backend/generated/
src/ail_generated/
```

Managed zone rules:

- [ ] Treat files under managed roots as rebuildable artifacts
- [ ] Allow overwrite and delete only through sync workflow
- [ ] Prevent casual direct editing where possible
- [ ] Mark files visually as generated if IDE supports decorations

### User Zones

User-managed paths typically include:

```text
src/custom/
src/extensions/
src/theme/
backend/custom/
```

User zone rules:

- [ ] Never let cloud sync overwrite user-zone files
- [ ] Never include user-zone paths in manifest-managed file writes
- [ ] Surface protocol violation if cloud output targets user zones

## 6. Source Handling Checklist

### AIL Source Read Path

- [ ] Read canonical AIL from `.ail/source.ail`
- [ ] Treat `.ail/source.ail` as the only compile source sent to cloud
- [ ] Do not derive compile source from generated files
- [ ] Do not treat generated code as editable truth source

### Optional Preflight Checks

- [ ] Verify source file exists before compile request
- [ ] Warn if source file is empty
- [ ] Validate project is AIL-managed before invoking sync actions

## 7. Cloud Compile Request Checklist

The IDE should call the cloud compile API using the v1 contract.

### Full Compile

- [ ] Send `project_id`
- [ ] Send `mode = full`
- [ ] Send `ail_source`
- [ ] Send `client_manifest_version` if local manifest exists
- [ ] Send `client_build_id` if known
- [ ] Pass compile options such as `include_artifact` or `dry_run` only when supported

### Patch Compile

- [ ] Only use patch compile if the IDE explicitly supports scoped compile UX
- [ ] Provide `target.type` and `target.name`
- [ ] Send `ail_patch`
- [ ] Keep patch compile aligned with v1 API constraints

### Request Safety Checklist

- [ ] Never send user-zone file content as compile input
- [ ] Never treat generated file edits as patch source
- [ ] Log request metadata for debugging without leaking private source unnecessarily

## 8. Response Handling Checklist

The IDE must expect the following response payloads from successful compile responses.

| Field | Required | Use |
| --- | --- | --- |
| `build_id` | yes | Build identity and conflict backup pathing |
| `files` | yes | Files to add or overwrite in managed zones |
| `deleted_files` | yes | Files to delete from managed zones |
| `manifest` | yes | New sync contract |
| `diff_summary` | yes | UI summary and sync preview |
| `artifact` | optional | Download integration if enabled |

### Response Validation Checklist

- [ ] Verify `status = ok`
- [ ] Verify `manifest` exists
- [ ] Verify all returned file paths are inside managed roots
- [ ] Verify hashes exist for all managed files
- [ ] Reject or block sync if response attempts user-zone writes

## 9. Manifest Handling Checklist

The IDE must treat `.ail/manifest.json` as the local synchronization contract.

- [ ] Load current manifest before sync
- [ ] Compare local manifest version with cloud response manifest version
- [ ] Use manifest file hashes for drift detection
- [ ] Do not update local manifest before sync is accepted and file writes succeed
- [ ] Replace local manifest only after all file operations finish successfully

### Manifest Write Rules

- [ ] Write manifest atomically if possible
- [ ] Avoid partial manifest updates
- [ ] If sync fails mid-way, do not commit new manifest state

## 10. Conflict Detection Checklist

Use the protocol rule:

```text
local_sha != manifest_sha
AND
cloud wants to update same file
```

### Detection Steps

- [ ] For each incoming managed file, compute local file hash if file exists
- [ ] Compare local file hash with manifest hash
- [ ] Mark conflict if local hash differs and cloud wants to update same path
- [ ] Apply the same logic for delete operations affecting drifted managed files

### Conflict Levels

| Level | Meaning | Expected IDE Behavior |
| --- | --- | --- |
| Level 1 | Safe overwrite | Auto-apply sync |
| Level 2 | Local drift detected | Prompt user, allow backup-and-overwrite |
| Level 3 | Hard conflict | Block silent sync, require explicit resolution |

## 11. Conflict Resolution UX Checklist

The IDE must support these user actions.

- [ ] Overwrite local version
- [ ] Keep local backup and continue
- [ ] Cancel sync

### Backup Convention

Recommended backup path:

```text
.ail/conflicts/<build_id>/...
```

Example:

```text
.ail/conflicts/build_20260316_001/src/views/generated/Home.local.vue
```

### UX Rules

- [ ] Never silently overwrite locally modified managed files
- [ ] Show conflicting file path
- [ ] Show conflict level
- [ ] Explain whether incoming operation is overwrite or delete
- [ ] Make cancel safe and non-destructive

## 12. Managed File Apply Checklist

After conflict resolution, the IDE may apply sync to managed zones.

### Write Phase

- [ ] Create directories for managed files if missing
- [ ] Write incoming files to managed roots only
- [ ] Delete managed files listed in `deleted_files` if deletion is accepted
- [ ] Never touch user-zone files

### Safety Rules

- [ ] Do not apply partial overwrite without tracking failure state
- [ ] Prefer transactional ordering where possible
- [ ] If file write fails, stop manifest update

## 13. Post-Sync Refresh Checklist

After successful sync:

- [ ] Write new `.ail/manifest.json`
- [ ] Optionally write `.ail/last_build.json`
- [ ] Refresh file tree
- [ ] Refresh open editor buffers if generated files changed
- [ ] Re-run language service or diagnostics if needed
- [ ] Update UI badges or status indicators for generated files
- [ ] Show sync result summary from `diff_summary`

## 14. IDE State and Visual Affordances

Recommended IDE behaviors:

| Feature | Recommendation |
| --- | --- |
| Generated file badge | Mark generated files visually |
| Read-only hint | Warn before editing managed files |
| Conflict panel | Show all conflicts before sync apply |
| Build summary panel | Show build id, manifest version, diff summary |
| Sync status | Show success, failure, or cancelled state |

## 15. Error Handling Checklist

The IDE should map API and local sync failures into actionable user messages.

### API Errors

- [ ] Handle invalid request responses
- [ ] Handle invalid AIL responses
- [ ] Handle manifest version conflict responses
- [ ] Handle missing project or build responses
- [ ] Handle internal errors without corrupting local state

### Local Sync Errors

- [ ] Handle unreadable manifest
- [ ] Handle file write failure
- [ ] Handle backup write failure
- [ ] Handle path validation failure
- [ ] Handle user-zone overwrite attempt as protocol violation

## 16. Suggested Implementation Sequence

Recommended implementation order:

1. project root and `.ail/source.ail` detection
2. cloud compile request client
3. response validation and managed path filtering
4. manifest loading and conflict detection
5. conflict UX and resolution actions
6. managed file apply pipeline
7. post-sync refresh and UI polish

## 17. Review Checklist

Use this section during implementation review.

- [ ] The IDE reads `.ail/source.ail` as compile truth
- [ ] The IDE never syncs into user zones
- [ ] The IDE validates cloud paths before write
- [ ] The IDE compares local file state against manifest before overwrite
- [ ] The IDE supports overwrite, backup-and-overwrite, and cancel
- [ ] The IDE does not update manifest on failed or cancelled sync
- [ ] The IDE refreshes local state after accepted sync
- [ ] Generated files are visually distinguishable from custom files

## 18. Non-Goals

This checklist does not require the IDE to implement:

- reverse code-to-AIL conversion
- AST merge
- collaborative sync
- semantic patch planning
- compiler hosting

## 19. Exit Criteria

An IDE integration may be considered v1-ready when:

- [ ] full compile flow works end-to-end
- [ ] manifest-aware sync works for managed zones
- [ ] conflict detection is enforced before overwrite
- [ ] conflict UX supports backup and cancel
- [ ] generated files refresh correctly in the workspace
- [ ] benchmark and compiler rules are not bypassed by the integration

## 20. Quick Reference

```text
Truth source: .ail/source.ail
Managed zones: compiler-owned, overwriteable through sync
User zones: never cloud-overwritten
Manifest: local sync contract
Conflict rule: local_sha != manifest_sha AND cloud updates same file
Default principle: never silently overwrite locally modified managed files
```
