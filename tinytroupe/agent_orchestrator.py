"""
Intelligent Agent Auto-Orchestration System for TinyTroupe

This module provides a comprehensive orchestration layer that can:
1. Auto-assign tasks to agents based on expertise and availability
2. Schedule meetings with flexible timing (same-day or distributed)
3. Process meeting outcomes to spawn new tasks and update agent profiles
4. Run in multiple execution modes: fully automated, incremental, or simulation
5. Integrate with CEO interrupts for real-time project steering

Features:
- JSON-driven project definitions with flexible scheduling
- Dynamic task spawning based on meeting outcomes
- Preference learning and agent skill development
- Multiple execution modes for different use cases
- Full integration with AsyncAdaptiveTinyPerson and AsyncTinyWorld
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid

from tinytroupe.async_adaptive_agent import AsyncAdaptiveTinyPerson, create_async_adaptive_agent
from tinytroupe.async_world import AsyncTinyWorld
from tinytroupe.async_event_bus import get_event_bus, EventType, Event
from tinytroupe.extraction import default_extractor

logger = logging.getLogger("tinytroupe.orchestrator")


class ExecutionMode(Enum):
    """Execution modes for the orchestration system"""
    FULLY_AUTOMATED = "fully_automated"    # Run entire project autonomously
    INCREMENTAL = "incremental"           # Execute with checkpoints and human review
    SIMULATION = "simulation"             # Simulate complete project management lifecycle
    

class SchedulingMode(Enum):
    """Scheduling modes for task execution"""
    SAME_DAY = "same_day"                # All tasks on same day for testing
    DISTRIBUTED = "distributed"          # Realistic timeline distribution
    COMPRESSED = "compressed"            # Accelerated but sequential timeline


@dataclass
class AgentProfile:
    """Enhanced agent profile with skill tracking and performance history"""
    agent_id: str
    agent_instance: AsyncAdaptiveTinyPerson
    skills: Dict[str, int]  # skill_name -> proficiency_level (1-10)
    availability: bool = True
    preferences: Dict[str, int] = field(default_factory=dict)  # task_type -> preference (1-10)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    current_workload: int = 0
    skill_development_rate: float = 0.1  # How quickly skills improve
    last_active: Optional[datetime] = None
    
    def update_skill(self, skill_name: str, improvement: float):
        """Update skill level based on performance"""
        current_level = self.skills.get(skill_name, 0)
        new_level = min(10, current_level + improvement * self.skill_development_rate)
        self.skills[skill_name] = round(new_level, 1)
        logger.debug(f"Agent {self.agent_id} skill '{skill_name}' improved: {current_level} -> {new_level}")


@dataclass
class TaskDefinition:
    """Comprehensive task definition with scheduling and execution options"""
    task_id: str
    description: str
    required_skills: Dict[str, int]  # skill_name -> minimum_level
    priority: int = 1
    scheduled_date: Optional[datetime] = None
    meeting_required: bool = False
    attendees: List[str] = field(default_factory=list)  # agent_ids
    dependencies: List[str] = field(default_factory=list)  # task_ids that must complete first
    follow_up_tasks: List[str] = field(default_factory=list)  # task_ids to create after completion
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(hours=1))
    status: str = "pending"  # pending, assigned, in_progress, completed, failed
    assigned_agents: List[str] = field(default_factory=list)
    completion_date: Optional[datetime] = None
    meeting_results: Dict[str, Any] = field(default_factory=dict)
    spawned_tasks: List[str] = field(default_factory=list)  # Tasks created from this task's results
    
    def is_ready_to_execute(self, completed_tasks: set) -> bool:
        """Check if all dependencies are completed"""
        return all(dep_id in completed_tasks for dep_id in self.dependencies)


@dataclass
class ProjectDefinition:
    """Complete project definition loaded from JSON"""
    project_id: str
    title: str
    description: str
    execution_mode: ExecutionMode
    scheduling_mode: SchedulingMode
    start_date: datetime
    compress_timeline: bool = False
    auto_adjust_dates: bool = True
    tasks: List[TaskDefinition] = field(default_factory=list)
    agents: List[Dict[str, Any]] = field(default_factory=list)  # Agent definitions
    ceo_oversight: Dict[str, Any] = field(default_factory=dict)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_json(cls, json_path: str) -> 'ProjectDefinition':
        """Load project definition from JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Parse execution and scheduling modes
        execution_mode = ExecutionMode(data.get('execution_mode', 'incremental'))
        scheduling_mode = SchedulingMode(data.get('scheduling', {}).get('mode', 'distributed'))
        
        # Parse start date
        start_date = datetime.fromisoformat(data.get('scheduling', {}).get('start_date', datetime.now().isoformat()))
        
        # Parse tasks
        tasks = []
        for task_data in data.get('tasks', []):
            scheduled_date = None
            if 'scheduled_date' in task_data:
                scheduled_date = datetime.fromisoformat(task_data['scheduled_date'])
            
            estimated_duration = timedelta(hours=task_data.get('estimated_hours', 1))
            
            task = TaskDefinition(
                task_id=task_data['task_id'],
                description=task_data['description'],
                required_skills=task_data.get('required_skills', {}),
                priority=task_data.get('priority', 1),
                scheduled_date=scheduled_date,
                meeting_required=task_data.get('meeting_required', False),
                attendees=task_data.get('attendees', []),
                dependencies=task_data.get('dependencies', []),
                follow_up_tasks=task_data.get('follow_up_tasks', []),
                estimated_duration=estimated_duration
            )
            tasks.append(task)
        
        return cls(
            project_id=data['project_id'],
            title=data.get('title', data['project_id']),
            description=data.get('description', ''),
            execution_mode=execution_mode,
            scheduling_mode=scheduling_mode,
            start_date=start_date,
            compress_timeline=data.get('scheduling', {}).get('compress_timeline', False),
            auto_adjust_dates=data.get('scheduling', {}).get('auto_adjust_dates', True),
            tasks=tasks,
            agents=data.get('agents', []),
            ceo_oversight=data.get('ceo_oversight', {}),
            success_criteria=data.get('success_criteria', {})
        )


class AgentOrchestrator:
    """
    Intelligent orchestration system for managing agents, tasks, and meetings.
    
    Supports multiple execution modes and flexible scheduling for comprehensive
    project management automation.
    """
    
    def __init__(self, world: AsyncTinyWorld = None):
        self.world = world or AsyncTinyWorld("Orchestrator World", enable_ceo_interrupt=True)
        self.agent_registry: Dict[str, AgentProfile] = {}
        self.task_registry: Dict[str, TaskDefinition] = {}
        self.completed_tasks: set = set()
        self.project: Optional[ProjectDefinition] = None
        self.current_time: datetime = datetime.now()
        self.execution_paused: bool = False
        self.execution_stats: Dict[str, Any] = {
            "tasks_completed": 0,
            "meetings_held": 0,
            "tasks_spawned": 0,
            "agent_skill_improvements": 0,
            "project_start_time": None,
            "project_end_time": None
        }
        
    async def initialize_event_bus(self):
        """Initialize event bus for orchestrator"""
        self.event_bus = await get_event_bus()
        await self.event_bus.subscribe(EventType.CEO_INTERRUPT, self._handle_ceo_interrupt)
        
    async def _handle_ceo_interrupt(self, event: Event):
        """Handle CEO interrupts for real-time project steering"""
        message = event.data.get('message', '').lower()
        logger.info(f"CEO interrupt received: {message}")
        
        if 'pause' in message:
            self.execution_paused = True
            logger.info("Project execution paused by CEO")
        elif 'resume' in message:
            self.execution_paused = False
            logger.info("Project execution resumed by CEO")
        elif 'status' in message:
            await self._provide_project_status()
        elif 'adjust' in message or 'change' in message:
            await self._handle_project_adjustment(message)
    
    def register_agent(self, agent: AsyncAdaptiveTinyPerson, skills: Dict[str, int], 
                      preferences: Dict[str, int] = None):
        """Register an agent with the orchestrator"""
        profile = AgentProfile(
            agent_id=agent.name,
            agent_instance=agent,
            skills=skills.copy(),
            preferences=preferences or {},
            last_active=datetime.now()
        )
        self.agent_registry[agent.name] = profile
        self.world.add_agent(agent)
        logger.info(f"Registered agent: {agent.name} with skills: {skills}")
    
    async def load_project(self, json_path: str):
        """Load a project definition from JSON"""
        self.project = ProjectDefinition.from_json(json_path)
        self.current_time = self.project.start_date
        
        # Load tasks into registry
        for task in self.project.tasks:
            self.task_registry[task.task_id] = task
        
        # Create agents if defined in project
        await self._create_project_agents()
        
        # Adjust scheduling based on mode
        await self._adjust_project_scheduling()
        
        logger.info(f"Loaded project: {self.project.title} with {len(self.project.tasks)} tasks")
    
    async def _create_project_agents(self):
        """Create agents defined in project JSON if they don't exist"""
        for agent_def in self.project.agents:
            agent_id = agent_def['agent_id']
            if agent_id not in self.agent_registry:
                # Create new agent
                agent = create_async_adaptive_agent(
                    name=agent_def['name'],
                    occupation=agent_def['occupation'],
                    personality_traits=agent_def.get('personality_traits', []),
                    professional_interests=agent_def.get('professional_interests', []),
                    skills=agent_def.get('skills', []),
                    years_experience=agent_def.get('years_experience', '5+ years')
                )
                
                # Register with orchestrator
                self.register_agent(
                    agent=agent,
                    skills=agent_def.get('skill_levels', {}),
                    preferences=agent_def.get('preferences', {})
                )
    
    async def _adjust_project_scheduling(self):
        """Adjust task scheduling based on project settings"""
        if self.project.scheduling_mode == SchedulingMode.SAME_DAY:
            # Schedule all tasks for the same day with time intervals
            current_time = self.project.start_date
            for task in self.project.tasks:
                task.scheduled_date = current_time
                current_time += timedelta(minutes=30)  # 30-minute intervals
                
        elif self.project.scheduling_mode == SchedulingMode.COMPRESSED:
            # Compress timeline but maintain dependencies
            await self._compress_timeline()
            
        elif self.project.scheduling_mode == SchedulingMode.DISTRIBUTED:
            # Use realistic scheduling with proper time distribution
            await self._distribute_timeline()
    
    async def _compress_timeline(self):
        """Compress project timeline while respecting dependencies"""
        # Topological sort to respect dependencies
        scheduled_tasks = set()
        current_date = self.project.start_date
        
        while len(scheduled_tasks) < len(self.project.tasks):
            # Find tasks ready to schedule
            ready_tasks = [
                task for task in self.project.tasks 
                if task.task_id not in scheduled_tasks and task.is_ready_to_execute(scheduled_tasks)
            ]
            
            if not ready_tasks:
                break
                
            # Schedule ready tasks
            for task in ready_tasks:
                task.scheduled_date = current_date
                scheduled_tasks.add(task.task_id)
                
            current_date += timedelta(hours=2)  # 2-hour intervals
    
    async def _distribute_timeline(self):
        """Distribute tasks across realistic timeline"""
        # More sophisticated scheduling that considers:
        # - Agent availability
        # - Meeting coordination
        # - Realistic work patterns
        
        current_date = self.project.start_date
        scheduled_tasks = set()
        
        # Group tasks by dependency levels
        dependency_levels = self._calculate_dependency_levels()
        
        for level in sorted(dependency_levels.keys()):
            level_tasks = dependency_levels[level]
            
            # Schedule tasks at this level
            for task in level_tasks:
                if task.meeting_required:
                    # Schedule meetings during business hours
                    task.scheduled_date = self._find_next_meeting_slot(current_date)
                    current_date = max(current_date, task.scheduled_date + task.estimated_duration)
                else:
                    # Schedule individual tasks
                    task.scheduled_date = current_date
                    current_date += task.estimated_duration
                
                scheduled_tasks.add(task.task_id)
            
            # Add buffer between dependency levels
            current_date += timedelta(days=1)
    
    def _calculate_dependency_levels(self) -> Dict[int, List[TaskDefinition]]:
        """Calculate dependency levels for proper scheduling"""
        levels = {}
        task_levels = {}
        
        def calculate_level(task_id: str) -> int:
            if task_id in task_levels:
                return task_levels[task_id]
            
            task = self.task_registry[task_id]
            if not task.dependencies:
                level = 0
            else:
                level = max(calculate_level(dep) for dep in task.dependencies) + 1
            
            task_levels[task_id] = level
            return level
        
        # Calculate levels for all tasks
        for task in self.project.tasks:
            level = calculate_level(task.task_id)
            if level not in levels:
                levels[level] = []
            levels[level].append(task)
        
        return levels
    
    def _find_next_meeting_slot(self, start_time: datetime) -> datetime:
        """Find next available meeting slot during business hours"""
        # Ensure meetings are scheduled during business hours (9 AM - 5 PM)
        target_time = start_time.replace(hour=9, minute=0, second=0, microsecond=0)
        
        if start_time.hour >= 17:  # After 5 PM
            target_time += timedelta(days=1)
        elif start_time.hour < 9:  # Before 9 AM
            pass  # Keep same day
        else:
            target_time = start_time
        
        return target_time
    
    async def run_project_fully_automated(self) -> Dict[str, Any]:
        """Run entire project autonomously from start to finish"""
        logger.info(f"Starting fully automated execution of project: {self.project.title}")
        self.execution_stats["project_start_time"] = datetime.now()
        
        try:
            while not self._is_project_complete():
                if self.execution_paused:
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks
                ready_tasks = self._get_ready_tasks()
                if ready_tasks:
                    await self._execute_tasks_batch(ready_tasks)
                else:
                    # Advance time if no tasks are ready
                    self._advance_time()
                
                # Brief pause to allow for interrupts
                await asyncio.sleep(0.1)
            
            self.execution_stats["project_end_time"] = datetime.now()
            logger.info("Project completed successfully in fully automated mode")
            return await self._generate_project_report()
            
        except Exception as error:
            logger.error(f"Error in fully automated execution: {error}")
            raise
    
    async def run_project_incremental(self, checkpoint_frequency: str = "after_each_meeting") -> Dict[str, Any]:
        """Execute project with checkpoints for human review"""
        logger.info(f"Starting incremental execution of project: {self.project.title}")
        self.execution_stats["project_start_time"] = datetime.now()
        
        try:
            while not self._is_project_complete():
                if self.execution_paused:
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks
                ready_tasks = self._get_ready_tasks()
                if ready_tasks:
                    await self._execute_tasks_batch(ready_tasks)
                    
                    # Check for checkpoint conditions
                    if await self._should_checkpoint(checkpoint_frequency, ready_tasks):
                        await self._create_checkpoint()
                        await self._wait_for_checkpoint_approval()
                else:
                    self._advance_time()
                
                await asyncio.sleep(0.1)
            
            self.execution_stats["project_end_time"] = datetime.now()
            logger.info("Project completed successfully in incremental mode")
            return await self._generate_project_report()
            
        except Exception as error:
            logger.error(f"Error in incremental execution: {error}")
            raise
    
    async def simulate_complete_project(self, spawn_additional_meetings: bool = True,
                                      adaptive_task_creation: bool = True) -> Dict[str, Any]:
        """Simulate complete project management lifecycle"""
        logger.info(f"Starting simulation of project: {self.project.title}")
        self.execution_stats["project_start_time"] = datetime.now()
        
        try:
            while not self._is_project_complete():
                if self.execution_paused:
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks
                ready_tasks = self._get_ready_tasks()
                if ready_tasks:
                    await self._execute_tasks_batch(ready_tasks)
                    
                    # Simulate project management activities
                    if spawn_additional_meetings:
                        await self._spawn_management_meetings()
                    
                    if adaptive_task_creation:
                        await self._create_adaptive_tasks()
                else:
                    self._advance_time()
                
                await asyncio.sleep(0.1)
            
            self.execution_stats["project_end_time"] = datetime.now()
            logger.info("Project simulation completed successfully")
            return await self._generate_project_report()
            
        except Exception as error:
            logger.error(f"Error in project simulation: {error}")
            raise
    
    def _get_ready_tasks(self) -> List[TaskDefinition]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        for task in self.project.tasks:
            if (task.status == "pending" and 
                task.is_ready_to_execute(self.completed_tasks) and
                (task.scheduled_date is None or task.scheduled_date <= self.current_time)):
                ready_tasks.append(task)
        
        # Sort by priority and scheduled date
        ready_tasks.sort(key=lambda t: (-t.priority, t.scheduled_date or datetime.min))
        return ready_tasks
    
    async def _execute_tasks_batch(self, tasks: List[TaskDefinition]):
        """Execute a batch of tasks concurrently when possible"""
        # Group tasks by type (meeting vs individual)
        meeting_tasks = [t for t in tasks if t.meeting_required]
        individual_tasks = [t for t in tasks if not t.meeting_required]
        
        # Execute individual tasks concurrently
        if individual_tasks:
            individual_futures = [self._execute_individual_task(task) for task in individual_tasks]
            await asyncio.gather(*individual_futures, return_exceptions=True)
        
        # Execute meetings sequentially (can't have multiple meetings at once)
        for task in meeting_tasks:
            await self._execute_meeting_task(task)
    
    async def _execute_individual_task(self, task: TaskDefinition):
        """Execute an individual task assignment"""
        # Find best agent for task
        assigned_agent = self._find_best_agent_for_task(task)
        if not assigned_agent:
            logger.warning(f"No suitable agent found for task: {task.task_id}")
            return
        
        # Assign and execute task
        task.status = "assigned"
        task.assigned_agents = [assigned_agent.agent_id]
        assigned_agent.availability = False
        assigned_agent.current_workload += 1
        
        try:
            logger.info(f"Executing task {task.task_id} with agent {assigned_agent.agent_id}")
            
            # Simulate task execution
            await assigned_agent.agent_instance.async_listen_and_act(
                f"Please work on the following task: {task.description}"
            )
            
            # Mark task as completed
            task.status = "completed"
            task.completion_date = self.current_time
            self.completed_tasks.add(task.task_id)
            self.execution_stats["tasks_completed"] += 1
            
            # Update agent profile
            await self._update_agent_profile_from_task(assigned_agent, task)
            
            # Spawn follow-up tasks
            await self._spawn_follow_up_tasks(task)
            
        except Exception as error:
            logger.error(f"Error executing task {task.task_id}: {error}")
            task.status = "failed"
        finally:
            assigned_agent.availability = True
            assigned_agent.current_workload -= 1
            assigned_agent.last_active = self.current_time
    
    async def _execute_meeting_task(self, task: TaskDefinition):
        """Execute a meeting task"""
        # Get meeting attendees
        attendee_profiles = [self.agent_registry[agent_id] for agent_id in task.attendees 
                           if agent_id in self.agent_registry]
        
        if not attendee_profiles:
            logger.warning(f"No attendees found for meeting task: {task.task_id}")
            return
        
        # Mark attendees as unavailable
        for profile in attendee_profiles:
            profile.availability = False
            profile.current_workload += 1
        
        try:
            logger.info(f"Executing meeting {task.task_id} with attendees: {task.attendees}")
            
            # Create meeting world
            meeting_agents = [profile.agent_instance for profile in attendee_profiles]
            meeting_world = AsyncTinyWorld(
                name=f"Meeting: {task.task_id}",
                agents=meeting_agents,
                is_meeting=True,
                enable_ceo_interrupt=True
            )
            
            # Initialize meeting context
            for agent in meeting_agents:
                agent.set_environment_context(
                    meeting_type="project_meeting",
                    agenda_items=[task.description],
                    participant_roles=[p.agent_id for p in attendee_profiles]
                )
            
            # Run meeting
            task.status = "in_progress"
            await meeting_world.async_run(steps=6)  # 6 rounds for productive meeting
            
            # Extract meeting results
            meeting_results = default_extractor.extract_results_from_world(
                meeting_world,
                extraction_objective=f"Extract key decisions, action items, and insights from meeting about: {task.description}",
                fields=["decisions", "action_items", "insights", "next_steps"],
                verbose=False
            )
            
            task.meeting_results = meeting_results
            task.status = "completed"
            task.completion_date = self.current_time
            self.completed_tasks.add(task.task_id)
            self.execution_stats["meetings_held"] += 1
            
            # Update agent profiles based on meeting participation
            await self._update_agent_profiles_from_meeting(attendee_profiles, meeting_results)
            
            # Spawn follow-up tasks based on meeting results
            await self._spawn_tasks_from_meeting_results(task, meeting_results)
            
            # Clean up meeting world
            await meeting_world.shutdown()
            
        except Exception as error:
            logger.error(f"Error executing meeting {task.task_id}: {error}")
            task.status = "failed"
        finally:
            # Mark attendees as available
            for profile in attendee_profiles:
                profile.availability = True
                profile.current_workload -= 1
                profile.last_active = self.current_time
    
    def _find_best_agent_for_task(self, task: TaskDefinition) -> Optional[AgentProfile]:
        """Find best available agent for a task"""
        eligible_agents = []
        
        for profile in self.agent_registry.values():
            if profile.availability and self._meets_skill_requirements(profile, task.required_skills):
                eligible_agents.append(profile)
        
        if not eligible_agents:
            return None
        
        # Score agents based on skill match, preferences, and workload
        def score_agent(profile: AgentProfile) -> float:
            skill_score = sum(profile.skills.get(skill, 0) for skill in task.required_skills) / len(task.required_skills)
            preference_score = profile.preferences.get(task.description.split()[0].lower(), 5)  # Default neutral preference
            workload_penalty = profile.current_workload * 0.5
            
            return skill_score + preference_score - workload_penalty
        
        return max(eligible_agents, key=score_agent)
    
    def _meets_skill_requirements(self, profile: AgentProfile, required_skills: Dict[str, int]) -> bool:
        """Check if agent meets minimum skill requirements"""
        for skill, min_level in required_skills.items():
            if profile.skills.get(skill, 0) < min_level:
                return False
        return True
    
    async def _update_agent_profile_from_task(self, profile: AgentProfile, task: TaskDefinition):
        """Update agent profile based on task completion"""
        # Improve relevant skills
        for skill in task.required_skills:
            improvement = 0.2  # Base improvement
            if task.status == "completed":
                improvement *= 1.5  # Bonus for successful completion
            profile.update_skill(skill, improvement)
            self.execution_stats["agent_skill_improvements"] += 1
        
        # Record performance
        performance_record = {
            "task_id": task.task_id,
            "completion_date": task.completion_date,
            "status": task.status,
            "skills_used": list(task.required_skills.keys())
        }
        profile.performance_history.append(performance_record)
    
    async def _update_agent_profiles_from_meeting(self, profiles: List[AgentProfile], meeting_results: Dict[str, Any]):
        """Update agent profiles based on meeting participation"""
        for profile in profiles:
            # Improve communication and collaboration skills
            profile.update_skill("communication", 0.3)
            profile.update_skill("collaboration", 0.2)
            
            # Record meeting participation
            performance_record = {
                "meeting_results": meeting_results,
                "participation_date": self.current_time,
                "type": "meeting"
            }
            profile.performance_history.append(performance_record)
            self.execution_stats["agent_skill_improvements"] += 1
    
    async def _spawn_follow_up_tasks(self, completed_task: TaskDefinition):
        """Spawn predefined follow-up tasks"""
        for follow_up_id in completed_task.follow_up_tasks:
            if follow_up_id in self.task_registry:
                follow_up_task = self.task_registry[follow_up_id]
                if follow_up_task.status == "pending":
                    # Update scheduling if needed
                    if follow_up_task.scheduled_date is None:
                        follow_up_task.scheduled_date = self.current_time + timedelta(hours=1)
                    completed_task.spawned_tasks.append(follow_up_id)
                    self.execution_stats["tasks_spawned"] += 1
    
    async def _spawn_tasks_from_meeting_results(self, meeting_task: TaskDefinition, meeting_results: Dict[str, Any]):
        """Spawn new tasks based on meeting outcomes"""
        action_items = meeting_results.get("action_items", [])
        
        for i, action_item in enumerate(action_items):
            if isinstance(action_item, str) and len(action_item) > 10:  # Valid action item
                # Create new task from action item
                new_task_id = f"{meeting_task.task_id}_action_{i+1}"
                
                # Infer required skills from action item content
                required_skills = self._infer_skills_from_text(action_item)
                
                new_task = TaskDefinition(
                    task_id=new_task_id,
                    description=action_item,
                    required_skills=required_skills,
                    priority=meeting_task.priority - 1,  # Lower priority than original
                    scheduled_date=self.current_time + timedelta(days=1),
                    meeting_required=False
                )
                
                self.task_registry[new_task_id] = new_task
                self.project.tasks.append(new_task)
                meeting_task.spawned_tasks.append(new_task_id)
                self.execution_stats["tasks_spawned"] += 1
                
                logger.info(f"Spawned new task from meeting: {new_task_id}")
    
    def _infer_skills_from_text(self, text: str) -> Dict[str, int]:
        """Infer required skills from task description text"""
        # Simple keyword-based skill inference
        skill_keywords = {
            "development": ["develop", "code", "implement", "program", "build"],
            "design": ["design", "create", "plan", "architect"],
            "compliance": ["compliance", "regulation", "legal", "audit", "hipaa"],
            "communication": ["coordinate", "meet", "discuss", "present", "communicate"],
            "analysis": ["analyze", "research", "investigate", "study", "evaluate"],
            "project_management": ["manage", "coordinate", "schedule", "plan", "organize"]
        }
        
        text_lower = text.lower()
        required_skills = {}
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                required_skills[skill] = 5  # Medium skill level requirement
        
        return required_skills if required_skills else {"general": 3}
    
    async def _spawn_management_meetings(self):
        """Spawn additional management meetings based on project state"""
        # Check if it's time for a status meeting
        if len(self.completed_tasks) > 0 and len(self.completed_tasks) % 5 == 0:  # Every 5 completed tasks
            status_meeting_id = f"status_meeting_{len(self.completed_tasks)//5}"
            
            if status_meeting_id not in self.task_registry:
                status_task = TaskDefinition(
                    task_id=status_meeting_id,
                    description=f"Project status review - completed {len(self.completed_tasks)} tasks",
                    required_skills={"project_management": 6, "communication": 5},
                    priority=3,
                    scheduled_date=self.current_time + timedelta(hours=2),
                    meeting_required=True,
                    attendees=list(self.agent_registry.keys())[:4]  # Limit to 4 attendees
                )
                
                self.task_registry[status_meeting_id] = status_task
                self.project.tasks.append(status_task)
                self.execution_stats["tasks_spawned"] += 1
                logger.info(f"Spawned status meeting: {status_meeting_id}")
    
    async def _create_adaptive_tasks(self):
        """Create new tasks based on project evolution"""
        # Analyze recent meeting results for emerging needs
        recent_meetings = [
            task for task in self.project.tasks 
            if task.meeting_required and task.status == "completed" and 
            task.completion_date and (self.current_time - task.completion_date).days < 2
        ]
        
        for meeting_task in recent_meetings:
            # Look for unaddressed concerns or risks in meeting results
            insights = meeting_task.meeting_results.get("insights", [])
            
            for insight in insights:
                if isinstance(insight, str) and ("risk" in insight.lower() or "concern" in insight.lower()):
                    # Create risk mitigation task
                    risk_task_id = f"risk_mitigation_{uuid.uuid4().hex[:8]}"
                    
                    risk_task = TaskDefinition(
                        task_id=risk_task_id,
                        description=f"Address risk/concern: {insight}",
                        required_skills={"risk_management": 6, "analysis": 5},
                        priority=4,  # High priority for risks
                        scheduled_date=self.current_time + timedelta(hours=4),
                        meeting_required=len(insight) > 100  # Long concerns need meetings
                    )
                    
                    self.task_registry[risk_task_id] = risk_task
                    self.project.tasks.append(risk_task)
                    self.execution_stats["tasks_spawned"] += 1
                    logger.info(f"Created adaptive risk mitigation task: {risk_task_id}")
    
    def _advance_time(self):
        """Advance simulation time when no tasks are ready"""
        # Find next scheduled task
        next_tasks = [
            task for task in self.project.tasks 
            if task.status == "pending" and task.scheduled_date and task.scheduled_date > self.current_time
        ]
        
        if next_tasks:
            next_time = min(task.scheduled_date for task in next_tasks)
            self.current_time = next_time
        else:
            # Advance by standard interval
            self.current_time += timedelta(hours=1)
    
    def _is_project_complete(self) -> bool:
        """Check if project is complete"""
        return all(task.status in ["completed", "failed"] for task in self.project.tasks)
    
    async def _should_checkpoint(self, frequency: str, completed_tasks: List[TaskDefinition]) -> bool:
        """Determine if checkpoint is needed"""
        if frequency == "after_each_meeting":
            return any(task.meeting_required for task in completed_tasks)
        elif frequency == "after_major_milestone":
            return len(self.completed_tasks) % 10 == 0  # Every 10 tasks
        elif frequency == "daily":
            # Check if a day has passed since last checkpoint (simplified)
            return True
        return False
    
    async def _create_checkpoint(self):
        """Create project checkpoint"""
        checkpoint_data = {
            "timestamp": self.current_time.isoformat(),
            "completed_tasks": len(self.completed_tasks),
            "total_tasks": len(self.project.tasks),
            "agent_status": {
                agent_id: {
                    "availability": profile.availability,
                    "workload": profile.current_workload,
                    "skills": profile.skills
                }
                for agent_id, profile in self.agent_registry.items()
            },
            "execution_stats": self.execution_stats.copy()
        }
        
        logger.info(f"Checkpoint created: {len(self.completed_tasks)}/{len(self.project.tasks)} tasks completed")
        return checkpoint_data
    
    async def _wait_for_checkpoint_approval(self):
        """Wait for approval to continue (simulated for now)"""
        logger.info("Waiting for checkpoint approval...")
        await asyncio.sleep(1)  # Simulate human review time
        logger.info("Checkpoint approved, continuing execution")
    
    async def _provide_project_status(self):
        """Provide current project status"""
        status = {
            "project": self.project.title,
            "progress": f"{len(self.completed_tasks)}/{len(self.project.tasks)} tasks completed",
            "current_time": self.current_time.isoformat(),
            "execution_mode": self.project.execution_mode.value,
            "stats": self.execution_stats
        }
        logger.info(f"Project status: {status}")
        return status
    
    async def _handle_project_adjustment(self, message: str):
        """Handle project adjustments from CEO"""
        # Simple adjustment handling - can be expanded
        if "priority" in message:
            # Adjust task priorities
            for task in self.project.tasks:
                if task.status == "pending":
                    task.priority += 1
            logger.info("Task priorities adjusted by CEO")
        elif "timeline" in message:
            # Compress timeline
            self.project.compress_timeline = True
            await self._compress_timeline()
            logger.info("Timeline compressed by CEO")
    
    async def _generate_project_report(self) -> Dict[str, Any]:
        """Generate comprehensive project completion report"""
        duration = None
        if self.execution_stats["project_start_time"] and self.execution_stats["project_end_time"]:
            duration = self.execution_stats["project_end_time"] - self.execution_stats["project_start_time"]
        
        report = {
            "project_id": self.project.project_id,
            "title": self.project.title,
            "execution_mode": self.project.execution_mode.value,
            "scheduling_mode": self.project.scheduling_mode.value,
            "start_time": self.execution_stats["project_start_time"],
            "end_time": self.execution_stats["project_end_time"],
            "duration": str(duration) if duration else None,
            "statistics": self.execution_stats,
            "task_summary": {
                "total_tasks": len(self.project.tasks),
                "completed_tasks": len([t for t in self.project.tasks if t.status == "completed"]),
                "failed_tasks": len([t for t in self.project.tasks if t.status == "failed"]),
                "spawned_tasks": sum(len(t.spawned_tasks) for t in self.project.tasks)
            },
            "agent_development": {
                agent_id: {
                    "final_skills": profile.skills,
                    "tasks_completed": len([p for p in profile.performance_history if p.get("type") != "meeting"]),
                    "meetings_attended": len([p for p in profile.performance_history if p.get("type") == "meeting"])
                }
                for agent_id, profile in self.agent_registry.items()
            }
        }
        
        logger.info("Project completion report generated")
        return report
    
    async def save_project_state(self, filepath: str):
        """Save current project state to file"""
        state = {
            "project": self.project.__dict__ if self.project else None,
            "task_registry": {k: v.__dict__ for k, v in self.task_registry.items()},
            "completed_tasks": list(self.completed_tasks),
            "current_time": self.current_time.isoformat(),
            "execution_stats": self.execution_stats,
            "agent_profiles": {k: v.__dict__ for k, v in self.agent_registry.items()}
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        logger.info(f"Project state saved to: {filepath}")
    
    async def load_project_state(self, filepath: str):
        """Load project state from file"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        # Restore state (implementation depends on specific needs)
        self.current_time = datetime.fromisoformat(state["current_time"])
        self.completed_tasks = set(state["completed_tasks"])
        self.execution_stats = state["execution_stats"]
        
        logger.info(f"Project state loaded from: {filepath}")


# Convenience functions for easy orchestrator usage
async def create_orchestrator_with_agents(agents_config: List[Dict[str, Any]]) -> AgentOrchestrator:
    """Create orchestrator and register agents from configuration"""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize_event_bus()
    
    for agent_config in agents_config:
        agent = create_async_adaptive_agent(**agent_config["agent_params"])
        orchestrator.register_agent(
            agent=agent,
            skills=agent_config["skills"],
            preferences=agent_config.get("preferences", {})
        )
    
    return orchestrator


async def run_healthcare_blockchain_project(project_json_path: str, execution_mode: str = "incremental") -> Dict[str, Any]:
    """Run a healthcare blockchain project with specified execution mode"""
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize_event_bus()
    await orchestrator.load_project(project_json_path)
    
    if execution_mode == "fully_automated":
        return await orchestrator.run_project_fully_automated()
    elif execution_mode == "incremental":
        return await orchestrator.run_project_incremental()
    elif execution_mode == "simulation":
        return await orchestrator.simulate_complete_project()
    else:
        raise ValueError(f"Unknown execution mode: {execution_mode}")