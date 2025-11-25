# Autogen-Orchestrator

A modular AI meta-orchestrator MVP built on AutoGen. Defines agents for PM, Dev, QA, Security, and Docs, enabling dynamic multi-agent conversations, task distribution, evaluation, and correction loops. Linux/WSL-first, extensible with adapters for external CLIs and APIs, designed to evolve into a full AI-assisted software company.

## Features

- **Multi-Agent Architecture**: PM, Dev, QA, Security, and Docs agents with specialized capabilities
- **Dynamic Conversations**: Flexible conversation modes (Sequential, Round-Robin, Dynamic, Broadcast)
- **Task Distribution**: Priority-based task queue with dependency management
- **Correction Loops**: Iterative improvement through evaluation and correction
- **Extensible Adapters**: Placeholder adapters for CLI, API, and VCS integrations
- **Observability**: Built-in logging, metrics collection, and distributed tracing
- **Cross-Platform**: Linux-first with WSL and cross-OS awareness

## Project Structure

```
autogen-orchestrator/
├── src/orchestrator/
│   ├── agents/           # Agent implementations
│   │   ├── base_agent.py # Base agent class
│   │   ├── pm_agent.py   # Project Manager agent
│   │   ├── dev_agent.py  # Developer agent
│   │   ├── qa_agent.py   # QA agent
│   │   ├── security_agent.py  # Security agent
│   │   └── docs_agent.py # Documentation agent
│   ├── contracts/        # Interface definitions
│   │   ├── agent_contract.py    # Agent interface
│   │   ├── adapter_contract.py  # Adapter interface
│   │   └── evaluation_contract.py  # Evaluation interface
│   ├── core/             # Core orchestration logic
│   │   ├── orchestrator.py     # Main orchestrator
│   │   ├── task.py             # Task management
│   │   ├── conversation.py     # Conversation management
│   │   └── correction_loop.py  # Correction loop logic
│   ├── adapters/         # External system adapters
│   │   ├── cli_adapter.py      # CLI integration (placeholder)
│   │   ├── api_adapter.py      # API integration (placeholder)
│   │   └── vcs_adapter.py      # VCS integration (placeholder)
│   ├── observability/    # Monitoring and tracing
│   │   ├── logger.py           # Structured logging
│   │   ├── metrics.py          # Metrics collection
│   │   └── tracer.py           # Distributed tracing
│   └── utils/            # Utilities
│       ├── platform.py         # Cross-OS utilities
│       └── config.py           # Configuration management
├── tests/                # Test suite
├── pyproject.toml        # Project configuration
└── README.md
```

## Installation

### Requirements

- Python 3.10 or higher
- Linux, WSL, or macOS (Windows support planned)

### Install from source

```bash
# Clone the repository
git clone https://github.com/nsalvacao/Autogen-Orchestrator.git
cd Autogen-Orchestrator

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from orchestrator import Orchestrator, Task, TaskPriority
from orchestrator.agents import PMAgent, DevAgent, QAAgent, SecurityAgent, DocsAgent
from orchestrator.core.task import TaskType

async def main():
    # Create the orchestrator
    orchestrator = Orchestrator()

    # Register agents
    orchestrator.register_agent(PMAgent())
    orchestrator.register_agent(DevAgent())
    orchestrator.register_agent(QAAgent())
    orchestrator.register_agent(SecurityAgent())
    orchestrator.register_agent(DocsAgent())

    # Start the orchestrator
    await orchestrator.start()

    # Create and submit a task
    task = Task(
        title="Implement User Authentication",
        description="Create a secure user authentication module",
        task_type=TaskType.DEVELOPMENT,
        priority=TaskPriority.HIGH,
    )

    task_id = await orchestrator.submit_task(task)
    print(f"Task submitted: {task_id}")

    # Process the task
    result = await orchestrator.process_task(task)
    print(f"Task result: {result}")

    # Shutdown
    await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

## Agents

### PM Agent (Project Manager)
- Task planning and decomposition
- Priority assignment
- Resource coordination
- Progress tracking

### Dev Agent (Developer)
- Code generation and implementation
- Bug fixing
- Code review participation
- Refactoring

### QA Agent (Quality Assurance)
- Test planning and strategy
- Test case generation
- Test execution
- Quality validation

### Security Agent
- Security analysis and review
- Vulnerability detection
- Compliance checking
- Threat modeling

### Docs Agent (Documentation)
- Documentation generation
- API documentation
- User guides
- Code documentation

## Configuration

Configuration can be set via environment variables:

```bash
# Environment
export ORCHESTRATOR_ENV=development  # development, testing, staging, production

# Debug mode
export ORCHESTRATOR_DEBUG=false

# LLM Configuration (placeholder)
export ORCHESTRATOR_LLM_PROVIDER=NOT_CONFIGURED
export ORCHESTRATOR_LLM_MODEL=NOT_CONFIGURED
export ORCHESTRATOR_LLM_MAX_TOKENS=4096
export ORCHESTRATOR_LLM_TEMPERATURE=0.7

# Observability
export ORCHESTRATOR_LOG_LEVEL=INFO
export ORCHESTRATOR_ENABLE_METRICS=true
export ORCHESTRATOR_ENABLE_TRACING=true

# Adapters (all disabled by default)
export ORCHESTRATOR_ENABLE_CLI_ADAPTER=false
export ORCHESTRATOR_ENABLE_API_ADAPTER=false
export ORCHESTRATOR_ENABLE_VCS_ADAPTER=false
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=orchestrator

# Run specific test file
pytest tests/test_agents.py
```

### Code Quality

```bash
# Lint with ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/
```

## Roadmap

### Phase 1 (Current) - MVP
- [x] Core agent framework
- [x] Task management and distribution
- [x] Dynamic conversation system
- [x] Correction loops
- [x] Placeholder adapters
- [x] Basic observability

### Phase 2 - Integration
- [ ] AutoGen integration
- [ ] LLM provider configuration
- [ ] CLI adapter implementation
- [ ] API adapter implementation

### Phase 3 - Advanced Features
- [ ] VCS/Git integration
- [ ] CI/CD adapter
- [ ] External metrics export
- [ ] Distributed tracing export
- [ ] Web UI dashboard

### Phase 4 - Production Ready
- [ ] Credential management
- [ ] Multi-tenant support
- [ ] Horizontal scaling
- [ ] Enterprise security features

## Architecture

### Contracts

The orchestrator uses contract-based design for extensibility:

- **AgentContract**: Defines the interface all agents must implement
- **AdapterContract**: Defines the interface for external system adapters
- **EvaluationContract**: Defines the interface for evaluators in correction loops

### Observability

Built-in observability features (placeholder implementations):

- **Logger**: Structured logging with correlation IDs
- **MetricsCollector**: Counter, gauge, histogram, and timer metrics
- **Tracer**: Distributed tracing with spans and events

### Cross-Platform Support

The orchestrator is designed to be Linux-first while maintaining cross-OS awareness:

- Automatic WSL detection
- Container environment detection
- Cross-platform path handling
- Platform-specific configuration paths

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see [LICENSE](LICENSE) for details.
