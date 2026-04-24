---
name: secdevai-fix
description: Apply suggested security fixes from a prior review. Use when the user wants to remediate security findings with before/after code diffs, severity filtering, and explicit approval before modifying code.
---

# SecDevAI Fix Command

## Description
Apply suggested security fixes from a prior review. Invoked via `/secdevai fix` or the `/secdevai-fix` alias.

## Usage
```
/secdevai fix                  # Apply all suggested fixes (with approval)
/secdevai fix severity high    # Apply fixes filtered by severity (critical, high, medium, low)
/secdevai-fix                  # Alias: same as /secdevai fix
/secdevai-fix severity high    # Alias: same as /secdevai fix severity high
```

## Expected Response

When this skill is invoked, follow these steps in order:

### Step 1: Check Prerequisites

- Verify there are findings from a prior `/secdevai review` or `/secdevai-review`
- If no prior review exists, inform the user and suggest running a review first

### Step 2: Apply Severity Filter (if specified)

- If `severity [level]` specified: Filter fixes to only that severity (critical, high, medium, low)
- If no filter: Show all available fixes

### Step 3: Present Fixes

For each fix, show:
- **Before/After code** with clear diff
- **Security implications** of the change
- **Severity level** of the finding being fixed
- **OWASP category** reference

```
## 🔧 **Suggested Fix #1** (Critical)

**Finding**: SQL Injection in `app.py:42`
**OWASP Category**: A03: Injection

**Before**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

**After**:
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

**Security Impact**: Eliminates SQL injection vulnerability by using parameterized queries.
```

### Step 4: Preview and Approval

- **Always show preview before changes**
- **Require explicit user approval** before modifying any code
- **Never modify code without approval**
- Create backups before applying fixes

### Step 5: Apply Fixes

After user approves:
- Apply the approved code changes
- Report which fixes were applied and which were skipped

### Step 6: Save Results

After applying fixes, collect information about applied fixes and export:

```python
import importlib.util
from pathlib import Path

# Load the exporter from secdevai-export skill scripts
script_path = Path("secdevai-export/scripts/results_exporter.py")
spec = importlib.util.spec_from_file_location("results_exporter", script_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Collect fix results into data structure
data = {
    "metadata": {
        "tool": "secdevai-fix",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "analyzer": "AI Security Fix",
    },
    "summary": {
        "total_fixes": [count],
        "applied": [count],
        "skipped": [count],
    },
    "fixes": [list of applied fix objects],
}

# Export to markdown and SARIF
markdown_path, sarif_path = mod.export_results(data, command_type="fix")
```

- The exporter will prompt the user to confirm the result directory (default: `secdevai-results`)
- Results are saved with timestamp: `secdevai-fix-YYYYMMDD_HHMMSS.md` and `.sarif`

## Important Notes

- **Always shows preview before changes and requires explicit approval**
- **Never modify code without explicit approval**
- **Create backups before applying fixes**
- After applying fixes, user can run `/secdevai git-commit` to commit the changes
