"""
Adaptive agent system that adjusts behavior based on conversation context.
Preserves existing TinyTroupe functionality while solving circular conversation problems.
"""

import os
from typing import Dict, List, Any, Optional
from tinytroupe.agent import TinyPerson
from tinytroupe.context_detection import ContextDetector, ContextType

class AdaptiveTinyPerson(TinyPerson):
    """
    Enhanced TinyPerson that adapts behavior based on conversation context.
    Maintains compatibility with existing TinyTroupe examples while solving
    circular conversation problems in technical/business discussions.
    """
    
    def __init__(self, name: str = "A Person", **kwargs):
        super().__init__(name, **kwargs)
        
        # Initialize context detection
        self.context_detector = ContextDetector()
        self.conversation_history = []
        self.round_count = 0
        self.forced_decision_count = 0
        
        # Store original prompt template path for fallback
        self.original_prompt_template = "tinyperson.mustache"
        self.adaptive_prompt_template = "tinyperson_flexible.mustache"
        
        # Track whether we should use adaptive prompting
        self.adaptive_mode_enabled = True
        
    def _get_conversation_context(self, environment_hints: Dict[str, Any] = None) -> ContextType:
        """Detect the current conversation context."""
        
        # Extract recent messages from conversation history
        recent_messages = self.conversation_history[-10:] if self.conversation_history else []
        
        # Get participant information from current environment
        participants = []
        if hasattr(self, '_accessible_agents'):
            participants = [agent.name for agent in self._accessible_agents]
        
        # Add environment hints from the current environment
        if not environment_hints:
            environment_hints = {}
        
        # Detect context
        context = self.context_detector.detect_context(
            messages=recent_messages,
            participants=participants,
            environment_hints=environment_hints
        )
        
        return context
    
    def _should_use_adaptive_prompting(self, context: ContextType) -> bool:
        """Determine if adaptive prompting should be used for this context."""
        
        if not self.adaptive_mode_enabled:
            return False
        
        # Use adaptive prompting for contexts that benefit from structured behavior
        adaptive_contexts = {
            ContextType.BUSINESS_MEETING,
            ContextType.TECHNICAL_DISCUSSION
        }
        
        return context in adaptive_contexts
    
    def _get_prompt_template_path(self, context: ContextType) -> str:
        """Get the appropriate prompt template path for the current context."""
        
        if self._should_use_adaptive_prompting(context):
            return self.adaptive_prompt_template
        else:
            return self.original_prompt_template
    
    def _enhance_configuration_for_context(self, context: ContextType) -> Dict[str, Any]:
        """Enhance the agent configuration based on detected context."""
        
        # Get base configuration
        enhanced_config = self._configuration.copy()
        
        # Get context-specific configuration
        context_config = self.context_detector.get_context_configuration()
        
        # Add interaction context to configuration
        enhanced_config["interaction_context"] = context_config
        
        # Add expertise domains if in business meeting context
        if context == ContextType.BUSINESS_MEETING:
            if "expertise_domains" not in enhanced_config:
                # Infer expertise from occupation
                occupation = enhanced_config.get("occupation", "").lower()
                seniority = enhanced_config.get("seniority_level", "").lower()
                
                expertise_domains = []
                
                # Map occupations to expertise domains
                if "developer" in occupation or "architect" in occupation:
                    expertise_domains.append({
                        "domain": "Software Architecture",
                        "competency_level": "Expert" if "senior" in seniority else "Advanced",
                        "specific_knowledge": "System design, technical implementation, best practices"
                    })
                
                if "data" in occupation and "scientist" in occupation:
                    expertise_domains.append({
                        "domain": "Data Science",
                        "competency_level": "Expert",
                        "specific_knowledge": "Machine learning, data analysis, statistical modeling"
                    })
                
                if "physician" in occupation or "doctor" in occupation:
                    expertise_domains.append({
                        "domain": "Healthcare",
                        "competency_level": "Expert",
                        "specific_knowledge": "Clinical workflows, medical standards, patient care"
                    })
                
                if "compliance" in occupation or "legal" in occupation:
                    expertise_domains.append({
                        "domain": "Compliance",
                        "competency_level": "Expert",
                        "specific_knowledge": "Regulatory requirements, risk assessment, audit procedures"
                    })
                
                if "manager" in occupation or "director" in occupation or "cto" in occupation:
                    expertise_domains.append({
                        "domain": "Business Strategy",
                        "competency_level": "Expert",
                        "specific_knowledge": "Strategic planning, resource allocation, team leadership"
                    })
                
                enhanced_config["expertise_domains"] = expertise_domains
        
        return enhanced_config
    
    def _generate_prompt(self, environment_hint: str = None) -> str:
        """Generate the agent prompt with context-aware adaptations."""
        
        # Detect current context
        environment_hints = {}
        if environment_hint:
            # Parse environment hints from the hint string
            environment_hints["environment_name"] = environment_hint
        
        context = self._get_conversation_context(environment_hints)
        
        # Get appropriate prompt template
        template_path = self._get_prompt_template_path(context)
        
        # Enhance configuration for context
        enhanced_config = self._enhance_configuration_for_context(context)
        
        # Generate prompt using parent class method with enhanced config
        original_config = self._configuration
        self._configuration = enhanced_config
        
        try:
            # Use the context-appropriate template
            prompt = super()._generate_prompt_from_template(template_path)
        finally:
            # Restore original configuration
            self._configuration = original_config
        
        return prompt
    
    def listen(self, content: str, source: "TinyPerson" = None):
        """Override listen to track conversation history and context."""
        
        # Track conversation history for context detection
        self.conversation_history.append(content)
        
        # Keep only recent history to avoid memory bloat
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-25:]
        
        # Check if we should force a decision (only in business meeting contexts)
        context = self._get_conversation_context()
        
        if self.context_detector.should_force_decision(self.conversation_history, self.round_count):
            # Inject decision-forcing prompt
            decision_prompt = self.context_detector.get_decision_forcing_prompt()
            enhanced_content = f"{content}\n\n{decision_prompt}"
            self.forced_decision_count += 1
        else:
            enhanced_content = content
        
        # Call parent listen method
        super().listen(enhanced_content, source)
    
    def act(self, environment_hint: str = None, max_content_length: int = None) -> bool:
        """Override act to track rounds and use adaptive prompting."""
        
        # Increment round count
        self.round_count += 1
        
        # Generate context-aware prompt
        if self.adaptive_mode_enabled:
            # Store original prompt generation
            original_generate_prompt = self._generate_prompt
            
            # Use our enhanced prompt generation
            self._generate_prompt = lambda: self._generate_prompt(environment_hint)
        
        try:
            # Call parent act method
            result = super().act(environment_hint, max_content_length)
        finally:
            # Restore original prompt generation if we modified it
            if self.adaptive_mode_enabled and 'original_generate_prompt' in locals():
                self._generate_prompt = original_generate_prompt
        
        return result
    
    def disable_adaptive_mode(self):
        """Disable adaptive mode to use only original TinyTroupe behavior."""
        self.adaptive_mode_enabled = False
    
    def enable_adaptive_mode(self):
        """Enable adaptive mode for context-aware behavior."""
        self.adaptive_mode_enabled = True
    
    def get_current_context(self) -> ContextType:
        """Get the currently detected context type."""
        return self.context_detector.current_context
    
    def get_context_confidence(self) -> float:
        """Get the confidence score for the current context detection."""
        return self.context_detector.context_confidence
    
    def reset_conversation_context(self):
        """Reset conversation history and context detection."""
        self.conversation_history = []
        self.round_count = 0
        self.forced_decision_count = 0
        self.context_detector.reset_context()
    
    def set_environment_context(self, meeting_type: str = None, agenda_items: List[str] = None, 
                               participant_roles: List[str] = None):
        """Explicitly set environment context hints for better context detection."""
        
        # Store environment hints for context detection
        environment_hints = {}
        
        if meeting_type:
            environment_hints["meeting_type"] = meeting_type
        
        if agenda_items:
            environment_hints["agenda_items"] = agenda_items
        
        if participant_roles:
            environment_hints["participant_roles"] = participant_roles
        
        # Update context based on explicit hints
        if environment_hints:
            context = self.context_detector.detect_context(
                messages=self.conversation_history,
                participants=participant_roles or [],
                environment_hints=environment_hints
            )
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context and conversation state."""
        
        return {
            "current_context": self.context_detector.current_context.value,
            "context_confidence": self.context_detector.context_confidence,
            "conversation_rounds": self.round_count,
            "forced_decisions": self.forced_decision_count,
            "adaptive_mode": self.adaptive_mode_enabled,
            "recent_messages": len(self.conversation_history),
            "context_history": self.context_detector.context_history[-5:]  # Last 5 context changes
        }

def create_adaptive_agent(name: str, occupation: str, personality_traits: List[str] = None, 
                         professional_interests: List[str] = None, personal_interests: List[str] = None,
                         skills: List[str] = None, **kwargs) -> AdaptiveTinyPerson:
    """
    Create an adaptive agent with enhanced context awareness.
    
    This function maintains compatibility with existing TinyTroupe agent creation
    while adding context-aware behavior for technical and business discussions.
    """
    
    agent = AdaptiveTinyPerson(name=name, **kwargs)
    
    # Set basic configuration
    agent.define("occupation", occupation)
    
    if personality_traits:
        agent.define_several("personality_traits", [{"trait": trait} for trait in personality_traits])
    
    if professional_interests:
        agent.define_several("professional_interests", [{"interest": interest} for interest in professional_interests])
    
    if personal_interests:
        agent.define_several("personal_interests", [{"interest": interest} for interest in personal_interests])
    
    if skills:
        agent.define_several("skills", [{"skill": skill} for skill in skills])
    
    return agent