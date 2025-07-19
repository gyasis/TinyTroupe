"""
Enhanced environment for business meeting simulations with decision-making capabilities.
Extends TinyWorld to support structured decision processes and expert authority.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson

logger = logging.getLogger("tinytroupe")

class BusinessDecision:
    """Represents a business decision with all its context and outcomes."""
    
    def __init__(self, topic: str, urgency: str = "medium", business_impact: str = "medium"):
        self.id = f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.topic = topic
        self.urgency = urgency  # low, medium, high, critical
        self.business_impact = business_impact  # low, medium, high, critical
        self.status = "open"  # open, debating, resolved, implemented
        self.created_at = datetime.now()
        self.options = []
        self.discussion_history = []
        self.final_decision = None
        self.rationale = ""
        self.action_items = []
        self.success_criteria = []
        self.risks = []
        
    def add_option(self, option: Dict[str, Any], proposed_by: str):
        """Add a decision option with proposer info."""
        option_entry = {
            "id": len(self.options) + 1,
            "option": option,
            "proposed_by": proposed_by,
            "proposed_at": datetime.now(),
            "expert_evaluations": []
        }
        self.options.append(option_entry)
        
    def add_expert_evaluation(self, option_id: int, expert: str, evaluation: Dict[str, Any]):
        """Add expert evaluation of a specific option."""
        for option in self.options:
            if option["id"] == option_id:
                option["expert_evaluations"].append({
                    "expert": expert,
                    "evaluation": evaluation,
                    "evaluated_at": datetime.now()
                })
                break
                
    def set_final_decision(self, decision: Dict[str, Any], decided_by: str, rationale: str):
        """Set the final decision with full context."""
        self.final_decision = decision
        self.rationale = rationale
        self.status = "resolved"
        self.decided_by = decided_by
        self.decided_at = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary for logging/storage."""
        return {
            "id": self.id,
            "topic": self.topic,
            "urgency": self.urgency,
            "business_impact": self.business_impact,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "options": self.options,
            "final_decision": self.final_decision,
            "rationale": self.rationale,
            "action_items": self.action_items,
            "success_criteria": self.success_criteria,
            "risks": self.risks
        }

class BusinessMeetingWorld(TinyWorld):
    """Enhanced environment for business meetings with decision-making capabilities."""
    
    def __init__(self, name: str = "Business Meeting", agents: List[TinyPerson] = None, 
                 meeting_type: str = "technical_decision", 
                 agenda_items: List[str] = None,
                 max_discussion_rounds: int = 15,
                 decision_forcing_threshold: int = 5):
        
        super().__init__(name, agents or [])
        
        self.meeting_type = meeting_type
        self.agenda_items = agenda_items or []
        self.current_agenda_item = 0
        self.max_discussion_rounds = max_discussion_rounds
        self.decision_forcing_threshold = decision_forcing_threshold
        
        # Decision tracking
        self.active_decisions: Dict[str, BusinessDecision] = {}
        self.completed_decisions: List[BusinessDecision] = []
        self.decision_history = []
        
        # Meeting state
        self.meeting_phase = "opening"  # opening, discussion, decision, action_planning, closing
        self.discussion_rounds = 0
        self.circular_discussion_detector = []
        self.last_substantial_progress = 0
        
        # Expert authority tracking
        self.expert_domains = self._map_expert_domains()
        
    def _map_expert_domains(self) -> Dict[str, List[str]]:
        """Map each agent to their domains of expertise."""
        expert_map = {}
        for agent in self.agents:
            # Extract expertise domains from agent definition
            if hasattr(agent, '_configuration') and 'expertise_domains' in agent._configuration:
                domains = agent._configuration['expertise_domains']
                expert_map[agent.name] = [d.get('domain', '') for d in domains]
            else:
                # Fallback: infer from occupation
                expert_map[agent.name] = [agent._configuration.get('occupation', 'General')]
        return expert_map
        
    def detect_decision_point(self, recent_messages: List[str]) -> Optional[str]:
        """Detect if a decision point has been reached based on conversation patterns."""
        
        # Increase discussion round counter
        self.discussion_rounds += 1
        
        # Check for circular discussion patterns
        decision_indicators = [
            "we need to decide",
            "what should we do",
            "which option",
            "make a choice",
            "move forward with",
            "implement",
            "let's go with"
        ]
        
        circular_indicators = [
            "coordinate",
            "work together",
            "collaborate",
            "schedule",
            "follow up",
            "touch base"
        ]
        
        recent_text = " ".join(recent_messages[-3:]).lower()
        
        # Force decision if discussion is circular
        circular_count = sum(1 for indicator in circular_indicators if indicator in recent_text)
        decision_count = sum(1 for indicator in decision_indicators if indicator in recent_text)
        
        if (self.discussion_rounds >= self.decision_forcing_threshold and 
            circular_count > decision_count):
            return "Circular discussion detected - forcing decision point"
            
        # Force decision if max rounds reached
        if self.discussion_rounds >= self.max_discussion_rounds:
            return "Maximum discussion rounds reached - forcing decision"
            
        # Detect explicit decision requests
        if decision_count >= 2:
            return "Explicit decision request detected"
            
        return None
        
    def initiate_decision_process(self, topic: str, urgency: str = "medium", 
                                business_impact: str = "medium") -> BusinessDecision:
        """Initiate a structured decision-making process."""
        
        decision = BusinessDecision(topic, urgency, business_impact)
        self.active_decisions[decision.id] = decision
        
        # Change meeting phase
        self.meeting_phase = "decision"
        
        # Notify all agents about the decision point
        self._broadcast_decision_point(decision)
        
        logger.info(f"Decision process initiated: {topic}")
        return decision
        
    def _broadcast_decision_point(self, decision: BusinessDecision):
        """Broadcast decision point to all agents with their authority context."""
        
        for agent in self.agents:
            # Determine agent's authority for this decision
            authority_context = self._get_agent_authority_context(agent, decision.topic)
            
            decision_message = {
                "type": "DECISION_POINT",
                "decision_id": decision.id,
                "topic": decision.topic,
                "urgency": decision.urgency,
                "business_impact": decision.business_impact,
                "authority_context": authority_context,
                "phase": "option_identification"
            }
            
            agent.listen(f"""
            DECISION POINT REACHED: {decision.topic}
            
            As a {agent._configuration.get('occupation', 'professional')} with expertise in {', '.join(self.expert_domains.get(agent.name, ['general']))}, 
            you must now participate in a structured decision-making process.
            
            AUTHORITY LEVEL: {authority_context['level']}
            YOUR ROLE: {authority_context['role']}
            
            REQUIRED ACTION: Propose specific, implementable options with technical details.
            NO VAGUE PROPOSALS - provide concrete specifications, timelines, and resource requirements.
            
            If this decision involves your area of expertise, assert your authority and guide the decision.
            If others propose technically incorrect solutions in your domain, override them with specific corrections.
            """)
            
    def _get_agent_authority_context(self, agent: TinyPerson, decision_topic: str) -> Dict[str, str]:
        """Determine an agent's authority level for a specific decision."""
        
        agent_domains = self.expert_domains.get(agent.name, [])
        occupation = agent._configuration.get('occupation', '').lower()
        seniority = agent._configuration.get('seniority_level', 'junior').lower()
        
        # Determine authority level based on expertise and decision topic
        topic_lower = decision_topic.lower()
        
        authority_level = "contributor"
        role = "Provide input and feedback"
        
        # Check for domain expertise match
        domain_match = any(domain.lower() in topic_lower for domain in agent_domains)
        
        if domain_match:
            if "expert" in seniority or "senior" in seniority or "director" in seniority:
                authority_level = "decision_maker"
                role = "Make authoritative decisions in your domain"
            else:
                authority_level = "technical_authority"
                role = "Provide expert technical guidance"
                
        # Special roles get decision authority regardless of topic
        if any(title in occupation for title in ["cto", "director", "manager", "officer"]):
            authority_level = "decision_maker"
            role = "Make final business decisions"
            
        return {
            "level": authority_level,
            "role": role,
            "domains": agent_domains
        }
        
    def force_decision_resolution(self, decision_id: str) -> Optional[BusinessDecision]:
        """Force resolution of a decision that's taking too long."""
        
        if decision_id not in self.active_decisions:
            return None
            
        decision = self.active_decisions[decision_id]
        
        # Find the most senior expert for this decision
        decision_maker = self._identify_decision_maker(decision)
        
        # Force the decision maker to make a final choice
        if decision_maker:
            decision_maker.listen(f"""
            DECISION DEADLINE REACHED: {decision.topic}
            
            As the senior authority for this decision, you must now make the final choice.
            
            AVAILABLE OPTIONS: {len(decision.options)} options have been proposed
            DISCUSSION ROUNDS: {self.discussion_rounds} rounds completed
            
            REQUIRED ACTION: 
            1. Choose one specific option or propose a hybrid solution
            2. Provide clear rationale for your decision
            3. Define specific action items with owners and deadlines
            4. Identify success criteria and risk mitigation plans
            
            Make your decision now - the meeting cannot proceed without resolution.
            """)
            
        return decision
        
    def _identify_decision_maker(self, decision: BusinessDecision) -> Optional[TinyPerson]:
        """Identify who should make the final decision based on expertise and seniority."""
        
        # Score each agent based on expertise relevance and seniority
        scored_agents = []
        
        for agent in self.agents:
            score = 0
            
            # Score based on domain expertise
            agent_domains = self.expert_domains.get(agent.name, [])
            for domain in agent_domains:
                if domain.lower() in decision.topic.lower():
                    score += 10
                    
            # Score based on seniority
            seniority = agent._configuration.get('seniority_level', '').lower()
            if 'executive' in seniority or 'cto' in seniority:
                score += 8
            elif 'director' in seniority or 'senior' in seniority:
                score += 5
            elif 'manager' in seniority:
                score += 3
                
            scored_agents.append((agent, score))
            
        # Return the highest-scoring agent
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0] if scored_agents else None
        
    def complete_decision(self, decision_id: str, final_choice: Dict[str, Any], 
                         decided_by: str, rationale: str) -> bool:
        """Complete a decision and move it to completed status."""
        
        if decision_id not in self.active_decisions:
            return False
            
        decision = self.active_decisions[decision_id]
        decision.set_final_decision(final_choice, decided_by, rationale)
        
        # Move to completed decisions
        self.completed_decisions.append(decision)
        del self.active_decisions[decision_id]
        
        # Log the decision
        self._log_decision(decision)
        
        # Reset meeting state
        self.meeting_phase = "action_planning"
        self.discussion_rounds = 0
        
        logger.info(f"Decision completed: {decision.topic} - decided by {decided_by}")
        return True
        
    def _log_decision(self, decision: BusinessDecision):
        """Log the decision for future reference."""
        
        decision_log = {
            "timestamp": datetime.now().isoformat(),
            "meeting": self.name,
            "decision": decision.to_dict()
        }
        
        self.decision_history.append(decision_log)
        
        # Could also write to file or database here
        logger.info(f"Decision logged: {decision.id}")
        
    def get_meeting_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive meeting summary with all decisions."""
        
        return {
            "meeting_name": self.name,
            "meeting_type": self.meeting_type,
            "duration": self.discussion_rounds,
            "participants": [agent.name for agent in self.agents],
            "agenda_items": self.agenda_items,
            "decisions_made": len(self.completed_decisions),
            "active_decisions": len(self.active_decisions),
            "completed_decisions": [d.to_dict() for d in self.completed_decisions],
            "expert_participation": self.expert_domains,
            "final_phase": self.meeting_phase
        }
        
    def run_business_meeting(self, max_rounds: int = 20, agenda_items: List[str] = None):
        """Run a complete business meeting with structured decision-making."""
        
        if agenda_items:
            self.agenda_items = agenda_items
            
        for round_num in range(1, max_rounds + 1):
            # Check for decision points
            recent_communications = self._get_recent_communications()
            decision_trigger = self.detect_decision_point(recent_communications)
            
            if decision_trigger and not self.active_decisions:
                # Initiate decision process
                current_topic = self._extract_decision_topic(recent_communications)
                self.initiate_decision_process(current_topic, "high", "high")
                
            # Run regular simulation step
            super()._step(timedelta(minutes=5), round_num, max_rounds)
            
            # Check if active decisions need forcing
            for decision_id, decision in list(self.active_decisions.items()):
                if (datetime.now() - decision.created_at).seconds > 300:  # 5 minutes
                    self.force_decision_resolution(decision_id)
                    
        return self.get_meeting_summary()
        
    def _get_recent_communications(self) -> List[str]:
        """Extract recent communications for pattern analysis."""
        # This would integrate with the TinyTroupe communication system
        # For now, return empty list - this would be implemented based on 
        # how communications are stored in the base system
        return []
        
    def _extract_decision_topic(self, communications: List[str]) -> str:
        """Extract the main decision topic from recent communications."""
        # Simple extraction - could be enhanced with NLP
        if communications:
            return f"Technical decision based on recent discussion"
        return "Unspecified technical decision"