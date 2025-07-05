"""
BusinessWorldFactory - Modular World Creation System

This module provides a factory pattern for creating different types of simulation worlds,
enabling support for business, research, hospital, education, and custom simulations.
Each world type has specialized configurations, agent roles, and behaviors.
"""

import asyncio
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from tinytroupe.persistent_world_manager import (
    PersistentWorldManager, WorldType, StorageBackend, WorldState, SimulationDay
)
from tinytroupe.business_time_manager import BusinessTimeManager, TimeZone
from tinytroupe.business_world import BusinessSimulationWorld
from tinytroupe.business_simulation import HiringDatabase
from tinytroupe.business_employee import AsyncBusinessEmployee
from tinytroupe.task_management import TaskManager, BusinessTask, TaskPriority, TaskComplexity
from tinytroupe.task_assignment import TaskAssignmentEngine

logger = logging.getLogger("tinytroupe.world_factory")


@dataclass
class WorldConfiguration:
    """Configuration template for a specific world type"""
    world_type: WorldType
    name: str
    description: str
    
    # Core settings
    default_timezone: TimeZone = TimeZone.PST
    business_hours_start: str = "09:00"
    business_hours_end: str = "17:00"
    max_employee_workload: float = 40.0
    
    # Agent and role configuration
    agent_roles: List[Dict[str, Any]] = field(default_factory=list)
    department_structure: Dict[str, List[str]] = field(default_factory=dict)
    required_skills: List[str] = field(default_factory=list)
    
    # Simulation behavior
    meeting_frequency: str = "daily"  # daily, weekly, monthly
    task_complexity_bias: TaskComplexity = TaskComplexity.MODERATE
    collaboration_intensity: str = "medium"  # low, medium, high
    
    # World-specific settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Initialization hooks
    setup_callbacks: List[Callable] = field(default_factory=list)


class BusinessWorldFactory:
    """
    Factory for creating different types of simulation worlds with specialized configurations.
    
    Supports modular world creation enabling users to run business simulations,
    research projects, hospital operations, educational institutions, and custom scenarios.
    """
    
    def __init__(self):
        self.world_configurations: Dict[WorldType, WorldConfiguration] = {}
        self.custom_configurations: Dict[str, WorldConfiguration] = {}
        
        # Initialize default configurations
        self._load_default_configurations()
        
        logger.info("Initialized BusinessWorldFactory with default configurations")
    
    def create_world(self, world_type: WorldType, world_id: str,
                    custom_config: Optional[Dict[str, Any]] = None,
                    storage_path: str = None) -> PersistentWorldManager:
        """
        Create a new simulation world of the specified type.
        
        Args:
            world_type: Type of world to create
            world_id: Unique identifier for the world
            custom_config: Optional configuration overrides
            storage_path: Custom storage path for this world
            
        Returns:
            Configured PersistentWorldManager ready for simulation
        """
        logger.info(f"Creating {world_type.value} world: {world_id}")
        
        # Get base configuration
        config = self.get_world_configuration(world_type)
        
        # Apply custom configuration if provided
        if custom_config:
            config = self._merge_configurations(config, custom_config)
        
        # Determine storage path
        if not storage_path:
            storage_path = f"{world_type.value}_simulations"
        
        # Create PersistentWorldManager
        world_manager = PersistentWorldManager(
            world_id=world_id,
            world_type=world_type,
            storage_backend=StorageBackend.JSON_FILES,
            storage_path=storage_path
        )
        
        # Apply world-specific configuration
        self._configure_world_manager(world_manager, config)
        
        # Run setup callbacks
        for callback in config.setup_callbacks:
            try:
                callback(world_manager, config)
            except Exception as e:
                logger.warning(f"Setup callback failed: {e}")
        
        logger.info(f"Created {world_type.value} world '{world_id}' with configuration: {config.name}")
        
        return world_manager
    
    def create_business_world(self, world_id: str, **kwargs) -> PersistentWorldManager:
        """Create a business simulation world with standard corporate settings"""
        return self.create_world(WorldType.BUSINESS, world_id, **kwargs)
    
    def create_research_world(self, world_id: str, **kwargs) -> PersistentWorldManager:
        """Create a research institution world focused on scientific collaboration"""
        return self.create_world(WorldType.RESEARCH, world_id, **kwargs)
    
    def create_hospital_world(self, world_id: str, **kwargs) -> PersistentWorldManager:
        """Create a hospital simulation world with medical roles and protocols"""
        return self.create_world(WorldType.HOSPITAL, world_id, **kwargs)
    
    def create_education_world(self, world_id: str, **kwargs) -> PersistentWorldManager:
        """Create an educational institution world with academic roles"""
        return self.create_world(WorldType.EDUCATION, world_id, **kwargs)
    
    def create_custom_world(self, world_id: str, custom_type_name: str,
                          configuration: Dict[str, Any]) -> PersistentWorldManager:
        """Create a custom world type with user-defined configuration"""
        
        # Prepare configuration without conflicting keys
        config_copy = configuration.copy()
        config_copy.pop('name', None)  # Remove name if present to avoid conflict
        config_copy.pop('description', None)  # Remove description if present to avoid conflict
        
        # Register custom configuration
        custom_config = WorldConfiguration(
            world_type=WorldType.CUSTOM,
            name=configuration.get("name", custom_type_name),
            description=configuration.get("description", f"Custom {custom_type_name} simulation"),
            **config_copy
        )
        
        self.custom_configurations[custom_type_name] = custom_config
        
        # Create world directly since CUSTOM type doesn't have base configuration
        storage_path = f"custom_{custom_type_name}_simulations"
        
        # Create PersistentWorldManager
        world_manager = PersistentWorldManager(
            world_id=world_id,
            world_type=WorldType.CUSTOM,
            storage_backend=StorageBackend.JSON_FILES,
            storage_path=storage_path
        )
        
        # Apply custom configuration
        self._configure_world_manager(world_manager, custom_config)
        
        # Run setup callbacks
        for callback in custom_config.setup_callbacks:
            try:
                callback(world_manager, custom_config)
            except Exception as e:
                logger.warning(f"Setup callback failed: {e}")
        
        logger.info(f"Created custom world '{world_id}' of type '{custom_type_name}'")
        
        return world_manager
    
    def get_world_configuration(self, world_type: WorldType) -> WorldConfiguration:
        """Get the configuration for a specific world type"""
        if world_type not in self.world_configurations:
            raise ValueError(f"Unknown world type: {world_type}")
        
        return self.world_configurations[world_type]
    
    def list_available_world_types(self) -> Dict[str, str]:
        """List all available world types with descriptions"""
        world_types = {}
        
        for world_type, config in self.world_configurations.items():
            world_types[world_type.value] = config.description
        
        for custom_name, config in self.custom_configurations.items():
            world_types[f"custom_{custom_name}"] = config.description
        
        return world_types
    
    def _load_default_configurations(self):
        """Load default configurations for each world type"""
        
        # Business World Configuration
        business_config = WorldConfiguration(
            world_type=WorldType.BUSINESS,
            name="Corporate Business Simulation",
            description="Standard business environment with departments, projects, and corporate hierarchy",
            agent_roles=[
                {"role": "CEO", "department": "Executive", "authority_level": 10},
                {"role": "VP Engineering", "department": "Engineering", "authority_level": 8},
                {"role": "VP Marketing", "department": "Marketing", "authority_level": 8},
                {"role": "Project Manager", "department": "Engineering", "authority_level": 6},
                {"role": "Senior Engineer", "department": "Engineering", "authority_level": 5},
                {"role": "Marketing Manager", "department": "Marketing", "authority_level": 6},
                {"role": "Sales Representative", "department": "Sales", "authority_level": 4},
                {"role": "Junior Developer", "department": "Engineering", "authority_level": 3}
            ],
            department_structure={
                "Executive": ["CEO", "VP Engineering", "VP Marketing"],
                "Engineering": ["VP Engineering", "Project Manager", "Senior Engineer", "Junior Developer"],
                "Marketing": ["VP Marketing", "Marketing Manager"],
                "Sales": ["Sales Representative"]
            },
            required_skills=["communication", "project_management", "technical_skills", "leadership"],
            meeting_frequency="daily",
            collaboration_intensity="high",
            custom_settings={
                "quarterly_reviews": True,
                "sprint_planning": True,
                "product_development": True
            }
        )
        
        # Research World Configuration
        research_config = WorldConfiguration(
            world_type=WorldType.RESEARCH,
            name="Research Institution Simulation",
            description="Academic research environment with labs, publications, and scientific collaboration",
            default_timezone=TimeZone.EST,
            business_hours_start="08:00",
            business_hours_end="18:00",
            agent_roles=[
                {"role": "Research Director", "department": "Administration", "authority_level": 10},
                {"role": "Principal Investigator", "department": "Research", "authority_level": 8},
                {"role": "Senior Researcher", "department": "Research", "authority_level": 6},
                {"role": "Research Scientist", "department": "Research", "authority_level": 5},
                {"role": "PhD Student", "department": "Research", "authority_level": 3},
                {"role": "Lab Technician", "department": "Support", "authority_level": 4},
                {"role": "Grant Coordinator", "department": "Administration", "authority_level": 5}
            ],
            department_structure={
                "Administration": ["Research Director", "Grant Coordinator"],
                "Research": ["Principal Investigator", "Senior Researcher", "Research Scientist", "PhD Student"],
                "Support": ["Lab Technician"]
            },
            required_skills=["research_methodology", "data_analysis", "scientific_writing", "collaboration"],
            meeting_frequency="weekly",
            task_complexity_bias=TaskComplexity.COMPLEX,
            collaboration_intensity="medium",
            custom_settings={
                "publication_cycles": True,
                "grant_applications": True,
                "peer_review": True,
                "conference_presentations": True
            }
        )
        
        # Hospital World Configuration
        hospital_config = WorldConfiguration(
            world_type=WorldType.HOSPITAL,
            name="Hospital Operations Simulation",
            description="Healthcare facility with medical staff, patients, and clinical protocols",
            business_hours_start="00:00",  # 24/7 operation
            business_hours_end="23:59",
            max_employee_workload=60.0,  # Healthcare often has longer shifts
            agent_roles=[
                {"role": "Chief of Medicine", "department": "Administration", "authority_level": 10},
                {"role": "Department Head", "department": "Clinical", "authority_level": 8},
                {"role": "Attending Physician", "department": "Clinical", "authority_level": 7},
                {"role": "Resident", "department": "Clinical", "authority_level": 5},
                {"role": "Nurse Manager", "department": "Nursing", "authority_level": 6},
                {"role": "Registered Nurse", "department": "Nursing", "authority_level": 4},
                {"role": "Medical Technician", "department": "Support", "authority_level": 3}
            ],
            department_structure={
                "Administration": ["Chief of Medicine"],
                "Clinical": ["Department Head", "Attending Physician", "Resident"],
                "Nursing": ["Nurse Manager", "Registered Nurse"],
                "Support": ["Medical Technician"]
            },
            required_skills=["medical_knowledge", "patient_care", "emergency_response", "teamwork"],
            meeting_frequency="daily",
            task_complexity_bias=TaskComplexity.EXPERT,
            collaboration_intensity="high",
            custom_settings={
                "shift_schedules": True,
                "patient_rounds": True,
                "emergency_protocols": True,
                "quality_reviews": True
            }
        )
        
        # Education World Configuration
        education_config = WorldConfiguration(
            world_type=WorldType.EDUCATION,
            name="Educational Institution Simulation",
            description="School or university environment with faculty, students, and academic programs",
            business_hours_start="08:00",
            business_hours_end="16:00",
            agent_roles=[
                {"role": "Principal/Dean", "department": "Administration", "authority_level": 10},
                {"role": "Department Chair", "department": "Academic", "authority_level": 8},
                {"role": "Professor", "department": "Academic", "authority_level": 7},
                {"role": "Assistant Professor", "department": "Academic", "authority_level": 5},
                {"role": "Teaching Assistant", "department": "Academic", "authority_level": 3},
                {"role": "Academic Coordinator", "department": "Administration", "authority_level": 5},
                {"role": "Support Staff", "department": "Support", "authority_level": 3}
            ],
            department_structure={
                "Administration": ["Principal/Dean", "Academic Coordinator"],
                "Academic": ["Department Chair", "Professor", "Assistant Professor", "Teaching Assistant"],
                "Support": ["Support Staff"]
            },
            required_skills=["teaching", "curriculum_development", "student_assessment", "academic_research"],
            meeting_frequency="weekly",
            task_complexity_bias=TaskComplexity.MODERATE,
            collaboration_intensity="medium",
            custom_settings={
                "semester_planning": True,
                "curriculum_review": True,
                "student_assessments": True,
                "faculty_meetings": True
            }
        )
        
        # Store configurations
        self.world_configurations = {
            WorldType.BUSINESS: business_config,
            WorldType.RESEARCH: research_config,
            WorldType.HOSPITAL: hospital_config,
            WorldType.EDUCATION: education_config
        }
    
    def _merge_configurations(self, base_config: WorldConfiguration, 
                            custom_config: Dict[str, Any]) -> WorldConfiguration:
        """Merge custom configuration with base configuration"""
        
        # Create a copy of base config
        merged_config = WorldConfiguration(
            world_type=base_config.world_type,
            name=custom_config.get("name", base_config.name),
            description=custom_config.get("description", base_config.description),
            default_timezone=custom_config.get("default_timezone", base_config.default_timezone),
            business_hours_start=custom_config.get("business_hours_start", base_config.business_hours_start),
            business_hours_end=custom_config.get("business_hours_end", base_config.business_hours_end),
            max_employee_workload=custom_config.get("max_employee_workload", base_config.max_employee_workload),
            agent_roles=custom_config.get("agent_roles", base_config.agent_roles.copy()),
            department_structure=custom_config.get("department_structure", base_config.department_structure.copy()),
            required_skills=custom_config.get("required_skills", base_config.required_skills.copy()),
            meeting_frequency=custom_config.get("meeting_frequency", base_config.meeting_frequency),
            task_complexity_bias=custom_config.get("task_complexity_bias", base_config.task_complexity_bias),
            collaboration_intensity=custom_config.get("collaboration_intensity", base_config.collaboration_intensity),
            custom_settings={**base_config.custom_settings, **custom_config.get("custom_settings", {})},
            setup_callbacks=custom_config.get("setup_callbacks", base_config.setup_callbacks.copy())
        )
        
        return merged_config
    
    def _configure_world_manager(self, world_manager: PersistentWorldManager, 
                               config: WorldConfiguration):
        """Apply configuration to a world manager"""
        
        # Note: Time manager will be created when prepare_simulation_day is called
        # Store configuration for later application
        world_manager._pending_timezone_config = config.default_timezone
        
        # Add recurring events based on meeting frequency
        if config.meeting_frequency == "daily":
            world_manager.schedule_recurring_event({
                "title": f"{config.name} Daily Standup",
                "type": "meeting",
                "duration": 30,
                "recurrence": {"type": "daily"}
            })
        elif config.meeting_frequency == "weekly":
            world_manager.schedule_recurring_event({
                "title": f"{config.name} Weekly Review",
                "type": "meeting", 
                "duration": 60,
                "recurrence": {"type": "weekly", "weekday": 1}  # Monday
            })
        
        # Store configuration in world manager metadata
        if not hasattr(world_manager, 'world_config'):
            world_manager.world_config = config
        
        logger.debug(f"Applied configuration to world manager: {config.name}")


# Convenience factory functions
def create_business_simulation(world_id: str, **kwargs) -> PersistentWorldManager:
    """Quick creation of business simulation world"""
    factory = BusinessWorldFactory()
    return factory.create_business_world(world_id, **kwargs)


def create_research_simulation(world_id: str, **kwargs) -> PersistentWorldManager:
    """Quick creation of research simulation world"""
    factory = BusinessWorldFactory()
    return factory.create_research_world(world_id, **kwargs)


def create_hospital_simulation(world_id: str, **kwargs) -> PersistentWorldManager:
    """Quick creation of hospital simulation world"""
    factory = BusinessWorldFactory()
    return factory.create_hospital_world(world_id, **kwargs)


def create_education_simulation(world_id: str, **kwargs) -> PersistentWorldManager:
    """Quick creation of education simulation world"""
    factory = BusinessWorldFactory()
    return factory.create_education_world(world_id, **kwargs)