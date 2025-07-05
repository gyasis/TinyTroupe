# Testing Guide: async_secondscript.py

## Overview
The `async_secondscript.py` is the primary demonstration and testing script for the new async agent orchestration features. It showcases all the advanced capabilities implemented in the async system.

## Location
```bash
scripts/async_secondscript.py
```

## How to Run
```bash
# From project root
python scripts/async_secondscript.py

# Or directly
cd scripts
python async_secondscript.py
```

## What It Demonstrates

### 1. AsyncAdaptiveTinyPerson Usage
The script creates 6 agents using the new async adaptive system:
```python
# Project Manager - Orchestrator
pm = create_async_adaptive_agent("Emily Martinez", "Project Manager")

# Domain Experts
cto = create_async_adaptive_agent("Dr. James Wilson", "CTO")
compliance = create_async_adaptive_agent("Michael Thompson", "Compliance Officer")

# Team Members
dev_lead = create_async_adaptive_agent("Lisa Chen", "Senior Developer")
blockchain_dev = create_async_adaptive_agent("Alex Rodriguez", "Blockchain Developer")
physician = create_async_adaptive_agent("Dr. Sarah Chen", "Physician")
```

### 2. Concurrent Async Processing
All agents process inputs simultaneously:
```python
# Traditional sync would process sequentially
# Async processes all agents in parallel
await world.async_run(4)  # 4 rounds of concurrent interaction
```

### 3. Meeting Broadcasting
The AsyncTinyWorld enables realistic meeting dynamics:
```python
world = AsyncTinyWorld("Healthcare Blockchain Planning", is_meeting=True)
# All TALK actions broadcast to ALL participants
# Everyone hears everything - like a real meeting
```

### 4. CEO Interrupt Capability
During execution, you can press SPACEBAR to:
- Pause the meeting
- Get status updates
- Redirect conversation
- Skip to conclusions
- Add new topics

### 5. Natural Conversation Flow
No forced wrap-up logic - agents converse naturally:
- Adaptive agents detect meeting context
- Domain experts assert expertise
- Memory checks prevent circular discussions
- Natural conclusion when objectives are met

### 6. Extraction-Based Results
After the meeting, structured data is extracted:
```python
results = default_extractor.extract_results_from_world(
    world,
    extraction_objective="Extract key technical decisions and action items",
    fields=["decisions", "action_items", "risks", "timeline"],
    fields_hints={
        "decisions": "Technical choices made during the discussion",
        "action_items": "Specific tasks assigned with owners",
        "risks": "Identified risks and concerns",
        "timeline": "Project milestones and deadlines"
    }
)
```

## Expected Output

### 1. Meeting Start
```
🚀 Starting Healthcare Blockchain Async Meeting...
📋 Meeting Context: Development of a blockchain-based medical records system
👥 Participants: 6 AsyncAdaptiveTinyPerson agents

⚡ Using AsyncTinyWorld for concurrent agent processing
🎙️ Meeting broadcasting enabled - all agents hear all conversations
🚨 CEO interrupt monitoring active (press SPACEBAR)
```

### 2. Concurrent Conversations
```
Emily Martinez --> Dr. James Wilson: [CONVERSATION] Let's discuss the technical architecture...
Dr. Sarah Chen --> Michael Thompson: [CONVERSATION] What are the HIPAA implications...
[Multiple simultaneous conversations]
```

### 3. Adaptive Behaviors
- Project Manager coordinates discussions
- CTO asserts technical decisions
- Compliance Officer raises regulatory concerns
- Developers discuss implementation details
- Physician provides clinical perspective

### 4. CEO Interrupt (if triggered)
```
🚨 CEO INTERRUPT DETECTED!
Current Status:
- Round 2 of 4
- Active speakers: Emily Martinez, Dr. James Wilson
- Topics discussed: blockchain platform, HIPAA compliance

CEO Message: "Focus on security architecture"
📢 Broadcasting CEO directive to all agents...
```

### 5. Extraction Results
```json
{
  "decisions": [
    "Use Hyperledger Fabric for healthcare compliance",
    "Implement FHIR standards for interoperability",
    "Deploy on HIPAA-compliant cloud infrastructure"
  ],
  "action_items": [
    "Lisa Chen: Create API specification for FHIR endpoints",
    "Alex Rodriguez: Prototype smart contracts for consent",
    "Michael Thompson: Complete compliance audit checklist"
  ],
  "risks": [
    "Scalability concerns with blockchain for large datasets",
    "Integration complexity with existing EHR systems",
    "Regulatory uncertainty around blockchain in healthcare"
  ],
  "timeline": [
    "Week 1-2: Technical architecture finalization",
    "Week 3-4: Prototype development",
    "Week 5-6: Compliance review and testing"
  ]
}
```

## Key Differences from Original secondscript.py

### Original (Sync) Version
```python
# Sequential processing
for agent in agents:
    agent.listen_and_act(stimulus)

# No concurrent execution
# No CEO interrupts
# No adaptive behaviors
```

### New Async Version
```python
# Concurrent processing
await world.async_run(4)

# All features:
# ✅ Concurrent agent processing
# ✅ CEO interrupt monitoring
# ✅ Adaptive meeting behaviors
# ✅ Meeting broadcasting
# ✅ Natural conversation flow
```

## Testing Different Scenarios

### 1. Test CEO Interrupts
```bash
# Run the script and press SPACEBAR during execution
python scripts/async_secondscript.py
# [Press SPACEBAR when you see conversations]
```

### 2. Test Longer Meetings
Edit the script to increase rounds:
```python
# Change from:
await world.async_run(4)
# To:
await world.async_run(8)  # Longer meeting
```

### 3. Test Different Agent Combinations
Comment out some agents to test smaller groups:
```python
# Test with just technical team
world.add_agent(cto)
world.add_agent(dev_lead)
world.add_agent(blockchain_dev)
```

### 4. Test Performance
Compare with original sync version:
```bash
# Time the async version
time python scripts/async_secondscript.py

# Time the sync version
time python scripts/secondscript.py

# Async should show better performance with concurrent processing
```

## Debugging Tips

### 1. Enable Debug Output
```python
# Add to script
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Monitor Event Bus
```python
# Check event flow
from tinytroupe.async_event_bus import get_event_bus
bus = get_event_bus()
print(f"Events in queue: {bus.event_queue.qsize()}")
```

### 3. Track Agent States
```python
# After meeting
for agent in world.agents:
    print(f"{agent.name}: {agent._actions_buffer}")
```

## Common Issues

### 1. "Warning: aioconsole not available"
- **Cause**: Optional dependency not installed
- **Impact**: CEO interrupts use fallback mode
- **Fix**: `pip install aioconsole` (optional)

### 2. No CEO Interrupt Response
- **Cause**: Terminal doesn't have focus
- **Fix**: Click on terminal window before pressing SPACEBAR

### 3. Agents Not Responding
- **Cause**: Event bus not initialized
- **Fix**: Ensure `initialize_event_bus()` is called

## Next Steps

After testing with `async_secondscript.py`, try:

1. **Full Orchestration**: `python examples/orchestrator_usage_example.py`
2. **Custom Projects**: Create your own JSON project definitions
3. **Integration**: Add async agents to your existing simulations
4. **Benchmarking**: Compare performance with sync versions

---

The `async_secondscript.py` serves as both a test script and a demonstration of all the new async capabilities. It's the best starting point for understanding how the async orchestration system works in practice.