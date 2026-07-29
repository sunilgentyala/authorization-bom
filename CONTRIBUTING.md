# Contributing

Thanks for your interest in ABOM. This is an early-stage (0.1.0, alpha) project; expect breaking
schema and API changes before 1.0.

## Development setup

```bash
git clone https://github.com/sunilgentyala/authorization-bom.git
cd authorization-bom
python -m pip install -e ".[dev]"
pytest tests/ --cov=authbom --cov-report=term-missing
ruff check src/ tests/
mypy src/authbom
bandit -r src/
```

## Before opening a PR

- All tests must pass; new behavior needs new tests (see `tests/` for the existing pattern:
  schema, unit, property-style, integration/CLI, negative, tamper, replay).
- `ruff check`, `mypy`, and `bandit` must be clean.
- If you change `schema/abom.schema.json`, update both copies (`schema/` and
  `src/authbom/schema/`) and re-validate `schema/examples/*.json`.
- If you add or change an adapter, keep it read-only and credential-free (see docs/threat_model.md
  for why this is a hard boundary, not a style preference).
- Do not fabricate benchmark numbers. If you touch `benchmarks/run_benchmarks.py` or the
  synthetic generator, re-run `python benchmarks/run_benchmarks.py` and update
  `research/benchmark_findings.md` honestly, including if a result becomes worse or inconclusive.
- Update `docs/limitations.md` if your change closes or introduces a limitation.

## Reporting bugs / requesting features

Open a GitHub issue. For suspected security issues, see [SECURITY.md](SECURITY.md) instead.
