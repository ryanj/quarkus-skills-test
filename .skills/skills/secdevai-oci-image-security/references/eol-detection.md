# EOL Component Detection

Reference for identifying end-of-life (EOL) components in OCI container images. Load this file during CVE and supply chain analysis steps.

---

## Why EOL Components Matter

An EOL component will not receive security patches from its upstream maintainer, regardless of whether a CVE has been assigned. This means:

1. Known vulnerabilities may exist but be untracked (no CVE assigned for EOL software).
2. Future vulnerabilities will be permanently unpatched in that version.
3. Scanner tools (Trivy, Grype) may not flag EOL components with full severity if no CVE exists.

EOL components warrant a finding even in the absence of a specific CVE, particularly when they are network-exposed or handle sensitive data.

---

## High-Priority EOL Components to Check

### OpenSSL

| Version | EOL Date | Notes |
|---|---|---|
| 1.0.2 | 2019-12-31 | Very commonly embedded in compiled binaries |
| 1.1.1 | 2023-09-11 | Still appears in many third-party images |
| 3.0.x | 2026-09-07 | Check current Red Hat support status |
| 3.1.x | 2025-03-14 | EOL |

Detection: `strings <binary> | grep -E "OpenSSL [0-9]\.[0-9]"`

### Python

| Version | EOL Date |
|---|---|
| 2.x | 2020-01-01 |
| 3.8 | 2024-10-07 |
| 3.9 | 2025-10-31 |

Detection: `python --version`, `python2 --version`, `python3 --version`; check `/usr/bin/python*`

### Node.js (LTS policy — only even major versions receive LTS)

| Version | EOL Date |
|---|---|
| ≤ 18 | 2025-04-30 |
| 20 | 2026-04-30 |

Detection: `node --version`

### Go runtime (embedded in statically compiled binaries)

Detection: `go version <binary>` or `strings <binary> | grep "go1\."`

Go binaries embed their build toolchain version. Binaries built with EOL Go versions do not receive patches for runtime vulnerabilities (e.g., `net/http` parsing issues).

### Java / JVM

| Vendor | EOL concerns |
|---|---|
| Oracle JDK | Paid support required for extended patches |
| OpenJDK 8 | Community support varies; check Red Hat's OpenJDK support lifecycle for RHEL images |
| OpenJDK 11 | LTS, check current status |

### Key libraries commonly embedded

| Library | Notes |
|---|---|
| libcurl | Check for vendored copies; compare against `curl` CVE list |
| zlib | Versions < 1.2.13 affected by CVE-2022-37434 |
| libxml2 | Frequently embedded in language runtimes |
| expat | Frequently embedded; CVE-2022-25315 and family |

---

## EOL Detection Workflow

1. **OS-level packages**: Run `rpm -qa --queryformat '%{NAME} %{VERSION}\n'` (RHEL/UBI) or `dpkg -l` (Debian). Cross-reference against vendor EOL tables.

2. **Embedded libraries**: Use `strings` and `ldd` as described in `./supply-chain-patterns.md`. Focus on binaries in `/usr/bin`, `/usr/sbin`, `/usr/local/bin`, and any application directories.

3. **Language runtimes**: Check version outputs for Python, Node, Ruby, Java, Go, Rust. Compare against upstream EOL schedules at https://endoflife.date.

4. **Application frameworks**: Django, Spring Boot, Rails, Express — check for EOL versions in application manifests (`requirements.txt`, `pom.xml`, `package.json`, `Gemfile.lock`).

---

## Finding Template for EOL Components

When an EOL component is found without a specific CVE:

```
**Finding:** EOL [component] [version] embedded in [package/binary]
**Category:** Supply Chain
**Severity:** Moderate (escalate to High if network-exposed or handling sensitive data)
**Component:** [package] [version] — embedded [library] [version]
**Description:** [library] [version] reached end-of-life on [date] and no longer
  receives security patches from upstream. Future vulnerabilities will be permanently
  unpatched. This was identified via embedded version string in [binary path],
  not the OS-level [library] package (which is current).
**Evidence:** strings [binary] | grep "[library version string]"
**Recommendation:** Update [package] to a version that vendors a current, supported
  [library] release, or request that the package maintainer update the embedded copy.
**References:** https://endoflife.date/[component]
```
