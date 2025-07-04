# System Patterns

## System Architecture

### Core Components
The adaptive agent system extends TinyTroupe with three main components working together:

```
┌─────────────────────────────────────────────────────────────┐
│                    Adaptive Agent System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Context        │  │  Adaptive       │  │  Flexible       │ │
│  │  Detection      │◄─┤  Agent          │◄─┤  Prompt         │ │
│  │  System         │  │  System         │  │  System         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Original TinyTroupe                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  TinyPerson     │  │  TinyWorld      │  │  Original       │ │
│  │  (Base Agent)   │  │  (Environment)  │  │  Prompts        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow
1. **AdaptiveTinyPerson** receives conversation input
2. **ContextDetector** analyzes message patterns, keywords, and participants
3. **Context Configuration** determines appropriate behavior mode
4. **Prompt Selection** chooses between `tinyperson.mustache` (original) or `tinyperson_flexible.mustache` (adaptive)
5. **Enhanced Configuration** adds expertise domains and authority levels for business contexts
6. **Agent Response** generated using context-appropriate prompt and configuration

## Key Technical Decisions

### 1. Composition Over Inheritance
- **Decision**: Extend TinyPerson through composition rather than modifying core classes
- **Rationale**: Preserves backward compatibility and allows gradual adoption
- **Implementation**: `AdaptiveTinyPerson` wraps and enhances `TinyPerson` functionality

### 2. Dual Prompt System
- **Decision**: Create separate prompt templates rather than modifying the original
- **Rationale**: Maintains original behavior for existing use cases while enabling new capabilities
- **Implementation**: 
  - `tinyperson.mustache` (original) for casual/creative/interview contexts
  - `tinyperson_flexible.mustache` (adaptive) for business/technical contexts

### 3. Automatic Context Detection
- **Decision**: Use keyword/pattern analysis rather than requiring manual context setting
- **Rationale**: Enables zero-configuration usage while allowing explicit control when needed
- **Implementation**: Confidence-based scoring system with fallback to default behavior

### 4. Expert Authority Through Configuration
- **Decision**: Implement expertise through enhanced agent configuration rather than new agent types
- **Rationale**: Leverages existing TinyTroupe persona system while adding domain authority
- **Implementation**: Dynamic expertise domain injection based on occupation and context

### 5. Drop-in Replacement Strategy
- **Decision**: Maintain identical interface to original TinyPerson
- **Rationale**: Enables seamless migration with minimal code changes
- **Implementation**: `create_adaptive_agent()` function mirrors original agent creation patterns

## Design Patterns in Use

### Strategy Pattern (Context-Aware Behavior)
```python
class ContextDetector:
    def detect_context(self, messages, participants, hints) -> ContextType
    
    def get_context_configuration(self) -> Dict[str, Any]
        # Returns different configurations based on detected context
```

### Template Method Pattern (Adaptive Prompting)
```python
class AdaptiveTinyPerson(TinyPerson):
    def _generate_prompt(self, environment_hint=None) -> str:
        context = self._get_conversation_context()
        template_path = self._get_prompt_template_path(context)
        enhanced_config = self._enhance_configuration_for_context(context)
        # Generate prompt using appropriate template and configuration
```

### Observer Pattern (Conversation Tracking)
```python
def listen(self, content: str, source=None):
    self.conversation_history.append(content)  # Track for context detection
    # Check for decision forcing triggers
    super().listen(enhanced_content, source)
```

### Factory Pattern (Agent Creation)
```python
def create_adaptive_agent(name, occupation, **kwargs) -> AdaptiveTinyPerson:
    # Creates properly configured adaptive agents
    # Maintains interface compatibility with original patterns
```

### State Pattern (Meeting Phases)
```python
class ContextDetector:
    current_context: ContextType
    context_confidence: float
    
    def should_force_decision(self, messages, round_count) -> bool:
        # Different behavior based on current context state
```

## Component Relationships

### Context Detection Dependencies
- **Input**: Recent messages, participant roles, environment hints
- **Processing**: Keyword analysis, pattern matching, confidence scoring
- **Output**: Context type with confidence level
- **Triggers**: Conversation updates, round progression, explicit hints

### Adaptive Agent Dependencies
- **Inherits**: TinyPerson (full backward compatibility)
- **Uses**: ContextDetector for behavior adaptation
- **Manages**: Conversation history, round counting, forced decision tracking
- **Provides**: Enhanced configuration, context-aware prompting

### Prompt System Dependencies
- **Original Prompt**: Used for casual, creative, interview contexts
- **Flexible Prompt**: Used for business meeting, technical discussion contexts
- **Configuration**: Enhanced with expertise domains, authority levels, context flags
- **Selection**: Based on context detection confidence and type

### Integration Points
- **TinyWorld Environment**: Unchanged, works with both original and adaptive agents
- **TinyPerson API**: Fully preserved, adaptive agents are drop-in replacements
- **Example Scripts**: Work unchanged with adaptive agents
- **Prompt Templates**: Both original and flexible templates use same variable structure