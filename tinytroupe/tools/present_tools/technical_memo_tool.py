"""
Technical Memo Tool for the TinyTroupe Present Feature

This tool generates technical memos, specifications, and documentation
in both detailed format and conversational summaries.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from tinytroupe.tools import logger
from tinytroupe.tools.tool_orchestrator import PresentTool, OutputMode
from tinytroupe.tools.document_manager import global_document_repository
import tinytroupe.utils as utils


class TechnicalMemoTool(PresentTool):
    """
    Tool for generating technical memos and specifications with dual output modes.
    
    Supports detailed technical documentation and conversational summaries
    for engineering discussions and decision-making.
    """
    
    def __init__(self, owner=None, exporter=None, enricher=None):
        super().__init__(
            name="technical_memo",
            description="Generate technical memos, specifications, and engineering documentation",
            owner=owner,
            real_world_side_effects=False,
            exporter=exporter,
            enricher=enricher,
            supported_modes=[OutputMode.PRESENT, OutputMode.TALK, OutputMode.HYBRID]
        )
        
        # Technical document types and templates
        self.memo_types = {
            "architecture": {
                "name": "Architecture Decision Record",
                "sections": [
                    "Context and Problem Statement",
                    "Decision Drivers", 
                    "Considered Options",
                    "Decision Outcome",
                    "Implementation Details",
                    "Consequences"
                ]
            },
            "specification": {
                "name": "Technical Specification",
                "sections": [
                    "Overview and Scope",
                    "Requirements",
                    "System Architecture",
                    "API Specifications",
                    "Implementation Plan",
                    "Testing Strategy"
                ]
            },
            "analysis": {
                "name": "Technical Analysis",
                "sections": [
                    "Problem Description",
                    "Current State Analysis",
                    "Technical Challenges",
                    "Proposed Solutions",
                    "Risk Assessment",
                    "Recommendations"
                ]
            },
            "design": {
                "name": "System Design Document",
                "sections": [
                    "System Overview",
                    "Functional Requirements",
                    "Non-Functional Requirements",
                    "System Architecture",
                    "Data Design",
                    "Security Considerations"
                ]
            }
        }
    
    def _process_present_action(self, agent, action: dict, output_mode: OutputMode) -> Dict[str, Any]:
        """Process technical memo generation in specified output mode."""
        
        try:
            content = action.get('content', {})
            if isinstance(content, str):
                content = utils.extract_json(content)
            
            # Extract parameters
            memo_type = content.get('memo_type', 'analysis').lower()
            subject = content.get('subject', 'Technical Analysis')
            system_name = content.get('system_name', 'Target System')
            technical_details = content.get('technical_details', {})
            stakeholders = content.get('stakeholders', [])
            priority = content.get('priority', 'medium')
            
            # Validate memo type
            if memo_type not in self.memo_types:
                raise ValueError(f"Unsupported memo type: {memo_type}")
            
            memo_info = self.memo_types[memo_type]
            
            if output_mode == OutputMode.PRESENT:
                return self._generate_detailed_memo(
                    agent, memo_type, memo_info, subject, system_name,
                    technical_details, stakeholders, priority, content
                )
            elif output_mode == OutputMode.TALK:
                return self._generate_conversational_summary(
                    agent, memo_type, memo_info, subject, system_name,
                    technical_details, stakeholders, priority, content
                )
            elif output_mode == OutputMode.HYBRID:
                return self._generate_hybrid_output(
                    agent, memo_type, memo_info, subject, system_name,
                    technical_details, stakeholders, priority, content
                )
            else:
                raise ValueError(f"Unsupported output mode: {output_mode}")
                
        except Exception as e:
            logger.error(f"Error generating technical memo: {e}")
            return {
                "content": f"Error generating technical memo: {str(e)}",
                "format": "text",
                "references": [],
                "confidence_score": 0.0
            }
    
    def _generate_detailed_memo(self, agent, memo_type, memo_info, subject, system_name,
                              technical_details, stakeholders, priority, params) -> Dict[str, Any]:
        """Generate a detailed technical memo document."""
        
        # Prepare template parameters
        template_params = {
            "title": f"{memo_info['name']}: {subject}",
            "author": agent.name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "subject": subject,
            "system_name": system_name,
            "priority": priority.upper(),
            "stakeholders": ", ".join(stakeholders) if stakeholders else "Engineering Team",
            "overview": self._generate_overview(memo_type, subject, system_name),
            "technical_details": self._format_technical_details(technical_details, memo_info['sections']),
            "implementation_plan": self._generate_implementation_plan(memo_type, technical_details),
            "risks": self._generate_risk_assessment(memo_type, technical_details),
            "conclusion": self._generate_conclusion(memo_type, subject),
            "tool_name": self.name
        }
        
        # Store in document repository
        doc_id = global_document_repository.store_document(
            title=template_params["title"],
            content="",  # Will be filled by template
            author=agent.name,
            doc_type="technical_memo",
            format="markdown",
            tags=[memo_type, "technical", "engineering", system_name.lower().replace(" ", "_")],
            template_name="technical_memo",
            template_params=template_params,
            tool_generated=self.name
        )
        
        # Store reference in agent memory
        agent.store_memory(f"Generated technical memo: {template_params['title']} (ID: {doc_id})")
        
        return {
            "content": f"Detailed {memo_info['name']} for {subject} generated",
            "format": "markdown",
            "document_id": doc_id,
            "references": [f"Technical Documentation: {subject}", f"System: {system_name}"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Generated comprehensive technical memo covering {len(memo_info['sections'])} key areas for {system_name}"
        }
    
    def _generate_conversational_summary(self, agent, memo_type, memo_info, subject, system_name,
                                       technical_details, stakeholders, priority, params) -> Dict[str, Any]:
        """Generate a conversational summary of the technical memo."""
        
        summary_style = params.get('style', 'technical')
        length = params.get('length', 'brief')
        
        if summary_style == 'executive':
            summary = self._generate_executive_tech_summary(memo_type, subject, system_name, priority, technical_details)
        elif summary_style == 'technical':
            summary = self._generate_technical_summary(memo_type, subject, system_name, technical_details, length)
        else:
            summary = self._generate_casual_tech_summary(memo_type, subject, system_name, technical_details)
        
        # Store in agent memory for reference
        agent.store_memory(f"Discussed technical memo: {subject} for {system_name}")
        
        return {
            "content": summary,
            "format": "text",
            "references": [f"Technical Analysis: {subject}", f"System: {system_name}"],
            "confidence_score": 0.85,
            "reasoning_trace": f"Summarized {memo_type} technical memo focusing on {summary_style} perspective"
        }
    
    def _generate_hybrid_output(self, agent, memo_type, memo_info, subject, system_name,
                              technical_details, stakeholders, priority, params) -> Dict[str, Any]:
        """Generate hybrid output with summary and document reference."""
        
        # First generate the detailed memo
        detailed_result = self._generate_detailed_memo(
            agent, memo_type, memo_info, subject, system_name,
            technical_details, stakeholders, priority, params
        )
        
        # Then create a summary with reference to the detailed memo
        doc_id = detailed_result.get('document_id')
        
        key_points = list(technical_details.keys())[:3] if technical_details else ["system design", "implementation", "considerations"]
        
        hybrid_summary = f"""I've completed the {memo_info['name']} for {subject} on the {system_name} system.

Key technical points:
• {key_points[0] if len(key_points) > 0 else 'Architecture considerations'}
• {key_points[1] if len(key_points) > 1 else 'Implementation approach'}  
• {key_points[2] if len(key_points) > 2 else 'Risk assessment'}

This is marked as {priority} priority. The detailed technical specifications, implementation plan, and risk analysis are all documented in the full memo (ID: {doc_id}).

Would you like me to walk through any specific technical aspects, or shall we discuss the implementation timeline?"""
        
        return {
            "content": hybrid_summary,
            "format": "text",
            "document_id": doc_id,
            "references": [f"Detailed Memo: {doc_id}", f"Technical Specs: {subject}"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Provided hybrid summary with reference to detailed technical memo {doc_id}"
        }
    
    def _generate_overview(self, memo_type, subject, system_name) -> str:
        """Generate overview section for the memo."""
        if memo_type == 'architecture':
            return f"This document captures the architectural decision made for {subject} in the {system_name} system, including the context, options considered, and rationale for the chosen approach."
        elif memo_type == 'specification':
            return f"This specification defines the technical requirements and implementation details for {subject} in the {system_name} system."
        elif memo_type == 'analysis':
            return f"This analysis examines {subject} for the {system_name} system, providing technical insights and recommendations."
        else:  # design
            return f"This design document outlines the system architecture and implementation approach for {subject} in the {system_name} system."
    
    def _format_technical_details(self, technical_details: Dict[str, Any], sections: List[str]) -> str:
        """Format technical details according to memo sections."""
        if not technical_details:
            formatted = ""
            for section in sections:
                formatted += f"## {section}\n\n[To be completed]\n\n"
            return formatted
        
        formatted = ""
        for section in sections:
            formatted += f"## {section}\n\n"
            
            # Try to find matching content for this section
            section_key = section.lower().replace(" ", "_").replace("and", "").strip("_")
            
            if section_key in technical_details:
                content = technical_details[section_key]
                if isinstance(content, list):
                    for item in content:
                        formatted += f"- {item}\n"
                else:
                    formatted += f"{content}\n"
            else:
                # Generate placeholder content based on section type
                if "requirement" in section.lower():
                    formatted += "- Functional requirements to be defined\n- Non-functional requirements to be specified\n"
                elif "architecture" in section.lower():
                    formatted += "- System components and interactions\n- Technology stack and frameworks\n"
                elif "implementation" in section.lower():
                    formatted += "- Development approach and timeline\n- Resource requirements and dependencies\n"
                elif "risk" in section.lower() or "consequence" in section.lower():
                    formatted += "- Technical risks and mitigation strategies\n- Long-term maintenance considerations\n"
                else:
                    formatted += "[Content to be developed]\n"
            
            formatted += "\n"
        
        return formatted
    
    def _generate_implementation_plan(self, memo_type, technical_details) -> str:
        """Generate implementation plan based on memo type and details."""
        plan = "## Implementation Plan\n\n"
        
        if 'timeline' in technical_details:
            plan += f"**Timeline**: {technical_details['timeline']}\n\n"
        
        plan += "### Phase 1: Design and Planning\n"
        plan += "- Finalize technical specifications\n"
        plan += "- Resource allocation and team assignment\n"
        plan += "- Setup development environment\n\n"
        
        plan += "### Phase 2: Core Implementation\n"
        plan += "- Develop core functionality\n"
        plan += "- Unit testing and code review\n"
        plan += "- Integration with existing systems\n\n"
        
        plan += "### Phase 3: Testing and Deployment\n"
        plan += "- Comprehensive testing (unit, integration, performance)\n"
        plan += "- Documentation and training materials\n"
        plan += "- Production deployment and monitoring\n\n"
        
        return plan
    
    def _generate_risk_assessment(self, memo_type, technical_details) -> str:
        """Generate risk assessment section."""
        risks = "## Risk Assessment\n\n"
        
        risks += "### Technical Risks\n"
        risks += "- **Complexity Risk**: Implementation complexity may exceed estimates\n"
        risks += "- **Integration Risk**: Challenges integrating with existing systems\n"
        risks += "- **Performance Risk**: System may not meet performance requirements\n\n"
        
        risks += "### Mitigation Strategies\n"
        risks += "- Conduct proof-of-concept development for complex components\n"
        risks += "- Implement comprehensive testing strategy\n"
        risks += "- Plan for iterative development and feedback cycles\n\n"
        
        return risks
    
    def _generate_conclusion(self, memo_type, subject) -> str:
        """Generate conclusion section."""
        if memo_type == 'architecture':
            return f"This architectural decision for {subject} provides a solid foundation for future development while maintaining system flexibility and scalability."
        elif memo_type == 'specification':
            return f"This specification provides comprehensive guidance for implementing {subject} with clear requirements and technical approach."
        else:
            return f"This analysis of {subject} provides the technical foundation needed to make informed decisions and proceed with implementation."
    
    def _generate_executive_tech_summary(self, memo_type, subject, system_name, priority, technical_details):
        """Generate executive-style technical summary."""
        return f"Completed {memo_type} analysis for {subject} on {system_name}. " + \
               f"Priority level: {priority}. " + \
               f"Technical approach is sound with manageable implementation complexity. " + \
               f"Recommend proceeding with proposed solution and timeline."
    
    def _generate_technical_summary(self, memo_type, subject, system_name, technical_details, length):
        """Generate technical-style summary."""
        detail_count = len(technical_details) if technical_details else 3
        
        if length == 'brief':
            return f"{memo_type.title()} analysis complete for {subject}. " + \
                   f"Covered {detail_count} key technical areas. " + \
                   f"Architecture approach validated, implementation plan defined. " + \
                   f"Ready for development phase with documented specifications."
        else:
            return f"Comprehensive {memo_type} analysis for {subject} in {system_name} system. " + \
                   f"Evaluated {detail_count} technical dimensions including architecture, implementation approach, and risk factors. " + \
                   f"Proposed solution meets requirements with acceptable complexity. " + \
                   f"Full technical specifications and implementation roadmap documented for development team."
    
    def _generate_casual_tech_summary(self, memo_type, subject, system_name, technical_details):
        """Generate casual-style technical summary."""
        return f"Just wrapped up the {memo_type} work for {subject}. " + \
               f"Technical approach looks solid - nothing too crazy complicated. " + \
               f"Got all the specs documented and implementation plan mapped out. " + \
               f"Should be straightforward for the dev team to pick up and run with."
    
    def actions_definitions_prompt(self) -> str:
        prompt = """
        - GENERATE_DOCUMENT: Generate a comprehensive technical memo. Content must include:
          * memo_type: Type of memo (architecture, specification, analysis, design)
          * subject: Technical subject or system being documented
          * system_name: Name of the system or component
          * technical_details: Dictionary of technical specifications and details
          * stakeholders: List of stakeholders (optional)
          * priority: Priority level (high, medium, low)
          
        - GENERATE_SUMMARY: Generate a conversational technical summary. Content must include:
          * memo_type: Type of memo (architecture, specification, analysis, design)
          * subject: Technical subject being summarized
          * system_name: Name of the system or component
          * style: Summary style (executive, technical, casual)
          * length: Summary length (brief, detailed)
        """
        return utils.dedent(prompt)
    
    def actions_constraints_prompt(self) -> str:
        prompt = """
        - Technical memos must be precise and technically accurate
        - Include specific implementation details and timelines when possible
        - Always consider technical risks and mitigation strategies
        - Use appropriate technical terminology for the intended audience
        - Store detailed technical documentation for future reference
        - Reference existing systems and architectural decisions when relevant
        """
        return utils.dedent(prompt)