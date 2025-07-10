"""
Test script for comprehensive state serialization and restoration
"""

import asyncio
import sys
import os
import tempfile
import shutil
import logging
from datetime import date, timedelta
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable debug logging for troubleshooting
logging.basicConfig(level=logging.INFO)
persistence_logger = logging.getLogger("tinytroupe.persistence")
persistence_logger.setLevel(logging.INFO)

from tinytroupe.business_world_factory import create_business_simulation
from tinytroupe.business_employee import AsyncBusinessEmployee

async def test_state_serialization():
    """Test complete state serialization and restoration cycle"""
    print("🧪 Testing Complete State Serialization System...")
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        test_storage = Path(temp_dir) / "test_serialization"
        
        try:
            # Phase 1: Create initial simulation with employees
            print("\n📅 Phase 1: Creating initial simulation...")
            
            world_manager = create_business_simulation(
                world_id="serialization_test",
                storage_path=str(test_storage)
            )
            
            # Add test event
            today = date.today()
            world_manager.schedule_event(today, {
                "title": "Team Standup",
                "type": "meeting",
                "attendees": ["CEO", "Engineers"],
                "duration": 30
            })
            
            # Prepare and initialize first simulation day
            simulation_day = await world_manager.prepare_simulation_day(today)
            world = await world_manager.initialize_world(simulation_day)
            
            # Add a test employee to the world
            test_employee = AsyncBusinessEmployee(
                name="Alice Johnson",
                employee_id="alice_001",
                role="Senior Engineer",
                department="Engineering"
            )
            test_employee.business_skills = {"python": 9, "leadership": 7}
            test_employee.performance_rating = "Exceeds Expectations"
            
            world.agents.append(test_employee)
            world.hiring_database.employees["alice_001"] = test_employee
            
            # Initialize business metrics
            world.business_metrics = {
                "meetings_completed": 0,
                "collaboration_events": 0,
                "productivity_score": 85.5
            }
            
            print(f"✓ Initial world created with {len(world.agents)} agents")
            
            # Run simulation to generate some state
            await world.async_run(1)
            world.business_metrics["meetings_completed"] = 1
            
            # Save state for day 1
            save_success = await world_manager.save_simulation_day(simulation_day)
            print(f"✓ Day 1 state saved: {save_success}")
            
            # Phase 2: Create second day and verify state restoration
            print("\n📅 Phase 2: Testing state restoration...")
            
            tomorrow = today + timedelta(days=1)
            
            # Create new world manager to simulate fresh start
            world_manager_2 = create_business_simulation(
                world_id="serialization_test",
                storage_path=str(test_storage)
            )
            
            # Prepare second day (should load previous state)
            simulation_day_2 = await world_manager_2.prepare_simulation_day(tomorrow)
            world_2 = await world_manager_2.initialize_world(simulation_day_2)
            
            print(f"✓ Day 2 world created with {len(world_2.agents)} agents")
            
            # Verify state restoration
            validation_results = await validate_restored_state(
                original_world=world,
                restored_world=world_2,
                simulation_day_2=simulation_day_2
            )
            
            # Phase 3: Run multi-day cycle
            print("\n📅 Phase 3: Testing multi-day persistence...")
            
            # Run simulation for day 2
            await world_2.async_run(1)
            world_2.business_metrics["meetings_completed"] += 1
            
            # Save day 2 state
            save_success_2 = await world_manager_2.save_simulation_day(simulation_day_2)
            print(f"✓ Day 2 state saved: {save_success_2}")
            
            # Check world history
            history = world_manager_2.get_world_history()
            print(f"✓ World history: {len(history)} saved states")
            print(f"  Available dates: {[d.isoformat() for d in history]}")
            
            # Phase 4: Final validation
            print("\n📊 Phase 4: Final Validation...")
            
            if validation_results["success"]:
                print("🎉 State Serialization Test PASSED!")
                print("\n✅ Validated Features:")
                for feature in validation_results["validated_features"]:
                    print(f"  ✓ {feature}")
                
                if validation_results["warnings"]:
                    print("\n⚠️ Warnings:")
                    for warning in validation_results["warnings"]:
                        print(f"  ⚠️ {warning}")
                
                return True
            else:
                print("❌ State Serialization Test FAILED!")
                print("\n❌ Failures:")
                for failure in validation_results["failures"]:
                    print(f"  ❌ {failure}")
                
                return False
                
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False

async def validate_restored_state(original_world, restored_world, simulation_day_2):
    """Validate that restored state matches original state"""
    
    validation_results = {
        "success": True,
        "validated_features": [],
        "failures": [],
        "warnings": []
    }
    
    # Check agent count
    if len(restored_world.agents) == len(original_world.agents):
        validation_results["validated_features"].append("Agent count preserved")
    else:
        validation_results["failures"].append(
            f"Agent count mismatch: {len(original_world.agents)} → {len(restored_world.agents)}"
        )
        validation_results["success"] = False
    
    # Check business metrics
    if hasattr(restored_world, 'business_metrics') and hasattr(original_world, 'business_metrics'):
        orig_productivity = original_world.business_metrics.get("productivity_score", 0)
        rest_productivity = restored_world.business_metrics.get("productivity_score", 0)
        
        if orig_productivity == rest_productivity:
            validation_results["validated_features"].append("Business metrics preserved")
        else:
            validation_results["failures"].append(
                f"Business metrics mismatch: {orig_productivity} → {rest_productivity}"
            )
            validation_results["success"] = False
    
    # Check employee data in hiring database
    if hasattr(restored_world, 'hiring_database') and hasattr(original_world, 'hiring_database'):
        orig_emp_count = len(original_world.hiring_database.employees)
        rest_emp_count = len(restored_world.hiring_database.employees)
        
        if orig_emp_count == rest_emp_count:
            validation_results["validated_features"].append("Hiring database employee count preserved")
        else:
            validation_results["failures"].append(
                f"Employee count in hiring DB mismatch: {orig_emp_count} → {rest_emp_count}"
            )
            validation_results["success"] = False
        
        # Check specific employee data
        if "alice_001" in original_world.hiring_database.employees and "alice_001" in restored_world.hiring_database.employees:
            orig_alice = original_world.hiring_database.employees["alice_001"]
            rest_alice = restored_world.hiring_database.employees["alice_001"]
            
            if orig_alice.business_skills == rest_alice.business_skills:
                validation_results["validated_features"].append("Employee business skills preserved")
            else:
                validation_results["failures"].append("Employee business skills not preserved")
                validation_results["success"] = False
            
            if orig_alice.performance_rating == rest_alice.performance_rating:
                validation_results["validated_features"].append("Employee performance rating preserved")
            else:
                validation_results["failures"].append("Employee performance rating not preserved")
                validation_results["success"] = False
    
    # Check if previous state was loaded
    if simulation_day_2.previous_state is not None:
        validation_results["validated_features"].append("Previous state successfully loaded")
    else:
        validation_results["warnings"].append("Previous state was not loaded (might be expected for new world)")
    
    # Check scheduled events
    if len(simulation_day_2.scheduled_events) > 0:
        validation_results["validated_features"].append("Scheduled events available")
    else:
        validation_results["warnings"].append("No scheduled events found")
    
    return validation_results

if __name__ == "__main__":
    success = asyncio.run(test_state_serialization())
    
    if success:
        print("\n✅ Complete State Serialization System is working correctly!")
    else:
        print("\n❌ State Serialization System needs attention.")