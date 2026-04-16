# Benchmark Harness

This benchmark harness validates the current profile surface without changing profile behavior.

## Scope

- `landing`
- `ecom_min`
- `after_sales`
- `app_min` (probe)

## Status Layers

- `frozen`: derived from `/Users/carwynmac/ai-cl/benchmark/benchmark_baseline.json`
- `experimental`: derived from `/Users/carwynmac/ai-cl/benchmark/benchmark_baseline.json`

## Files

- `tasks_v0_1.json`: fixed task set
- `benchmark_baseline.json`: release baseline and experimental policy
- `BENCHMARK_POLICY.md`: human-readable policy
- `mock_llm_server.py`: optional local deterministic OpenAI-compatible mock
- `run_benchmark.py`: batch runner
- `run_benchmark.sh`: shell entry
- `results/latest/benchmark_results.json`: structured results
- `results/latest/report.md`: human-readable summary

## What it does

1. monkeypatches `httpx.AsyncClient` inside the benchmark process with deterministic profile fixtures
2. runs each task through `/generate_ail`
3. compiles the generated AIL through `/compile`
4. checks expected profile, keywords, and generated routes
5. runs existing gate scripts:
   - `verify_profiles.sh`
   - `verify_app_profile.sh`
   - `verify_app_profile_smoke.sh`

Current release baseline:

- all `landing` tasks
- all `ecom_min` tasks
- all `after_sales` tasks
- `app_min` remains experimental

## Run

```bash
bash /Users/carwynmac/ai-cl/benchmark/run_benchmark.sh
```

## Notes

- no external network is used
- the runner does not require binding an extra local port
- benchmark is separate from the formal frozen gate
- tasks are deterministic because prompts are resolved by fixed local profile fixtures
