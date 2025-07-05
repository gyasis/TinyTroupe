"""
Context detection system for TinyTroupe agents.
Automatically identifies conversation types and adapts agent behavior accordingly.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ContextType(Enum):
    """Enumeration of supported context types."""
    BUSINESS_MEETING = "business_meeting"
    TECHNICAL_DISCUSSION = "technical_discussion"
    CASUAL_CONVERSATION = "casual_conversation"
    CREATIVE_BRAINSTORMING = "creative_brainstorming"
    INTERVIEW = "interview"
    DEFAULT = "default"

@dataclass
class ContextSignal:
    """A signal that indicates a particular context type."""
    keywords: List[str]
    patterns: List[str]
    weight: float
    required_participants: int = 1

class ContextDetector:
    """Detects conversation context and adapts agent behavior accordingly."""
    
    def __init__(self):
        self.context_signals = self._initialize_context_signals()
        self.current_context = ContextType.DEFAULT
        self.context_confidence = 0.0
        self.context_history = []
        
    def _initialize_context_signals(self) -> Dict[ContextType, List[ContextSignal]]:
        """Initialize the signals for each context type."""
        
        return {
            ContextType.BUSINESS_MEETING: [
                ContextSignal(
                    keywords=["decision", "decide", "choose", "select", "implement", "strategy", "business", "budget", "timeline", "deadline", "deliverable", "milestone", "requirements", "specs", "architecture", "compliance", "security", "performance"],
                    patterns=[r"we need to (decide|choose|select)", r"what should we (do|implement|build)", r"which option", r"make a decision", r"business case", r"technical decision", r"architecture review"],
                    weight=1.0,
                    required_participants=2
                ),
                ContextSignal(
                    keywords=["blockchain", "FHIR", "HIPAA", "compliance", "enterprise", "scalability", "integration", "API", "framework", "platform", "consensus", "protocol"],
                    patterns=[r"technical (requirements|specifications|architecture)", r"implementation (plan|approach|strategy)", r"compliance (framework|requirements)"],
                    weight=0.8,
                    required_participants=2
                ),
                ContextSignal(
                    keywords=["expert", "authority", "domain", "specialist", "consultant", "advisor", "CTO", "director", "manager", "officer", "senior", "lead"],
                    patterns=[r"as (an expert|a specialist|the lead)", r"in my (domain|area|expertise)", r"from a (technical|business|compliance) perspective"],
                    weight=0.7,
                    required_participants=2
                )
            ],
            
            ContextType.TECHNICAL_DISCUSSION: [
                ContextSignal(
                    keywords=["technical", "implementation", "code", "system", "architecture", "design", "algorithm", "performance", "optimization", "database", "API", "framework", "library", "protocol", "specification"],
                    patterns=[r"how (does|would|should) (the|this|that) (system|code|implementation)", r"technical (approach|solution|challenge)", r"from a technical perspective"],
                    weight=1.0,
                    required_participants=1
                ),
                ContextSignal(
                    keywords=["bug", "error", "issue", "problem", "debug", "troubleshoot", "fix", "solve", "optimize", "refactor", "test", "validate"],
                    patterns=[r"(bug|error|issue|problem) (with|in)", r"how to (fix|solve|debug)", r"technical (issue|problem|challenge)"],
                    weight=0.9,
                    required_participants=1
                )
            ],
            
            ContextType.CASUAL_CONVERSATION: [
                ContextSignal(
                    keywords=["hello", "hi", "how are you", "nice to meet", "good morning", "good afternoon", "weekend", "vacation", "hobby", "family", "weather", "movie", "book", "music", "food", "travel"],
                    patterns=[r"how (are|is) (you|your)", r"nice to (meet|see|talk)", r"tell me about (yourself|your)", r"what do you (like|enjoy|do for fun)"],
                    weight=1.0,
                    required_participants=1
                ),
                ContextSignal(
                    keywords=["personal", "life", "experience", "story", "background", "interests", "hobbies", "feelings", "opinion", "thoughts"],
                    patterns=[r"in my (personal|own) (experience|opinion)", r"I (feel|think|believe) that", r"what's your (opinion|thought|view)"],
                    weight=0.8,
                    required_participants=1
                )
            ],
            
            ContextType.CREATIVE_BRAINSTORMING: [
                ContextSignal(
                    keywords=["brainstorm", "idea", "creative", "innovative", "imagine", "possibility", "potential", "concept", "vision", "inspiration", "think outside", "blue sky", "wild idea", "what if"],
                    patterns=[r"let's (brainstorm|think about|explore)", r"what if (we|you|I)", r"wild idea", r"think outside", r"blue sky", r"creative (approach|solution|idea)"],
                    weight=1.0,
                    required_participants=2
                ),
                ContextSignal(
                    keywords=["features", "product", "design", "user experience", "innovation", "new approach", "alternative", "possibility", "vision", "reimagine"],
                    patterns=[r"feature ideas", r"product (concept|vision|idea)", r"reimagine", r"think big", r"creative (features|solutions|approaches)"],
                    weight=0.9,
                    required_participants=2
                )
            ],
            
            ContextType.INTERVIEW: [
                ContextSignal(
                    keywords=["interview", "questions", "tell me about", "describe your", "experience", "background", "qualifications", "skills", "achievements", "challenges", "goals"],
                    patterns=[r"tell me about (your|yourself)", r"describe your (experience|background|role)", r"what are your (goals|challenges|skills)", r"can you elaborate", r"give me an example"],
                    weight=1.0,
                    required_participants=2
                ),
                ContextSignal(
                    keywords=["position", "role", "job", "career", "professional", "work", "responsibilities", "team", "manager", "reports", "projects"],
                    patterns=[r"in your (current|previous) (role|position|job)", r"working with (teams|clients|customers)", r"professional (experience|background)"],
                    weight=0.8,
                    required_participants=2
                )
            ]
        }
    
    def detect_context(self, messages: List[str], participants: List[str], 
                      environment_hints: Dict[str, Any] = None) -> ContextType:
        """
        Detect the conversation context based on messages and participants.
        
        Args:
            messages: List of recent messages in the conversation
            participants: List of participant names/roles
            environment_hints: Optional hints from the environment (meeting type, agenda, etc.)
        
        Returns:
            Detected context type
        """
        
        # Combine all messages into a single text for analysis
        combined_text = " ".join(messages).lower()
        
        # Calculate scores for each context type
        context_scores = {}
        
        for context_type, signals in self.context_signals.items():
            score = self._calculate_context_score(combined_text, signals, len(participants))
            context_scores[context_type] = score
        
        # Apply environment hints to boost certain contexts
        if environment_hints:
            context_scores = self._apply_environment_hints(context_scores, environment_hints)
        
        # Find the context with the highest score
        best_context = max(context_scores.items(), key=lambda x: x[1])
        self.current_context = best_context[0]
        self.context_confidence = best_context[1]
        
        # Only switch context if confidence is above threshold
        if self.context_confidence < 0.3:
            self.current_context = ContextType.DEFAULT
        
        # Track context history
        self.context_history.append({
            "context": self.current_context,
            "confidence": self.context_confidence,
            "scores": context_scores
        })
        
        return self.current_context
    
    def _calculate_context_score(self, text: str, signals: List[ContextSignal], 
                                participant_count: int) -> float:
        """Calculate the score for a specific context type."""
        
        total_score = 0.0
        
        for signal in signals:
            signal_score = 0.0
            
            # Check if minimum participants requirement is met
            if participant_count < signal.required_participants:
                continue
            
            # Score based on keyword matches
            keyword_matches = sum(1 for keyword in signal.keywords if keyword in text)
            keyword_score = (keyword_matches / len(signal.keywords)) * signal.weight
            
            # Score based on pattern matches
            pattern_matches = sum(1 for pattern in signal.patterns if re.search(pattern, text))
            pattern_score = (pattern_matches / len(signal.patterns)) * signal.weight if signal.patterns else 0
            
            # Combine keyword and pattern scores
            signal_score = max(keyword_score, pattern_score)
            total_score += signal_score
        
        # Normalize by number of signals
        return total_score / len(signals) if signals else 0.0
    
    def _apply_environment_hints(self, scores: Dict[ContextType, float], 
                               hints: Dict[str, Any]) -> Dict[ContextType, float]:
        """Apply environment hints to boost context scores."""
        
        # Boost scores based on explicit hints
        if hints.get("meeting_type") == "technical_decision":
            scores[ContextType.BUSINESS_MEETING] *= 1.5
            scores[ContextType.TECHNICAL_DISCUSSION] *= 1.3
        
        if hints.get("meeting_type") == "brainstorming":
            scores[ContextType.CREATIVE_BRAINSTORMING] *= 1.5
        
        if hints.get("meeting_type") == "interview":
            scores[ContextType.INTERVIEW] *= 1.5
        
        if hints.get("environment_name") and "chat" in hints["environment_name"].lower():
            scores[ContextType.CASUAL_CONVERSATION] *= 1.3
        
        # Boost based on agenda items
        agenda_items = hints.get("agenda_items", [])
        if agenda_items:
            agenda_text = " ".join(agenda_items).lower()
            if any(word in agenda_text for word in ["decision", "architecture", "implementation", "technical"]):
                scores[ContextType.BUSINESS_MEETING] *= 1.2
                scores[ContextType.TECHNICAL_DISCUSSION] *= 1.2
        
        # Boost based on participant roles
        participant_roles = hints.get("participant_roles", [])
        if participant_roles:
            role_text = " ".join(participant_roles).lower()
            if any(role in role_text for role in ["cto", "director", "manager", "expert", "architect"]):
                scores[ContextType.BUSINESS_MEETING] *= 1.2
        
        return scores
    
    def get_context_configuration(self) -> Dict[str, Any]:
        """Get the configuration for the current context."""
        
        context_configs = {
            ContextType.BUSINESS_MEETING: {
                "context_type": "business_meeting",
                "context_type_is_business_meeting": True,
                "context_type_is_technical_discussion": False,
                "context_type_is_casual_conversation": False,
                "context_type_is_creative_brainstorming": False,
                "context_type_is_interview": False,
                "action_limit": 12,
                "thinking_required": True,
                "authority_system_enabled": True
            },
            ContextType.TECHNICAL_DISCUSSION: {
                "context_type": "technical_discussion",
                "context_type_is_business_meeting": False,
                "context_type_is_technical_discussion": True,
                "context_type_is_casual_conversation": False,
                "context_type_is_creative_brainstorming": False,
                "context_type_is_interview": False,
                "action_limit": 10,
                "thinking_required": True,
                "authority_system_enabled": False
            },
            ContextType.CASUAL_CONVERSATION: {
                "context_type": "casual_conversation",
                "context_type_is_business_meeting": False,
                "context_type_is_technical_discussion": False,
                "context_type_is_casual_conversation": True,
                "context_type_is_creative_brainstorming": False,
                "context_type_is_interview": False,
                "action_limit": 6,
                "thinking_required": False,
                "authority_system_enabled": False
            },
            ContextType.CREATIVE_BRAINSTORMING: {
                "context_type": "creative_brainstorming",
                "context_type_is_business_meeting": False,
                "context_type_is_technical_discussion": False,
                "context_type_is_casual_conversation": False,
                "context_type_is_creative_brainstorming": True,
                "context_type_is_interview": False,
                "action_limit": 8,
                "thinking_required": False,
                "authority_system_enabled": False
            },
            ContextType.INTERVIEW: {
                "context_type": "interview",
                "context_type_is_business_meeting": False,
                "context_type_is_technical_discussion": False,
                "context_type_is_casual_conversation": False,
                "context_type_is_creative_brainstorming": False,
                "context_type_is_interview": True,
                "action_limit": 8,
                "thinking_required": True,
                "authority_system_enabled": False
            },
            ContextType.DEFAULT: {
                "context_type": "default",
                "context_type_is_business_meeting": False,
                "context_type_is_technical_discussion": False,
                "context_type_is_casual_conversation": False,
                "context_type_is_creative_brainstorming": False,
                "context_type_is_interview": False,
                "action_limit": 6,
                "thinking_required": False,
                "authority_system_enabled": False
            }
        }
        
        return context_configs.get(self.current_context, context_configs[ContextType.DEFAULT])
    
    def should_force_decision(self, messages: List[str], round_count: int) -> bool:
        """
        Determine if a decision should be forced based on conversation patterns.
        Only applies to business meeting contexts.
        """
        
        if self.current_context != ContextType.BUSINESS_MEETING:
            return False
        
        # Force decision if too many rounds without resolution
        if round_count >= 15:
            return True
        
        # Check for circular conversation patterns
        recent_text = " ".join(messages[-5:]).lower()
        circular_indicators = [
            "coordinate", "work together", "collaborate", "schedule", 
            "follow up", "touch base", "sync up", "check in"
        ]
        
        decision_indicators = [
            "decide", "choose", "select", "implement", "move forward",
            "go with", "pick", "final decision"
        ]
        
        circular_count = sum(1 for indicator in circular_indicators if indicator in recent_text)
        decision_count = sum(1 for indicator in decision_indicators if indicator in recent_text)
        
        # Force decision if lots of coordination talk but no decisions
        if circular_count >= 3 and decision_count <= 1 and round_count >= 8:
            return True
        
        return False
    
    def get_decision_forcing_prompt(self) -> str:
        """Get a prompt to force decision resolution."""
        
        return """
        DECISION DEADLINE REACHED
        
        The discussion has been going in circles without reaching concrete decisions.
        As a professional expert, you must now help force resolution:
        
        1. Identify the specific decision that needs to be made
        2. Propose a concrete solution or choice
        3. Provide clear rationale for your recommendation
        4. Call for explicit agreement or alternative proposals
        
        No more coordination talk - we need specific decisions with clear ownership and timelines.
        """
    
    def reset_context(self):
        """Reset the context detector to default state."""
        self.current_context = ContextType.DEFAULT
        self.context_confidence = 0.0
        self.context_history = []