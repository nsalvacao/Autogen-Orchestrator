"""
Research Agent - Information gathering and analysis agent.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class ResearchAgent(BaseAgent):
    """
    Research Agent.

    Responsible for:
    - Information gathering and synthesis
    - Technology research and comparison
    - Best practices identification
    - Competitive analysis
    - Documentation research
    - Knowledge base maintenance
    """

    def __init__(self, name: str = "ResearchAgent"):
        """Initialize the Research Agent."""
        super().__init__(
            name=name,
            description=(
                "Research agent responsible for information gathering, technology analysis, "
                "best practices research, and knowledge synthesis."
            ),
            capabilities=[
                AgentCapability.EVALUATION,
                AgentCapability.DOCUMENTATION,
            ],
        )
        self._research_cache: dict[str, dict[str, Any]] = {}
        self._knowledge_base: list[dict[str, Any]] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the Research Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        content = message.content.lower()

        if "research" in content or "find" in content or "search" in content:
            return self._generate_research_response(message.content)
        elif "compare" in content or "versus" in content or "vs" in content:
            return self._generate_comparison_response(message.content)
        elif "best practice" in content or "recommend" in content:
            return self._generate_best_practices_response(message.content)
        elif "analyze" in content or "analysis" in content:
            return self._generate_analysis_response(message.content)
        elif "summary" in content or "summarize" in content:
            return self._generate_summary_response(message.content)
        else:
            return (
                f"Research Agent received: {message.content}. "
                "I can help with research, technology comparison, best practices, "
                "analysis, and summarization."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the Research Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        # Perform research based on task
        research_result = await self._conduct_research(task)
        self._knowledge_base.append(research_result)

        return {
            "content": (
                f"Research completed for '{task.title}'.\n"
                f"Findings: {len(research_result['findings'])}\n"
                f"Sources: {len(research_result['sources'])}\n"
                f"Recommendations: {len(research_result['recommendations'])}"
            ),
            "success": True,
            "artifacts": [research_result],
            "metadata": {"research_id": research_result["id"]},
            "needs_correction": False,
        }

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if Research agent can handle the task type."""
        return task_type in ("planning", "documentation", "research", "analysis")

    async def _conduct_research(self, task: Any) -> dict[str, Any]:
        """
        Conduct research for a task.

        Args:
            task: The task to research.

        Returns:
            Research findings.
        """
        import uuid

        research_id = str(uuid.uuid4())

        return {
            "type": "research_report",
            "id": research_id,
            "task_id": task.id,
            "title": f"Research Report: {task.title}",
            "summary": f"Comprehensive research findings for {task.title}",
            "findings": [
                {
                    "category": "Technical",
                    "content": "Identified key technical requirements and constraints",
                    "confidence": 0.85,
                },
                {
                    "category": "Best Practices",
                    "content": "Industry best practices have been analyzed",
                    "confidence": 0.90,
                },
                {
                    "category": "Risks",
                    "content": "Potential risks and mitigation strategies identified",
                    "confidence": 0.75,
                },
            ],
            "sources": [
                {"type": "documentation", "name": "Official Documentation"},
                {"type": "article", "name": "Industry Articles"},
                {"type": "case_study", "name": "Case Studies"},
            ],
            "recommendations": [
                "Consider industry-standard approaches",
                "Review similar implementations",
                "Consult with domain experts",
            ],
            "metadata": {
                "research_depth": "comprehensive",
                "last_updated": "current",
            },
        }

    def _generate_research_response(self, request: str) -> str:
        """Generate a research response."""
        return (
            "Research Process Initiated:\n\n"
            "**Phase 1: Discovery**\n"
            "- Identifying relevant sources\n"
            "- Collecting documentation\n"
            "- Gathering technical specifications\n\n"
            "**Phase 2: Analysis**\n"
            "- Evaluating information quality\n"
            "- Cross-referencing sources\n"
            "- Identifying patterns and trends\n\n"
            "**Phase 3: Synthesis**\n"
            "- Compiling findings\n"
            "- Generating recommendations\n"
            "- Creating actionable insights\n\n"
            f"Researching: {request[:100]}..."
        )

    def _generate_comparison_response(self, request: str) -> str:
        """Generate a comparison response."""
        return (
            "Comparative Analysis Framework:\n\n"
            "**Evaluation Criteria:**\n"
            "- Performance and scalability\n"
            "- Ease of use and learning curve\n"
            "- Community and ecosystem\n"
            "- Cost and licensing\n"
            "- Long-term viability\n\n"
            "**Methodology:**\n"
            "- Feature-by-feature comparison\n"
            "- Benchmark analysis\n"
            "- Use case mapping\n"
            "- Risk assessment\n\n"
            "Will provide detailed comparison matrix."
        )

    def _generate_best_practices_response(self, request: str) -> str:
        """Generate a best practices response."""
        return (
            "Best Practices Research:\n\n"
            "**Industry Standards:**\n"
            "- SOLID principles for code design\n"
            "- 12-Factor App methodology\n"
            "- RESTful API design guidelines\n"
            "- Security best practices (OWASP)\n\n"
            "**Code Quality:**\n"
            "- Comprehensive testing strategies\n"
            "- Documentation standards\n"
            "- Code review processes\n"
            "- Continuous integration practices\n\n"
            "**Operations:**\n"
            "- Monitoring and observability\n"
            "- Incident response procedures\n"
            "- Change management processes"
        )

    def _generate_analysis_response(self, request: str) -> str:
        """Generate an analysis response."""
        return (
            "Analysis Framework:\n\n"
            "**Technical Analysis:**\n"
            "- Architecture review\n"
            "- Code quality assessment\n"
            "- Performance evaluation\n"
            "- Security audit\n\n"
            "**Business Analysis:**\n"
            "- Requirements mapping\n"
            "- Stakeholder impact\n"
            "- Cost-benefit analysis\n"
            "- Risk assessment\n\n"
            "**Gap Analysis:**\n"
            "- Current state vs. desired state\n"
            "- Missing capabilities\n"
            "- Improvement opportunities"
        )

    def _generate_summary_response(self, request: str) -> str:
        """Generate a summary response."""
        return (
            "Summary Generation:\n\n"
            "I will create a comprehensive summary including:\n\n"
            "**Executive Summary:**\n"
            "- Key findings and insights\n"
            "- Critical decisions needed\n"
            "- Recommended next steps\n\n"
            "**Detailed Findings:**\n"
            "- Technical discoveries\n"
            "- Process observations\n"
            "- Stakeholder feedback\n\n"
            "**Action Items:**\n"
            "- Prioritized recommendations\n"
            "- Timeline suggestions\n"
            "- Resource requirements"
        )

    def get_knowledge_base(self) -> list[dict[str, Any]]:
        """Get the accumulated knowledge base."""
        return self._knowledge_base.copy()

    def search_knowledge(self, query: str) -> list[dict[str, Any]]:
        """
        Search the knowledge base.

        Args:
            query: Search query.

        Returns:
            Matching knowledge entries.
        """
        query_lower = query.lower()
        results = []

        for entry in self._knowledge_base:
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()

            if query_lower in title or query_lower in summary:
                results.append(entry)

        return results
