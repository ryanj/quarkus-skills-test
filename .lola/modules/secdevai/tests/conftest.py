"""Shared fixtures for SecDevAI CLI tests."""

from pathlib import Path

import pytest


@pytest.fixture
def lola_module_dir() -> Path:
    """Return the real lola-module directory from the project root."""
    return Path(__file__).parent.parent / "lola-module"


@pytest.fixture
def fake_lola_module(tmp_path: Path) -> Path:
    """Create a minimal fake lola-module directory for isolated tests.

    Mirrors the real lola-module/ structure:
      skills/secdevai/SKILL.md
      skills/secdevai-export/SKILL.md
      skills/secdevai-export/scripts/results_exporter.py
      skills/secdevai-tool/scripts/container-run.sh
      skills/secdevai-tool/SKILL.md
      skills/secdevai-review/SKILL.md
    """
    module_dir = tmp_path / "lola-module"
    module_dir.mkdir()

    # skills/secdevai/SKILL.md
    skill_dir = module_dir / "skills" / "secdevai"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Fake SKILL\n")

    # skills/secdevai-export/SKILL.md + scripts/results_exporter.py
    export_dir = module_dir / "skills" / "secdevai-export"
    export_dir.mkdir(parents=True)
    (export_dir / "SKILL.md").write_text("# Export SKILL\n")
    export_scripts = export_dir / "scripts"
    export_scripts.mkdir()
    (export_scripts / "results_exporter.py").write_text("# stub exporter\n")

    # skills/secdevai-tool/SKILL.md + scripts/container-run.sh
    tool_dir = module_dir / "skills" / "secdevai-tool"
    tool_dir.mkdir(parents=True)
    (tool_dir / "SKILL.md").write_text("# Tool SKILL\n")
    script_dir = tool_dir / "scripts"
    script_dir.mkdir()
    (script_dir / "container-run.sh").write_text("#!/bin/bash\necho 'stub'\n")

    # skills/secdevai-review/SKILL.md
    review_dir = module_dir / "skills" / "secdevai-review"
    review_dir.mkdir(parents=True)
    (review_dir / "SKILL.md").write_text("# Review SKILL\n")

    return module_dir


@pytest.fixture
def target_project(tmp_path: Path) -> Path:
    """Create a temporary target project directory."""
    project = tmp_path / "my-project"
    project.mkdir()
    return project
