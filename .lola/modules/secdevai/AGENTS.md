# AGENTS.md

Guidelines for AI assistants (Claude, Cursor, Gemini, etc.) when working on this project.

## Project Summary

SecDevAI is an AI-powered security code review tool that integrates with Cursor, Claude Code, and Gemini CLI. It deploys a Lola AI Context Module containing security skills and security context such as OWASP/WSTG patterns into project directories, enabling slash-command-driven security analysis from within AI coding assistants.

## Commands

```bash
# Install for development
uv pip install -e ".[dev]"

# Run all tests
python -m pytest

# Run a single test class
python -m pytest tests/test_module_deployer.py::TestDetectPlatforms

# Run a single test
python -m pytest tests/test_cli.py::TestInitCommand::test_init_copies_lola_module -v

# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Install CLI tool locally for manual testing
uv tool install --no-cache .
secdevai --help
```

## Architecture

### Two-layer design

1. **CLI (`src/secdevai_cli/__init__.py`)** -- A Typer app with a single `init` command. The `ModuleDeployer` class copies the entire `lola-module/` tree into platform-specific directories (`.cursor/`, `.claude/`, `.gemini/`) in a target project. For Gemini CLI, `.md` files under `commands/` are converted to `.toml` format. Shell scripts get `+x` permissions.

2. **Lola Module (`lola-module/skills/`)** -- The actual security content delivered to projects. Each skill has a `SKILL.md` following the [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) pattern. The module follows the [Lola](https://github.com/RedHatProductSecurity/lola) pattern for cross-assistant distribution.

### Skill dispatch

`/secdevai` dispatches to sub-skills (expandable):
- `secdevai-review` -- Security review using OWASP Top 10 and WSTG patterns (context files in `context/`)
- `secdevai-fix` -- Apply fixes with explicit user approval
- `secdevai-tool` -- Run external tools
- `secdevai-oci-image-security` -- Scan OCI/container images for CVEs and misconfigurations
- `secdevai-export` -- Export findings to Markdown/SARIF via `scripts/results_exporter.py`
- `secdevai-help` -- Show available commands

### Module location at runtime

The CLI finds `lola-module/` via hatchling shared-data: `{sysconfig.get_path("data")}/share/secdevai/lola-module`. This works across `uv run`, `uv tool install`, `uvx`, and `pip install`.

### Platform detection

`ModuleDeployer.detect_platforms()` checks for `.cursor/`, `.claude/`, `.gemini/` directories in the target. If none exist, defaults to `["cursor", "claude"]`.

## Testing

Tests use `pytest` with `typer.testing.CliRunner`. The `conftest.py` provides three fixtures:
- `lola_module_dir` -- real `lola-module/` from project root (integration tests skip if absent)
- `fake_lola_module` -- minimal in-memory structure for isolated unit tests
- `target_project` -- temp directory simulating a user project

The CLI's `_find_module_dir` is patched in most tests since sysconfig paths differ in test environments.

Since `init` is the only `@app.command()`, Typer auto-delegates: invoke as `runner.invoke(app, [project_path])` not `["init", project_path]`.

## Code Style

- Python 3.11+, ruff with line-length 100, rules: E, F, I, N, W
- Bash scripts: `set -euo pipefail`, portable across macOS/Linux
- Skill files: `SKILL.md` (uppercase), commands/scripts: `kebab-case`
- Security patterns in context files use Python examples; AI adapts to the reviewed language at runtime
