# Context Tokenizer Repo-Scale Report (2026-04-29)

This report captures one repo-scale comparison between heuristic token estimates and tokenizer-backed metrics for the `context` workflow.

Benchmark target:

- directory: `/Users/carwynmac/ai-cl/cli`
- platform: macOS
- Python: `3.9.6`
- file count: `10`
- character count: `925,337`
- line count: `18,124`
- tokenizer model: `cl100k_base`

## Commands Under Test

```bash
PYTHONPATH="$PWD" python3 -m cli context compress --preset codebase --input-dir /Users/carwynmac/ai-cl/cli --tokenizer-backend heuristic --json
PYTHONPATH="$PWD" python3 -m cli context compress --preset codebase --input-dir /Users/carwynmac/ai-cl/cli --tokenizer-backend auto --json
PYTHONPATH="$PWD" python3 -m cli context compress --preset codebase --input-dir /Users/carwynmac/ai-cl/cli --tokenizer-backend tiktoken --tokenizer-model cl100k_base --json
```

## Timing

| Path | Runs | Average |
|---|---|---:|
| `heuristic` | `6296.68 ms`, `255.38 ms`, `251.19 ms` | `2267.75 ms` |
| `auto` | `254.65 ms` | `254.65 ms` |
| `tiktoken` | `252.07 ms`, `253.35 ms`, `255.91 ms` | `253.78 ms` |

Notes:

- the first heuristic run showed one cold-start outlier at `6296.68 ms`
- the steady-state timing for both `heuristic` and `tiktoken` settled around `250 ms`
- in this environment, `auto` selected `tiktoken` and did not fall back

## Metric Comparison

| Metric | Heuristic | `tiktoken` (`cl100k_base`) |
|---|---:|---:|
| Source tokens | `231,335` | `192,815` |
| Skeleton tokens | `4,872` | `5,280` |
| Tokens saved | `226,463` | `187,535` |
| Reduction ratio | `0.0211` | `0.0274` |

Interpretation:

- heuristic estimated a larger source token count than `tiktoken`
- heuristic also estimated a slightly smaller skeleton token count than `tiktoken`
- as a result, heuristic overstated total token savings in this sample
- `tiktoken` remains the better choice when operators want one tokenizer-backed measurement for reporting

## Delta View

| Delta | Value |
|---|---:|
| Heuristic source minus `tiktoken` source | `38,520` |
| Heuristic skeleton minus `tiktoken` skeleton | `-408` |
| Heuristic saved minus `tiktoken` saved | `38,928` |

## Backend Selection Behavior

Observed backend behavior:

| Requested backend | Actual backend | Fallback used |
|---|---|---:|
| `heuristic` | `heuristic` | `false` |
| `auto` | `tiktoken` | `false` |
| `tiktoken` | `tiktoken` | `false` |

This confirms that:

- `auto` now prefers tokenizer-backed metrics when `tiktoken` is available
- `heuristic` remains useful as an explicit low-dependency baseline
- both metric families can be compared in the same payload when tokenizer support exists

## Practical Takeaways

- for repo-scale code directories, tokenizer-backed metrics produce more conservative and more realistic token savings than `chars / 4`
- the difference is large enough to matter in reporting: this sample differed by `38,928` saved tokens between the two methods
- `auto` is now a good default when `tiktoken` is installed
- `heuristic` remains a safe fallback when packaging or environment constraints prevent tokenizer installation
