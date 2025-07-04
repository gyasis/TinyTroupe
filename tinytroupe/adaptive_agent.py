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
            
            # Add enhanced RECALL instructions for business meetings
            enhanced_config["recall_before_questions"] = True
            enhanced_config["memory_check_instructions"] = self._get_memory_check_instructions(occupation)
        
        return enhanced_config
    
    def _get_memory_check_instructions(self, occupation: str) -> str:
        """Generate role-specific memory check instructions for business meetings."""
        
        base_instructions = """
CRITICAL MEMORY CHECK PROTOCOL:
Before asking ANY question about tasks, assignments, or topics, you MUST:

1. THINK about what you want to ask
2. RECALL recent discussions about this topic (use keywords like "hospital contacts", "user testing", "assignments", etc.)
3. THINK about what you found in your memory
4. Only ask the question if the information is truly missing or needs clarification

If you find that someone already volunteered or committed to handle a task, acknowledge this and move the conversation forward instead of repeating the question.
"""
        
        # Add role-specific guidance
        occupation_lower = occupation.lower()
        
        if "manager" in occupation_lower or "director" in occupation_lower:
            role_specific = """
As a project manager/leader, your role is to:
- Track what has been decided and assigned
- Move the agenda forward when topics are resolved
- Summarize progress and redirect to next agenda items
- Say things like: "Great! [Task] is covered by [Person]. Let's move to [Next Topic]."
"""
        elif "developer" in occupation_lower or "architect" in occupation_lower:
            role_specific = """
As a technical expert, your role is to:
- Provide specific technical recommendations
- Ask clarifying questions about implementation details
- Recall previous technical decisions to build upon them
"""
        elif "compliance" in occupation_lower or "legal" in occupation_lower:
            role_specific = """
As a compliance expert, your role is to:
- Assert regulatory requirements clearly
- Recall relevant compliance standards and constraints
- Provide definitive guidance on regulatory matters
"""
        else:
            role_specific = """
In your professional role, focus on:
- Contributing your domain expertise effectively
- Building upon previous discussion points
- Avoiding repetition of already-covered topics
"""
        
        return base_instructions + "\n" + role_specific
    
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
        
        # Add environment hint to configuration if it contains meeting directives
        if environment_hint and ("MEETING WRAP-UP" in environment_hint or "MEETING CONCLUSION" in environment_hint):
            enhanced_config["meeting_directive"] = environment_hint
            enhanced_config["is_final_round"] = "MEETING CONCLUSION" in environment_hint
            enhanced_config["is_wrap_up_round"] = "MEETING WRAP-UP" in environment_hint
        
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
    
    def act(self, until_done=True, n=None, return_actions=False,
            max_content_length=None, current_round=None, total_rounds=None):
        """Override act to track rounds and use adaptive prompting."""
        
        # Increment round count
        self.round_count += 1
        
        # Store environment context for adaptive behavior
        environment_hint = f"Round {current_round}/{total_rounds}" if current_round and total_rounds else None
        
        # Check if this is a business meeting nearing completion
        # Only wrap up if total rounds >= 7 (never wrap up short meetings)
        if (self.adaptive_mode_enabled and current_round and total_rounds and total_rounds >= 7 and
            self.context_detector.current_context == ContextType.BUSINESS_MEETING):
            
            if current_round == total_rounds - 1:  # Second to last round
                # Add meeting wrap-up warning
                environment_hint += " - MEETING WRAP-UP: This meeting has 1 minute left. Ask everyone for final considerations before we conclude."
                print(f"DEBUG: {self.name} Round {current_round}/{total_rounds} - Adding wrap-up prompt")
            elif current_round == total_rounds:  # Final round
                # Add meeting conclusion prompt  
                environment_hint += " - MEETING CONCLUSION: Provide a meeting recap with key decisions, action items, and next steps. Be specific about who does what."
                print(f"DEBUG: {self.name} Round {current_round}/{total_rounds} - Adding conclusion prompt")
        
        # Generate context-aware prompt
        if self.adaptive_mode_enabled and environment_hint:
            # Temporarily update the prompt with meeting directives
            original_prompt_path = self._prompt_template_path
            
            # Force regeneration of system message with environment hints
            if "MEETING WRAP-UP" in environment_hint or "MEETING CONCLUSION" in environment_hint:
                # Add the directive to current context
                if "project manager" in (self._configuration.get("occupation", "") or "").lower():
                    # Project managers take lead in wrap-up
                    self._configuration["take_meeting_lead"] = True
                
                # Force prompt regeneration with new context
                self._configuration["meeting_directive"] = environment_hint
                self._configuration["is_final_round"] = "MEETING CONCLUSION" in environment_hint
                self._configuration["is_wrap_up_round"] = "MEETING WRAP-UP" in environment_hint
                self.reset_prompt()  # This regenerates the system message
        
        try:
            # Call parent act method with correct signature
            result = super().act(until_done=until_done, n=n, return_actions=return_actions,
                               max_content_length=max_content_length, current_round=current_round, 
                               total_rounds=total_rounds)
        finally:
            # Clean up any temporary configuration changes
            if self.adaptive_mode_enabled and environment_hint:
                if "MEETING WRAP-UP" in environment_hint or "MEETING CONCLUSION" in environment_hint:
                    # Remove temporary meeting directives
                    self._configuration.pop("meeting_directive", None)
                    self._configuration.pop("is_final_round", None)
                    self._configuration.pop("is_wrap_up_round", None)
                    self._configuration.pop("take_meeting_lead", None)
                    # Regenerate clean prompt for next round
                    self.reset_prompt()
        
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
                         skills: List[str] = None, years_experience: str = None, **kwargs) -> AdaptiveTinyPerson:
    """
    Create an adaptive agent with enhanced context awareness.
    
    This function maintains compatibility with existing TinyTroupe agent creation
    while adding context-aware behavior for technical and business discussions.
    
    Args:
        name: Agent name
        occupation: Job title and role description
        personality_traits: List of personality characteristics
        professional_interests: List of work-related interests
        personal_interests: List of personal hobbies and interests
        skills: List of technical and professional skills
        years_experience: Experience level (e.g., "10+ years", "5-8 years")
                         If not provided, will be inferred from occupation title
        **kwargs: Additional parameters passed to TinyPerson constructor
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
    
    # Set experience information for adaptive prompts
    if years_experience:
        agent.define("years_experience", years_experience)
        # Also infer seniority level from occupation and experience
        occupation_lower = occupation.lower()
        if "senior" in occupation_lower or "lead" in occupation_lower or "principal" in occupation_lower:
            agent.define("seniority_level", "Senior")
        elif "junior" in occupation_lower or "associate" in occupation_lower:
            agent.define("seniority_level", "Junior")
        elif "director" in occupation_lower or "manager" in occupation_lower or "head" in occupation_lower:
            agent.define("seniority_level", "Leadership")
        elif "chief" in occupation_lower or "cto" in occupation_lower or "ceo" in occupation_lower:
            agent.define("seniority_level", "Executive")
        else:
            agent.define("seniority_level", "Mid-level")
    else:
        # Infer from occupation if no experience provided
        occupation_lower = occupation.lower()
        if "senior" in occupation_lower:
            agent.define("years_experience", "8+ years")
            agent.define("seniority_level", "Senior")
        elif "junior" in occupation_lower:
            agent.define("years_experience", "1-3 years") 
            agent.define("seniority_level", "Junior")
        elif "lead" in occupation_lower or "principal" in occupation_lower:
            agent.define("years_experience", "10+ years")
            agent.define("seniority_level", "Senior")
        elif "director" in occupation_lower or "manager" in occupation_lower:
            agent.define("years_experience", "12+ years")
            agent.define("seniority_level", "Leadership")
        elif "chief" in occupation_lower or "cto" in occupation_lower:
            agent.define("years_experience", "15+ years")
            agent.define("seniority_level", "Executive")
        else:
            agent.define("years_experience", "5+ years")
            agent.define("seniority_level", "Mid-level")
    
    return agent