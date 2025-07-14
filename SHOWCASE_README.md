# TinyTroupe 3-Day Business Simulation Showcase

This directory contains comprehensive demonstration scripts that showcase ALL of TinyTroupe's advanced features through realistic 3-day business simulations.

## 🎯 Scripts Overview

### 1. `comprehensive_3day_simulation.py` (Full Feature Demo)
The most complete demonstration showcasing every TinyTroupe capability:
- **MCP Integration**: External tool access via MCP servers
- **Present Feature**: Professional document generation
- **Adaptive Agents**: Context-aware behavior
- **Async Orchestration**: Concurrent agent processing
- **CEO Dashboard**: Real-time business monitoring
- **CEO Interrupt**: Interactive simulation control
- **Agent Orchestrator**: JSON-driven project management
- **Context Detection**: Intelligent meeting behavior

**Scenario**: HealthChain Dynamics, a healthcare blockchain startup, preparing for investor demo

### 2. `simple_3day_showcase.py` (No External Dependencies)
A simplified version that demonstrates core features without requiring MCP servers:
- **Present Feature**: Document generation and sharing
- **Adaptive Agents**: Smart meeting behavior
- **Async World**: Concurrent meetings
- **CEO Dashboard**: Business monitoring
- **Clean Display**: Readable output formatting

**Scenario**: TechVenture AI, an enterprise AI platform, planning Q4 strategy

## 🚀 Quick Start

### Running the Simple Showcase (Recommended for First Run)
```bash
python simple_3day_showcase.py
```

This will:
- Create a 5-person startup team
- Run 3 days of strategic meetings
- Generate documents using Present Feature
- Display real-time CEO Dashboard
- Save results to `techventure_results.json`

### Running the Comprehensive Simulation
```bash
# First, ensure you have MCP servers available (optional)
# uvx mcp-server-filesystem
# uvx mcp-server-git

python comprehensive_3day_simulation.py
```

This demonstrates:
- Full MCP integration with external tools
- Agent Orchestrator with task dependencies
- CEO Interrupt system (press SPACEBAR)
- Complete Present Feature capabilities
- All async features

## 📊 Features Demonstrated

### Day 1: Planning & Foundation
- Strategic planning meetings with adaptive agents
- Document generation (compliance reports, technical specs)
- MCP tool usage for code analysis
- Context-aware meeting behavior

### Day 2: Development & Integration  
- Async standup meetings
- Security review sessions
- Concurrent agent work
- Present Feature for investor materials
- Task orchestration and tracking

### Day 3: Integration & Demo Prep
- Final integration meetings
- Demo preparation with full team
- CEO interrupt capability
- Comprehensive reporting
- Sprint retrospective

## 🔧 Key Components Used

### Agent Types
```python
# Standard Adaptive Agent
ceo = create_adaptive_agent("Sarah Chen", "CEO")

# MCP-Enabled Present Agent  
cto = create_mcp_present_adaptive_agent("Dr. James Wilson", "CTO")

# Present-Enabled Agent
pm = create_present_adaptive_agent("Emily Martinez", "Product Manager")

# Async Adaptive Agent
dev = AsyncAdaptiveTinyPerson("Alex Kumar")
```

### Meeting Patterns
```python
# Async meeting with broadcasting
world = AsyncTinyWorld("Sprint Planning", is_meeting=True)
await world.run_async(4)

# Context detection for appropriate behavior
# Automatically adjusts based on meeting type
```

### Document Generation
```python
# Present Feature for reports
agent.act({
    "type": "PRESENT",
    "content": {
        "tool": "compliance_report",
        "topic": "HIPAA Compliance Assessment",
        "format": "markdown"
    }
})
```

### MCP Tool Usage
```python
# External tool access via MCP
agent.act({
    "type": "MCP_GIT_LOG",
    "content": {
        "tool": "mcp_git_log",
        "arguments": {"max_commits": 20},
        "output_mode": "present"
    }
})
```

## 📈 Output Examples

### CEO Dashboard
```
╔════════════════════════════════════════════════════════════╗
║             🏢 HealthChain Sprint Dashboard                ║
╠════════════════════════════════════════════════════════════╣
║ Company: HealthChain Dynamics                              ║
║ Industry: Healthcare Blockchain | Stage: Seed              ║
╠════════════════════════════════════════════════════════════╣
║ 📊 Key Metrics                                             ║
║ Sprint Day: 3/3            Documents Generated: 6          ║
║ Tasks Completed: 9/9       Sprint Completion: 100%         ║
╚════════════════════════════════════════════════════════════╝
```

### Clean Agent Communication
```
Sarah Chen --> All: Good morning everyone! Welcome to our 3-day MVP sprint.
Dr. James Wilson: I'll ensure our blockchain architecture is investor-ready.
Michael Thompson: I'll complete the HIPAA compliance review today.
```

### Generated Documents
- Technical Architecture (Markdown)
- HIPAA Compliance Report (Detailed)
- Investor Presentation (Executive Summary)
- Sprint Summary Report (Comprehensive)

## 🎮 Interactive Features

### CEO Interrupt (Full Demo Only)
Press **SPACEBAR** during simulation to:
- Pause/resume execution
- Check agent status
- Skip to next task
- Adjust priorities
- Get real-time updates

### Async Processing
Watch agents think and communicate simultaneously:
- Parallel meeting discussions
- Concurrent document generation
- Real-time status updates

## 📂 Output Files

Both simulations generate:
- `*.cache.json` - Simulation state cache
- `*_results.json` - Comprehensive results and metrics
- Console output with meeting transcripts
- Generated documents (in agent memories)

## 🔍 Customization

### Modify Team Composition
Edit the team creation functions to add different roles:
```python
data_scientist = create_adaptive_agent("Dr. Lisa Park", "Data Scientist")
```

### Adjust Meeting Length
Change the number of rounds:
```python
await world.run_async(6)  # Longer meeting
```

### Add Custom Documents
Create new Present Feature tools:
```python
agent.act({
    "type": "PRESENT",
    "content": {
        "tool": "custom_report",
        "topic": "Your Topic Here"
    }
})
```

## 🚨 Troubleshooting

### MCP Servers Not Found
The comprehensive demo will gracefully continue without MCP servers. To fully experience MCP features, install:
```bash
pip install mcp
uvx mcp-server-filesystem
uvx mcp-server-git
```

### Import Errors
Ensure all TinyTroupe features are properly installed:
```bash
cd /path/to/tinytroupe
pip install -e .
```

### API Key Issues
Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-key-here"
```

## 🎯 Learning Path

1. **Start Simple**: Run `simple_3day_showcase.py` first
2. **Explore Features**: Read the generated JSON results
3. **Go Comprehensive**: Try `comprehensive_3day_simulation.py`
4. **Customize**: Modify scenarios for your use case
5. **Build Your Own**: Use these as templates for your simulations

## 📚 Related Documentation

- [CLAUDE.md](CLAUDE.md) - Complete feature documentation
- [Present Feature](tinytroupe/tools/README.md) - Document generation details
- [MCP Integration](tinytroupe/mcp_integration.py) - External tool access
- [CEO Dashboard](tinytroupe/ceo_dashboard.py) - Monitoring capabilities
- [Agent Orchestrator](tinytroupe/agent_orchestrator.py) - Project management

## 🎉 Summary

These showcase scripts demonstrate how TinyTroupe can simulate complex business scenarios with:
- Realistic multi-agent interactions
- Professional document generation
- External tool integration
- Real-time monitoring and control
- Asynchronous processing for scale

Perfect for:
- Testing business strategies
- Training scenarios
- Process optimization
- Decision simulation
- Team dynamics research

Enjoy exploring the full power of TinyTroupe! 🚀