---
name: secdevai-oci-image-security
description: Analyze OCI container images for security vulnerabilities, misconfigurations, supply chain risks, and hardening gaps. Use when reviewing container images from Red Hat, Quay.io, Docker Hub, or any OCI-compliant registry. Covers CVE analysis, config security, EOL component detection, credential exposure, and TLS/crypto misconfigurations.
---

# OCI Container Image Security Analysis

This skill guides systematic security analysis of OCI container images. It is structured around four core finding categories that consistently yield actionable signal when analyzing images from registries such as Red Hat, Quay.io, and Docker Hub.

## When to Use This Skill

- Reviewing container images before promotion to production or a registry
- Triaging CVE scanner output (Trivy, Grype, ACS/RHACS) for a container image
- Analyzing a new base image or upstream image for adoption decisions
- Performing security review as part of a FedRAMP ConMon or ATO workflow
- Investigating a supply chain concern involving an OCI image or package
- Hardening a Dockerfile or image build pipeline

## Analysis Workflow

Work through the four finding categories in order. Each category has its own detection patterns and reference material.

### 1. CVE and Package Vulnerability Analysis

Goal: Identify exploitable or high-signal CVEs in the image's installed packages, with a focus on supply chain and embedded component risks that scanner tools may miss.

Steps:
1. Run Trivy or Grype against the image and collect the raw findings.
2. Filter for HIGH and CRITICAL CVEs. Cross-reference against CISA KEV for any active exploitation.
3. Look beyond top-level packages — check for **embedded or vendored libraries** that scanners may not attribute correctly. See `./references/supply-chain-patterns.md` for known high-risk patterns.
4. For each HIGH/CRITICAL CVE: assess exploitability in the container context (network exposure, privilege level, whether the vulnerable code path is reachable).
5. Flag any packages that are **end-of-life (EOL)** at the upstream level even if no specific CVE is assigned. EOL components represent ongoing unpatched risk. See `./references/eol-detection.md`.

Key signals to escalate:
- Embedded EOL OpenSSL, libcurl, or libssl in compiled binaries (not OS packages)
- Packages shipping vendored copies of libraries with known CVEs
- Any KEV-listed CVE present in the image

### 2. Configuration Security Analysis

Goal: Identify default credentials, insecure service configurations, and settings that create exploitable conditions at runtime.

Steps:
1. Inspect entrypoint scripts, config files, and environment variable defaults for hardcoded or default credentials.
2. Check service configuration files for authentication bypass conditions (e.g., empty passwords, `auth=none`, `no-password` defaults).
3. Review TLS/crypto configuration for contradictions — services that advertise TLS support but ship with configurations that disable or weaken it.
4. Look for world-readable credential files, SSH keys, or tokens baked into image layers.

See `./references/config-security-patterns.md` for specific detection patterns and example scenarios.

Key signals to escalate:
- Default credentials present with no documented change-on-first-use enforcement
- TLS advertised in documentation/labels but disabled or optional in default config
- Credential files with overly permissive filesystem permissions in the image

### 3. Supply Chain and Provenance Analysis

Goal: Assess the trustworthiness of the image's build chain and the integrity of its included components.

Steps:
1. Check for image signature and SBOM availability (cosign, sigstore, Red Hat's image signing).
2. Verify base image provenance — is the base a known-good upstream (UBI, official Docker Hub image) or an unverified third-party?
3. Identify any components pulled from external URLs during build (RUN curl | bash patterns, ADD from HTTP, etc.).
4. Check for presence of build tools (compilers, package managers) left in production layers.
5. Review installed package versions against upstream release cadence — significant lag may indicate abandoned maintenance.

See `./references/supply-chain-patterns.md` for specific risk patterns.

### 4. Hardening Gap Analysis

Goal: Identify missing security controls that are expected for the image's intended use case.

Steps:
1. Check for a non-root user — does the image default to running as root (UID 0)?
2. Review capability requirements — does the image require `--privileged` or broad Linux capabilities?
3. Check for seccomp and AppArmor/SELinux compatibility labels.
4. Assess read-only filesystem compatibility — are writable paths minimized?
5. For images intended for FIPS environments: verify FIPS-validated crypto is present and non-FIPS algorithms are not available as defaults.

See `./references/hardening-checklist.md` for environment-specific hardening baselines (RHEL UBI, FedRAMP, CIS).

## Output Format

For each finding, produce a structured entry:

```
**Finding:** [Short title]
**Category:** [CVE | Config | Supply Chain | Hardening]
**Severity:** [Critical | High | Moderate | Low | Informational]
**Component:** [Package name, version, and path if known]
**Description:** [What the issue is and why it matters]
**Evidence:** [Specific file path, config key, package version, or CVE ID]
**Recommendation:** [Concrete remediation or mitigation step]
**References:** [CVE links, upstream advisories, vendor bug tracker if applicable]
```

## Scope Considerations

- **Red Hat / UBI images**: Prioritize CVEs with Red Hat severity ratings. Check the Red Hat Security Advisories (RHSA) feed for patch availability. Deviation Requests (DRs) may be appropriate for CVEs where Red Hat has not issued a patch and exploitation in context is limited.
- **Docker Hub official images**: Treat as untrusted until provenance is verified. Higher bar for supply chain scrutiny.
- **Quay.io third-party images**: Verify organization reputation and signing status. Check for stale builds.
- **Scratch/distroless images**: Package CVE surface is minimal; shift focus to application layer and config analysis.

## Integration Notes

This skill is designed to complement automated scanner output from Trivy, Grype, and ACS/RHACS. It adds the analytical layer that scanners cannot provide: contextual exploitability, configuration logic flaws, and supply chain reasoning. Run scanner tools first, then apply this skill to interpret and prioritize findings.
