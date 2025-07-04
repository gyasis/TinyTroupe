# Project Brief

## Project Name
**TinyTroupe Adaptive Agent System Enhancement**

## Project Overview
This project enhances Microsoft's TinyTroupe library by solving a critical problem: agents getting stuck in circular, polite conversations during technical and business discussions. The solution introduces an adaptive agent system that automatically detects conversation context and adapts agent behavior accordingly, while preserving all existing TinyTroupe functionality.

## Core Requirements
- **Primary Goal**: Eliminate circular conversation loops in technical/business discussions where agents repeatedly say "let's coordinate", "work together", "follow up" without making concrete decisions
- **Backward Compatibility**: Preserve all existing TinyTroupe examples and use cases (casual conversations, brainstorming, interviews)
- **Automatic Detection**: Context detection should require no manual configuration for most use cases
- **Expert Authority**: Domain experts should assert authority and guide decisions in their specialties
- **Decision Forcing**: Implement mechanisms to force concrete decisions when discussions become circular
- **Drop-in Replacement**: Provide enhanced functionality with minimal code changes

## Project Scope

### In Scope
- Context-aware prompt system with adaptive behavior
- Automatic conversation context detection (business meetings, technical discussions, casual chat, brainstorming, interviews)
- Expert authority system for domain-specific decision making
- Circular conversation detection and resolution mechanisms
- Comprehensive testing to ensure existing functionality preservation
- Documentation and migration guide

### Out of Scope
- Modifying core TinyTroupe architecture or breaking existing APIs
- Adding new LLM model dependencies
- Real-time collaboration features
- Integration with external business systems
- Advanced AI reasoning capabilities beyond conversation management

## Stakeholders
- **Primary User**: Researchers and developers using TinyTroupe for technical decision-making scenarios
- **Secondary Users**: Existing TinyTroupe users with casual conversation, brainstorming, and interview use cases
- **Microsoft TinyTroupe Team**: Core maintainers of the open-source library
- **Research Community**: AI simulation and multi-agent system researchers

## Success Criteria
- **Technical Success**: Agents in technical/business discussions make concrete decisions with specific rationale instead of looping in politeness
- **Compatibility Success**: All existing TinyTroupe examples (simple_chat.ipynb, interview_with_customer.ipynb, product_brainstorming.ipynb) work unchanged
- **Usability Success**: Drop-in replacement requires only import statement changes for enhanced functionality
- **Robustness Success**: Context detection works accurately across diverse conversation types with >80% confidence
- **Documentation Success**: Clear migration guide and comprehensive testing demonstrate functionality preservation