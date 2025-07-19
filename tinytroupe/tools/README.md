# TinyTroupe Document Management & Tool Orchestration

This directory contains the core infrastructure for TinyTroupe's document generation and tool management capabilities.

## 📋 Overview

The tools system provides agents with the ability to:
- Generate structured documents (compliance reports, technical memos, summaries)
- Share documents between agents with access control
- Dynamically select tools based on agent roles and context
- Track tool usage with full provenance logging

## 🏗️ Core Components

### Tool Orchestrator (`tool_orchestrator.py`)

The central hub for all tool management in TinyTroupe.

**Key Features:**
- **Tool Registration**: Register custom tools with metadata and permissions
- **Role-Based Access**: Assign tools to agents based on their roles
- **Output Modes**: Support for PRESENT (detailed), TALK (conversational), and HYBRID modes
- **Provenance Tracking**: Complete logging of tool usage with reasoning traces
- **Context Awareness**: Suggest appropriate tools based on meeting context

**Usage Example:**
```python
from tinytroupe.tools.tool_orchestrator import ToolOrchestrator

# Get the singleton instance
orchestrator = ToolOrchestrator()

# Register a custom tool
orchestrator.register_tool(
    tool_id="custom_analysis",
    name="Custom Analysis Tool",
    description="Performs custom data analysis",
    tool_class=CustomAnalysisTool,
    supported_roles=["data_analyst", "researcher"],
    supported_output_modes=["present", "talk", "hybrid"]
)

# Execute a tool
result = orchestrator.execute_tool(
    agent_id="agent_123",
    agent_role="data_analyst",
    tool_id="custom_analysis",
    parameters={"data": data, "analysis_type": "regression"},
    output_mode="present"
)
```

### Document Manager (`document_manager.py`)

Comprehensive document lifecycle management system.

**Key Features:**
- **SharedDocumentRepository**: Centralized storage with access control
- **Full-Text Search**: Find documents by content, not just metadata
- **Template Management**: Mustache-based templates for consistent formatting
- **Metadata Indexing**: Rich metadata for categorization and retrieval
- **Access Control**: Role-based permissions for document sharing

**Usage Example:**
```python
from tinytroupe.tools.document_manager import DocumentManager, SharedDocumentRepository

# Create a document manager
doc_manager = DocumentManager()

# Generate a document from a template
doc_id = doc_manager.create_from_template(
    template_name="compliance_report",
    data={
        "regulation": "HIPAA",
        "findings": findings_list,
        "recommendations": recommendations
    },
    metadata={
        "author": "compliance_agent",
        "department": "compliance",
        "priority": "high"
    }
)

# Share with repository
shared_repo = SharedDocumentRepository()
shared_repo.share_document(
    doc_id=doc_id,
    shared_by="compliance_agent",
    shared_with=["cto_agent", "legal_agent"],
    permissions=["read", "comment"]
)

# Search documents
results = shared_repo.search_documents(
    query="HIPAA compliance",
    filters={"department": "compliance"},
    shared_with="cto_agent"
)
```

## 🛠️ Present Tools

The `present_tools/` directory contains specialized document generation tools:

### ComplianceReportTool
Generates compliance reports for various regulations:
- HIPAA (Healthcare)
- SOX (Financial)
- PCI-DSS (Payment Card)
- Custom compliance frameworks

### TechnicalMemoTool
Creates technical documentation:
- Architecture Decision Records (ADRs)
- Technical Specifications
- System Analysis Reports
- Performance Assessments

### SummaryTool
Produces various types of summaries:
- Meeting Minutes
- Project Status Reports
- Research Abstracts
- Executive Summaries

## 🔧 Integration with Agents

### Using with PresentAdaptiveTinyPerson

```python
from tinytroupe.present_adaptive_agent import create_present_adaptive_agent

# Create an agent with present capabilities
agent = create_present_adaptive_agent("Sarah Chen", "Compliance Officer")

# Agent automatically has access to compliance tools
agent.act({
    "type": "PRESENT",
    "content": {
        "tool": "compliance_report",
        "topic": "Q4 HIPAA Compliance Audit",
        "format": "detailed_report",
        "parameters": {
            "regulation": "HIPAA",
            "period": "Q4 2024"
        }
    }
})
```

### Role-Based Tool Assignment

Tools are automatically assigned based on agent roles:

```python
# Role mappings (defined in tool_orchestrator.py)
ROLE_TOOL_MAPPING = {
    "compliance_officer": ["compliance_report", "summary"],
    "technical_lead": ["technical_memo", "summary"],
    "project_manager": ["summary", "project_report"],
    "researcher": ["research_summary", "technical_memo"]
}
```

## 📊 Output Modes

### PRESENT Mode
Full detailed documents with complete structure:
```python
result = orchestrator.execute_tool(
    tool_id="compliance_report",
    output_mode="present"
)
# Returns: Full multi-page compliance report
```

### TALK Mode
Conversational summary for meetings:
```python
result = orchestrator.execute_tool(
    tool_id="compliance_report",
    output_mode="talk"
)
# Returns: "I've completed the HIPAA audit. We found 3 minor issues..."
```

### HYBRID Mode
Summary with reference to detailed document:
```python
result = orchestrator.execute_tool(
    tool_id="compliance_report",
    output_mode="hybrid"
)
# Returns: Brief summary + "See document #CR-2024-001 for details"
```

## 🔍 Provenance & Logging

All tool usage is tracked:

```python
# View tool usage history
history = orchestrator.get_provenance_log(
    agent_id="agent_123",
    time_range=("2024-01-01", "2024-12-31")
)

# Get tool statistics
stats = orchestrator.get_tool_statistics()
```

## 🚀 Creating Custom Tools

To create a custom tool:

1. Inherit from `BasePresentTool`:
```python
from tinytroupe.tools.present_tools import BasePresentTool

class CustomReportTool(BasePresentTool):
    def generate_present_output(self, agent_context, parameters):
        # Generate detailed document
        return {
            "content": detailed_report,
            "metadata": {...}
        }
    
    def generate_talk_output(self, agent_context, parameters):
        # Generate conversational summary
        return f"I've created a {parameters['report_type']} report..."
```

2. Register with orchestrator:
```python
orchestrator.register_tool(
    tool_id="custom_report",
    tool_class=CustomReportTool,
    supported_roles=["analyst"]
)
```

## 📚 Best Practices

1. **Use Appropriate Output Modes**: 
   - PRESENT for formal documentation
   - TALK for meeting discussions
   - HYBRID for executive communications

2. **Leverage Templates**: Create reusable templates for consistent formatting

3. **Set Proper Metadata**: Include author, date, tags for better searchability

4. **Role-Based Access**: Ensure tools match agent capabilities

5. **Monitor Provenance**: Track tool usage for compliance and optimization

## 🔗 Related Documentation

- [Present Feature Overview](../../PRESENT_FEATURE_SUMMARY.md)
- [Agent Integration Guide](../../tinytroupe/agent/README.md)
- [TinyTroupe Main Documentation](../../README.md)