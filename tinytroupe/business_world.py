"""
BusinessSimulationWorld - Business-focused extension of AsyncTinyWorld

Extends AsyncTinyWorld with business simulation capabilities including
organizational structure awareness and business-specific interactions.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, time

from tinytroupe.async_world import AsyncTinyWorld
from tinytroupe.business_employee import AsyncBusinessEmployee
from tinytroupe.business_simulation import HiringDatabase

logger = logging.getLogger("tinytroupe.business")


class BusinessSimulationWorld(AsyncTinyWorld):
    """
    Business simulation world that extends AsyncTinyWorld with:
    - Integration with HiringDatabase for employee management
    - Business hours and scheduling awareness
    - Organizational hierarchy support
    - Business-specific event handling
    """
    
    def __init__(self, name: str = "Business Simulation", 
                 hiring_database: Optional[HiringDatabase] = None,
                 business_hours_start: time = time(9, 0),
                 business_hours_end: time = time(17, 0),
                 **kwargs):
        """
        Initialize business simulation world.
        
        Args:
            name: World name
            hiring_database: Employee database (creates new if None)
            business_hours_start: Start of business day
            business_hours_end: End of business day
            **kwargs: Additional arguments for AsyncTinyWorld
        """
        super().__init__(name=name, is_meeting=True, **kwargs)
        
        # Business-specific attributes
        self.hiring_database = hiring_database or HiringDatabase()
        self.business_hours_start = business_hours_start
        self.business_hours_end = business_hours_end
        
        # Business state tracking
        self.business_metrics: Dict[str, Any] = {
            "productivity_score": 0.0,
            "collaboration_events": 0,
            "decisions_made": 0,
            "meetings_completed": 0
        }
        
        logger.info(f"Created BusinessSimulationWorld: {name}")
    
    def is_business_hours(self) -> bool:
        """Check if current simulation time is within business hours"""
        current_time = self.current_datetime.time()
        return self.business_hours_start <= current_time <= self.business_hours_end
    
    async def add_employee(self, employee_id: str) -> Optional[AsyncBusinessEmployee]:
        """Add an employee to the world by loading from hiring database"""
        agent = await self.hiring_database.create_agent(employee_id)
        if agent:
            self.add_agent(agent)
            logger.info(f"Added employee {agent.name} ({employee_id}) to business world")
            return agent
        return None
    
    async def add_department(self, department: str) -> List[AsyncBusinessEmployee]:
        """Add all employees from a department to the world"""
        employees = self.hiring_database.get_employees_by_department(department)
        added_agents = []
        
        for employee in employees:
            agent = await self.add_employee(employee.employee_id)
            if agent:
                added_agents.append(agent)
        
        logger.info(f"Added {len(added_agents)} employees from {department} department")
        return added_agents
    
    def get_business_employee(self, employee_id: str) -> Optional[AsyncBusinessEmployee]:
        """Get business employee by ID from active agents"""
        for agent in self.agents:
            if isinstance(agent, AsyncBusinessEmployee) and agent.employee_id == employee_id:
                return agent
        return None
    
    def get_employees_by_department(self, department: str) -> List[AsyncBusinessEmployee]:
        """Get active employees in a specific department"""
        return [agent for agent in self.agents 
                if isinstance(agent, AsyncBusinessEmployee) and agent.department == department]
    
    def get_team_members(self, manager_id: str) -> List[AsyncBusinessEmployee]:
        """Get team members (direct reports) for a manager"""
        manager = self.get_business_employee(manager_id)
        if not manager:
            return []
        
        team = []
        for agent in self.agents:
            if isinstance(agent, AsyncBusinessEmployee) and agent.manager_id == manager_id:
                team.append(agent)
        
        return team
    
    async def conduct_team_meeting(self, manager_id: str, topic: str, 
                                 include_manager: bool = True) -> Dict[str, Any]:
        """Conduct a meeting with a manager's team"""
        team = self.get_team_members(manager_id)
        
        if include_manager:
            manager = self.get_business_employee(manager_id)
            if manager:
                team.append(manager)
        
        if not team:
            logger.warning(f"No team members found for manager {manager_id}")
            return {"success": False, "reason": "No team members found"}
        
        # Create meeting stimulus
        meeting_prompt = f"""
        Team Meeting: {topic}
        
        This is a team meeting to discuss: {topic}
        
        Please participate actively by:
        - Sharing your perspective on the topic
        - Asking relevant questions
        - Providing constructive feedback
        - Contributing to action items and next steps
        
        Keep your responses focused and professional.
        """
        
        # Send meeting prompt to all team members
        for employee in team:
            await employee.async_listen(meeting_prompt)
        
        # Run meeting simulation
        rounds = 3  # Keep meetings focused
        await self.async_run(rounds)
        
        # Update business metrics
        self.business_metrics["meetings_completed"] += 1
        self.business_metrics["collaboration_events"] += len(team)
        
        logger.info(f"Completed team meeting for {manager_id} with {len(team)} participants")
        
        return {
            "success": True,
            "participants": [emp.name for emp in team],
            "topic": topic,
            "rounds": rounds
        }
    
    async def simulate_business_day(self, activities: List[str] = None) -> Dict[str, Any]:
        """Simulate a business day with various activities"""
        if not self.is_business_hours():
            logger.warning("Simulating business day outside of business hours")
        
        default_activities = [
            "Daily standup meeting",
            "Project work and collaboration", 
            "Status updates and planning"
        ]
        
        activities = activities or default_activities
        day_results = {"activities": [], "metrics": {}}
        
        for i, activity in enumerate(activities):
            logger.info(f"Business day activity {i+1}: {activity}")
            
            # Send activity to all employees
            activity_prompt = f"""
            Business Day Activity: {activity}
            
            As part of your regular workday, please engage with: {activity}
            
            Respond with how you would approach this activity based on your role,
            skills, and current priorities. Be specific about actions you would take.
            """
            
            # Send to all business employees
            business_employees = [agent for agent in self.agents 
                                if isinstance(agent, AsyncBusinessEmployee)]
            
            for employee in business_employees:
                await employee.async_listen(activity_prompt)
            
            # Run simulation rounds for this activity
            await self.async_run(2)
            
            activity_result = {
                "activity": activity,
                "participants": len(business_employees),
                "timestamp": datetime.now().isoformat()
            }
            day_results["activities"].append(activity_result)
            
            # Update metrics
            self.business_metrics["collaboration_events"] += len(business_employees)
        
        # Calculate daily productivity score
        total_employees = len([agent for agent in self.agents 
                             if isinstance(agent, AsyncBusinessEmployee)])
        if total_employees > 0:
            productivity = (self.business_metrics["collaboration_events"] / 
                          (total_employees * len(activities)))
            self.business_metrics["productivity_score"] = round(productivity, 2)
        
        day_results["metrics"] = self.business_metrics.copy()
        
        logger.info(f"Completed business day simulation with {len(activities)} activities")
        return day_results
    
    def get_business_analytics(self) -> Dict[str, Any]:
        """Get business simulation analytics"""
        business_employees = [agent for agent in self.agents 
                            if isinstance(agent, AsyncBusinessEmployee)]
        
        # Department breakdown
        dept_counts = {}
        for emp in business_employees:
            dept = emp.department
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        # Role breakdown  
        role_counts = {}
        for emp in business_employees:
            role = emp.role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Hierarchy analysis
        managers = [emp for emp in business_employees if emp.direct_reports]
        individual_contributors = [emp for emp in business_employees if not emp.direct_reports]
        
        return {
            "world_name": self.name,
            "total_employees": len(business_employees),
            "departments": dept_counts,
            "roles": role_counts,
            "managers": len(managers),
            "individual_contributors": len(individual_contributors),
            "business_metrics": self.business_metrics,
            "business_hours": {
                "start": self.business_hours_start.strftime("%H:%M"),
                "end": self.business_hours_end.strftime("%H:%M"),
                "currently_business_hours": self.is_business_hours()
            }
        }