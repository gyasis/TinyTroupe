#!/usr/bin/env python3
"""
Simple 3-Day Business Simulation Showcase (No External Dependencies)
===================================================================

This simplified version demonstrates TinyTroupe features without requiring
external MCP servers to be installed. Perfect for quick testing.

Features demonstrated:
- Present Feature document generation
- Adaptive agents with context awareness  
- Async world for concurrent meetings
- CEO Dashboard monitoring
- Context detection system
- Clean display output
"""

import asyncio
import json
from datetime import datetime

# Core imports
from tinytroupe import control
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from tinytroupe.extraction import ResultsExtractor

# Advanced features
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.async_world import AsyncTinyWorld
from tinytroupe.ceo_dashboard import CEODashboard

# Present Feature
from tinytroupe.present_adaptive_agent import create_present_adaptive_agent

# Clean display settings
TinyPerson.rich_text_display = False
TinyWorld.rich_text_display = False
TinyPerson.debug_display = False
TinyWorld.debug_display = False
TinyPerson.communication_style = "simplified"


def create_startup_team():
    """Create a diverse team showcasing different agent types."""
    
    print("👥 Creating TechVenture AI team...")
    
    # CEO - Standard adaptive agent
    ceo = create_adaptive_agent("Jennifer Walsh", "CEO and Co-Founder")
    ceo.define("personality_traits", [
        {"trait": "Visionary and strategic"},
        {"trait": "Data-driven decision maker"},
        {"trait": "Excellent communicator"}
    ])
    
    # CTO - Present-enabled adaptive agent
    cto = create_present_adaptive_agent("Dr. Raj Patel", "Chief Technology Officer")
    cto.define("expertise_domains", [{
        "domain": "AI/ML Architecture",
        "competency_level": "Expert",
        "specific_knowledge": "Deep learning, MLOps, scalable systems"
    }])
    
    # CPO - Present-enabled adaptive agent
    cpo = create_present_adaptive_agent("Maria Rodriguez", "Chief Product Officer")
    cpo.define("personality_traits", [
        {"trait": "User-focused"},
        {"trait": "Creative problem solver"},
        {"trait": "Metrics-driven"}
    ])
    
    # VP Sales - Standard adaptive agent
    vp_sales = create_adaptive_agent("David Kim", "VP of Sales")
    vp_sales.define("interests", [
        {"interest": "Enterprise software sales"},
        {"interest": "Building partner relationships"},
        {"interest": "Revenue optimization"}
    ])
    
    # Lead Engineer - Standard TinyPerson
    engineer = TinyPerson("Sophie Chen")
    engineer.define("occupation", "Lead ML Engineer")
    engineer.define_several("interests", [
        {"interest": "Model optimization"},
        {"interest": "Production deployment"},
        {"interest": "Code quality"}
    ])
    
    return {
        "ceo": ceo,
        "cto": cto,
        "cpo": cpo,
        "vp_sales": vp_sales,
        "engineer": engineer
    }


async def day_1_strategy_session(team, dashboard):
    """Day 1: Strategic Planning and Vision Alignment"""
    
    print("\n" + "="*60)
    print("📅 DAY 1: Q4 Strategic Planning Session")
    print("="*60)
    
    # Create async world for strategic planning
    world = AsyncTinyWorld("Q4 Strategy Meeting", is_meeting=True)
    
    # Add executives
    world.add_agent(team["ceo"])
    world.add_agent(team["cto"]) 
    world.add_agent(team["cpo"])
    world.add_agent(team["vp_sales"])
    
    # Update dashboard
    dashboard.update_metric("active_meetings", 1)
    dashboard.update_metric("day", 1)
    
    # CEO kicks off
    print("\n🎯 Strategic Planning Meeting")
    await world.broadcast(
        f"{team['ceo'].name}: Good morning everyone! We're here to plan our Q4 strategy. "
        "We need to align on product roadmap, technical priorities, and sales targets. "
        "Our Series A is closing next month, so this quarter is critical."
    )
    
    # Run strategic discussion
    await world.run_async(4)
    
    # After meeting, CTO creates technical roadmap
    print("\n📋 Afternoon: Document Generation")
    print("\n💻 Raj (CTO) creating technical roadmap...")
    
    team["cto"].act({
        "type": "PRESENT",
        "content": {
            "tool": "technical_memo",
            "topic": "Q4 Technical Roadmap - AI Platform Scaling",
            "memo_type": "planning",
            "format": "markdown"
        }
    })
    dashboard.add_event("Technology", "Technical roadmap documented")
    
    # CPO creates product strategy
    print("\n📱 Maria (CPO) documenting product strategy...")
    team["cpo"].act({
        "type": "PRESENT",
        "content": {
            "tool": "summary",
            "topic": "Q4 Product Strategy - Enterprise AI Features",
            "summary_type": "strategic",
            "format": "markdown"
        }
    })
    dashboard.add_event("Product", "Product strategy documented")
    
    # Extract results
    extractor = ResultsExtractor()
    results = extractor.extract_results_from_world(
        world,
        extraction_objective="Extract strategic decisions and Q4 priorities",
        fields=["key_decisions", "priorities", "success_metrics", "risks"],
        verbose=False
    )
    
    dashboard.update_metric("documents_generated", 2)
    dashboard.update_metric("strategic_decisions", len(results.get("key_decisions", [])))
    
    return results


async def day_2_product_sprint(team, dashboard):
    """Day 2: Product Development Sprint"""
    
    print("\n" + "="*60)
    print("📅 DAY 2: Product Development Sprint")
    print("="*60)
    
    dashboard.update_metric("day", 2)
    
    # Morning standup
    print("\n☕ Morning Standup")
    standup_world = AsyncTinyWorld("Daily Standup", is_meeting=True)
    standup_world.add_agent(team["cto"])
    standup_world.add_agent(team["cpo"])
    standup_world.add_agent(team["engineer"])
    
    await standup_world.broadcast(
        f"{team['cpo'].name}: Good morning! Quick standup - "
        "let's review yesterday's decisions and today's sprint goals."
    )
    
    await standup_world.run_async(2)
    
    # Feature planning session
    print("\n🔧 Feature Planning Session")
    feature_world = AsyncTinyWorld("Feature Planning", is_meeting=True)
    feature_world.add_agent(team["cpo"])
    feature_world.add_agent(team["cto"])
    feature_world.add_agent(team["engineer"])
    
    await feature_world.broadcast(
        f"{team['cpo'].name}: Let's detail out the enterprise features for Q4. "
        "We need model versioning, A/B testing capabilities, and improved monitoring."
    )
    
    await feature_world.run_async(3)
    
    # Generate technical specifications
    print("\n📐 Sophie (Engineer) creating technical specs...")
    team["engineer"].act({
        "type": "THINK",
        "content": "I need to create detailed specifications for the model versioning system. "
        "This should include API design, database schema, and deployment strategy."
    })
    
    # Sales alignment meeting
    print("\n💼 Sales Alignment Session")
    sales_world = AsyncTinyWorld("Sales Alignment", is_meeting=True)
    sales_world.add_agent(team["vp_sales"])
    sales_world.add_agent(team["cpo"])
    sales_world.add_agent(team["ceo"])
    
    await sales_world.broadcast(
        f"{team['vp_sales'].name}: I need to understand the new features so I can "
        "position them correctly with our enterprise prospects. "
        "What's our unique value proposition?"
    )
    
    await sales_world.run_async(3)
    
    # Extract results
    extractor = ResultsExtractor()
    results = extractor.extract_results_from_world(
        feature_world,
        extraction_objective="Extract feature specifications and technical decisions",
        fields=["features", "technical_approach", "timeline", "dependencies"],
        verbose=False
    )
    
    dashboard.update_metric("features_planned", len(results.get("features", [])))
    dashboard.add_event("Product", "Feature specifications completed")
    
    return results


async def day_3_execution_planning(team, dashboard):
    """Day 3: Execution Planning and Investor Prep"""
    
    print("\n" + "="*60)
    print("📅 DAY 3: Execution Planning & Investor Prep")
    print("="*60)
    
    dashboard.update_metric("day", 3)
    
    # Resource planning meeting
    print("\n👥 Resource Planning Meeting")
    resource_world = AsyncTinyWorld("Resource Planning", is_meeting=True)
    resource_world.add_agent(team["ceo"])
    resource_world.add_agent(team["cto"])
    resource_world.add_agent(team["cpo"])
    
    await resource_world.broadcast(
        f"{team['ceo'].name}: With our Series A closing, we need to plan hiring. "
        "What roles are critical for executing our Q4 roadmap?"
    )
    
    await resource_world.run_async(3)
    
    # Investor deck preparation
    print("\n📊 Investor Update Preparation")
    investor_world = AsyncTinyWorld("Investor Prep", is_meeting=True)
    
    # Full team for investor prep
    for agent in team.values():
        investor_world.add_agent(agent)
    
    await investor_world.broadcast(
        f"{team['ceo'].name}: Let's prepare our investor update. "
        "We need to show strong Q3 results and ambitious Q4 plans. "
        "Each of you should present your area's highlights."
    )
    
    await investor_world.run_async(4)
    
    # Generate final summary using Present Feature
    print("\n📄 Maria (CPO) creating executive summary...")
    team["cpo"].act({
        "type": "PRESENT",
        "content": {
            "tool": "summary",
            "topic": "TechVenture AI - Q3 Results & Q4 Strategy",
            "summary_type": "executive",
            "format": "markdown",
            "parameters": {
                "include_metrics": True,
                "include_roadmap": True,
                "tone": "confident"
            }
        }
    })
    
    # Final alignment meeting
    print("\n✅ Final Alignment Check")
    final_world = AsyncTinyWorld("Final Alignment", is_meeting=True)
    final_world.add_agent(team["ceo"])
    final_world.add_agent(team["cto"])
    final_world.add_agent(team["cpo"])
    final_world.add_agent(team["vp_sales"])
    
    await final_world.broadcast(
        f"{team['ceo'].name}: Excellent work everyone! Let's do a final check - "
        "are we all aligned on priorities and ready to execute?"
    )
    
    await final_world.run_async(2)
    
    # Extract final results
    extractor = ResultsExtractor()
    results = extractor.extract_results_from_world(
        final_world,
        extraction_objective="Extract execution plan and team alignment",
        fields=["execution_plan", "resource_needs", "success_metrics", "team_confidence"],
        verbose=False
    )
    
    dashboard.update_metric("documents_generated", 3)
    dashboard.update_metric("execution_readiness", 95)
    
    return results


async def main():
    """Run the 3-day simulation."""
    
    print("\n🚀 TechVenture AI - 3-Day Strategic Sprint")
    print("Demonstrating TinyTroupe's Advanced Features\n")
    
    # Initialize control
    control.begin("techventure_3day_sprint.cache.json")
    
    try:
        # Create team
        team = create_startup_team()
        
        # Initialize CEO Dashboard
        dashboard = CEODashboard("TechVenture AI Dashboard")
        dashboard.update_company_info("TechVenture AI", "Enterprise AI Platform", "Series A")
        
        # Add team to dashboard
        for role, agent in team.items():
            dashboard.add_agent_status(agent.name, "Active", f"{role.upper()} duties")
        
        # Initial dashboard
        print("\n📊 Initial Company Status:")
        dashboard.display()
        
        # Run 3-day simulation
        print("\n🎬 Starting 3-Day Strategic Sprint\n")
        
        # Day 1
        day1_results = await day_1_strategy_session(team, dashboard)
        control.checkpoint()
        print("\n📊 End of Day 1 Status:")
        dashboard.display()
        await asyncio.sleep(1)
        
        # Day 2  
        day2_results = await day_2_product_sprint(team, dashboard)
        control.checkpoint()
        print("\n📊 End of Day 2 Status:")
        dashboard.display()
        await asyncio.sleep(1)
        
        # Day 3
        day3_results = await day_3_execution_planning(team, dashboard)
        control.checkpoint()
        
        # Final dashboard
        print("\n" + " FINAL SPRINT RESULTS ".center(60, "="))
        dashboard.display()
        
        # Save comprehensive results
        final_results = {
            "company": "TechVenture AI",
            "sprint_duration": "3 days",
            "team_size": len(team),
            "day_1_strategy": day1_results,
            "day_2_product": day2_results,
            "day_3_execution": day3_results,
            "achievements": {
                "documents_generated": dashboard.metrics.get("documents_generated", 0),
                "strategic_decisions": dashboard.metrics.get("strategic_decisions", 0),
                "features_planned": dashboard.metrics.get("features_planned", 0),
                "execution_readiness": dashboard.metrics.get("execution_readiness", 0)
            }
        }
        
        with open("techventure_results.json", 'w') as f:
            json.dump(final_results, f, indent=2)
        
        print("\n✅ Simulation complete! Results saved to techventure_results.json")
        print("\n🏆 TechVenture AI is ready for explosive Q4 growth!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        control.end()
        print("\n👋 Thanks for experiencing TinyTroupe's capabilities!")


if __name__ == "__main__":
    asyncio.run(main())