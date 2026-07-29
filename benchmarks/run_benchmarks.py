#!/usr/bin/env python
"""Benchmark harness for RQ1-RQ6 (research/gap_analysis.md).

Generates synthetic fixtures across multiple recorded seeds and scales, runs the reference
engine, and writes raw JSON results plus a plain-text summary to benchmarks/results/. This script
is the only source of the numbers that may appear in any ABOM manuscript -- per the project's
integrity rules, manuscript tables/figures must be generated from repository results, not
invented separately.

Usage: python benchmarks/run_benchmarks.py
"""

from __future__ import annotations

import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from importlib.metadata import version as pkg_version
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from authbom import __version__ as authbom_version  # noqa: E402
from authbom.adapters.synthetic import generate  # noqa: E402
from authbom.engine import delegation, drift, graph_checks, revocation, toxic  # noqa: E402
from authbom.engine.effective_permissions import (  # noqa: E402
    effective_permissions,
    naive_effective_permissions,
    score,
)
from authbom.manifest import validate  # noqa: E402
from authbom.signing import sign_manifest, verify_manifest  # noqa: E402

SEEDS = list(range(10))  # 10 recorded seeds, per "use multiple recorded seeds"
RESULTS_DIR = REPO_ROOT / "benchmarks" / "results"


def environment_record() -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "os": platform.platform(),
        "python_version": platform.python_version(),
        "authbom_version": authbom_version,
        "jsonschema_version": pkg_version("jsonschema"),
        "pyyaml_version": pkg_version("PyYAML"),
        "seeds": SEEDS,
    }


def rq1_effective_permission_accuracy() -> dict:
    """RQ1: corrected engine vs. naive baseline, scored against ground truth."""
    naive_scores, corrected_scores = [], []
    for seed in SEEDS:
        doc, gt = generate(seed=seed, tenants=3, agents_per_tenant=3, defect_rate=0.4)
        naive = naive_effective_permissions(doc)
        corrected = effective_permissions(doc)
        naive_scores.append(score(naive, gt.effective_permissions))
        corrected_scores.append(score(corrected, gt.effective_permissions))
    return {
        "naive_baseline": _summarize_scores(naive_scores),
        "corrected_engine": _summarize_scores(corrected_scores),
        "per_seed": {"naive": naive_scores, "corrected": corrected_scores},
    }


def _summarize_scores(scores: list[dict]) -> dict:
    return {
        metric: {
            "mean": statistics.mean(s[metric] for s in scores),
            "stdev": statistics.stdev(s[metric] for s in scores) if len(scores) > 1 else 0.0,
        }
        for metric in ("precision", "recall", "f1", "false_positive_rate")
    }


def rq2_chain_depth_vs_reconstruction_accuracy() -> dict:
    """RQ2: does reconstruction accuracy degrade as delegation-chain depth increases?"""
    by_depth: dict[int, list[bool]] = {}
    for seed in SEEDS:
        doc, gt = generate(seed=seed, tenants=2, agents_per_tenant=6, defect_rate=0.3, max_extra_agent_hops=3)
        for grant in doc["grants"]:
            if not grant.get("delegationChain"):
                continue
            depth = delegation.chain_depth(grant)
            issues = delegation.validate_chain(doc, grant)
            non_amplification_issues = [i for i in issues if "privilege amplification" not in i]
            reconstructed_cleanly = not non_amplification_issues
            by_depth.setdefault(depth, []).append(reconstructed_cleanly)
    return {
        str(depth): {"n": len(results), "clean_reconstruction_rate": sum(results) / len(results)}
        for depth, results in sorted(by_depth.items())
    }


def rq3_drift_detection_ablation() -> dict:
    """RQ3: temporal-context (full manifest) vs. a naive snapshot-diff-only ablation.

    The "snapshot-diff-only" ablation is simulated by stripping runtimeEvidence and revocation
    metadata down to a single before/after pair per grant (no intermediate temporal context),
    then checking whether drift is still detected.
    """
    full_scores, ablation_scores = [], []
    for seed in SEEDS:
        doc, gt = generate(seed=seed, tenants=2, agents_per_tenant=2, defect_rate=0.4)
        now = datetime(2026, 7, 29, 12)
        full_findings = drift.detect_drift(doc, now)
        full_flagged = {f["grantId"] for f in full_findings}

        ablated = json.loads(json.dumps(doc))
        for grant in ablated["grants"]:
            if grant.get("runtimeEvidence"):
                grant["runtimeEvidence"] = grant["runtimeEvidence"][:1]
        ablated_findings = drift.detect_drift(ablated, now)
        ablated_flagged = {f["grantId"] for f in ablated_findings}

        truth = gt.drift_defect_grant_ids
        all_ids = {g["id"] for g in doc["grants"]}
        full_scores.append(_binary_score(full_flagged, truth, all_ids))
        ablation_scores.append(_binary_score(ablated_flagged, truth, all_ids))
    return {
        "full_temporal_context": _summarize_scores(full_scores),
        "snapshot_diff_ablation": _summarize_scores(ablation_scores),
    }


def _binary_score(flagged: set, truth: set, universe: set) -> dict:
    tp = len(flagged & truth)
    fp = len(flagged - truth)
    fn = len(truth - flagged)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    fpr = fp / (fp + tp) if (fp + tp) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "false_positive_rate": fpr}


def rq4_toxic_combination_scope() -> dict:
    """RQ4: human-only vs. agent-inclusive separation-of-duty rule scope."""
    human_only_counts, agent_inclusive_counts = [], []
    for seed in SEEDS:
        doc, _gt = generate(seed=seed, tenants=3, agents_per_tenant=3, humans_per_tenant=3, defect_rate=0.4)
        human_only_counts.append(len(toxic.detect_approver_executor_overlap(doc, include_agents=False)))
        agent_inclusive_counts.append(len(toxic.detect_approver_executor_overlap(doc, include_agents=True)))
    return {
        "human_only_mean": statistics.mean(human_only_counts),
        "agent_inclusive_mean": statistics.mean(agent_inclusive_counts),
        "additional_violations_found": statistics.mean(agent_inclusive_counts) - statistics.mean(human_only_counts),
    }


def rq5_revocation_convergence() -> dict:
    """RQ5: revocation convergence time distribution as a function of estate size."""
    results_by_scale = {}
    for label, (tenants, workloads) in {"small": (1, 2), "medium": (3, 4), "large": (6, 8)}.items():
        seconds = []
        unresolved = 0
        for seed in SEEDS:
            doc, _gt = generate(seed=seed, tenants=tenants, workloads_per_tenant=workloads, defect_rate=0.4)
            for r in revocation.convergence_times(doc):
                if r["convergenceSeconds"] is not None:
                    seconds.append(r["convergenceSeconds"])
                else:
                    unresolved += 1
        results_by_scale[label] = {
            "n_resolved": len(seconds),
            "n_unresolved": unresolved,
            "mean_seconds": statistics.mean(seconds) if seconds else None,
        }
    return results_by_scale


def rq6_overhead_by_estate_size() -> dict:
    """RQ6: wall-clock cost of generate/validate/sign/verify/analyze as a function of estate size."""
    results = {}
    for label, (tenants, humans, workloads, agents) in {
        "small": (1, 2, 2, 1),
        "medium": (3, 4, 4, 3),
        "large": (6, 8, 8, 6),
    }.items():
        timings = {"generate": [], "validate": [], "sign": [], "verify": [], "analyze": []}
        for seed in SEEDS[:5]:
            t0 = time.perf_counter()
            doc, _gt = generate(
                seed=seed, tenants=tenants, humans_per_tenant=humans,
                workloads_per_tenant=workloads, agents_per_tenant=agents, defect_rate=0.3,
            )
            timings["generate"].append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            validate(doc)
            timings["validate"].append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            signed = sign_manifest(doc, secret="bench-secret", key_id="bench-key")
            timings["sign"].append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            verify_manifest(signed, {"bench-key": "bench-secret"})
            timings["verify"].append(time.perf_counter() - t0)

            t0 = time.perf_counter()
            effective_permissions(doc)
            delegation.analyze_delegations(doc)
            drift.detect_drift(doc, datetime(2026, 7, 29, 12))
            toxic.detect_approver_executor_overlap(doc)
            graph_checks.find_orphans(doc)
            graph_checks.find_cross_tenant_grants(doc)
            revocation.convergence_times(doc)
            timings["analyze"].append(time.perf_counter() - t0)

        results[label] = {
            "n_grants": len(doc["grants"]),
            "n_identities": len(doc["identities"]),
            "mean_seconds": {stage: statistics.mean(vals) for stage, vals in timings.items()},
            "max_seconds": {stage: max(vals) for stage, vals in timings.items()},
        }
    return results


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "environment": environment_record(),
        "rq1_effective_permission_accuracy": rq1_effective_permission_accuracy(),
        "rq2_chain_depth_vs_reconstruction_accuracy": rq2_chain_depth_vs_reconstruction_accuracy(),
        "rq3_drift_detection_ablation": rq3_drift_detection_ablation(),
        "rq4_toxic_combination_scope": rq4_toxic_combination_scope(),
        "rq5_revocation_convergence": rq5_revocation_convergence(),
        "rq6_overhead_by_estate_size": rq6_overhead_by_estate_size(),
    }
    out_path = RESULTS_DIR / "benchmark_results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")

    summary_path = RESULTS_DIR / "benchmark_summary.md"
    summary_path.write_text(_render_summary(results), encoding="utf-8")
    print(f"wrote {summary_path}")


def _render_summary(results: dict) -> str:
    env = results["environment"]
    lines = [
        "# ABOM Benchmark Results",
        "",
        f"Generated: {env['timestamp']}",
        f"OS: {env['os']}",
        f"Python: {env['python_version']}",
        f"authorization-bom: {env['authbom_version']}",
        f"Seeds: {env['seeds']}",
        "",
        "## RQ1: Effective-permission accuracy (naive baseline vs. corrected engine)",
        "",
        "| Metric | Naive mean | Naive stdev | Corrected mean | Corrected stdev |",
        "|---|---|---|---|---|",
    ]
    rq1 = results["rq1_effective_permission_accuracy"]
    for metric in ("precision", "recall", "f1", "false_positive_rate"):
        n, c = rq1["naive_baseline"][metric], rq1["corrected_engine"][metric]
        lines.append(f"| {metric} | {n['mean']:.4f} | {n['stdev']:.4f} | {c['mean']:.4f} | {c['stdev']:.4f} |")

    lines += ["", "## RQ2: Chain depth vs. clean-reconstruction rate", "", "| Depth | n | Clean rate |", "|---|---|---|"]
    for depth, d in results["rq2_chain_depth_vs_reconstruction_accuracy"].items():
        lines.append(f"| {depth} | {d['n']} | {d['clean_reconstruction_rate']:.4f} |")

    lines += ["", "## RQ3: Drift detection -- full temporal context vs. snapshot-diff-only ablation", "",
              "| Metric | Full mean | Ablation mean |", "|---|---|---|"]
    rq3 = results["rq3_drift_detection_ablation"]
    for metric in ("precision", "recall", "f1"):
        lines.append(
            f"| {metric} | {rq3['full_temporal_context'][metric]['mean']:.4f} "
            f"| {rq3['snapshot_diff_ablation'][metric]['mean']:.4f} |"
        )

    rq4 = results["rq4_toxic_combination_scope"]
    lines += [
        "",
        "## RQ4: Toxic-combination detection scope",
        "",
        f"- Human-only mean violations: {rq4['human_only_mean']:.2f}",
        f"- Agent-inclusive mean violations: {rq4['agent_inclusive_mean']:.2f}",
        f"- Additional violations surfaced by agent-inclusive scope: {rq4['additional_violations_found']:.2f}",
    ]

    lines += ["", "## RQ5: Revocation convergence by estate size", "", "| Scale | Resolved | Unresolved | Mean seconds |", "|---|---|---|---|"]
    for scale, d in results["rq5_revocation_convergence"].items():
        mean_s = f"{d['mean_seconds']:.1f}" if d["mean_seconds"] is not None else "n/a"
        lines.append(f"| {scale} | {d['n_resolved']} | {d['n_unresolved']} | {mean_s} |")

    lines += ["", "## RQ6: CLI-stage overhead by estate size", "", "| Scale | Grants | Generate (s) | Validate (s) | Sign (s) | Verify (s) | Analyze (s) |", "|---|---|---|---|---|---|---|"]
    for scale, d in results["rq6_overhead_by_estate_size"].items():
        m = d["mean_seconds"]
        lines.append(
            f"| {scale} | {d['n_grants']} | {m['generate']:.4f} | {m['validate']:.4f} | "
            f"{m['sign']:.4f} | {m['verify']:.4f} | {m['analyze']:.4f} |"
        )

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
