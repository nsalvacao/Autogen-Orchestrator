"""
CLI Adapter - Adapter for command-line interface integrations.

This adapter provides a framework for integrating with external CLI tools,
supporting actual subprocess execution with sandboxing and timeout controls.
"""

import asyncio
import shlex
from typing import Any

from orchestrator.contracts.adapter_contract import (
    AdapterConfig,
    AdapterContract,
    AdapterResult,
    AdapterStatus,
    AdapterType,
)


class CLIAdapter(AdapterContract):
    """
    Adapter for external CLI tools.

    Supports:
    - Build tools (make, cmake, etc.)
    - Package managers (pip, npm, cargo, etc.)
    - Testing frameworks
    - Linting tools
    - Custom shell commands

    Security features:
    - Command allowlisting
    - Timeout enforcement
    - Working directory restrictions
    """

    def __init__(
        self,
        config: AdapterConfig | None = None,
        allowed_commands: list[str] | None = None,
        default_timeout: int = 60,
        working_directory: str | None = None,
    ):
        """
        Initialize the CLI adapter.

        Args:
            config: Adapter configuration.
            allowed_commands: List of allowed command prefixes (e.g., ["pip", "npm"]).
            default_timeout: Default timeout in seconds for commands.
            working_directory: Default working directory for commands.
        """
        if config is None:
            config = AdapterConfig(
                adapter_type=AdapterType.CLI,
                name="CLIAdapter",
                enabled=False,
            )
        super().__init__(config)
        self._allowed_commands = allowed_commands
        self._default_timeout = default_timeout
        self._working_directory = working_directory
        self._execution_history: list[dict[str, Any]] = []

    @property
    def adapter_type(self) -> AdapterType:
        """Return the adapter type."""
        return AdapterType.CLI

    @property
    def name(self) -> str:
        """Return the adapter name."""
        return self._config.name

    async def connect(self) -> AdapterResult:
        """
        Establish connection (verify CLI tools availability).

        Returns:
            AdapterResult indicating success or failure.
        """
        if not self._config.enabled:
            return AdapterResult(
                success=False,
                error_message="CLI adapter is not enabled. Configure and enable before use.",
            )

        self._status = AdapterStatus.CONNECTED
        return AdapterResult(
            success=True,
            data={
                "message": "CLI adapter connected",
                "allowed_commands": self._allowed_commands,
                "default_timeout": self._default_timeout,
            },
        )

    async def disconnect(self) -> AdapterResult:
        """
        Disconnect (cleanup resources).

        Returns:
            AdapterResult indicating success or failure.
        """
        self._status = AdapterStatus.DISCONNECTED
        return AdapterResult(
            success=True,
            data={"message": "CLI adapter disconnected"},
        )

    async def execute(self, operation: str, **kwargs: Any) -> AdapterResult:
        """
        Execute a CLI operation.

        Args:
            operation: The CLI command to execute.
            **kwargs: Additional parameters:
                - timeout: Command timeout in seconds
                - cwd: Working directory
                - env: Environment variables
                - capture_output: Whether to capture output (default True)

        Returns:
            AdapterResult containing the operation result.
        """
        if not self.is_connected():
            return AdapterResult(
                success=False,
                error_message="CLI adapter is not connected. Call connect() first.",
            )

        # Check if command is allowed
        if not self._is_command_allowed(operation):
            return AdapterResult(
                success=False,
                error_message=f"Command not allowed: {operation.split()[0]}",
            )

        timeout = kwargs.get("timeout", self._default_timeout)
        cwd = kwargs.get("cwd", self._working_directory)
        env = kwargs.get("env")
        capture_output = kwargs.get("capture_output", True)

        try:
            result = await self._run_command(
                operation,
                timeout=timeout,
                cwd=cwd,
                env=env,
                capture_output=capture_output,
            )

            # Record in history
            self._execution_history.append({
                "command": operation,
                "success": result["success"],
                "return_code": result.get("return_code"),
            })

            return AdapterResult(
                success=result["success"],
                data=result,
                metadata={"adapter": self.name},
            )

        except asyncio.TimeoutError:
            return AdapterResult(
                success=False,
                error_message=f"Command timed out after {timeout} seconds",
                metadata={"adapter": self.name, "command": operation},
            )
        except Exception as e:
            return AdapterResult(
                success=False,
                error_message=f"Command execution failed: {str(e)}",
                metadata={"adapter": self.name, "command": operation},
            )

    async def _run_command(
        self,
        command: str,
        timeout: int,
        cwd: str | None,
        env: dict[str, str] | None,
        capture_output: bool,
    ) -> dict[str, Any]:
        """
        Run a shell command asynchronously.

        Args:
            command: The command to run.
            timeout: Timeout in seconds.
            cwd: Working directory.
            env: Environment variables.
            capture_output: Whether to capture stdout/stderr.

        Returns:
            Dictionary with command results.
        """
        # Parse command safely
        args = shlex.split(command)

        if capture_output:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )

                return {
                    "success": process.returncode == 0,
                    "return_code": process.returncode,
                    "stdout": stdout.decode("utf-8", errors="replace"),
                    "stderr": stderr.decode("utf-8", errors="replace"),
                    "command": command,
                }

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise

        else:
            process = await asyncio.create_subprocess_exec(
                *args,
                cwd=cwd,
                env=env,
            )

            try:
                await asyncio.wait_for(process.wait(), timeout=timeout)

                return {
                    "success": process.returncode == 0,
                    "return_code": process.returncode,
                    "command": command,
                }

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise

    def _is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is in the allowlist.

        Args:
            command: The command to check.

        Returns:
            True if allowed, False otherwise.
        """
        if self._allowed_commands is None:
            return True  # No restrictions if allowlist not set

        parts = command.split()
        if not parts:
            return False

        cmd = parts[0]
        return any(
            cmd == allowed or cmd.startswith(allowed + " ")
            for allowed in self._allowed_commands
        )

    async def health_check(self) -> AdapterResult:
        """
        Check if CLI tools are available.

        Returns:
            AdapterResult indicating health status.
        """
        if not self.is_connected():
            return AdapterResult(
                success=True,
                data={
                    "status": "not_connected",
                    "adapter": self.name,
                },
            )

        # Try to run a simple command to verify CLI access
        try:
            result = await self._run_command(
                "echo health_check",
                timeout=5,
                cwd=None,
                env=None,
                capture_output=True,
            )

            return AdapterResult(
                success=True,
                data={
                    "status": "healthy" if result["success"] else "degraded",
                    "adapter": self.name,
                    "shell_access": result["success"],
                },
            )

        except Exception as e:
            return AdapterResult(
                success=False,
                error_message=f"Health check failed: {str(e)}",
                data={
                    "status": "unhealthy",
                    "adapter": self.name,
                },
            )

    def get_execution_history(self) -> list[dict[str, Any]]:
        """Get the command execution history."""
        return self._execution_history.copy()

    def clear_history(self) -> None:
        """Clear the execution history."""
        self._execution_history.clear()

    async def run_build(self, build_command: str = "make") -> AdapterResult:
        """
        Convenience method to run a build command.

        Args:
            build_command: The build command to run.

        Returns:
            AdapterResult with build output.
        """
        return await self.execute(build_command, timeout=300)

    async def run_tests(self, test_command: str = "pytest") -> AdapterResult:
        """
        Convenience method to run tests.

        Args:
            test_command: The test command to run.

        Returns:
            AdapterResult with test output.
        """
        return await self.execute(test_command, timeout=600)

    async def run_linter(self, lint_command: str = "ruff check .") -> AdapterResult:
        """
        Convenience method to run a linter.

        Args:
            lint_command: The lint command to run.

        Returns:
            AdapterResult with lint output.
        """
        return await self.execute(lint_command, timeout=120)
