"""
Summary Tool for the TinyTroupe Present Feature

This tool generates summaries and abstracts from various sources
in both detailed document format and conversational formats.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from tinytroupe.tools import logger
from tinytroupe.tools.tool_orchestrator import PresentTool, OutputMode
from tinytroupe.tools.document_manager import global_document_repository
import tinytroupe.utils as utils


class SummaryTool(PresentTool):
    """
    Tool for generating summaries and abstracts with dual output modes.
    
    Supports detailed summary documents and conversational summaries
    from various sources including meetings, documents, and discussions.
    """
    
    def __init__(self, owner=None, exporter=None, enricher=None):
        super().__init__(
            name="summary",
            description="Generate summaries and abstracts from meetings, documents, and discussions",
            owner=owner,
            real_world_side_effects=False,
            exporter=exporter,
            enricher=enricher,
            supported_modes=[OutputMode.PRESENT, OutputMode.TALK, OutputMode.HYBRID]
        )
        
        # Summary types and their characteristics
        self.summary_types = {
            "meeting": {
                "name": "Meeting Summary",
                "sections": [
                    "Meeting Overview",
                    "Key Discussion Points",
                    "Decisions Made",
                    "Action Items",
                    "Next Steps"
                ],
                "focus": "decisions and actions"
            },
            "document": {
                "name": "Document Summary",
                "sections": [
                    "Document Overview",
                    "Key Findings",
                    "Main Arguments",
                    "Conclusions",
                    "Implications"
                ],
                "focus": "content and insights"
            },
            "project": {
                "name": "Project Summary",
                "sections": [
                    "Project Overview",
                    "Current Status",
                    "Key Milestones",
                    "Challenges and Risks",
                    "Next Phase"
                ],
                "focus": "progress and planning"
            },
            "research": {
                "name": "Research Summary",
                "sections": [
                    "Research Objective",
                    "Methodology",
                    "Key Findings",
                    "Analysis",
                    "Recommendations"
                ],
                "focus": "findings and methodology"
            }
        }
    
    def _process_present_action(self, agent, action: dict, output_mode: OutputMode) -> Dict[str, Any]:
        """Process summary generation in specified output mode."""
        
        try:
            content = action.get('content', {})
            if isinstance(content, str):
                content = utils.extract_json(content)
            
            # Extract parameters
            summary_type = content.get('summary_type', 'meeting').lower()
            source_title = content.get('source_title', 'Discussion')
            source_content = content.get('source_content', '')
            key_points = content.get('key_points', [])
            attendees = content.get('attendees', [])
            duration = content.get('duration', 'Unknown')
            focus_areas = content.get('focus_areas', [])
            
            # Validate summary type
            if summary_type not in self.summary_types:
                raise ValueError(f"Unsupported summary type: {summary_type}")
            
            summary_info = self.summary_types[summary_type]
            
            if output_mode == OutputMode.PRESENT:
                return self._generate_detailed_summary(
                    agent, summary_type, summary_info, source_title, source_content,
                    key_points, attendees, duration, focus_areas, content
                )
            elif output_mode == OutputMode.TALK:
                return self._generate_conversational_summary(
                    agent, summary_type, summary_info, source_title, source_content,
                    key_points, attendees, duration, focus_areas, content
                )
            elif output_mode == OutputMode.HYBRID:
                return self._generate_hybrid_output(
                    agent, summary_type, summary_info, source_title, source_content,
                    key_points, attendees, duration, focus_areas, content
                )
            else:
                raise ValueError(f"Unsupported output mode: {output_mode}")
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "content": f"Error generating summary: {str(e)}",
                "format": "text",
                "references": [],
                "confidence_score": 0.0
            }
    
    def _generate_detailed_summary(self, agent, summary_type, summary_info, source_title, 
                                 source_content, key_points, attendees, duration, focus_areas, params) -> Dict[str, Any]:
        """Generate a detailed summary document."""
        
        # Prepare template parameters based on summary type
        if summary_type == "meeting":
            template_params = {
                "title": source_title,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "attendees": ", ".join(attendees) if attendees else "Not specified",
                "duration": duration,
                "discussion_points": self._format_key_points(key_points, "discussion"),
                "decisions": self._extract_decisions(key_points, source_content),
                "action_items": self._extract_action_items(key_points, source_content),
                "next_meeting": self._determine_next_steps(summary_type, key_points),
                "tool_name": self.name
            }
            template_name = "meeting_summary"
        else:
            # Generic summary template for other types
            template_params = {
                "title": f"{summary_info['name']}: {source_title}",
                "author": agent.name,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "overview": self._generate_overview(summary_type, source_title, source_content),
                "key_findings": self._format_key_points(key_points, "findings"),
                "analysis": self._generate_analysis(summary_type, key_points, focus_areas),
                "conclusions": self._generate_conclusions(summary_type, key_points),
                "recommendations": self._generate_recommendations(summary_type, key_points),
                "tool_name": self.name
            }
            template_name = "document_summary"  # Will create a generic template
        
        # Store in document repository
        doc_id = global_document_repository.store_document(
            title=template_params["title"],
            content="",  # Will be filled by template
            author=agent.name,
            doc_type=f"{summary_type}_summary",
            format="markdown",
            tags=[summary_type, "summary", source_title.lower().replace(" ", "_")],
            template_name=template_name,
            template_params=template_params,
            tool_generated=self.name
        )
        
        # Store reference in agent memory
        agent.store_memory(f"Generated {summary_type} summary: {source_title} (ID: {doc_id})")
        
        return {
            "content": f"Detailed {summary_info['name']} for '{source_title}' generated",
            "format": "markdown",
            "document_id": doc_id,
            "references": [f"Source: {source_title}", f"Summary Type: {summary_info['name']}"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Generated comprehensive {summary_type} summary covering {len(summary_info['sections'])} key areas"
        }
    
    def _generate_conversational_summary(self, agent, summary_type, summary_info, source_title,
                                       source_content, key_points, attendees, duration, focus_areas, params) -> Dict[str, Any]:
        """Generate a conversational summary."""
        
        summary_style = params.get('style', 'casual')
        length = params.get('length', 'brief')
        
        if summary_style == 'executive':
            summary = self._generate_executive_summary(summary_type, source_title, key_points, attendees)
        elif summary_style == 'detailed' or length == 'detailed':
            summary = self._generate_detailed_conversational_summary(summary_type, source_title, key_points, focus_areas)
        else:
            summary = self._generate_casual_summary(summary_type, source_title, key_points, attendees)
        
        # Store in agent memory for reference
        agent.store_memory(f"Discussed {summary_type} summary: {source_title}")
        
        return {
            "content": summary,
            "format": "text",
            "references": [f"Source: {source_title}", f"Summary Focus: {summary_info['focus']}"],
            "confidence_score": 0.85,
            "reasoning_trace": f"Summarized {summary_type} content focusing on {summary_style} perspective"
        }
    
    def _generate_hybrid_output(self, agent, summary_type, summary_info, source_title,
                              source_content, key_points, attendees, duration, focus_areas, params) -> Dict[str, Any]:
        """Generate hybrid output with summary and document reference."""
        
        # First generate the detailed summary
        detailed_result = self._generate_detailed_summary(
            agent, summary_type, summary_info, source_title, source_content,
            key_points, attendees, duration, focus_areas, params
        )
        
        # Then create a conversational summary with reference
        doc_id = detailed_result.get('document_id')
        
        if summary_type == 'meeting':
            hybrid_summary = f"""Quick update from our {source_title}:

We covered {len(key_points) if key_points else 'several'} main topics and made some key decisions. {'The team included ' + ', '.join(attendees[:3]) + ('...' if len(attendees) > 3 else '') if attendees else 'Good participation from the team'}.

{self._extract_top_decisions(key_points, 2)}

I've documented everything in detail including all action items and next steps (ID: {doc_id}). Let me know if you want to dive deeper into any of the decisions or if you need clarification on any action items."""

        else:
            hybrid_summary = f"""I've completed the {summary_info['name'].lower()} for '{source_title}'.

{self._extract_top_insights(key_points, focus_areas, 2)}

The complete analysis with detailed findings, methodology, and recommendations is documented in the full summary (ID: {doc_id}). Happy to discuss any specific aspects or help you understand the implications for our work."""
        
        return {
            "content": hybrid_summary,
            "format": "text",
            "document_id": doc_id,
            "references": [f"Detailed Summary: {doc_id}", f"Source: {source_title}"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Provided hybrid summary with reference to detailed {summary_type} summary {doc_id}"
        }
    
    def _format_key_points(self, key_points: List[str], context: str) -> str:
        """Format key points for the document."""
        if not key_points:
            return f"No specific {context} points documented."
        
        formatted = ""
        for i, point in enumerate(key_points, 1):
            formatted += f"### {context.title()} Point {i}\n{point}\n\n"
        
        return formatted
    
    def _extract_decisions(self, key_points: List[str], source_content: str) -> str:
        """Extract decisions from key points and content."""
        decisions = []
        
        # Look for decision-like language in key points
        for point in key_points:
            if any(word in point.lower() for word in ['decided', 'agreed', 'approved', 'chosen', 'selected']):
                decisions.append(point)
        
        if not decisions:
            return "No specific decisions were documented in this session."
        
        formatted = ""
        for i, decision in enumerate(decisions, 1):
            formatted += f"**Decision {i}**: {decision}\n\n"
        
        return formatted
    
    def _extract_action_items(self, key_points: List[str], source_content: str) -> str:
        """Extract action items from key points and content."""
        actions = []
        
        # Look for action-like language in key points
        for point in key_points:
            if any(word in point.lower() for word in ['will', 'should', 'need to', 'action', 'task', 'follow up']):
                actions.append(point)
        
        if not actions:
            return "No specific action items were identified."
        
        formatted = ""
        for i, action in enumerate(actions, 1):
            formatted += f"- **Action {i}**: {action}\n"
        
        return formatted
    
    def _determine_next_steps(self, summary_type: str, key_points: List[str]) -> str:
        """Determine next steps based on summary type and content."""
        if summary_type == 'meeting':
            return "Next meeting to be scheduled based on action item progress."
        elif summary_type == 'project':
            return "Continue with planned project milestones and regular status updates."
        else:
            return "Follow up on key recommendations and findings as appropriate."
    
    def _generate_overview(self, summary_type: str, source_title: str, source_content: str) -> str:
        """Generate overview section for the summary."""
        if summary_type == 'document':
            return f"This summary captures the key insights and findings from '{source_title}', highlighting the main arguments, conclusions, and implications for our work."
        elif summary_type == 'project':
            return f"This summary provides an overview of the current status and progress of '{source_title}', including key milestones, challenges, and upcoming activities."
        elif summary_type == 'research':
            return f"This summary outlines the research conducted on '{source_title}', including methodology, key findings, and recommendations for future action."
        else:
            return f"This summary captures the essential information from '{source_title}' for reference and follow-up."
    
    def _generate_analysis(self, summary_type: str, key_points: List[str], focus_areas: List[str]) -> str:
        """Generate analysis section."""
        if not key_points and not focus_areas:
            return "Analysis to be completed based on additional information."
        
        analysis = "## Analysis\n\n"
        
        if focus_areas:
            analysis += "### Focus Areas\n"
            for area in focus_areas:
                analysis += f"- **{area}**: Detailed analysis of this area\n"
            analysis += "\n"
        
        if key_points:
            analysis += "### Key Insights\n"
            for point in key_points[:3]:  # Limit to top 3 points
                analysis += f"- {point}\n"
        
        return analysis
    
    def _generate_conclusions(self, summary_type: str, key_points: List[str]) -> str:
        """Generate conclusions section."""
        if summary_type == 'research':
            return "Research findings support the proposed approach with identified areas for further investigation."
        elif summary_type == 'project':
            return "Project is progressing according to plan with manageable risks and challenges."
        else:
            return "Key insights provide valuable guidance for decision-making and future planning."
    
    def _generate_recommendations(self, summary_type: str, key_points: List[str]) -> str:
        """Generate recommendations section."""
        recommendations = "## Recommendations\n\n"
        recommendations += "1. **Immediate Actions**: Address high-priority items identified in the summary\n"
        recommendations += "2. **Follow-up**: Schedule regular reviews and updates as needed\n"
        recommendations += "3. **Documentation**: Maintain records of decisions and progress\n"
        
        return recommendations
    
    def _generate_executive_summary(self, summary_type: str, source_title: str, key_points: List[str], attendees: List[str]) -> str:
        """Generate executive-style summary."""
        participant_info = f" with {len(attendees)} participants" if attendees else ""
        
        return f"Completed {summary_type} summary for '{source_title}'{participant_info}. " + \
               f"{'Key decisions made and action items assigned.' if summary_type == 'meeting' else 'Primary findings documented with recommendations.'} " + \
               f"{'No blocking issues identified.' if key_points else 'Detailed analysis available for review.'}"
    
    def _generate_detailed_conversational_summary(self, summary_type: str, source_title: str, key_points: List[str], focus_areas: List[str]) -> str:
        """Generate detailed conversational summary."""
        summary = f"Here's a comprehensive summary of our {summary_type} on '{source_title}': "
        
        if key_points:
            summary += f"We covered {len(key_points)} main areas. "
            if len(key_points) >= 2:
                summary += f"The top priorities were {key_points[0]} and {key_points[1]}. "
        
        if focus_areas:
            summary += f"Our focus was specifically on {', '.join(focus_areas[:2])}. "
        
        if summary_type == 'meeting':
            summary += "All decisions are documented with clear action items and owners assigned."
        else:
            summary += "The analysis includes detailed findings and specific recommendations for next steps."
        
        return summary
    
    def _generate_casual_summary(self, summary_type: str, source_title: str, key_points: List[str], attendees: List[str]) -> str:
        """Generate casual-style summary."""
        return f"Just wrapped up the {summary_type} on '{source_title}'. " + \
               f"{'Good discussion with the team' if attendees else 'Covered all the important stuff'}. " + \
               f"{'Made some solid decisions and got action items sorted' if summary_type == 'meeting' else 'Got the key insights documented'}. " + \
               f"Everything's captured in the detailed summary if you need the specifics."
    
    def _extract_top_decisions(self, key_points: List[str], limit: int = 2) -> str:
        """Extract top decisions for hybrid summary."""
        decisions = [point for point in key_points if any(word in point.lower() for word in ['decided', 'agreed', 'approved'])]
        
        if not decisions:
            return "Main topics discussed with clear outcomes documented."
        
        if len(decisions) == 1:
            return f"Key decision: {decisions[0]}"
        else:
            return f"Main decisions: {decisions[0]} and {decisions[1] if len(decisions) > 1 else 'additional items addressed'}."
    
    def _extract_top_insights(self, key_points: List[str], focus_areas: List[str], limit: int = 2) -> str:
        """Extract top insights for hybrid summary."""
        if key_points:
            if len(key_points) == 1:
                return f"Key insight: {key_points[0]}"
            else:
                return f"Main findings: {key_points[0]} and {key_points[1] if len(key_points) > 1 else 'supporting analysis completed'}."
        elif focus_areas:
            return f"Analysis focused on {', '.join(focus_areas[:2])} with detailed findings documented."
        else:
            return "Comprehensive analysis completed with actionable insights identified."
    
    def actions_definitions_prompt(self) -> str:
        prompt = """
        - GENERATE_DOCUMENT: Generate a comprehensive summary document. Content must include:
          * summary_type: Type of summary (meeting, document, project, research)
          * source_title: Title or name of what is being summarized
          * source_content: Original content to summarize (optional)
          * key_points: List of key points or topics covered
          * attendees: List of participants (for meetings)
          * duration: Duration or timeframe (optional)
          * focus_areas: Specific areas of focus (optional)
          
        - GENERATE_SUMMARY: Generate a conversational summary. Content must include:
          * summary_type: Type of summary (meeting, document, project, research)
          * source_title: Title or name of what is being summarized
          * key_points: List of key points or topics covered
          * style: Summary style (executive, detailed, casual)
          * length: Summary length (brief, detailed)
        """
        return utils.dedent(prompt)
    
    def actions_constraints_prompt(self) -> str:
        prompt = """
        - Summaries must capture the essential information accurately
        - Include specific action items and decisions when summarizing meetings
        - Maintain appropriate level of detail for the intended audience
        - Reference source materials and participants when relevant
        - Store detailed summaries for future reference and follow-up
        - Use clear, concise language appropriate for the summary type
        """
        return utils.dedent(prompt)