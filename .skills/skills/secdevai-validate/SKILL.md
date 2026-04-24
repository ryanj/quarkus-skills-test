---
name: secdevai-validate
description: Validate security findings for exploitability, severity accuracy, and CVSS scoring. Use when secdevai-review dispatches findings for validation, or when the user invokes /secdevai validate to re-validate prior results. Rejects false positives, calibrates severity to Red Hat classification, and produces per-finding CVSS v3.1 analysis.
---

# SecDevAI Validate Command

## Description
Validate security findings by checking exploitability, calibrating severity against Red Hat's classification, and producing CVSS v3.1 analysis. Invoked automatically by `secdevai-review` as a subagent, or manually via `/secdevai validate` or the `/secdevai-validate` alias.

## Usage
```
/secdevai validate               # Validate findings from prior review
/secdevai-validate               # Alias: same as /secdevai validate
```

## Expected Response

When dispatched as a subagent from `secdevai-review`, you receive a list of findings. For each finding, perform the full validation pipeline below.

### Step 1: Read the Actual Source Code

**Never rely solely on the review agent's description.** For each finding:

1. Read the source file at the reported location
2. Read surrounding context (at least 20 lines above and below)
3. Trace the data flow — identify where untrusted input enters and whether it reaches the vulnerable sink
4. Check imports, configurations, and middleware that may apply mitigations

### Step 2: Exploitability Analysis

Determine whether the finding is exploitable in a realistic attack scenario.

**Evaluate each condition:**

| Check | Question |
|-------|----------|
| **Reachability** | Is the vulnerable code reachable from an attacker-controlled input? Trace from entry point (HTTP handler, CLI arg, file parser, IPC) to the vulnerable sink. |
| **Existing mitigations** | Are mitigations already in place? (input validation, bounds checks, sanitization, safe wrappers, WAF rules, compiler hardening flags like FORTIFY_SOURCE, stack canaries, ASLR) |
| **Preconditions** | What must be true for exploitation? (specific config, authentication state, race condition, memory layout, platform/architecture) |
| **Attack surface** | Is the component exposed to untrusted users, or is it internal-only / admin-only / test-only? |
| **Weaponizability** | Can this be turned into a reliable exploit, or is it a theoretical concern? |

**For specific vulnerability classes:**

- **Memory safety** (CWE-787, CWE-416, CWE-125, CWE-476, CWE-119, CWE-190): Verify exact buffer sizes, allocation patterns, control flow, and whether modern mitigations (ASLR, stack canaries, FORTIFY_SOURCE) block exploitation
- **Concurrency** (CWE-362): Verify shared state, synchronization primitives, and whether the race window is practically exploitable
- **Injection** (CWE-89, CWE-79, CWE-78): Verify the complete data flow from source to sink — is user input actually interpolated without sanitization?
- **Authentication/Authorization** (CWE-287, CWE-862): Verify whether the bypass works against the deployed auth stack, not just the isolated code path

**Classify exploitability:**

| Verdict | Criteria |
|---------|----------|
| **Exploitable** | Clear attack path exists with realistic preconditions. A competent attacker could weaponize this. |
| **Conditionally exploitable** | Valid vulnerability, but exploitation requires non-default config, specific platform, unlikely race condition, or chained attack. Explain the conditions. |
| **Not exploitable** | The vulnerability pattern exists in the code but mitigations prevent exploitation, or the code is unreachable from attacker input. **Still report as a valid finding** with explanation of why it is not exploitable in current context. |

### Step 3: Severity Calibration — Red Hat Classification

Map each finding to [Red Hat's severity classification](https://access.redhat.com/security/updates/classification):

| Severity | Criteria |
|-----------------|----------|
| **Critical** | Easily exploited by a remote unauthenticated attacker leading to system compromise (arbitrary code execution) without user interaction. Flaws requiring authentication, local/physical access, or unlikely configuration are NOT Critical. |
| **Important** | Easily compromises confidentiality, integrity, or availability. Includes: local/authenticated privilege escalation, unauthenticated remote access to protected resources, authenticated remote code execution, remote denial of service. |
| **Moderate** | More difficult to exploit but could still compromise CIA under certain circumstances. Includes: vulnerabilities that would be Critical/Important but are harder to exploit or affect unlikely configurations. |
| **Low** | Requires unlikely circumstances to exploit, or successful exploit yields minimal consequences. Includes theoretical vulnerabilities with no proven exploitation vector. |

**Challenge the review agent's severity:**
- If the finding requires local access but was rated Critical, downgrade to Important or Moderate
- If the finding requires authentication but was rated as unauthenticated, adjust accordingly
- If exploitation requires non-default configuration, consider downgrade
- If mitigations (SELinux, sandboxing, containerization) limit impact, note and potentially downgrade

### Step 4: CVSS v3.1 Base Score Analysis

Analyze each CVSS base metric independently, arguing for the most accurate value:

#### Attack Vector (AV)
- **Network (N)**: Vulnerable component reachable over the network without local access
- **Adjacent (A)**: Requires same network segment
- **Local (L)**: Requires local access or user must open a crafted file. Many parser bugs are Local, not Network
- **Physical (P)**: Requires physical hardware access
- *Challenge*: If the PoC runs locally on a crafted file, argue for Local unless there is clear evidence of a network-reachable path

#### Attack Complexity (AC)
- **Low (L)**: Exploitation repeatable without special conditions
- **High (H)**: Requires race conditions, non-default configurations, specific memory layouts, or platform constraints
- *Challenge*: If the PoC only works on a specific architecture, requires large input, or depends on non-default settings, argue for High

#### Privileges Required (PR)
- **None (N)**: Completely unauthenticated, anonymous attacker can trigger this
- **Low (L)**: Requires basic authentication or user-level account
- **High (H)**: Requires admin/root privileges
- *Challenge*: If attack requires writing files to a specific directory or calling a privileged API, argue for Low or High

#### User Interaction (UI)
- **None (N)**: Zero user action required
- **Required (R)**: User must process a crafted file, click a link, visit a page, or import data
- *Challenge*: Parser vulnerabilities typically require a user to process attacker-supplied input — argue for Required unless the component autonomously fetches and parses untrusted data

#### Scope (S)
- **Unchanged (U)**: Impact stays within the vulnerable component's security authority
- **Changed (C)**: Exploitation impacts beyond the vulnerable component (container escape, sandbox bypass)
- *Challenge*: Most library-level bugs have Unchanged scope. Argue against Changed unless cross-boundary impact is demonstrated

#### Confidentiality (C)
- **None (N)**: No data leaked. Many DoS/crash bugs have zero confidentiality impact
- **Low (L)**: Limited or non-sensitive data leaked
- **High (H)**: Arbitrary sensitive data readable
- *Challenge*: If the finding is a crash/DoS, argue for None

#### Integrity (I)
- **None (N)**: No data modification. Crashes and info leaks typically have zero integrity impact
- **Low (L)**: Modification limited to non-critical data
- **High (H)**: Arbitrary writes or control flow hijack
- *Challenge*: Integer overflows leading to undersized allocations need careful analysis — does the overflow lead to a write primitive, or just a crash?

#### Availability (A)
- **None (N)**: No availability impact
- **Low (L)**: Degraded performance, service continues
- **High (H)**: Complete denial of service — process crash, hang, or resource exhaustion
- *Challenge*: A crash in a library is High only if the consuming application cannot catch/recover

### Step 5: Produce Verdict

For each finding, return a structured validation result:

```
## Finding <N>: <title>

### Review Agent's Assessment
- **Severity**: <original severity>
- **CWE/OWASP**: <ID>
- **Location**: <file:line>

### Exploitability Analysis
- **Verdict**: Exploitable | Conditionally exploitable | Not exploitable
- **Attack path**: <describe the realistic attack scenario or explain why exploitation fails>
- **Mitigations found**: <list existing mitigations in the code/environment>
- **Preconditions**: <what must be true for exploitation>

### CVSS v3.1 Analysis
- **AV**: <value> — <reasoning>
- **AC**: <value> — <reasoning>
- **PR**: <value> — <reasoning>
- **UI**: <value> — <reasoning>
- **S**: <value> — <reasoning>
- **C**: <value> — <reasoning>
- **I**: <value> — <reasoning>
- **A**: <value> — <reasoning>

### CVSS Vector: <CVSS:3.1/AV:X/AC:X/PR:X/UI:X/S:X/C:X/I:X/A:X>
### CVSS Score: <numeric score>
### Severity: <Critical | Important | Moderate | Low>

### Validation Verdict: <CONFIRMED | ADJUSTED | DISPUTED | REJECTED>
- **CONFIRMED**: Exploitability and severity match the review agent's assessment
- **ADJUSTED**: Valid finding, but severity or exploitability was recalibrated (explain why)
- **DISPUTED**: Finding exists but exploitability is questionable — needs manual review
- **REJECTED**: False positive — vulnerable pattern does not exist at the reported location, or mitigations fully prevent exploitation

### Reasoning
<2-3 sentence explanation of the verdict, citing specific code evidence>
```

### Step 6: Return Summary to Review Agent

After validating all findings, return a summary:

```
## Validation Summary

| # | Finding | Original Severity | Validated Severity | CVSS Score | Exploitability | Verdict |
|---|---------|-------------------|-------------------|------------|----------------|---------|
| 1 | <title> | Critical | Important | 7.5 | Conditionally exploitable | ADJUSTED |
| 2 | <title> | High | High | 8.1 | Exploitable | CONFIRMED |
| ... | | | | | | |

### Statistics
- **Total findings validated**: N
- **Confirmed**: N (severity matches)
- **Adjusted**: N (severity recalibrated)
- **Disputed**: N (needs manual review)
- **Rejected**: N (false positives removed)

### Rejected Findings (moved to skipped)
- <Finding X>: <reason for rejection>
```

## Processing Rules for the Calling Agent (secdevai-review)

When `secdevai-review` receives validation results, apply:

| Verdict | Action |
|---------|--------|
| **CONFIRMED** | Keep finding with original severity. Add CVSS vector and score. |
| **ADJUSTED** | Update severity to the validated level. Add CVSS vector, score, and adjustment reason. |
| **DISPUTED** | Keep finding, add "[Needs Manual Review]" tag and the dispute reasoning. |
| **REJECTED** | Remove from results. Log to skipped findings with rejection reason. |

For all retained findings, enrich the output with:
- `CVSS Vector`: the computed CVSS:3.1 vector string
- `CVSS Score`: the numeric score
- `Severity`: the calibrated severity per Red Hat classification
- `Exploitability`: the exploitability verdict and attack path summary

## Analysis Rules

1. **Read the actual source code** — never rely solely on the review agent's description
2. **Be specific in challenges** — "AV should be Local because the only consumption path requires opening a crafted file" is useful; "I think this is overstated" is not
3. **Acknowledge when the review agent is right** — do not downgrade for the sake of downgrading
4. **Do NOT dismiss valid findings** — your job is to calibrate severity, not reject discoveries
5. **Do NOT add new findings** — you validate what the review agent found
6. **Document your reasoning** — every CVSS component and severity decision must have clear justification
7. **Consider deployment context** — how is this code actually used? What are typical consuming applications?
8. **Check for mitigating factors** — resource limits, process isolation, input size limits, compile-time hardening

## Fallback: Inline Validation

If subagent dispatch is unavailable (e.g., platform does not support parallel task execution): the calling agent performs validation inline by re-reading each flagged location and applying the same verification steps from this skill. Annotate uncertain findings with "[Needs Manual Review]".
