"""
AgentOrchestrator Usage Examples

This script demonstrates how to use the AgentOrchestrator system with different
execution modes and scheduling options for healthcare blockchain projects.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tinytroupe.agent_orchestrator import (
    AgentOrchestrator, run_healthcare_blockchain_project,
    create_orchestrator_with_agents
)
from tinytroupe.async_adaptive_agent import create_async_adaptive_agent
from tinytroupe.async_event_bus import initialize_event_bus, shutdown_event_bus


async def example_1_quick_compressed_execution():
    """
    Example 1: Quick compressed execution for testing
    Run entire healthcare blockchain project in compressed timeline
    """
    print("🚀 Example 1: Quick Compressed Execution")
    print("=" * 50)
    
    project_path = "../projects/healthcare_blockchain_compressed.json"
    
    if not os.path.exists(project_path):
        print("❌ Project file not found. Please ensure the project JSON exists.")
        return
    
    print("⚡ Running compressed healthcare blockchain project...")
    print("📅 All tasks scheduled for same day")
    print("🤖 Fully automated execution")
    
    try:
        result = await run_healthcare_blockchain_project(
            project_path, 
            execution_mode="fully_automated"
        )
        
        print("\n✅ Project completed successfully!")
        print(f"📊 Results:")
        print(f"  • Tasks completed: {result['task_summary']['completed_tasks']}")
        print(f"  • Meetings held: {result['statistics']['meetings_held']}")
        print(f"  • Tasks spawned: {result['statistics']['tasks_spawned']}")
        print(f"  • Duration: {result.get('duration', 'N/A')}")
        
        return result
        
    except Exception as error:
        print(f"❌ Execution failed: {error}")


async def example_2_incremental_with_checkpoints():
    """
    Example 2: Incremental execution with checkpoints
    Run project with human review points
    """
    print("\n🎛️ Example 2: Incremental Execution with Checkpoints")
    print("=" * 50)
    
    project_path = "../projects/healthcare_blockchain_compressed.json"
    
    if not os.path.exists(project_path):
        print("❌ Project file not found.")
        return
    
    print("⏸️ Incremental execution with checkpoints")
    print("👁️ Human review points after meetings")
    print("🚨 CEO interrupt capability enabled")
    
    try:
        result = await run_healthcare_blockchain_project(
            project_path, 
            execution_mode="incremental"
        )
        
        print("\n✅ Incremental execution completed!")
        print(f"📊 Agent Development:")
        for agent_id, development in result['agent_development'].items():
            print(f"  • {agent_id}: {development['tasks_completed']} tasks, {development['meetings_attended']} meetings")
        
        return result
        
    except Exception as error:
        print(f"❌ Incremental execution failed: {error}")


async def example_3_simulation_mode():
    """
    Example 3: Full project management simulation
    Complete project lifecycle with adaptive task creation
    """
    print("\n🎮 Example 3: Full Project Management Simulation")
    print("=" * 50)
    
    project_path = "../projects/healthcare_blockchain_project.json"
    
    if not os.path.exists(project_path):
        print("❌ Full project file not found.")
        return
    
    print("🌐 Complete project management simulation")
    print("📈 Adaptive task creation enabled")
    print("🏢 Additional management meetings spawned")
    print("📋 Dynamic project evolution")
    
    try:
        result = await run_healthcare_blockchain_project(
            project_path, 
            execution_mode="simulation"
        )
        
        print("\n✅ Simulation completed!")
        print(f"📊 Full Project Results:")
        print(f"  • Original tasks: {result['task_summary']['total_tasks']}")
        print(f"  • Spawned tasks: {result['task_summary']['spawned_tasks']}")
        print(f"  • Success rate: {result['task_summary']['completed_tasks']}/{result['task_summary']['total_tasks']}")
        
        return result
        
    except Exception as error:
        print(f"❌ Simulation failed: {error}")


async def example_4_custom_orchestrator():
    """
    Example 4: Custom orchestrator with manual agent setup
    Build orchestrator from scratch with specific agents
    """
    print("\n🔧 Example 4: Custom Orchestrator Setup")
    print("=" * 50)
    
    await initialize_event_bus()
    
    try:
        # Create orchestrator
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize_event_bus()
        
        print("👥 Creating custom agent team...")
        
        # Create specialized agents
        pm = create_async_adaptive_agent(
            name="Alice Johnson",
            occupation="Healthcare IT Project Manager",
            personality_traits=["organized", "communicative", "results-focused"],
            years_experience="10+ years"
        )
        
        tech_lead = create_async_adaptive_agent(
            name="Bob Chen",
            occupation="Senior Blockchain Developer",
            personality_traits=["technical", "innovative", "security-focused"],
            years_experience="8+ years"
        )
        
        # Register agents with skills
        orchestrator.register_agent(
            pm, 
            skills={"project_management": 9, "communication": 8, "healthcare": 7},
            preferences={"coordination": 10, "planning": 9}
        )
        
        orchestrator.register_agent(
            tech_lead,
            skills={"blockchain": 9, "development": 8, "security": 8},
            preferences={"architecture": 10, "coding": 9}
        )
        
        print(f"✅ Registered {len(orchestrator.agent_registry)} agents")
        
        # Show agent profiles
        print("\n📋 Agent Profiles:")
        for agent_id, profile in orchestrator.agent_registry.items():
            print(f"  • {agent_id}: Skills {profile.skills}, Preferences {profile.preferences}")
        
        # Create a simple task for demonstration
        from tinytroupe.agent_orchestrator import TaskDefinition
        
        task = TaskDefinition(
            task_id="demo_task",
            description="Plan the blockchain healthcare platform architecture",
            required_skills={"blockchain": 7, "healthcare": 5},
            priority=1,
            meeting_required=True,
            attendees=["Alice Johnson", "Bob Chen"]
        )
        
        orchestrator.task_registry["demo_task"] = task
        
        print("\n🎯 Executing demo task...")
        await orchestrator._execute_meeting_task(task)
        
        print(f"✅ Task completed: {task.status}")
        print(f"📊 Meeting results: {len(task.meeting_results)} fields extracted")
        
        return {"custom_orchestrator": "success", "task_status": task.status}
        
    except Exception as error:
        print(f"❌ Custom orchestrator failed: {error}")
    finally:
        if 'orchestrator' in locals():
            await orchestrator.world.shutdown()
        await shutdown_event_bus()


async def example_5_real_time_ceo_control():
    """
    Example 5: Demonstrate real-time CEO control capabilities
    Show how CEO can interrupt and steer project execution
    """
    print("\n🚨 Example 5: Real-time CEO Control")
    print("=" * 50)
    
    print("🎛️ This example demonstrates CEO interrupt capabilities")
    print("⌨️ During execution, CEO can:")
    print("  • Press SPACEBAR to interrupt")
    print("  • Provide steering commands")
    print("  • Pause/resume execution") 
    print("  • Request status updates")
    print("  • Adjust priorities")
    
    project_path = "../projects/healthcare_blockchain_compressed.json"
    
    if not os.path.exists(project_path):
        print("❌ Project file not found.")
        return
    
    print("\n🚀 Starting project with CEO control enabled...")
    print("💡 Try pressing SPACEBAR during execution for CEO interrupts!")
    
    try:
        # This will enable CEO interrupt monitoring
        result = await run_healthcare_blockchain_project(
            project_path, 
            execution_mode="incremental"  # Better for demonstrating interrupts
        )
        
        print("\n✅ Project with CEO control completed!")
        return result
        
    except Exception as error:
        print(f"❌ CEO control demo failed: {error}")


async def main():
    """Main demonstration function"""
    print("🎯 AgentOrchestrator Usage Examples")
    print("=" * 80)
    print("🏥 Healthcare Blockchain Project Orchestration")
    print()
    
    examples = [
        ("Quick Compressed Execution", example_1_quick_compressed_execution),
        ("Incremental with Checkpoints", example_2_incremental_with_checkpoints),
        ("Full Simulation Mode", example_3_simulation_mode),
        ("Custom Orchestrator", example_4_custom_orchestrator),
        ("Real-time CEO Control", example_5_real_time_ceo_control)
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nChoose an example to run:")
    print("  • Enter number (1-5) for specific example")
    print("  • Enter 'all' to run all examples")
    print("  • Enter 'quit' to exit")
    
    try:
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'quit':
            print("👋 Goodbye!")
            return
        elif choice == 'all':
            print("\n🚀 Running all examples...")
            for name, example_func in examples:
                print(f"\n{'='*20} {name} {'='*20}")
                try:
                    await example_func()
                except Exception as error:
                    print(f"❌ {name} failed: {error}")
                print("\n⏸️ Pausing between examples...")
                await asyncio.sleep(2)
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            example_index = int(choice) - 1
            name, example_func = examples[example_index]
            print(f"\n🚀 Running: {name}")
            await example_func()
        else:
            print("❌ Invalid choice. Please enter 1-5, 'all', or 'quit'.")
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as error:
        print(f"\n❌ Error: {error}")
    
    print("\n🎉 Examples completed!")


if __name__ == "__main__":
    asyncio.run(main())