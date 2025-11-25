"""
Platform - Cross-OS platform detection and utilities.

This module provides platform detection and cross-OS utilities
to ensure the orchestrator works correctly on Linux, WSL, and Windows.
"""

import os
import platform
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OSType(str, Enum):
    """Operating system types."""

    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    WSL = "wsl"
    UNKNOWN = "unknown"


class Architecture(str, Enum):
    """CPU architectures."""

    X86_64 = "x86_64"
    ARM64 = "arm64"
    X86 = "x86"
    UNKNOWN = "unknown"


@dataclass
class PlatformInfo:
    """Information about the current platform."""

    os_type: OSType
    os_name: str
    os_version: str
    architecture: Architecture
    python_version: str
    is_wsl: bool
    is_container: bool
    home_dir: Path
    temp_dir: Path

    def is_linux_based(self) -> bool:
        """Check if running on Linux or WSL."""
        return self.os_type in (OSType.LINUX, OSType.WSL)

    def is_unix_like(self) -> bool:
        """Check if running on a Unix-like system."""
        return self.os_type in (OSType.LINUX, OSType.WSL, OSType.MACOS)


def _detect_wsl() -> bool:
    """Detect if running in Windows Subsystem for Linux."""
    # Check common WSL indicators
    if os.path.exists("/proc/version"):
        try:
            with open("/proc/version") as f:
                version_info = f.read().lower()
                if "microsoft" in version_info or "wsl" in version_info:
                    return True
        except OSError:
            pass

    # Check for WSL environment variable
    if "WSL_DISTRO_NAME" in os.environ:
        return True

    # Check for WSL interop
    if os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"):
        return True

    return False


def _detect_container() -> bool:
    """Detect if running in a container."""
    # Check for Docker
    if os.path.exists("/.dockerenv"):
        return True

    # Check cgroup for container indicators
    if os.path.exists("/proc/1/cgroup"):
        try:
            with open("/proc/1/cgroup") as f:
                cgroup_content = f.read()
                if "docker" in cgroup_content or "kubepods" in cgroup_content:
                    return True
        except OSError:
            pass

    # Check for Kubernetes
    if "KUBERNETES_SERVICE_HOST" in os.environ:
        return True

    return False


def _get_os_type() -> OSType:
    """Determine the current OS type."""
    system = platform.system().lower()

    if system == "linux":
        if _detect_wsl():
            return OSType.WSL
        return OSType.LINUX
    elif system == "windows":
        return OSType.WINDOWS
    elif system == "darwin":
        return OSType.MACOS
    else:
        return OSType.UNKNOWN


def _get_architecture() -> Architecture:
    """Determine the CPU architecture."""
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        return Architecture.X86_64
    elif machine in ("arm64", "aarch64"):
        return Architecture.ARM64
    elif machine in ("i386", "i686", "x86"):
        return Architecture.X86
    else:
        return Architecture.UNKNOWN


def get_platform_info() -> PlatformInfo:
    """
    Get information about the current platform.

    Returns:
        PlatformInfo with details about the current system.
    """
    os_type = _get_os_type()

    return PlatformInfo(
        os_type=os_type,
        os_name=platform.system(),
        os_version=platform.version(),
        architecture=_get_architecture(),
        python_version=sys.version,
        is_wsl=os_type == OSType.WSL,
        is_container=_detect_container(),
        home_dir=Path.home(),
        temp_dir=Path(tempfile.gettempdir()),
    )


def get_path_separator() -> str:
    """Get the appropriate path separator for the current OS."""
    return os.sep


def normalize_path(path: str) -> str:
    """
    Normalize a path for the current OS.

    Args:
        path: The path to normalize.

    Returns:
        Normalized path string.
    """
    return str(Path(path).resolve())


def is_executable(path: str) -> bool:
    """
    Check if a file is executable.

    Args:
        path: Path to the file.

    Returns:
        True if the file is executable.
    """
    return os.path.isfile(path) and os.access(path, os.X_OK)


def find_executable(name: str) -> str | None:
    """
    Find an executable in the system PATH.

    Args:
        name: Name of the executable.

    Returns:
        Full path to the executable, or None if not found.
    """
    path_env = os.environ.get("PATH", "")
    paths = path_env.split(os.pathsep)

    for path in paths:
        full_path = os.path.join(path, name)
        if is_executable(full_path):
            return full_path

        # On Windows, try with common extensions
        if platform.system() == "Windows":
            for ext in (".exe", ".cmd", ".bat", ".ps1"):
                ext_path = full_path + ext
                if is_executable(ext_path):
                    return ext_path

    return None


def ensure_directory(path: str | Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory.

    Returns:
        Path object for the directory.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
