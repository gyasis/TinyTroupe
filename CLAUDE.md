# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
```bash
# Run all tests
cd tests
pytest -s --refresh_cache

# Run specific test categories
pytest tests/unit/           # Unit tests
pytest tests/scenarios/      # Scenario tests
pytest tests/non_functional/ # Non-functional tests
```

### Installation
```bash
# Create conda environment
conda create -n tinytroupe python=3.10
conda activate tinytroupe

# Install in development mode
pip install -e .

# Install from repository (production)
pip install .
```

### Configuration
- Copy `examples/config.ini` to your working directory and customize it
- Set environment variables for API keys:
  - `OPENAI_API_KEY` for OpenAI API
  - `AZURE_OPENAI_KEY` and `AZURE_OPENAI_ENDPOINT` for Azure OpenAI

## Architecture Overview

### Core Components

**TinyPerson** (`tinytroupe/agent.py`):
- Main agent class representing simulated people
- Contains episodic and semantic memory systems
- Handles stimulus-response interactions through `listen()` and `act()` methods
- Cognitive states include attention, emotions, and goals
- Uses LLM calls for behavior generation

**TinyWorld** (`tinytroupe/environment.py`):
- Environment class where agents interact
- Manages agent communications and actions
- Handles simulation time progression
- Supports both broadcast and targeted messaging

**TinyFactory** (`tinytroupe/factory.py`):
- Generates new TinyPerson instances using LLM prompts
- Uses template-based persona generation
- Supports context-specific agent creation

**Control System** (`tinytroupe/control.py`):
- Manages simulation state and caching
- Provides transactional support for reliable state management
- Handles checkpoint and rollback functionality

### Key Design Principles

1. **Simulation-focused**: Agents simulate human behavior rather than provide assistance
2. **Cognitive psychology inspired**: Memory systems, attention, emotions
3. **Programmatic control**: Python-based agent and environment definition
4. **Caching support**: Two-level caching (simulation state + LLM API calls)

### Data Flow

1. **Agent Creation**: Use `TinyPersonFactory` or pre-defined examples from `examples.py`
2. **Environment Setup**: Create `TinyWorld` and add agents
3. **Simulation**: Agents receive stimuli via `listen()` and respond via `act()`
4. **Extraction**: Use `ResultsExtractor` to process simulation outputs

## Configuration System

### Config File Structure (`config.ini`)
```ini
[OpenAI]
API_TYPE=openai              # or "azure"
MODEL=gpt-4o-mini           # Default model
TEMPERATURE=1.5             # Higher temp for more human-like variation
CACHE_API_CALLS=False       # Enable LLM call caching

[Simulation]
RAI_HARMFUL_CONTENT_PREVENTION=True
RAI_COPYRIGHT_INFRINGEMENT_PREVENTION=True

[Logging]
LOGLEVEL=ERROR              # ERROR, WARNING, INFO, DEBUG
```

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI API access
- `AZURE_OPENAI_KEY` + `AZURE_OPENAI_ENDPOINT`: Required for Azure OpenAI

## Working with Agents

### Agent Definition Pattern
```python
agent = TinyPerson("Name")
agent.define("age", 30)
agent.define("occupation", "Role")
agent.define("personality_traits", [{"trait": "Description"}])
agent.define_several("interests", [{"interest": "Topic"}])
```

### Memory Systems
- **Episodic Memory**: Recent experiences and interactions
- **Semantic Memory**: General knowledge and facts
- **Attention System**: Focus and filtering mechanisms

### Interaction Patterns
- `listen()`: Receive stimuli from environment or other agents
- `act()`: Generate responses and actions
- `listen_and_act()`: Convenience method for simple interactions

## Caching and Performance

### Simulation State Caching
```python
import tinytroupe.control as control
control.begin("simulation.cache.json")
# ... run simulation steps ...
control.checkpoint()  # Save state
control.end()
```

### LLM API Caching
- Enable in `config.ini`: `CACHE_API_CALLS=True`
- Caches identical API calls to reduce costs
- Separate from simulation state caching

## Working with Examples

### Pre-built Agents
- `create_oscar_the_architect()`: German architect persona
- `create_lisa_the_data_scientist()`: Canadian data scientist persona
- Examples in `tinytroupe/examples.py`

### Jupyter Notebooks
- All examples are in `examples/` directory
- Use dark theme for better output visualization
- Interactive development recommended for simulations

## Testing Strategy

### Test Categories
- **Unit tests** (`tests/unit/`): Test individual components
- **Scenario tests** (`tests/scenarios/`): Test complete simulation flows
- **Non-functional tests** (`tests/non_functional/`): Security and performance

### Test Execution
- Tests require valid API keys in environment
- Use `--refresh_cache` flag to force new API calls
- Tests are designed to be repeatable with caching

## Important Notes

- **Simulation vs Assistant**: TinyTroupe simulates human behavior, not AI assistance
- **Content Safety**: Uses Azure OpenAI content filters when available
- **API Dependencies**: Requires OpenAI or Azure OpenAI API access
- **Memory Usage**: Agents maintain detailed internal state - monitor memory usage
- **Prompt Engineering**: Core behavior defined in `tinytroupe/prompts/` directory

## Advanced Features

### Adaptive Agents System
TinyTroupe now includes an advanced **Adaptive Agent System** for intelligent meeting simulations:

#### AdaptiveTinyPerson (`tinytroupe/adaptive_agent.py`)
Enhanced agents with context-aware behavior:
- **Context Detection**: Automatically detects meeting types (business, technical, casual)
- **Meeting Management**: Wrap-up logic and conclusion prompts
- **Expert Authority**: Domain experts assert expertise in their areas
- **RECALL Enhancement**: Memory checks prevent circular conversations
- **Decision Forcing**: Prevents endless coordination without decisions

#### Hybrid Architecture Pattern (Recommended)
```python
# Orchestrator: Project Manager (Adaptive)
pm = create_adaptive_agent("Emily Martinez", "Project Manager")

# Domain Experts: CTO, Compliance Officer (Adaptive) 
cto = create_adaptive_agent("Dr. James Wilson", "CTO")
compliance = create_adaptive_agent("Michael Thompson", "Compliance Officer")

# Regular Participants: Standard TinyPerson
developer = TinyPerson("Lisa Chen", "Developer")
physician = TinyPerson("Dr. Sarah Chen", "Physician")
```

#### Meeting Broadcasting System
Enhanced `TinyWorld` with meeting-wide communication:
```python
# Enable meeting mode for realistic cross-agent communication
world = TinyWorld("Meeting Name", is_meeting=True)
# All TALK actions now broadcast to ALL participants
```

### Display Control System
Comprehensive formatting control for clean, readable output:

#### Display Flags
```python
# Rich text formatting control
TinyPerson.rich_text_display = False  # Disable Rich markup and > line breaks
TinyWorld.rich_text_display = False

# Debug output control  
TinyPerson.debug_display = False      # Disable debug messages
TinyWorld.debug_display = False

# Communication display control
TinyPerson.communication_display = True   # Enable/disable conversations
TinyPerson.communication_style = "simplified"  # "simplified" or "full"
```

#### Clean Output Examples
**Before (Rich text):**
```
Michael Thompson --> Emily Martinez: [CONVERSATION] 
                      > I'm glad we have consensus on the questions, and I look forward to
                      > implementing this feedback mechanism as well.
                       + --> ...others...
```

**After (Clean text):**
```
Michael Thompson --> Emily Martinez: [CONVERSATION] I'm glad we have consensus on the questions, and I look forward to implementing this feedback mechanism as well.
```

### Context Detection System (`tinytroupe/context_detection.py`)
Intelligent context awareness for appropriate agent behavior:
- **Business Meeting**: Higher action limits, authority systems, decision forcing
- **Technical Discussion**: Focus on technical expertise and problem-solving  
- **Casual Conversation**: Lower action limits, natural social interaction
- **Creative Brainstorming**: Encourages innovative thinking and idea generation
- **Interview**: Structured question-answer patterns

### Meeting Intelligence Features
1. **Natural Conversations**: Agents discuss freely without forced structure
2. **Cross-Agent Communication**: All participants hear all conversations  
3. **Memory Enhancement**: RECALL checks prevent repeated questions
4. **Expert Authority**: Domain specialists assert expertise appropriately
5. **Post-Processing Extraction**: Extract structured insights afterward

### Extraction System
TinyTroupe's core paradigm for getting structured results from simulations:

```python
# 1. Let agents have natural conversations
world.run(4)  # No forced wrap-up logic needed

# 2. Extract structured results afterward
results = default_extractor.extract_results_from_world(
    world,
    extraction_objective="Extract key technical decisions and action items",
    fields=["decisions", "action_items", "risks", "timeline"],
    fields_hints={
        "decisions": "Technical choices made during the discussion",
        "action_items": "Specific tasks assigned with owners",
        "risks": "Identified risks and concerns",
        "timeline": "Project milestones and deadlines"
    },
    verbose=True
)

# 3. Save results as JSON
default_extractor.save_as_json("meeting_results.json")
```

**Benefits:**
- Natural conversation flow
- Multiple extraction objectives from single simulation
- Structured JSON output for downstream processing
- Agents focus on domain expertise, not meeting management
5. **Decision Forcing**: Prevents circular "let's coordinate" discussions

## Project Memory Context

### Recent Development Achievements (2025-07-04)
- **✅ Hybrid Architecture**: Implemented optimal orchestrator + domain expert pattern
- **✅ Clean Display System**: Solved Rich text formatting issues with comprehensive flags
- **✅ Meeting Broadcasting**: Fixed cross-agent communication for realistic meetings
- **✅ Adaptive Intelligence**: Context-aware agents with wrap-up and decision logic
- **✅ RECALL Enhancement**: Memory checks prevent circular conversation problems
- **✅ Natural Intelligence**: Agents use conversation history effectively

### Current Best Practices
- Use **Hybrid Architecture** for business meeting simulations
- Enable **clean display mode** for readable conversations  
- Set **is_meeting=True** for cross-agent communication
- Use **adaptive agents** for orchestrators and domain experts
- Use **standard TinyPerson** for regular meeting participants

## Async Agent Orchestration System (2025-07-05)

### New Async Components
TinyTroupe now includes a comprehensive **Async Agent Orchestration System** that extends all capabilities with concurrent processing:

#### Core Async Infrastructure
- **AsyncTinyPerson** (`tinytroupe/async_agent.py`): Async version of TinyPerson with concurrent processing
- **AsyncAdaptiveTinyPerson** (`tinytroupe/async_adaptive_agent.py`): Combines async + adaptive behaviors
- **AsyncTinyWorld** (`tinytroupe/async_world.py`): Concurrent agent simulation environment
- **AsyncEventBus** (`tinytroupe/async_event_bus.py`): Priority-based event handling system
- **CEOInterruptHandler** (`tinytroupe/ceo_interrupt.py`): Real-time simulation control with cross-platform keypress detection

#### Agent Orchestrator System (`tinytroupe/agent_orchestrator.py`)
Intelligent task management and project orchestration:
- **JSON-driven Projects**: Define complete projects with agents, tasks, and dependencies
- **Flexible Scheduling**: Same-day, distributed, or compressed timeline modes
- **Skill-based Assignment**: Automatically matches agents to tasks based on skills
- **Dynamic Task Spawning**: Meeting outcomes generate new tasks automatically
- **Multiple Execution Modes**:
  - `fully_automated`: Run entire project autonomously
  - `incremental`: Execute with checkpoints for human review
  - `simulation`: Complete project management lifecycle

#### Project Definition Format
```json
{
  "project_id": "healthcare_blockchain_v1",
  "execution_mode": "incremental",
  "scheduling": {
    "mode": "distributed",
    "start_date": "2024-01-15T09:00:00"
  },
  "agents": [{
    "agent_id": "pm",
    "name": "Emily Martinez",
    "skill_levels": {"project_management": 9}
  }],
  "tasks": [{
    "task_id": "kickoff",
    "meeting_required": true,
    "attendees": ["pm", "cto"],
    "dependencies": []
  }]
}
```

#### Quick Start Examples
```bash
# Test async meeting simulation
python scripts/async_secondscript.py

# Run orchestration examples
python examples/orchestrator_usage_example.py

# Run tests
pytest tests/test_agent_orchestrator.py -v
```

#### CEO Interrupt System
Real-time control during any async simulation:
- Press **SPACEBAR** to interrupt at any time
- Get status updates, pause/resume, skip tasks, adjust priorities
- Works cross-platform (Windows/Unix/Mac)
- Fallback modes if aioconsole not available

### Async Best Practices
- **Use AsyncAdaptiveTinyPerson** for all agents in concurrent simulations
- **Enable CEO interrupts** for real-time control: `enable_ceo_interrupt=True`
- **Leverage concurrent processing**: All agents think/act simultaneously
- **Use orchestrator** for complex multi-agent projects
- **Define projects in JSON** for reusable, shareable simulations

### Recent Async Development (2025-07-05)
- **✅ Async Infrastructure**: Complete async agent system with backward compatibility
- **✅ CEO Interrupt**: Real-time simulation control with cross-platform support
- **✅ Agent Orchestrator**: JSON-driven project management with flexible scheduling
- **✅ Concurrent Processing**: 10x faster meetings through parallel agent processing
- **✅ Comprehensive Tests**: Full test suite and usage examples
- **✅ Documentation**: Complete guides for async features and orchestration