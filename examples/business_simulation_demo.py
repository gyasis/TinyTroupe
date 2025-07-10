"""
Business Simulation Demo

This example demonstrates the Virtual Business Simulation extension for TinyTroupe.
It shows how to:
1. Load employees from the hiring database
2. Create a business simulation world
3. Conduct team meetings
4. Simulate business day activities
5. Get business analytics

Run this demo to see the business simulation in action.
"""

import asyncio
import logging
from datetime import time

from tinytroupe.business_simulation import HiringDatabase
from tinytroupe.business_world import BusinessSimulationWorld
import tinytroupe.control as control

# Configure logging for better output
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("business_demo")


async def main():
    """Main demo function"""
    
    # Initialize the business simulation
    logger.info("=== TinyTroupe Business Simulation Demo ===")
    
    # Start simulation control
    control.begin()
    
    try:
        # 1. Load the hiring database with employees
        logger.info("\n1. Loading Hiring Database...")
        hiring_db = HiringDatabase("employees")
        
        print(f"Loaded {len(hiring_db.employees)} employees:")
        for emp_id, employee in hiring_db.employees.items():
            print(f"  - {employee.name} ({employee.role}, {employee.department})")
        
        # 2. Create a business simulation world
        logger.info("\n2. Creating Business Simulation World...")
        business_world = BusinessSimulationWorld(
            name="TechCorp Virtual Office",
            hiring_database=hiring_db,
            business_hours_start=time(9, 0),
            business_hours_end=time(17, 0),
            enable_ceo_interrupt=True
        )
        
        # 3. Add Engineering department employees to the simulation
        logger.info("\n3. Adding Engineering Department to Simulation...")
        engineering_employees = await business_world.add_department("Engineering")
        
        print(f"Added {len(engineering_employees)} engineering employees:")
        for emp in engineering_employees:
            print(f"  - {emp.name} ({emp.role})")
        
        # 4. Show initial business analytics
        logger.info("\n4. Initial Business Analytics...")
        analytics = business_world.get_business_analytics()
        print(f"World: {analytics['world_name']}")
        print(f"Total Employees: {analytics['total_employees']}")
        print(f"Departments: {analytics['departments']}")
        print(f"Roles: {analytics['roles']}")
        print(f"Business Hours: {analytics['business_hours']['start']} - {analytics['business_hours']['end']}")
        
        # 5. Conduct a team meeting
        logger.info("\n5. Conducting Team Meeting...")
        
        # Find a manager (Sarah Johnson is EMP001)
        if "EMP001" in hiring_db.employees:
            meeting_result = await business_world.conduct_team_meeting(
                manager_id="EMP001",
                topic="Q4 Planning and Sprint Prioritization",
                include_manager=True
            )
            
            if meeting_result["success"]:
                print(f"Team meeting completed successfully!")
                print(f"Topic: {meeting_result['topic']}")
                print(f"Participants: {', '.join(meeting_result['participants'])}")
                print(f"Rounds: {meeting_result['rounds']}")
            else:
                print(f"Meeting failed: {meeting_result['reason']}")
        
        # 6. Simulate a business day
        logger.info("\n6. Simulating Business Day Activities...")
        
        business_activities = [
            "Morning standup and sprint planning",
            "Code review and technical discussions", 
            "Afternoon project work and collaboration"
        ]
        
        day_results = await business_world.simulate_business_day(business_activities)
        
        print("Business day simulation completed!")
        print(f"Activities completed: {len(day_results['activities'])}")
        for activity in day_results['activities']:
            print(f"  - {activity['activity']} ({activity['participants']} participants)")
        
        # 7. Final business analytics
        logger.info("\n7. Final Business Analytics...")
        final_analytics = business_world.get_business_analytics()
        
        print("Business Metrics:")
        for metric, value in final_analytics['business_metrics'].items():
            print(f"  - {metric}: {value}")
        
        # 8. Show organizational insights
        logger.info("\n8. Organizational Insights...")
        
        # Show team structure
        if "EMP001" in hiring_db.employees:
            sarah_team = business_world.get_team_members("EMP001")
            print(f"Sarah Johnson's Team ({len(sarah_team)} members):")
            for member in sarah_team:
                print(f"  - {member.name} ({member.role})")
        
        # Show department analytics
        eng_analytics = hiring_db.get_department_analytics("Engineering")
        print(f"\nEngineering Department Analytics:")
        print(f"  - Total Employees: {eng_analytics['total_employees']}")
        print(f"  - Average Salary: ${eng_analytics['average_salary']:,.0f}")
        print(f"  - Average Tenure: {eng_analytics['average_tenure_years']} years")
        print(f"  - Performance Distribution: {eng_analytics['performance_distribution']}")
        
        logger.info("\n=== Demo Completed Successfully! ===")
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise
    
    finally:
        # End simulation control
        control.end()


if __name__ == "__main__":
    asyncio.run(main())