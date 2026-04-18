# Quickstart For Open-Source Testers

## Purpose

This guide is the shortest path for external testers to verify that AI-CL runs locally and exposes its main CLI surfaces.

## Prerequisites

Minimum assumptions:

- Python `3.10+`
- Git
- a Unix-like shell

Helpful but optional:

- Node.js and npm if you want to build the bundled frontend sample projects

## 1. Clone And Enter The Repo

```bash
git clone <your-github-url> ai-cl
cd ai-cl
export REPO_ROOT="$PWD"
```

## 2. Optional: Create A Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install The Local Python Package

```bash
pip install -e .
```

## 4. Sanity-Check The CLI

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli --help
```

If that works, the CLI entry surface is available.

## 5. Run The Shortest Verified Website Check

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli website check '做一个企业产品官网，包含首页、功能介绍、FAQ、联系我们。' --base-url embedded://local --json
```

What you should expect:

- a JSON payload
- a deliverability judgment for the current website surface
- no crash

## 6. Read The Current Workspace Surface

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli workspace summary --base-url embedded://local
```

This gives a higher-level operator view before you dig into project-specific flows.

## 7. Inspect Durable Customization From A Proof Baseline

```bash
cd "$REPO_ROOT/output_projects/CompanyProductSiteBrandPostureReview"
PYTHONPATH="$REPO_ROOT" python3 -m cli project hook-guide --json
```

What you should expect:

- a guided durable-customization payload
- recommended next commands
- hook discovery / preview / handoff structure

## 8. Optional: Build A Proof Baseline Frontend

Company line:

```bash
cd "$REPO_ROOT/output_projects/CompanyProductSiteBrandPostureReview/frontend"
npm install
npm run build
```

Personal line:

```bash
cd "$REPO_ROOT/output_projects/PersonalIndependentSiteSignatureReview/frontend"
npm install
npm run build
```

## Suggested First Feedback

The most useful early external feedback is:

- which CLI flows are easy to follow
- where the README or Quickstart is still too internal
- what broke during local setup
- which outputs feel impressive versus confusing
- whether durable customization feels understandable to a first-time tester

## Next Docs

After this guide, read:

- [`OPEN_SOURCE_STATUS.md`](OPEN_SOURCE_STATUS.md)
- [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md)
- [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)
