# TinyTroupe Adaptive Agent System

## Overview

This enhanced system solves the circular conversation problem in TinyTroupe while preserving all existing functionality. It automatically detects conversation context and adapts agent behavior accordingly.

## Problem Solved

**Before**: Agents in technical/business discussions would get stuck in politeness loops:
- "We should coordinate on this"
- "Let's work together to figure it out"
- "I'll follow up with you later"
- (No concrete decisions ever made)

**After**: Agents make concrete decisions and provide specific technical recommendations based on their expertise.

## Key Features

### 🎯 Context-Aware Behavior
- **Casual Conversations**: Natural, social interaction (unchanged from original)
- **Creative Brainstorming**: Free-flowing idea generation (unchanged from original) 
- **Interviews**: Thoughtful Q&A format (unchanged from original)
- **Technical Discussions**: Focused on concrete specifications and solutions
- **Business Meetings**: Decision-forcing with expert authority

### 🔧 Automatic Context Detection
The system automatically detects conversation type based on:
- Keywords and phrases used
- Number of participants
- Meeting agenda/environment hints
- Conversation patterns

### ⚡ Decision-Forcing Mechanisms
- Detects circular conversations automatically
- Forces concrete decisions when discussions loop
- Expert authority system for domain-specific decisions
- Prevents endless "coordination" discussions

## Quick Start

### Basic Usage (Drop-in Replacement)

```python
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld

# Create agents (same interface as before)
lisa = create_adaptive_agent(
    name="Lisa",
    occupation="Data scientist", 
    personality_traits=["Analytical", "Collaborative"]
)

oscar = create_adaptive_agent(
    name="Oscar",
    occupation="Software architect",
    personality_traits=["Technical", "Pragmatic"]
)

# Use exactly like original TinyTroupe
world = TinyWorld("Tech Discussion", [lisa, oscar])
world.make_everyone_accessible()

# For casual chat - works exactly like before
lisa.listen("Hi Oscar, how's your weekend going?")
world.run(3)  # Natural social conversation

# For technical decisions - now gets concrete results
lisa.listen("We need to decide on our microservices architecture. Should we use Kubernetes or Docker Swarm?")
world.run(5)  # Agents will make specific technical recommendations
```

### Advanced Usage (Explicit Context)

```python
# Set explicit meeting context for better detection
alex = create_adaptive_agent(
    name="Alex",
    occupation="Senior Blockchain Developer"
)

# Tell the agent this is a business meeting
alex.set_environment_context(
    meeting_type="technical_decision",
    agenda_items=["Platform Selection", "Implementation Timeline"],
    participant_roles=["Developer", "Architect", "Product Manager"]
)

# Agent will now use business meeting behavior
alex.listen("We need to choose between Ethereum and Hyperledger for our blockchain implementation.")
alex.act()  # Will provide specific technical recommendations
```

## Supported Context Types

### 1. Casual Conversation
- **Trigger**: Social greetings, personal topics, casual language
- **Behavior**: Friendly, natural, expressive (original TinyTroupe behavior)
- **Example**: "Hi, how are you?" → Social chat about weekend, hobbies, etc.

### 2. Creative Brainstorming  
- **Trigger**: "brainstorm", "ideas", "creative", "what if", "possibility"
- **Behavior**: Free-flowing creativity, building on ideas (original TinyTroupe behavior)
- **Example**: "Let's brainstorm AI features" → Wild creative ideas

### 3. Interview
- **Trigger**: "tell me about", interview questions, Q&A format
- **Behavior**: Thoughtful detailed responses (original TinyTroupe behavior)
- **Example**: "Describe your experience" → Professional background sharing

### 4. Technical Discussion
- **Trigger**: Technical terms, implementation details, "how to"
- **Behavior**: Specific technical details, evidence-based reasoning
- **Example**: "How should we implement caching?" → Specific tech recommendations

### 5. Business Meeting
- **Trigger**: "decision", "choose", "implement", business/technical requirements
- **Behavior**: Expert authority, concrete decisions, outcome-focused
- **Example**: "Which database should we use?" → Specific choice with rationale

## Expert Authority System

When agents are in business meeting contexts, they assert domain expertise:

```python
# Blockchain expert automatically gets authority over blockchain decisions
blockchain_dev = create_adaptive_agent(
    name="Alex",
    occupation="Senior Blockchain Developer",
    skills=["Ethereum", "Hyperledger", "Smart Contracts"]
)

# When blockchain topics arise, Alex will:
# - Make definitive technical statements
# - Override incorrect technical suggestions  
# - Provide specific implementation guidance
# - Guide architectural decisions
```

## Decision-Forcing Mechanisms

The system automatically detects and resolves circular conversations:

```python
# This type of circular discussion:
# Agent 1: "We should coordinate on this"
# Agent 2: "Yes, let's work together" 
# Agent 1: "I'll follow up with you"
# Agent 2: "Sounds good, let's sync up"

# Gets automatically interrupted with:
# "DECISION DEADLINE REACHED - You must now make a specific choice..."
```

## Compatibility with Existing Examples

All existing TinyTroupe examples work unchanged:

- ✅ `simple_chat.ipynb` - Still works exactly the same
- ✅ `interview_with_customer.ipynb` - Still works exactly the same  
- ✅ `product_brainstorming.ipynb` - Still works exactly the same
- ✅ All other examples - Unchanged behavior

## When to Use Each Mode

### Use Default Mode For:
- Social conversations between agents
- Creative brainstorming sessions
- Customer interviews
- Casual information gathering
- Personality-driven interactions

### Adaptive Mode Automatically Activates For:
- Technical decision meetings  
- Architecture reviews
- Business planning sessions
- Expert consultations
- Problem-solving discussions

## Configuration Options

### Disable Adaptive Mode
```python
agent = create_adaptive_agent("Alice", "Developer")
agent.disable_adaptive_mode()  # Uses only original TinyTroupe behavior
```

### Check Current Context
```python
print(f"Current context: {agent.get_current_context()}")
print(f"Confidence: {agent.get_context_confidence()}")
```

### Reset Context
```python
agent.reset_conversation_context()  # Start fresh
```

## Migration from Original TinyTroupe

### Zero-Change Migration
Replace imports only:
```python
# OLD:
from tinytroupe.agent import TinyPerson
from tinytroupe.examples import create_lisa_the_data_scientist

# NEW:  
from tinytroupe.adaptive_agent import create_adaptive_agent

# All existing code works unchanged
```

### Enhanced Migration
Take advantage of new features:
```python
# Add expertise domains for business meetings
agent = create_adaptive_agent(
    name="Dr. Sarah",
    occupation="Chief Technology Officer", 
    skills=["Strategic Planning", "Architecture", "Team Leadership"]
)

# Set meeting context for better behavior
agent.set_environment_context(
    meeting_type="technical_decision",
    agenda_items=["Platform Selection", "Timeline Planning"]
)
```

## Testing

Run the comprehensive test:
```bash
python test_adaptive_system.py
```

This tests:
- ✅ Casual conversations work like original
- ✅ Brainstorming works like original  
- ✅ Interviews work like original
- ✅ Business meetings make concrete decisions
- ✅ Technical discussions provide specific solutions

## Summary

The adaptive agent system provides:

1. **Backward Compatibility**: All existing TinyTroupe examples work unchanged
2. **Automatic Context Detection**: No manual configuration needed for most cases
3. **Circular Conversation Resolution**: Technical/business discussions reach concrete decisions
4. **Expert Authority**: Domain experts guide decisions in their areas
5. **Flexible Behavior**: Adapts from casual chat to structured decision-making

The system preserves the personality and creativity of original TinyTroupe while solving the circular conversation problem for technical and business scenarios.