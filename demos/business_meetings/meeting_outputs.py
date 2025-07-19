"""
Meeting output generation system for business meetings.
Ensures every meeting produces concrete, actionable deliverables.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json

@dataclass
class ActionItem:
    """Represents a specific action item with ownership and timeline."""
    id: str
    description: str
    owner: str
    due_date: datetime
    priority: str  # critical, high, medium, low
    status: str = "open"  # open, in_progress, completed, blocked
    dependencies: List[str] = field(default_factory=list)
    success_criteria: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "owner": self.owner,
            "due_date": self.due_date.isoformat(),
            "priority": self.priority,
            "status": self.status,
            "dependencies": self.dependencies,
            "success_criteria": self.success_criteria,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class TechnicalDecision:
    """Represents a concrete technical decision with full context."""
    id: str
    decision_topic: str
    selected_option: str
    rationale: str
    decided_by: str
    alternatives_considered: List[str]
    technical_specifications: Dict[str, Any]
    implementation_plan: List[ActionItem]
    success_metrics: List[str]
    risks_and_mitigation: List[Dict[str, str]]
    review_date: datetime
    decided_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_topic": self.decision_topic,
            "selected_option": self.selected_option,
            "rationale": self.rationale,
            "decided_by": self.decided_by,
            "alternatives_considered": self.alternatives_considered,
            "technical_specifications": self.technical_specifications,
            "implementation_plan": [item.to_dict() for item in self.implementation_plan],
            "success_metrics": self.success_metrics,
            "risks_and_mitigation": self.risks_and_mitigation,
            "review_date": self.review_date.isoformat(),
            "decided_at": self.decided_at.isoformat()
        }

@dataclass
class MeetingDeliverable:
    """Represents a required deliverable from a meeting."""
    name: str
    description: str
    owner: str
    due_date: datetime
    deliverable_type: str  # document, prototype, analysis, plan, specification
    acceptance_criteria: List[str]
    stakeholders: List[str]
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "owner": self.owner,
            "due_date": self.due_date.isoformat(),
            "deliverable_type": self.deliverable_type,
            "acceptance_criteria": self.acceptance_criteria,
            "stakeholders": self.stakeholders,
            "status": self.status
        }

class MeetingOutputGenerator:
    """Generates structured outputs from business meetings."""
    
    def __init__(self, meeting_name: str, meeting_type: str):
        self.meeting_name = meeting_name
        self.meeting_type = meeting_type
        self.decisions: List[TechnicalDecision] = []
        self.action_items: List[ActionItem] = []
        self.deliverables: List[MeetingDeliverable] = []
        self.participants: List[str] = []
        self.meeting_start: datetime = datetime.now()
        self.meeting_end: Optional[datetime] = None
        
    def add_participant(self, participant: str, role: str, expertise: List[str]):
        """Add a meeting participant with their role and expertise."""
        self.participants.append({
            "name": participant,
            "role": role,
            "expertise": expertise
        })
        
    def record_decision(self, decision_topic: str, selected_option: str, 
                       decided_by: str, rationale: str,
                       technical_specs: Dict[str, Any],
                       alternatives: List[str] = None) -> TechnicalDecision:
        """Record a technical decision made during the meeting."""
        
        decision_id = f"decision_{len(self.decisions) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        decision = TechnicalDecision(
            id=decision_id,
            decision_topic=decision_topic,
            selected_option=selected_option,
            rationale=rationale,
            decided_by=decided_by,
            alternatives_considered=alternatives or [],
            technical_specifications=technical_specs,
            implementation_plan=[],
            success_metrics=[],
            risks_and_mitigation=[],
            review_date=datetime.now() + timedelta(days=30)
        )
        
        self.decisions.append(decision)
        return decision
        
    def add_action_item(self, description: str, owner: str, due_date: datetime,
                       priority: str = "medium", success_criteria: str = "",
                       dependencies: List[str] = None) -> ActionItem:
        """Add an action item with specific ownership and timeline."""
        
        action_id = f"action_{len(self.action_items) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        action_item = ActionItem(
            id=action_id,
            description=description,
            owner=owner,
            due_date=due_date,
            priority=priority,
            success_criteria=success_criteria,
            dependencies=dependencies or []
        )
        
        self.action_items.append(action_item)
        return action_item
        
    def add_deliverable(self, name: str, description: str, owner: str,
                       due_date: datetime, deliverable_type: str,
                       acceptance_criteria: List[str], stakeholders: List[str]) -> MeetingDeliverable:
        """Add a required deliverable from the meeting."""
        
        deliverable = MeetingDeliverable(
            name=name,
            description=description,
            owner=owner,
            due_date=due_date,
            deliverable_type=deliverable_type,
            acceptance_criteria=acceptance_criteria,
            stakeholders=stakeholders
        )
        
        self.deliverables.append(deliverable)
        return deliverable
        
    def generate_meeting_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive meeting summary with all outputs."""
        
        self.meeting_end = datetime.now()
        duration = self.meeting_end - self.meeting_start
        
        return {
            "meeting_info": {
                "name": self.meeting_name,
                "type": self.meeting_type,
                "start_time": self.meeting_start.isoformat(),
                "end_time": self.meeting_end.isoformat(),
                "duration_minutes": int(duration.total_seconds() / 60),
                "participants": self.participants
            },
            "decisions_made": {
                "count": len(self.decisions),
                "decisions": [decision.to_dict() for decision in self.decisions]
            },
            "action_items": {
                "count": len(self.action_items),
                "items": [item.to_dict() for item in self.action_items],
                "by_priority": self._group_actions_by_priority(),
                "by_owner": self._group_actions_by_owner()
            },
            "deliverables": {
                "count": len(self.deliverables),
                "items": [deliverable.to_dict() for deliverable in self.deliverables],
                "by_type": self._group_deliverables_by_type()
            },
            "next_steps": self._generate_next_steps(),
            "follow_up_required": self._identify_follow_up_needs()
        }
        
    def _group_actions_by_priority(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group action items by priority level."""
        grouped = {"critical": [], "high": [], "medium": [], "low": []}
        for item in self.action_items:
            if item.priority in grouped:
                grouped[item.priority].append(item.to_dict())
        return grouped
        
    def _group_actions_by_owner(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group action items by owner."""
        grouped = {}
        for item in self.action_items:
            if item.owner not in grouped:
                grouped[item.owner] = []
            grouped[item.owner].append(item.to_dict())
        return grouped
        
    def _group_deliverables_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group deliverables by type."""
        grouped = {}
        for deliverable in self.deliverables:
            if deliverable.deliverable_type not in grouped:
                grouped[deliverable.deliverable_type] = []
            grouped[deliverable.deliverable_type].append(deliverable.to_dict())
        return grouped
        
    def _generate_next_steps(self) -> List[str]:
        """Generate immediate next steps based on decisions and action items."""
        next_steps = []
        
        # Immediate actions (due within 1 week)
        immediate_actions = [item for item in self.action_items 
                           if item.due_date <= datetime.now() + timedelta(days=7)]
        
        if immediate_actions:
            next_steps.append(f"Complete {len(immediate_actions)} immediate action items due within 1 week")
            
        # Critical decisions needing implementation
        unimplemented_decisions = [d for d in self.decisions if not d.implementation_plan]
        if unimplemented_decisions:
            next_steps.append(f"Create implementation plans for {len(unimplemented_decisions)} decisions")
            
        # Pending deliverables
        pending_deliverables = [d for d in self.deliverables if d.status == "pending"]
        if pending_deliverables:
            next_steps.append(f"Begin work on {len(pending_deliverables)} deliverables")
            
        return next_steps
        
    def _identify_follow_up_needs(self) -> List[Dict[str, str]]:
        """Identify what follow-up meetings or communications are needed."""
        follow_ups = []
        
        # Check for decisions needing review
        for decision in self.decisions:
            if decision.review_date <= datetime.now() + timedelta(days=30):
                follow_ups.append({
                    "type": "decision_review",
                    "description": f"Review implementation of decision: {decision.decision_topic}",
                    "due_date": decision.review_date.isoformat(),
                    "participants": [decision.decided_by]
                })
                
        # Check for action items needing check-ins
        critical_actions = [item for item in self.action_items if item.priority == "critical"]
        if critical_actions:
            follow_ups.append({
                "type": "status_check",
                "description": f"Check progress on {len(critical_actions)} critical action items",
                "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "participants": list(set([item.owner for item in critical_actions]))
            })
            
        return follow_ups
        
    def validate_meeting_outputs(self) -> Dict[str, bool]:
        """Validate that the meeting produced adequate outputs."""
        
        validation_results = {
            "has_concrete_decisions": len(self.decisions) > 0,
            "has_action_items": len(self.action_items) > 0,
            "action_items_have_owners": all(item.owner for item in self.action_items),
            "action_items_have_deadlines": all(item.due_date for item in self.action_items),
            "decisions_have_rationale": all(decision.rationale for decision in self.decisions),
            "decisions_have_technical_specs": all(decision.technical_specifications for decision in self.decisions),
            "all_participants_have_actions": self._check_participant_engagement()
        }
        
        return validation_results
        
    def _check_participant_engagement(self) -> bool:
        """Check if all participants have some action items or involvement."""
        participant_names = [p["name"] for p in self.participants]
        involved_participants = set()
        
        # Add participants who own action items
        involved_participants.update([item.owner for item in self.action_items])
        
        # Add participants who made decisions
        involved_participants.update([decision.decided_by for decision in self.decisions])
        
        # Add participants who own deliverables
        involved_participants.update([deliverable.owner for deliverable in self.deliverables])
        
        # Check if most participants are involved (allow for some observers)
        return len(involved_participants) >= len(participant_names) * 0.7
        
    def export_action_plan(self, filename: str = None) -> str:
        """Export action plan as formatted text or JSON."""
        
        if not filename:
            filename = f"{self.meeting_name.replace(' ', '_')}_action_plan_{datetime.now().strftime('%Y%m%d')}.json"
            
        action_plan = {
            "meeting": self.meeting_name,
            "generated_at": datetime.now().isoformat(),
            "summary": self.generate_meeting_summary(),
            "validation": self.validate_meeting_outputs()
        }
        
        with open(filename, 'w') as f:
            json.dump(action_plan, f, indent=2)
            
        return filename

class MeetingOutputValidator:
    """Validates that meetings produce adequate business outputs."""
    
    @staticmethod
    def validate_technical_decision_meeting(output_generator: MeetingOutputGenerator) -> Dict[str, Any]:
        """Validate outputs from a technical decision meeting."""
        
        validation = {
            "required_outputs_present": {
                "technical_decisions": len(output_generator.decisions) >= 1,
                "implementation_actions": len(output_generator.action_items) >= 3,
                "deliverables_defined": len(output_generator.deliverables) >= 1
            },
            "decision_quality": {
                "decisions_have_technical_specs": all(
                    decision.technical_specifications for decision in output_generator.decisions
                ),
                "decisions_have_alternatives": all(
                    decision.alternatives_considered for decision in output_generator.decisions
                ),
                "decisions_have_rationale": all(
                    len(decision.rationale) > 50 for decision in output_generator.decisions
                )
            },
            "actionability": {
                "actions_have_specific_owners": all(
                    item.owner and item.owner != "TBD" for item in output_generator.action_items
                ),
                "actions_have_realistic_deadlines": all(
                    item.due_date > datetime.now() for item in output_generator.action_items
                ),
                "critical_actions_identified": any(
                    item.priority == "critical" for item in output_generator.action_items
                )
            }
        }
        
        # Calculate overall score
        all_checks = []
        for category in validation.values():
            all_checks.extend(category.values())
            
        validation["overall_score"] = sum(all_checks) / len(all_checks)
        validation["passed"] = validation["overall_score"] >= 0.8
        
        return validation
        
    @staticmethod
    def generate_output_requirements_prompt(meeting_type: str) -> str:
        """Generate a prompt that enforces output requirements for specific meeting types."""
        
        if meeting_type == "technical_decision":
            return """
            MEETING OUTPUT REQUIREMENTS - TECHNICAL DECISION MEETING
            
            This meeting MUST produce the following concrete outputs:
            
            1. TECHNICAL DECISIONS (minimum 1 required)
               - Specific option selected with exact technical specifications
               - Clear rationale explaining why this option was chosen over alternatives
               - List of alternatives that were considered and rejected
               - Technical implementation details and architecture specifications
            
            2. ACTION ITEMS (minimum 3 required)
               - Specific tasks with named owners (not "team" or "we")
               - Realistic deadlines (specific dates, not "soon" or "next week")
               - Clear success criteria for each action
               - Dependencies and blocking issues identified
            
            3. DELIVERABLES (minimum 1 required)
               - Technical documents, prototypes, or specifications to be created
               - Named owners and specific delivery dates
               - Acceptance criteria for each deliverable
               - Stakeholders who will review and approve
            
            FAILURE TO PRODUCE THESE OUTPUTS MEANS THE MEETING FAILED
            
            Do not end the meeting until these outputs are explicitly documented.
            Challenge any vague commitments and demand specific details.
            """
            
        elif meeting_type == "architecture_review":
            return """
            MEETING OUTPUT REQUIREMENTS - ARCHITECTURE REVIEW MEETING
            
            This meeting MUST produce the following concrete outputs:
            
            1. ARCHITECTURE DECISIONS
               - Selected architectural approach with detailed design
               - Trade-off analysis comparing alternatives
               - Technology stack and platform decisions
               - Integration patterns and data flow specifications
            
            2. IMPLEMENTATION ROADMAP
               - Phased implementation plan with milestones
               - Dependencies between architectural components
               - Risk mitigation strategies for each phase
               - Resource requirements and team assignments
            
            3. GOVERNANCE FRAMEWORK
               - Architecture review and approval processes
               - Standards and guidelines for implementation
               - Change management procedures for architectural modifications
            
            ARCHITECTURE AUTHORITY MUST BE EXERCISED
            Senior architects make final decisions after expert input.
            """
            
        else:
            return """
            MEETING OUTPUT REQUIREMENTS - GENERAL BUSINESS MEETING
            
            This meeting MUST produce actionable outputs:
            - Specific decisions with rationale and ownership
            - Action items with owners, deadlines, and success criteria
            - Clear next steps and follow-up requirements
            
            Vague commitments and "we'll coordinate later" are not acceptable outputs.
            """