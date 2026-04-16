# Generated Or Cache Archive (2026-03-16)

This directory contains root-level generated or cache artifacts moved out of the main workspace during repository cleanup.

Moved items:
- ail_data.db
- __pycache__/
- .pycache/

Rationale:
- root-level SQLite file did not have active in-repo path references as a required workspace source
- Python cache directories are disposable runtime artifacts
