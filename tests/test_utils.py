"""Tests for the utility modules."""

from orchestrator.utils.config import (
    Config,
    Environment,
    get_default_config_paths,
    load_config,
)
from orchestrator.utils.platform import (
    Architecture,
    OSType,
    ensure_directory,
    get_platform_info,
    normalize_path,
)


class TestPlatformInfo:
    """Tests for platform utilities."""

    def test_get_platform_info(self):
        """Test getting platform information."""
        info = get_platform_info()

        assert info is not None
        assert info.os_type in OSType
        assert info.architecture in Architecture
        assert info.python_version is not None
        assert info.home_dir.exists()

    def test_is_linux_based(self):
        """Test Linux-based OS detection."""
        info = get_platform_info()

        # This will depend on the actual platform
        if info.os_type in (OSType.LINUX, OSType.WSL):
            assert info.is_linux_based() is True
        else:
            assert info.is_linux_based() is False

    def test_is_unix_like(self):
        """Test Unix-like OS detection."""
        info = get_platform_info()

        if info.os_type in (OSType.LINUX, OSType.WSL, OSType.MACOS):
            assert info.is_unix_like() is True
        elif info.os_type == OSType.WINDOWS:
            assert info.is_unix_like() is False

    def test_normalize_path(self):
        """Test path normalization."""
        path = normalize_path("/tmp/../tmp/test")
        assert "test" in path

    def test_ensure_directory(self, tmp_path):
        """Test directory creation."""
        new_dir = tmp_path / "test_dir" / "nested"

        result = ensure_directory(new_dir)

        assert result.exists()
        assert result.is_dir()


class TestConfig:
    """Tests for configuration utilities."""

    def test_default_config(self):
        """Test default configuration."""
        config = Config()

        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is False
        assert config.llm.provider == "NOT_CONFIGURED"

    def test_config_is_production(self):
        """Test production environment check."""
        config = Config()
        assert config.is_production() is False

        config.environment = Environment.PRODUCTION
        assert config.is_production() is True

    def test_config_is_development(self):
        """Test development environment check."""
        config = Config()
        assert config.is_development() is True

        config.environment = Environment.PRODUCTION
        assert config.is_development() is False

    def test_load_config_defaults(self):
        """Test loading config with defaults."""
        config = load_config()

        assert config is not None
        assert config.environment == Environment.DEVELOPMENT

    def test_load_config_from_env(self, monkeypatch):
        """Test loading config from environment variables."""
        monkeypatch.setenv("ORCHESTRATOR_ENV", "production")
        monkeypatch.setenv("ORCHESTRATOR_DEBUG", "true")
        monkeypatch.setenv("ORCHESTRATOR_LLM_PROVIDER", "openai")

        config = load_config()

        assert config.environment == Environment.PRODUCTION
        assert config.debug is True
        assert config.llm.provider == "openai"

    def test_load_config_with_invalid_env(self, monkeypatch):
        """Test loading config with invalid environment value."""
        monkeypatch.setenv("ORCHESTRATOR_ENV", "invalid")

        config = load_config()

        # Should default to development
        assert config.environment == Environment.DEVELOPMENT

    def test_get_default_config_paths(self):
        """Test getting default config paths."""
        paths = get_default_config_paths()

        assert len(paths) > 0
        assert all(hasattr(p, "exists") for p in paths)
