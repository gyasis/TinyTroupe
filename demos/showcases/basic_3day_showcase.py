#!/usr/bin/env python3
"""
Basic 3-Day Business Simulation Showcase (Core Features Only)
=============================================================

This version uses only the core, stable TinyTroupe features to demonstrate
a realistic 3-day business simulation without complex dependencies.

Features demonstrated:
- Core TinyPerson agents with different roles
- TinyWorld environment for meetings  
- Natural agent conversations
- Business decision-making scenarios
- Clean output formatting
"""

import json
import sys
from datetime import datetime

# Core TinyTroupe imports only
from tinytroupe import control
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from tinytroupe.extraction import ResultsExtractor


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

# Clean display settings
TinyPerson.rich_text_display = False
TinyWorld.rich_text_display = False
TinyPerson.debug_display = False
TinyWorld.debug_display = False
TinyPerson.communication_style = "simplified"


def create_startup_team():
    """Create a diverse startup team using core TinyPerson features."""
    
    print("👥 Creating CloudFlow Dynamics team...")
    
    # CEO
    ceo = TinyPerson("Rachel Chen")
    ceo.define("occupation", "CEO and Co-Founder")
    ceo.define("age", 35)
    ceo.define("personality_traits", [
        {"trait": "Visionary and strategic thinker"},
        {"trait": "Excellent at stakeholder communication"},
        {"trait": "Data-driven decision maker"}
    ])
    ceo.define("interests", [
        {"interest": "Cloud computing trends"},
        {"interest": "Market expansion strategies"},
        {"interest": "Team leadership"}
    ])
    
    # CTO
    cto = TinyPerson("Dr. Michael Zhang")
    cto.define("occupation", "Chief Technology Officer")
    cto.define("age", 38)
    cto.define("personality_traits", [
        {"trait": "Technical perfectionist"},
        {"trait": "Innovation focused"},
        {"trait": "Systematic problem solver"}
    ])
    cto.define("interests", [
        {"interest": "Microservices architecture"},
        {"interest": "DevOps automation"},
        {"interest": "Performance optimization"}
    ])
    
    # VP Product
    vp_product = TinyPerson("Sarah Martinez")
    vp_product.define("occupation", "VP of Product")
    vp_product.define("age", 32)
    vp_product.define("personality_traits", [
        {"trait": "User-centric design advocate"},
        {"trait": "Metrics-driven"},
        {"trait": "Creative problem solver"}
    ])
    vp_product.define("interests", [
        {"interest": "User experience research"},
        {"interest": "Product analytics"},
        {"interest": "Competitive analysis"}
    ])
    
    # VP Sales
    vp_sales = TinyPerson("David Kumar")
    vp_sales.define("occupation", "VP of Sales")
    vp_sales.define("age", 40)
    vp_sales.define("personality_traits", [
        {"trait": "Relationship-focused"},
        {"trait": "Results-oriented"},
        {"trait": "Persuasive communicator"}
    ])
    vp_sales.define("interests", [
        {"interest": "Enterprise sales strategies"},
        {"interest": "Customer success"},
        {"interest": "Revenue optimization"}
    ])
    
    # Lead Engineer
    lead_engineer = TinyPerson("Alex Kim")
    lead_engineer.define("occupation", "Lead Software Engineer")
    lead_engineer.define("age", 29)
    lead_engineer.define("personality_traits", [
        {"trait": "Detail-oriented"},
        {"trait": "Quality-focused"},
        {"trait": "Collaborative team player"}
    ])
    lead_engineer.define("interests", [
        {"interest": "Scalable system design"},
        {"interest": "Code quality best practices"},
        {"interest": "Team mentoring"}
    ])
    
    return {
        "ceo": ceo,
        "cto": cto,
        "vp_product": vp_product,
        "vp_sales": vp_sales,
        "lead_engineer": lead_engineer
    }


def simulate_day_1(team):
    """Day 1: Strategic Planning Session"""
    
    print("\n" + "="*60)
    print("📅 DAY 1: Q1 Strategic Planning Session")
    print("="*60)
    
    # Create world for strategic planning
    world = TinyWorld("Q1 Strategy Meeting", [team["ceo"], team["cto"], team["vp_product"], team["vp_sales"]])
    
    print("\n🎯 Morning: Strategic Planning Meeting")
    
    # CEO kicks off
    world.broadcast(
        f"{team['ceo'].name}: Good morning everyone! We're here to plan our Q1 strategy. "
        "Our Series B is approaching, and we need to show strong momentum. "
        "Let's align on our priorities and make sure everyone is on the same page."
    )
    
    # Run strategic discussion
    world.run(5)  # 5 rounds of discussion
    
    print("\n📋 Afternoon: Department Planning")
    
    # Individual department planning (simulated)
    print(f"\n💻 {team['cto'].name} (CTO) planning technical roadmap...")
    team["cto"].listen_and_act(
        "You need to plan the technical roadmap for Q1. Consider scalability, "
        "new features, technical debt, and team growth. Think about what's most important."
    )
    
    print(f"\n📱 {team['vp_product'].name} (VP Product) analyzing market requirements...")
    team["vp_product"].listen_and_act(
        "You need to analyze customer feedback and market trends to prioritize "
        "product features for Q1. What should the product team focus on?"
    )
    
    print(f"\n💼 {team['vp_sales'].name} (VP Sales) reviewing sales targets...")
    team["vp_sales"].listen_and_act(
        "You need to set realistic but ambitious sales targets for Q1 based on "
        "current pipeline and market conditions. What's achievable?"
    )
    
    # Extract Day 1 results
    extractor = ResultsExtractor()
    results = extractor.extract_results_from_world(
        world,
        extraction_objective="Extract Q1 strategic priorities and key decisions",
        fields=["strategic_priorities", "key_decisions", "success_metrics", "potential_risks"],
        verbose=False
    )
    
    print(f"\n✅ Day 1 Complete - Strategic direction established")
    return results


def simulate_day_2(team):
    """Day 2: Cross-functional Collaboration"""
    
    print("\n" + "="*60)
    print("📅 DAY 2: Cross-functional Planning & Execution")
    print("="*60)
    
    # Morning standup
    print("\n☕ Morning: Team Standup")
    standup_world = TinyWorld("Daily Standup", [team["cto"], team["vp_product"], team["lead_engineer"]])
    
    standup_world.broadcast(
        f"{team['vp_product'].name}: Good morning team! Let's have a quick standup. "
        "What did we decide yesterday and what are our priorities for today?"
    )
    
    standup_world.run(3)  # Quick standup
    
    # Product-Engineering alignment
    print("\n🔧 Mid-morning: Product-Engineering Alignment")
    product_tech_world = TinyWorld("Product-Tech Sync", [team["vp_product"], team["cto"], team["lead_engineer"]])
    
    product_tech_world.broadcast(
        f"{team['vp_product'].name}: We need to align on the technical implementation "
        "of our Q1 features. Let's make sure engineering understands the requirements "
        "and we understand the technical constraints."
    )
    
    product_tech_world.run(4)
    
    # Sales-Product strategy session
    print("\n💰 Afternoon: Sales-Product Strategy")
    sales_product_world = TinyWorld("Sales-Product Strategy", [team["vp_sales"], team["vp_product"], team["ceo"]])
    
    sales_product_world.broadcast(
        f"{team['vp_sales'].name}: I need to understand our product roadmap so I can "
        "set proper expectations with prospects and existing customers. "
        "What can I confidently sell in Q1?"
    )
    
    sales_product_world.run(4)
    
    # Individual work time
    print("\n⚙️ Late Afternoon: Individual Focus Time")
    
    print(f"\n🔧 {team['lead_engineer'].name} (Lead Engineer) architecting technical solutions...")
    team["lead_engineer"].listen_and_act(
        "Based on today's discussions, you need to create a technical implementation plan "
        "for the Q1 features. Consider architecture, timeline, and resource needs."
    )
    
    # Extract Day 2 results
    product_tech_extractor = ResultsExtractor()
    pt_results = product_tech_extractor.extract_results_from_world(
        product_tech_world,
        extraction_objective="Extract product-engineering alignment and technical decisions",
        fields=["technical_approach", "feature_specifications", "timeline", "resource_needs"],
        verbose=False
    )
    
    sales_product_extractor = ResultsExtractor()
    sp_results = sales_product_extractor.extract_results_from_world(
        sales_product_world,
        extraction_objective="Extract sales-product alignment and go-to-market strategy",
        fields=["target_customers", "value_propositions", "pricing_strategy", "sales_timeline"],
        verbose=False
    )
    
    print(f"\n✅ Day 2 Complete - Cross-functional alignment achieved")
    return {"product_tech": pt_results, "sales_product": sp_results}


def simulate_day_3(team):
    """Day 3: Final Planning and Team Alignment"""
    
    print("\n" + "="*60)
    print("📅 DAY 3: Final Planning & Team Commitment")
    print("="*60)
    
    # Resource planning meeting
    print("\n👥 Morning: Resource Planning")
    resource_world = TinyWorld("Resource Planning", [team["ceo"], team["cto"], team["vp_product"]])
    
    resource_world.broadcast(
        f"{team['ceo'].name}: We need to finalize our hiring plan and resource allocation "
        "for Q1. Based on our technical and product roadmap, what roles are critical?"
    )
    
    resource_world.run(4)
    
    # All-hands alignment meeting
    print("\n🏢 Midday: All-Hands Alignment")
    all_hands_world = TinyWorld("All-Hands Q1 Planning", list(team.values()))
    
    all_hands_world.broadcast(
        f"{team['ceo'].name}: This is our final alignment meeting for Q1 planning. "
        "I want everyone to share their department's commitments and hear from others. "
        "Let's make sure we're all rowing in the same direction."
    )
    
    all_hands_world.run(6)  # Longer meeting for full team
    
    # Final individual commitments
    print("\n📝 Afternoon: Individual Commitments")
    
    print(f"\n🎯 {team['cto'].name} finalizing technical commitments...")
    team["cto"].listen_and_act(
        "Based on all the discussions, finalize your technical commitments for Q1. "
        "What can you guarantee to deliver and what are the key risks?"
    )
    
    print(f"\n📊 {team['vp_product'].name} setting product milestones...")
    team["vp_product"].listen_and_act(
        "Set clear product milestones for Q1 based on customer needs and technical constraints. "
        "What will customers see and when?"
    )
    
    print(f"\n💰 {team['vp_sales'].name} committing to revenue targets...")
    team["vp_sales"].listen_and_act(
        "Make your final revenue commitment for Q1 based on the product roadmap "
        "and market conditions. What can you realistically achieve?"
    )
    
    # Final CEO wrap-up
    print(f"\n🎯 {team['ceo'].name} final thoughts...")
    team["ceo"].listen_and_act(
        "Reflect on the 3-day planning process. Are you confident in the team's "
        "alignment and Q1 plan? What are you most excited about?"
    )
    
    # Extract final results
    extractor = ResultsExtractor()
    final_results = extractor.extract_results_from_world(
        all_hands_world,
        extraction_objective="Extract final Q1 commitments and team alignment",
        fields=["department_commitments", "success_metrics", "team_confidence", "key_risks", "next_steps"],
        verbose=False
    )
    
    print(f"\n✅ Day 3 Complete - Team ready to execute Q1 plan")
    return final_results


def main():
    """Run the 3-day simulation."""
    
    # Create logs directory if it doesn't exist
    import os
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Set up logging to both console and file
    log_filename = os.path.join(logs_dir, f"cloudflow_simulation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    logger = TeeLogger(log_filename)
    sys.stdout = logger
    
    print(f"📝 Logging simulation to: {log_filename}")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 CloudFlow Dynamics - 3-Day Q1 Planning Sprint")
    print("Showcasing TinyTroupe's Core Business Simulation Capabilities")
    print("="*60)
    
    # Initialize control system
    control.begin("cloudflow_q1_planning.cache.json")
    
    try:
        # Create team
        team = create_startup_team()
        
        print(f"\n👤 Team Members:")
        for role, agent in team.items():
            print(f"  - {agent.name}: {agent._configuration.get('occupation', 'Unknown role')}")
        
        # Run 3-day simulation
        print("\n🎬 Starting 3-Day Q1 Planning Sprint")
        
        # Day 1
        day1_results = simulate_day_1(team)
        control.checkpoint()  # Save Day 1 state
        
        # Day 2  
        day2_results = simulate_day_2(team)
        control.checkpoint()  # Save Day 2 state
        
        # Day 3
        day3_results = simulate_day_3(team)
        control.checkpoint()  # Save Day 3 state
        
        # Compile final results
        print("\n" + " FINAL Q1 PLANNING RESULTS ".center(60, "="))
        
        final_simulation_results = {
            "company": "CloudFlow Dynamics",
            "simulation_type": "Q1 Strategic Planning Sprint",
            "duration": "3 days",
            "team": {name: agent.name for name, agent in team.items()},
            "day_1_strategy": day1_results,
            "day_2_collaboration": day2_results,
            "day_3_alignment": day3_results,
            "simulation_metadata": {
                "total_meetings": 7,
                "simulation_date": datetime.now().isoformat(),
                "tinytroupe_features": [
                    "Core TinyPerson agents",
                    "TinyWorld environments", 
                    "Natural agent conversations",
                    "Business decision scenarios",
                    "Results extraction",
                    "State management with checkpoints"
                ]
            }
        }
        
        # Save results
        results_file = "cloudflow_q1_planning_results.json"
        with open(results_file, 'w') as f:
            json.dump(final_simulation_results, f, indent=2)
        
        print(f"\n✅ Simulation completed successfully!")
        print(f"📄 Results saved to: {results_file}")
        
        # Display summary
        print("\n🏆 CloudFlow Dynamics Q1 Planning Summary:")
        print("  - Strategic priorities aligned across all departments")
        print("  - Technical roadmap coordinated with product goals")
        print("  - Sales targets set based on realistic product delivery")
        print("  - Resource needs identified for successful execution")
        print("  - Team commitment secured for Q1 objectives")
        
        print("\n🎯 Ready to execute ambitious Q1 growth plan!")
        
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        control.end()
        print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n👋 Thank you for experiencing TinyTroupe's business simulation capabilities!")
        print(f"📝 Full simulation log saved to: {log_filename}")
        
        # Restore stdout and close logger
        sys.stdout = logger.terminal
        logger.close()
        
        # Print final message to console only
        print(f"\n✅ Simulation complete! Full log available at: {log_filename}")


if __name__ == "__main__":
    main()