"""Integration tests for the secdevai CLI (typer app).

Note: Since ``init`` is the only @app.command(), Typer auto-delegates to
it without requiring the subcommand name.  The runner is invoked as
``runner.invoke(app, [project_path])`` – *not* ``["init", project_path]``.
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from secdevai_cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# init command – happy paths
# ---------------------------------------------------------------------------


class TestInitCommand:
    """Test `secdevai init`."""

    def test_init_copies_lola_module(self, tmp_path, lola_module_dir):
        """Core test: init copies ALL lola-module files into platform dirs."""
        if not lola_module_dir.exists():
            pytest.skip("lola-module not found (not running from source)")

        project = tmp_path / "project"
        project.mkdir()

        with patch("secdevai_cli._find_module_dir", return_value=lola_module_dir):
            result = runner.invoke(app, [str(project)])

        assert result.exit_code == 0, result.output
        assert "initialized successfully" in result.output

        # Default platforms: .cursor and .claude
        for platform in ("cursor", "claude"):
            platform_dir = project / f".{platform}"
            assert platform_dir.is_dir(), f".{platform}/ should be created"

            source_files = sorted(
                str(f.relative_to(lola_module_dir))
                for f in lola_module_dir.rglob("*")
                if f.is_file()
            )
            deployed_files = sorted(
                str(f.relative_to(platform_dir))
                for f in platform_dir.rglob("*")
                if f.is_file()
            )
            assert deployed_files == source_files, (
                f"Files in .{platform}/ don't match lola-module/"
            )

    def test_init_default_path_is_cwd(self, tmp_path, monkeypatch, lola_module_dir):
        """Running `secdevai` without args should init in cwd."""
        if not lola_module_dir.exists():
            pytest.skip("lola-module not found")

        monkeypatch.chdir(tmp_path)
        with patch("secdevai_cli._find_module_dir", return_value=lola_module_dir):
            result = runner.invoke(app, [])

        assert result.exit_code == 0, result.output
        assert "initialized successfully" in result.output

    def test_init_with_existing_platform_dirs(self, tmp_path, lola_module_dir):
        """If .gemini/ exists, it should be detected and populated."""
        if not lola_module_dir.exists():
            pytest.skip("lola-module not found")

        project = tmp_path / "project"
        project.mkdir()
        (project / ".gemini").mkdir()

        with patch("secdevai_cli._find_module_dir", return_value=lola_module_dir):
            result = runner.invoke(app, [str(project)])

        assert result.exit_code == 0, result.output
        assert (project / ".gemini").is_dir()
        # Gemini should have at least some files
        assert any((project / ".gemini").rglob("*"))

    def test_init_file_contents_match_source(self, tmp_path, lola_module_dir):
        """Every deployed file must be byte-identical to its source."""
        if not lola_module_dir.exists():
            pytest.skip("lola-module not found")

        project = tmp_path / "project"
        project.mkdir()

        with patch("secdevai_cli._find_module_dir", return_value=lola_module_dir):
            result = runner.invoke(app, [str(project)])

        assert result.exit_code == 0, result.output

        for src in lola_module_dir.rglob("*"):
            if not src.is_file():
                continue
            rel = src.relative_to(lola_module_dir)
            deployed = project / ".cursor" / rel
            assert deployed.exists(), f"Missing: {rel}"
            assert deployed.read_bytes() == src.read_bytes(), f"Content mismatch: {rel}"


# ---------------------------------------------------------------------------
# init command – error handling
# ---------------------------------------------------------------------------


class TestInitErrors:
    """Error-path tests for init command."""

    def test_init_nonexistent_directory(self):
        result = runner.invoke(app, ["/nonexistent/path/abc123"])
        assert result.exit_code == 1
        assert "does not exist" in result.output

    def test_init_module_not_found(self, tmp_path):
        """When _find_module_dir returns None, show helpful error."""
        project = tmp_path / "project"
        project.mkdir()

        with patch("secdevai_cli._find_module_dir", return_value=None):
            result = runner.invoke(app, [str(project)])

        assert result.exit_code == 1
        assert "lola-module" in result.output.lower()


# ---------------------------------------------------------------------------
# _find_module_dir
# ---------------------------------------------------------------------------


class TestFindModuleDir:
    """Tests for the _find_module_dir helper."""

    def test_returns_path_when_shared_data_exists(self, tmp_path):
        """When sysconfig data dir has the expected lola-module, return it."""
        from secdevai_cli import _find_module_dir

        fake_data = tmp_path / "data"
        lola = fake_data / "share" / "secdevai" / "lola-module"
        lola.mkdir(parents=True)
        (lola / "SKILL.md").write_text("# test")

        with patch("sysconfig.get_path", return_value=str(fake_data)):
            result = _find_module_dir()

        assert result is not None
        assert result == lola

    def test_returns_none_when_dir_missing(self, tmp_path):
        """When sysconfig data dir does NOT contain lola-module, return None."""
        from secdevai_cli import _find_module_dir

        fake_data = tmp_path / "empty-data"
        fake_data.mkdir()

        with patch("sysconfig.get_path", return_value=str(fake_data)):
            result = _find_module_dir()

        assert result is None

    def test_returns_none_when_sysconfig_returns_none(self):
        """When sysconfig.get_path returns None, return None."""
        from secdevai_cli import _find_module_dir

        with patch("sysconfig.get_path", return_value=None):
            result = _find_module_dir()

        assert result is None
