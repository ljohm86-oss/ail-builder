# Trial Fix Investigation 2026-03-17

## 1. Purpose

This document records the code-level investigation behind the first-user trial friction identified in:

- `/Users/carwynmac/ai-cl/testing/results/first_user_trial_summary_20260317.md`
- `/Users/carwynmac/ai-cl/TRIAL_FIX_PLAN_20260317.md`

The goal is to answer one narrow question:

- why does the frozen-profile golden path currently require `repair` immediately after `generate`?

This is not a broad generator-quality review.

## 2. Investigated Path

The investigation focused on the CLI golden path:

```text
ail init
  -> ail generate
  -> ail diagnose
  -> ail repair
  -> ail compile --cloud
  -> ail sync
```

Code paths inspected:

- `/Users/carwynmac/ai-cl/cli/ail_cli.py`
- `/Users/carwynmac/ai-cl/cli/cloud_client.py`
- `/Users/carwynmac/ai-cl/cli/source_normalizer.py`
- `/Users/carwynmac/ai-cl/cli/skill_bridge.py`
- `/Users/carwynmac/ai-cl/testing/repair_smoke_runner.py`

## 3. Reproduction

Minimal reproduction command:

```bash
tmpdir=$(mktemp -d /tmp/ail_sys_mismatch.XXXXXX)
cd "$tmpdir"
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli init .
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli generate "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。"
PYTHONPATH=/Users/carwynmac/ai-cl python3 -m cli diagnose .ail/source.ail --requirement "做一个 AI SaaS 官网，包含首页、功能介绍、FAQ、联系我们。" --json
```

Observed generated source:

```ail
^SYS[LandingProject]
#PROFILE[landing]
@PAGE[Home,/]
#UI[landing:Header]{}
#UI[landing:Hero]{}
#UI[landing:FeatureGrid]{}
#UI[landing:CTA]{}
#UI[landing:Footer]{}
#UI[landing:Contact]{}
```

Observed diagnose result:

```json
{
  "status": "validation_failed",
  "diagnosis": {
    "compile_recommended": "no",
    "unsupported_constructs": [
      "^SYS[LandingProject]"
    ]
  }
}
```

This directly reproduces the exact first-pass mismatch seen in the controlled frozen-profile trials.

## 4. Findings

### Finding A. `generate` persists `^SYS[...]` into `.ail/source.ail`

`/Users/carwynmac/ai-cl/cli/ail_cli.py:100`

`cmd_generate()` calls `AILCloudClient.generate_ail()` and writes its output directly to `.ail/source.ail`.

There is no post-generate validation or source cleanup step before persistence.

### Finding B. The CLI fallback generator explicitly emits `^SYS[...]`

`/Users/carwynmac/ai-cl/cli/cloud_client.py:206`

The local fallback generator returns first lines such as:

- `^SYS[LandingProject]`
- `^SYS[EcomProject]`
- `^SYS[AfterSalesProject]`
- `^SYS[AppProject]`

This means the CLI itself can generate AIL that its own diagnose path later rejects.

### Finding C. Diagnose does not accept `^SYS[...]` as a valid construct

`/Users/carwynmac/ai-cl/testing/repair_smoke_runner.py:81`

The accepted top-level AIL grammar is currently limited to:

- `#PROFILE[...]`
- `>DB_TABLE[...]`
- `@API[...]`
- `@PAGE[...]`
- `#UI[...]`
- `#FLOW[...]`

`^SYS[...]` is not included in `AIL_LINE_RE`, so it falls through into `unsupported_constructs`.

### Finding D. Compile has its own normalization layer

`/Users/carwynmac/ai-cl/cli/source_normalizer.py:26`

`normalize_for_current_compile()` is only used on the compile path. It:

- removes `#FLOW[...]`
- normalizes bare `#UI[...]` into `#UI[...]{}`
- inserts `^SYS[CLIProject]` if missing

So compile is already operating on a normalized view of the source, not the raw source that diagnose checks.

### Finding E. The mismatch is structural, not random

The current system semantics are:

- generate may output `^SYS[...]`
- diagnose treats `^SYS[...]` as unsupported
- repair removes or rewrites enough structure to produce acceptable AIL
- compile normalizes again before sending to the current compiler

That means the same logical project can be:

- rejected by diagnose
- accepted after repair
- and still compiled successfully later

This is why the first-user trial felt rough even though the system was operational.

## 5. Root Cause

The root cause is a cross-layer contract mismatch:

| Layer | Current expectation |
| --- | --- |
| generate | `^SYS[...]` is part of emitted AIL |
| diagnose | `^SYS[...]` is unsupported |
| compile | `^SYS[...]` is compiler-compatibility metadata and may be inserted automatically |
| repair | produces AIL acceptable to diagnose, often without preserving the original `^SYS[...]` line |

The platform currently lacks a single answer to this question:

- Is `^SYS[...]` part of user-owned AIL source, or is it compiler-only metadata?

Right now different layers answer that differently.

## 6. Important Secondary Signals

### Secondary Signal A. `ail init` also seeds `^SYS[...]`

`/Users/carwynmac/ai-cl/cli/ail_cli.py:90`

The default source template written by `ail init` begins with:

```ail
^SYS[Project]
```

So even the starting template is already on the side of “`^SYS[...]` belongs in source”.

### Secondary Signal B. The compiler/server side still appears to expect `^SYS[...]`

Repo-wide `^SYS[` search shows strong usage in:

- `/Users/carwynmac/ai-cl/ail_engine_v4.py`
- `/Users/carwynmac/ai-cl/ail_server_v5.py`
- `/Users/carwynmac/ai-cl/profile_examples/*.ail`

This suggests we should not do a broad removal at the compiler layer as a first fix.

### Secondary Signal C. Benchmark artifacts also include `^SYS[...]`

Generated benchmark artifacts under:

- `/Users/carwynmac/ai-cl/benchmark/results/latest/artifacts/`

contain `^SYS[...]` lines.

This reinforces that `^SYS[...]` is currently part of the compiler-facing AIL shape, even if the diagnostic path disagrees.

## 7. Candidate Fix Options

### Option A. Narrow CLI generate-side source cleanup

Interpretation:

- `.ail/source.ail` should contain diagnose-compatible user source
- `^SYS[...]` should be treated as compiler-facing metadata, not first-class user source for the v1 golden path

Implementation shape:

- after `generate`, strip or rewrite `^SYS[...]` before writing `.ail/source.ail`
- keep compile-side normalization unchanged for now

Benefits:

- directly fixes first-pass user friction
- narrow blast radius
- avoids weakening diagnose semantics

Risks:

- may create drift between `.ail/source.ail` and compiler-facing AIL shape
- may require a tiny compatibility note in docs

### Option B. Teach diagnose to tolerate `^SYS[...]`

Interpretation:

- `^SYS[...]` is a valid top-level construct and diagnose should stop rejecting it

Implementation shape:

- extend diagnostic parser to recognize `^SYS[...]`
- possibly update repair smoke logic and related test runners

Benefits:

- smallest apparent user-facing change
- keeps source closer to current compiler-facing shape

Risks:

- broadens diagnostic grammar
- touches governance logic used across multiple testing runners
- may blur the distinction between user-owned AIL and compiler metadata

### Option C. Keep behavior and normalize the story

Interpretation:

- `generate -> diagnose -> repair` is simply the intended golden path

Implementation shape:

- adjust quickstart, CLI messaging, and operator guidance

Benefits:

- lowest engineering cost

Risks:

- preserves a poor first-run feel
- does not actually reduce friction
- weakens confidence in first-pass generation

## 8. Recommendation

Recommended order:

### 1. Prefer Option A first

Make the smallest possible CLI-side change so `.ail/source.ail` is written in a diagnose-compatible shape for the frozen-profile path.

Why this is the best first move:

- it targets the exact user-facing friction
- it avoids reopening compiler semantics
- it keeps the fix narrow and reversible

### 2. Keep compile normalization unchanged for now

Do not try to redesign compiler-side `^SYS[...]` semantics in the same change.

That would turn a narrow UX fix into a cross-system rewrite.

### 3. Use Option B only if Option A proves unsafe

If removing or rewriting `^SYS[...]` on the generate-side causes downstream issues, then the fallback is to make diagnose accept it explicitly.

### 4. Treat Option C only as temporary communication fallback

If no code fix lands immediately, update quickstart and CLI messaging so users are not surprised by the repair step.

## 9. Minimum Validation After Fix

Re-run the same three frozen-profile controlled scenarios:

1. `landing`
2. `ecom_min`
3. `after_sales`

Success target:

- `generate -> diagnose` returns success without requiring repair on these standard examples

Minimum no-regression checks:

- `bash /Users/carwynmac/ai-cl/testing/run_cli_checks.sh`
- `bash /Users/carwynmac/ai-cl/testing/repair_smoke.sh`
- `bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh`

## 10. One-Line Conclusion

The first-pass trial friction is caused by a real contract mismatch: the CLI generate path persists `^SYS[...]` into user source, while the diagnose path rejects that same construct. The narrowest high-value fix is to make the CLI golden path write diagnose-compatible source before compile normalization adds compiler-facing compatibility metadata.
