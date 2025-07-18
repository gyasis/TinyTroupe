"""
Compliance Report Tool for the TinyTroupe Present Feature

This tool generates compliance reports (HIPAA, SOX, etc.) in both detailed 
document format and conversational summary format.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from tinytroupe.tools import logger
from tinytroupe.tools.tool_orchestrator import PresentTool, OutputMode
from tinytroupe.tools.document_manager import global_document_repository
import tinytroupe.utils as utils


class ComplianceReportTool(PresentTool):
    """
    Tool for generating compliance reports with dual output modes.
    
    Supports detailed compliance reports for documentation and 
    conversational summaries for meetings and quick updates.
    """
    
    def __init__(self, owner=None, exporter=None, enricher=None):
        super().__init__(
            name="compliance_report",
            description="Generate compliance reports (HIPAA, SOX, PCI-DSS, etc.) in detailed or summary format",
            owner=owner,
            real_world_side_effects=False,
            exporter=exporter,
            enricher=enricher,
            supported_modes=[OutputMode.PRESENT, OutputMode.TALK, OutputMode.HYBRID]
        )
        
        # Compliance area knowledge base
        self.compliance_areas = {
            "hipaa": {
                "name": "HIPAA (Health Insurance Portability and Accountability Act)",
                "key_areas": [
                    "Physical Safeguards",
                    "Administrative Safeguards", 
                    "Technical Safeguards",
                    "Breach Notification",
                    "Business Associate Agreements"
                ],
                "common_violations": [
                    "Unsecured PHI transmission",
                    "Inadequate access controls",
                    "Missing audit logs",
                    "Insufficient staff training"
                ]
            },
            "sox": {
                "name": "Sarbanes-Oxley Act",
                "key_areas": [
                    "Internal Controls",
                    "Financial Reporting",
                    "Auditor Independence",
                    "Corporate Governance"
                ],
                "common_violations": [
                    "Inadequate internal controls",
                    "Financial misstatements", 
                    "Insufficient documentation",
                    "Management override"
                ]
            },
            "pci_dss": {
                "name": "PCI Data Security Standard",
                "key_areas": [
                    "Secure Network",
                    "Protect Cardholder Data",
                    "Vulnerability Management",
                    "Access Control",
                    "Network Monitoring",
                    "Information Security Policy"
                ],
                "common_violations": [
                    "Unencrypted card data",
                    "Default passwords",
                    "Insufficient access controls",
                    "Missing security patches"
                ]
            }
        }
    
    def _process_present_action(self, agent, action: dict, output_mode: OutputMode) -> Dict[str, Any]:
        """Process compliance report generation in specified output mode."""
        
        try:
            content = action.get('content', {})
            if isinstance(content, str):
                content = utils.extract_json(content)
            
            # Extract parameters
            compliance_type = content.get('compliance_type', 'hipaa').lower()
            organization = content.get('organization', 'Unknown Organization')
            assessment_period = content.get('assessment_period', 'Q1 2024')
            findings = content.get('findings', [])
            status = content.get('status', 'in_progress')
            
            # Validate compliance type
            if compliance_type not in self.compliance_areas:
                raise ValueError(f"Unsupported compliance type: {compliance_type}")
            
            compliance_info = self.compliance_areas[compliance_type]
            
            if output_mode == OutputMode.PRESENT:
                return self._generate_detailed_report(
                    agent, compliance_type, compliance_info, organization, 
                    assessment_period, findings, status, content
                )
            elif output_mode == OutputMode.TALK:
                return self._generate_conversational_summary(
                    agent, compliance_type, compliance_info, organization,
                    assessment_period, findings, status, content
                )
            elif output_mode == OutputMode.HYBRID:
                return self._generate_hybrid_output(
                    agent, compliance_type, compliance_info, organization,
                    assessment_period, findings, status, content
                )
            else:
                raise ValueError(f"Unsupported output mode: {output_mode}")
                
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {
                "content": f"Error generating compliance report: {str(e)}",
                "format": "text",
                "references": [],
                "confidence_score": 0.0
            }
    
    def _generate_detailed_report(self, agent, compliance_type, compliance_info, 
                                organization, assessment_period, findings, status, params) -> Dict[str, Any]:
        """Generate a detailed compliance report document."""
        
        # Prepare template parameters
        template_params = {
            "title": f"{compliance_info['name']} Compliance Assessment",
            "author": agent.name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "report_type": compliance_info['name'],
            "organization": organization,
            "assessment_period": assessment_period,
            "executive_summary": self._generate_executive_summary(compliance_type, status, findings),
            "compliance_areas": self._format_compliance_areas(compliance_info['key_areas']),
            "findings": self._format_findings(findings, compliance_info['common_violations']),
            "recommendations": self._generate_recommendations(compliance_type, findings),
            "next_steps": self._generate_next_steps(status, compliance_type),
            "tool_name": self.name
        }
        
        # Store in document repository
        doc_id = global_document_repository.store_document(
            title=template_params["title"],
            content="",  # Will be filled by template
            author=agent.name,
            doc_type="compliance_report",
            format="markdown",
            tags=[compliance_type, "compliance", "report"],
            template_name="compliance_report",
            template_params=template_params,
            tool_generated=self.name
        )
        
        # Store reference in agent memory
        agent.store_memory(f"Generated compliance report: {template_params['title']} (ID: {doc_id})")
        
        return {
            "content": f"Detailed {compliance_info['name']} compliance report generated",
            "format": "markdown",
            "document_id": doc_id,
            "references": [f"Compliance Standards: {compliance_info['name']}"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Generated comprehensive compliance report for {organization} covering {len(compliance_info['key_areas'])} key areas"
        }
    
    def _generate_conversational_summary(self, agent, compliance_type, compliance_info,
                                       organization, assessment_period, findings, status, params) -> Dict[str, Any]:
        """Generate a conversational summary of compliance status."""
        
        summary_style = params.get('style', 'executive')
        
        if summary_style == 'executive':
            summary = self._generate_executive_style_summary(compliance_type, compliance_info, organization, status, findings)
        elif summary_style == 'technical':
            summary = self._generate_technical_style_summary(compliance_type, compliance_info, organization, status, findings)
        else:
            summary = self._generate_casual_style_summary(compliance_type, compliance_info, organization, status, findings)
        
        # Store in agent memory for reference
        agent.store_memory(f"Discussed {compliance_info['name']} compliance status for {organization}")
        
        return {
            "content": summary,
            "format": "text",
            "references": [f"Compliance Assessment: {organization} - {assessment_period}"],
            "confidence_score": 0.85,
            "reasoning_trace": f"Summarized {compliance_type} compliance status focusing on {summary_style} perspective"
        }
    
    def _generate_hybrid_output(self, agent, compliance_type, compliance_info,
                              organization, assessment_period, findings, status, params) -> Dict[str, Any]:
        """Generate hybrid output with summary and document reference."""
        
        # First generate the detailed report
        detailed_result = self._generate_detailed_report(
            agent, compliance_type, compliance_info, organization,
            assessment_period, findings, status, params
        )
        
        # Then create a summary with reference to the detailed report
        doc_id = detailed_result.get('document_id')
        
        hybrid_summary = f"""I've completed our {compliance_info['name']} compliance assessment for {organization}. 

Here's the key takeaway: We're currently {status} with our compliance efforts. The assessment covered {len(compliance_info['key_areas'])} critical areas including {', '.join(compliance_info['key_areas'][:3])}.

{'We identified several areas needing attention.' if findings else 'No significant issues were found.'}

I've prepared a comprehensive report with all the details, recommendations, and next steps. You can reference the full document (ID: {doc_id}) for the complete analysis, or I can dive deeper into any specific area you'd like to discuss."""
        
        return {
            "content": hybrid_summary,
            "format": "text",
            "document_id": doc_id,
            "references": [f"Detailed Report: {doc_id}", f"Compliance Standards: {compliance_info['name']}"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Provided hybrid summary with reference to detailed compliance report {doc_id}"
        }
    
    def _generate_executive_summary(self, compliance_type, status, findings) -> str:
        """Generate executive summary for the report."""
        findings_count = len(findings) if findings else 0
        
        if status == 'compliant':
            summary = f"This assessment confirms that our organization maintains compliance with {compliance_type.upper()} regulations."
        elif status == 'non_compliant':
            summary = f"This assessment identifies {findings_count} areas where our organization does not currently meet {compliance_type.upper()} requirements."
        else:
            summary = f"This assessment reviews our organization's progress toward {compliance_type.upper()} compliance, identifying {findings_count} areas for improvement."
        
        summary += f" The assessment covers all required compliance areas and provides specific recommendations for maintaining or achieving full compliance."
        
        return summary
    
    def _format_compliance_areas(self, areas: List[str]) -> str:
        """Format compliance areas for the report."""
        formatted = ""
        for i, area in enumerate(areas, 1):
            formatted += f"{i}. **{area}**\n   - Assessment completed\n   - Documentation reviewed\n   - Controls evaluated\n\n"
        return formatted
    
    def _format_findings(self, findings: List[str], common_violations: List[str]) -> str:
        """Format findings for the report."""
        if not findings:
            return "No significant compliance issues were identified during this assessment."
        
        formatted = ""
        for i, finding in enumerate(findings, 1):
            formatted += f"### Finding {i}: {finding}\n"
            formatted += f"**Severity**: Medium\n"
            formatted += f"**Impact**: Potential compliance violation\n"
            formatted += f"**Status**: Open\n\n"
        
        return formatted
    
    def _generate_recommendations(self, compliance_type, findings) -> str:
        """Generate recommendations based on findings."""
        if not findings:
            return "Continue current compliance practices and conduct regular assessments."
        
        recommendations = f"Based on the assessment findings, we recommend the following actions:\n\n"
        recommendations += f"1. **Immediate Actions**: Address high-priority findings within 30 days\n"
        recommendations += f"2. **Process Improvements**: Implement enhanced controls and monitoring\n" 
        recommendations += f"3. **Training**: Conduct staff training on {compliance_type.upper()} requirements\n"
        recommendations += f"4. **Documentation**: Update policies and procedures as needed\n"
        recommendations += f"5. **Monitoring**: Establish ongoing compliance monitoring processes\n"
        
        return recommendations
    
    def _generate_next_steps(self, status, compliance_type) -> str:
        """Generate next steps based on current status."""
        if status == 'compliant':
            return f"1. Schedule next compliance assessment\n2. Monitor for regulatory changes\n3. Maintain current controls"
        else:
            return f"1. Develop remediation plan\n2. Assign ownership for each finding\n3. Set target completion dates\n4. Schedule follow-up assessment"
    
    def _generate_executive_style_summary(self, compliance_type, compliance_info, organization, status, findings):
        """Generate executive-style summary."""
        return f"Our {compliance_info['name']} compliance assessment shows we're {status}. " + \
               f"{'No critical issues identified.' if not findings else f'{len(findings)} areas need attention.'} " + \
               f"I recommend {'continuing our current practices' if status == 'compliant' else 'implementing the remediation plan'} to maintain compliance."
    
    def _generate_technical_style_summary(self, compliance_type, compliance_info, organization, status, findings):
        """Generate technical-style summary."""
        return f"Completed {compliance_type.upper()} assessment covering {len(compliance_info['key_areas'])} control areas. " + \
               f"Current status: {status}. " + \
               f"{'All technical controls validated.' if not findings else f'Identified {len(findings)} technical gaps requiring remediation.'} " + \
               f"Detailed findings and technical recommendations are documented in the full report."
    
    def _generate_casual_style_summary(self, compliance_type, compliance_info, organization, status, findings):
        """Generate casual-style summary."""
        return f"Just finished reviewing our {compliance_type.upper()} compliance. " + \
               f"Good news: we're {status}! " + \
               f"{'Everything looks solid.' if not findings else f'Found a few things to clean up - nothing major.'} " + \
               f"Happy to discuss any specific areas you're curious about."
    
    def actions_definitions_prompt(self) -> str:
        prompt = """
        - GENERATE_DOCUMENT: Generate a comprehensive compliance report. Content must include:
          * compliance_type: Type of compliance (hipaa, sox, pci_dss)
          * organization: Organization name
          * assessment_period: Time period for assessment
          * findings: List of compliance findings (optional)
          * status: Current compliance status (compliant, non_compliant, in_progress)
          
        - GENERATE_SUMMARY: Generate a conversational compliance summary. Content must include:
          * compliance_type: Type of compliance (hipaa, sox, pci_dss)
          * organization: Organization name
          * style: Summary style (executive, technical, casual)
          * status: Current compliance status
        """
        return utils.dedent(prompt)
    
    def actions_constraints_prompt(self) -> str:
        prompt = """
        - Compliance reports must be accurate and based on established standards
        - Always specify the compliance framework being assessed
        - Include specific, actionable recommendations
        - Maintain professional tone in all compliance communications
        - Store detailed reports for future reference and auditing
        """
        return utils.dedent(prompt)