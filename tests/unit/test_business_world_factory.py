"""
Comprehensive tests for BusinessWorldFactory

Tests the factory pattern for creating different types of simulation worlds
and validates world-specific configurations and behaviors.
"""

import pytest
import asyncio
import tempfile
import shutil
from datetime import date, datetime
from pathlib import Path

from tinytroupe.business_world_factory import (
    BusinessWorldFactory,
    WorldConfiguration,
    create_business_simulation,
    create_research_simulation,
    create_hospital_simulation,
    create_education_simulation
)
from tinytroupe.persistent_world_manager import WorldType, PersistentWorldManager
from tinytroupe.business_time_manager import TimeZone


class TestBusinessWorldFactory:
    """Test suite for BusinessWorldFactory"""
    
    @pytest.fixture
    def factory(self):
        """Create a factory instance for testing"""
        return BusinessWorldFactory()
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_factory_initialization(self, factory):
        """Test that factory initializes with default configurations"""
        assert factory is not None
        assert len(factory.world_configurations) == 4  # business, research, hospital, education
        assert WorldType.BUSINESS in factory.world_configurations
        assert WorldType.RESEARCH in factory.world_configurations
        assert WorldType.HOSPITAL in factory.world_configurations
        assert WorldType.EDUCATION in factory.world_configurations
    
    def test_list_available_world_types(self, factory):
        """Test listing available world types"""
        world_types = factory.list_available_world_types()
        
        assert isinstance(world_types, dict)
        assert "business" in world_types
        assert "research" in world_types
        assert "hospital" in world_types
        assert "education" in world_types
        
        # Check descriptions are provided
        for world_type, description in world_types.items():
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_get_world_configuration(self, factory):
        """Test retrieving world configurations"""
        # Test valid world type
        business_config = factory.get_world_configuration(WorldType.BUSINESS)
        assert isinstance(business_config, WorldConfiguration)
        assert business_config.world_type == WorldType.BUSINESS
        assert business_config.name == "Corporate Business Simulation"
        
        # Test invalid world type
        with pytest.raises(ValueError):
            factory.get_world_configuration("invalid_type")
    
    def test_business_world_configuration(self, factory):
        """Test business world configuration details"""
        config = factory.get_world_configuration(WorldType.BUSINESS)
        
        assert config.world_type == WorldType.BUSINESS
        assert config.default_timezone == TimeZone.PST
        assert config.business_hours_start == "09:00"
        assert config.business_hours_end == "17:00"
        assert config.max_employee_workload == 40.0
        assert config.meeting_frequency == "daily"
        assert config.collaboration_intensity == "high"
        
        # Check role configuration
        assert len(config.agent_roles) > 0
        ceo_role = next((r for r in config.agent_roles if r["role"] == "CEO"), None)
        assert ceo_role is not None
        assert ceo_role["authority_level"] == 10
        
        # Check department structure
        assert "Executive" in config.department_structure
        assert "Engineering" in config.department_structure
        assert "CEO" in config.department_structure["Executive"]
    
    def test_research_world_configuration(self, factory):
        """Test research world configuration details"""
        config = factory.get_world_configuration(WorldType.RESEARCH)
        
        assert config.world_type == WorldType.RESEARCH
        assert config.default_timezone == TimeZone.EST
        assert config.business_hours_start == "08:00"
        assert config.business_hours_end == "18:00"
        assert config.meeting_frequency == "weekly"
        assert config.task_complexity_bias.value == 4  # COMPLEX
        
        # Check research-specific roles
        roles = [r["role"] for r in config.agent_roles]
        assert "Research Director" in roles
        assert "Principal Investigator" in roles
        assert "PhD Student" in roles
        
        # Check research-specific settings
        assert config.custom_settings["publication_cycles"] is True
        assert config.custom_settings["grant_applications"] is True
    
    def test_hospital_world_configuration(self, factory):
        """Test hospital world configuration details"""
        config = factory.get_world_configuration(WorldType.HOSPITAL)
        
        assert config.world_type == WorldType.HOSPITAL
        assert config.business_hours_start == "00:00"  # 24/7 operation
        assert config.business_hours_end == "23:59"
        assert config.max_employee_workload == 60.0  # Longer healthcare shifts
        assert config.task_complexity_bias.value == 5  # EXPERT
        
        # Check medical roles
        roles = [r["role"] for r in config.agent_roles]
        assert "Chief of Medicine" in roles
        assert "Attending Physician" in roles
        assert "Registered Nurse" in roles
        
        # Check healthcare-specific settings
        assert config.custom_settings["shift_schedules"] is True
        assert config.custom_settings["emergency_protocols"] is True
    
    def test_education_world_configuration(self, factory):
        """Test education world configuration details"""
        config = factory.get_world_configuration(WorldType.EDUCATION)
        
        assert config.world_type == WorldType.EDUCATION
        assert config.business_hours_start == "08:00"
        assert config.business_hours_end == "16:00"
        assert config.meeting_frequency == "weekly"
        
        # Check academic roles
        roles = [r["role"] for r in config.agent_roles]
        assert "Principal/Dean" in roles
        assert "Professor" in roles
        assert "Teaching Assistant" in roles
        
        # Check education-specific settings
        assert config.custom_settings["semester_planning"] is True
        assert config.custom_settings["curriculum_review"] is True
    
    def test_create_business_world(self, factory, temp_storage):
        """Test creating a business world"""
        world_manager = factory.create_business_world(
            world_id="test_business",
            storage_path=temp_storage
        )
        
        assert isinstance(world_manager, PersistentWorldManager)
        assert world_manager.world_id == "test_business"
        assert world_manager.world_type == WorldType.BUSINESS
        assert hasattr(world_manager, 'world_config')
        assert world_manager.world_config.world_type == WorldType.BUSINESS
    
    def test_create_research_world(self, factory, temp_storage):
        """Test creating a research world"""
        world_manager = factory.create_research_world(
            world_id="test_research",
            storage_path=temp_storage
        )
        
        assert isinstance(world_manager, PersistentWorldManager)
        assert world_manager.world_id == "test_research"
        assert world_manager.world_type == WorldType.RESEARCH
        assert world_manager.world_config.world_type == WorldType.RESEARCH
    
    def test_create_hospital_world(self, factory, temp_storage):
        """Test creating a hospital world"""
        world_manager = factory.create_hospital_world(
            world_id="test_hospital",
            storage_path=temp_storage
        )
        
        assert isinstance(world_manager, PersistentWorldManager)
        assert world_manager.world_id == "test_hospital"
        assert world_manager.world_type == WorldType.HOSPITAL
        assert world_manager.world_config.world_type == WorldType.HOSPITAL
    
    def test_create_education_world(self, factory, temp_storage):
        """Test creating an education world"""
        world_manager = factory.create_education_world(
            world_id="test_education", 
            storage_path=temp_storage
        )
        
        assert isinstance(world_manager, PersistentWorldManager)
        assert world_manager.world_id == "test_education"
        assert world_manager.world_type == WorldType.EDUCATION
        assert world_manager.world_config.world_type == WorldType.EDUCATION
    
    def test_create_custom_world(self, factory, temp_storage):
        """Test creating a custom world type"""
        custom_config = {
            "name": "Test Custom World",
            "description": "Custom world for testing",
            "business_hours_start": "10:00",
            "business_hours_end": "18:00",
            "agent_roles": [
                {"role": "Manager", "department": "Operations", "authority_level": 8},
                {"role": "Worker", "department": "Operations", "authority_level": 3}
            ],
            "department_structure": {
                "Operations": ["Manager", "Worker"]
            },
            "required_skills": ["custom_skill_1", "custom_skill_2"],
            "custom_settings": {
                "custom_feature": True,
                "custom_value": 42
            }
        }
        
        world_manager = factory.create_custom_world(
            world_id="test_custom",
            custom_type_name="test_type",
            configuration=custom_config
        )
        
        assert isinstance(world_manager, PersistentWorldManager)
        assert world_manager.world_id == "test_custom"
        assert world_manager.world_type == WorldType.CUSTOM
        assert world_manager.world_config.name == "Test Custom World"
        assert world_manager.world_config.business_hours_start == "10:00"
        assert world_manager.world_config.custom_settings["custom_feature"] is True
        
        # Check that custom configuration is stored
        assert "test_type" in factory.custom_configurations
        stored_config = factory.custom_configurations["test_type"]
        assert stored_config.name == "Test Custom World"
    
    def test_custom_configuration_override(self, factory, temp_storage):
        """Test overriding default configuration with custom settings"""
        custom_config = {
            "name": "Custom Business World",
            "business_hours_start": "08:00",
            "business_hours_end": "19:00",
            "max_employee_workload": 45.0,
            "meeting_frequency": "weekly",
            "custom_settings": {
                "overtime_allowed": True,
                "flexible_hours": True
            }
        }
        
        world_manager = factory.create_business_world(
            world_id="custom_business",
            custom_config=custom_config,
            storage_path=temp_storage
        )
        
        config = world_manager.world_config
        assert config.name == "Custom Business World"
        assert config.business_hours_start == "08:00"
        assert config.business_hours_end == "19:00"
        assert config.max_employee_workload == 45.0
        assert config.meeting_frequency == "weekly"
        assert config.custom_settings["overtime_allowed"] is True
        assert config.custom_settings["flexible_hours"] is True
        
        # Check that base settings are preserved
        assert config.world_type == WorldType.BUSINESS
        assert config.default_timezone == TimeZone.PST


class TestConvenienceFunctions:
    """Test convenience factory functions"""
    
    def test_create_business_simulation(self):
        """Test business simulation convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            world_manager = create_business_simulation(
                world_id="convenience_business",
                storage_path=temp_dir
            )
            
            assert isinstance(world_manager, PersistentWorldManager)
            assert world_manager.world_id == "convenience_business"
            assert world_manager.world_type == WorldType.BUSINESS
    
    def test_create_research_simulation(self):
        """Test research simulation convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            world_manager = create_research_simulation(
                world_id="convenience_research",
                storage_path=temp_dir
            )
            
            assert isinstance(world_manager, PersistentWorldManager)
            assert world_manager.world_id == "convenience_research"
            assert world_manager.world_type == WorldType.RESEARCH
    
    def test_create_hospital_simulation(self):
        """Test hospital simulation convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            world_manager = create_hospital_simulation(
                world_id="convenience_hospital",
                storage_path=temp_dir
            )
            
            assert isinstance(world_manager, PersistentWorldManager)
            assert world_manager.world_id == "convenience_hospital"
            assert world_manager.world_type == WorldType.HOSPITAL
    
    def test_create_education_simulation(self):
        """Test education simulation convenience function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            world_manager = create_education_simulation(
                world_id="convenience_education",
                storage_path=temp_dir
            )
            
            assert isinstance(world_manager, PersistentWorldManager)
            assert world_manager.world_id == "convenience_education"
            assert world_manager.world_type == WorldType.EDUCATION


@pytest.mark.asyncio
class TestWorldManagerIntegration:
    """Test integration between factory and world manager"""
    
    async def test_world_manager_scheduling(self):
        """Test that created worlds have proper event scheduling"""
        with tempfile.TemporaryDirectory() as temp_dir:
            factory = BusinessWorldFactory()
            world_manager = factory.create_business_world(
                world_id="integration_test",
                storage_path=temp_dir
            )
            
            # Schedule an event
            today = date.today()
            world_manager.schedule_event(today, {
                "title": "Test Meeting",
                "type": "meeting",
                "duration": 60
            })
            
            # Prepare simulation day
            simulation_day = await world_manager.prepare_simulation_day(today)
            
            assert simulation_day is not None
            assert simulation_day.virtual_date == today
            
            # Should have at least the test meeting plus any recurring events
            assert len(simulation_day.scheduled_events) >= 1
            
            # Check if test meeting is in events
            test_meeting = next(
                (event for event in simulation_day.scheduled_events 
                 if event.get("title") == "Test Meeting"), 
                None
            )
            assert test_meeting is not None
    
    async def test_time_manager_configuration(self):
        """Test that time manager is properly configured"""
        with tempfile.TemporaryDirectory() as temp_dir:
            factory = BusinessWorldFactory()
            world_manager = factory.create_research_world(
                world_id="time_test",
                storage_path=temp_dir
            )
            
            # Prepare a simulation day to initialize time manager
            today = date.today()
            await world_manager.prepare_simulation_day(today)
            
            # Check that time manager has correct timezone (research world uses EST)
            assert world_manager.time_manager is not None
            assert world_manager.time_manager.calendar.timezone == TimeZone.EST


if __name__ == "__main__":
    pytest.main([__file__, "-v"])