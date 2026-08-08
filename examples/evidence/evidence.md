# DiffSeal Evidence

## Decision: **PASS**

### Reasons
- all required evidence satisfactory

### Run
- Schema version: `0.1`
- Evidence ID: `sample-evidence-id`
- Run ID: `sample-run-id`
- Product version: `0.1.0`
- Started: `2026-01-01T00:00:00+00:00`
- Finished: `2026-01-01T00:00:01+00:00`
- Invocation mode: `local-cli`
- Configuration hash: `d32f1027156ac1c16d921e4d137aa5d41884773d76f218c67997d85691849560`
- Policy hash: `11cf74be6c323c7a16668652f49e69456bd4359af4991d99a897b0ce800abc00`

### Repository / Change
- Repository: `examples/python-basic`
- Base revision: `n/a`
- Head revision: `6b6421544080b7914cc559b84db873c527cbf0f2`
- branch: `main`
- files_changed: `0`
- is_git: `True`
- staged_files: `0`

## Checks

### pytest (required)
**PASS** — 1 passed
- collector: `pytest`
- duration: 0.438s

### ruff (required)
**PASS** — no lint violations
- collector: `ruff`
- duration: 0.070s

### coverage (optional)
**PASS** — coverage 100.0% meets threshold 80%
- collector: `coverage`
- duration: 1.160s

### dependency (optional)
**SKIPPED** — no declared dependencies found; check skipped
- collector: `dependency`
- duration: 0.000s

## Tool Versions
- coverage: `7.15.4`
- pytest: `9.1.1`
- ruff: `0.16.2`
