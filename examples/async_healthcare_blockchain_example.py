"""
Healthcare Blockchain Meeting Example using AsyncAdaptiveTinyPerson

This example demonstrates how to use the new async agent capabilities
for a realistic healthcare blockchain project meeting.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tinytroupe.async_adaptive_agent import create_async_adaptive_agent
from tinytroupe.async_world import AsyncTinyWorld
from tinytroupe.async_event_bus import initialize_event_bus, shutdown_event_bus


async def healthcare_blockchain_meeting_simulation():
    """
    Simulate a healthcare blockchain project meeting with:
    - Concurrent agent processing
    - Context-aware adaptive behavior  
    - Real-time CEO interrupt capability
    - Meeting wrap-up intelligence
    """
    
    print("🏥 Healthcare Blockchain Project Meeting Simulation")
    print("=" * 60)
    
    try:
        # Initialize async event system
        await initialize_event_bus()
        
        # Create async adaptive agents with domain expertise
        print("👥 Creating meeting participants...")
        
        # Orchestrator: Project Manager (AsyncAdaptive)
        pm = create_async_adaptive_agent(
            name="Emily Martinez",
            occupation="Senior Project Manager",
            personality_traits=["organized", "collaborative", "results-oriented"],
            professional_interests=["healthcare technology", "project delivery", "stakeholder management"],
            skills=["agile methodology", "stakeholder communication", "risk management"],
            years_experience="12+ years"
        )
        
        # Domain Experts: CTO (AsyncAdaptive)
        cto = create_async_adaptive_agent(
            name="Dr. James Wilson",
            occupation="Chief Technology Officer",
            personality_traits=["analytical", "strategic", "innovative"],
            professional_interests=["blockchain technology", "healthcare IT", "system architecture"],
            skills=["distributed systems", "blockchain", "healthcare standards", "technical leadership"],
            years_experience="15+ years"
        )
        
        # Domain Experts: Compliance Officer (AsyncAdaptive)
        compliance = create_async_adaptive_agent(
            name="Michael Thompson",
            occupation="Healthcare Compliance Officer",
            personality_traits=["detail-oriented", "thorough", "principled"],
            professional_interests=["HIPAA compliance", "healthcare regulations", "audit procedures"],
            skills=["regulatory compliance", "risk assessment", "audit management", "healthcare law"],
            years_experience="10+ years"
        )
        
        # Technical Expert: Senior Developer (AsyncAdaptive)
        developer = create_async_adaptive_agent(
            name="Lisa Chen",
            occupation="Senior Blockchain Developer",
            personality_traits=["technical", "problem-solver", "collaborative"],
            professional_interests=["blockchain development", "smart contracts", "healthcare data"],
            skills=["Solidity", "Ethereum", "IPFS", "healthcare APIs", "cryptography"],
            years_experience="8+ years"
        )
        
        # Clinical Expert: Physician (AsyncAdaptive)
        physician = create_async_adaptive_agent(
            name="Dr. Sarah Chen",
            occupation="Clinical Informaticist",
            personality_traits=["patient-focused", "analytical", "collaborative"],
            professional_interests=["clinical workflows", "healthcare IT", "patient data management"],
            skills=["clinical practice", "health informatics", "workflow analysis", "EMR systems"],
            years_experience="12+ years"
        )
        
        # Create async world with meeting context and CEO interrupt
        world = AsyncTinyWorld(
            name="Healthcare Blockchain Meeting",
            agents=[pm, cto, compliance, developer, physician],
            is_meeting=True,  # Enable cross-agent communication
            enable_ceo_interrupt=True,  # Allow real-time steering
            ceo_interrupt_keys=['space']  # Press spacebar for CEO interrupt
        )
        
        print(f"✅ Created meeting with {len(world.agents)} participants")
        print("🎯 Meeting focus: Healthcare blockchain platform development")
        print("⌨️  Press SPACEBAR during simulation for CEO interrupts")
        print()
        
        # Set explicit meeting context for better adaptive behavior
        for agent in world.agents:
            agent.set_environment_context(
                meeting_type="business_meeting",
                agenda_items=[
                    "Technical architecture review",
                    "HIPAA compliance requirements", 
                    "Implementation timeline",
                    "Hospital integration strategy",
                    "User acceptance testing plan"
                ],
                participant_roles=[
                    "project_manager", "cto", "compliance_officer", 
                    "developer", "physician"
                ]
            )
        
        # Initial meeting setup - broadcast agenda to all participants
        print("📋 Starting meeting with agenda...")
        await world.broadcast(
            "Welcome to our healthcare blockchain project meeting. Today's agenda: "
            "1) Technical architecture review, 2) HIPAA compliance requirements, "
            "3) Implementation timeline, 4) Hospital integration strategy, "
            "5) User acceptance testing plan. Let's begin with introductions and initial thoughts.",
            source=None
        )
        
        # Run async simulation with CEO interrupt capability
        print("\n🚀 Running async meeting simulation...")
        print("💡 Agents will process concurrently with adaptive behavior")
        print("🚨 CEO can interrupt at any time for real-time steering")
        print()
        
        # Run 8 rounds (allows for wrap-up logic on longer meetings)
        await world.async_run(
            steps=8,
            enable_ceo_interrupt=True
        )
        
        print("\n📊 Meeting Results:")
        print("=" * 40)
        
        # Show final state of all agents
        async_state = world.get_async_state()
        print(f"🔍 Async agents: {len(async_state['async_agents'])}")
        print(f"🔍 Sync agents: {len(async_state['sync_agents'])}")
        print(f"⚡ CEO monitoring: {async_state['ceo_monitoring']}")
        
        # Show context summaries for adaptive agents
        print("\n🧠 Agent Context Summaries:")
        for agent in world.agents:
            if hasattr(agent, 'get_context_summary'):
                summary = await agent.get_context_summary()
                print(f"  📝 {agent.name}:")
                print(f"     Context: {summary['current_context']}")
                print(f"     Rounds: {summary['conversation_rounds']}")
                print(f"     Messages: {summary['recent_messages']}")
        
        print("\n✅ Healthcare blockchain meeting simulation completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Meeting interrupted by user")
    except Exception as error:
        print(f"\n❌ Meeting failed: {error}")
    finally:
        # Clean shutdown
        if 'world' in locals():
            await world.shutdown()
        await shutdown_event_bus()
        print("🧹 Cleanup completed")


async def quick_async_demo():
    """Quick demo of core async capabilities without full meeting"""
    
    print("⚡ Quick Async Agent Demo")
    print("=" * 30)
    
    # Create a few async adaptive agents
    agents = [
        create_async_adaptive_agent("Project Manager", "Project Manager"),
        create_async_adaptive_agent("Developer", "Senior Developer"),
        create_async_adaptive_agent("Compliance", "Compliance Officer")
    ]
    
    # Initialize event bus
    await initialize_event_bus()
    
    try:
        # Initialize all agents
        for agent in agents:
            await agent._initialize_event_bus()
        
        print("👥 Created 3 async adaptive agents")
        
        # Test concurrent execution
        print("⚡ Testing concurrent async operations...")
        
        start_time = asyncio.get_event_loop().time()
        
        # Run all agents concurrently
        results = await asyncio.gather(
            agents[0].async_listen_and_act("Let's discuss the project requirements"),
            agents[1].async_listen_and_act("I can handle the technical implementation"),
            agents[2].async_listen_and_act("We need to ensure regulatory compliance")
        )
        
        end_time = asyncio.get_event_loop().time()
        
        print(f"✅ Completed {len(agents)} concurrent operations in {end_time - start_time:.3f} seconds")
        
        # Show context for each agent
        for agent in agents:
            context = agent.get_current_context()
            print(f"  🎯 {agent.name}: {context.value}")
        
    finally:
        await shutdown_event_bus()


if __name__ == "__main__":
    print("🏥 TinyTroupe Async Healthcare Example")
    print("=" * 50)
    print()
    print("Choose simulation:")
    print("1. Full healthcare blockchain meeting (with CEO interrupt)")
    print("2. Quick async demo")
    print()
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting full healthcare blockchain meeting simulation...")
            asyncio.run(healthcare_blockchain_meeting_simulation())
        elif choice == "2":
            print("\n⚡ Starting quick async demo...")
            asyncio.run(quick_async_demo())
        else:
            print("❌ Invalid choice. Please run again and enter 1 or 2.")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as error:
        print(f"\n❌ Error: {error}")