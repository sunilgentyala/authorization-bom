# ABOM Benchmark Findings (RQ1-RQ6)

Raw results: benchmarks/results/benchmark_results.json. Summary table: benchmarks/results/
benchmark_summary.md. Reproduce with `python benchmarks/run_benchmarks.py` (10 recorded seeds,
0-9). Environment recorded in the results JSON (OS, Python version, package versions, timestamp).

This document is the honest interpretation layer required by the assignment's integrity rules
("preserve failed, negative, and inconclusive results"; "bound every conclusion to the tested
environment"). Every claim below is qualified by what the synthetic benchmark actually measured,
not what the formal model aspires to.

## RQ1 -- effective-permission accuracy (supported)

Corrected engine: precision 1.0000, recall 1.0000, F1 1.0000, FPR 0.0000 (stdev 0 across all 10
seeds). Naive baseline: precision 0.9745 (stdev 0.0221), recall 1.0000, F1 0.9870, FPR 0.0255.

H1 is supported on this synthetic benchmark: correcting for chains whose emitted actionRefs
contradict their own recorded scopeReduction measurably improves precision (fewer over-broad
effective-permission claims) with no recall cost. The effect size is modest (about 2.5 percentage
points of precision) because only a `defect_rate`-controlled fraction of delegated grants carry
the injected contradiction in the first place; this is not evidence of "solving" effective-
permission computation in general, only of eliminating one specific, mechanically detectable
contradiction class. Bounded to the tested synthetic environment.

## RQ2 -- chain depth vs. reconstruction accuracy (negative result, reported as such)

Clean chain-consistency reconstruction rate was 1.0000 at every tested depth (2, 3, 4, 5 hops;
n=40, 40, 20, 20 respectively). **H1 (accuracy decreases with depth) is rejected on this
benchmark; H0 is not rejected.** The chain-consistency check (`engine/delegation.py`
`validate_chain`) sums `scopeReduction` across every hop regardless of chain length, so as long
as the full chain is present in the manifest, depth alone does not degrade detection in this
implementation. This is a genuine negative result, not a null test -- it should not be
reframed as a strength ("scales perfectly to any depth") because the benchmark only tested
chains up to depth 5 and never tested a chain with *missing* intermediate hops, which is the
actual failure mode `evidenceCompleteness: partial` exists to flag (see docs/threat_model.md T3).

## RQ3 -- drift-detection ablation (inconclusive, methodological limitation disclosed)

Full-temporal-context and snapshot-diff-only-ablation scores were identical (precision/recall/F1
all 1.0000). This is **not** evidence that temporal-context modeling provides no benefit -- it is
a limitation of how the ablation was implemented against the current synthetic generator: each
observable grant in `adapters/synthetic.py` receives exactly one `runtimeEvidence` event, so
truncating to the first event (`grant["runtimeEvidence"][:1]`) is a no-op. The ablation as
designed cannot distinguish the two conditions given the fixture's current richness. This is
recorded as an open limitation, not silently dropped: a meaningful RQ3 ablation requires extending
the synthetic generator to emit multiple time-separated runtime-evidence events per grant so a
snapshot-diff approach can plausibly miss drift that occurs between snapshots. This is flagged as
future work, not claimed as a completed, decisive ablation.

## RQ4 -- toxic-combination detection scope (supported)

Agent-inclusive analysis found a mean of 2.00 violations per fixture versus 0.00 for human-only
analysis, across 10 seeds. H1 is supported: extending separation-of-duty analysis to
agent-mediated delegation chains surfaces violations completely invisible to a human-only rule
scope, on this benchmark. This is expected by construction (the synthetic generator's delegation
chains always terminate at an `ai_agent` identity), so the effect size here should not be read as
representative of any real organization's ratio of agent-mediated to human-only SoD violations --
only as a demonstration that the detection gap is real and mechanically closable.

## RQ5 -- revocation convergence (partially supported, one modeling limitation disclosed)

Unresolved-revocation counts scaled with estate size as expected (small: 5 unresolved / 10 total,
medium: 36/90, large: 142/360), supporting the qualitative claim that revocation-propagation gaps
grow with estate size. However, the **convergence-time value itself (300.0s / 5 minutes) was
identical across all scales and all resolved events** -- this is a synthetic-generator artifact
(`adapters/synthetic.py` hardcodes a fixed 5-minute propagation delay for every "resolved"
revocation), not a measured latency phenomenon. RQ5's *count*-scaling result is genuine; its
*time*-scaling result is not yet measured and should not be cited as such. A future iteration of
the generator should sample propagation delay from a distribution to make time-scaling
measurable.

## RQ6 -- CLI-stage overhead (supported)

Wall-clock time for generate/validate/sign/verify/analyze stayed under 51ms even at the "large"
fixture scale (228 grants), far inside the 10-second-per-stage budget stated as the rejection
criterion in research/gap_analysis.md. H1 is supported: overhead is practical at CI scale for the
estate sizes tested here. This says nothing about estates orders of magnitude larger (thousands of
grants); the `H_max` hop-cap and graph-expansion-DoS considerations in docs/threat_model.md T14
remain unverified beyond this benchmark's largest tested size.

## Overall bounding statement

All six results are bounded to Python 3.14.4 on Windows 11, this repository's synthetic generator
at its current commit, and 10 recorded seeds (0-9). No claim here generalizes to production
authorization estates, which this project has not evaluated (synthetic-only, per research/
gap_analysis.md's stated threats to validity).
