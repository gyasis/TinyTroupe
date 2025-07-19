# Async Agent Orchestration Features - Quick Reference

## 🚀 New Features Added to TinyTroupe

### Core Async Components
1. **AsyncTinyPerson** (`tinytroupe/async_agent.py`) - Async version of TinyPerson
2. **AsyncAdaptiveTinyPerson** (`tinytroupe/async_adaptive_agent.py`) - Async + Adaptive behaviors
3. **AsyncTinyWorld** (`tinytroupe/async_world.py`) - Concurrent agent simulation
4. **AsyncEventBus** (`tinytroupe/async_event_bus.py`) - Priority-based event handling
5. **CEOInterruptHandler** (`tinytroupe/ceo_interrupt.py`) - Real-time simulation control
6. **AgentOrchestrator** (`tinytroupe/agent_orchestrator.py`) - Intelligent task management

### Test Files
- **Primary Test**: `scripts/async_secondscript.py` - Healthcare blockchain meeting with all async features
- **Orchestration Demo**: `examples/orchestrator_usage_example.py` - 5 usage examples
- **Test Suite**: `tests/test_agent_orchestrator.py` - Comprehensive tests

### Project Definitions
- `projects/healthcare_blockchain_compressed.json` - Same-day execution
- `projects/healthcare_blockchain_project.json` - Distributed timeline

## 🎯 Quick Start

### 1. Test Async Meeting Simulation
```bash
# Run the async version of secondscript.py
python scripts/async_secondscript.py
```

This demonstrates:
- All 6 agents using AsyncAdaptiveTinyPerson
- Concurrent processing (all agents think/act simultaneously)
- CEO interrupt capability (press SPACEBAR)
- Meeting broadcasting (all agents hear all conversations)
- Natural conversation flow without forced wrap-ups
- Extraction-based results processing

### 2. Test Orchestration System
```bash
# Interactive menu with 5 examples
python examples/orchestrator_usage_example.py
```

Choose from:
1. Quick Compressed Execution
2. Incremental with Checkpoints
3. Full Simulation Mode
4. Custom Orchestrator
5. Real-time CEO Control

### 3. Run Tests
```bash
cd tests
pytest test_agent_orchestrator.py -v
```

## 🔑 Key Differences

### Original secondscript.py (Sync)
- Sequential agent processing
- No CEO interrupts
- Mixed agent types (TinyPerson + AdaptiveTinyPerson)
- Forced wrap-up logic

### New async_secondscript.py (Async)
- **Concurrent processing** - All agents process simultaneously
- **CEO interrupts** - Press SPACEBAR for real-time control
- **All AsyncAdaptiveTinyPerson** - Everyone gets async + adaptive
- **Natural conversations** - Intelligent wrap-up after 7+ rounds
- **Performance metrics** - Track async vs sync agents

## 📊 Performance Benefits

```python
# Sync version (sequential)
for agent in agents:
    agent.listen_and_act(prompt)  # One at a time

# Async version (concurrent)
await asyncio.gather(*[
    agent.async_listen_and_act(prompt) 
    for agent in agents
])  # All at once!
```

## 🎛️ CEO Interrupt Usage

During any async simulation:
1. Press **SPACEBAR** to interrupt
2. Options appear:
   - Get status update
   - Pause/resume execution
   - Skip current task
   - Adjust priorities
   - Add steering commands

## 📁 Documentation

- **Complete Guide**: `docs/async_orchestration_guide.md`
- **Testing Guide**: `docs/async_secondscript_testing.md`
- **CEO Interrupt PRD**: `docs/prd_ceo_interrupt.md`

## ⚡ Quick Code Example

```python
from tinytroupe.async_adaptive_agent import create_async_adaptive_agent
from tinytroupe.async_world import AsyncTinyWorld

# Create async adaptive agent
agent = create_async_adaptive_agent(
    name="Alice",
    occupation="Project Manager",
    personality_traits=["organized", "communicative"]
)

# Create async world with CEO interrupt
world = AsyncTinyWorld(
    "Team Meeting",
    agents=[agent],
    enable_ceo_interrupt=True
)

# Run with concurrent processing
await world.async_run(steps=5)
```

## 🔧 Installation Note

The async features are already integrated into your branch. No additional installation needed beyond the existing TinyTroupe setup.

## 🚨 Important Notes

1. **Backward Compatible**: Async versions live alongside sync versions
2. **No Original Code Changes**: All new features in separate files
3. **Optional Dependencies**: `aioconsole` for better CEO interrupts (fallback available)
4. **Cross-Platform**: CEO interrupts work on Windows/Unix/Mac

---

Start with `python scripts/async_secondscript.py` to see all features in action!