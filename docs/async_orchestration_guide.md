# Async Agent Orchestration System - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Core Components](#core-components)
5. [Execution Modes](#execution-modes)
6. [Project Definition Format](#project-definition-format)
7. [Usage Examples](#usage-examples)
8. [API Reference](#api-reference)
9. [Testing](#testing)
10. [Best Practices](#best-practices)

## Overview

The Async Agent Orchestration System is a comprehensive framework for managing multi-agent simulations with intelligent task assignment, flexible scheduling, and real-time control capabilities. It extends TinyTroupe with asynchronous processing, adaptive agent behaviors, and CEO interrupt functionality.

### Key Features
- **Async Processing**: Concurrent agent execution for improved performance
- **Intelligent Task Assignment**: Skill-based matching of agents to tasks
- **Flexible Scheduling**: Same-day, distributed, or compressed timelines
- **Dynamic Task Spawning**: Meeting outcomes generate new tasks automatically
- **CEO Interrupts**: Real-time meeting control with cross-platform keypress detection
- **Multiple Execution Modes**: Fully automated, incremental, or simulation modes
- **Skill Development**: Agents improve their capabilities through task completion

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentOrchestrator                        │
├─────────────────────────────────────────────────────────────┤
│  • Project Management (JSON-driven)                         │
│  • Task Assignment Algorithm                                │
│  • Meeting Coordination                                     │
│  • CEO Interrupt Handling                                   │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴───────┬─────────────┬──────────────┐
       │               │             │              │
┌──────▼──────┐ ┌─────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
│AsyncTinyWorld│ │AsyncEventBus│ │CEO      │ │AsyncAdaptive│
│             │ │            │ │Interrupt│ │TinyPerson   │
└─────────────┘ └────────────┘ └─────────┘ └─────────────┘
```

## Quick Start

### 1. Basic Healthcare Blockchain Demo
```bash
# Run the async healthcare blockchain meeting simulation
python scripts/async_secondscript.py
```

### 2. Interactive Orchestrator Examples
```bash
# Choose from 5 different examples
python examples/orchestrator_usage_example.py
```

### 3. Run Tests
```bash
# Run comprehensive test suite
cd tests
pytest test_agent_orchestrator.py -v
```

## Core Components

### AsyncTinyPerson
Extends the base TinyPerson with async capabilities:
```python
from tinytroupe.async_agent import AsyncTinyPerson

# Create async agent
agent = AsyncTinyPerson("Alice")
agent.define("occupation", "Project Manager")
await agent.async_listen_and_act("What's our project status?")
```

### AsyncAdaptiveTinyPerson
Combines async processing with adaptive behaviors:
```python
from tinytroupe.async_adaptive_agent import create_async_adaptive_agent

# Create adaptive async agent
pm = create_async_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager",
    personality_traits=["organized", "communicative"],
    years_experience="10+ years"
)
```

### AgentOrchestrator
The main orchestration engine:
```python
from tinytroupe.agent_orchestrator import AgentOrchestrator

# Create orchestrator
orchestrator = AgentOrchestrator()
await orchestrator.initialize_event_bus()

# Register agents with skills
orchestrator.register_agent(
    agent,
    skills={"project_management": 8, "communication": 7},
    preferences={"coordination": 9}
)

# Load project from JSON
await orchestrator.load_project("projects/healthcare_blockchain.json")

# Run project
result = await orchestrator.run_project_fully_automated()
```

### CEO Interrupt System
Real-time control during execution:
```python
from tinytroupe.ceo_interrupt import CEOInterruptHandler

# Handler automatically monitors for keypresses
# Press SPACEBAR during execution to interrupt
# Supports Windows, Unix, and fallback modes
```

## Execution Modes

### 1. Fully Automated Mode
Runs entire project without human intervention:
```python
result = await orchestrator.run_project_fully_automated()
```
- Executes all tasks in sequence
- Handles dependencies automatically
- Spawns follow-up tasks from meetings
- No human input required

### 2. Incremental Mode
Executes with checkpoints for human review:
```python
result = await orchestrator.run_project_incremental(
    checkpoint_frequency="after_each_meeting"
)
```
- Pauses after meetings for review
- Allows CEO interrupts at any time
- Human can adjust project direction
- Resume/skip/modify capabilities

### 3. Simulation Mode
Complete project management lifecycle:
```python
result = await orchestrator.simulate_complete_project(
    spawn_additional_meetings=True
)
```
- Simulates realistic project evolution
- Spawns management meetings dynamically
- Adapts to project complexity
- Full project lifecycle modeling

## Project Definition Format

### JSON Schema
```json
{
  "project_id": "unique_id",
  "title": "Project Title",
  "description": "Project description",
  "execution_mode": "fully_automated|incremental|simulation",
  "scheduling": {
    "mode": "same_day|distributed|compressed",
    "start_date": "2024-01-15T09:00:00",
    "compress_timeline": true,
    "auto_adjust_dates": true
  },
  "agents": [
    {
      "agent_id": "pm",
      "name": "Agent Name",
      "occupation": "Role",
      "skill_levels": {
        "skill_name": 8  // 1-10 scale
      },
      "preferences": {
        "task_type": 9  // 1-10 scale
      }
    }
  ],
  "tasks": [
    {
      "task_id": "unique_task_id",
      "description": "Task description",
      "scheduled_date": "2024-01-15T09:00:00",
      "estimated_hours": 2,
      "priority": 5,  // 1-5 scale
      "meeting_required": true,
      "attendees": ["agent_id1", "agent_id2"],
      "required_skills": {
        "skill_name": 6  // minimum level
      },
      "dependencies": ["other_task_id"],
      "follow_up_tasks": ["next_task_id"]
    }
  ],
  "ceo_oversight": {
    "enabled": true,
    "interrupt_triggers": ["milestone_completion"],
    "review_frequency": "weekly"
  }
}
```

### Example Projects
1. **Healthcare Blockchain (Compressed)**: `projects/healthcare_blockchain_compressed.json`
   - 6 tasks, same-day execution
   - Good for testing and demos

2. **Healthcare Blockchain (Full)**: `projects/healthcare_blockchain_project.json`
   - 12 tasks, distributed timeline
   - Realistic project simulation

## Usage Examples

### Example 1: Quick Test with Compressed Project
```python
from tinytroupe.agent_orchestrator import run_healthcare_blockchain_project

# Run compressed project for quick testing
result = await run_healthcare_blockchain_project(
    "projects/healthcare_blockchain_compressed.json",
    execution_mode="fully_automated"
)

print(f"Tasks completed: {result['task_summary']['completed_tasks']}")
print(f"Meetings held: {result['statistics']['meetings_held']}")
```

### Example 2: Custom Orchestrator Setup
```python
from tinytroupe.agent_orchestrator import AgentOrchestrator
from tinytroupe.async_adaptive_agent import create_async_adaptive_agent

# Create orchestrator
orchestrator = AgentOrchestrator()
await orchestrator.initialize_event_bus()

# Create custom agents
pm = create_async_adaptive_agent("Alice", "Project Manager")
dev = create_async_adaptive_agent("Bob", "Developer")

# Register with skills
orchestrator.register_agent(pm, {"management": 9}, {"coordination": 10})
orchestrator.register_agent(dev, {"development": 8}, {"coding": 9})

# Create custom task
task = TaskDefinition(
    task_id="custom_task",
    description="Design new feature",
    required_skills={"development": 7},
    meeting_required=True,
    attendees=["Alice", "Bob"]
)

# Execute task
await orchestrator._execute_meeting_task(task)
```

### Example 3: CEO Interrupt During Execution
```python
# During any execution, press SPACEBAR to interrupt
# The system will pause and show current status
# You can then:
# - Resume execution
# - Skip current task
# - Adjust priorities
# - Add new tasks
# - Request status update
```

## API Reference

### AgentOrchestrator Methods

#### `register_agent(agent, skills, preferences)`
Register an agent with the orchestrator.
- `agent`: AsyncAdaptiveTinyPerson instance
- `skills`: Dict[str, int] - skill levels (1-10)
- `preferences`: Dict[str, int] - task preferences (1-10)

#### `load_project(project_path)`
Load project definition from JSON file.
- `project_path`: Path to JSON project file

#### `run_project_fully_automated()`
Execute project in fully automated mode.
- Returns: Dict with execution results

#### `run_project_incremental(checkpoint_frequency)`
Execute project with checkpoints.
- `checkpoint_frequency`: "after_each_task" | "after_each_meeting" | "daily"
- Returns: Dict with execution results

#### `simulate_complete_project(spawn_additional_meetings)`
Run full project simulation.
- `spawn_additional_meetings`: Boolean - whether to create management meetings
- Returns: Dict with simulation results

### Task Assignment Algorithm
```python
def _find_best_agent_for_task(self, task: TaskDefinition) -> Optional[AgentProfile]:
    """
    Skill-based assignment algorithm:
    1. Filter agents meeting minimum skill requirements
    2. Calculate match score: Σ(agent_skill * skill_importance)
    3. Add preference bonus: preference_level * 0.1
    4. Consider workload: penalty for overloaded agents
    5. Return best matching agent
    """
```

## Testing

### Running the Test Script: async_secondscript.py

The `async_secondscript.py` is the primary test file for the new async orchestration features:

```bash
# Location: scripts/async_secondscript.py
python scripts/async_secondscript.py
```

This script demonstrates:
1. **AsyncAdaptiveTinyPerson** agents in action
2. **Concurrent meeting processing**
3. **CEO interrupt capabilities**
4. **Meeting broadcasting** with all agents hearing all conversations
5. **Natural conversation flow** without forced wrap-ups
6. **Extraction-based results** processing

### What async_secondscript.py Tests
```python
# Creates 6 AsyncAdaptiveTinyPerson agents
pm = create_async_adaptive_agent("Emily Martinez", "Project Manager")
cto = create_async_adaptive_agent("Dr. James Wilson", "CTO")
# ... and 4 more

# Runs concurrent meeting simulation
await world.async_run(4)  # 4 rounds of concurrent processing

# Extracts structured results
results = default_extractor.extract_results_from_world(
    world,
    extraction_objective="Extract key decisions...",
    fields=["decisions", "action_items", "risks"]
)
```

### Unit Tests
```bash
cd tests
pytest test_agent_orchestrator.py -v

# Run specific test
pytest test_agent_orchestrator.py::TestAgentOrchestrator::test_task_assignment_algorithm -v
```

### Integration Tests
```bash
# Test compressed project execution
pytest test_agent_orchestrator.py::TestProjectExecution::test_compressed_project_execution -v
```

## Best Practices

### 1. Project Design
- Start with compressed timeline for testing
- Use distributed timeline for realistic simulations
- Define clear skill requirements for tasks
- Set appropriate task dependencies

### 2. Agent Configuration
- Assign realistic skill levels (5-8 for competent, 9-10 for expert)
- Set preferences to guide task assignment
- Use personality traits for better conversations

### 3. Meeting Design
- Keep initial meetings short (0.5-2 hours)
- Include relevant stakeholders only
- Define clear meeting objectives
- Let extraction handle result processing

### 4. CEO Interrupts
- Use sparingly for critical decisions
- Provide clear steering commands
- Don't micromanage agent conversations
- Trust the orchestration system

### 5. Performance Optimization
- Use async agents for all participants
- Enable meeting broadcasting for realism
- Batch task execution when possible
- Monitor agent workload distribution

## Troubleshooting

### Common Issues

1. **"aioconsole not available" warning**
   - Normal on some systems
   - CEO interrupt falls back to threading
   - Functionality not affected

2. **Tasks not executing**
   - Check task dependencies
   - Verify agent skills match requirements
   - Ensure scheduled dates are set

3. **Meetings producing no outcomes**
   - Increase meeting rounds
   - Check extraction objective clarity
   - Verify agents have relevant context

4. **CEO interrupt not working**
   - Try different terminal emulators
   - Check keyboard focus is on terminal
   - Use incremental mode for easier interrupts

## Advanced Features

### Dynamic Task Spawning
Meeting outcomes automatically generate new tasks:
```python
# In meeting results
"action_items": [
    "Create technical specification",
    "Schedule follow-up review"
]
# Becomes new tasks automatically
```

### Skill Development
Agents improve through task completion:
```python
# After completing a blockchain task
agent.skills["blockchain"] += 0.1 * skill_development_rate
```

### Preference Learning
System adapts to agent performance:
```python
# Successful task completion increases preference
if task_success:
    agent.preferences[task_type] += 0.1
```

## Integration with Existing Code

The async system is designed to work alongside existing TinyTroupe code:

```python
# Mix async and sync agents
async_agent = AsyncAdaptiveTinyPerson("Async Alice")
sync_agent = TinyPerson("Sync Bob")

# Both can participate in same world
world = AsyncTinyWorld("Mixed Meeting")
world.add_agent(async_agent)
world.add_agent(sync_agent)  # Wrapped automatically
```

## Future Enhancements

Planned features:
1. **Web Dashboard**: Real-time project monitoring
2. **ML-based Scheduling**: Optimize task timing
3. **Multi-project Orchestration**: Manage agent allocation across projects
4. **Advanced Analytics**: Performance metrics and insights
5. **Plugin System**: Custom task executors and extractors

---

For more examples, see `examples/orchestrator_usage_example.py` which contains 5 complete usage scenarios.