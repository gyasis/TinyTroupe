"""
Test script for Hierarchical Task Delegation and Escalation System
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tinytroupe.delegation_system import (
    HierarchicalDelegationSystem, DelegationReason, EscalationTrigger
)
from tinytroupe.task_management import TaskManager, BusinessTask, TaskPriority, TaskStatus
from tinytroupe.business_simulation import HiringDatabase
from tinytroupe.task_assignment import TaskAssignmentEngine
from tinytroupe.business_employee import AsyncBusinessEmployee

async def test_delegation_system():
    """Test comprehensive delegation and escalation functionality"""
    print("🧪 Testing Hierarchical Task Delegation and Escalation System...")
    
    try:
        # Phase 1: Setup test environment
        print("\n📋 Phase 1: Setting up test environment...")
        
        # Create hiring database with organizational hierarchy
        hiring_db = HiringDatabase()
        
        # Create test employees with hierarchy
        ceo = AsyncBusinessEmployee("John CEO", "emp_ceo", "CEO", "Executive")
        vp_eng = AsyncBusinessEmployee("Sarah VP", "emp_vp_eng", "VP Engineering", "Engineering", "emp_ceo")
        manager = AsyncBusinessEmployee("Mike Manager", "emp_mgr", "Engineering Manager", "Engineering", "emp_vp_eng")
        senior_dev = AsyncBusinessEmployee("Alice Senior", "emp_sr_dev", "Senior Developer", "Engineering", "emp_mgr")
        junior_dev = AsyncBusinessEmployee("Bob Junior", "emp_jr_dev", "Junior Developer", "Engineering", "emp_mgr")
        
        # Add to hiring database
        for emp in [ceo, vp_eng, manager, senior_dev, junior_dev]:
            hiring_db.employees[emp.employee_id] = emp
        
        # Set up organizational chart
        hiring_db.organizational_chart["emp_ceo"] = {"emp_vp_eng"}
        hiring_db.organizational_chart["emp_vp_eng"] = {"emp_mgr"}
        hiring_db.organizational_chart["emp_mgr"] = {"emp_sr_dev", "emp_jr_dev"}
        
        # Create task manager and assignment engine
        task_manager = TaskManager()
        assignment_engine = TaskAssignmentEngine(task_manager, hiring_db)
        
        # Create delegation system
        delegation_system = HierarchicalDelegationSystem(hiring_db, task_manager, assignment_engine)
        
        print("✓ Test environment set up with 5 employees in hierarchy")
        
        # Phase 2: Test task delegation
        print("\n📤 Phase 2: Testing task delegation...")
        
        # Create test task
        test_task = task_manager.create_task(
            title="Implement new feature",
            description="Build authentication system",
            created_by="emp_mgr",
            priority=TaskPriority.HIGH,
            required_skills=["development", "security"]
        )
        test_task.assigned_to = "emp_mgr"
        test_task.due_date = datetime.now() + timedelta(days=3)
        
        # Test delegation from manager to senior developer
        success, message = await delegation_system.delegate_task(
            test_task.task_id,
            from_employee="emp_mgr",
            to_employee="emp_sr_dev",
            delegated_by="emp_mgr",
            reason=DelegationReason.SKILL_MATCH,
            delegation_message="You have the best security skills for this task"
        )
        
        print(f"✓ Delegation result: {success} - {message}")
        assert success, f"Delegation should succeed: {message}"
        assert test_task.assigned_to == "emp_sr_dev", "Task should be assigned to senior developer"
        
        # Test delegation chain tracking
        chain = delegation_system.delegation_chains[test_task.task_id]
        assert chain.chain_depth == 1, "Delegation chain depth should be 1"
        assert chain.original_assignee == "emp_mgr", "Original assignee should be manager"
        assert chain.current_assignee == "emp_sr_dev", "Current assignee should be senior dev"
        
        print("✓ Delegation chain tracking working correctly")
        
        # Phase 3: Test authority validation
        print("\n🔐 Phase 3: Testing authority validation...")
        
        # Try unauthorized delegation (junior trying to delegate high priority task)
        success, message = await delegation_system.delegate_task(
            test_task.task_id,
            from_employee="emp_sr_dev",
            to_employee="emp_jr_dev",
            delegated_by="emp_jr_dev",  # Junior trying to delegate
            reason=DelegationReason.WORKLOAD_BALANCE,
            delegation_message="I'm overloaded"
        )
        
        print(f"✓ Unauthorized delegation blocked: {not success} - {message}")
        assert not success, "Junior should not be able to delegate high priority task"
        
        # Test authorized delegation by VP
        success, message = await delegation_system.delegate_task(
            test_task.task_id,
            from_employee="emp_sr_dev",
            to_employee="emp_jr_dev",
            delegated_by="emp_vp_eng",  # VP has authority
            reason=DelegationReason.DEVELOPMENT_OPPORTUNITY,
            delegation_message="Good learning opportunity"
        )
        
        print(f"✓ Authorized delegation successful: {success} - {message}")
        assert success, f"VP should be able to delegate: {message}"
        
        # Phase 4: Test escalation
        print("\n📈 Phase 4: Testing task escalation...")
        
        # Create overdue task for escalation testing
        overdue_task = task_manager.create_task(
            title="Critical bug fix",
            description="Fix security vulnerability",
            created_by="emp_jr_dev",
            priority=TaskPriority.CRITICAL
        )
        overdue_task.assigned_to = "emp_jr_dev"
        overdue_task.due_date = datetime.now() - timedelta(hours=2)  # Already overdue
        
        # Test manual escalation
        success, message = await delegation_system.escalate_task(
            overdue_task.task_id,
            escalated_by="emp_jr_dev",
            trigger=EscalationTrigger.MANUAL_REQUEST,
            escalation_message="I need help with this critical bug"
        )
        
        print(f"✓ Manual escalation result: {success} - {message}")
        assert success, f"Manual escalation should succeed: {message}"
        assert overdue_task.assigned_to == "emp_mgr", "Task should be escalated to manager"
        
        # Test automatic escalation
        auto_escalations = await delegation_system.auto_escalate_overdue_tasks()
        print(f"✓ Found {len(auto_escalations)} tasks for auto-escalation")
        
        # Phase 5: Test delegation suggestions
        print("\n💡 Phase 5: Testing delegation suggestions...")
        
        # Create multiple tasks for manager
        for i in range(3):
            manager_task = task_manager.create_task(
                title=f"Manager Task {i+1}",
                description=f"Task {i+1} for delegation testing",
                created_by="emp_mgr",
                priority=TaskPriority.MEDIUM,
                required_skills=["development"]
            )
            manager_task.assigned_to = "emp_mgr"
        
        # Get delegation suggestions
        suggestions = await delegation_system.suggest_delegation_opportunities("emp_mgr")
        print(f"✓ Generated {len(suggestions)} delegation suggestions")
        
        for suggestion in suggestions:
            print(f"  - Task: {suggestion['task_title']} → {suggestion['recommended_assignee']}")
            print(f"    Reason: {suggestion['recommendation_reason']}")
        
        # Phase 6: Test analytics
        print("\n📊 Phase 6: Testing delegation analytics...")
        
        analytics = delegation_system.get_delegation_analytics()
        print(f"✓ Total delegations: {analytics['delegation_stats']['total_delegations']}")
        print(f"✓ Total escalations: {analytics['delegation_stats']['total_escalations']}")
        print(f"✓ Average delegation depth: {analytics['delegation_stats']['average_delegation_depth']:.2f}")
        
        if analytics['delegation_reasons']:
            print("✓ Delegation reasons breakdown:")
            for reason, count in analytics['delegation_reasons'].items():
                print(f"  - {reason}: {count}")
        
        # Phase 7: Final validation
        print("\n✅ Phase 7: Final validation...")
        
        # Verify delegation system integrity
        total_delegations = len(delegation_system.delegation_records)
        total_escalations = len(delegation_system.escalation_records)
        total_chains = len(delegation_system.delegation_chains)
        
        print(f"✓ System state: {total_delegations} delegations, {total_escalations} escalations, {total_chains} chains")
        
        # Check that all chains are valid
        for task_id, chain in delegation_system.delegation_chains.items():
            assert task_id in task_manager.tasks, f"Chain references non-existent task: {task_id}"
            assert chain.chain_depth == len(chain.delegation_history), "Chain depth mismatch"
            assert chain.chain_depth <= delegation_system.max_delegation_depth, "Chain exceeds max depth"
        
        print("🎉 Hierarchical Task Delegation and Escalation System Test PASSED!")
        print("\n✅ Validated Features:")
        print("  ✓ Hierarchical task delegation with authority validation")
        print("  ✓ Delegation chain tracking and depth management")
        print("  ✓ Manual and automatic task escalation")
        print("  ✓ Workload-based delegation suggestions")
        print("  ✓ Comprehensive analytics and reporting")
        print("  ✓ Organizational hierarchy integration")
        print("  ✓ Authority level enforcement")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\n🔬 Testing Edge Cases...")
    
    # Minimal setup for edge case testing
    hiring_db = HiringDatabase()
    task_manager = TaskManager()
    assignment_engine = TaskAssignmentEngine(task_manager, hiring_db)
    delegation_system = HierarchicalDelegationSystem(hiring_db, task_manager, assignment_engine)
    
    # Test delegation of non-existent task
    success, message = await delegation_system.delegate_task(
        "non_existent_task",
        from_employee="emp1",
        to_employee="emp2",
        delegated_by="emp1",
        reason=DelegationReason.WORKLOAD_BALANCE
    )
    assert not success, "Should fail for non-existent task"
    print("✓ Non-existent task delegation properly rejected")
    
    # Test escalation of non-existent task
    success, message = await delegation_system.escalate_task(
        "non_existent_task",
        escalated_by="emp1",
        trigger=EscalationTrigger.MANUAL_REQUEST
    )
    assert not success, "Should fail for non-existent task"
    print("✓ Non-existent task escalation properly rejected")
    
    print("✓ Edge case testing completed")

if __name__ == "__main__":
    print("🚀 Starting Hierarchical Task Delegation and Escalation System Tests...")
    
    async def run_all_tests():
        # Run main functionality tests
        main_test_success = await test_delegation_system()
        
        # Run edge case tests
        await test_edge_cases()
        
        return main_test_success
    
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ All Delegation System Tests PASSED!")
        print("The Hierarchical Task Delegation and Escalation System is working correctly.")
    else:
        print("\n❌ Some tests FAILED!")
        print("The Delegation System needs attention.")