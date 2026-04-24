# Usage Guide

Get SecDevAI up and running in your project, then explore advanced features.

## Quick Start

### Installation

[`uv`](https://github.com/astral-sh/uv) is required for installation.

**Option 1: Direct installation from Git (simplest)**

```bash
uv tool install git+https://github.com/RedHatProductSecurity/secdevai.git
```

**Option 2: Install from local clone**

```bash
# Clone the repository first
git clone git@github.com:RedHatProductSecurity/secdevai.git
cd secdevai
# Install from local directory
uv tool install --no-cache .
```

Make sure `~/.local/bin` is in your PATH if using uv.

### Initialize SecDevAI in Your Project

Navigate to the project you want to review (not the secdevai project itself):

```bash
cd your-project  # Your application/codebase to review
secdevai          # Defaults to current directory
# or specify a path
secdevai /path/to/project
```

This will:
- Create `.secdevai/` directory with context files and scripts
- Deploy slash commands to platform-specific directories (see Platform Detection below)
- Create `.secdevaiignore` file

**Platform Detection:**
SecDevAI automatically detects which AI assistant platforms are present in your project:
- If `.claude/` directory exists → commands are deployed to `.claude/commands/` (`.md` format)
- If `.cursor/` directory exists → commands are deployed to `.cursor/commands/` (`.md` format)
- If `.gemini/` directory exists → commands are deployed to `.gemini/commands/` (`.toml` format)
- If **no platform directories are detected** → defaults to `.cursor/commands/` only

**Note:** Gemini CLI uses `.toml` format for commands (as per [Gemini CLI documentation](https://cloud.google.com/blog/topics/developers-practitioners/gemini-cli-custom-slash-commands)), while Cursor and Claude use `.md` format. SecDevAI automatically converts commands to the appropriate format for each platform.

To use commands in multiple platforms, create the platform directories before running `secdevai`:
```bash
mkdir -p .claude .cursor .gemini  # Create directories for all platforms
secdevai                           # Commands will be deployed to all detected platforms
```

### Example Workflow

1. **Initialize SecDevAI**:
   ```bash
   secdevai
   ```

2. **Review a specific file**:
   - In the AI assistant, type: `/secdevai review @ src/api/auth.py`
   - Review the security findings for that file

3. **Review code**:
   - Type: `/secdevai review`
   - If code is selected: Reviews only the selected code
   - If no selection: Reviews entire codebase (full scan)

4. **Review last commit**:
   - Type: `/secdevai review last-commit`
   - Review security findings in the last commit

5. **Apply fixes** (with approval):
   - Type: `/secdevai fix` to apply all fixes
   - Or: `/secdevai fix severity high` to apply only high/critical severity fixes
   - Review suggested changes
   - Approve individual fixes

6. **Commit fixes** (optional):
   - Type: `/secdevai git-commit`
   - Only works if fixes were approved and git is configured

**Note**: Security review results are automatically saved to the `secdevai-results` directory in your project root. Each review creates timestamped subdirectories with Markdown and SARIF reports. See the Results Storage section below for more details.

### Optional: Install Security Tools

For enhanced analysis, install optional tools:

```bash
pip install bandit          # Python security linter
# Install scorecard from https://github.com/ossf/scorecard
```

Then use with:
```
/secdevai tool bandit       # Python security analysis
/secdevai tool scorecard    # Repository security assessment
/secdevai tool all          # Run all available security tools
```

---

## Using the Slash Command

In your AI assistant (Cursor, Claude Code, or Gemini CLI), use:

### Basic Commands

```
/secdevai                      # Show help (default)
/secdevai help                 # Show all available commands
/secdevai review               # Review selected code (if selected) or full codebase scan
/secdevai review @ file        # Review specific file
/secdevai review last-commit   # Review last commit
/secdevai review last-commit --number N  # Review last N commits
/secdevai fix [severity high]  # Apply suggested fixes (with approval, optional severity filter)
```

### Command Aliases

For convenience, you can also use these shorter aliases in Cursor or Claude UI:

```
/secdevai-review               # Alias for /secdevai review
/secdevai-fix                  # Alias for /secdevai fix
/secdevai-help                 # Alias for /secdevai help
/secdevai-tool                 # Alias for /secdevai tool
```

### Advanced Options

```
/secdevai tool bandit          # Use specific tool (bandit, scorecard, all)
/secdevai git-commit           # Commit approved fixes (requires git config and approved fixes)
/secdevai export json          # Export report (json, markdown, sarif)
```

## Workflow

1. **Initialize**: Run `secdevai` in your project
2. **Review**: Use `/secdevai review` in your AI assistant
3. **Review Findings**: AI presents prioritized security findings
4. **Remediate**: Review suggested fixes and approve if needed
5. **Commit** (optional): Use `/secdevai git-commit` to commit approved fixes (requires git configuration)
6. **Export**: Optionally export reports for documentation

## Results Storage

SecDevAI automatically saves security review results to help you track findings over time.

### Default Location

Results are stored in the `secdevai-results` directory by default (created in your project root). Each review creates a timestamped subdirectory:

```
secdevai-results/
└── secdevai-20240101_120000/
    ├── secdevai-review-20240101_120000.md
    └── secdevai-review-20240101_120000.sarif
```

### Result Files

Each review generates two files:
- **Markdown report** (`.md`): Human-readable security findings report
- **SARIF report** (`.sarif`): Standardized format for integration with security tools and CI/CD pipelines

### Customizing Results Directory

When exporting results, you can specify a custom directory. The exporter will prompt you to confirm the directory location (defaults to `secdevai-results` if not specified).

**Note**: The `secdevai-results` directory is typically added to `.gitignore` to avoid committing review results to version control.

## Configuration

### Ignoring Files

Edit `.secdevaiignore` to exclude files from security scans:

```
# Dependencies
node_modules/
venv/

# Build artifacts
dist/
build/
```

## Examples

### Show Help

```
/secdevai
# or
/secdevai help
```

### Full Codebase Scan

```
/secdevai review
```

### Review Specific File

```
/secdevai review @ src/api/auth.py
```

### Review Selected Code

When you have code selected in the editor, `/secdevai review` will automatically review only the selected code instead of the full codebase.

### Review Last Commit

```
/secdevai review last-commit
```

### Review Multiple Commits

```
/secdevai review last-commit --number 5
```

### Apply Fixes

Apply suggested fixes with approval:

```
/secdevai fix
```

Apply fixes filtered by severity:

```
/secdevai fix severity high
```

Available severity levels: `critical`, `high`, `medium`, `low`

### Review with Tool Integration

```
/secdevai tool bandit
```

### Export Report

Export security review results to various formats:

```
/secdevai export json          # Export as JSON
/secdevai export markdown      # Export as Markdown
/secdevai export sarif         # Export as SARIF
```

Results are saved to the `secdevai-results` directory by default, organized in timestamped subdirectories. You can also use the CLI to export results:

```bash
secdevai export results.json --output-dir custom-results
```

This creates both Markdown and SARIF files in the specified directory (or prompts for confirmation if not specified).

### Commit Approved Fixes

After applying and approving fixes, commit them to git:

```
/secdevai git-commit
```

**Note**: This command only works if:
- There are approved fixes that have been applied
- Git is configured (repository exists and user config is set)

## Tips

- Use `/secdevai`, `/secdevai help`, or `/secdevai-help` to see all available commands
- Use `/secdevai review` for code reviews (full codebase scans by default)
- Use `review @ file` to focus on specific files
- Select code in the editor to automatically review only the selection
- Use `review last-commit` to review recent git commits
- Use `fix severity high` to focus on critical/high severity fixes first
- Use tool integration for enhanced analysis
- Review findings before applying fixes
- Export reports for tracking security improvements

## Extending SecDevAI

SecDevAI's security contexts and skills live in the `lola-module/` directory and follow the [Lola](https://github.com/RedHatProductSecurity/lola) AI Context Module pattern. Each skill uses a `SKILL.md` following the [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) pattern.

> **Contributing**: We encourage you to contribute improvements and new contexts back to the project. See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

### Adding Custom Security Rules

Add or update security patterns in `lola-module/skills/secdevai-review/context/security-review.context`:

```markdown
## Custom Pattern

**Pattern to detect**: [Description]

**Python Example**:
```python
# BAD
[example]

# GOOD
[example]
```
```

### Adding New Tools

Add a new row to the **Available Tools** table in `lola-module/skills/secdevai-tool/SKILL.md` and a corresponding run example in Step 2. No changes to `scripts/container-run.sh` are needed — it is a generic wrapper.

```markdown
| custom-tool | https://github.com/org/custom-tool | `ghcr.io/org/custom-tool:latest` | Python |
```

```bash
# Step 2 example
scripts/container-run.sh ghcr.io/org/custom-tool:latest --format json /src
```

### Customizing Output Format

Modify the output format in `lola-module/skills/secdevai-review/context/security-review.context` under the "Output Format" section.

### Adding Programming Language Support

SecDevAI and AI development tools can support multiple programming languages, even if specific examples for a particular language are not provided. However, supplying language-specific examples will improve the quality of code reviews for those languages, as shown below:

1. Add language-specific patterns to `lola-module/skills/secdevai-review/context/security-review.context`
2. Update tool integration script in `lola-module/skills/secdevai-tool/scripts/` for language-specific tools
3. Add language detection logic