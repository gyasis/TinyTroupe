"""
Comprehensive test suite for AgentOrchestrator system

Tests all execution modes, scheduling options, and orchestration features
with both unit tests and integration scenarios.
"""

import pytest
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tinytroupe.agent_orchestrator import (
    AgentOrchestrator, ProjectDefinition, TaskDefinition, AgentProfile,
    ExecutionMode, SchedulingMode, create_orchestrator_with_agents,
    run_healthcare_blockchain_project
)
from tinytroupe.async_adaptive_agent import create_async_adaptive_agent
from tinytroupe.async_world import AsyncTinyWorld
from tinytroupe.async_event_bus import initialize_event_bus, shutdown_event_bus


@pytest.mark.asyncio
class TestAgentOrchestrator:
    
    async def setup_method(self):
        """Setup for each test method"""
        await initialize_event_bus()
        self.orchestrator = AgentOrchestrator()
        await self.orchestrator.initialize_event_bus()
    
    async def teardown_method(self):
        """Cleanup after each test method"""
        if hasattr(self, 'orchestrator') and self.orchestrator.world:
            await self.orchestrator.world.shutdown()
        await shutdown_event_bus()
    
    async def test_orchestrator_initialization(self):
        """Test basic orchestrator initialization"""
        assert self.orchestrator is not None
        assert isinstance(self.orchestrator.world, AsyncTinyWorld)
        assert len(self.orchestrator.agent_registry) == 0
        assert len(self.orchestrator.task_registry) == 0
    
    async def test_agent_registration(self):
        """Test agent registration with skills and preferences"""
        agent = create_async_adaptive_agent(
            name="Test Agent",
            occupation="Test Developer"
        )
        
        skills = {"development": 8, "testing": 6}
        preferences = {"coding": 9, "documentation": 4}
        
        self.orchestrator.register_agent(agent, skills, preferences)
        
        assert "Test Agent" in self.orchestrator.agent_registry
        profile = self.orchestrator.agent_registry["Test Agent"]
        assert profile.skills == skills
        assert profile.preferences == preferences
        assert profile.availability == True
        assert profile.current_workload == 0
    
    async def test_project_loading_from_json(self):
        """Test loading project definition from JSON"""
        # Create a minimal test project
        test_project = {
            "project_id": "test_project",
            "title": "Test Project",
            "description": "A test project",
            "execution_mode": "incremental",
            "scheduling": {
                "mode": "same_day",
                "start_date": "2024-01-15T09:00:00",
                "compress_timeline": true
            },
            "agents": [
                {
                    "agent_id": "test_agent",
                    "name": "Test Agent",
                    "occupation": "Tester",
                    "skill_levels": {"testing": 7},
                    "preferences": {"testing": 8}
                }
            ],
            "tasks": [
                {
                    "task_id": "test_task",
                    "description": "A test task",
                    "required_skills": {"testing": 5},
                    "priority": 1,
                    "meeting_required": false,
                    "dependencies": [],
                    "follow_up_tasks": []
                }
            ]
        }
        
        # Save to temporary file
        test_file = "/tmp/test_project.json"
        with open(test_file, 'w') as f:
            json.dump(test_project, f)
        
        try:
            await self.orchestrator.load_project(test_file)
            
            assert self.orchestrator.project is not None
            assert self.orchestrator.project.project_id == "test_project"
            assert len(self.orchestrator.task_registry) == 1
            assert "test_task" in self.orchestrator.task_registry
            
        finally:
            os.remove(test_file)
    
    async def test_task_assignment_algorithm(self):
        """Test skill-based task assignment"""
        # Register agents with different skills
        agent1 = create_async_adaptive_agent("Developer", "Software Developer")
        agent2 = create_async_adaptive_agent("Designer", "UI Designer")
        
        self.orchestrator.register_agent(agent1, {"development": 9, "testing": 6}, {"coding": 10})
        self.orchestrator.register_agent(agent2, {"design": 8, "testing": 4}, {"design": 9})
        
        # Create a development task
        task = TaskDefinition(
            task_id="dev_task",
            description="Implement new feature",
            required_skills={"development": 7},
            priority=1
        )
        
        # Find best agent
        best_agent = self.orchestrator._find_best_agent_for_task(task)
        
        assert best_agent is not None
        assert best_agent.agent_id == "Developer"  # Should pick the developer
    
    async def test_scheduling_modes(self):
        """Test different scheduling modes"""
        # Create test project with multiple tasks
        tasks = [
            TaskDefinition(
                task_id=f"task_{i}",
                description=f"Task {i}",
                required_skills={"general": 5},
                priority=1,
                dependencies=[] if i == 0 else [f"task_{i-1}"]
            )
            for i in range(3)
        ]
        
        self.orchestrator.project = ProjectDefinition(
            project_id="test",
            title="Test",
            description="Test",
            execution_mode=ExecutionMode.FULLY_AUTOMATED,
            scheduling_mode=SchedulingMode.SAME_DAY,
            start_date=datetime.now(),
            tasks=tasks
        )
        
        # Test same-day scheduling
        await self.orchestrator._adjust_project_scheduling()
        
        # All tasks should be scheduled for the same day
        for task in tasks:
            assert task.scheduled_date is not None
            assert task.scheduled_date.date() == self.orchestrator.project.start_date.date()
    
    async def test_skill_improvement(self):
        """Test agent skill improvement from task completion"""
        agent = create_async_adaptive_agent("Learner", "Junior Developer")
        self.orchestrator.register_agent(agent, {"development": 5}, {})
        
        profile = self.orchestrator.agent_registry["Learner"]
        initial_skill = profile.skills["development"]
        
        # Simulate skill improvement
        profile.update_skill("development", 1.0)
        
        assert profile.skills["development"] > initial_skill
    
    async def test_ceo_interrupt_handling(self):
        """Test CEO interrupt handling during execution"""
        from tinytroupe.async_event_bus import CEOInterruptEvent
        
        # Create a simple CEO interrupt event
        ceo_event = CEOInterruptEvent(
            message="pause execution",
            override_context=True,
            resume_action="continue"
        )
        
        # Handle the interrupt
        await self.orchestrator._handle_ceo_interrupt(ceo_event)
        
        # Should be paused
        assert self.orchestrator.execution_paused == True
        
        # Resume
        resume_event = CEOInterruptEvent(
            message="resume execution",
            override_context=True,
            resume_action="continue"
        )
        
        await self.orchestrator._handle_ceo_interrupt(resume_event)
        assert self.orchestrator.execution_paused == False


@pytest.mark.asyncio
class TestProjectExecution:
    """Integration tests for complete project execution"""
    
    async def setup_method(self):
        """Setup for each test method"""
        await initialize_event_bus()
    
    async def teardown_method(self):
        """Cleanup after each test method"""
        await shutdown_event_bus()
    
    async def test_compressed_project_execution(self):
        """Test execution of compressed healthcare blockchain project"""
        project_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "projects", 
            "healthcare_blockchain_compressed.json"
        )
        
        if not os.path.exists(project_path):
            pytest.skip("Compressed project file not found")
        
        try:
            # Run compressed project in fully automated mode
            result = await run_healthcare_blockchain_project(
                project_path, 
                execution_mode="fully_automated"
            )
            
            assert result is not None
            assert "project_id" in result
            assert result["project_id"] == "healthcare_blockchain_compressed"
            assert "task_summary" in result
            assert result["task_summary"]["completed_tasks"] > 0
            
        except Exception as error:
            pytest.fail(f"Project execution failed: {error}")
    
    async def test_task_spawning_from_meetings(self):
        """Test dynamic task creation from meeting outcomes"""
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize_event_bus()
        
        try:
            # Register test agents
            pm = create_async_adaptive_agent("PM", "Project Manager")
            dev = create_async_adaptive_agent("Dev", "Developer")
            
            orchestrator.register_agent(pm, {"project_management": 8}, {})
            orchestrator.register_agent(dev, {"development": 8}, {})
            
            # Create a meeting task that should spawn follow-ups
            meeting_task = TaskDefinition(
                task_id="planning_meeting",
                description="Project planning and task assignment meeting",
                required_skills={"project_management": 6},
                priority=2,
                meeting_required=True,
                attendees=["PM", "Dev"]
            )
            
            orchestrator.task_registry["planning_meeting"] = meeting_task
            
            # Simulate meeting results that should spawn tasks
            meeting_results = {
                "action_items": [
                    "Create technical specification document",
                    "Set up development environment",
                    "Schedule weekly status meetings"
                ],
                "decisions": ["Use React for frontend"],
                "next_steps": ["Begin development phase"]
            }
            
            # Test task spawning
            await orchestrator._spawn_tasks_from_meeting_results(meeting_task, meeting_results)
            
            # Should have created new tasks from action items
            assert len(meeting_task.spawned_tasks) > 0
            assert orchestrator.execution_stats["tasks_spawned"] > 0
            
            # Check that spawned tasks exist in registry
            for spawned_id in meeting_task.spawned_tasks:
                assert spawned_id in orchestrator.task_registry
            
        finally:
            await orchestrator.world.shutdown()


@pytest.mark.asyncio
class TestMockExecution:
    """Tests using mock implementations for fast execution"""
    
    async def setup_method(self):
        """Setup with mocked components"""
        await initialize_event_bus()
        
        # Create orchestrator with mock world
        class MockAsyncTinyWorld:
            def __init__(self, *args, **kwargs):
                self.agents = []
                
            def add_agent(self, agent):
                self.agents.append(agent)
                
            async def async_run(self, steps=1):
                await asyncio.sleep(0.01)  # Minimal delay
                return f"Mock meeting completed in {steps} steps"
                
            async def shutdown(self):
                pass
        
        self.orchestrator = AgentOrchestrator(MockAsyncTinyWorld())
        await self.orchestrator.initialize_event_bus()
    
    async def teardown_method(self):
        """Cleanup"""
        await shutdown_event_bus()
    
    async def test_rapid_task_execution(self):
        """Test rapid execution of multiple tasks"""
        # Create mock agents
        class MockAgent:
            def __init__(self, name):
                self.name = name
                
            async def async_listen_and_act(self, prompt):
                await asyncio.sleep(0.01)
                return f"Mock response to: {prompt[:50]}"
            
            def set_environment_context(self, **kwargs):
                pass
        
        # Register mock agents
        for i in range(3):
            agent = MockAgent(f"Agent_{i}")
            profile = AgentProfile(
                agent_id=f"Agent_{i}",
                agent_instance=agent,
                skills={"general": 7, "mock": 8}
            )
            self.orchestrator.agent_registry[f"Agent_{i}"] = profile
        
        # Create multiple tasks
        tasks = []
        for i in range(5):
            task = TaskDefinition(
                task_id=f"mock_task_{i}",
                description=f"Mock task {i} description",
                required_skills={"general": 5},
                priority=1,
                scheduled_date=datetime.now()
            )
            tasks.append(task)
            self.orchestrator.task_registry[task.task_id] = task
        
        # Set up project
        self.orchestrator.project = ProjectDefinition(
            project_id="mock_project",
            title="Mock Project",
            description="Fast mock execution test",
            execution_mode=ExecutionMode.FULLY_AUTOMATED,
            scheduling_mode=SchedulingMode.SAME_DAY,
            start_date=datetime.now(),
            tasks=tasks
        )
        
        # Execute tasks rapidly
        start_time = datetime.now()
        
        ready_tasks = self.orchestrator._get_ready_tasks()
        await self.orchestrator._execute_tasks_batch(ready_tasks)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Should complete quickly with mocks
        assert execution_time < 1.0
        assert self.orchestrator.execution_stats["tasks_completed"] > 0


async def demo_orchestrator_features():
    """Demonstration of key orchestrator features"""
    print("🎯 AgentOrchestrator Features Demo")
    print("=" * 50)
    
    await initialize_event_bus()
    
    try:
        # 1. Test compressed project execution
        print("\n⚡ Testing Compressed Project Execution")
        project_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "projects", 
            "healthcare_blockchain_compressed.json"
        )
        
        if os.path.exists(project_path):
            print(f"📁 Loading project: {project_path}")
            
            # Create orchestrator
            orchestrator = AgentOrchestrator()
            await orchestrator.initialize_event_bus()
            
            try:
                await orchestrator.load_project(project_path)
                print(f"✅ Project loaded: {orchestrator.project.title}")
                print(f"📋 Tasks: {len(orchestrator.project.tasks)}")
                print(f"👥 Agents: {len(orchestrator.agent_registry)}")
                print(f"🗓️ Execution mode: {orchestrator.project.execution_mode.value}")
                print(f"⏱️ Scheduling mode: {orchestrator.project.scheduling_mode.value}")
                
                # Show task schedule
                print("\n📅 Task Schedule:")
                for task in orchestrator.project.tasks:
                    status = "✅" if task.meeting_required else "📝"
                    deps = f" (deps: {', '.join(task.dependencies)})" if task.dependencies else ""
                    print(f"  {status} {task.task_id}: {task.description[:60]}...{deps}")
                
                print("\n🚀 Starting project execution...")
                result = await orchestrator.run_project_fully_automated()
                
                print("\n📊 Execution Results:")
                print(f"  ✅ Tasks completed: {result['task_summary']['completed_tasks']}")
                print(f"  🏢 Meetings held: {result['statistics']['meetings_held']}")
                print(f"  📋 Tasks spawned: {result['statistics']['tasks_spawned']}")
                print(f"  📈 Skill improvements: {result['statistics']['agent_skill_improvements']}")
                
                if result.get('duration'):
                    print(f"  ⏱️ Duration: {result['duration']}")
                
            finally:
                await orchestrator.world.shutdown()
        else:
            print("❌ Compressed project file not found")
        
        # 2. Test different execution modes
        print("\n🎛️ Testing Different Execution Modes")
        
        execution_modes = ["fully_automated", "incremental", "simulation"]
        for mode in execution_modes:
            print(f"\n🔄 Testing {mode} mode...")
            try:
                # Use convenience function
                if os.path.exists(project_path):
                    result = await run_healthcare_blockchain_project(project_path, mode)
                    print(f"  ✅ {mode} mode completed successfully")
                    print(f"  📊 Completed: {result['task_summary']['completed_tasks']} tasks")
                else:
                    print(f"  ⚠️ Skipped {mode} mode - project file not found")
            except Exception as error:
                print(f"  ❌ {mode} mode failed: {error}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as error:
        print(f"\n❌ Demo failed: {error}")
        import traceback
        traceback.print_exc()
    
    finally:
        await shutdown_event_bus()


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demo_orchestrator_features())