# ABOM Benchmark Results

Generated: 2026-07-29T20:57:11.843745+00:00
OS: Windows-11-10.0.26200-SP0
Python: 3.14.4
authorization-bom: 0.1.0
Seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

## RQ1: Effective-permission accuracy (naive baseline vs. corrected engine)

| Metric | Naive mean | Naive stdev | Corrected mean | Corrected stdev |
|---|---|---|---|---|
| precision | 0.9745 | 0.0221 | 1.0000 | 0.0000 |
| recall | 1.0000 | 0.0000 | 1.0000 | 0.0000 |
| f1 | 0.9870 | 0.0114 | 1.0000 | 0.0000 |
| false_positive_rate | 0.0255 | 0.0221 | 0.0000 | 0.0000 |

## RQ2: Chain depth vs. clean-reconstruction rate

| Depth | n | Clean rate |
|---|---|---|
| 2 | 40 | 1.0000 |
| 3 | 40 | 1.0000 |
| 4 | 20 | 1.0000 |
| 5 | 20 | 1.0000 |

## RQ3: Drift detection -- full temporal context vs. snapshot-diff-only ablation

| Metric | Full mean | Ablation mean |
|---|---|---|
| precision | 1.0000 | 1.0000 |
| recall | 1.0000 | 1.0000 |
| f1 | 1.0000 | 1.0000 |

## RQ4: Toxic-combination detection scope

- Human-only mean violations: 0.00
- Agent-inclusive mean violations: 2.00
- Additional violations surfaced by agent-inclusive scope: 2.00

## RQ5: Revocation convergence by estate size

| Scale | Resolved | Unresolved | Mean seconds |
|---|---|---|---|
| small | 5 | 5 | 300.0 |
| medium | 54 | 36 | 300.0 |
| large | 218 | 142 | 300.0 |

## RQ6: CLI-stage overhead by estate size

| Scale | Grants | Generate (s) | Validate (s) | Sign (s) | Verify (s) | Analyze (s) |
|---|---|---|---|---|---|---|
| small | 9 | 0.0002 | 0.0031 | 0.0003 | 0.0002 | 0.0001 |
| medium | 57 | 0.0009 | 0.0138 | 0.0012 | 0.0008 | 0.0003 |
| large | 228 | 0.0036 | 0.0475 | 0.0044 | 0.0031 | 0.0012 |
