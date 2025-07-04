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

## Project Memory Context

### Recent Development Observations
- Exploring advanced cognitive modeling techniques in agent simulation
- Iterating on memory system design to improve agent behavior realism
- Investigating more nuanced interaction patterns between simulated agents