# Quickstart For Open-Source Testers

## Purpose

This guide is the shortest path for external testers to verify that AIL Builder runs locally and exposes its main CLI surfaces.

## Prerequisites

Minimum assumptions:

- Python `3.10+`
- Git
- a shell environment such as `bash`, `zsh`, or PowerShell

Helpful but optional:

- Node.js and npm if you want to build the bundled frontend sample projects

## Cross-Platform Notes

- The examples below use Unix shell syntax with `python3` and `export`.
- On Windows PowerShell, use `$env:REPO_ROOT = $PWD.Path` instead of `export REPO_ROOT="$PWD"`.
- On Windows, if `python3` is unavailable, try `py -3` or `python`.
- The CLI now resolves the repository root dynamically, so you should not need to edit hardcoded macOS paths.

## 1. Clone And Enter The Repo

```bash
git clone <your-github-url> ail-builder
cd ail-builder
export REPO_ROOT="$PWD"
```

PowerShell equivalent:

```powershell
git clone <your-github-url> ail-builder
cd ail-builder
$env:REPO_ROOT = $PWD.Path
```

## 2. Optional: Create A Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

PowerShell equivalent:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install The Local Python Package

```bash
pip install -e .
```

If PowerShell does not have `pip` on PATH yet, use:

```powershell
py -3 -m pip install -e .
```

## 4. Sanity-Check The CLI

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli --help
```

PowerShell equivalent:

```powershell
$env:PYTHONPATH = $env:REPO_ROOT
py -3 -m cli --help
```

If that works, the CLI entry surface is available.

## 5. Run The Shortest Verified Website Check

```bash
PYTHONPATH="$REPO_ROOT" python3 -m cli website check 'Create a company product website with a home page, features, FAQ, and contact page.' --base-url embedded://local --json
```

PowerShell equivalent:

```powershell
$env:PYTHONPATH = $env:REPO_ROOT
py -3 -m cli website check "Create a company product website with a home page, features, FAQ, and contact page." --base-url embedded://local --json
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

You can preview a generated frontend through the CLI:

```bash
cd "$REPO_ROOT/output_projects/CompanyProductSiteBrandPostureReview"
PYTHONPATH="$REPO_ROOT" python3 -m cli project serve --dry-run --json
PYTHONPATH="$REPO_ROOT" python3 -m cli project serve --install-if-needed
```

PowerShell equivalent:

```powershell
cd "$env:REPO_ROOT\output_projects\CompanyProductSiteBrandPostureReview"
$env:PYTHONPATH = $env:REPO_ROOT
py -3 -m cli project serve --dry-run --json
py -3 -m cli project serve --install-if-needed
```

The command starts the frontend dev server in the background and returns a local URL such as `http://127.0.0.1:5173`.

You can also build the proof frontends manually.

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
