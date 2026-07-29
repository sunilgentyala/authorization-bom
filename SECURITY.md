# Security Policy

## Reporting a vulnerability

Please report suspected vulnerabilities privately via GitHub's "Report a vulnerability" feature
under this repository's Security tab, or by opening a private security advisory. Do not open a
public issue for suspected vulnerabilities.

Include, where possible: affected version/commit, a minimal reproduction, and the impact you
believe it has (see docs/threat_model.md for the abuse-case categories this project already
tracks -- confused deputy, delegation abuse, manifest tampering, revocation failure, etc.).

## Scope

In scope: `src/authbom/` (schema validation, signing/verification, analysis engine, CLI,
adapters). All adapters are read-only fixture parsers by design (see docs/threat_model.md); a
report that an adapter requires or handles live credentials would itself be treated as a
vulnerability, since that violates this project's design boundary.

Out of scope: vulnerabilities in the source systems an adapter's fixture was exported from
(Kubernetes, OPA, cloud IAM, etc.) -- those belong to their own maintainers.

## Supported versions

Only the latest released version on the default branch is currently supported; this project is
pre-1.0 (alpha) and does not yet maintain parallel security-patch branches.

## Known, disclosed limitations

See [docs/limitations.md](docs/limitations.md) for currently known gaps (e.g., only HMAC-SHA256
signing is implemented; Ed25519/ECDSA are schema-allowed but not yet implemented). These are not
vulnerabilities to report -- they are already tracked.
