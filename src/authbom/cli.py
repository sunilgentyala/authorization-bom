"""authbom command-line interface.

Minimum command set per the project spec: import, generate, validate, sign, verify, diff,
analyze, reconcile, report.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from authbom import adapters, signing
from authbom import manifest as manifest_mod
from authbom.adapters import synthetic
from authbom.engine import delegation, drift, graph_checks, revocation, toxic
from authbom.engine.effective_permissions import effective_permissions
from authbom.reporters import RENDERERS


def _add_secret_args(parser: argparse.ArgumentParser, prefix: str = "secret") -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(f"--{prefix}", help="Secret value (visible in shell history/ps; prefer the alternatives below).")
    group.add_argument(f"--{prefix}-file", help="Path to a file containing the secret.")
    group.add_argument(f"--{prefix}-env", help="Name of an environment variable containing the secret.")
    group.add_argument(f"--{prefix}-stdin", action="store_true", help="Read the secret from stdin.")


def _resolve_secret(args: argparse.Namespace, prefix: str = "secret") -> str:
    import os

    value = getattr(args, prefix, None)
    if value:
        print(f"warning: --{prefix} exposes the secret in shell history/process list; "
              f"prefer --{prefix}-file/--{prefix}-env/--{prefix}-stdin", file=sys.stderr)
        return value
    file_val = getattr(args, f"{prefix}_file", None)
    if file_val:
        return Path(file_val).read_text(encoding="utf-8").strip()
    env_val = getattr(args, f"{prefix}_env", None)
    if env_val:
        secret = os.environ.get(env_val)
        if secret is None:
            raise SystemExit(f"environment variable {env_val} is not set")
        return secret
    if getattr(args, f"{prefix}_stdin", False):
        return sys.stdin.readline().rstrip("\n")
    raise SystemExit("no secret source provided")


def cmd_generate(args: argparse.Namespace) -> int:
    doc, _gt = synthetic.generate(
        seed=args.seed,
        tenants=args.tenants,
        humans_per_tenant=args.humans,
        workloads_per_tenant=args.workloads,
        agents_per_tenant=args.agents,
        defect_rate=args.defect_rate,
    )
    errors = manifest_mod.validate(doc)
    if errors:
        print("generated manifest failed schema validation:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    manifest_mod.save(doc, args.output)
    print(f"wrote {args.output}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    parse_fn = adapters.ADAPTERS.get(args.source)
    if parse_fn is None:
        print(f"unknown source: {args.source}. Known: {sorted(adapters.ADAPTERS)}", file=sys.stderr)
        return 1
    fixture = manifest_mod.load(args.input)
    fragment = parse_fn(fixture)
    if args.merge and Path(args.merge).exists():
        base = manifest_mod.load(args.merge)
    else:
        base = manifest_mod.new_manifest()
    merged = manifest_mod.merge(base, fragment)
    errors = manifest_mod.validate(merged)
    if errors:
        print("imported manifest failed schema validation:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    manifest_mod.save(merged, args.output)
    print(f"wrote {args.output} ({len(fragment['grants'])} grant(s) imported from {args.source})")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    doc = manifest_mod.load(args.manifest)
    errors = manifest_mod.validate(doc)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"INVALID: {len(errors)} error(s)")
        return 1
    print("VALID")
    return 0


def cmd_sign(args: argparse.Namespace) -> int:
    doc = manifest_mod.load(args.manifest)
    secret = _resolve_secret(args)
    signed = signing.sign_manifest(doc, secret, args.key_id)
    manifest_mod.save(signed, args.output)
    print(f"wrote {args.output} ({len(signed['grants'])} grant(s) signed)")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    doc = manifest_mod.load(args.manifest)
    secret = _resolve_secret(args)
    result = signing.verify_manifest(doc, {args.key_id: secret})
    print(json.dumps(result, indent=2))
    return 0 if result["all_grants_valid"] and (not doc.get("attestations") or result["all_attestations_valid"]) else 1


def cmd_diff(args: argparse.Namespace) -> int:
    a = manifest_mod.load(args.manifest_a)
    b = manifest_mod.load(args.manifest_b)
    grants_a = manifest_mod.index_by_id(a.get("grants", []))
    grants_b = manifest_mod.index_by_id(b.get("grants", []))
    added = sorted(set(grants_b) - set(grants_a))
    removed = sorted(set(grants_a) - set(grants_b))
    changed = sorted(
        gid for gid in (set(grants_a) & set(grants_b)) if grants_a[gid] != grants_b[gid]
    )
    result = {"added": added, "removed": removed, "changed": changed}
    out = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out, end="")
    return 0


def cmd_reconcile(args: argparse.Namespace) -> int:
    doc = manifest_mod.load(args.manifest)
    events = manifest_mod.load(args.observed)
    grants_by_id = manifest_mod.index_by_id(doc.get("grants", []))
    for event in events.get("events", []):
        grant = grants_by_id.get(event["grantId"])
        if grant is None:
            continue
        grant.setdefault("runtimeEvidence", []).append(
            {k: v for k, v in event.items() if k != "grantId"}
        )
    doc["grants"] = list(grants_by_id.values())
    errors = manifest_mod.validate(doc)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    manifest_mod.save(doc, args.output)
    print(f"wrote {args.output}")
    return 0


def _run_analysis(doc: dict[str, Any], now: datetime, staleness_days: int) -> dict[str, Any]:
    eff = effective_permissions(doc)
    return {
        "manifestId": doc.get("metadata", {}).get("id"),
        "effectivePermissions": {f"{s}|{r}": sorted(acts) for (s, r), acts in eff.items()},
        "delegation": delegation.analyze_delegations(doc),
        "drift": drift.detect_drift(doc, now, staleness=timedelta(days=staleness_days)),
        "toxicCombinations": toxic.detect_approver_executor_overlap(doc),
        "orphans": graph_checks.find_orphans(doc),
        "crossTenant": graph_checks.find_cross_tenant_grants(doc),
        "revocation": {
            "events": (rev_events := revocation.convergence_times(doc)),
            "summary": revocation.summary(rev_events),
        },
    }


def cmd_analyze(args: argparse.Namespace) -> int:
    doc = manifest_mod.load(args.manifest)
    now = datetime.fromisoformat(args.now) if args.now else datetime.utcnow()
    result = _run_analysis(doc, now, args.staleness_days)
    out = json.dumps(result, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(out, end="")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    result = manifest_mod.load(args.analysis)
    renderer = RENDERERS.get(args.format)
    if renderer is None:
        print(f"unknown format: {args.format}", file=sys.stderr)
        return 1
    rendered = renderer(result)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(rendered, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="authbom", description="Authorization Bill of Materials CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("generate", help="Generate a synthetic ABOM manifest")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--tenants", type=int, default=2)
    p.add_argument("--humans", type=int, default=3)
    p.add_argument("--workloads", type=int, default=3)
    p.add_argument("--agents", type=int, default=2)
    p.add_argument("--defect-rate", type=float, default=0.2)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("import", help="Import a source-system fixture into a manifest")
    p.add_argument("--source", required=True, choices=sorted(adapters.ADAPTERS))
    p.add_argument("--input", required=True)
    p.add_argument("--merge", help="Existing manifest to merge into (created fresh if omitted/absent)")
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_import)

    p = sub.add_parser("validate", help="Validate a manifest against the ABOM JSON Schema")
    p.add_argument("manifest")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("sign", help="Sign every grant and attach a manifest-level attestation")
    p.add_argument("manifest")
    p.add_argument("--key-id", required=True)
    p.add_argument("--output", required=True)
    _add_secret_args(p)
    p.set_defaults(func=cmd_sign)

    p = sub.add_parser("verify", help="Verify grant signatures and attestations")
    p.add_argument("manifest")
    p.add_argument("--key-id", required=True)
    _add_secret_args(p)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("diff", help="Diff two manifests' grants (added/removed/changed)")
    p.add_argument("manifest_a")
    p.add_argument("manifest_b")
    p.add_argument("--output")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("reconcile", help="Merge observed runtime-evidence events into a manifest")
    p.add_argument("manifest")
    p.add_argument("--observed", required=True, help="JSON file with {'events': [{'grantId':..., ...}]}")
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_reconcile)

    p = sub.add_parser(
        "analyze",
        help="Run effective-permission, delegation, drift, toxic-combination, and revocation analysis",
    )
    p.add_argument("manifest")
    p.add_argument("--now", help="ISO-8601 timestamp to analyze as-of (defaults to current UTC time)")
    p.add_argument("--staleness-days", type=int, default=90)
    p.add_argument("--output")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("report", help="Render an analysis result as json/markdown/sarif")
    p.add_argument("analysis")
    p.add_argument("--format", choices=sorted(RENDERERS), default="markdown")
    p.add_argument("--output")
    p.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
