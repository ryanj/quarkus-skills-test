---
name: secdevai
description: AI-powered secure development assistant. Dispatches to review, fix, tool, and export subcommands. Use when the user invokes /secdevai with no subcommand or needs an overview of available security commands.
---

# SecDevAI Secure Development Assistant Command

## Description
AI-powered secure development assistant that dispatches to specialized sub-skills. Use `/secdevai` with no arguments for help, or specify a subcommand.

**Important**: `/secdevai` with no arguments shows help. Use `/secdevai review` to perform security reviews.

## Usage
```
/secdevai                      # Show help (default)
/secdevai help                 # Show all available commands
/secdevai review               # Review selected code (if selected) or full codebase scan
/secdevai review @ file        # Review specific file
/secdevai review last-commit   # Review last commit
/secdevai review last-commit --number N  # Review last N commits
/secdevai fix [severity high]  # Apply suggested fixes (with approval, optional severity filter)
/secdevai tool bandit          # Use specific tool (bandit, scorecard, all)
/secdevai dast                 # DAST scan web app/API using RapiDAST (auto-detects Dockerfile/OpenAPI)
/secdevai dast --url <URL>     # DAST scan a specific URL (legal warning applies)
/secdevai git-commit           # Commit approved fixes (requires git config and approved fixes)
/secdevai validate             # Validate findings from prior review (exploitability, CVSS, severity)
/secdevai export json          # Export report (json, markdown, sarif)
/secdevai oci-image-security   # Analyze OCI container images for security issues
```

## Aliases
```
/secdevai-help                 # Show help (alias for /secdevai help)
/secdevai-fix                  # Apply suggested fixes (alias for /secdevai fix)
/secdevai-review               # Review code (alias for /secdevai review)
/secdevai-report               # Generate security report
/secdevai-tool                 # Use specific tool (alias for /secdevai tool)
/secdevai-validate             # Validate findings (alias for /secdevai validate)
/secdevai-dast                 # DAST scan (alias for /secdevai dast)
/secdevai-export               # Export report (alias for /secdevai export)
/secdevai-oci-image-security   # Analyze OCI container images for security issues
```

## Command Dispatch

When user runs `/secdevai`, route to the appropriate sub-skill:

1. **No arguments / `help`** (default):
   - **IMPORTANT**: `/secdevai` with no arguments should ONLY show help, NOT run review
   - Display all available commands with descriptions
   - Show usage examples
   - List all options and flags
   - Do NOT perform any security review unless `review` is explicitly specified

2. **`review`**: **Delegate to the `secdevai-review` skill.**
   The review skill handles all security code review logic including scope detection, security context loading, OWASP/WSTG analysis, findings presentation, and result export.

3. **`fix`**: **Delegate to the `secdevai-fix` skill.**
   The fix skill handles applying security remediation with before/after diffs, severity filtering, explicit approval, and result export.

4. **`tool`**: **Delegate to the `secdevai-tool` skill.**
   The tool skill handles external tool execution (Bandit, Scorecard), output parsing, AI synthesis, and result export.

5. **`validate`**: **Delegate to the `secdevai-validate` skill.**
   The validate skill checks exploitability, calibrates severity against Red Hat's classification, and produces CVSS v3.1 analysis. Typically invoked automatically by `secdevai-review` as a subagent, but can be run manually to re-validate prior results.

6. **`export`**: **Delegate to the `secdevai-export` skill.**
   The export skill handles converting findings to Markdown and SARIF formats.

7. **`oci-image-security`**: **Delegate to the `secdevai-oci-image-security` skill.**
   The OCI image security skill analyzes container images for CVE/package vulnerabilities, configuration security issues, supply chain risks, and hardening gaps. Use when reviewing Dockerfiles, Containerfiles, or OCI images from any registry.

8. **`dast`**: **Delegate to the `secdevai-dast` skill.**
   The DAST skill performs dynamic application security testing using RapiDAST. It auto-detects Dockerfile/Compose for container setup, discovers OpenAPI specs, handles authentication, runs passive then optionally active scanning, and exports SARIF results. Crucially, it also **traces each DAST finding back to the exact source file and line that is the root cause** — bridging the gap between a runtime HTTP observation (e.g. "SQL injection detected at `/api/pets/name/<param>`") and the vulnerable code that produced it (e.g. raw f-string SQL construction in `db.py:32`). The correlation report is saved alongside the SARIF as `source-correlation.md`.

9. **`git-commit`**:
   - Only proceed if there are approved fixes that have been applied
   - Verify git is configured (check for git repository and user config)
   - If conditions met: Create a commit with descriptive message about security fixes
   - If conditions not met: Explain what's missing (no approved fixes or git not configured)

## Security Principles

Follow these principles from the security context:
- Complete Mediation
- Defense in Depth
- Least Privilege
- Secure by Design, Default, Deployment

## Security Context Sources

This command uses multiple security context files:
- `secdevai-review/context/security-review.context` - OWASP Top 10 patterns (always loaded)
- `secdevai-review/context/wstg-testing.context` - OWASP WSTG v4.2 web app testing patterns (auto-loaded for web code)
- `secdevai-review/context/golang-security.context` - Go-specific vulnerabilities and weaknesses (auto-loaded for Go code)

**Multi-Language Support**: While context files contain primarily Python examples, all sub-skills MUST adapt security patterns to the language being reviewed (JavaScript, Java, Go, Ruby, PHP, C#, Rust, etc.). Translate the security principles and provide language-specific remediation with appropriate frameworks and idioms.

## Integration

This command integrates with:
- `secdevai-review/context/` directory for security analysis guidelines
- `secdevai-validate` for finding validation, exploitability checks, CVSS scoring, and Red Hat severity calibration
- `secdevai-tool` for optional tool integration via containerized runners
- `secdevai-dast/scripts/rapidast-scan.sh` for DAST scanning via RapiDAST (produces SARIF + `source-correlation.md`)
- `secdevai-export/scripts/results_exporter.py` for result export
- `.secdevaiignore` for excluding files from scans
- `secdevai-oci-image-security/references/` for OCI container image security patterns
- External tools: Bandit, Scorecard, Trivy, Grype, RapiDAST

## Important Notes

- **Never modify code without explicit approval**
- **Always show preview before changes**
- **Create backups before applying fixes**
- **Respect `.secdevaiignore` file**
- **Cache results to avoid re-scanning**
- **DAST → source tracing**: After any DAST scan, always attempt to trace findings to source code. A DAST finding without a source location is an incomplete result — the developer needs to know *where* to fix, not just *what* was found at runtime.
