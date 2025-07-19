#!/usr/bin/env python3
"""
Comprehensive 3-Day Business Simulation Showcase
================================================

This script demonstrates ALL TinyTroupe features in a realistic 3-day business simulation:
- MCP (Model Context Protocol) integration for external tool access
- Present Feature for document generation and sharing
- Adaptive agents with context-aware behavior
- Async orchestration with concurrent processing
- CEO Dashboard for real-time monitoring
- CEO Interrupt system for simulation control
- Context detection for appropriate meeting behavior
- Agent Orchestrator for JSON-driven project management

The simulation follows a healthcare blockchain startup through 3 days of intensive work.
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any


class TeeLogger:
    """Logger that writes to both console and file simultaneously."""
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()  # Ensure immediate writing

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()

# Core TinyTroupe imports
from tinytroupe import control
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from tinytroupe.extraction import ResultsExtractor

# Advanced features
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.async_adaptive_agent import AsyncAdaptiveTinyPerson
from tinytroupe.async_world import AsyncTinyWorld
from tinytroupe.agent_orchestrator import AgentOrchestrator
from tinytroupe.ceo_dashboard import CEODashboard
from tinytroupe.ceo_interrupt import CEOInterruptHandler
from tinytroupe.context_detection import ContextDetector

# Present Feature and MCP imports
from tinytroupe.mcp_present_agent import create_mcp_present_adaptive_agent
from tinytroupe.mcp_integration import mcp_integration_manager
from tinytroupe.tools.tool_orchestrator import global_tool_orchestrator

# Utilities
from tinytroupe.utils import JsonSerializableRegistry

# Set up clean display mode for readable output
TinyPerson.rich_text_display = False
TinyWorld.rich_text_display = False
TinyPerson.debug_display = False
TinyWorld.debug_display = False
TinyPerson.communication_style = "simplified"


async def setup_mcp_servers():
    """Configure and connect to MCP servers for external tool access."""
    print("\n🔧 Setting up MCP servers...")
    
    # Configure filesystem MCP server
    mcp_integration_manager.configure_mcp_server(
        name="filesystem",
        command=["uvx", "mcp-server-filesystem", "--directory", "."]
    )
    
    # Configure git MCP server
    mcp_integration_manager.configure_mcp_server(
        name="git", 
        command=["uvx", "mcp-server-git", "--repository", "."]
    )
    
    # Note: In a real scenario, you might also configure:
    # - Database MCP server for data access
    # - API MCP server for external service integration
    # - Cloud storage MCP server for document management
    
    try:
        await mcp_integration_manager.connect_to_servers()
        status = mcp_integration_manager.get_integration_status()
        print(f"✅ Connected to {len(status['connected_servers'])} MCP servers")
        print(f"📊 Available MCP tools: {status['total_mcp_tools']}")
    except Exception as e:
        print(f"⚠️  MCP server connection skipped (servers may not be installed): {e}")
        print("   Continuing with built-in tools only...")


async def create_team_members():
    """Create the startup team with all advanced capabilities."""
    print("\n👥 Creating the HealthChain Dynamics team...")
    
    # CEO - Uses standard adaptive agent (monitors everything)
    ceo = create_adaptive_agent("Sarah Chen", "CEO and Founder")
    ceo.define("expertise_domains", [{
        "domain": "Healthcare Technology Leadership",
        "competency_level": "Expert",
        "specific_knowledge": "Healthcare regulations, blockchain applications, startup growth"
    }])
    
    # CTO - MCP-enabled for technical tool access
    cto = create_mcp_present_adaptive_agent("Dr. James Wilson", "Chief Technology Officer")
    cto.define("expertise_domains", [{
        "domain": "Blockchain Architecture",
        "competency_level": "Expert", 
        "specific_knowledge": "Smart contracts, distributed systems, healthcare integration"
    }])
    
    # Compliance Officer - MCP-enabled for regulatory tools
    compliance = create_mcp_present_adaptive_agent("Michael Thompson", "Compliance Officer")
    compliance.define("expertise_domains", [{
        "domain": "Healthcare Compliance",
        "competency_level": "Expert",
        "specific_knowledge": "HIPAA, FDA regulations, blockchain compliance, audit procedures"
    }])
    
    # Product Manager - Present Feature enabled
    from tinytroupe.present_adaptive_agent import create_present_adaptive_agent
    pm = create_present_adaptive_agent("Emily Martinez", "Product Manager")
    pm.define("expertise_domains", [{
        "domain": "Product Strategy",
        "competency_level": "Expert",
        "specific_knowledge": "User research, roadmap planning, stakeholder management"
    }])
    
    # Lead Developer - Async-enabled for concurrent work
    dev_lead = AsyncAdaptiveTinyPerson("Alex Kumar")
    dev_lead.define("occupation", "Lead Blockchain Developer")
    dev_lead.define("expertise_domains", [{
        "domain": "Smart Contract Development",
        "competency_level": "Expert",
        "specific_knowledge": "Solidity, Web3, healthcare data systems"
    }])
    
    # Data Scientist - Standard agent
    data_scientist = TinyPerson("Dr. Lisa Park")
    data_scientist.define("occupation", "Healthcare Data Scientist")
    data_scientist.define_several("interests", [
        {"interest": "Medical data privacy"},
        {"interest": "Predictive analytics"},
        {"interest": "Blockchain data integrity"}
    ])
    
    return {
        "ceo": ceo,
        "cto": cto,
        "compliance": compliance,
        "pm": pm,
        "dev_lead": dev_lead,
        "data_scientist": data_scientist
    }


def create_project_definition():
    """Create a JSON project definition for the Agent Orchestrator."""
    project = {
        "project_id": "healthchain_mvp_sprint",
        "project_name": "HealthChain MVP Development Sprint",
        "description": "3-day intensive sprint to finalize MVP for investor demo",
        "execution_mode": "incremental",
        "scheduling": {
            "mode": "distributed",
            "start_date": datetime.now().isoformat(),
            "working_hours": {"start": "09:00", "end": "18:00"}
        },
        "agents": [
            {
                "agent_id": "ceo",
                "name": "Sarah Chen",
                "role": "CEO and Founder",
                "skill_levels": {
                    "leadership": 10,
                    "strategy": 9,
                    "healthcare_domain": 8
                }
            },
            {
                "agent_id": "cto",
                "name": "Dr. James Wilson",
                "role": "Chief Technology Officer",
                "skill_levels": {
                    "blockchain": 10,
                    "architecture": 9,
                    "security": 8
                }
            },
            {
                "agent_id": "compliance",
                "name": "Michael Thompson",
                "role": "Compliance Officer",
                "skill_levels": {
                    "compliance": 10,
                    "healthcare_regulations": 9,
                    "risk_assessment": 8
                }
            },
            {
                "agent_id": "pm",
                "name": "Emily Martinez",
                "role": "Product Manager",
                "skill_levels": {
                    "product_management": 9,
                    "user_research": 8,
                    "roadmap_planning": 9
                }
            },
            {
                "agent_id": "dev_lead",
                "name": "Alex Kumar",
                "role": "Lead Developer",
                "skill_levels": {
                    "smart_contracts": 9,
                    "web3": 8,
                    "testing": 8
                }
            }
        ],
        "tasks": [
            # Day 1 Tasks
            {
                "task_id": "day1_planning",
                "name": "Sprint Planning Meeting",
                "description": "Kick off 3-day sprint with goals and task allocation",
                "meeting_required": True,
                "attendees": ["ceo", "cto", "pm", "compliance", "dev_lead"],
                "duration_hours": 2,
                "scheduled_date": "Day 1",
                "dependencies": []
            },
            {
                "task_id": "compliance_review",
                "name": "HIPAA Compliance Review",
                "description": "Review current implementation against HIPAA requirements",
                "assigned_to": "compliance",
                "duration_hours": 3,
                "scheduled_date": "Day 1",
                "dependencies": ["day1_planning"],
                "deliverables": ["compliance_report"]
            },
            {
                "task_id": "tech_architecture",
                "name": "Finalize Technical Architecture",
                "description": "Complete architecture documentation for investor presentation",
                "assigned_to": "cto",
                "duration_hours": 4,
                "scheduled_date": "Day 1",
                "dependencies": ["day1_planning"],
                "deliverables": ["architecture_document"]
            },
            # Day 2 Tasks
            {
                "task_id": "day2_standup",
                "name": "Day 2 Standup",
                "description": "Quick sync on progress and blockers",
                "meeting_required": True,
                "attendees": ["ceo", "cto", "pm", "dev_lead"],
                "duration_hours": 0.5,
                "scheduled_date": "Day 2",
                "dependencies": ["compliance_review", "tech_architecture"]
            },
            {
                "task_id": "smart_contract_review",
                "name": "Smart Contract Security Review",
                "description": "Joint review of smart contract implementation",
                "meeting_required": True,
                "attendees": ["cto", "dev_lead", "compliance"],
                "duration_hours": 2,
                "scheduled_date": "Day 2",
                "dependencies": ["day2_standup"]
            },
            {
                "task_id": "investor_deck",
                "name": "Prepare Investor Presentation",
                "description": "Create comprehensive deck showcasing MVP",
                "assigned_to": "pm",
                "duration_hours": 4,
                "scheduled_date": "Day 2",
                "dependencies": ["tech_architecture"],
                "deliverables": ["investor_presentation"]
            },
            # Day 3 Tasks
            {
                "task_id": "day3_integration",
                "name": "Final Integration Meeting",
                "description": "Ensure all components are ready for demo",
                "meeting_required": True,
                "attendees": ["cto", "dev_lead", "pm"],
                "duration_hours": 2,
                "scheduled_date": "Day 3",
                "dependencies": ["smart_contract_review", "investor_deck"]
            },
            {
                "task_id": "demo_prep",
                "name": "Demo Preparation Session",
                "description": "Practice investor demo and address any issues",
                "meeting_required": True,
                "attendees": ["ceo", "cto", "pm", "compliance"],
                "duration_hours": 2,
                "scheduled_date": "Day 3",
                "dependencies": ["day3_integration"]
            },
            {
                "task_id": "final_review",
                "name": "Final Sprint Review",
                "description": "Review accomplishments and prepare for investor meeting",
                "meeting_required": True,
                "attendees": ["ceo", "cto", "pm", "compliance", "dev_lead"],
                "duration_hours": 1,
                "scheduled_date": "Day 3",
                "dependencies": ["demo_prep"]
            }
        ]
    }
    
    return project


async def simulate_day_1(team: Dict, dashboard: CEODashboard):
    """Day 1: Planning and Foundation Work"""
    print("\n" + "="*60)
    print("📅 DAY 1: Sprint Planning and Foundation")
    print("="*60)
    
    # Create async world for Day 1 planning meeting
    world = AsyncTinyWorld("HealthChain Sprint Planning", is_meeting=True)
    
    # Add relevant team members
    world.add_agent(team["ceo"])
    world.add_agent(team["cto"])
    world.add_agent(team["pm"])
    world.add_agent(team["compliance"])
    world.add_agent(team["dev_lead"])
    
    # Update dashboard
    dashboard.update_metric("active_meetings", 1)
    dashboard.update_metric("sprint_day", 1)
    
    # CEO kicks off the meeting
    await world.broadcast(
        f"{team['ceo'].name}: Good morning everyone! Welcome to our 3-day MVP sprint. "
        "We need to finalize everything for the investor demo on Thursday. "
        "Let's review our goals and create a clear action plan."
    )
    
    # Run the planning meeting with async processing
    print("\n🏃 Running Day 1 Planning Meeting (async)...")
    await world.run_async(4)
    
    # After meeting, agents work on their tasks
    print("\n📋 Day 1 Afternoon: Individual Task Work")
    
    # Compliance Officer generates HIPAA compliance report using Present Feature
    print("\n🔍 Michael (Compliance) is reviewing HIPAA compliance...")
    team["compliance"].act({
        "type": "PRESENT",
        "content": {
            "tool": "compliance_report",
            "topic": "HealthChain HIPAA Compliance Assessment",
            "format": "markdown",
            "compliance_type": "hipaa",
            "parameters": {
                "include_gaps": True,
                "risk_assessment": True,
                "recommendations": True
            }
        }
    })
    dashboard.add_event("Compliance", "Generated HIPAA compliance report")
    
    # CTO uses MCP tools to analyze codebase
    print("\n💻 James (CTO) is analyzing the technical architecture...")
    team["cto"].act({
        "type": "MCP_GIT_LOG",
        "content": {
            "tool": "mcp_git_log",
            "arguments": {"max_commits": 20},
            "output_mode": "present"
        }
    })
    
    # CTO generates architecture document
    team["cto"].act({
        "type": "PRESENT",
        "content": {
            "tool": "technical_memo",
            "topic": "HealthChain Blockchain Architecture",
            "memo_type": "architecture",
            "format": "markdown"
        }
    })
    dashboard.add_event("Technology", "Completed architecture documentation")
    
    # Extract Day 1 results
    extractor = ResultsExtractor()
    day1_results = extractor.extract_results_from_world(
        world,
        extraction_objective="Extract Day 1 planning decisions and action items",
        fields=["decisions", "action_items", "assignments", "risks"],
        verbose=False
    )
    
    # Update dashboard metrics
    dashboard.update_metric("documents_generated", 2)
    dashboard.update_metric("tasks_completed", 3)
    
    return day1_results


async def simulate_day_2(team: Dict, dashboard: CEODashboard, orchestrator: AgentOrchestrator):
    """Day 2: Development and Integration"""
    print("\n" + "="*60)
    print("📅 DAY 2: Development and Integration")
    print("="*60)
    
    dashboard.update_metric("sprint_day", 2)
    
    # Morning standup (quick async meeting)
    print("\n☕ Day 2 Morning Standup")
    standup_world = AsyncTinyWorld("Day 2 Standup", is_meeting=True)
    standup_world.add_agent(team["ceo"])
    standup_world.add_agent(team["cto"]) 
    standup_world.add_agent(team["pm"])
    standup_world.add_agent(team["dev_lead"])
    
    await standup_world.broadcast(
        f"{team['ceo'].name}: Good morning! Let's have a quick standup. "
        "What did we accomplish yesterday and what are today's priorities?"
    )
    
    await standup_world.run_async(2)  # Quick 2-round standup
    
    # Smart Contract Security Review Meeting
    print("\n🔐 Smart Contract Security Review Session")
    security_world = AsyncTinyWorld("Security Review", is_meeting=True)
    security_world.add_agent(team["cto"])
    security_world.add_agent(team["dev_lead"])
    security_world.add_agent(team["compliance"])
    
    # Dev lead presents code for review
    await security_world.broadcast(
        f"{team['dev_lead'].name}: I've completed the smart contract implementation. "
        "Let's review the security measures and compliance checks together."
    )
    
    # Run security review with concurrent agent thinking
    await security_world.run_async(3)
    
    # PM works on investor presentation using Present Feature
    print("\n📊 Emily (PM) is creating the investor presentation...")
    team["pm"].act({
        "type": "PRESENT",
        "content": {
            "tool": "summary",
            "topic": "HealthChain MVP Investor Presentation",
            "summary_type": "executive",
            "format": "markdown",
            "parameters": {
                "sections": ["problem", "solution", "technology", "market", "team", "ask"],
                "tone": "professional",
                "length": "comprehensive"
            }
        }
    })
    dashboard.add_event("Product", "Completed investor presentation draft")
    
    # Use orchestrator to check task progress
    if orchestrator:
        task_status = orchestrator.get_task_status("Day 2")
        print(f"\n📈 Day 2 Task Completion: {task_status}")
    
    # Extract Day 2 results
    extractor = ResultsExtractor()
    security_results = extractor.extract_results_from_world(
        security_world,
        extraction_objective="Extract security review findings and recommendations",
        fields=["security_issues", "compliance_gaps", "recommendations", "sign_offs"],
        verbose=False
    )
    
    # Update dashboard
    dashboard.update_metric("documents_generated", 4)
    dashboard.update_metric("tasks_completed", 6)
    dashboard.update_metric("active_meetings", 2)
    
    return security_results


async def simulate_day_3(team: Dict, dashboard: CEODashboard, interrupt_handler: CEOInterruptHandler):
    """Day 3: Final Integration and Demo Prep"""
    print("\n" + "="*60)
    print("📅 DAY 3: Final Integration and Demo Preparation")
    print("="*60)
    
    dashboard.update_metric("sprint_day", 3)
    
    # Enable CEO interrupt for critical day
    if interrupt_handler:
        print("\n🎮 CEO Interrupt System Active - Press SPACEBAR for real-time control")
    
    # Final integration meeting
    print("\n🔧 Final Integration Meeting")
    integration_world = AsyncTinyWorld("Integration Meeting", is_meeting=True)
    integration_world.add_agent(team["cto"])
    integration_world.add_agent(team["dev_lead"])
    integration_world.add_agent(team["pm"])
    
    await integration_world.broadcast(
        f"{team['cto'].name}: Let's ensure all components are properly integrated. "
        "We need the smart contracts, frontend, and documentation all working together."
    )
    
    await integration_world.run_async(3)
    
    # Demo preparation with full team
    print("\n🎯 Demo Preparation Session")
    demo_world = AsyncTinyWorld("Demo Prep", is_meeting=True)
    
    # Add all team members for demo prep
    for agent in team.values():
        demo_world.add_agent(agent)
    
    # CEO leads demo prep
    await demo_world.broadcast(
        f"{team['ceo'].name}: This is our final preparation before the investor demo. "
        "Let's run through the entire presentation and make sure everything is perfect. "
        "James, can you start with the technical demo?"
    )
    
    # Run demo prep with potential for CEO interrupt
    await demo_world.run_async(4)
    
    # Generate final summary report using MCP + Present Feature
    print("\n📄 Generating Final Sprint Summary Report...")
    team["pm"].act({
        "type": "PRESENT",
        "content": {
            "tool": "summary",
            "topic": "3-Day Sprint Final Summary Report",
            "summary_type": "comprehensive",
            "format": "markdown",
            "parameters": {
                "include_metrics": True,
                "include_deliverables": True,
                "include_next_steps": True
            }
        }
    })
    
    # Final review meeting
    print("\n✅ Final Sprint Review")
    review_world = AsyncTinyWorld("Sprint Review", is_meeting=True)
    
    for agent in team.values():
        review_world.add_agent(agent)
    
    await review_world.broadcast(
        f"{team['ceo'].name}: Excellent work everyone! Let's do a final review of what "
        "we've accomplished and make sure we're ready for tomorrow's investor meeting."
    )
    
    await review_world.run_async(2)
    
    # Extract final results
    extractor = ResultsExtractor()
    final_results = extractor.extract_results_from_world(
        review_world,
        extraction_objective="Extract sprint accomplishments and readiness assessment",
        fields=["accomplishments", "deliverables", "readiness_score", "remaining_risks", "team_sentiment"],
        verbose=False
    )
    
    # Update final dashboard metrics
    dashboard.update_metric("documents_generated", 6)
    dashboard.update_metric("tasks_completed", 9)
    dashboard.update_metric("sprint_completion", 100)
    
    return final_results


async def main():
    """Main simulation orchestration function."""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Set up logging to both console and file
    log_filename = os.path.join(logs_dir, f"healthchain_simulation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    logger = TeeLogger(log_filename)
    sys.stdout = logger
    
    print(f"📝 Logging simulation to: {log_filename}")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 HealthChain Dynamics - 3-Day MVP Sprint Simulation")
    print("Showcasing ALL TinyTroupe Features:")
    print("- MCP Integration (External Tools)")
    print("- Present Feature (Document Generation)")
    print("- Adaptive Agents (Context-Aware)")
    print("- Async Orchestration (Concurrent Processing)")
    print("- CEO Dashboard (Real-time Monitoring)")
    print("- Agent Orchestrator (Project Management)")
    print("- Context Detection (Meeting Intelligence)")
    
    # Initialize simulation cache
    control.begin("healthchain_3day_sprint.cache.json")
    
    try:
        # Setup MCP servers
        await setup_mcp_servers()
        
        # Create team
        team = await create_team_members()
        
        # Initialize CEO Dashboard
        dashboard = CEODashboard("HealthChain Sprint Dashboard")
        dashboard.update_company_info("HealthChain Dynamics", "Healthcare Blockchain", "Seed")
        dashboard.add_agent_status(team["ceo"].name, "Active", "Leading sprint")
        dashboard.add_agent_status(team["cto"].name, "Active", "Architecture design")
        dashboard.add_agent_status(team["compliance"].name, "Active", "Compliance review")
        dashboard.add_agent_status(team["pm"].name, "Active", "Investor prep")
        dashboard.add_agent_status(team["dev_lead"].name, "Active", "Implementation")
        
        # Initialize Agent Orchestrator with project definition
        project_def = create_project_definition()
        orchestrator = AgentOrchestrator(execution_mode="incremental")
        orchestrator.load_project(project_def)
        orchestrator.assign_agents({
            "ceo": team["ceo"],
            "cto": team["cto"],
            "compliance": team["compliance"],
            "pm": team["pm"],
            "dev_lead": team["dev_lead"]
        })
        
        # Initialize CEO Interrupt Handler
        interrupt_handler = CEOInterruptHandler()
        
        # Display initial dashboard
        dashboard.display()
        
        # Run 3-day simulation
        print("\n" + "🎬 STARTING 3-DAY SIMULATION ".center(60, "="))
        
        # Day 1
        day1_results = await simulate_day_1(team, dashboard)
        control.checkpoint()  # Save Day 1 state
        dashboard.display()
        
        # Brief pause between days
        print("\n⏰ End of Day 1 - Team regroups tomorrow morning...")
        await asyncio.sleep(2)
        
        # Day 2
        day2_results = await simulate_day_2(team, dashboard, orchestrator)
        control.checkpoint()  # Save Day 2 state
        dashboard.display()
        
        print("\n⏰ End of Day 2 - Final push tomorrow...")
        await asyncio.sleep(2)
        
        # Day 3
        day3_results = await simulate_day_3(team, dashboard, interrupt_handler)
        control.checkpoint()  # Save Day 3 state
        
        # Display final dashboard
        print("\n" + " FINAL SPRINT RESULTS ".center(60, "="))
        dashboard.display()
        
        # Generate comprehensive sprint report
        print("\n📊 Generating Comprehensive Sprint Analysis...")
        
        # Combine all results
        complete_results = {
            "sprint_overview": {
                "company": "HealthChain Dynamics",
                "duration": "3 days",
                "team_size": len(team),
                "objective": "Finalize MVP for investor demo"
            },
            "day_1": day1_results,
            "day_2": day2_results, 
            "day_3": day3_results,
            "metrics": {
                "total_meetings": 7,
                "documents_generated": dashboard.metrics.get("documents_generated", 0),
                "tasks_completed": dashboard.metrics.get("tasks_completed", 0),
                "mcp_tools_used": mcp_integration_manager.get_integration_status()["total_mcp_tools"],
                "sprint_completion": dashboard.metrics.get("sprint_completion", 0)
            },
            "deliverables": [
                "HIPAA Compliance Report",
                "Technical Architecture Document",
                "Smart Contract Security Review",
                "Investor Presentation",
                "Sprint Summary Report",
                "Demo-ready MVP"
            ]
        }
        
        # Save final results
        results_path = "simulation_results_healthchain_3day_sprint.json"
        with open(results_path, 'w') as f:
            json.dump(complete_results, f, indent=2)
        
        print(f"\n✅ Complete simulation results saved to: {results_path}")
        
        # Display summary
        print("\n" + " SIMULATION COMPLETE ".center(60, "🎉"))
        print("\nKey Achievements:")
        print(f"- ✅ {dashboard.metrics.get('tasks_completed', 0)} tasks completed")
        print(f"- 📄 {dashboard.metrics.get('documents_generated', 0)} documents generated")
        print(f"- 🔧 {len(mcp_integration_manager.connected_servers)} MCP servers utilized")
        print(f"- 👥 {len(team)} team members collaborated")
        print(f"- 🎯 MVP ready for investor demo!")
        
        print("\n🏆 HealthChain Dynamics is ready to revolutionize healthcare data!")
        
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        control.end()
        await mcp_integration_manager.disconnect_from_servers()
        
        print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n👋 Thank you for experiencing the full power of TinyTroupe!")
        print("   This simulation showcased:")
        print("   - MCP integration for external tool access")
        print("   - Present Feature for professional documentation")
        print("   - Adaptive agents with context awareness")
        print("   - Async orchestration for realistic concurrency")
        print("   - CEO Dashboard for business monitoring")
        print("   - And much more!")
        print(f"📝 Full simulation log saved to: {log_filename}")
        
        # Restore stdout and close logger
        sys.stdout = logger.terminal
        logger.close()
        
        # Print final message to console only
        print(f"\n✅ Comprehensive simulation complete! Full log available at: {log_filename}")


if __name__ == "__main__":
    # Run the comprehensive simulation
    asyncio.run(main())