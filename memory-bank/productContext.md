# Product Context

## Why This Project Exists
TinyTroupe is a powerful LLM-powered multiagent persona simulation library from Microsoft Research, designed for business insights and imagination enhancement. However, when using TinyTroupe for technical decision-making scenarios (like architecture reviews, technology selection, or business planning), agents would get stuck in endless polite conversations without reaching concrete decisions.

**The Core Problem**: Agents would repeatedly exchange pleasantries like:
- "We should coordinate on this"
- "Let's work together to figure it out" 
- "I'll follow up with you later"
- "Sounds good, let's sync up"

These circular conversations prevented the library from being effective for business and technical decision-making scenarios, while working perfectly for casual conversations, interviews, and creative brainstorming.

## Problems to Solve
- **Circular Conversation Loops**: Technical discussions never reach concrete decisions due to excessive politeness
- **Lack of Expert Authority**: Domain experts don't assert their expertise to guide decisions
- **Context Insensitivity**: Same behavior pattern regardless of conversation type (casual chat vs. business meeting)
- **Decision Avoidance**: Agents avoid making specific choices or recommendations
- **Vague Commitments**: Conversations end with non-actionable "coordinate later" agreements
- **Compatibility Risk**: Any solution must not break existing use cases that work well

## How It Should Work

### Adaptive Behavior Based on Context
The system should automatically detect conversation context and adapt agent behavior:

**Business Meeting Context**:
- Experts assert domain authority and make definitive technical statements
- Agents demand concrete specifics instead of accepting vague agreements
- Discussion flows toward specific decisions with clear rationale
- Circular conversations are detected and forced toward resolution

**Casual Conversation Context** (unchanged):
- Natural, friendly social interaction
- Personal experience sharing and emotional expression
- Relaxed conversational flow without forced outcomes

**Creative Brainstorming Context** (unchanged):
- Free-flowing idea generation and exploration
- Building constructively on others' suggestions
- Encouraging unconventional approaches

**Interview Context** (unchanged):
- Thoughtful, detailed responses to questions
- Professional but personal tone
- Focus on sharing relevant experiences

### Expert Authority System
When discussions enter a domain expert's specialty:
- Expert has authority to make definitive statements
- Expert can override technically incorrect suggestions
- Expert provides specific alternatives when disagreeing
- Expert guides implementation choices and sets requirements

### Decision-Forcing Mechanisms
- Automatic detection of circular conversation patterns
- Progressive escalation to force concrete decisions
- Senior/expert roles have final decision authority
- Clear documentation of decisions with implementation details

## User Experience Goals
- **Zero-Change Migration**: Existing TinyTroupe code works unchanged with `from tinytroupe.adaptive_agent import create_adaptive_agent`
- **Automatic Intelligence**: Context detection requires no manual configuration in most cases
- **Preserved Personality**: Agents retain their creativity and natural conversation abilities
- **Concrete Outcomes**: Technical discussions produce specific decisions, action items, and implementation plans
- **Expert Credibility**: Domain experts naturally assert authority and guide decisions appropriately
- **Flexible Control**: Advanced users can explicitly set context when needed for precise control