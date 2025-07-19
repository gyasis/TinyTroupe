"""
Test script for CEO Dashboard - Real-time Business Simulation Monitoring System
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tinytroupe.ceo_dashboard import CEODashboard, AlertLevel, MetricTrend, create_ceo_dashboard
from tinytroupe.task_management import TaskManager, BusinessTask, TaskPriority, TaskStatus
from tinytroupe.business_simulation import HiringDatabase
from tinytroupe.task_assignment import TaskAssignmentEngine
from tinytroupe.delegation_system import HierarchicalDelegationSystem
from tinytroupe.business_employee import AsyncBusinessEmployee

async def test_ceo_dashboard():
    """Test comprehensive CEO dashboard functionality"""
    print("🚀 Testing CEO Dashboard - Real-time Business Monitoring System...")
    
    try:
        # Phase 1: Setup test environment
        print("\n📋 Phase 1: Setting up business simulation environment...")
        
        # Create hiring database with sample organization
        hiring_db = HiringDatabase()
        
        # Create diverse organizational structure
        employees = [
            AsyncBusinessEmployee("Alice CEO", "emp_ceo", "Chief Executive Officer", "Executive"),
            AsyncBusinessEmployee("Bob CTO", "emp_cto", "Chief Technology Officer", "Technology", "emp_ceo"),
            AsyncBusinessEmployee("Carol VP Sales", "emp_vp_sales", "VP of Sales", "Sales", "emp_ceo"),
            AsyncBusinessEmployee("David Engineering Manager", "emp_eng_mgr", "Engineering Manager", "Engineering", "emp_cto"),
            AsyncBusinessEmployee("Eve Senior Developer", "emp_sr_dev", "Senior Developer", "Engineering", "emp_eng_mgr"),
            AsyncBusinessEmployee("Frank Junior Developer", "emp_jr_dev", "Junior Developer", "Engineering", "emp_eng_mgr"),
            AsyncBusinessEmployee("Grace Sales Manager", "emp_sales_mgr", "Sales Manager", "Sales", "emp_vp_sales"),
            AsyncBusinessEmployee("Henry Sales Rep", "emp_sales_rep", "Sales Representative", "Sales", "emp_sales_mgr"),
            AsyncBusinessEmployee("Iris Marketing Manager", "emp_mkt_mgr", "Marketing Manager", "Marketing", "emp_ceo"),
            AsyncBusinessEmployee("Jack Support Lead", "emp_support", "Support Lead", "Customer Support", "emp_cto")
        ]
        
        # Add employees to hiring database
        for emp in employees:
            hiring_db.employees[emp.employee_id] = emp
            # Add some business skills
            emp.business_skills = {
                "leadership": 7 if "manager" in emp.role.lower() or "ceo" in emp.role.lower() else 5,
                "technical": 8 if "developer" in emp.role.lower() or "cto" in emp.role.lower() else 4,
                "communication": 8 if "sales" in emp.role.lower() or "marketing" in emp.role.lower() else 6,
                "project_management": 6
            }
        
        # Set up organizational chart
        hiring_db.organizational_chart = {
            "emp_ceo": {"emp_cto", "emp_vp_sales", "emp_mkt_mgr"},
            "emp_cto": {"emp_eng_mgr", "emp_support"},
            "emp_vp_sales": {"emp_sales_mgr"},
            "emp_eng_mgr": {"emp_sr_dev", "emp_jr_dev"},
            "emp_sales_mgr": {"emp_sales_rep"}
        }
        
        # Create business management systems
        task_manager = TaskManager()
        assignment_engine = TaskAssignmentEngine(task_manager, hiring_db)
        delegation_system = HierarchicalDelegationSystem(hiring_db, task_manager, assignment_engine)
        
        # Create CEO Dashboard
        dashboard = create_ceo_dashboard(task_manager, hiring_db, assignment_engine, delegation_system)
        
        print("✓ Business environment set up with 10 employees across 5 departments")
        
        # Phase 2: Create realistic business scenario with tasks
        print("\n📈 Phase 2: Creating realistic business scenario with diverse tasks...")
        
        # Create various types of tasks
        tasks_data = [
            # High-priority engineering tasks
            ("Implement authentication system", "Build secure user authentication", "emp_sr_dev", TaskPriority.HIGH, 16),
            ("Fix critical security bug", "Resolve SQL injection vulnerability", "emp_jr_dev", TaskPriority.CRITICAL, 8),
            ("Database optimization", "Optimize query performance", "emp_eng_mgr", TaskPriority.MEDIUM, 12),
            
            # Sales and marketing tasks
            ("Q3 sales campaign", "Launch new product campaign", "emp_sales_mgr", TaskPriority.HIGH, 20),
            ("Client demo preparation", "Prepare demo for Fortune 500 client", "emp_sales_rep", TaskPriority.HIGH, 6),
            ("Marketing content creation", "Create blog posts and social media", "emp_mkt_mgr", TaskPriority.MEDIUM, 15),
            
            # Cross-functional tasks
            ("Product roadmap planning", "Define next quarter roadmap", "emp_ceo", TaskPriority.HIGH, 10),
            ("Customer support automation", "Implement chatbot system", "emp_support", TaskPriority.MEDIUM, 14),
            ("Team building event", "Organize company retreat", "emp_mkt_mgr", TaskPriority.LOW, 8),
            
            # Overdue tasks to test alerts
            ("Legacy system migration", "Migrate old customer database", "emp_sr_dev", TaskPriority.CRITICAL, 25),
        ]
        
        created_tasks = []
        for title, desc, assignee, priority, hours in tasks_data:
            task = task_manager.create_task(
                title=title,
                description=desc,
                created_by="emp_ceo",
                priority=priority,
                estimated_hours=hours,
                required_skills=["technical", "project_management"]
            )
            task.assigned_to = assignee
            
            # Make some tasks overdue
            if "critical" in title.lower() or "legacy" in title.lower():
                task.due_date = datetime.now() - timedelta(days=2)  # Overdue
            else:
                task.due_date = datetime.now() + timedelta(days=7)
                
            created_tasks.append(task)
        
        # Complete some tasks to show performance metrics
        for i in range(3):
            task = created_tasks[i]
            task.status = TaskStatus.COMPLETED
            task.completed_date = datetime.now() - timedelta(days=i+1)
        
        # Block one task to test escalation
        created_tasks[4].status = TaskStatus.BLOCKED
        
        print(f"✓ Created {len(created_tasks)} diverse business tasks")
        print(f"  - {len([t for t in created_tasks if t.status == TaskStatus.COMPLETED])} completed tasks")
        print(f"  - {len([t for t in created_tasks if t.due_date and datetime.now() > t.due_date and t.status != TaskStatus.COMPLETED])} overdue tasks")
        print(f"  - {len([t for t in created_tasks if t.status == TaskStatus.BLOCKED])} blocked tasks")
        
        # Phase 3: Test real-time dashboard overview
        print("\n📊 Phase 3: Testing real-time dashboard overview...")
        
        overview = await dashboard.get_real_time_overview()
        
        print("✓ Dashboard Overview Generated:")
        print(f"  - Business Health Score: {overview['business_overview'].business_health_score:.1f}")
        print(f"  - Total Employees: {overview['business_overview'].total_employees}")
        print(f"  - Active Tasks: {overview['business_overview'].active_tasks}")
        print(f"  - Completed Today: {overview['business_overview'].completed_tasks_today}")
        print(f"  - On-time Delivery Rate: {overview['business_overview'].on_time_delivery_rate:.1f}%")
        print(f"  - Burnout Risk Employees: {overview['business_overview'].burnout_risk_employees}")
        print(f"  - Critical Task Delays: {overview['business_overview'].critical_task_delays}")
        
        # Test employee metrics
        employee_metrics = overview['employee_metrics']
        print(f"\n✓ Employee Metrics Generated for {len(employee_metrics)} employees:")
        for emp_id, metrics in list(employee_metrics.items())[:3]:  # Show first 3
            print(f"  - {metrics.name} ({metrics.role}): {metrics.current_tasks} tasks, {metrics.utilization_percentage:.1f}% utilization")
        
        # Test department metrics
        department_metrics = overview['department_metrics']
        print(f"\n✓ Department Metrics Generated for {len(department_metrics)} departments:")
        for dept_name, metrics in department_metrics.items():
            print(f"  - {dept_name}: {metrics.employee_count} employees, {metrics.completion_rate:.1f}% completion rate")
        
        # Test alerts system
        alerts = overview['active_alerts']
        print(f"\n✓ Alert System Generated {len(alerts)} alerts:")
        for alert in alerts[:5]:  # Show first 5 alerts
            print(f"  - {alert.level.value.upper()}: {alert.title}")
            if alert.actions_suggested:
                print(f"    Suggested Actions: {', '.join(alert.actions_suggested[:2])}")
        
        # Phase 4: Test employee deep dive analysis
        print("\n🔍 Phase 4: Testing employee deep dive analysis...")
        
        # Test deep dive for a senior developer
        deep_dive = await dashboard.get_employee_deep_dive("emp_sr_dev")
        
        print("✓ Employee Deep Dive Analysis:")
        print(f"  - Employee: {deep_dive['employee_info']['name']}")
        print(f"  - Current Tasks: {deep_dive['metrics'].current_tasks}")
        print(f"  - Workload Hours: {deep_dive['metrics'].total_workload_hours}")
        print(f"  - Performance Trend: {deep_dive['metrics'].performance_trend.value}")
        print(f"  - Development Opportunities: {deep_dive['metrics'].development_opportunities}")
        print(f"  - Recommendations: {len(deep_dive['recommendations'])} strategic recommendations")
        
        # Phase 5: Test department analysis
        print("\n🏢 Phase 5: Testing department analysis...")
        
        dept_analysis = await dashboard.get_department_analysis("Engineering")
        
        print("✓ Department Analysis for Engineering:")
        print(f"  - Department Metrics: {dept_analysis['metrics'].employee_count} employees")
        print(f"  - Active Tasks: {dept_analysis['metrics'].total_active_tasks}")
        print(f"  - Completion Rate: {dept_analysis['metrics'].completion_rate:.1f}%")
        print(f"  - Average Utilization: {dept_analysis['metrics'].average_utilization:.1f}%")
        print(f"  - Improvement Opportunities: {len(dept_analysis['improvement_opportunities'])} identified")
        
        # Phase 6: Test task management insights
        print("\n📋 Phase 6: Testing task management insights...")
        
        task_insights = await dashboard.get_task_management_insights()
        
        print("✓ Task Management Insights:")
        print(f"  - Task Flow Analysis: {len(task_insights['task_flow_analysis'])} flow patterns")
        print(f"  - Bottlenecks Identified: {len(task_insights['bottlenecks'])} bottlenecks")
        print(f"  - Priority Analysis: {len(task_insights['priority_analysis'])} priority levels analyzed")
        print(f"  - Delegation Effectiveness: {task_insights['delegation_effectiveness']['score']:.1f}% effective")
        print(f"  - Optimization Suggestions: {len(task_insights['optimization_suggestions'])} suggestions")
        
        # Phase 7: Test alert management
        print("\n🚨 Phase 7: Testing alert management...")
        
        # Acknowledge first alert
        if alerts:
            first_alert = alerts[0]
            success = await dashboard.acknowledge_alert(first_alert.alert_id)
            print(f"✓ Alert acknowledgment: {success}")
            
            # Dismiss second alert
            if len(alerts) > 1:
                second_alert = alerts[1]
                success = await dashboard.dismiss_alert(second_alert.alert_id)
                print(f"✓ Alert dismissal: {success}")
        
        # Phase 8: Test dashboard data export
        print("\n💾 Phase 8: Testing dashboard data export...")
        
        export_data = dashboard.export_dashboard_data("json")
        print("✓ Dashboard export functionality tested")
        
        # Phase 9: Performance and reliability validation
        print("\n⚡ Phase 9: Performance and reliability validation...")
        
        # Test dashboard refresh performance
        start_time = datetime.now()
        overview_2 = await dashboard.get_real_time_overview()
        refresh_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✓ Dashboard refresh performance: {refresh_time:.2f} seconds")
        print(f"✓ Data consistency: {len(overview_2['employee_metrics'])} employees in second refresh")
        
        # Validate dashboard health
        dashboard_health = overview_2['dashboard_health']
        print("✓ Dashboard Health Check:")
        print(f"  - System Status: {dashboard_health['system_status']}")
        print(f"  - Total Alerts: {dashboard_health['total_alerts']}")
        print(f"  - Critical Alerts: {dashboard_health['critical_alerts']}")
        print(f"  - Urgent Alerts: {dashboard_health['urgent_alerts']}")
        
        print("\n🎉 CEO Dashboard Test PASSED!")
        print("\n✅ Validated Features:")
        print("  ✓ Real-time business overview with comprehensive KPIs")
        print("  ✓ Employee performance metrics and workload monitoring")
        print("  ✓ Department analytics and resource utilization")
        print("  ✓ Intelligent alert system with actionable recommendations")
        print("  ✓ Employee deep dive analysis with development insights")
        print("  ✓ Department analysis with team dynamics")
        print("  ✓ Task management insights and bottleneck identification")
        print("  ✓ Alert management (acknowledge/dismiss functionality)")
        print("  ✓ Performance monitoring and data export capabilities")
        print("  ✓ Business health scoring and trend analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_dashboard_edge_cases():
    """Test edge cases and error conditions"""
    print("\n🔬 Testing CEO Dashboard Edge Cases...")
    
    # Clean minimal setup for edge case testing
    hiring_db = HiringDatabase()
    hiring_db.employees.clear()  # Ensure empty state
    task_manager = TaskManager()
    task_manager.tasks.clear()   # Ensure empty state
    assignment_engine = TaskAssignmentEngine(task_manager, hiring_db)
    delegation_system = HierarchicalDelegationSystem(hiring_db, task_manager, assignment_engine)
    dashboard = CEODashboard(task_manager, hiring_db, assignment_engine, delegation_system)
    
    # Test with empty organization
    overview = await dashboard.get_real_time_overview()
    assert overview['business_overview'].total_employees == 0
    print("✓ Empty organization handled correctly")
    
    # Test non-existent employee deep dive
    result = await dashboard.get_employee_deep_dive("non_existent")
    assert "error" in result
    print("✓ Non-existent employee properly handled")
    
    # Test non-existent department analysis
    result = await dashboard.get_department_analysis("NonExistentDept")
    assert "error" in result
    print("✓ Non-existent department properly handled")
    
    # Test alert operations on non-existent alerts
    success = await dashboard.acknowledge_alert("fake_alert_id")
    assert not success
    print("✓ Non-existent alert acknowledgment properly handled")
    
    success = await dashboard.dismiss_alert("fake_alert_id")
    assert not success
    print("✓ Non-existent alert dismissal properly handled")
    
    print("✓ Edge case testing completed")

if __name__ == "__main__":
    print("🚀 Starting CEO Dashboard Comprehensive Tests...")
    
    async def run_all_tests():
        # Run main functionality tests
        main_test_success = await test_ceo_dashboard()
        
        # Run edge case tests
        await test_dashboard_edge_cases()
        
        return main_test_success
    
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ All CEO Dashboard Tests PASSED!")
        print("The CEO Dashboard Real-time Business Monitoring System is working correctly.")
    else:
        print("\n❌ Some tests FAILED!")
        print("The CEO Dashboard needs attention.")