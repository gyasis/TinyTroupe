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
    
    async def _restore_world_state(self, world: BusinessSimulationWorld, world_state: WorldState):
        """Restore world from saved state"""
        logger.info("Restoring world from previous state")
        
        # Restore time manager
        self.time_manager.load_state(world_state.time_manager_state)
        
        # Restore hiring database
        if hasattr(world, 'hiring_database'):
            await self._restore_hiring_database(world.hiring_database, world_state.hiring_database_state)
        
        # Restore task manager (TODO: implement when task manager is integrated)
        # if hasattr(world, 'task_manager'):
        #     await self._restore_task_manager(world.task_manager, world_state.task_manager_state)
        
        # Restore business metrics
        if hasattr(world, 'business_metrics'):
            world.business_metrics.update(world_state.business_metrics)
    
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
        if hasattr(world, 'hiring_database'):
            return {"employees": {}, "metrics": {}}  # TODO: Implement proper extraction
        return {}
    
    async def _extract_business_metrics(self, world: BusinessSimulationWorld) -> Dict[str, Any]:
        """Extract business metrics from world"""
        return getattr(world, 'business_metrics', {})
    
    async def _extract_world_specific_state(self, world: BusinessSimulationWorld) -> Dict[str, Any]:
        """Extract world-type specific state"""
        # Override in subclasses for different world types
        return {}
    
    async def _restore_hiring_database(self, hiring_db, state_data: Dict[str, Any]):
        """Restore hiring database from state"""
        # TODO: Implement proper restoration
        pass


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