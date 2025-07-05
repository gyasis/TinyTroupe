# Tech Context

## Technologies Used

### Core Technologies
- **Python 3.10+**: Primary development language, leveraging existing TinyTroupe requirements
- **OpenAI/Azure OpenAI**: LLM backend for agent behavior generation (inherited from TinyTroupe)
- **Mustache Templates**: Prompt templating system (pystache library)
- **JSON**: Configuration and state management
- **Regular Expressions**: Pattern matching for context detection

### Python Libraries
- **dataclasses**: Type-safe configuration and state management
- **enum**: Context type definitions
- **typing**: Type hints for better code clarity and IDE support
- **datetime**: Conversation timing and decision forcing
- **json**: Serialization for caching and state persistence

### TinyTroupe Dependencies (Inherited)
- **tinytroupe.agent**: Base TinyPerson class for agent functionality
- **tinytroupe.environment**: TinyWorld for agent environments
- **tinytroupe.openai_utils**: LLM API communication
- **tinytroupe.utils**: Utility functions for logging and configuration

## Development Setup

### Project Structure
```
tinytroupe/
├── adaptive_agent.py           # Enhanced agent with context awareness
├── context_detection.py        # Context detection and classification
├── prompts/
│   ├── tinyperson.mustache     # Original prompt template
│   └── tinyperson_flexible.mustache  # Context-adaptive prompt template
└── [existing TinyTroupe files...]

# Project root
├── test_adaptive_system.py     # Comprehensive test suite
├── ADAPTIVE_AGENT_GUIDE.md     # User documentation
└── memory-bank/               # Project documentation
```

### Installation & Setup
1. **Environment**: Use existing TinyTroupe conda environment
   ```bash
   conda activate tinytroupe
   ```

2. **Dependencies**: No additional dependencies required beyond TinyTroupe
   ```bash
   pip install -e .  # Install in editable mode for development
   ```

3. **API Keys**: Inherits TinyTroupe's OpenAI/Azure OpenAI configuration
   - Set `AZURE_OPENAI_KEY` and `AZURE_OPENAI_ENDPOINT` for Azure
   - Set `OPENAI_API_KEY` for OpenAI
   - Configure via `config.ini` files

4. **Testing**: Run comprehensive test suite
   ```bash
   python test_adaptive_system.py
   ```

### Development Workflow
1. **Code Changes**: Edit adaptive system files with immediate effect (editable install)
2. **Testing**: Use test suite to verify functionality preservation
3. **Validation**: Test with existing TinyTroupe examples to ensure compatibility
4. **Documentation**: Update memory bank files when patterns change

## Technical Constraints

### Backward Compatibility Requirements
- **No Breaking Changes**: Must work with all existing TinyTroupe examples
- **API Preservation**: AdaptiveTinyPerson must have identical interface to TinyPerson
- **Configuration Compatibility**: Must work with existing config.ini files
- **Environment Compatibility**: Must work with existing TinyWorld environments

### LLM Integration Constraints
- **Single LLM Backend**: Uses same OpenAI/Azure OpenAI as base TinyTroupe
- **Prompt Length Limits**: Must respect token limits for different models
- **API Rate Limits**: Inherits TinyTroupe's rate limiting and caching mechanisms
- **Content Filtering**: Must work with Azure OpenAI content filters when enabled

### Performance Constraints
- **Context Detection Speed**: Must be fast enough for real-time conversation flow
- **Memory Usage**: Conversation history limited to prevent memory bloat
- **Prompt Generation**: Template switching must be efficient
- **Confidence Calculation**: Context detection confidence must be computed quickly

### Architectural Constraints
- **No Core Modifications**: Cannot modify existing TinyTroupe core classes
- **Composition Only**: Enhancement through composition, not inheritance
- **Optional Enhancement**: System must be opt-in, not mandatory
- **Fallback Behavior**: Must gracefully fallback to original behavior when uncertain

## Dependencies

### Direct Dependencies
```python
# Core adaptive system dependencies
from tinytroupe.agent import TinyPerson        # Base agent class
from tinytroupe.environment import TinyWorld   # Environment management
from typing import Dict, List, Any, Optional   # Type hints
from dataclasses import dataclass             # Configuration classes
from enum import Enum                        # Context type definitions
from datetime import datetime, timedelta     # Timing and decision forcing
import re                                   # Pattern matching
import json                                 # Serialization
```

### Indirect Dependencies (via TinyTroupe)
- **OpenAI/Azure OpenAI SDK**: LLM API communication
- **pystache**: Mustache template rendering
- **logging**: System logging and debugging
- **os**: Environment variable access
- **configparser**: Configuration file parsing

### Development Dependencies
- **pytest**: Unit testing framework (for future test expansion)
- **jupyter**: For running example notebooks
- **pandas**: Data manipulation in examples
- **matplotlib**: Visualization in examples

### Optional Dependencies
- **memory profiling tools**: For performance optimization
- **code coverage tools**: For test coverage analysis
- **static analysis tools**: For code quality assurance

## Configuration Management

### Context Detection Configuration
```python
# Default thresholds and settings
CONFIDENCE_THRESHOLD = 0.3
MAX_CONVERSATION_HISTORY = 50
DECISION_FORCING_THRESHOLD = 5
MAX_DISCUSSION_ROUNDS = 15
```

### Prompt Template Configuration
```python
# Template selection logic
ORIGINAL_TEMPLATE = "tinyperson.mustache"
ADAPTIVE_TEMPLATE = "tinyperson_flexible.mustache"
```

### Integration with TinyTroupe Config
- Uses existing `config.ini` system for LLM settings
- Adds adaptive-specific settings as needed
- Maintains compatibility with existing configurations