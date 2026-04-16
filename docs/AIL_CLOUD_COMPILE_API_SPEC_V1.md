# AIL Cloud Compile API Spec v1

## 1. Overview

This document defines the formal API contract for the AIL Cloud Compiler service.

The API is intended to serve as the unified integration surface for:

- CLI clients
- IDE integrations
- future AIL Studio or web-based tooling
- internal orchestration services

This specification should be read together with:

- `/Users/carwynmac/ai-cl/docs/AIL_CLOUD_SYNC_PROTOCOL_V1.md`
- `/Users/carwynmac/ai-cl/docs/AIL_MANIFEST_SPEC_V1.md`
- `/Users/carwynmac/ai-cl/docs/AIL_CONFLICT_RESOLUTION_GUIDE.md`

### Core Principles

- AIL is the single source of truth.
- Generated files are rebuildable artifacts.
- API responses must include enough data for sync and conflict detection.

### Scope

This document defines:

- compile request and response formats
- patch compile request and response formats
- build lookup APIs
- project-level build listing APIs
- artifact retrieval APIs
- error semantics
- compatibility and versioning rules

This document does not define:

- internal compiler implementation
- deployment topology
- authentication implementation details
- rollback execution behavior

## 2. API Design Goals

The v1 API must support the following engineering goals.

| Goal | Description |
| --- | --- |
| Full compile support | Compile a full AIL source into deterministic managed artifacts |
| Patch compile extensibility | Support scoped compile requests without redefining the base protocol |
| Manifest-aware sync | Return enough data for local sync and conflict detection |
| Deterministic artifact return | Ensure identical compile inputs produce predictable artifact outputs |
| Build history compatibility | Preserve identifiers and metadata needed for future build history and rollback |

## 3. Base Conventions

### 3.1 Base Path

All v1 endpoints are rooted at:

```text
/api/v1
```

### 3.2 Content Type

Requests and responses must use:

```text
Content-Type: application/json
```

Artifact download responses may use a different content type if the artifact is delivered as binary or archive data.

### 3.3 Authentication

Authentication is implementation-defined in v1 and out of scope for this specification.

Possible deployment choices may include:

- bearer token
- session-based auth
- internal service-to-service auth

The API contract must remain valid regardless of auth mechanism.

### 3.4 Time Format

All timestamps must use ISO 8601 UTC format.

Example:

```text
2026-03-16T08:30:00Z
```

### 3.5 ID Naming Conventions

| Field | Meaning | Example |
| --- | --- | --- |
| `project_id` | Stable project identifier | `proj_001` |
| `build_id` | Unique build identifier | `build_20260316_001` |
| `artifact_id` | Optional artifact identifier | `artifact_build_20260316_001` |

### 3.6 Response Envelope

All JSON responses should use a consistent envelope.

Successful response shape:

```json
{
  "status": "ok",
  "data": {}
}
```

Error response shape:

```json
{
  "status": "error",
  "error": {
    "code": "compile_invalid_ail",
    "message": "AIL source failed validation.",
    "details": {}
  }
}
```

## 4. Endpoint Summary

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/compile` | Execute full compile from AIL source |
| `POST` | `/api/v1/compile/patch` | Execute scoped patch compile |
| `GET` | `/api/v1/build/{build_id}` | Query build metadata and summary |
| `GET` | `/api/v1/project/{project_id}` | Query project-level metadata |
| `GET` | `/api/v1/project/{project_id}/builds` | List builds for a project |
| `GET` | `/api/v1/build/{build_id}/artifact` | Download artifact bundle or generated output package |

## 5. POST /api/v1/compile

This endpoint performs a full compile using the provided AIL source.

### 5.1 Request Body

```json
{
  "project_id": "proj_001",
  "mode": "full",
  "ail_source": "#PROFILE[landing]\n@PAGE[Home,/]\n...",
  "client_manifest_version": 3,
  "client_build_id": "build_prev_001",
  "options": {
    "include_artifact": false,
    "dry_run": false
  }
}
```

### 5.2 Request Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | string | yes | Stable project identity |
| `mode` | string | yes | Must be `full` for this endpoint |
| `ail_source` | string | yes | Full canonical AIL source |
| `client_manifest_version` | integer | no | Client-side known manifest version |
| `client_build_id` | string | no | Client-side last known build identifier |
| `options.include_artifact` | boolean | no | If true, include downloadable artifact metadata |
| `options.dry_run` | boolean | no | If true, validate and diff without applying persistent build state |

### 5.3 Success Response Example

```json
{
  "status": "ok",
  "data": {
    "build_id": "build_20260316_001",
    "project_id": "proj_001",
    "mode": "full",
    "created_at": "2026-03-16T08:30:00Z",
    "files": [
      {
        "path": "src/views/generated/Home.vue",
        "content": "<template>...</template>",
        "sha256": "abc123"
      }
    ],
    "deleted_files": [],
    "manifest": {
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
    },
    "diff_summary": {
      "added": 1,
      "updated": 0,
      "deleted": 0
    },
    "artifact": null
  }
}
```

### 5.4 Response Requirements

A successful full compile response must include:

1. build metadata
2. generated files
3. deleted file list
4. manifest payload
5. diff summary
6. artifact metadata if requested

## 6. POST /api/v1/compile/patch

This endpoint performs a scoped compile against a specific target.

### 6.1 Request Body Example

```json
{
  "project_id": "proj_001",
  "mode": "patch",
  "target": {
    "type": "page",
    "name": "Home"
  },
  "ail_patch": "@PAGE[Home,/]\n#UI[landing:Hero]",
  "client_manifest_version": 4,
  "client_build_id": "build_20260316_001",
  "options": {
    "include_artifact": false,
    "dry_run": false
  }
}
```

### 6.2 Request Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `project_id` | string | yes | Stable project identity |
| `mode` | string | yes | Must be `patch` for this endpoint |
| `target.type` | string | yes | Patch scope type such as `page`, `route`, or `component` |
| `target.name` | string | yes | Name of target to patch |
| `ail_patch` | string | yes | Patch source payload |
| `client_manifest_version` | integer | no | Client-side manifest version |
| `client_build_id` | string | no | Last known client build id |
| `options.include_artifact` | boolean | no | Include artifact metadata if true |
| `options.dry_run` | boolean | no | Validate patch without persisting build state |

### 6.3 Success Response Example

```json
{
  "status": "ok",
  "data": {
    "build_id": "build_20260316_002",
    "project_id": "proj_001",
    "mode": "patch",
    "target": {
      "type": "page",
      "name": "Home"
    },
    "created_at": "2026-03-16T08:45:00Z",
    "files": [
      {
        "path": "src/views/generated/Home.vue",
        "content": "<template>patched</template>",
        "sha256": "def456"
      }
    ],
    "deleted_files": [],
    "manifest": {
      "project_id": "proj_001",
      "manifest_version": 5,
      "current_build_id": "build_20260316_002",
      "managed_roots": [
        "src/views/generated/",
        "src/router/generated/"
      ],
      "managed_files": {
        "src/views/generated/Home.vue": {
          "sha256": "def456"
        }
      }
    },
    "diff_summary": {
      "added": 0,
      "updated": 1,
      "deleted": 0
    }
  }
}
```

### 6.4 v1 Patch Notes

v1 patch compile is defined for protocol compatibility and future extensibility. Implementations may support only a limited subset of targets in early versions.

## 7. GET /api/v1/build/{build_id}

Returns build metadata and high-level compile results.

### 7.1 Success Response Example

```json
{
  "status": "ok",
  "data": {
    "build_id": "build_20260316_001",
    "project_id": "proj_001",
    "mode": "full",
    "status": "succeeded",
    "created_at": "2026-03-16T08:30:00Z",
    "diff_summary": {
      "added": 1,
      "updated": 0,
      "deleted": 0
    },
    "artifact_available": true,
    "manifest_version": 4
  }
}
```

## 8. GET /api/v1/project/{project_id}

Returns project-level metadata known to the cloud compiler service.

### 8.1 Success Response Example

```json
{
  "status": "ok",
  "data": {
    "project_id": "proj_001",
    "latest_build_id": "build_20260316_002",
    "latest_manifest_version": 5,
    "created_at": "2026-03-10T09:00:00Z",
    "updated_at": "2026-03-16T08:45:00Z"
  }
}
```

## 9. GET /api/v1/project/{project_id}/builds

Lists builds for a project.

### 9.1 Query Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `limit` | integer | no | Maximum number of builds to return |
| `cursor` | string | no | Pagination cursor |
| `mode` | string | no | Filter by `full` or `patch` |

### 9.2 Success Response Example

```json
{
  "status": "ok",
  "data": {
    "items": [
      {
        "build_id": "build_20260316_002",
        "mode": "patch",
        "status": "succeeded",
        "created_at": "2026-03-16T08:45:00Z"
      },
      {
        "build_id": "build_20260316_001",
        "mode": "full",
        "status": "succeeded",
        "created_at": "2026-03-16T08:30:00Z"
      }
    ],
    "next_cursor": null
  }
}
```

## 10. GET /api/v1/build/{build_id}/artifact

Downloads or describes the compiled artifact bundle for a build.

### 10.1 Response Modes

Implementations may support one of two v1-compatible modes:

| Mode | Description |
| --- | --- |
| Redirect or binary stream | Returns a zip/tar artifact directly |
| JSON descriptor | Returns signed URL or artifact metadata |

### 10.2 JSON Descriptor Example

```json
{
  "status": "ok",
  "data": {
    "build_id": "build_20260316_001",
    "artifact_id": "artifact_build_20260316_001",
    "download_url": "https://example.invalid/artifacts/build_20260316_001.zip",
    "expires_at": "2026-03-16T09:30:00Z",
    "sha256": "zipsha123"
  }
}
```

## 11. Response Objects

### 11.1 Generated File Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `path` | string | yes | Project-relative file path |
| `content` | string | yes | Generated file content |
| `sha256` | string | yes | Hash of file content |

### 11.2 Diff Summary Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `added` | integer | yes | Number of newly added managed files |
| `updated` | integer | yes | Number of updated managed files |
| `deleted` | integer | yes | Number of removed managed files |

### 11.3 Build Status Values

| Value | Meaning |
| --- | --- |
| `queued` | Build accepted but not yet started |
| `running` | Build is executing |
| `succeeded` | Build completed successfully |
| `failed` | Build failed |
| `cancelled` | Build was cancelled |

## 12. Error Semantics

The API must provide stable, machine-readable error codes.

### 12.1 Common Error Codes

| Code | Meaning |
| --- | --- |
| `compile_invalid_request` | Request body is malformed or missing required fields |
| `compile_invalid_ail` | AIL source failed validation |
| `compile_unsupported_mode` | Requested compile mode is unsupported |
| `compile_target_not_found` | Patch target does not exist or cannot be resolved |
| `manifest_version_conflict` | Client manifest version is incompatible with server state |
| `project_not_found` | Project id does not exist |
| `build_not_found` | Build id does not exist |
| `artifact_not_available` | Artifact was not produced or is unavailable |
| `internal_error` | Unexpected server-side failure |

### 12.2 Error Response Example

```json
{
  "status": "error",
  "error": {
    "code": "manifest_version_conflict",
    "message": "Client manifest version does not match server manifest state.",
    "details": {
      "client_manifest_version": 3,
      "server_manifest_version": 5,
      "project_id": "proj_001"
    }
  }
}
```

### 12.3 HTTP Status Recommendations

| HTTP Status | Typical Usage |
| --- | --- |
| `200` | Successful GET or compile response |
| `400` | Invalid request body or invalid compile mode |
| `404` | Unknown project, build, or artifact |
| `409` | Manifest or build state conflict |
| `422` | AIL validation failure |
| `500` | Internal compiler or service error |

## 13. Manifest and Sync Requirements

Compile responses must provide enough information for local sync tooling to:

- identify new and updated managed files
- identify deleted managed files
- compare server state against local manifest state
- update `.ail/manifest.json` after accepted sync
- trigger conflict detection before overwriting locally drifted files

This means `files`, `deleted_files`, `manifest`, and `diff_summary` are not optional protocol concepts even if a specific transport optimizes their shape.

## 14. Determinism and Idempotency Guidance

The service should aim for deterministic outputs for equivalent inputs.

Recommended properties:

- same `project_id` + same canonical `ail_source` + same compiler version should produce equivalent managed file set
- `sha256` values must correspond to returned content
- repeated GET queries for the same build should return stable metadata

This specification does not require strict request idempotency keys in v1, but implementations may add them.

## 15. Compatibility and Versioning Rules

### 15.1 API Versioning

This document defines v1 of the API contract.

Version is encoded in the path:

```text
/api/v1
```

### 15.2 Backward Compatibility

Within v1:

- existing response fields must not change meaning silently
- required fields must not be removed
- new optional fields may be added
- new endpoints may be added if they do not break existing clients

### 15.3 Client Compatibility Expectations

Clients should:

- ignore unknown optional fields
- rely only on documented required fields
- treat missing required fields as protocol violation

## 16. Non-Goals for v1

v1 does not define:

- real-time streaming compile
- AST merge APIs
- collaborative locking
- server-side code editing APIs
- reverse compilation from generated code to AIL

## 17. Future Evolution

Likely v2 or later extensions include:

- page-level compile guarantees
- richer patch target taxonomy
- rollback endpoint
- build compare endpoint
- artifact diff endpoint
- signed upload of local diagnostics or conflict snapshots

## 18. Spec Summary

The AIL Cloud Compile API v1 provides a stable contract for cloud compilation and sync-aware clients.

Its job is to return enough structured data for:

- deterministic compile consumption
- manifest-aware synchronization
- conflict detection
- future-compatible build history workflows
