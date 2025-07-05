"""
PersistentWorldManager - Central State Lifecycle Coordinator

This module provides the central coordination system for persistent multi-day 
business simulations, including:
- State loading from previous simulation days
- Calendar event integration for scheduled activities
- World initialization with combined state and events
- End-of-day state persistence for continuity
- Support for different world types (business/research/hospital)
"""

import asyncio
import json
import logging
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union, Type
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import uuid

from tinytroupe.business_time_manager import BusinessTimeManager, BusinessDay
from tinytroupe.business_world import BusinessSimulationWorld
from tinytroupe.business_simulation import HiringDatabase
from tinytroupe.task_management import TaskManager, BusinessTask
from tinytroupe.task_assignment import TaskAssignmentEngine

logger = logging.getLogger("tinytroupe.persistence")


class WorldType(Enum):
    """Types of persistent worlds"""
    BUSINESS = "business"
    RESEARCH = "research"
    HOSPITAL = "hospital"
    EDUCATION = "education"
    CUSTOM = "custom"


class StorageBackend(Enum):
    """Storage backend options"""
    JSON_FILES = "json_files"
    SQLITE = "sqlite" 
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


@dataclass
class WorldState:
    """Complete world state for a simulation day"""
    world_id: str
    world_type: WorldType
    simulation_date: date
    
    # Core state components
    time_manager_state: Dict[str, Any]
    task_manager_state: Dict[str, Any]
    hiring_database_state: Dict[str, Any]
    business_metrics: Dict[str, Any]
    
    # World-specific state
    world_specific_state: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    created_timestamp: datetime = field(default_factory=datetime.now)
    simulation_version: str = "1.0"
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "world_id": self.world_id,
            "world_type": self.world_type.value,
            "simulation_date": self.simulation_date.isoformat(),
            "time_manager_state": self.time_manager_state,
            "task_manager_state": self.task_manager_state,
            "hiring_database_state": self.hiring_database_state,
            "business_metrics": self.business_metrics,
            "world_specific_state": self.world_specific_state,
            "created_timestamp": self.created_timestamp.isoformat(),
            "simulation_version": self.simulation_version,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldState':
        """Create from dictionary"""
        return cls(
            world_id=data["world_id"],
            world_type=WorldType(data["world_type"]),
            simulation_date=date.fromisoformat(data["simulation_date"]),
            time_manager_state=data["time_manager_state"],
            task_manager_state=data["task_manager_state"],
            hiring_database_state=data["hiring_database_state"],
            business_metrics=data["business_metrics"],
            world_specific_state=data.get("world_specific_state", {}),
            created_timestamp=datetime.fromisoformat(data["created_timestamp"]),
            simulation_version=data.get("simulation_version", "1.0"),
            notes=data.get("notes", "")
        )


@dataclass
class SimulationDay:
    """Complete simulation day with state and events"""
    virtual_date: date
    business_day: BusinessDay
    scheduled_events: List[Dict[str, Any]]
    previous_state: Optional[WorldState]
    world_instance: Optional[BusinessSimulationWorld] = None


class StateStorage:
    """
    Abstract state storage interface with multiple backend support.
    Handles persistence of world states across simulation days.
    """
    
    def __init__(self, backend: StorageBackend = StorageBackend.JSON_FILES,
                 storage_path: str = "simulation_states"):
        self.backend = backend
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        logger.info(f"Initialized StateStorage with {backend.value} backend at {storage_path}")
    
    def save_world_state(self, world_state: WorldState) -> bool:
        """Save world state to storage"""
        try:
            if self.backend == StorageBackend.JSON_FILES:
                return self._save_json(world_state)
            else:
                logger.error(f"Storage backend {self.backend.value} not implemented")
                return False
        except Exception as e:
            logger.error(f"Failed to save world state: {e}")
            return False
    
    def load_world_state(self, world_id: str, simulation_date: date) -> Optional[WorldState]:
        """Load world state from storage"""
        try:
            if self.backend == StorageBackend.JSON_FILES:
                return self._load_json(world_id, simulation_date)
            else:
                logger.error(f"Storage backend {self.backend.value} not implemented")
                return None
        except Exception as e:
            logger.error(f"Failed to load world state: {e}")
            return None
    
    def get_latest_state(self, world_id: str) -> Optional[WorldState]:
        """Get the most recent state for a world"""
        if self.backend == StorageBackend.JSON_FILES:
            return self._get_latest_json_state(world_id)
        return None
    
    def list_available_dates(self, world_id: str) -> List[date]:
        """List all available simulation dates for a world"""
        if self.backend == StorageBackend.JSON_FILES:
            return self._list_json_dates(world_id)
        return []
    
    def _save_json(self, world_state: WorldState) -> bool:
        """Save state as JSON file"""
        filename = f"{world_state.world_id}_{world_state.simulation_date.isoformat()}.json"
        filepath = self.storage_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(world_state.to_dict(), f, indent=2)
        
        logger.info(f"Saved world state to {filepath}")
        return True
    
    def _load_json(self, world_id: str, simulation_date: date) -> Optional[WorldState]:
        """Load state from JSON file"""
        filename = f"{world_id}_{simulation_date.isoformat()}.json"
        filepath = self.storage_path / filename
        
        if not filepath.exists():
            logger.debug(f"No state file found: {filepath}")
            return None
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded world state from {filepath}")
        return WorldState.from_dict(data)
    
    def _get_latest_json_state(self, world_id: str) -> Optional[WorldState]:
        """Get most recent JSON state for world"""
        pattern = f"{world_id}_*.json"
        matching_files = list(self.storage_path.glob(pattern))
        
        if not matching_files:
            return None
        
        # Sort by date in filename
        latest_file = max(matching_files, key=lambda f: f.stem.split('_')[-1])
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        return WorldState.from_dict(data)
    
    def _list_json_dates(self, world_id: str) -> List[date]:
        """List available dates from JSON files"""
        pattern = f"{world_id}_*.json"
        matching_files = list(self.storage_path.glob(pattern))
        
        dates = []
        for file in matching_files:
            try:
                date_str = file.stem.split('_')[-1]
                dates.append(date.fromisoformat(date_str))
            except ValueError:
                continue
        
        return sorted(dates)


class BusinessCalendarSystem:
    """
    Calendar system for scheduled events and meetings.
    Integrates with BusinessTimeManager for date-aware simulation.
    """
    
    def __init__(self):
        self.scheduled_events: Dict[date, List[Dict[str, Any]]] = {}
        self.recurring_events: List[Dict[str, Any]] = []
        
    def schedule_event(self, event_date: date, event_data: Dict[str, Any]):
        """Schedule an event for a specific date"""
        if event_date not in self.scheduled_events:
            self.scheduled_events[event_date] = []
        
        event_data["event_id"] = event_data.get("event_id", str(uuid.uuid4()))
        self.scheduled_events[event_date].append(event_data)
        
        logger.info(f"Scheduled event for {event_date}: {event_data.get('title', 'Untitled')}")
    
    def schedule_recurring_event(self, event_data: Dict[str, Any]):
        """Schedule a recurring event"""
        event_data["event_id"] = event_data.get("event_id", str(uuid.uuid4()))
        self.recurring_events.append(event_data)
        
        logger.info(f"Scheduled recurring event: {event_data.get('title', 'Untitled')}")
    
    def get_events_for_date(self, event_date: date) -> List[Dict[str, Any]]:
        """Get all events (one-time and recurring) for a specific date"""
        events = self.scheduled_events.get(event_date, []).copy()
        
        # Add recurring events that match this date
        for recurring_event in self.recurring_events:
            if self._event_matches_date(recurring_event, event_date):
                events.append(recurring_event.copy())
        
        return events
    
    def _event_matches_date(self, recurring_event: Dict[str, Any], check_date: date) -> bool:
        """Check if recurring event should occur on given date"""
        recurrence = recurring_event.get("recurrence", {})
        recurrence_type = recurrence.get("type", "")
        
        if recurrence_type == "daily":
            return True
        elif recurrence_type == "weekly":
            target_weekday = recurrence.get("weekday", check_date.weekday())
            return check_date.weekday() == target_weekday
        elif recurrence_type == "monthly":
            target_day = recurrence.get("day_of_month", check_date.day)
            return check_date.day == target_day
        
        return False
    
    def save_calendar_state(self) -> Dict[str, Any]:
        """Save calendar state for persistence"""
        return {
            "scheduled_events": {
                date_str: events for date_str, events in 
                [(d.isoformat(), evts) for d, evts in self.scheduled_events.items()]
            },
            "recurring_events": self.recurring_events
        }
    
    def load_calendar_state(self, state_data: Dict[str, Any]):
        """Load calendar state from saved data"""
        # Load one-time events
        self.scheduled_events = {}
        for date_str, events in state_data.get("scheduled_events", {}).items():
            event_date = date.fromisoformat(date_str)
            self.scheduled_events[event_date] = events
        
        # Load recurring events
        self.recurring_events = state_data.get("recurring_events", [])
        
        logger.info("Loaded calendar state")


class PersistentWorldManager:
    """
    Central coordinator for persistent multi-day business simulations.
    
    Manages the complete lifecycle of simulation days including state loading,
    calendar integration, world initialization, and state persistence.
    """
    
    def __init__(self, world_id: str, world_type: WorldType = WorldType.BUSINESS,
                 storage_backend: StorageBackend = StorageBackend.JSON_FILES,
                 storage_path: str = "simulation_states"):
        """
        Initialize PersistentWorldManager.
        
        Args:
            world_id: Unique identifier for this world
            world_type: Type of world being managed
            storage_backend: Storage system to use
            storage_path: Path for state storage
        """
        self.world_id = world_id
        self.world_type = world_type
        
        # Core systems
        self.state_storage = StateStorage(storage_backend, storage_path)
        self.calendar_system = BusinessCalendarSystem()
        self.time_manager: Optional[BusinessTimeManager] = None
        
        # Current simulation state
        self.current_world: Optional[BusinessSimulationWorld] = None
        self.current_simulation_day: Optional[SimulationDay] = None
        
        logger.info(f"Initialized PersistentWorldManager for world '{world_id}' ({world_type.value})")
    
    async def prepare_simulation_day(self, target_date: date) -> SimulationDay:
        """
        Prepare a complete simulation day with state and scheduled events.
        
        This is the main entry point for loading a simulation day.
        """
        logger.info(f"Preparing simulation day for {target_date}")
        
        # 1. Initialize or load time manager
        if not self.time_manager:
            # Check for timezone configuration from world factory
            timezone = getattr(self, '_pending_timezone_config', None)
            if timezone:
                self.time_manager = BusinessTimeManager(start_date=target_date, timezone=timezone)
            else:
                self.time_manager = BusinessTimeManager(start_date=target_date)
        else:
            self.time_manager.set_virtual_date(target_date)
        
        # 2. Get business day information
        business_day = self.time_manager.get_current_business_day()
        
        # 3. Load previous state or create initial state
        previous_state = await self._load_previous_state(target_date)
        
        # 4. Get scheduled events for this date
        scheduled_events = self.calendar_system.get_events_for_date(target_date)
        
        # 5. Create simulation day
        simulation_day = SimulationDay(
            virtual_date=target_date,
            business_day=business_day,
            scheduled_events=scheduled_events,
            previous_state=previous_state
        )
        
        self.current_simulation_day = simulation_day
        
        logger.info(f"Prepared simulation day: {target_date} ({business_day.day_type.value}), "
                   f"{len(scheduled_events)} events, "
                   f"{'with' if previous_state else 'without'} previous state")
        
        return simulation_day
    
    async def initialize_world(self, simulation_day: SimulationDay) -> BusinessSimulationWorld:
        """
        Initialize business world with state and scheduled events.
        """
        logger.info(f"Initializing world for {simulation_day.virtual_date}")
        
        # Create new world instance
        world = BusinessSimulationWorld(
            name=f"{self.world_id}_{simulation_day.virtual_date}",
            enable_ceo_interrupt=True
        )
        
        # Initialize with time manager
        world.time_manager = self.time_manager
        
        # Load previous state if available
        if simulation_day.previous_state:
            await self._restore_world_state(world, simulation_day.previous_state)
        else:
            await self._initialize_new_world(world)
        
        # Inject scheduled events
        await self._inject_scheduled_events(world, simulation_day.scheduled_events)
        
        # Store reference
        self.current_world = world
        simulation_day.world_instance = world
        
        logger.info(f"World initialized with {len(world.agents)} agents and {len(simulation_day.scheduled_events)} events")
        
        return world
    
    async def save_simulation_day(self, simulation_day: SimulationDay) -> bool:
        """
        Save complete simulation day state for future loading.
        """
        if not simulation_day.world_instance:
            logger.error("No world instance to save")
            return False
        
        logger.info(f"Saving simulation day state for {simulation_day.virtual_date}")
        
        # Collect state from all components
        world_state = WorldState(
            world_id=self.world_id,
            world_type=self.world_type,
            simulation_date=simulation_day.virtual_date,
            time_manager_state=self.time_manager.save_state(),
            task_manager_state=await self._extract_task_manager_state(simulation_day.world_instance),
            hiring_database_state=await self._extract_hiring_database_state(simulation_day.world_instance),
            business_metrics=await self._extract_business_metrics(simulation_day.world_instance),
            world_specific_state=await self._extract_world_specific_state(simulation_day.world_instance)
        )
        
        # Save to storage
        success = self.state_storage.save_world_state(world_state)
        
        if success:
            logger.info(f"Successfully saved simulation day state for {simulation_day.virtual_date}")
        else:
            logger.error(f"Failed to save simulation day state for {simulation_day.virtual_date}")
        
        return success
    
    async def run_simulation_day(self, target_date: date, rounds: int = 5) -> Dict[str, Any]:
        """
        Complete workflow: prepare, initialize, run, and save simulation day.
        """
        logger.info(f"Running complete simulation day for {target_date}")
        
        try:
            # 1. Prepare simulation day
            simulation_day = await self.prepare_simulation_day(target_date)
            
            # 2. Initialize world
            world = await self.initialize_world(simulation_day)
            
            # 3. Run simulation
            await world.async_run(rounds)
            
            # 4. Save state
            save_success = await self.save_simulation_day(simulation_day)
            
            # 5. Get analytics
            analytics = world.get_business_analytics()
            analytics["simulation_date"] = target_date.isoformat()
            analytics["state_saved"] = save_success
            
            logger.info(f"Completed simulation day for {target_date}")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to run simulation day for {target_date}: {e}")
            raise
    
    def schedule_event(self, event_date: date, event_data: Dict[str, Any]):
        """Schedule an event in the calendar system"""
        self.calendar_system.schedule_event(event_date, event_data)
    
    def schedule_recurring_event(self, event_data: Dict[str, Any]):
        """Schedule a recurring event"""
        self.calendar_system.schedule_recurring_event(event_data)
    
    def get_world_history(self) -> List[date]:
        """Get all available simulation dates for this world"""
        return self.state_storage.list_available_dates(self.world_id)
    
    async def _load_previous_state(self, target_date: date) -> Optional[WorldState]:
        """Load the most recent state before target date"""
        available_dates = self.get_world_history()
        
        # Find most recent date before target
        previous_dates = [d for d in available_dates if d < target_date]
        
        if not previous_dates:
            logger.info(f"No previous state found before {target_date}")
            return None
        
        latest_previous_date = max(previous_dates)
        previous_state = self.state_storage.load_world_state(self.world_id, latest_previous_date)
        
        if previous_state:
            logger.info(f"Loaded previous state from {latest_previous_date}")
        else:
            logger.warning(f"Failed to load previous state from {latest_previous_date}")
        
        return previous_state
    
    # _restore_world_state method implemented later with enhanced functionality
    
    async def _initialize_new_world(self, world: BusinessSimulationWorld):
        """Initialize a new world with default state"""
        logger.info("Initializing new world with default state")
        
        # Set up basic business metrics
        world.business_metrics = {
            "simulation_start_date": self.time_manager.current_virtual_date.isoformat(),
            "total_simulation_days": 0,
            "productivity_score": 0.0,
            "collaboration_events": 0,
            "decisions_made": 0,
            "meetings_completed": 0
        }
    
    async def _inject_scheduled_events(self, world: BusinessSimulationWorld, events: List[Dict[str, Any]]):
        """Inject scheduled events into the world simulation"""
        logger.info(f"Injecting {len(events)} scheduled events")
        
        for event in events:
            event_type = event.get("type", "generic")
            
            if event_type == "meeting":
                await self._inject_meeting_event(world, event)
            elif event_type == "deadline":
                await self._inject_deadline_event(world, event)
            elif event_type == "announcement":
                await self._inject_announcement_event(world, event)
            else:
                logger.debug(f"Unknown event type: {event_type}")
    
    async def _inject_meeting_event(self, world: BusinessSimulationWorld, event: Dict[str, Any]):
        """Inject a meeting event into the simulation"""
        meeting_title = event.get("title", "Scheduled Meeting")
        attendees = event.get("attendees", [])
        
        # Add meeting to world's daily activities
        world.business_metrics["meetings_completed"] += 1
        
        logger.debug(f"Injected meeting: {meeting_title} with {len(attendees)} attendees")
    
    async def _inject_deadline_event(self, world: BusinessSimulationWorld, event: Dict[str, Any]):
        """Inject a deadline event"""
        deadline_title = event.get("title", "Deadline")
        priority = event.get("priority", "medium")
        
        logger.debug(f"Injected deadline: {deadline_title} (priority: {priority})")
    
    async def _inject_announcement_event(self, world: BusinessSimulationWorld, event: Dict[str, Any]):
        """Inject an announcement event"""
        announcement = event.get("title", "Company Announcement")
        
        logger.debug(f"Injected announcement: {announcement}")
    
    async def _extract_task_manager_state(self, world: BusinessSimulationWorld) -> Dict[str, Any]:
        """Extract task manager state from world"""
        # TODO: Implement when task manager is integrated with world
        return {"tasks": [], "metrics": {}}
    
    async def _extract_hiring_database_state(self, world: BusinessSimulationWorld) -> Dict[str, Any]:
        """Extract hiring database state from world"""
        if not hasattr(world, 'hiring_database'):
            return {}
        
        hiring_db = world.hiring_database
        
        # Extract employee data
        employees_data = {}
        for emp_id, employee in hiring_db.employees.items():
            employees_data[emp_id] = {
                "name": employee.name,
                "employee_id": employee.employee_id,
                "role": employee.role,
                "department": employee.department,
                "manager_id": employee.manager_id,
                "direct_reports": employee.direct_reports,
                "business_skills": employee.business_skills,
                "performance_rating": employee.performance_rating,
                "hire_date": employee.hire_date.isoformat() if employee.hire_date and hasattr(employee.hire_date, 'isoformat') else None
            }
        
        # Extract metrics
        metrics = {
            "total_employees": len(hiring_db.employees),
            "departments": list(set(emp.department for emp in hiring_db.employees.values())),
            "roles": list(set(emp.role for emp in hiring_db.employees.values())),
            "hiring_events": len(hiring_db.hiring_events)
        }
        
        return {
            "employees": employees_data,
            "metrics": metrics,
            "organizational_chart": {k: list(v) for k, v in hiring_db.organizational_chart.items()} if hasattr(hiring_db, 'organizational_chart') else {}
        }
    
    async def _extract_business_metrics(self, world: BusinessSimulationWorld) -> Dict[str, Any]:
        """Extract business metrics from world"""
        return getattr(world, 'business_metrics', {})
    
    async def _extract_world_specific_state(self, world: BusinessSimulationWorld) -> Dict[str, Any]:
        """Extract world-type specific state including agent states"""
        
        # Extract agent states for persistence
        agent_states = {}
        for agent in world.agents:
            if hasattr(agent, 'employee_id'):  # Business employee
                agent_states[agent.employee_id] = await self._extract_agent_state(agent)
            else:  # Regular agent
                agent_states[agent.name] = await self._extract_agent_state(agent)
        
        # Extract world-specific business data
        world_data = {
            "agent_states": agent_states,
            "active_agent_count": len(world.agents),
            "world_type": "business",
            "business_hours_start": world.business_hours_start.isoformat() if hasattr(world, 'business_hours_start') else "09:00",
            "business_hours_end": world.business_hours_end.isoformat() if hasattr(world, 'business_hours_end') else "17:00"
        }
        
        return world_data
    
    async def _extract_agent_state(self, agent) -> Dict[str, Any]:
        """Extract comprehensive agent state for persistence"""
        
        # Base agent state
        agent_state = {
            "name": agent.name,
            "agent_type": type(agent).__name__
        }
        
        # Extract memory states if available
        if hasattr(agent, 'episodic_memory') and agent.episodic_memory:
            agent_state["episodic_memory"] = self._serialize_memory(agent.episodic_memory)
        
        if hasattr(agent, 'semantic_memory') and agent.semantic_memory:
            agent_state["semantic_memory"] = self._serialize_memory(agent.semantic_memory)
        
        # Extract persona and mental state
        if hasattr(agent, '_persona'):
            agent_state["persona"] = agent._persona
        
        if hasattr(agent, '_mental_state'):
            agent_state["mental_state"] = agent._mental_state
        
        # Business-specific attributes for AsyncBusinessEmployee
        if hasattr(agent, 'employee_id'):
            agent_state.update({
                "employee_id": agent.employee_id,
                "role": agent.role,
                "department": agent.department,
                "manager_id": agent.manager_id,
                "direct_reports": agent.direct_reports,
                "business_skills": agent.business_skills,
                "performance_rating": agent.performance_rating,
                "hire_date": agent.hire_date.isoformat() if agent.hire_date and hasattr(agent.hire_date, 'isoformat') else None
            })
        
        return agent_state
    
    def _serialize_memory(self, memory) -> Dict[str, Any]:
        """Serialize memory object for storage"""
        try:
            if hasattr(memory, 'to_json'):
                return memory.to_json()
            elif hasattr(memory, '__dict__'):
                # Simple serialization of memory attributes
                memory_data = {}
                for key, value in memory.__dict__.items():
                    if not key.startswith('_'):  # Skip private attributes
                        if isinstance(value, (str, int, float, bool, list, dict)):
                            memory_data[key] = value
                        else:
                            memory_data[key] = str(value)
                return memory_data
            else:
                return {"serialized": str(memory)}
        except Exception as e:
            logger.warning(f"Failed to serialize memory: {e}")
            return {"error": f"Serialization failed: {e}"}
    
    async def _restore_hiring_database(self, hiring_db, state_data: Dict[str, Any]):
        """Restore hiring database from state"""
        if not state_data or "employees" not in state_data:
            return
        
        from tinytroupe.business_employee import AsyncBusinessEmployee
        from tinytroupe.agent.tiny_person import TinyPerson
        from datetime import datetime
        
        # Clear existing employees
        hiring_db.employees.clear()
        
        # Clear TinyPerson registry to avoid name conflicts during restoration
        original_all_agents = TinyPerson.all_agents.copy()
        TinyPerson.all_agents.clear()
        
        try:
            # Restore employees
            for emp_id, emp_data in state_data["employees"].items():
                try:
                    # Create business employee
                    employee = AsyncBusinessEmployee(
                        name=emp_data["name"],
                        employee_id=emp_data["employee_id"],
                        role=emp_data["role"],
                        department=emp_data["department"],
                        manager_id=emp_data.get("manager_id")
                    )
                    
                    # Restore business attributes
                    employee.direct_reports = emp_data.get("direct_reports", [])
                    employee.business_skills = emp_data.get("business_skills", {})
                    employee.performance_rating = emp_data.get("performance_rating", "Not Rated")
                    
                    # Restore hire date
                    if emp_data.get("hire_date"):
                        employee.hire_date = datetime.fromisoformat(emp_data["hire_date"]).date()
                    
                    # Add to hiring database
                    hiring_db.employees[emp_id] = employee
                    
                except Exception as e:
                    logger.warning(f"Failed to restore employee {emp_id}: {e}")
        
        finally:
            # Restore original agent registry (keeping the new employees)
            # This preserves any existing agents while allowing the restored ones
            for agent_name, agent in original_all_agents.items():
                # Only add back agents that don't conflict with restored ones
                if agent_name not in [emp.name for emp in hiring_db.employees.values()]:
                    TinyPerson.all_agents[agent_name] = agent
        
        logger.info(f"Restored {len(hiring_db.employees)} employees to hiring database")
    
    async def _restore_world_state(self, world: BusinessSimulationWorld, world_state: WorldState):
        """Restore world from saved state with enhanced agent restoration"""
        logger.info("Restoring world from previous state with full agent states")
        
        # Restore time manager
        self.time_manager.load_state(world_state.time_manager_state)
        
        # Restore hiring database
        if hasattr(world, 'hiring_database'):
            await self._restore_hiring_database(world.hiring_database, world_state.hiring_database_state)
        
        # Restore business metrics
        if hasattr(world, 'business_metrics'):
            world.business_metrics.update(world_state.business_metrics)
        
        # Restore agent states
        await self._restore_agent_states(world, world_state.world_specific_state)
    
    async def _restore_agent_states(self, world: BusinessSimulationWorld, world_specific_state: Dict[str, Any]):
        """Restore agent states from saved data and add them to world.agents"""
        if "agent_states" not in world_specific_state:
            logger.warning("No agent_states found in world_specific_state")
            return
        
        agent_states = world_specific_state["agent_states"]
        logger.info(f"Found {len(agent_states)} agent states to restore: {list(agent_states.keys())}")
        
        if hasattr(world, 'hiring_database'):
            logger.info(f"Hiring database has {len(world.hiring_database.employees)} employees: {list(world.hiring_database.employees.keys())}")
        
        restored_agents = []
        
        for agent_id, agent_state in agent_states.items():
            try:
                agent = None
                logger.info(f"Restoring agent {agent_id} of type {agent_state.get('agent_type')}")
                
                # For business employees, look them up in the hiring database first
                if agent_state.get("agent_type") == "AsyncBusinessEmployee":
                    employee_id = agent_state.get("employee_id")
                    logger.info(f"Looking for employee_id {employee_id} in hiring database")
                    
                    if employee_id and hasattr(world, 'hiring_database') and employee_id in world.hiring_database.employees:
                        # Use the employee already created by hiring database restoration
                        agent = world.hiring_database.employees[employee_id]
                        logger.info(f"Found employee {employee_id} in hiring database: {agent.name}")
                        
                        # Restore agent-specific state (memories, persona, mental state)
                        await self._restore_agent_memories(agent, agent_state)
                        
                        if "persona" in agent_state:
                            agent._persona = agent_state["persona"]
                        
                        if "mental_state" in agent_state:
                            agent._mental_state = agent_state["mental_state"]
                    else:
                        logger.warning(f"Employee {employee_id} not found in hiring database, creating new one")
                        # Fallback: create new business employee
                        agent = await self._restore_business_employee(agent_state)
                else:
                    # Regular agent
                    agent = await self._restore_regular_agent(agent_state)
                
                if agent:
                    world.agents.append(agent)
                    restored_agents.append(agent.name)
                    logger.info(f"Successfully restored agent {agent.name} to world.agents")
                else:
                    logger.warning(f"Failed to create agent for {agent_id}")
                    
            except Exception as e:
                logger.warning(f"Failed to restore agent {agent_id}: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info(f"Restored {len(restored_agents)} agents to world.agents: {restored_agents}")
    
    async def _restore_business_employee(self, agent_state: Dict[str, Any]):
        """Restore a business employee from state"""
        from tinytroupe.business_employee import AsyncBusinessEmployee
        from datetime import datetime
        
        # Create business employee
        employee = AsyncBusinessEmployee(
            name=agent_state["name"],
            employee_id=agent_state["employee_id"],
            role=agent_state["role"],
            department=agent_state["department"],
            manager_id=agent_state.get("manager_id")
        )
        
        # Restore business attributes
        employee.direct_reports = agent_state.get("direct_reports", [])
        employee.business_skills = agent_state.get("business_skills", {})
        employee.performance_rating = agent_state.get("performance_rating", "Not Rated")
        
        if agent_state.get("hire_date"):
            employee.hire_date = datetime.fromisoformat(agent_state["hire_date"]).date()
        
        # Restore persona and mental state
        if "persona" in agent_state:
            employee._persona = agent_state["persona"]
        
        if "mental_state" in agent_state:
            employee._mental_state = agent_state["mental_state"]
        
        # Restore memories
        await self._restore_agent_memories(employee, agent_state)
        
        return employee
    
    async def _restore_regular_agent(self, agent_state: Dict[str, Any]):
        """Restore a regular TinyPerson agent from state"""
        # This would require importing and creating appropriate agent types
        # For now, return None to skip regular agents in business context
        logger.debug(f"Skipping restoration of regular agent: {agent_state.get('name')}")
        return None
    
    async def _restore_agent_memories(self, agent, agent_state: Dict[str, Any]):
        """Restore agent memory states"""
        try:
            # Restore episodic memory
            if "episodic_memory" in agent_state and hasattr(agent, 'episodic_memory'):
                await self._restore_memory(agent.episodic_memory, agent_state["episodic_memory"])
            
            # Restore semantic memory
            if "semantic_memory" in agent_state and hasattr(agent, 'semantic_memory'):
                await self._restore_memory(agent.semantic_memory, agent_state["semantic_memory"])
                
        except Exception as e:
            logger.warning(f"Failed to restore memories for {agent.name}: {e}")
    
    async def _restore_memory(self, memory_obj, memory_data: Dict[str, Any]):
        """Restore a memory object from serialized data"""
        if not memory_data or "error" in memory_data:
            return
        
        try:
            if hasattr(memory_obj, 'from_json') and "serialized" not in memory_data:
                memory_obj.from_json(memory_data)
            else:
                # Simple attribute restoration
                for key, value in memory_data.items():
                    if hasattr(memory_obj, key):
                        setattr(memory_obj, key, value)
                        
        except Exception as e:
            logger.warning(f"Failed to restore memory object: {e}")


# Convenience factory functions
def create_business_world_manager(world_id: str, storage_path: str = "business_simulations") -> PersistentWorldManager:
    """Create a business world manager with standard settings"""
    return PersistentWorldManager(
        world_id=world_id,
        world_type=WorldType.BUSINESS,
        storage_backend=StorageBackend.JSON_FILES,
        storage_path=storage_path
    )


def create_research_world_manager(world_id: str, storage_path: str = "research_simulations") -> PersistentWorldManager:
    """Create a research world manager"""
    return PersistentWorldManager(
        world_id=world_id,
        world_type=WorldType.RESEARCH,
        storage_backend=StorageBackend.JSON_FILES,
        storage_path=storage_path
    )