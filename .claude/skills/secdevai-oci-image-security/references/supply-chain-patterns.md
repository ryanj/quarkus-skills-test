# Supply Chain Detection Patterns

Common patterns observed in OCI container image security analysis. Load this file when performing supply chain or CVE analysis steps.

---

## Pattern 1: Embedded EOL Libraries in Compiled Binaries

**Risk:** A package may vendor or statically link a library that is end-of-life at the upstream project level, even when the OS-level package for that library is current. Scanners attribute CVEs to OS packages, not embedded copies.

**How to detect:**
- Run `strings <binary> | grep -E "OpenSSL [0-9]|libcurl/[0-9]"` to surface version strings baked into binaries.
- Use `ldd` to identify dynamically linked libraries; compare versions against EOL dates.
- Check build metadata and upstream changelogs for vendored dependency pins.

**Example scenario:**
> A TLS-wrapping utility package in a container image embeds OpenSSL 1.0.x (EOL as of 2019-12-31) as a static dependency, despite the OS-level `openssl` package being a current 3.x version. No CVE is assigned to the utility for this condition, but the embedded library is vulnerable to multiple known OpenSSL 1.0.x CVEs. The correct attribution is to the utility package as a supply chain risk, not to the OS openssl package.

**Escalation criteria:**
- Embedded library is EOL upstream
- Embedded library version is affected by a KEV-listed CVE
- No vendor patch available or planned

---

## Pattern 2: Vendored libcurl with Unpatched CVEs

**Risk:** Packages that vendor libcurl (rather than linking against the system library) do not receive OS-level libcurl patches. The package maintainer must independently vendor updated libcurl releases.

**How to detect:**
- Identify packages with embedded libcurl via: `find / -name "libcurl.so*" 2>/dev/null` — multiple hits indicate vendored copies.
- Compare embedded version against current libcurl release and known CVE list.
- Check the upstream package source for vendored `curl/` or `libcurl/` directories.

**Example scenario:**
> A hardware attestation tool ships a vendored libcurl at a version affected by multiple moderate-severity CVEs (including transport-layer and credential handling issues). The system `curl` package is patched, but the tool's vendored copy is not. This is a supply chain finding against the tool, not a generic libcurl finding.

**Escalation criteria:**
- Vendored libcurl version differs from system libcurl version
- Vendored version is affected by CVEs with CVSS ≥ 7.0
- Package is used in a network-facing or authentication context

---

## Pattern 3: Unsigned or Unverifiable Base Images

**Risk:** Images built on unverified base layers inherit unknown provenance for all OS packages and configurations.

**How to detect:**
- Check for cosign/sigstore signature: `cosign verify <image>`
- For Red Hat images: verify presence of `com.redhat.component` label and cross-reference against `registry.access.redhat.com`.
- For Docker Hub official images: confirm `Docker Official Image` badge and check image definition repository.

**Escalation criteria:**
- No verifiable image signature
- Base image from a non-official publisher on Docker Hub
- Base image label claims Red Hat/UBI origin but is not from `registry.access.redhat.com` or `registry.redhat.io`

---

## Pattern 4: Build Artifacts Left in Production Layers

**Risk:** Compilers, package manager caches, development headers, and test tooling left in production image layers expand the attack surface and may contain exploitable tools.

**How to detect:**
- Inspect image layers: `docker history <image>` or `dive <image>`
- Look for: `gcc`, `make`, `pip`, `npm`, `go build` artifacts, `*.a` static library files, test suites
- Check `/tmp`, `/root`, and build user home directories for leftover artifacts

**Escalation criteria:**
- Compiler toolchain present in final image layer
- Package manager (pip, npm, yum/dnf) cache present and executable
- Source code present in production image

---

## Pattern 5: Packages with Significantly Lagged Update Cadence

**Risk:** When a package in a container image is many releases behind the upstream project, it may indicate abandoned maintenance, making future CVE patching unlikely.

**How to detect:**
- Compare installed package version against current upstream release tag.
- Check upstream project for activity (last commit, last release date).
- Query the Red Hat Security Advisories API for outstanding unpatched CVEs against the installed version.

**Escalation criteria:**
- Package is more than 2 major versions behind upstream
- Upstream project shows no activity in 12+ months
- Outstanding HIGH/CRITICAL CVEs with no patch scheduled
