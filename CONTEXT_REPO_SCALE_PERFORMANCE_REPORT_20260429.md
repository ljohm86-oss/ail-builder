# Context Repo-Scale Performance Report (2026-04-29)

This report captures one repo-scale benchmark of the `context` workflow against a real code directory inside this repository:

- target directory: `/Users/carwynmac/ai-cl/cli`
- platform: macOS
- Python: `3.9.6`
- tokenizer backend requested: `heuristic` and `auto`
- tokenizer backend actually used: `heuristic`
- note: `auto` fell back cleanly because `tiktoken` was not installed in this local environment

## Benchmark Target

| Metric | Value |
|---|---:|
| Directory size | `928K` |
| File count | `10` |
| Character count | `925,337` |
| Line count | `18,124` |

## Compression Metrics

Measured command family:

```bash
PYTHONPATH="$PWD" python3 -m cli context compress --preset codebase --input-dir /Users/carwynmac/ai-cl/cli --tokenizer-backend heuristic --json
```

| Metric | Value |
|---|---:|
| Source tokens (heuristic) | `231,335` |
| Skeleton tokens (heuristic) | `4,872` |
| Tokens saved (heuristic) | `226,463` |
| Token reduction ratio | `0.0211` |
| Token direction | `reduced` |

Interpretation:

- in this sample, the skeleton retained about `2.11%` of the estimated source token footprint
- in this sample, the system saved about `97.89%` of the estimated source tokens
- these token values are still heuristic estimates because the local environment did not have `tiktoken`

## Timing Results

| Step | Result |
|---|---:|
| `compress` run 1 | `131.09 ms` |
| `compress` run 2 | `157.13 ms` |
| `compress` run 3 | `126.25 ms` |
| `compress` average | `138.16 ms` |
| `bundle` | `150.86 ms` |
| `inspect` | `60.55 ms` |
| `patch` | `170.66 ms` |
| `apply-check` | `101.82 ms` |
| `patch-apply` | `66.32 ms` |

## Patch / Replay Verification

The benchmark also exercised a real directory patch flow:

1. created a source bundle from `/Users/carwynmac/ai-cl/cli`
2. copied the directory to a temporary candidate tree
3. appended one safe comment line to:
   - `ail_cli.py`
   - `context_compression.py`
4. generated a directory patch
5. ran `context patch-apply --merge-mode reject-conflicts`
6. compared the replayed files against the candidate files

Observed results:

| Metric | Value |
|---|---:|
| Changed paths | `2` |
| Added lines | `4` |
| `apply-check` score | `90` |
| `apply-check` band | `strong` |
| `patch-apply` mode | `directory_restore_plus_overlay` |
| Merge check passed | `true` |
| Replayed edited files matched candidate | `true` |

## Auto Backend Fallback

Measured command family:

```bash
PYTHONPATH="$PWD" python3 -m cli context compress --preset codebase --input-dir /Users/carwynmac/ai-cl/cli --tokenizer-backend auto --json
```

Observed results:

| Metric | Value |
|---|---:|
| Requested backend | `auto` |
| Actual backend | `heuristic` |
| Fallback used | `true` |

This confirms the current fallback path is healthy: `auto` does not fail when tokenizer support is unavailable, and still produces formal metrics.

## Takeaways

- the `context` workflow is fast enough for interactive repo-scale use on a real code directory
- the compression ratio remains strong on a `~925K` character code subtree
- `bundle`, `patch`, `apply-check`, and `patch-apply` all complete quickly in the same environment
- merge-aware replay did not interfere with normal clean replay
- tokenizer-backed metrics remain optional rather than required
