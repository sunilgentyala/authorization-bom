# ABOM Citation Ledger

Research cutoff: 2026-07-29. Every entry below was independently verified this session via the
Crossref API (`api.crossref.org/works/{DOI}`) or, for arXiv preprints, the DataCite API
(`api.datacite.org/dois/{DOI}`) -- arXiv DOIs are registered with DataCite, not Crossref, so a
Crossref-only check would incorrectly appear to show "no DOI found" for genuine arXiv DOIs; both
were checked to avoid that false negative. Patents were verified via Google Patents/Justia (title,
assignee, inventors, dates). Standards/specifications are included without a DOI where none
exists, per the assignment's own rule that specifications may legitimately lack one.

28 references total: 23 carry a verified DOI, 5 are standards/specifications or patents with no
DOI expected (2 patents + 3 specs). References 24-28 were added 2026-07-30 when the manuscript was
expanded to include the author's own related published work (see the addendum below); all five
DOIs were re-verified via Crossref at that time.

## DOI-verified academic and standards references

| # | Citation | DOI | Verified via | Maps to which ABOM claim |
|---|---|---|---|---|
| 1 | Sandhu, R., Coyne, E., Feinstein, H., Youman, C. "Role-Based Access Control Models." *IEEE Computer*, 1996. | 10.1109/2.485845 | Crossref | Foundational RBAC baseline that ABOM's `authorityType: inherited` and role-based grants build on (docs/formal_model.md). |
| 2 | Hu, V. et al. "Guide to Attribute Based Access Control (ABAC) Definition and Considerations." NIST SP 800-162, 2014. | 10.6028/NIST.SP.800-162 | Crossref | ABAC baseline referenced in research/gap_analysis.md's comparison against `constraints.contextual`/`conditions`. |
| 3 | Rose, S., Borchert, O., Mitchell, S., Connelly, S. "Zero Trust Architecture." NIST SP 800-207, 2020. | 10.6028/NIST.SP.800-207 | Crossref | Motivates continuous/contextual authorization checking (docs/threat_model.md T5, T9). |
| 4 | Hardt, D. (ed.) "The OAuth 2.0 Authorization Framework." RFC 6749, 2012. | 10.17487/RFC6749 | Crossref | `policyProvenance.source: oauth_scope` and the OAuth adapter (src/authbom/adapters/oauth.py). |
| 5 | McGloin, M., Hunt, P. "OAuth 2.0 Threat Model and Security Considerations." RFC 6819, 2013. | 10.17487/RFC6819 | Crossref | Threat model precedent for T5 (token theft/replay) and T9 (excessive scopes). |
| 6 | Simon, R., Zurko, M.E. "Separation of Duty in Role-Based Environments." *Proc. 10th IEEE Computer Security Foundations Workshop*, 1997. | 10.1145/266741.266749 | Crossref | Foundational SoD/toxic-combination formalization that `engine/toxic.py` operationalizes for RQ4. |
| 7 | Ahn, G.J., Sandhu, R. "The RSL99 Language for Role-Based Separation of Duty Constraints." *Proc. 4th ACM Workshop on Role-Based Access Control*, 1999. | 10.1145/319171.319176 | Crossref | Additional SoD-constraint-language prior art compared against `ToxicCombination.rule` (schema/abom.schema.json). |
| 8 | "The Confused Deputy and the Domain Hijacker." *IEEE Security & Privacy*, 2008. | 10.1109/msp.2008.25 | Crossref | Direct prior art for docs/threat_model.md T1 (confused-deputy behavior). |
| 9 | "PaddyFrog: Systematically Detecting Confused Deputy Vulnerability in Android Applications." *Security and Communication Networks*, 2015. | 10.1002/sec.1179 | Crossref | Confused-deputy detection precedent in a different platform (mobile), cited to bound novelty claims for T1. |
| 10 | "iService: Detecting and Evaluating the Impact of Confused Deputy Problem in AppleOS." *ACM CCS*, 2022. | 10.1145/3564625.3568001 | Crossref | Same purpose as #9, different platform (AppleOS), strengthens the "confused deputy is a known, cross-platform class" framing rather than an ABOM invention. |
| 11 | "Extensible Access Control Markup Language (XACML) and Next Generation Access Control (NGAC)." *IDtrust/ABAC workshop proceedings*, 2016. | 10.1145/2875491.2875496 | Crossref | NGAC comparison baseline (assignment Section 4's required comparison list). |
| 12 | "Towards a User-Centric IAM Entitlement Shop -- Learnings from E-Commerce." *ACM conference proceedings*, 2020. | 10.1145/3433174.3433585 | Crossref | Entitlement-management/IGA comparison, related to research/comparison_matrix.md's SailPoint/Saviynt category. |
| 13 | Chen, Y., Malin, B. "Detection of Anomalous Insiders in Collaborative Environments via Relational Analysis of Access Logs." *ACM CODASPY*, 2011. | 10.1145/1943513.1943524 | Crossref | Relational/graph-based access-log anomaly detection, prior art for the drift-detection framing in RQ3. |
| 14 | "Invited Tutorial: Macaron -- A Comprehensive Framework for Securing and Analyzing the Software Supply Chain." *IEEE SecDev*, 2025. | 10.1109/secdev66745.2025.00010 | Crossref | Supply-chain evidence-framework comparator alongside in-toto/SLSA in research/comparison_matrix.md. |
| 15 | "Efficient Indexing for Google Zanzibar Based Authorization Systems Using Graph Dynamic-Transitive Closures." *ICACT*, 2026. | 10.23919/icact68090.2026.11431331 | Crossref | Closest recent academic treatment of transitive-closure computation over a Zanzibar-style relationship graph -- directly bounds ABOM's effective-permission-closure novelty claim (docs/formal_model.md). |
| 16 | Marro, S., Chan, A., Ren, X., Hammond, L. et al. "Permission Manifests for Web Agents." arXiv:2601.02371, 2026. | 10.48550/arXiv.2601.02371 | DataCite | Closest naming/manifest-pattern prior art, disclosed in research/novelty_gate.md and research/comparison_matrix.md. |
| 17 | Tallam, K. "Authorization Propagation in Multi-Agent AI Systems: Identity Governance as Infrastructure." arXiv:2605.05440, 2026. | 10.48550/arXiv.2605.05440 | DataCite | Closest runtime-authorization-propagation prior art for AI agents, disclosed in research/novelty_gate.md. |
| 18 | "OpenID Connect for Agents (OIDC-A) 1.0: A Standard Extension for LLM-Based Agent Identity and Authorization." arXiv:2509.25974, 2025. | 10.48550/arXiv.2509.25974 | DataCite | Direct prior art for ABOM's `delegationChain` schema field and RQ2, disclosed in research/novelty_gate.md. |

## Patents (no DOI; verified via Google Patents / Justia)

| # | Citation | Identifier | Verified via | Maps to which ABOM claim |
|---|---|---|---|---|
| 19 | Cook, J.B., Rungta, N., Varming, C., Peebles, D.G., et al. "Analysis of Role Reachability Using Policy Complements." Amazon Technologies, Inc. | US 11,757,886 B2 (granted 2024-07-09) | Google Patents / Justia | Directly bounds the novelty claim for delegation-reachability analysis in docs/formal_model.md ("Effective-permission closure"); scoped to AWS IAM only, disclosed in research/comparison_matrix.md. |
| 20 | Cook, J.B., Rungta, N., Gacek, A.J., Peebles, D.G., Varming, C. "Analysis of Role Reachability with Transitive Tags." Amazon Technologies, Inc. | US 2022/0191205 A1 (application family of #19) | Justia | Same purpose as #19, transitive-tag variant. |

## Standards / specifications (no DOI, per assignment's own allowance)

| # | Citation | Reference | Maps to which ABOM claim |
|---|---|---|---|
| 21 | OWASP CycloneDX Authoritative Guide, cyclonedx.org (accessed 2026-07-29) | No DOI (living specification) | Host format evaluated and rejected as insufficient for authorization state in research/novelty_gate.md Q2. |
| 22 | SPDX 3.0 Specification, Linux Foundation / ISO/IEC 5962, spdx.dev (accessed 2026-07-29) | No DOI (living specification) | Profile-architecture pattern (Security/Licensing/Build/AI/Dataset) that ABOM is positioned to extend, per research/novelty_gate.md Q4. |
| 23 | in-toto: A Framework to Secure the Integrity of Software Supply Chains, in-toto.io / slsa.dev (accessed 2026-07-29) | No DOI (living specification/framework site) | Attestation/signing pattern ABOM's `Attestation` object (schema/abom.schema.json) follows, per docs/formal_model.md. |

## Addendum, 2026-07-30: five references added at author's request

References 24-28 were added when the manuscript was expanded from 4 to 7 pages. All five are the
lead author's own prior published work, cited for a specific, narrow claim each, not as a general
background dump. Each DOI/URL was independently re-verified via the Crossref API before insertion.

| # | Citation | DOI | Verified via | Maps to which ABOM claim |
|---|---|---|---|---|
| 24 | Gentyala, S., Caprio, F., Mudusu, S.K., Darisi, S.K., Allani, S.K. "The Metamorphosis of Access: Strategic Imperatives for Identity 3.0 and Zero Trust Integration in Critical Infrastructure." *SmartNets 2026*, pp. 1-6. | 10.1109/smartnets69662.2026.11604842 | Crossref | Motivates the continuous, evidence-based zero-trust framing in Section I/II; ABOM is positioned as the evidentiary layer beneath this kind of program, not a replacement for it. |
| 25 | Gentyala, S., Sanjeevaiah, K., Darisi, S.K. "SybilShield-Core: A Composite Trust Scoring Framework for Sybil Attack Mitigation in Permissionless Blockchain Networks." *ICICDS 2026*, pp. 349-355. | 10.1109/icicds70526.2026.11604799 | Crossref | Related graph-topology-based anomaly-surfacing precedent, cited to bound (not claim novelty for) ABOM's orphan-identity and cross-tenant-reachability checks (Section II.B, VII). |
| 26 | Gentyala, S., Tejasri, N., Mudusu, S.K. "A Multi-Stage NLP Framework for Enterprise Data Protection in Public LLM Interactions." *ICIRCA 2026*, pp. 2057-2064. | 10.1109/icirca69024.2026.11570292 | Crossref | Cited in Section II.B as an orthogonal, complementary data-layer control (protects prompt/response content) distinct from ABOM's authorization-layer evidence (protects/records access decisions); the two do not overlap and neither substitutes for the other. Previously excluded from the reference list as too tangential (see prior version of this file); re-scoped and re-included once a specific, non-overlapping claim was identified rather than cited as general background. |
| 27 | Gentyala, S., Srinivas, C., Dhumpati, R. "A Zero-Trust Supply Chain Security Framework for Model Context Protocol-based AI Systems." *ICCBI 2026*, pp. 913-919. | 10.1109/ICCBI68589.2026.11619741 | Crossref | Direct MCP-specific related work: runtime tool-registry attestation and capability-binding enforcement, complementary to ABOM's after-the-fact MCP grant evidence (Section II.B, Threat Model T4). |
| 28 | Gentyala, S. "Securing the Swarm: Governance, Attack Surfaces, and Zero-Trust Architectures in Multi-Agent AI Environments." Cloud Security Alliance, 2026-06-24. | No DOI (blog publication) | Manually confirmed at cloudsecurityalliance.org | Multi-agent AI governance/zero-trust framing that motivates positioning ABOM as an evidence layer beneath a control plane (Section I, II.B), not a competing enforcement mechanism. |
