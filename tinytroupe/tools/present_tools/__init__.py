"""
Present-enabled tools for the TinyTroupe Present Feature.

This package contains specialized tools that support dual output modes
(PRESENT for detailed documents, TALK for conversational summaries).
"""

from .compliance_report_tool import ComplianceReportTool
from .technical_memo_tool import TechnicalMemoTool
from .summary_tool import SummaryTool

__all__ = [
    'ComplianceReportTool',
    'TechnicalMemoTool', 
    'SummaryTool'
]