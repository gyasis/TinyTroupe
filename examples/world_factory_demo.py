"""
BusinessWorldFactory Usage Demo

This example demonstrates how to use the BusinessWorldFactory to create
different types of simulation worlds: business, research, hospital, and education.
"""

import asyncio
import logging
import sys
import os
from datetime import date, datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tinytroupe.business_world_factory import (
    BusinessWorldFactory, 
    create_business_simulation,
    create_research_simulation,
    create_hospital_simulation,
    create_education_simulation,
    WorldConfiguration
)
from tinytroupe.persistent_world_manager import WorldType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_business_world():
    """Demonstrate creating and configuring a business simulation world"""
    print("\n" + "="*60)
    print("BUSINESS WORLD SIMULATION DEMO")
    print("="*60)
    
    # Create business world using convenience function
    business_world = create_business_simulation(
        world_id="acme_corp_2024",
        storage_path="business_demo"
    )
    
    print(f"Created business world: {business_world.world_id}")
    print(f"World type: {business_world.world_type.value}")
    
    # Schedule some business events
    today = date.today()
    business_world.schedule_event(today, {
        "title": "Q4 Planning Meeting",
        "type": "meeting",
        "attendees": ["CEO", "VP_Engineering", "VP_Marketing"],
        "duration": 120,
        "priority": "high"
    })
    
    business_world.schedule_event(today + timedelta(days=1), {
        "title": "Product Launch Review",
        "type": "meeting", 
        "attendees": ["Product_Manager", "Engineering_Team"],
        "duration": 90,
        "priority": "medium"
    })
    
    # Prepare a simulation day
    simulation_day = await business_world.prepare_simulation_day(today)
    print(f"Prepared simulation day: {simulation_day.virtual_date}")
    print(f"Business day type: {simulation_day.business_day.day_type.value}")
    print(f"Scheduled events: {len(simulation_day.scheduled_events)}")
    
    for event in simulation_day.scheduled_events:
        print(f"  - {event.get('title', 'Untitled Event')}")
    
    return business_world


async def demo_research_world():
    """Demonstrate creating a research institution simulation"""
    print("\n" + "="*60)
    print("RESEARCH WORLD SIMULATION DEMO")
    print("="*60)
    
    # Create research world with custom configuration
    custom_config = {
        "name": "Advanced AI Research Lab",
        "description": "Leading artificial intelligence research facility",
        "custom_settings": {
            "focus_areas": ["machine_learning", "robotics", "nlp"],
            "publication_goal": 12,  # papers per year
            "grant_funding": 2500000  # USD
        }
    }
    
    research_world = create_research_simulation(
        world_id="ai_research_lab_2024",
        custom_config=custom_config,
        storage_path="research_demo"
    )
    
    print(f"Created research world: {research_world.world_id}")
    print(f"World configuration: {research_world.world_config.name}")
    
    # Schedule research-specific events
    today = date.today()
    research_world.schedule_event(today, {
        "title": "Research Progress Review",
        "type": "meeting",
        "attendees": ["Research_Director", "Principal_Investigators"],
        "duration": 90,
        "research_focus": "quarterly_review"
    })
    
    research_world.schedule_recurring_event({
        "title": "Lab Meeting", 
        "type": "meeting",
        "duration": 60,
        "recurrence": {"type": "weekly", "weekday": 2}  # Tuesday
    })
    
    # Prepare simulation
    simulation_day = await research_world.prepare_simulation_day(today)
    print(f"Research simulation prepared for: {simulation_day.virtual_date}")
    print(f"Events scheduled: {len(simulation_day.scheduled_events)}")
    
    return research_world


async def demo_hospital_world():
    """Demonstrate creating a hospital operations simulation"""
    print("\n" + "="*60)
    print("HOSPITAL WORLD SIMULATION DEMO")
    print("="*60)
    
    # Create hospital world
    hospital_world = create_hospital_simulation(
        world_id="general_hospital_2024",
        storage_path="hospital_demo"
    )
    
    print(f"Created hospital world: {hospital_world.world_id}")
    
    # Schedule medical events
    today = date.today()
    hospital_world.schedule_event(today, {
        "title": "Morning Rounds",
        "type": "medical_activity",
        "attendees": ["Attending_Physicians", "Residents", "Nurses"],
        "duration": 60,
        "priority": "high",
        "medical_focus": "patient_care"
    })
    
    hospital_world.schedule_event(today, {
        "title": "Emergency Drill",
        "type": "training",
        "attendees": ["All_Staff"],
        "duration": 30,
        "priority": "medium"
    })
    
    hospital_world.schedule_recurring_event({
        "title": "Shift Change Briefing",
        "type": "briefing",
        "duration": 15,
        "recurrence": {"type": "daily"}
    })
    
    # Prepare simulation
    simulation_day = await hospital_world.prepare_simulation_day(today)
    print(f"Hospital simulation prepared for: {simulation_day.virtual_date}")
    print(f"Medical events: {len(simulation_day.scheduled_events)}")
    
    return hospital_world


async def demo_education_world():
    """Demonstrate creating an educational institution simulation"""
    print("\n" + "="*60)
    print("EDUCATION WORLD SIMULATION DEMO")
    print("="*60)
    
    # Create education world
    education_world = create_education_simulation(
        world_id="university_cs_dept_2024",
        storage_path="education_demo"
    )
    
    print(f"Created education world: {education_world.world_id}")
    
    # Schedule academic events
    today = date.today()
    education_world.schedule_event(today, {
        "title": "Faculty Meeting",
        "type": "meeting",
        "attendees": ["Department_Chair", "Professors", "Assistant_Professors"],
        "duration": 90,
        "academic_focus": "curriculum_planning"
    })
    
    education_world.schedule_event(today + timedelta(days=3), {
        "title": "Student Assessment Review",
        "type": "academic_review",
        "attendees": ["Professors", "Teaching_Assistants"],
        "duration": 60
    })
    
    # Prepare simulation
    simulation_day = await education_world.prepare_simulation_day(today)
    print(f"Education simulation prepared for: {simulation_day.virtual_date}")
    print(f"Academic events: {len(simulation_day.scheduled_events)}")
    
    return education_world


async def demo_custom_world():
    """Demonstrate creating a custom world type"""
    print("\n" + "="*60)
    print("CUSTOM WORLD SIMULATION DEMO")
    print("="*60)
    
    factory = BusinessWorldFactory()
    
    # Define custom retail simulation configuration
    retail_config = {
        "name": "Retail Store Operations",
        "description": "Retail chain management simulation with stores, inventory, and customers",
        "business_hours_start": "10:00",
        "business_hours_end": "20:00",
        "agent_roles": [
            {"role": "Store Manager", "department": "Management", "authority_level": 8},
            {"role": "Assistant Manager", "department": "Management", "authority_level": 6},
            {"role": "Sales Associate", "department": "Sales", "authority_level": 3},
            {"role": "Cashier", "department": "Sales", "authority_level": 2},
            {"role": "Inventory Specialist", "department": "Operations", "authority_level": 4},
            {"role": "Customer Service Rep", "department": "Service", "authority_level": 3}
        ],
        "department_structure": {
            "Management": ["Store Manager", "Assistant Manager"],
            "Sales": ["Sales Associate", "Cashier"],
            "Operations": ["Inventory Specialist"],
            "Service": ["Customer Service Rep"]
        },
        "required_skills": ["customer_service", "sales", "inventory_management", "cash_handling"],
        "meeting_frequency": "weekly",
        "custom_settings": {
            "store_hours": "10:00-20:00",
            "peak_hours": ["12:00-14:00", "17:00-19:00"],
            "inventory_cycles": "monthly",
            "customer_satisfaction_target": 85
        }
    }
    
    # Create custom retail world
    retail_world = factory.create_custom_world(
        world_id="retail_chain_flagship_2024",
        custom_type_name="retail_operations",
        configuration=retail_config
    )
    
    print(f"Created custom retail world: {retail_world.world_id}")
    print(f"World configuration: {retail_world.world_config.name}")
    
    # Schedule retail-specific events
    today = date.today()
    retail_world.schedule_event(today, {
        "title": "Daily Store Opening Briefing",
        "type": "briefing",
        "attendees": ["All_Staff"],
        "duration": 15,
        "retail_focus": "daily_goals"
    })
    
    retail_world.schedule_event(today, {
        "title": "Inventory Count",
        "type": "operations",
        "attendees": ["Inventory_Specialist", "Assistant_Manager"],
        "duration": 120,
        "priority": "medium"
    })
    
    # Prepare simulation
    simulation_day = await retail_world.prepare_simulation_day(today)
    print(f"Retail simulation prepared for: {simulation_day.virtual_date}")
    print(f"Retail events: {len(simulation_day.scheduled_events)}")
    
    return retail_world


def demo_factory_features():
    """Demonstrate factory features and capabilities"""
    print("\n" + "="*60)
    print("FACTORY FEATURES DEMO")
    print("="*60)
    
    factory = BusinessWorldFactory()
    
    # List available world types
    print("Available World Types:")
    world_types = factory.list_available_world_types()
    for world_type, description in world_types.items():
        print(f"  {world_type}: {description}")
    
    # Show configuration details for each type
    print("\nWorld Type Configurations:")
    for world_type in [WorldType.BUSINESS, WorldType.RESEARCH, WorldType.HOSPITAL, WorldType.EDUCATION]:
        config = factory.get_world_configuration(world_type)
        print(f"\n{world_type.value.upper()}:")
        print(f"  Name: {config.name}")
        print(f"  Business Hours: {config.business_hours_start} - {config.business_hours_end}")
        print(f"  Max Workload: {config.max_employee_workload} hours/week")
        print(f"  Meeting Frequency: {config.meeting_frequency}")
        print(f"  Collaboration: {config.collaboration_intensity}")
        print(f"  Departments: {list(config.department_structure.keys())}")
        print(f"  Roles: {len(config.agent_roles)} different roles")


async def main():
    """Run all factory demos"""
    print("BUSINESS WORLD FACTORY DEMONSTRATION")
    print("This demo shows how to create different types of simulation worlds")
    
    # Demo factory features
    demo_factory_features()
    
    # Demo each world type
    business_world = await demo_business_world()
    research_world = await demo_research_world()
    hospital_world = await demo_hospital_world()
    education_world = await demo_education_world()
    retail_world = await demo_custom_world()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Successfully created {5} different simulation worlds:")
    print(f"  1. Business: {business_world.world_id}")
    print(f"  2. Research: {research_world.world_id}")
    print(f"  3. Hospital: {hospital_world.world_id}")
    print(f"  4. Education: {education_world.world_id}")
    print(f"  5. Custom Retail: {retail_world.world_id}")
    
    print("\nEach world type has:")
    print("  - Specialized role configurations")
    print("  - Domain-specific event scheduling")
    print("  - Customized business rules")
    print("  - Tailored collaboration patterns")
    
    print("\nNext steps:")
    print("  - Initialize worlds with agents")
    print("  - Run multi-day simulations")
    print("  - Analyze cross-world performance")
    print("  - Create industry-specific scenarios")


if __name__ == "__main__":
    asyncio.run(main())