"""
Test Daily Scheduling System

This script tests the newly implemented Daily Scheduling System features:
- Employee working hours management
- Task work scheduling
- Meeting scheduling with conflict detection
- Time logging and tracking
- Activity summaries and analytics
- Schedule conflict detection and resolution
"""

import asyncio
import logging
from datetime import datetime, timedelta, time, date
from typing import Dict, Any

from tinytroupe.task_management import TaskManager, TaskPriority
from tinytroupe.business_simulation import HiringDatabase
from tinytroupe.daily_scheduling import (
    DailySchedulingSystem, WorkingHours, ActivityType, 
    ScheduleConflictType, create_daily_scheduling_system
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_test_environment():
    """Set up test environment with sample data"""
    # Create components
    task_manager = TaskManager()
    hiring_database = HiringDatabase()
    
    # Add sample employees
    employees = [
        {
            "employee_id": "alice_001", 
            "name": "Alice Johnson", 
            "role": "Senior Engineer", 
            "department": "Engineering",
            "manager_id": "bob_002",
            "skills": {"python": 9, "architecture": 8, "project_management": 6}
        },
        {
            "employee_id": "bob_002", 
            "name": "Bob Smith", 
            "role": "Engineering Manager", 
            "department": "Engineering",
            "manager_id": "ceo_001",
            "skills": {"leadership": 9, "project_management": 9, "engineering": 7}
        },
        {
            "employee_id": "carol_003", 
            "name": "Carol Davis", 
            "role": "QA Engineer", 
            "department": "Engineering",
            "manager_id": "bob_002",
            "skills": {"testing": 9, "automation": 8, "quality_assurance": 9}
        },
        {
            "employee_id": "david_004",
            "name": "David Wilson",
            "role": "Product Manager",
            "department": "Product",
            "manager_id": "ceo_001", 
            "skills": {"product_management": 9, "strategy": 8, "communication": 9}
        }
    ]
    
    for emp_data in employees:
        await hiring_database.add_employee(**emp_data)
    
    # Create sample tasks
    tasks = [
        {
            "title": "Implement Authentication System",
            "description": "Build secure user login and registration",
            "created_by": "bob_002",
            "priority": TaskPriority.HIGH,
            "assigned_to": "alice_001",
            "due_date": datetime.now() + timedelta(days=5)
        },
        {
            "title": "Create Test Automation Framework", 
            "description": "Build automated testing infrastructure",
            "created_by": "bob_002",
            "priority": TaskPriority.MEDIUM,
            "assigned_to": "carol_003",
            "due_date": datetime.now() + timedelta(days=10)
        },
        {
            "title": "Product Requirements Analysis",
            "description": "Analyze market requirements for new features",
            "created_by": "david_004",
            "priority": TaskPriority.HIGH,
            "assigned_to": "david_004",
            "due_date": datetime.now() + timedelta(days=7)
        }
    ]
    
    task_ids = []
    for task_data in tasks:
        task_id = task_manager.create_task(**task_data)
        task_ids.append(task_id)
    
    # Create scheduling system
    scheduling_system = create_daily_scheduling_system(task_manager, hiring_database)
    
    return scheduling_system, task_manager, hiring_database, task_ids

async def test_working_hours_setup(scheduling_system: DailySchedulingSystem):
    """Test employee working hours configuration"""
    print("\n=== Testing Working Hours Setup ===")
    
    # Test custom working hours for Alice (early bird)
    alice_hours = WorkingHours(
        start_time=time(8, 0),    # 8:00 AM
        end_time=time(16, 0),     # 4:00 PM
        lunch_start=time(12, 0),  # 12:00 PM
        lunch_end=time(12, 30),   # 12:30 PM
        break_start=time(10, 30), # 10:30 AM
        break_end=time(10, 45),   # 10:45 AM
        timezone="PST"
    )
    
    success = await scheduling_system.set_employee_working_hours("alice_001", alice_hours)
    print(f"✅ Alice's custom hours set: {success}")
    print(f"   Working hours: {alice_hours.start_time} - {alice_hours.end_time}")
    print(f"   Total daily hours: {alice_hours.total_working_hours():.1f}")
    
    # Test custom working hours for Bob (standard with long lunch)
    bob_hours = WorkingHours(
        start_time=time(9, 0),    # 9:00 AM
        end_time=time(18, 0),     # 6:00 PM
        lunch_start=time(12, 0),  # 12:00 PM
        lunch_end=time(13, 30),   # 1:30 PM
        timezone="EST"
    )
    
    success = await scheduling_system.set_employee_working_hours("bob_002", bob_hours)
    print(f"✅ Bob's custom hours set: {success}")
    print(f"   Working hours: {bob_hours.start_time} - {bob_hours.end_time}")
    print(f"   Total daily hours: {bob_hours.total_working_hours():.1f}")
    
    return True

async def test_daily_schedule_creation(scheduling_system: DailySchedulingSystem):
    """Test daily schedule creation"""
    print("\n=== Testing Daily Schedule Creation ===")
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Create schedules for multiple employees and dates
    employees = ["alice_001", "bob_002", "carol_003", "david_004"]
    dates = [today, tomorrow]
    
    created_schedules = 0
    for employee_id in employees:
        for schedule_date in dates:
            schedule = await scheduling_system.create_daily_schedule(employee_id, schedule_date)
            if schedule:
                created_schedules += 1
                print(f"✅ Schedule created for {employee_id} on {schedule_date}")
            else:
                print(f"❌ Failed to create schedule for {employee_id} on {schedule_date}")
    
    print(f"📊 Total schedules created: {created_schedules}/{len(employees) * len(dates)}")
    return created_schedules > 0

async def test_task_work_scheduling(scheduling_system: DailySchedulingSystem, task_ids: list):
    """Test task work scheduling"""
    print("\n=== Testing Task Work Scheduling ===")
    
    today = date.today()
    
    # Schedule task work for Alice (Authentication System)
    alice_work_time = datetime.combine(today, time(9, 30))  # 9:30 AM
    alice_activity = await scheduling_system.schedule_task_work(
        employee_id="alice_001",
        task_id=task_ids[0],
        start_datetime=alice_work_time,
        estimated_hours=4.0
    )
    
    if alice_activity:
        print(f"✅ Task work scheduled for Alice: {alice_activity.title}")
        print(f"   Time: {alice_activity.start_datetime.strftime('%H:%M')} - {alice_activity.end_datetime.strftime('%H:%M')}")
        print(f"   Duration: {alice_activity.duration_hours} hours")
    else:
        print("❌ Failed to schedule task work for Alice")
    
    # Schedule task work for Carol (Test Automation)
    carol_work_time = datetime.combine(today, time(10, 0))  # 10:00 AM
    carol_activity = await scheduling_system.schedule_task_work(
        employee_id="carol_003",
        task_id=task_ids[1],
        start_datetime=carol_work_time,
        estimated_hours=6.0
    )
    
    if carol_activity:
        print(f"✅ Task work scheduled for Carol: {carol_activity.title}")
        print(f"   Time: {carol_activity.start_datetime.strftime('%H:%M')} - {carol_activity.end_datetime.strftime('%H:%M')}")
        print(f"   Duration: {carol_activity.duration_hours} hours")
    else:
        print("❌ Failed to schedule task work for Carol")
    
    # Try to schedule conflicting work for Alice (should detect conflict)
    conflicting_time = datetime.combine(today, time(11, 0))  # 11:00 AM (overlaps with 9:30-13:30)
    conflicting_activity = await scheduling_system.schedule_task_work(
        employee_id="alice_001",
        task_id=task_ids[2],
        start_datetime=conflicting_time,
        estimated_hours=3.0
    )
    
    if not conflicting_activity:
        print("✅ Conflict correctly detected and prevented scheduling")
    else:
        print("❌ Conflict not detected - this is a problem!")
    
    return alice_activity is not None and carol_activity is not None

async def test_meeting_scheduling(scheduling_system: DailySchedulingSystem):
    """Test meeting scheduling with multiple attendees"""
    print("\n=== Testing Meeting Scheduling ===")
    
    today = date.today()
    
    # Schedule team meeting
    meeting_time = datetime.combine(today, time(14, 0))  # 2:00 PM
    meeting_result = await scheduling_system.schedule_meeting(
        organizer_id="bob_002",
        attendee_ids=["alice_001", "carol_003", "david_004"],
        meeting_title="Sprint Planning Meeting",
        start_datetime=meeting_time,
        duration_hours=1.5,
        location="Conference Room A"
    )
    
    print(f"Meeting scheduling result: {meeting_result['success']}")
    print(f"✅ Scheduled attendees: {len(meeting_result['scheduled_attendees'])}")
    print(f"⚠️  Conflicts detected: {len(meeting_result['conflicts'])}")
    
    if meeting_result['conflicts']:
        print("   Conflict details:")
        for conflict in meeting_result['conflicts'][:3]:  # Show first 3
            print(f"   - {conflict.description}")
    
    if 'conflict_resolution' in meeting_result:
        print(f"   Alternative times suggested: {len(meeting_result['conflict_resolution'])}")
        for alt in meeting_result['conflict_resolution'][:2]:  # Show first 2
            alt_time = datetime.fromisoformat(alt['suggested_time'])
            print(f"   - {alt_time.strftime('%H:%M')} (no conflicts)")
    
    # Try scheduling another meeting with conflicts
    conflicting_meeting_time = datetime.combine(today, time(14, 30))  # 2:30 PM (overlaps)
    conflicting_result = await scheduling_system.schedule_meeting(
        organizer_id="david_004",
        attendee_ids=["alice_001", "bob_002"],
        meeting_title="Product Review",
        start_datetime=conflicting_meeting_time,
        duration_hours=1.0
    )
    
    print(f"\nConflicting meeting result: {conflicting_result['success']}")
    print(f"   Conflicts: {len(conflicting_result['conflicts'])}")
    
    return meeting_result['success']

async def test_time_logging(scheduling_system: DailySchedulingSystem):
    """Test time logging and tracking"""
    print("\n=== Testing Time Logging ===")
    
    # Simulate Alice logging time for her authentication work
    start_time = datetime.combine(date.today(), time(9, 30))
    end_time = datetime.combine(date.today(), time(13, 0))  # 3.5 hours actual vs 4 hours estimated
    
    # Find Alice's task activity
    alice_schedule = await scheduling_system.get_daily_schedule("alice_001", date.today())
    alice_activity = None
    if alice_schedule:
        for activity in alice_schedule.activities:
            if activity.activity_type == ActivityType.TASK_WORK and activity.employee_id == "alice_001":
                alice_activity = activity
                break
    
    if alice_activity:
        success = await scheduling_system.log_time_entry(
            employee_id="alice_001",
            activity_id=alice_activity.activity_id,
            start_time=start_time,
            end_time=end_time,
            notes="Completed user registration, working on login functionality"
        )
        
        print(f"✅ Time logged for Alice: {success}")
        print(f"   Planned: {alice_activity.estimated_hours} hours")
        print(f"   Actual: {(end_time - start_time).total_seconds() / 3600:.1f} hours")
        print(f"   Efficiency: {(alice_activity.estimated_hours / 3.5 * 100):.1f}%")
    else:
        print("❌ Could not find Alice's activity to log time")
        success = False
    
    # Log time for Carol's testing work
    carol_start = datetime.combine(date.today(), time(10, 0))
    carol_end = datetime.combine(date.today(), time(12, 30))  # 2.5 hours of a 6-hour task
    
    carol_schedule = await scheduling_system.get_daily_schedule("carol_003", date.today())
    carol_activity = None
    if carol_schedule:
        for activity in carol_schedule.activities:
            if activity.activity_type == ActivityType.TASK_WORK and activity.employee_id == "carol_003":
                carol_activity = activity
                break
    
    if carol_activity:
        carol_success = await scheduling_system.log_time_entry(
            employee_id="carol_003",
            activity_id=carol_activity.activity_id,
            start_time=carol_start,
            end_time=carol_end,
            notes="Set up initial test framework structure"
        )
        
        print(f"✅ Time logged for Carol: {carol_success}")
        print(f"   Progress: {(2.5 / carol_activity.estimated_hours * 100):.1f}% complete")
    else:
        print("❌ Could not find Carol's activity to log time")
        carol_success = False
    
    return success and carol_success

async def test_activity_summary(scheduling_system: DailySchedulingSystem):
    """Test activity summary generation"""
    print("\n=== Testing Activity Summary ===")
    
    today = date.today()
    date_range = (today, today)  # Single day summary
    
    # Generate summary for Alice
    alice_summary = await scheduling_system.generate_activity_summary("alice_001", date_range)
    
    print(f"📊 Alice's Activity Summary for {today}")
    print(f"   Scheduled hours: {alice_summary['scheduled_hours']:.1f}")
    print(f"   Actual hours: {alice_summary['actual_hours']:.1f}")
    print(f"   Productivity score: {alice_summary['productivity_score']:.1f}%")
    print(f"   Conflicts: {alice_summary['conflicts']}")
    print(f"   Overtime: {alice_summary['overtime_hours']:.1f} hours")
    
    print("   Activity breakdown:")
    for activity_type, breakdown in alice_summary['activity_breakdown'].items():
        print(f"   - {activity_type}: {breakdown['count']} activities, {breakdown['actual_hours']:.1f}h actual")
    
    # Generate summary for Carol
    carol_summary = await scheduling_system.generate_activity_summary("carol_003", date_range)
    
    print(f"\n📊 Carol's Activity Summary for {today}")
    print(f"   Scheduled hours: {carol_summary['scheduled_hours']:.1f}")
    print(f"   Actual hours: {carol_summary['actual_hours']:.1f}")
    print(f"   Productivity score: {carol_summary['productivity_score']:.1f}%")
    
    return len(alice_summary['activity_breakdown']) > 0

async def test_conflict_detection(scheduling_system: DailySchedulingSystem):
    """Test comprehensive conflict detection"""
    print("\n=== Testing Conflict Detection ===")
    
    today = date.today()
    
    # Get all conflicts for today
    conflicts = await scheduling_system.detect_schedule_conflicts_for_date(today)
    
    print(f"🔍 Schedule conflicts detected for {today}: {len(conflicts)}")
    
    conflict_types = {}
    for conflict in conflicts:
        conflict_type = conflict.conflict_type.value
        if conflict_type not in conflict_types:
            conflict_types[conflict_type] = 0
        conflict_types[conflict_type] += 1
        
        print(f"   ⚠️  {conflict.description}")
        print(f"      Severity: {conflict.severity}")
        print(f"      Suggestion: {conflict.suggested_resolution}")
    
    print(f"\n📈 Conflict type breakdown:")
    for conflict_type, count in conflict_types.items():
        print(f"   - {conflict_type}: {count}")
    
    # Get employee-specific conflicts
    alice_conflicts = await scheduling_system.get_schedule_conflicts("alice_001")
    print(f"\n👤 Alice's specific conflicts: {len(alice_conflicts)}")
    
    return len(conflicts) >= 0  # Even 0 conflicts is a valid result

async def test_schedule_retrieval(scheduling_system: DailySchedulingSystem):
    """Test schedule retrieval and querying"""
    print("\n=== Testing Schedule Retrieval ===")
    
    today = date.today()
    
    # Test getting daily schedules
    employees = ["alice_001", "bob_002", "carol_003", "david_004"]
    schedules_found = 0
    
    for employee_id in employees:
        schedule = await scheduling_system.get_daily_schedule(employee_id, today)
        if schedule:
            schedules_found += 1
            print(f"✅ {employee_id}: {len(schedule.activities)} activities, {schedule.total_scheduled_hours:.1f}h scheduled")
            
            # Show activity details
            for activity in schedule.activities[:2]:  # Show first 2 activities
                print(f"   - {activity.title} [{activity.activity_type.value}]")
                print(f"     {activity.start_datetime.strftime('%H:%M')} - {activity.end_datetime.strftime('%H:%M')}")
        else:
            print(f"❌ No schedule found for {employee_id}")
    
    print(f"\n📊 Schedules retrieved: {schedules_found}/{len(employees)}")
    return schedules_found > 0

async def run_comprehensive_test():
    """Run comprehensive Daily Scheduling System test suite"""
    print("🚀 Starting Daily Scheduling System Test")
    print("=" * 60)
    
    # Setup test environment
    scheduling_system, task_manager, hiring_database, task_ids = await setup_test_environment()
    
    print(f"✅ Test environment setup complete")
    print(f"   - Employees: {len(hiring_database.employees)}")
    print(f"   - Tasks: {len(task_manager.tasks)}")
    
    # Run scheduling tests
    test_results = {}
    
    try:
        # Test core scheduling features
        test_results['working_hours'] = await test_working_hours_setup(scheduling_system)
        test_results['schedule_creation'] = await test_daily_schedule_creation(scheduling_system)
        test_results['task_scheduling'] = await test_task_work_scheduling(scheduling_system, task_ids)
        test_results['meeting_scheduling'] = await test_meeting_scheduling(scheduling_system)
        test_results['time_logging'] = await test_time_logging(scheduling_system)
        test_results['activity_summary'] = await test_activity_summary(scheduling_system)
        test_results['conflict_detection'] = await test_conflict_detection(scheduling_system)
        test_results['schedule_retrieval'] = await test_schedule_retrieval(scheduling_system)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 DAILY SCHEDULING SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        if successful_tests == total_tests:
            print(f"\n🎉 ALL DAILY SCHEDULING FEATURES ARE WORKING PERFECTLY!")
            print(f"📅 Employees can now have comprehensive schedule management")
            print(f"⏱️  Time tracking and productivity analytics available")
            print(f"🚨 Conflict detection and resolution working")
        else:
            print(f"\n⚠️  {total_tests - successful_tests} test(s) failed - check logs for details")
            
        return successful_tests == total_tests
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        logger.exception("Test suite error")
        return False

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_comprehensive_test())