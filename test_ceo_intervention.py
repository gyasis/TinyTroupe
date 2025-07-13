"""
Test CEO Intervention Capabilities

This script tests the newly implemented CEO intervention features:
- Direct task reassignment
- Priority adjustments
- Deadline modifications
- Emergency interventions
- Intervention history tracking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from tinytroupe.task_management import TaskManager, BusinessTask, TaskStatus, TaskPriority
from tinytroupe.business_simulation import HiringDatabase
from tinytroupe.task_assignment import TaskAssignmentEngine
from tinytroupe.delegation_system import HierarchicalDelegationSystem
from tinytroupe.ceo_dashboard import CEODashboard, create_ceo_dashboard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_test_environment():
    """Set up test environment with sample data"""
    # Create components
    task_manager = TaskManager()
    hiring_database = HiringDatabase()
    assignment_engine = TaskAssignmentEngine(task_manager, hiring_database)
    delegation_system = HierarchicalDelegationSystem(task_manager, hiring_database)
    
    # Add sample employees
    employees = [
        {
            "employee_id": "alice_001", 
            "name": "Alice Johnson", 
            "role": "Senior Engineer", 
            "department": "Engineering",
            "manager_id": "ceo_001",
            "skills": {"python": 9, "architecture": 8, "leadership": 7}
        },
        {
            "employee_id": "bob_002", 
            "name": "Bob Smith", 
            "role": "Project Manager", 
            "department": "Engineering",
            "manager_id": "ceo_001",
            "skills": {"project_management": 9, "coordination": 8, "planning": 9}
        },
        {
            "employee_id": "carol_003", 
            "name": "Carol Davis", 
            "role": "QA Engineer", 
            "department": "Engineering",
            "manager_id": "bob_002",
            "skills": {"testing": 9, "automation": 7, "quality_assurance": 8}
        },
        {
            "employee_id": "ceo_001",
            "name": "CEO Executive",
            "role": "Chief Executive Officer",
            "department": "Executive",
            "manager_id": None,
            "skills": {"leadership": 10, "strategy": 9, "decision_making": 10}
        }
    ]
    
    for emp_data in employees:
        await hiring_database.add_employee(**emp_data)
    
    # Create sample tasks
    tasks = [
        {
            "title": "Implement User Authentication",
            "description": "Build secure user login system",
            "created_by": "bob_002",
            "priority": TaskPriority.HIGH,
            "assigned_to": "alice_001",
            "due_date": datetime.now() + timedelta(days=7)
        },
        {
            "title": "Database Performance Optimization", 
            "description": "Optimize slow database queries",
            "created_by": "alice_001",
            "priority": TaskPriority.MEDIUM,
            "assigned_to": "alice_001",
            "due_date": datetime.now() + timedelta(days=14)
        },
        {
            "title": "API Testing Suite",
            "description": "Create comprehensive API test coverage",
            "created_by": "bob_002", 
            "priority": TaskPriority.LOW,
            "assigned_to": "carol_003",
            "due_date": datetime.now() + timedelta(days=21)
        },
        {
            "title": "Critical Security Patch",
            "description": "Fix critical security vulnerability",
            "created_by": "ceo_001",
            "priority": TaskPriority.CRITICAL,
            "assigned_to": "alice_001",
            "due_date": datetime.now() + timedelta(days=2)
        }
    ]
    
    task_ids = []
    for task_data in tasks:
        task_id = task_manager.create_task(**task_data)
        task_ids.append(task_id)
    
    # Create CEO Dashboard
    dashboard = create_ceo_dashboard(task_manager, hiring_database, assignment_engine, delegation_system)
    
    return dashboard, task_manager, hiring_database, task_ids

async def test_task_reassignment(dashboard: CEODashboard, task_ids: list):
    """Test CEO task reassignment capability"""
    print("\n=== Testing CEO Task Reassignment ===")
    
    task_id = task_ids[0]  # "Implement User Authentication"
    new_assignee = "bob_002"  # Reassign from Alice to Bob
    reason = "Alice is overloaded with critical security work"
    
    # Perform reassignment
    result = await dashboard.reassign_task(task_id, new_assignee, reason)
    
    print(f"Reassignment Result: {result['success']}")
    if result['success']:
        print(f"✅ Task '{result['task_details']['title']}' successfully reassigned")
        print(f"   From: {result['task_details']['old_assignee']}")
        print(f"   To: {result['task_details']['new_assignee']}")
        print(f"   Reason: {reason}")
    else:
        print(f"❌ Reassignment failed: {result['error']}")
    
    return result

async def test_priority_adjustment(dashboard: CEODashboard, task_ids: list):
    """Test CEO priority adjustment capability"""
    print("\n=== Testing CEO Priority Adjustment ===")
    
    task_id = task_ids[2]  # "API Testing Suite" 
    new_priority = TaskPriority.HIGH  # Escalate from LOW to HIGH
    reason = "Customer demo next week requires API testing"
    
    # Perform priority adjustment
    result = await dashboard.adjust_task_priority(task_id, new_priority, reason)
    
    print(f"Priority Adjustment Result: {result['success']}")
    if result['success']:
        print(f"✅ Task '{result['task_details']['title']}' priority updated")
        print(f"   From: {result['task_details']['old_priority']}")
        print(f"   To: {result['task_details']['new_priority']}")
        print(f"   Reason: {reason}")
    else:
        print(f"❌ Priority adjustment failed: {result['error']}")
    
    return result

async def test_deadline_modification(dashboard: CEODashboard, task_ids: list):
    """Test CEO deadline modification capability"""
    print("\n=== Testing CEO Deadline Modification ===")
    
    task_id = task_ids[1]  # "Database Performance Optimization"
    new_deadline = datetime.now() + timedelta(days=5)  # Shorten deadline significantly
    reason = "Performance issues blocking production release"
    
    # Perform deadline modification
    result = await dashboard.modify_task_deadline(task_id, new_deadline, reason)
    
    print(f"Deadline Modification Result: {result['success']}")
    if result['success']:
        print(f"✅ Task '{result['task_details']['title']}' deadline updated")
        print(f"   Old deadline: {result['task_details']['old_deadline']}")
        print(f"   New deadline: {result['task_details']['new_deadline']}")
        print(f"   Impact: {result['task_details']['impact']} by {abs(result['task_details']['deadline_change_days'] or 0)} days")
        print(f"   Reason: {reason}")
    else:
        print(f"❌ Deadline modification failed: {result['error']}")
    
    return result

async def test_emergency_intervention(dashboard: CEODashboard, task_ids: list):
    """Test CEO emergency intervention capability"""
    print("\n=== Testing CEO Emergency Intervention ===")
    
    task_id = task_ids[3]  # "Critical Security Patch"
    intervention_type = "rush"
    target_assignee = "bob_002"  # Rush assignment to Bob
    new_deadline = datetime.now() + timedelta(hours=6)  # 6 hours to complete
    reason = "Security vulnerability being actively exploited"
    
    # Perform emergency intervention
    result = await dashboard.emergency_task_intervention(
        task_id=task_id,
        intervention_type=intervention_type,
        target_assignee=target_assignee,
        new_deadline=new_deadline,
        reason=reason
    )
    
    print(f"Emergency Intervention Result: {result['success']}")
    if result['success']:
        print(f"✅ Emergency '{intervention_type}' intervention completed")
        print(f"   Alert created: {result['alert_created']}")
        print(f"   Interventions performed: {len(result['intervention_results'])}")
        for i, intervention in enumerate(result['intervention_results']):
            if intervention.get('success'):
                print(f"   {i+1}. {intervention.get('intervention_log', {}).get('action', 'Unknown')} ✅")
            else:
                print(f"   {i+1}. Failed: {intervention.get('error')} ❌")
    else:
        print(f"❌ Emergency intervention failed: {result['error']}")
    
    return result

async def test_intervention_history(dashboard: CEODashboard):
    """Test intervention history tracking"""
    print("\n=== Testing Intervention History ===")
    
    # Get intervention history
    history = await dashboard.get_intervention_history(days_back=1)
    
    print(f"Intervention History: {len(history)} interventions found")
    
    for i, intervention in enumerate(history[:5]):  # Show first 5
        print(f"{i+1}. {intervention['title']}")
        print(f"   Type: {intervention['type']}")
        print(f"   Description: {intervention['description']}")
        print(f"   Timestamp: {intervention['timestamp']}")
        print(f"   Acknowledged: {intervention['acknowledged']}")
        print()
    
    return history

async def test_dashboard_alerts(dashboard: CEODashboard):
    """Test dashboard alerts related to interventions"""
    print("\n=== Testing Dashboard Alerts ===")
    
    print(f"Current Alerts: {len(dashboard.alerts)}")
    
    ceo_alerts = [alert for alert in dashboard.alerts if "CEO" in alert.title]
    print(f"CEO Intervention Alerts: {len(ceo_alerts)}")
    
    for alert in ceo_alerts:
        print(f"- {alert.title} [{alert.level.value}]")
        print(f"  {alert.description}")
        print(f"  Affected: {alert.affected_entity}")
        print(f"  Suggested actions: {', '.join(alert.actions_suggested)}")
        print()

async def run_comprehensive_test():
    """Run comprehensive CEO intervention test suite"""
    print("🚀 Starting CEO Intervention Capabilities Test")
    print("=" * 60)
    
    # Setup test environment
    dashboard, task_manager, hiring_database, task_ids = await setup_test_environment()
    
    print(f"✅ Test environment setup complete")
    print(f"   - Employees: {len(hiring_database.employees)}")
    print(f"   - Tasks: {len(task_manager.tasks)}")
    
    # Run intervention tests
    test_results = {}
    
    try:
        # Test individual intervention capabilities
        test_results['reassignment'] = await test_task_reassignment(dashboard, task_ids)
        test_results['priority'] = await test_priority_adjustment(dashboard, task_ids)
        test_results['deadline'] = await test_deadline_modification(dashboard, task_ids)
        test_results['emergency'] = await test_emergency_intervention(dashboard, task_ids)
        
        # Test tracking and reporting
        test_results['history'] = await test_intervention_history(dashboard)
        await test_dashboard_alerts(dashboard)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CEO INTERVENTION CAPABILITIES TEST SUMMARY")
        print("=" * 60)
        
        successful_tests = sum(1 for test, result in test_results.items() 
                             if test != 'history' and result.get('success', False))
        total_tests = len([t for t in test_results.keys() if t != 'history'])
        
        print(f"✅ Successful interventions: {successful_tests}/{total_tests}")
        print(f"📊 Total interventions tracked: {len(test_results['history'])}")
        print(f"🚨 Alerts generated: {len(dashboard.alerts)}")
        
        if successful_tests == total_tests:
            print("\n🎉 ALL CEO INTERVENTION CAPABILITIES ARE WORKING PERFECTLY!")
        else:
            print(f"\n⚠️  {total_tests - successful_tests} intervention(s) failed - check logs for details")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        logger.exception("Test suite error")
        return False

if __name__ == "__main__":
    # Run the test suite
    asyncio.run(run_comprehensive_test())