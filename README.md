# Autogen-Orchestrator

A modular AI meta-orchestrator MVP built on AutoGen. Defines agents for PM, Dev, QA, Security, Docs, Architect, Research, DevOps, and Data, enabling dynamic multi-agent conversations, task distribution, evaluation, and correction loops. Linux/WSL-first, extensible with adapters for external CLIs and APIs, designed to evolve into a full AI-assisted software company.

## Features

- **AutoGen LLM Integration**: Optional AI-powered agent responses using AutoGen framework (NEW in v0.4.0)
- **Multi-Agent Architecture**: PM, Dev, QA, Security, Docs, Architect, Research, DevOps, and Data agents with specialized capabilities
- **Workflow Engine**: Define and execute multi-step workflows with dependencies and parallel execution
- **Dynamic Conversations**: Flexible conversation modes (Sequential, Round-Robin, Dynamic, Broadcast)
- **Task Distribution**: Priority-based task queue with dependency management
- **Task Templates**: Reusable task templates with variable substitution for common development scenarios
- **Task Retry & Recovery**: Automatic retry logic with configurable strategies (immediate, linear, exponential backoff)
- **Correction Loops**: Iterative improvement through evaluation and correction
- **Memory & Knowledge**: Agent memory system and shared knowledge base
- **Plugin System**: Extensible architecture for custom agents, adapters, and evaluators
- **CLI Adapter**: Execute shell commands with sandboxing and timeout controls
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
│   │   ├── docs_agent.py # Documentation agent
│   │   ├── architect_agent.py  # System Architect agent
│   │   ├── research_agent.py   # Research agent
│   │   ├── devops_agent.py     # DevOps agent
│   │   └── data_agent.py       # Data agent
│   ├── contracts/        # Interface definitions
│   │   ├── agent_contract.py    # Agent interface
│   │   ├── adapter_contract.py  # Adapter interface
│   │   └── evaluation_contract.py  # Evaluation interface
│   ├── core/             # Core orchestration logic
│   │   ├── orchestrator.py     # Main orchestrator
│   │   ├── task.py             # Task management, templates, retry
│   │   ├── conversation.py     # Conversation management
│   │   └── correction_loop.py  # Correction loop logic
│   ├── workflow/         # Workflow engine
│   │   ├── definition.py       # Workflow and step definitions
│   │   └── engine.py           # Workflow execution engine
│   ├── memory/           # Memory and knowledge management
│   │   ├── memory_store.py     # Agent memory storage
│   │   └── knowledge_base.py   # Shared knowledge repository
│   ├── plugins/          # Plugin system
│   │   ├── base.py             # Plugin base classes
│   │   └── manager.py          # Plugin lifecycle management
│   ├── adapters/         # External system adapters
│   │   ├── cli_adapter.py      # CLI integration with subprocess execution
│   │   ├── api_adapter.py      # API integration (placeholder)
│   │   └── vcs_adapter.py      # VCS integration (placeholder)
│   ├── observability/    # Monitoring and tracing
│   │   ├── logger.py           # Structured logging
│   │   ├── metrics.py          # Metrics collection
│   │   └── tracer.py           # Distributed tracing
│   └── utils/            # Utilities
│       ├── platform.py         # Cross-OS utilities
│       └── config.py           # Configuration management
├── tests/                # Test suite (230+ tests)
├── BACKLOG.md            # Evolutionary backlog
├── pyproject.toml        # Project configuration
└── README.md

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

    # Register agents (with optional AutoGen LLM integration)
    # Set ORCHESTRATOR_LLM_API_KEY environment variable to enable AutoGen
    enable_autogen = True  # or False for rule-based responses
    orchestrator.register_agent(PMAgent(enable_autogen=enable_autogen))
    orchestrator.register_agent(DevAgent(enable_autogen=enable_autogen))
    orchestrator.register_agent(QAAgent(enable_autogen=enable_autogen))
    orchestrator.register_agent(SecurityAgent(enable_autogen=enable_autogen))
    orchestrator.register_agent(DocsAgent(enable_autogen=enable_autogen))

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

### Architect Agent (NEW)
- System design and architecture decisions
- Technical specifications
- Technology stack recommendations
- Design pattern suggestions
- Component interaction design

### Research Agent (NEW)
- Information gathering and synthesis
- Technology research and comparison
- Best practices identification
- Knowledge base maintenance

### DevOps Agent (NEW)
- CI/CD pipeline design and management
- Infrastructure as Code (IaC)
- Deployment automation
- Container orchestration

### Data Agent (NEW)
- Data modeling and schema design
- Database design and optimization
- Data pipeline architecture (ETL/ELT)
- Data quality and validation
- Data analysis and insights

## Task Templates (NEW)

Create tasks from reusable templates with variable substitution:

```python
from orchestrator.core.task import TaskTemplates, TaskTemplateLibrary

# Use pre-built templates
library = TaskTemplates.get_default_library()

# Create a feature implementation task
task = library.create_task_from_template(
    "feature_implementation",
    title="Add User Authentication",
    variables={
        "feature_name": "OAuth2 Login",
        "requirements": "Support Google and GitHub SSO",
        "acceptance_criteria": "Users can log in via OAuth2 providers",
    },
)

# Or use templates directly
template = TaskTemplates.bug_fix()
task = template.create_task(
    title="Fix Login Bug",
    variables={
        "bug_description": "Login fails on Safari",
        "steps_to_reproduce": "1. Open Safari\n2. Click login",
    },
)
```

Available templates: `feature_implementation`, `bug_fix`, `code_review`, `security_audit`, `api_endpoint`, `database_migration`, `test_suite`, `documentation`.

## Task Retry & Recovery (NEW)

Configure automatic retry for failed tasks:

```python
from orchestrator.core.task import Task, RetryConfig, RetryStrategy

# Configure retry behavior
retry_config = RetryConfig(
    strategy=RetryStrategy.EXPONENTIAL,  # or LINEAR, IMMEDIATE, NONE
    max_retries=5,
    base_delay_seconds=2.0,
    max_delay_seconds=60.0,
    retry_on_errors=["timeout", "connection"],  # Empty = retry on all errors
)

task = Task(
    title="Deploy to Production",
    description="Deploy the application",
    retry_config=retry_config,
)

# Task queue handles retry logic automatically
queue = TaskQueue()
queue.add_task(task)

# On failure, task enters RETRYING state
will_retry = queue.mark_failed(task.id, "Connection timeout")

# Process tasks ready for retry
retried_ids = queue.process_retries()
```

## Workflow Engine (NEW)

Define and execute multi-step workflows with dependencies:

```python
from orchestrator.workflow import Workflow, WorkflowStep, WorkflowStepType, WorkflowEngine, WorkflowTemplates

# Use a pre-built template
workflow = WorkflowTemplates.feature_development()

# Or create custom workflows
workflow = Workflow(name="Custom Workflow")
step1 = WorkflowStep(name="plan", step_type=WorkflowStepType.TASK, config={"agent": "PMAgent"})
step2 = WorkflowStep(name="develop", step_type=WorkflowStepType.TASK, config={"agent": "DevAgent"}, dependencies=[step1.id])
workflow.add_step(step1)
workflow.add_step(step2)

# Execute the workflow
engine = WorkflowEngine()
engine.register_agents(orchestrator.agents)
result = await engine.execute(workflow)
```

## Memory & Knowledge System (NEW)

Agents can store and retrieve memories and knowledge:

```python
from orchestrator.memory import MemoryStore, KnowledgeBase, KnowledgeCategory

# Agent memory
memory = MemoryStore(owner="DevAgent")
memory.store("Important finding about the codebase", tags=["architecture"])
results = memory.search(query="codebase")

# Shared knowledge base
kb = KnowledgeBase.create_with_defaults()
kb.add("API Design Guidelines", "Use RESTful conventions...", KnowledgeCategory.BEST_PRACTICE)
entries = kb.search(category=KnowledgeCategory.BEST_PRACTICE)
```

## Plugin System (NEW)

Extend functionality with plugins:

```python
from orchestrator.plugins import Plugin, PluginMetadata, PluginType, PluginManager

class MyPlugin(Plugin):
    @property
    def metadata(self):
        return PluginMetadata(
            name="my_plugin",
            version="1.0.0",
            description="Custom plugin",
            plugin_type=PluginType.PROCESSOR
        )
    
    async def execute(self, context):
        return {"processed": True}

manager = PluginManager()
await manager.register(MyPlugin())
```

## AutoGen LLM Integration (NEW in v0.4.0)

The orchestrator now supports optional AutoGen framework integration for AI-powered agent responses:

```python
from orchestrator.agents import DevAgent, PMAgent

# Enable AutoGen for intelligent LLM-powered responses
# Requires ORCHESTRATOR_LLM_API_KEY environment variable
dev_agent = DevAgent(enable_autogen=True)
pm_agent = PMAgent(enable_autogen=True)

# Without AutoGen (rule-based responses)
dev_agent = DevAgent(enable_autogen=False)  # or just DevAgent()
```

**Features:**
- All 9 agents support AutoGen integration (PM, Dev, QA, Security, Docs, Architect, Research, DevOps, Data)
- Graceful fallback to rule-based responses when API key not configured
- Configurable via environment variables
- Per-agent enable/disable control

**Configuration:**
```bash
# Required for AutoGen integration
export ORCHESTRATOR_LLM_API_KEY=your_openai_api_key

# Optional - customize LLM behavior
export ORCHESTRATOR_LLM_MODEL=gpt-4  # default: gpt-4
export ORCHESTRATOR_LLM_MAX_TOKENS=4096
export ORCHESTRATOR_LLM_TEMPERATURE=0.7
```

**Example:**
```bash
# Run the AutoGen integration example
export ORCHESTRATOR_LLM_API_KEY=your_key
python examples/autogen_integration_example.py
```

See `examples/autogen_integration_example.py` for a complete demonstration.

## Configuration

Configuration can be set via environment variables:

```bash
# Environment
export ORCHESTRATOR_ENV=development  # development, testing, staging, production

# Debug mode
export ORCHESTRATOR_DEBUG=false

# LLM Configuration (AutoGen Integration - NEW in v0.4.0)
export ORCHESTRATOR_LLM_API_KEY=your_openai_api_key  # Required for AutoGen LLM integration
export ORCHESTRATOR_LLM_MODEL=gpt-4  # or gpt-3.5-turbo, gpt-4-turbo, etc.
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

### Phase 1 - MVP ✅ COMPLETED
- [x] Core agent framework
- [x] Task management and distribution
- [x] Dynamic conversation system
- [x] Correction loops
- [x] Placeholder adapters
- [x] Basic observability

### Phase 2 - Integration (In Progress)
- [x] AutoGen integration ✅ NEW in v0.4.0
- [x] LLM provider configuration ✅ NEW in v0.4.0
- [x] CLI adapter implementation ✅
- [ ] API adapter implementation
- [ ] VCS/Git adapter implementation

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
