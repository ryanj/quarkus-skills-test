

## Lola Skills

These skills are installed by Lola and provide specialized capabilities.
When a task matches a skill's description, read the skill's SKILL.md file
to learn the detailed instructions and workflows.

**How to use skills:**
1. Check if your task matches any skill description below
2. Use `read_file` to read the skill's SKILL.md for detailed instructions
3. Follow the instructions in the SKILL.md file

<!-- lola:skills:start -->

### secdevai

#### secdevai
**When to use:** AI-powered secure development assistant. Dispatches to review, fix, tool, and export subcommands. Use when the user invokes /secdevai with no subcommand or needs an overview of available security commands.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai/SKILL.md` for detailed guidance.

#### secdevai-dast
**When to use:** Dynamic Application Security Testing (DAST) using RapiDAST and ZAP. Use when the user wants to scan a running web app or API for security vulnerabilities, run a DAST scan, test a service endpoint, use RapiDAST or ZAP, or says "/secdevai dast" or "/secdevai-dast". Auto-detects Dockerfile/Compose for containerized targets, finds OpenAPI specs, guides the full scan workflow from target setup through SARIF result export, and — uniquely — traces each DAST finding back to the exact source file and line that is the root cause.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-dast/SKILL.md` for detailed guidance.

#### secdevai-export
**When to use:** Export security review results to Markdown and SARIF report formats. Use when the user wants to save, export, or generate reports from security review findings produced by /secdevai review, /secdevai fix, or /secdevai tool.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-export/SKILL.md` for detailed guidance.

#### secdevai-fix
**When to use:** Apply suggested security fixes from a prior review. Use when the user wants to remediate security findings with before/after code diffs, severity filtering, and explicit approval before modifying code.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-fix/SKILL.md` for detailed guidance.

#### secdevai-help
**When to use:** Display all available SecDevAI commands, usage examples, aliases, and configuration options. Use when the user asks for help, needs a command reference, or wants to see the typical security review workflow.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-help/SKILL.md` for detailed guidance.

#### secdevai-oci-image-security
**When to use:** Analyze OCI container images for security vulnerabilities, misconfigurations, supply chain risks, and hardening gaps. Use when reviewing container images from Red Hat, Quay.io, Docker Hub, or any OCI-compliant registry. Covers CVE analysis, config security, EOL component detection, credential exposure, and TLS/crypto misconfigurations.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-oci-image-security/SKILL.md` for detailed guidance.

#### secdevai-review
**When to use:** Perform AI-powered security code review using OWASP Top 10, CWE/SANS Top 25, and WSTG patterns. Use when reviewing source code, specific files, git commits, or entire codebases for security vulnerabilities. Supports web and non-web code (C/C++, Go, Rust, etc.), multi-language analysis, severity classification, and automated finding validation via subagent.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-review/SKILL.md` for detailed guidance.

#### secdevai-tool
**When to use:** Run external security analysis tools (Bandit, Gosec, Scorecard) inside read-only containers via podman/docker. Use when the user wants to execute specific security tools, combine their output with AI analysis, or run all available tools at once.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-tool/SKILL.md` for detailed guidance.

#### secdevai-validate
**When to use:** Validate security findings for exploitability, severity accuracy, and CVSS scoring. Use when secdevai-review dispatches findings for validation, or when the user invokes /secdevai validate to re-validate prior results. Rejects false positives, calibrates severity to Red Hat classification, and produces per-finding CVSS v3.1 analysis.
**Instructions:** Read `.lola/modules/secdevai/lola-module/skills/secdevai-validate/SKILL.md` for detailed guidance.

<!-- lola:skills:end -->
