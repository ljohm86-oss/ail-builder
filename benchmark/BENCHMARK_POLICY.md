# Benchmark Policy

## Purpose

This file separates task definitions from release policy.

## Policy Source

- machine-readable policy: `/Users/carwynmac/ai-cl/benchmark/benchmark_baseline.json`

## Current Release Baseline

- `L1-L6`
- `E1-E6`
- `A1-A4`

## Current Experimental Set

- `P1-P4`

## Release Rule

- baseline tasks must all pass
- experimental tasks are observed but do not block release

## Current Interpretation

- `landing`, `ecom_min`, `after_sales` are frozen release profiles
- `app_min` remains experimental and is not part of the release gate
