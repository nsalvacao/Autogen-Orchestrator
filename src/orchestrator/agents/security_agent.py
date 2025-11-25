"""
Security Agent - Security analysis agent for vulnerability detection.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class SecurityAgent(BaseAgent):
    """
    Security Agent.

    Responsible for:
    - Security analysis and review
    - Vulnerability detection
    - Security best practices enforcement
    - Compliance checking
    - Threat modeling
    """

    def __init__(self, name: str = "SecurityAgent", enable_autogen: bool = False):
        """Initialize the Security Agent."""
        system_message = (
            "You are a security expert with deep knowledge of cybersecurity, "
            "vulnerability assessment, and secure coding practices. You excel at "
            "identifying security risks, conducting threat modeling, and ensuring compliance."
        )
        super().__init__(
            name=name,
            description=(
                "Security agent responsible for security analysis, "
                "vulnerability detection, and security best practices enforcement."
            ),
            capabilities=[
                AgentCapability.SECURITY_ANALYSIS,
                AgentCapability.CODE_REVIEW,
                AgentCapability.EVALUATION,
            ],
            enable_autogen=enable_autogen,
            system_message=system_message,
        )
        self._security_findings: list[dict[str, Any]] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the Security Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        if self.is_autogen_enabled:
            return await self._generate_autogen_response(message.content)
        
        content = message.content.lower()

        if "vulnerability" in content or "scan" in content:
            return self._generate_scan_response(message.content)
        elif "review" in content or "analyze" in content:
            return self._generate_review_response(message.content)
        elif "compliance" in content:
            return self._generate_compliance_response(message.content)
        elif "threat" in content:
            return self._generate_threat_model_response(message.content)
        else:
            return (
                f"Security Agent received: {message.content}. "
                "I can help with security scans, reviews, compliance checks, and threat modeling."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the Security Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        if self.is_autogen_enabled:
            return await self._handle_task_with_autogen(task)
        
        task_type = getattr(task, "task_type", None)
        task_type_value = task_type.value if task_type else "unknown"

        if task_type_value == "security_review":
            return await self._handle_security_review(task)
        else:
            # Security can review any task for security implications
            return await self._perform_security_scan(task)

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if Security can handle the task type."""
        return task_type in ("security_review", "code_review", "evaluation")

    async def _handle_security_review(self, task: Any) -> dict[str, Any]:
        """Handle a security review task."""
        findings = self._analyze_security(task)
        self._security_findings.extend(findings)

        has_critical = any(f.get("severity") == "critical" for f in findings)
        needs_correction = has_critical

        return {
            "content": (
                f"Security review completed for '{task.title}'. "
                f"Found {len(findings)} potential issues."
            ),
            "success": not has_critical,
            "artifacts": [{"type": "security_findings", "data": findings}],
            "needs_correction": needs_correction,
            "correction_reason": "Critical security issues found" if needs_correction else None,
        }

    async def _perform_security_scan(self, task: Any) -> dict[str, Any]:
        """Perform a security scan on task output."""
        findings = self._analyze_security(task)

        return {
            "content": f"Security scan completed for '{task.title}'",
            "success": True,
            "artifacts": [{"type": "security_scan", "data": findings}],
            "needs_correction": False,
        }

    def _analyze_security(self, task: Any) -> list[dict[str, Any]]:
        """
        Analyze security aspects of a task.

        Placeholder implementation - in production, this would use
        actual security analysis tools.
        """
        # Return placeholder findings
        return [
            {
                "type": "info",
                "severity": "info",
                "title": "Security scan initiated",
                "description": f"Scanning '{task.title}' for security issues",
                "recommendation": "Review findings and apply recommended fixes",
            }
        ]

    def _generate_scan_response(self, request: str) -> str:
        """Generate a vulnerability scan response."""
        return (
            "Security Scan Results:\n"
            "Scanning for:\n"
            "- SQL Injection vulnerabilities\n"
            "- Cross-Site Scripting (XSS)\n"
            "- Authentication weaknesses\n"
            "- Sensitive data exposure\n"
            "- Dependency vulnerabilities"
        )

    def _generate_review_response(self, request: str) -> str:
        """Generate a security review response."""
        return (
            "Security Review Checklist:\n"
            "- [ ] Input validation\n"
            "- [ ] Output encoding\n"
            "- [ ] Authentication & Authorization\n"
            "- [ ] Data encryption\n"
            "- [ ] Error handling\n"
            "- [ ] Logging practices"
        )

    def _generate_compliance_response(self, request: str) -> str:
        """Generate a compliance check response."""
        return (
            "Compliance Check:\n"
            "- OWASP Top 10: Checking...\n"
            "- GDPR requirements: Evaluating...\n"
            "- Industry standards: Verifying...\n"
            "- Internal policies: Validating..."
        )

    def _generate_threat_model_response(self, request: str) -> str:
        """Generate a threat model response."""
        return (
            "Threat Model Analysis:\n"
            "1. Asset identification\n"
            "2. Threat enumeration (STRIDE)\n"
            "3. Attack vector analysis\n"
            "4. Risk assessment\n"
            "5. Mitigation recommendations"
        )
    
    async def _handle_task_with_autogen(self, task: Any) -> dict[str, Any]:
        """Handle a task using AutoGen LLM for intelligent security analysis."""
        task_prompt = (
            f"As a security expert, analyze the following task for security implications:\n\n"
            f"Task: {task.title}\n"
            f"Description: {task.description}\n"
            f"Type: {getattr(task, 'task_type', 'unknown')}\n\n"
            "Please provide:\n"
            "1. Security risks and vulnerabilities\n"
            "2. Threat modeling considerations\n"
            "3. Recommended security controls\n"
            "4. Compliance considerations"
        )
        response = await self._generate_autogen_response(task_prompt)
        return {"content": response, "success": True, "artifacts": [], "needs_correction": False}
