---
name: secdevai-review
description: Perform AI-powered security code review using OWASP Top 10, CWE/SANS Top 25, and WSTG patterns. Use when reviewing source code, specific files, git commits, or entire codebases for security vulnerabilities. Supports web and non-web code (C/C++, Go, Rust, etc.), multi-language analysis, severity classification, and automated finding validation via subagent.
---

# SecDevAI Review Command

## Description
Perform AI-powered security code review. Invoked via `/secdevai review` or the `/secdevai-review` alias.

## Usage
```
/secdevai review               # Review selected code (if selected) or full codebase scan
/secdevai review @ file        # Review specific file
/secdevai review last-commit   # Review last commit
/secdevai review last-commit --number N  # Review last N commits
/secdevai-review               # Alias: same as /secdevai review
/secdevai-review @ file        # Alias: same as /secdevai review @ file
```

## Expected Response

When this skill is invoked, follow these steps in order:

### Step 1: Detect Scope

Determine what to review (in priority order):

1. If `review last-commit --number N` specified: Review last N commits (requires git)
2. If `review last-commit` specified: Review last commit (requires git)
3. If `review @ file` is specified: Review the specified file
4. If text is selected in UI: Automatically review only the selected code
5. Otherwise (default): Scan entire codebase

### Step 2: Filter with `.secdevaiignore`

Read `secdevai-review/context/.secdevaiignore` and apply its patterns to the files identified in Step 1. In addition to the explicit patterns in that file, **always skip**:

- **Binary and media files** — images, fonts, audio, video, compiled artifacts (`.class`, `.pyc`, `.o`), archives, and other non-human-readable content
- **SecDevAI own files** — the skill's own configuration and context files, including `.secdevaiignore`, `secdevai-*/` skill directories, `secdevai-review/context/`, and `secdevai-results/` output

> **Note:** Documentation files (markdown, RST, plaintext, etc.) are **not** skipped. They can contain hardcoded secrets (passwords, API keys, tokens), leaked infrastructure details, or AI agent instructions (e.g. `SKILL.md`, `AGENTS.md`) that may introduce prompt injection risks.

Apply filtering according to scope:

- **Codebase scan**: Exclude matching files from the scan.
- **Commit review** (`last-commit` / `last-commit --number N`): Check changed files in each commit against the rules above and remove matches from the review set.
- **File review** (`@ file`): If the specified file would be excluded, warn the user but proceed — they explicitly chose it.
- **Selected text**: No filtering — the user explicitly selected code to review.

**If ALL files are excluded after filtering**, stop and report:

```
## Security Review: Skipped

**Scope**: [commit hash / file / codebase]
**Reason**: All files match .secdevaiignore exclusion patterns or are binary files. No security-relevant content to review.

Tip: To review an excluded file, remove its pattern from .secdevaiignore.
```

**If SOME files are excluded**, proceed with the remaining files and list the skipped files at the end of the review output.

### Step 3: Load Security Context

- **Always read**: `secdevai-review/context/security-review.context` for OWASP Top 10 patterns

- **Auto-detect CWE/SANS Top 25 native code context** (additionally read `secdevai-review/context/cwe-top25-native.context` if ANY condition applies):
  - Source code includes C (`.c`, `.h`), C++ (`.cpp`, `.cc`, `.cxx`, `.hpp`), or Rust (`.rs`) files
  - `Makefile`, `CMakeLists.txt`, `meson.build`, `Cargo.toml`, or `*.sln`/`*.vcxproj` build files are present
  - User explicitly mentions: "CWE", "SANS Top 25", "buffer overflow", "memory safety", "native code", "systems code"
  - Assembly (`.s`, `.asm`) files or FFI/JNI bindings are detected

- **Auto-detect WSTG context** (additionally read `secdevai-review/context/wstg-testing.context` if ANY condition applies):
  - Source code is for a web application, web service, or web site
  - User explicitly mentions: "WSTG", "Web Security Testing Guide", or category numbers (4.1-4.12)

- **Auto-detect Golang context** (additionally read `secdevai-review/context/golang-security.context` if ANY condition applies):
  - Source code or files under review include Go (e.g. `.go` files, `go.mod` present)

- **Auto-detect OCI/container context** (additionally read `secdevai-oci-image-security/references/` files if ANY condition applies):
  - `Dockerfile` or `Containerfile` is present in the repo
  - Kubernetes manifests (YAML files with `apiVersion`/`kind` fields) are detected
  - OpenShift deployment configs or templates are present
  - `docker-compose.yml` or `compose.yaml` exists

- **Note**: CWE/SANS Top 25 patterns cover memory safety, integer overflow, race conditions, and privilege management for native/systems code; WSTG patterns enhance web application security analysis; golang-security.context provides Go-specific vulnerability and weakness patterns; OCI image security references provide container supply chain, configuration, hardening, and EOL detection patterns

### Step 4: Optional Tool Integration

- If `tool` specified: Run the tool via `secdevai-tool` (see `secdevai-tool/scripts/container-run.sh`)
- Parse tool output and synthesize with AI analysis
- If tool unavailable: Fall back to AI-only analysis

### Step 5: Perform Analysis

- Scan code for security patterns from loaded context (OWASP Top 10 and/or CWE/SANS Top 25 depending on loaded contexts)
- Classify findings by severity (Critical/High/Medium/Low/Info)
- Reference OWASP categories and/or CWE IDs
- Provide context-aware explanations

### Step 5.5: Validate Findings — Delegate to `secdevai-validate`

**Purpose**: Reduce false positives and calibrate severity by dispatching findings to the `secdevai-validate` skill.

**Delegate to the `secdevai-validate` skill.** Pass all findings from Step 5 to the validation skill, which independently:
1. Reads the actual source code at each reported location
2. Checks exploitability — whether a realistic attack path exists
3. Calibrates severity against [Red Hat's classification](https://access.redhat.com/security/updates/classification) (Critical / Important / Moderate / Low)
4. Produces a CVSS v3.1 base score analysis for each finding

Dispatch via subagent when the platform supports parallel task execution. Pass findings using this prompt template:

```
Use the secdevai-validate skill to validate the following security findings.
Read the actual source code for each finding. Check exploitability, calibrate severity per Red Hat classification, and produce CVSS v3.1 analysis.

Findings:
[paste the structured findings list from Step 5]
```

**Processing validation results** (returned by `secdevai-validate`):

| Verdict | Action |
|---------|--------|
| **CONFIRMED** | Keep finding with original severity. Add CVSS vector and score. |
| **ADJUSTED** | Update severity to the validated level. Add CVSS vector, score, and adjustment reason. |
| **DISPUTED** | Keep finding, add "[Needs Manual Review]" tag and the dispute reasoning. |
| **REJECTED** | Remove from results. Log to skipped findings with rejection reason. |

For all retained findings, enrich the output with: CVSS vector string, CVSS numeric score, Severity, and exploitability verdict.

**Report only valid, exploitable findings** in the final output. Non-exploitable findings that are still valid issues should be listed in a separate "Informational / Not Exploitable" section with the explanation from the validation skill.

**If subagent dispatch is unavailable** (e.g., platform does not support parallel task execution): perform the validation inline by reading the `secdevai-validate` skill and applying its steps directly. Still annotate uncertain findings with "[Needs Manual Review]".

### Step 6: Present Findings

Present only validated, exploitable findings. Group by Severity:

```
## 🔒 **Security Review Results**

### 🔴 **Critical** (2)
- [Finding with code reference, CVSS vector/score, exploitability summary]

### 🟠 **Important** (3)
- [Finding details with CVSS]

### 🟡 **Moderate** (5)
- [Finding details with CVSS]

### 🔵 **Low** (1)
- [Finding details with CVSS]

### ℹ️ **Informational / Not Exploitable** (2)
- [Valid pattern but not exploitable — with explanation]

**Total**: 11 validated findings across [file/codebase] (2 false positives rejected)
```

Each finding should include:
- `Severity`: Critical / Important / Moderate / Low
- `CVSS Vector`: CVSS:3.1/AV:X/AC:X/PR:X/UI:X/S:X/C:X/I:X/A:X
- `CVSS Score`: numeric score
- `Exploitability`: Exploitable / Conditionally exploitable / Not exploitable
- `Validation`: CONFIRMED / ADJUSTED (with reason) / DISPUTED

### Step 7: Save Results (Optional)

After presenting findings, ask the user:

> **Would you like to export these findings to Markdown and SARIF report files?**

If the user confirms, **delegate to the `secdevai-export` skill**. Collect all findings into the structured data format documented in that skill and invoke export with `command_type="review"`. If the user declines, skip export and proceed.

### Step 8: Offer Remediation (if `fix` also specified)

If `fix` is specified alongside review:
- If `fix severity [level]` specified: Filter fixes by severity (critical, high, medium, low)
- Show suggested fixes with before/after code
- Explain security implications
- Preview changes before applying
- Require explicit approval
- After applying fixes, delegate to the `secdevai-fix` skill for result export

## Security Context Sources

- `secdevai-review/context/security-review.context` - OWASP Top 10 patterns (always loaded)
- `secdevai-review/context/cwe-top25-native.context` - CWE/SANS Top 25 patterns for native/systems code (auto-loaded for C/C++/Rust)
- `secdevai-review/context/wstg-testing.context` - OWASP WSTG v4.2 web app testing patterns (auto-loaded for web code)
- `secdevai-review/context/golang-security.context` - Go-specific vulnerabilities and weaknesses (auto-loaded for Go code)

**CWE/SANS Top 25 Auto-Detection**: The native code context automatically loads when reviewing C, C++, Rust, or other compiled/systems code, or when the user mentions CWE, SANS Top 25, buffer overflows, or memory safety.

**WSTG Auto-Detection**: The WSTG context automatically loads when reviewing web application code or when explicitly requested.

**Golang Auto-Detection**: The Golang context automatically loads when reviewing Go source (e.g. `.go` files, `go.mod`) or when the user mentions Go/Golang.

**OCI/Container Auto-Detection**: The OCI image security references automatically load when the repo contains Dockerfiles, Containerfiles, Kubernetes manifests, or docker-compose files.

## Multi-Language Support

**CRITICAL**: While security context files contain primarily Python examples, you MUST adapt patterns to the language being reviewed.

### Language Detection and Adaptation

1. **Detect the Language**: Identify the programming language from file extension, syntax, or imports
   - C: `.c`, `.h`, `#include <stdio.h>`, `malloc`, `free`
   - C++: `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `#include <iostream>`, `std::`, `class`, `template`
   - Rust: `.rs`, `use`, `fn`, `impl`, `unsafe`, `Cargo.toml`
   - Python: `.py`, imports like `import flask`, `from django`
   - JavaScript/TypeScript: `.js`, `.ts`, `.jsx`, `.tsx`, `require()`, `import from`
   - Java: `.java`, `import`, `class`, `public static void`
   - Go: `.go`, `package`, `import`, `func`
   - Ruby: `.rb`, `require`, `def`, `class`
   - PHP: `.php`, `<?php`, `namespace`
   - C#: `.cs`, `using`, `namespace`

2. **Translate Security Patterns**: Apply the same security principle but with language-specific syntax

   **Example - SQL Injection**:
   
   *Python (from context)*:
   ```python
   # BAD
   query = f"SELECT * FROM users WHERE id = {user_id}"
   # GOOD
   cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
   ```
   
   *JavaScript/Node.js (your response)*:
   ```javascript
   // BAD
   const query = `SELECT * FROM users WHERE id = ${userId}`;
   // GOOD
   db.query("SELECT * FROM users WHERE id = ?", [userId]);
   ```
   
   *Java (your response)*:
   ```java
   // BAD
   String query = "SELECT * FROM users WHERE id = " + userId;
   // GOOD
   PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
   stmt.setInt(1, userId);
   ```
   
   *Go (your response)*:
   ```go
   // BAD
   query := fmt.Sprintf("SELECT * FROM users WHERE id = %s", userID)
   // GOOD
   db.Query("SELECT * FROM users WHERE id = ?", userID)
   ```

3. **Use Language-Specific Frameworks and Idioms**:
   - C: POSIX APIs, OpenSSL, safe string functions (`strlcpy`/`snprintf`), SEI CERT C patterns
   - C++: STL containers, smart pointers (`std::unique_ptr`, `std::shared_ptr`), RAII, C++ Core Guidelines
   - Rust: Ownership/borrowing (safe Rust), `unsafe` blocks, `std::fs`, `tokio` patterns
   - Python: Django ORM, Flask, FastAPI patterns
   - JavaScript: Express.js, Next.js, React patterns
   - Java: Spring Security, Jakarta EE patterns
   - Go: net/http, Gin, Echo patterns
   - Ruby: Rails security patterns
   - PHP: Laravel, Symfony patterns
   - C#: ASP.NET Core patterns

4. **Provide Language-Appropriate Remediation**:
   - Reference language-specific security libraries
   - Use idiomatic code for that language
   - Cite language-specific documentation

5. **Security Principles Are Universal**:
   - The underlying vulnerability (SQL injection, XSS, etc.) is the same
   - The detection pattern (string concatenation, unescaped input) is similar
   - Only the syntax and remediation differ

### Example Language Adaptations

**Buffer Overflow Prevention** (CWE-787, native code):
- C: Use `snprintf` instead of `sprintf`, `strncpy`/`strlcpy` instead of `strcpy`, `fgets` instead of `gets`
- C++: Prefer `std::string`, `std::vector`, `std::array` over raw buffers; use `.at()` for bounds-checked access
- Rust: Safe Rust prevents buffer overflows at compile time; audit `unsafe` blocks

**Memory Management** (CWE-416, CWE-415, native code):
- C: Nullify pointers after `free()`, use static analysis (Coverity, cppcheck)
- C++: Use smart pointers (`std::unique_ptr`, `std::shared_ptr`), RAII for resource management
- Rust: Ownership system prevents use-after-free; audit `unsafe` blocks and raw pointer usage

**Integer Overflow** (CWE-190, native code):
- C: Check before arithmetic: `if (a > SIZE_MAX - b)`, use safe integer libraries
- C++: Use `<limits>`, `std::numeric_limits`, or safe integer libraries like SafeInt
- Rust: Debug builds panic on overflow; use `checked_add()`, `saturating_add()` in release

**XSS Prevention**:
- Python/Flask: Use Jinja2 auto-escaping, `escape()`, `Markup()`
- JavaScript/React: Use `textContent`, DOMPurify, React auto-escaping
- Java: Use OWASP Java Encoder, ESAPI
- Go: Use `html.EscapeString()`, `template.HTMLEscapeString()`

**Authentication**:
- Python: bcrypt, argon2, werkzeug.security
- JavaScript: bcrypt.js, passport.js, jsonwebtoken
- Java: Spring Security, BCryptPasswordEncoder
- Go: golang.org/x/crypto/bcrypt

**CSRF Protection**:
- Python/Django: `@csrf_protect`, CSRF middleware
- JavaScript/Express: csurf middleware
- Java/Spring: `@EnableWebSecurity`, CSRF token
- Go: gorilla/csrf

### Response Format for Non-Python Code

When reviewing non-Python code, structure your findings exactly the same way but with appropriate language examples.

**Web/managed language example (OWASP)**:

```
## 🔴 **Critical: SQL Injection**

**Location**: `UserController.java:42-45`
**Language**: Java
**OWASP Category**: A03: Injection
**CWE**: CWE-89

**Vulnerable Code**:
```java
String query = "SELECT * FROM users WHERE username = '" + username + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

**Risk**: Attacker can inject SQL commands leading to data breach

**Remediation**:
```java
String query = "SELECT * FROM users WHERE username = ?";
PreparedStatement stmt = connection.prepareStatement(query);
stmt.setString(1, username);
ResultSet rs = stmt.executeQuery();
```

**References**:
- OWASP: https://owasp.org/www-community/attacks/SQL_Injection
- CWE-89: https://cwe.mitre.org/data/definitions/89.html
```

**Native/systems code example (CWE/SANS Top 25)**:

```
## 🔴 **Critical: Buffer Overflow (CWE-787)**

**Location**: `network.c:87-89`
**Language**: C
**CWE**: CWE-787 (Out-of-bounds Write)
**Severity**: Critical
**CVSS Vector**: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
**CVSS Score**: 9.8
**Exploitability**: Exploitable — network-reachable parser with no bounds checking
**Validation**: ✅ CONFIRMED

**Vulnerable Code**:
```c
char buf[64];
strcpy(buf, packet->payload);  // No bounds checking
```

**Risk**: Stack-based buffer overflow allows arbitrary code execution via crafted network packet

**Remediation**:
```c
char buf[64];
strncpy(buf, packet->payload, sizeof(buf) - 1);
buf[sizeof(buf) - 1] = '\0';
```

**References**:
- CWE-787: https://cwe.mitre.org/data/definitions/787.html
- SANS Top 25: https://www.sans.org/top25-software-errors
- SEI CERT C: https://wiki.sei.cmu.edu/confluence/display/c/STR31-C
```

## Verification Requirements

**CRITICAL - Line Number Verification**: Before presenting any findings:
1. After analyzing git diff/commits, read the actual modified files
2. Verify all line numbers in findings match the actual file content
3. Ensure Location fields match code reference line numbers exactly
4. Cross-check each finding against actual file content

**Format Consistency**:
- Location: `file:line_start-line_end` must match code block `startLine:endLine:filepath`
- Read actual files to confirm line numbers, don't rely only on diff context
