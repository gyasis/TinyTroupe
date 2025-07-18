"""
Present-Enabled Adaptive Agent for TinyTroupe

This module extends the AdaptiveTinyPerson with Present Feature capabilities,
enabling agents to generate documents and summaries while maintaining
context-aware behavior.
"""

from typing import Dict, List, Any, Optional
from tinytroupe.adaptive_agent import AdaptiveTinyPerson
from tinytroupe.agent.present_faculty import PresentMentalFaculty
from tinytroupe.tools.tool_orchestrator import global_tool_orchestrator
from tinytroupe.tools.present_tools import ComplianceReportTool, TechnicalMemoTool, SummaryTool
from tinytroupe.context_detection import ContextType


class PresentAdaptiveTinyPerson(AdaptiveTinyPerson):
    """
    Enhanced AdaptiveTinyPerson with Present Feature capabilities.
    
    Combines context-aware behavior with document generation and sharing tools,
    enabling agents to create both detailed documents and conversational summaries
    based on their role and the current conversation context.
    """
    
    def __init__(self, name: str = "A Person", **kwargs):
        super().__init__(name, **kwargs)
        
        # Initialize present capabilities
        self.present_faculty = PresentMentalFaculty()
        self.add_mental_faculty(self.present_faculty)
        
        # Track role for tool assignment
        self.role = self._infer_role_from_occupation()
        
        # Initialize and assign tools based on role
        self._setup_role_based_tools()
        
        # Track document generation activity
        self.documents_generated = []
        self.summaries_shared = []
    
    def _infer_role_from_occupation(self) -> str:
        """Infer agent role from occupation for tool assignment."""
        occupation = self._configuration.get("occupation", "").lower()
        
        if "compliance" in occupation or "legal" in occupation:
            return "compliance_officer"
        elif "developer" in occupation or "architect" in occupation or "cto" in occupation:
            return "technical_lead"
        elif "manager" in occupation or "director" in occupation:
            return "project_manager"
        elif "data" in occupation and "scientist" in occupation:
            return "data_specialist"
        elif "physician" in occupation or "doctor" in occupation:
            return "medical_professional"
        else:
            return "team_member"
    
    def _setup_role_based_tools(self):
        """Setup tools based on the agent's role and register with orchestrator."""
        
        # Create role-appropriate tools
        role_tools = []
        
        if self.role == "compliance_officer":
            # Compliance officers get specialized compliance tools
            compliance_tool = ComplianceReportTool(owner=self)
            role_tools.append(compliance_tool)
            
            # Set compliance-specific permissions
            global_tool_orchestrator.permission_manager.set_role_permission(
                self.role, "compliance_report", "admin"
            )
        
        if self.role in ["technical_lead", "data_specialist"]:
            # Technical roles get technical memo tools
            tech_memo_tool = TechnicalMemoTool(owner=self)
            role_tools.append(tech_memo_tool)
            
            # Set technical tool permissions
            global_tool_orchestrator.permission_manager.set_role_permission(
                self.role, "technical_memo", "admin"
            )
        
        if self.role in ["project_manager", "medical_professional"]:
            # Managers and medical professionals get summary tools
            summary_tool = SummaryTool(owner=self)
            role_tools.append(summary_tool)
            
            # Set summary tool permissions
            global_tool_orchestrator.permission_manager.set_role_permission(
                self.role, "summary", "admin"
            )
        
        # All roles get basic summary capabilities
        if self.role == "team_member":
            summary_tool = SummaryTool(owner=self)
            role_tools.append(summary_tool)
            global_tool_orchestrator.permission_manager.set_role_permission(
                self.role, "summary", "write"
            )
        
        # Register tools with the global orchestrator
        for tool in role_tools:
            global_tool_orchestrator.register_tool(tool)
        
        # Assign tools to this role
        tool_names = [tool.name for tool in role_tools]
        global_tool_orchestrator.assign_tools_to_role(self.role, tool_names)
    
    def _enhance_configuration_for_context(self, context: ContextType) -> Dict[str, Any]:
        """Enhanced configuration that includes present feature guidance."""
        
        # Get base adaptive configuration
        enhanced_config = super()._enhance_configuration_for_context(context)
        
        # Add present feature configuration
        enhanced_config["present_capabilities"] = {
            "role": self.role,
            "available_tools": [tool.name for tool in global_tool_orchestrator.get_tools_for_role(self.role)],
            "document_generation_enabled": True,
            "summary_sharing_enabled": True
        }
        
        # Add context-specific present guidance
        if context == ContextType.BUSINESS_MEETING:
            enhanced_config["present_guidance"] = self._get_business_meeting_present_guidance()
        elif context == ContextType.TECHNICAL_DISCUSSION:
            enhanced_config["present_guidance"] = self._get_technical_discussion_present_guidance()
        else:
            enhanced_config["present_guidance"] = self._get_general_present_guidance()
        
        # Add output mode selection logic
        enhanced_config["output_mode_selection"] = self._get_output_mode_guidance(context)
        
        return enhanced_config
    
    def _get_business_meeting_present_guidance(self) -> str:
        """Get present feature guidance for business meetings."""
        
        role_guidance = {
            "compliance_officer": """
Your Present Feature Role:
- Generate compliance reports when compliance topics are discussed
- Use PRESENT mode for formal compliance documentation
- Use SUMMARIZE mode for quick compliance status updates
- SHARE compliance reports with relevant stakeholders
- REFERENCE existing compliance documents when discussing regulations
""",
            "technical_lead": """
Your Present Feature Role:
- Create technical memos for architecture decisions
- Use PRESENT mode for detailed technical specifications
- Use SUMMARIZE mode for technical updates in meetings
- SHARE technical documentation with development teams
- REFERENCE existing technical documents for consistency
""",
            "project_manager": """
Your Present Feature Role:
- Generate meeting summaries and project status reports
- Use PRESENT mode for formal project documentation
- Use SUMMARIZE mode for quick status updates
- SHARE project documents with all stakeholders
- REFERENCE project documents to track decisions and progress
""",
            "team_member": """
Your Present Feature Role:
- Create summaries of discussions in your area of expertise
- Use SUMMARIZE mode for conversational updates
- SHARE insights with relevant team members
- REFERENCE shared documents to avoid repetition
"""
        }
        
        return role_guidance.get(self.role, role_guidance["team_member"])
    
    def _get_technical_discussion_present_guidance(self) -> str:
        """Get present feature guidance for technical discussions."""
        
        return """
Technical Discussion Present Feature Usage:
- Generate technical memos for complex technical decisions
- Use PRESENT mode for specifications that need to be referenced later
- Use SUMMARIZE mode for quick technical explanations
- SHARE technical documentation with relevant team members
- Always include technical details and implementation considerations
- Reference existing technical documents for consistency
"""
    
    def _get_general_present_guidance(self) -> str:
        """Get general present feature guidance."""
        
        return """
General Present Feature Usage:
- Use PRESENT mode when creating documents for future reference
- Use SUMMARIZE mode for conversational sharing of information
- Consider your audience when choosing output mode
- SHARE important documents with relevant participants
- REFERENCE existing documents to build upon previous work
"""
    
    def _get_output_mode_guidance(self, context: ContextType) -> str:
        """Get guidance for selecting appropriate output modes."""
        
        if context == ContextType.BUSINESS_MEETING:
            return """
Output Mode Selection for Business Meetings:
- PRESENT: For formal decisions, compliance reports, project documentation
- SUMMARIZE: For quick updates, casual discussions, meeting notes
- HYBRID: When you want to share insights with reference to detailed documentation
- Consider the formality of the discussion and audience needs
"""
        elif context == ContextType.TECHNICAL_DISCUSSION:
            return """
Output Mode Selection for Technical Discussions:
- PRESENT: For architecture decisions, technical specifications, design documents
- SUMMARIZE: For technical explanations, quick technical updates
- HYBRID: When explaining complex concepts with detailed backup documentation
- Always include technical details appropriate to the audience
"""
        else:
            return """
Output Mode Selection:
- PRESENT: When creating referenceable documentation
- SUMMARIZE: For conversational sharing and quick updates
- HYBRID: When combining immediate insights with detailed documentation
- Match the formality to the context and audience
"""
    
    def _should_generate_document(self, context: ContextType, topic: str) -> bool:
        """Determine if a document should be generated based on context and role."""
        
        # Business meetings often benefit from documentation
        if context == ContextType.BUSINESS_MEETING:
            # Compliance officers should document compliance discussions
            if self.role == "compliance_officer" and any(word in topic.lower() for word in ["compliance", "regulation", "audit", "hipaa", "sox"]):
                return True
            
            # Technical leads should document technical decisions
            if self.role == "technical_lead" and any(word in topic.lower() for word in ["architecture", "design", "technical", "system", "implementation"]):
                return True
            
            # Project managers should document project decisions
            if self.role == "project_manager" and any(word in topic.lower() for word in ["project", "timeline", "milestone", "resource", "planning"]):
                return True
        
        # Technical discussions often need documentation
        if context == ContextType.TECHNICAL_DISCUSSION:
            if self.role in ["technical_lead", "data_specialist"] and any(word in topic.lower() for word in ["specification", "architecture", "design", "analysis"]):
                return True
        
        return False
    
    def _should_share_summary(self, context: ContextType, participants: List[str]) -> bool:
        """Determine if a summary should be shared based on context."""
        
        # Share summaries in business meetings with multiple participants
        if context == ContextType.BUSINESS_MEETING and len(participants) > 2:
            return True
        
        # Share technical summaries when multiple technical people are present
        if context == ContextType.TECHNICAL_DISCUSSION and len(participants) > 2:
            return True
        
        return False
    
    def process_action(self, action: dict) -> bool:
        """Enhanced action processing with present feature support."""
        
        # First try present feature actions
        if self.present_faculty.process_action(self, action):
            # Track document generation activity
            action_type = action.get('type', '').upper()
            if action_type == 'PRESENT':
                self.documents_generated.append({
                    'timestamp': self._get_current_timestamp(),
                    'topic': action.get('content', {}).get('topic', 'Unknown'),
                    'action': action
                })
            elif action_type in ['SUMMARIZE', 'SHARE']:
                self.summaries_shared.append({
                    'timestamp': self._get_current_timestamp(),
                    'action_type': action_type,
                    'action': action
                })
            return True
        
        # Fall back to standard adaptive behavior
        return super().process_action(action)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for tracking."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_present_capabilities_summary(self) -> Dict[str, Any]:
        """Get a summary of this agent's present capabilities."""
        
        available_tools = global_tool_orchestrator.get_available_tools(self)
        
        return {
            "role": self.role,
            "available_tools": [tool.name for tool in available_tools],
            "documents_generated": len(self.documents_generated),
            "summaries_shared": len(self.summaries_shared),
            "present_faculty_enabled": self.present_faculty is not None,
            "tool_permissions": {
                tool.name: global_tool_orchestrator.permission_manager.check_permission(
                    self.role, tool.name, "write"
                ) for tool in available_tools
            }
        }
    
    def suggest_present_action(self, topic: str, participants: List[str] = None) -> Optional[Dict[str, Any]]:
        """Suggest an appropriate present action based on context and role."""
        
        if participants is None:
            participants = []
        
        # Detect current context
        context = self._get_conversation_context()
        
        # Determine if documentation is needed
        if self._should_generate_document(context, topic):
            if self.role == "compliance_officer":
                return {
                    "type": "PRESENT",
                    "content": {
                        "tool": "compliance_report",
                        "topic": topic,
                        "format": "markdown",
                        "compliance_type": "hipaa"  # Could be inferred from topic
                    }
                }
            elif self.role == "technical_lead":
                return {
                    "type": "PRESENT", 
                    "content": {
                        "tool": "technical_memo",
                        "topic": topic,
                        "memo_type": "analysis",
                        "format": "markdown"
                    }
                }
            elif self.role == "project_manager":
                return {
                    "type": "PRESENT",
                    "content": {
                        "tool": "summary",
                        "topic": topic,
                        "summary_type": "meeting",
                        "format": "markdown"
                    }
                }
        
        # Suggest summary sharing
        elif self._should_share_summary(context, participants):
            return {
                "type": "SUMMARIZE",
                "content": {
                    "tool": "summary",
                    "topic": topic,
                    "style": "executive" if context == ContextType.BUSINESS_MEETING else "technical",
                    "length": "brief"
                }
            }
        
        return None


def create_present_adaptive_agent(name: str, role_occupation: str, **kwargs) -> PresentAdaptiveTinyPerson:
    """
    Factory function to create a PresentAdaptiveTinyPerson with role-appropriate configuration.
    
    Args:
        name: Agent name
        role_occupation: The agent's occupation/role (used for tool assignment)
        **kwargs: Additional configuration parameters
    
    Returns:
        Configured PresentAdaptiveTinyPerson instance
    """
    
    # Create the agent (don't pass occupation to constructor)
    agent = PresentAdaptiveTinyPerson(name, **kwargs)
    
    # Set occupation after creation using define method
    agent.define("occupation", role_occupation)
    
    # Additional role-specific configuration
    role_configs = {
        "compliance_officer": {
            "expertise_domains": [
                {
                    "domain": "Compliance",
                    "competency_level": "Expert",
                    "specific_knowledge": "HIPAA, SOX, PCI-DSS, regulatory auditing"
                }
            ]
        },
        "technical_lead": {
            "expertise_domains": [
                {
                    "domain": "Software Architecture",
                    "competency_level": "Expert", 
                    "specific_knowledge": "System design, technical specifications, implementation planning"
                }
            ]
        },
        "project_manager": {
            "expertise_domains": [
                {
                    "domain": "Project Management",
                    "competency_level": "Expert",
                    "specific_knowledge": "Project planning, resource management, stakeholder communication"
                }
            ]
        }
    }
    
    # Apply role-specific configuration
    if agent.role in role_configs:
        for key, value in role_configs[agent.role].items():
            agent.define(key, value)
    
    return agent