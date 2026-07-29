# Reproducibility Guide

## Environment used to produce the results in this repository

- OS: Windows 11 Pro 10.0.26200
- Python: 3.14.4
- Key dependencies: jsonschema 4.26.0, PyYAML 6.0.3 (exact versions also recorded live in
  `benchmarks/results/benchmark_results.json` -> `environment`)
- Execution date: 2026-07-29

## Install from a clean environment

```bash
git clone https://github.com/sunilgentyala/authorization-bom.git
cd authorization-bom
python -m pip install -e ".[dev]"
```

## Run the test suite

```bash
pytest tests/ --cov=authbom --cov-report=term-missing
```

Expect 76 passed, ~94% coverage, as of this writing.

## Run static/security checks

```bash
ruff check src/ tests/
mypy src/authbom
bandit -r src/
```

## Reproduce the benchmark results

```bash
python benchmarks/run_benchmarks.py
```

Writes `benchmarks/results/benchmark_results.json` (raw) and `benchmark_summary.md` (rendered
tables). Uses 10 fixed seeds (0-9); output should be identical run-to-run modulo wall-clock timing
figures (RQ6) and the `environment.timestamp` field. See research/benchmark_findings.md for the
honest interpretation of these numbers, including two disclosed negative/inconclusive results.

## Try the CLI directly

```bash
authbom generate --seed 42 --tenants 2 --output manifest.json
authbom validate manifest.json
authbom analyze manifest.json --now 2026-07-29T12:00:00 --output analysis.json
authbom report analysis.json --format markdown --output report.md
```

## What is NOT reproducible from this repository alone

- The literature/patent/vendor search underlying research/novelty_gate.md is a point-in-time web
  search (2026-07-29) without institutional database access; re-running it may surface different
  or additional results (see docs/limitations.md).
- Any manuscript numbers must trace back to `benchmarks/results/benchmark_results.json` at a
  specific commit; a manuscript quoting a number not present in that file (or a later regenerated
  version of it, per the same seeds) should be treated as a defect, not accepted at face value.
