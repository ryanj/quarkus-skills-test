---
name: secdevai-export
description: Export security review results to Markdown and SARIF report formats. Use when the user wants to save, export, or generate reports from security review findings produced by /secdevai review, /secdevai fix, or /secdevai tool.
---

# SecDevAI Export Command (Alias)

## Description
Alias for `/secdevai export` - Export security review results to Markdown and SARIF formats.

## Usage
```
/secdevai-export json           # Export from a JSON results file
/secdevai export json           # Same via main command
```

## What This Command Does
This is an alias for `/secdevai export`. See the main `/secdevai` command documentation for full details.

When invoked, this command:
- Converts structured security findings into a Markdown report and SARIF file
- Prompts the user to confirm the result directory (default: `secdevai-results`, or `$SECDEVAI_RESULTS_DIR` if set)
- Saves timestamped files: `secdevai-<type>-YYYYMMDD_HHMMSS.md` and `.sarif`

## Script

The export logic lives in `scripts/results_exporter.py` within this skill directory. It provides:

- `export_results(data, result_dir, command_type)` - Main entry point
- `convert_to_markdown(data)` - Convert findings to Markdown
- `convert_to_sarif(data)` - Convert findings to SARIF 2.1.0

### Usage from AI skills

```python
from pathlib import Path
import importlib.util

# Load the exporter from the deployed skill scripts
script_path = Path("secdevai-export/scripts/results_exporter.py")
spec = importlib.util.spec_from_file_location("results_exporter", script_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Export to markdown and SARIF
markdown_path, sarif_path = mod.export_results(data, command_type="review")
```

### Data format

The `data` dictionary should follow this structure:

```json
{
  "metadata": {
    "tool": "secdevai-ai-analysis",
    "version": "1.0.0",
    "timestamp": "ISO 8601 timestamp",
    "target_file": "file path or 'codebase'",
    "analyzer": "AI Security Review"
  },
  "summary": {
    "total_findings": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  },
  "findings": [],
  "affected_endpoints": [],
  "recommendations": {
    "immediate_actions": [],
    "long_term_improvements": []
  }
}
```

## Expected Response
See `/secdevai` command documentation. This alias executes `/secdevai export` with the same behavior.

**Important**:
- The exporter prompts the user to confirm the result directory (default: `secdevai-results`)
- Set `SECDEVAI_RESULTS_DIR` in your shell profile to use a custom base directory without retyping it each run — the prompt will show your value as the default. This env var is shared by all secdevai commands (`review`, `fix`, `tool`, `dast`).
- Results are saved with timestamp: `secdevai-<type>-YYYYMMDD_HHMMSS.md` and `.sarif`
- SARIF output conforms to SARIF v2.1.0 schema for integration with GitHub Code Scanning, VS Code SARIF Viewer, etc.
