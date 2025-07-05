"""
AsyncAdaptiveTinyPerson - Combines async capabilities with adaptive behavior

This module provides AsyncAdaptiveTinyPerson which extends both AsyncTinyPerson 
and AdaptiveTinyPerson to offer:
- Concurrent async execution 
- Context-aware adaptive behavior
- CEO interrupt handling
- Meeting intelligence and wrap-up logic
"""

import asyncio
import logging
import threading
from typing import Dict, List, Any, Optional, Union

from tinytroupe.async_agent import AsyncTinyPerson
from tinytroupe.adaptive_agent import AdaptiveTinyPerson
from tinytroupe.context_detection import ContextDetector, ContextType
from tinytroupe.async_event_bus import get_event_bus, EventType, Event, CEOInterruptEvent

logger = logging.getLogger("tinytroupe")


class AsyncAdaptiveTinyPerson(AsyncTinyPerson):
    """
    Combines AsyncTinyPerson and AdaptiveTinyPerson capabilities.
    
    Features from AsyncTinyPerson:
    - Concurrent async execution with async_listen(), async_act(), async_listen_and_act()
    - CEO interrupt handling and event bus integration
    - Thread-safe state management
    
    Features from AdaptiveTinyPerson:
    - Context-aware behavior (business meetings, technical discussions)
    - Meeting wrap-up and conclusion logic
    - Expert authority in domain areas
    - RECALL enhancement to prevent circular conversations
    - Decision forcing to prevent endless coordination
    """
    
    def __init__(self, name: str = "An Adaptive Async Person", **kwargs):
        # Initialize AsyncTinyPerson (which handles TinyPerson initialization)
        super().__init__(name, **kwargs)
        
        # Add AdaptiveTinyPerson attributes
        self.context_detector = ContextDetector()
        self.conversation_history = []
        self.round_count = 0
        self.forced_decision_count = 0
        
        # Store original prompt template path for fallback
        self.original_prompt_template = "tinyperson.mustache"
        self.adaptive_prompt_template = "tinyperson_flexible.mustache"
        
        # Track whether we should use adaptive prompting
        self.adaptive_mode_enabled = True
        
        # Thread safety for adaptive features
        self._adaptive_lock = asyncio.Lock()
        
        logger.debug(f"Created AsyncAdaptiveTinyPerson: {self.name}")
    
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
    
    async def async_listen(self, content: str, source: "TinyPerson" = None, max_content_length=None):
        """
        Async version of listen with adaptive behavior tracking.
        
        Args:
            content: Message content to listen to
            source: Source agent/entity
            max_content_length: Maximum content length
            
        Returns:
            Result from listening to the content
        """
        async with self._adaptive_lock:
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
        
        # Call parent async_listen method with enhanced content
        return await super().async_listen(enhanced_content, source, max_content_length)
    
    async def async_act(self, until_done=True, n=None, return_actions=False,
                       max_content_length=None, current_round=None, total_rounds=None):
        """
        Async version of act with adaptive prompting and meeting management.
        
        Args:
            until_done: Whether to act until done
            n: Number of actions to take
            return_actions: Whether to return actions
            max_content_length: Maximum content length
            current_round: Current simulation round
            total_rounds: Total simulation rounds
            
        Returns:
            Result from acting
        """
        async with self._adaptive_lock:
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
                    logger.debug(f"[ASYNC] {self.name} Round {current_round}/{total_rounds} - Adding wrap-up prompt")
                elif current_round == total_rounds:  # Final round
                    # Add meeting conclusion prompt  
                    environment_hint += " - MEETING CONCLUSION: Provide a meeting recap with key decisions, action items, and next steps. Be specific about who does what."
                    logger.debug(f"[ASYNC] {self.name} Round {current_round}/{total_rounds} - Adding conclusion prompt")
            
            # Generate context-aware prompt
            if self.adaptive_mode_enabled and environment_hint:
                # Temporarily update the prompt with meeting directives
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
            # Call parent async_act method
            result = await super().async_act(
                until_done=until_done, 
                n=n, 
                return_actions=return_actions,
                max_content_length=max_content_length, 
                current_round=current_round, 
                total_rounds=total_rounds
            )
            
            return result
            
        finally:
            # Clean up any temporary configuration changes
            async with self._adaptive_lock:
                if self.adaptive_mode_enabled and environment_hint:
                    if "MEETING WRAP-UP" in environment_hint or "MEETING CONCLUSION" in environment_hint:
                        # Remove temporary meeting directives
                        self._configuration.pop("meeting_directive", None)
                        self._configuration.pop("is_final_round", None)
                        self._configuration.pop("is_wrap_up_round", None)
                        self._configuration.pop("take_meeting_lead", None)
                        # Regenerate clean prompt for next round
                        self.reset_prompt()
    
    async def async_listen_and_act(self, speech: str, return_actions=False, max_content_length=None):
        """
        Async version of listen_and_act with adaptive behavior.
        
        Args:
            speech: Speech content to listen to and respond to
            return_actions: Whether to return actions
            max_content_length: Maximum content length
            
        Returns:
            Result from listening and acting
        """
        # First listen with adaptive tracking
        await self.async_listen(speech, max_content_length=max_content_length)
        
        # Then act with adaptive prompting
        return await self.async_act(return_actions=return_actions, max_content_length=max_content_length)
    
    # Adaptive behavior control methods
    def disable_adaptive_mode(self):
        """Disable adaptive mode to use only original TinyTroupe behavior."""
        self.adaptive_mode_enabled = False
        logger.debug(f"[{self.name}] Adaptive mode disabled")
    
    def enable_adaptive_mode(self):
        """Enable adaptive mode for context-aware behavior."""
        self.adaptive_mode_enabled = True
        logger.debug(f"[{self.name}] Adaptive mode enabled")
    
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
        logger.debug(f"[{self.name}] Conversation context reset")
    
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
            logger.debug(f"[{self.name}] Environment context set: {context.value}")
    
    async def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context and conversation state."""
        
        return {
            "agent_name": self.name,
            "agent_type": "AsyncAdaptiveTinyPerson",
            "current_context": self.context_detector.current_context.value,
            "context_confidence": self.context_detector.context_confidence,
            "conversation_rounds": self.round_count,
            "forced_decisions": self.forced_decision_count,
            "adaptive_mode": self.adaptive_mode_enabled,
            "recent_messages": len(self.conversation_history),
            "context_history": self.context_detector.context_history[-5:],  # Last 5 context changes
            "async_state": await self.get_async_state()
        }
    
    # Override CEO interrupt handling to include adaptive context
    async def _process_ceo_interrupt(self):
        """Process CEO interrupt with adaptive context awareness."""
        
        # Get current adaptive context
        context = self.get_current_context()
        
        # Add context information to interrupt processing
        logger.info(f"[{self.name}] Processing CEO interrupt in {context.value} context")
        
        # Call parent CEO interrupt processing
        await super()._process_ceo_interrupt()
        
        # Reset conversation state if needed based on interrupt
        if self._last_interrupt_message and "reset" in self._last_interrupt_message.lower():
            self.reset_conversation_context()
            logger.info(f"[{self.name}] Conversation context reset due to CEO interrupt")


# Convenience function for creating async adaptive agents
def create_async_adaptive_agent(name: str, occupation: str, personality_traits: List[str] = None, 
                               professional_interests: List[str] = None, personal_interests: List[str] = None,
                               skills: List[str] = None, years_experience: str = None, **kwargs) -> AsyncAdaptiveTinyPerson:
    """
    Create an async adaptive agent with enhanced context awareness and async capabilities.
    
    This function maintains compatibility with existing TinyTroupe agent creation
    while adding both async execution and context-aware behavior.
    
    Args:
        name: Agent name
        occupation: Job title and role description
        personality_traits: List of personality characteristics
        professional_interests: List of work-related interests
        personal_interests: List of personal hobbies and interests
        skills: List of technical and professional skills
        years_experience: Experience level (e.g., "10+ years", "5-8 years")
        **kwargs: Additional parameters passed to AsyncAdaptiveTinyPerson constructor
    
    Returns:
        Configured AsyncAdaptiveTinyPerson instance
    """
    
    agent = AsyncAdaptiveTinyPerson(name=name, **kwargs)
    
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
    
    logger.info(f"Created AsyncAdaptiveTinyPerson: {name} ({occupation})")
    return agent


# Convenience function for running multiple async adaptive agents
async def run_async_adaptive_agents_concurrently(agents: List[AsyncAdaptiveTinyPerson], 
                                                task_prompts: List[str], **kwargs):
    """
    Run multiple AsyncAdaptiveTinyPerson agents concurrently on different tasks.
    
    Args:
        agents: List of AsyncAdaptiveTinyPerson instances
        task_prompts: List of task prompts (one per agent)
        **kwargs: Additional arguments passed to async_listen_and_act
    
    Returns:
        Dict mapping agent names to their results
    """
    logger.info(f"Running {len(agents)} async adaptive agents concurrently")
    
    # Create tasks for each agent
    tasks = {}
    for agent, prompt in zip(agents, task_prompts):
        task = asyncio.create_task(agent.async_listen_and_act(prompt, **kwargs))
        tasks[agent.name] = task
    
    # Wait for all agents to complete
    results = {}
    for agent_name, task in tasks.items():
        try:
            result = await task
            results[agent_name] = result
            logger.info(f"Async adaptive agent '{agent_name}' completed successfully")
        except Exception as error:
            logger.error(f"Async adaptive agent '{agent_name}' failed: {error}")
            results[agent_name] = None
    
    return results