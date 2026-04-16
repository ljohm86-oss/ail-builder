# AIL CLI Implementation Guide

## 1. Purpose

This document is an implementation guide for CLI and toolchain developers building the AIL command-line interface.

Its goal is to turn the AIL v1 protocol and workflow specifications into an executable engineering plan for a real `ail` command-line tool.

The CLI is the primary developer entrypoint for the AIL platform and must follow these platform rules:

- AIL is the single source of truth.
- Generated files are rebuildable artifacts.
- Manifest controls sync.
- Custom zones are never overwritten.

This guide is intended to be used as:

- an implementation guide
- a code review checklist
- an engineering task decomposition
- a release-readiness checklist for CLI delivery

## 2. Scope

### In Scope

- `ail init`
- `ail generate`
- `ail diagnose`
- `ail repair`
- `ail compile`
- `ail sync`
- `ail conflicts`
- local `.ail/` directory initialization
- `.ail/source.ail` management
- cloud compile request and response handling
- manifest read and write flow
- managed zone synchronization
- conflict detection and terminal interaction

### Out of Scope

- IDE user interface
- compiler server implementation
- collaborative editing
- code-to-AIL reverse sync
- AST merge
- runtime or app execution implementation

## 3. CLI Architecture Overview

```text
User Command
    ↓
CLI Command Dispatcher
    ↓
AIL Project Context Loader
    ↓
Source / Manifest / Conflict Services
    ↓
Cloud Compile API Client
    ↓
Managed File Sync
    ↓
Terminal Output + Exit Code
```

### Responsibility Split

| Layer | Responsibility |
| --- | --- |
| Command dispatcher | Parse args, resolve command, route execution |
| Project context loader | Locate project root, `.ail/`, managed roots, source file |
| Source service | Read and write `.ail/source.ail` |
| Manifest service | Load, validate, and persist `.ail/manifest.json` |
| Conflict service | Detect conflicts, classify severity, drive resolution flow |
| API client | Call cloud compile endpoints |
| Sync service | Apply managed file changes safely |
| Output layer | Print user-facing summaries and exit with stable codes |

## 4. Command Set Checklist

The CLI v1 command set should include:

| Command | Primary Purpose |
| --- | --- |
| `ail init` | Initialize an AIL project structure |
| `ail generate` | Generate AIL from a requirement |
| `ail diagnose` | Validate AIL against current skill/system boundaries |
| `ail repair` | Repair near-valid or drifted AIL |
| `ail compile` | Compile AIL through cloud compile API |
| `ail sync` | Apply managed files into the local project |
| `ail conflicts` | Inspect and review sync conflicts |

Implementation checklist:

- [ ] Commands have clear arg parsing and help text
- [ ] Commands share project context loading logic
- [ ] Commands fail with actionable error messages
- [ ] Commands return stable exit codes
- [ ] Commands avoid duplicating manifest and sync logic

## 5. Project Context Loading

The CLI must consistently resolve AIL project context before running stateful commands.

### Required Detection

- [ ] Resolve current project root
- [ ] Detect `.ail/` directory
- [ ] Detect `.ail/source.ail`
- [ ] Detect `.ail/manifest.json` if present
- [ ] Identify managed roots and user zones

### Failure Behavior

- [ ] If project root cannot be resolved, stop with clear error
- [ ] If `.ail/` is missing for non-`init` commands, stop with project-not-initialized error
- [ ] If source file is missing for compile-related commands, fail fast

## 6. `ail init` Implementation Checklist

Purpose: initialize an AIL-managed project.

### Expected Responsibilities

- [ ] Create `.ail/`
- [ ] Create `.ail/source.ail`
- [ ] Create placeholder `.ail/manifest.json` if policy allows
- [ ] Optionally create skeleton managed/user directories
- [ ] Print next-step guidance

### Suggested Output

```text
Initialized AIL project.
Created:
- .ail/source.ail
- .ail/manifest.json
Next steps:
- edit .ail/source.ail
- run ail compile --cloud
```

## 7. `ail generate` Implementation Checklist

Purpose: generate AIL from requirement input using the approved generator workflow.

### Responsibilities

- [ ] Accept requirement text from arg, file, stdin, or interactive prompt
- [ ] Produce exactly one AIL program
- [ ] Enforce single-profile expectation
- [ ] Write output to `.ail/source.ail` unless dry-run mode is used
- [ ] Optionally print generated AIL to terminal

### Safety Rules

- [ ] Do not write generated files into managed zones
- [ ] Do not treat generated code as source input
- [ ] Preserve source formatting predictably

## 8. `ail diagnose` Implementation Checklist

Purpose: evaluate AIL validity against current system boundaries.

### Responsibilities

- [ ] Read source from explicit input or `.ail/source.ail`
- [ ] Run the diagnostic workflow
- [ ] Print structured diagnosis summary
- [ ] Exit non-zero when validation fails if strict mode is requested

### Minimum Output Expectations

- [ ] `valid`
- [ ] `compile_recommended`
- [ ] `detected_profile`
- [ ] issue categories
- [ ] short conclusion

## 9. `ail repair` Implementation Checklist

Purpose: repair near-valid AIL into a compile candidate when possible.

### Responsibilities

- [ ] Accept original requirement and original AIL input
- [ ] Optionally accept diagnosis report as input context
- [ ] Produce only repaired AIL
- [ ] Preserve intent while normalizing to supported boundaries
- [ ] Optionally write repaired source back to `.ail/source.ail`

### Safety Rules

- [ ] Do not invent unsupported tokens
- [ ] Do not output multiple AIL programs
- [ ] Do not rewrite beyond supported repair scope

## 10. `ail compile` Implementation Checklist

Purpose: compile `.ail/source.ail` using the cloud compile API.

### Responsibilities

- [ ] Load `.ail/source.ail`
- [ ] Load `.ail/manifest.json` if present
- [ ] Send `project_id`, `ail_source`, client manifest version, and build id when available
- [ ] Support full compile in v1
- [ ] Optionally support patch compile later behind explicit mode
- [ ] Store latest build metadata if compile succeeds

### Compile Request Checklist

- [ ] Never send generated file content as compile truth
- [ ] Do not proceed if source file missing
- [ ] Validate request body structure before sending
- [ ] Surface API errors cleanly

## 11. `ail sync` Implementation Checklist

Purpose: apply compile output into managed zones.

### Responsibilities

- [ ] Consume compile response or last successful build payload
- [ ] Validate returned file paths are within managed roots
- [ ] Compare local file state against manifest
- [ ] Detect overwrite and delete conflicts
- [ ] Apply managed file writes and deletes after resolution
- [ ] Update `.ail/manifest.json` only after successful sync

### Sync Safety Checklist

- [ ] Never write to user zones
- [ ] Never silently overwrite drifted managed files
- [ ] Never update manifest before successful apply
- [ ] Stop on failed write or unresolved conflict

## 12. `ail conflicts` Implementation Checklist

Purpose: expose current conflict state to the user.

### Suggested Capabilities

- [ ] Show unresolved conflicts from latest sync attempt
- [ ] Print file path and conflict level
- [ ] Show available resolution actions
- [ ] Show backup paths if already created

### Suggested Example Output

```text
Conflict detected: src/views/generated/Home.vue
Level: 2
Available actions:
- overwrite
- backup-and-overwrite
- cancel
```

## 13. Manifest Service Checklist

The CLI must treat `.ail/manifest.json` as the local synchronization contract.

- [ ] Parse manifest safely
- [ ] Validate required fields
- [ ] Verify managed file entries only target managed roots
- [ ] Expose manifest version and current build id to compile and sync services
- [ ] Write manifest atomically where possible

### Manifest Update Rules

- [ ] Update only after accepted sync completes successfully
- [ ] Do not update on cancelled sync
- [ ] Do not update on partial failure

## 14. Conflict Detection and Resolution Checklist

The CLI must use the protocol rule:

```text
local_sha != manifest_sha
AND
cloud wants to update same file
```

### Required Behavior

- [ ] Detect conflicts before any destructive file operation
- [ ] Classify Level 1, Level 2, Level 3
- [ ] Provide overwrite, backup-and-overwrite, and cancel choices
- [ ] Preserve local backup under `.ail/conflicts/<build_id>/...` when requested

### Terminal UX Requirements

- [ ] Explain which file conflicts
- [ ] Explain what cloud wants to do
- [ ] Explain what local drift was detected
- [ ] Make the default behavior safe rather than destructive

## 15. Managed File Sync Checklist

### File Apply Phase

- [ ] Create parent directories as needed
- [ ] Write returned files into managed zones only
- [ ] Delete only manifest-owned files listed by cloud response
- [ ] Refuse user-zone writes even if cloud returns them

### Failure Handling

- [ ] If one file write fails, stop and report failure
- [ ] Preserve enough state for retry or inspection
- [ ] Do not commit new manifest on failed apply

## 16. Output and Exit Code Guidelines

The CLI should be scriptable and human-readable.

### Output Principles

- [ ] Print concise summaries by default
- [ ] Print structured detail in verbose mode
- [ ] Keep errors machine-parseable where practical

### Suggested Exit Code Patterns

| Exit Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | General failure |
| `2` | Invalid CLI usage |
| `3` | Validation or diagnosis failure |
| `4` | Conflict detected and unresolved |
| `5` | Remote API failure |

## 17. Logging and Observability Checklist

Recommended CLI-visible metadata:

- [ ] `project_id`
- [ ] `build_id`
- [ ] `manifest_version`
- [ ] diff summary
- [ ] conflict count
- [ ] sync outcome

Recommended developer logs:

- [ ] request metadata
- [ ] response status
- [ ] file operation failures
- [ ] backup path creation events

## 18. Suggested Implementation Order

Recommended order for building the CLI:

1. project context loader
2. `ail init`
3. source file handling
4. `ail generate`, `ail diagnose`, `ail repair`
5. cloud API client
6. `ail compile`
7. manifest service
8. conflict detection service
9. `ail sync`
10. `ail conflicts`
11. output polishing and exit code cleanup

## 19. Review Checklist

Use this during engineering review.

- [ ] CLI reads `.ail/source.ail` as the truth source
- [ ] CLI never writes cloud output into user zones
- [ ] CLI validates compile response paths before sync
- [ ] CLI enforces manifest-aware conflict detection
- [ ] CLI supports overwrite, backup, and cancel
- [ ] CLI avoids manifest update on failed or cancelled sync
- [ ] CLI returns stable exit codes
- [ ] CLI output is understandable in both interactive and scripted use

## 20. Non-Goals

This implementation guide does not require:

- compiler implementation
- runtime bootstrapping
- editor UI integration
- collaborative workflow support
- code-to-AIL reverse engineering
- AST merge

## 21. Exit Criteria

A CLI implementation may be considered v1-ready when:

- [ ] `ail init`, `ail generate`, `ail diagnose`, `ail repair`, `ail compile`, `ail sync`, and `ail conflicts` exist
- [ ] compile flow reads `.ail/source.ail` and uses cloud API contract correctly
- [ ] sync is manifest-aware and respects managed vs user zones
- [ ] conflict handling is explicit and safe
- [ ] generated artifacts are treated as rebuildable outputs rather than editable truth
- [ ] command output and exit codes are stable enough for CI and scripting

## 22. Quick Reference

```text
Truth source: .ail/source.ail
Managed zones: compiler-owned and sync-managed
User zones: never overwritten by cloud sync
Manifest: local sync contract
Compile API: primary remote integration surface
Conflict rule: local_sha != manifest_sha AND cloud updates same file
CLI priority: safe automation with explicit conflict handling
```
