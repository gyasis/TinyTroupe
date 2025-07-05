"""
Business Simulation Extension for TinyTroupe

This module provides a comprehensive business simulation framework that extends
TinyTroupe's existing capabilities with business-specific features including:
- Employee management and hiring database
- Organizational hierarchy and reporting structures
- Business task management and assignment
- Performance tracking and analytics
- Integration with AsyncAdaptiveTinyPerson and AsyncTinyWorld
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field
from pathlib import Path
import uuid

from tinytroupe.async_adaptive_agent import AsyncAdaptiveTinyPerson
from tinytroupe.async_world import AsyncTinyWorld
from tinytroupe.business_employee import AsyncBusinessEmployee, create_business_employee

logger = logging.getLogger("tinytroupe.business")


@dataclass
class BusinessEmployee:
    """Business employee data structure that extends agent persona with business attributes"""
    employee_id: str
    persona: Dict[str, Any]
    business_properties: Dict[str, Any]
    agent_instance: Optional[AsyncAdaptiveTinyPerson] = None
    
    @property
    def name(self) -> str:
        return self.persona.get("name", "Unknown Employee")
    
    @property
    def role(self) -> str:
        return self.business_properties.get("role", "Unknown Role")
    
    @property
    def department(self) -> str:
        return self.business_properties.get("department", "Unknown Department")
    
    @property
    def manager_id(self) -> Optional[str]:
        return self.business_properties.get("manager_id")
    
    @property
    def direct_reports(self) -> List[str]:
        return self.business_properties.get("direct_reports", [])
    
    @property
    def salary(self) -> int:
        return self.business_properties.get("salary", 0)
    
    @property
    def hire_date(self) -> str:
        return self.business_properties.get("hire_date", "")
    
    @property
    def performance_rating(self) -> str:
        return self.business_properties.get("performance_rating", "Not Rated")
    
    @property
    def business_skills(self) -> Dict[str, int]:
        return self.business_properties.get("business_skills", {})


@dataclass
class HiringEvent:
    """Record of a hiring event"""
    employee_id: str
    hire_date: datetime
    role: str
    department: str
    salary: int
    hiring_manager: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class PerformanceReview:
    """Performance review record"""
    employee_id: str
    review_date: datetime
    reviewer_id: str
    rating: str
    goals: List[str]
    achievements: List[str]
    development_areas: List[str]
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class HiringDatabase:
    """
    Comprehensive employee management system for the business simulation.
    
    Manages employee lifecycle, organizational structure, and business analytics.
    Integrates with TinyTroupe's agent system to create business employees.
    """
    
    def __init__(self, employee_directory: str = "employees"):
        self.employee_directory = Path(employee_directory)
        self.employees: Dict[str, BusinessEmployee] = {}
        self.hiring_events: List[HiringEvent] = []
        self.performance_reviews: List[PerformanceReview] = []
        self.organizational_chart: Dict[str, Set[str]] = {}  # manager_id -> set of direct_reports
        
        # Load existing employees
        self.load_employees()
        self._build_org_chart()
    
    def load_employees(self):
        """Load all employees from the employee directory"""
        if not self.employee_directory.exists():
            logger.warning(f"Employee directory {self.employee_directory} does not exist")
            return
        
        for employee_file in self.employee_directory.glob("*.employee.json"):
            try:
                with open(employee_file, 'r') as f:
                    employee_data = json.load(f)
                
                # Validate employee data structure
                if not self._validate_employee_data(employee_data):
                    logger.error(f"Invalid employee data in {employee_file}")
                    continue
                
                business_props = employee_data.get("business_properties", {})
                employee_id = business_props.get("employee_id")
                
                if not employee_id:
                    logger.error(f"Missing employee_id in {employee_file}")
                    continue
                
                employee = BusinessEmployee(
                    employee_id=employee_id,
                    persona=employee_data.get("persona", {}),
                    business_properties=business_props
                )
                
                self.employees[employee_id] = employee
                logger.debug(f"Loaded employee: {employee.name} ({employee_id})")
                
            except Exception as e:
                logger.error(f"Error loading employee from {employee_file}: {e}")
    
    def _validate_employee_data(self, data: Dict[str, Any]) -> bool:
        """Validate employee data structure"""
        required_fields = ["persona", "business_properties"]
        if not all(field in data for field in required_fields):
            return False
        
        business_props = data["business_properties"]
        required_business_fields = ["employee_id", "role", "department", "hire_date"]
        if not all(field in business_props for field in required_business_fields):
            return False
        
        return True
    
    def _build_org_chart(self):
        """Build organizational chart from employee data"""
        self.organizational_chart.clear()
        
        for employee in self.employees.values():
            manager_id = employee.manager_id
            if manager_id:
                if manager_id not in self.organizational_chart:
                    self.organizational_chart[manager_id] = set()
                self.organizational_chart[manager_id].add(employee.employee_id)
    
    async def create_agent(self, employee_id: str) -> Optional[AsyncBusinessEmployee]:
        """Create an AsyncBusinessEmployee from employee data"""
        if employee_id not in self.employees:
            logger.error(f"Employee {employee_id} not found")
            return None
        
        employee = self.employees[employee_id]
        persona = employee.persona
        business_props = employee.business_properties
        
        # Create business employee using factory function
        agent = create_business_employee(
            name=persona.get("name", "Unknown"),
            employee_id=employee_id,
            role=business_props.get("role", "Unknown Role"),
            department=business_props.get("department", "Unknown Department"),
            occupation=persona.get("occupation", {}).get("description", ""),
            personality_traits=persona.get("personality", {}).get("traits", []),
            professional_interests=persona.get("preferences", {}).get("interests", []),
            skills=persona.get("skills", []),
            manager_id=business_props.get("manager_id")
        )
        
        # Set additional business properties
        agent.direct_reports = business_props.get("direct_reports", [])
        agent.business_skills = business_props.get("business_skills", {})
        agent.performance_rating = business_props.get("performance_rating", "Not Rated")
        
        if business_props.get("hire_date"):
            agent.hire_date = datetime.fromisoformat(business_props["hire_date"])
        
        # Store agent reference
        employee.agent_instance = agent
        
        logger.info(f"Created business agent for employee: {employee.name} ({employee_id})")
        return agent
    
    def get_employee(self, employee_id: str) -> Optional[BusinessEmployee]:
        """Get employee by ID"""
        return self.employees.get(employee_id)
    
    def get_employees_by_department(self, department: str) -> List[BusinessEmployee]:
        """Get all employees in a specific department"""
        return [emp for emp in self.employees.values() 
                if emp.department.lower() == department.lower()]
    
    def get_employees_by_role(self, role: str) -> List[BusinessEmployee]:
        """Get all employees with a specific role"""
        return [emp for emp in self.employees.values() 
                if role.lower() in emp.role.lower()]
    
    def get_direct_reports(self, manager_id: str) -> List[BusinessEmployee]:
        """Get all direct reports for a manager"""
        direct_report_ids = self.organizational_chart.get(manager_id, set())
        return [self.employees[emp_id] for emp_id in direct_report_ids 
                if emp_id in self.employees]
    
    def get_team_hierarchy(self, manager_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """Get hierarchical team structure under a manager"""
        def build_hierarchy(emp_id: str, depth: int) -> Dict[str, Any]:
            if depth >= max_depth or emp_id not in self.employees:
                return {}
            
            employee = self.employees[emp_id]
            hierarchy = {
                "employee": employee,
                "reports": {}
            }
            
            for report_id in self.organizational_chart.get(emp_id, set()):
                hierarchy["reports"][report_id] = build_hierarchy(report_id, depth + 1)
            
            return hierarchy
        
        return build_hierarchy(manager_id, 0)
    
    def hire_employee(self, employee_data: Dict[str, Any], hiring_manager: str) -> str:
        """Hire a new employee and add to database"""
        business_props = employee_data.get("business_properties", {})
        employee_id = business_props.get("employee_id", str(uuid.uuid4()))
        
        # Create employee record
        employee = BusinessEmployee(
            employee_id=employee_id,
            persona=employee_data.get("persona", {}),
            business_properties=business_props
        )
        
        self.employees[employee_id] = employee
        
        # Record hiring event
        hire_event = HiringEvent(
            employee_id=employee_id,
            hire_date=datetime.fromisoformat(business_props.get("hire_date", datetime.now().isoformat())),
            role=business_props.get("role", ""),
            department=business_props.get("department", ""),
            salary=business_props.get("salary", 0),
            hiring_manager=hiring_manager
        )
        
        self.hiring_events.append(hire_event)
        self._build_org_chart()  # Rebuild org chart
        
        logger.info(f"Hired new employee: {employee.name} ({employee_id})")
        return employee_id
    
    def conduct_performance_review(self, employee_id: str, reviewer_id: str, 
                                 rating: str, goals: List[str] = None, 
                                 achievements: List[str] = None, 
                                 development_areas: List[str] = None) -> str:
        """Conduct a performance review for an employee"""
        if employee_id not in self.employees:
            raise ValueError(f"Employee {employee_id} not found")
        
        review = PerformanceReview(
            employee_id=employee_id,
            review_date=datetime.now(),
            reviewer_id=reviewer_id,
            rating=rating,
            goals=goals or [],
            achievements=achievements or [],
            development_areas=development_areas or []
        )
        
        self.performance_reviews.append(review)
        
        # Update employee's performance rating
        self.employees[employee_id].business_properties["performance_rating"] = rating
        
        logger.info(f"Performance review completed for {employee_id} by {reviewer_id}")
        return review.review_id
    
    def get_department_analytics(self, department: str) -> Dict[str, Any]:
        """Get analytics for a specific department"""
        dept_employees = self.get_employees_by_department(department)
        
        if not dept_employees:
            return {"error": f"No employees found in department {department}"}
        
        total_employees = len(dept_employees)
        total_salary = sum(emp.salary for emp in dept_employees)
        avg_salary = total_salary / total_employees if total_employees > 0 else 0
        
        # Performance distribution
        performance_dist = {}
        for emp in dept_employees:
            rating = emp.performance_rating
            performance_dist[rating] = performance_dist.get(rating, 0) + 1
        
        # Tenure analysis
        current_date = datetime.now()
        tenures = []
        for emp in dept_employees:
            if emp.hire_date:
                hire_date = datetime.fromisoformat(emp.hire_date)
                tenure_years = (current_date - hire_date).days / 365.25
                tenures.append(tenure_years)
        
        avg_tenure = sum(tenures) / len(tenures) if tenures else 0
        
        return {
            "department": department,
            "total_employees": total_employees,
            "total_salary_cost": total_salary,
            "average_salary": avg_salary,
            "performance_distribution": performance_dist,
            "average_tenure_years": round(avg_tenure, 2),
            "employees": [{"id": emp.employee_id, "name": emp.name, "role": emp.role} 
                         for emp in dept_employees]
        }
    
    def get_company_analytics(self) -> Dict[str, Any]:
        """Get company-wide analytics"""
        total_employees = len(self.employees)
        departments = list(set(emp.department for emp in self.employees.values()))
        
        # Department breakdown
        dept_breakdown = {}
        for dept in departments:
            dept_breakdown[dept] = len(self.get_employees_by_department(dept))
        
        # Salary analytics
        salaries = [emp.salary for emp in self.employees.values()]
        total_salary_cost = sum(salaries)
        avg_salary = total_salary_cost / total_employees if total_employees > 0 else 0
        
        # Recent hires (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_hires = [event for event in self.hiring_events 
                       if event.hire_date >= thirty_days_ago]
        
        return {
            "total_employees": total_employees,
            "departments": dept_breakdown,
            "total_salary_cost": total_salary_cost,
            "average_salary": round(avg_salary, 2),
            "recent_hires_30_days": len(recent_hires),
            "total_hiring_events": len(self.hiring_events),
            "total_performance_reviews": len(self.performance_reviews)
        }
    
    def export_org_chart(self, format: str = "json") -> Union[Dict[str, Any], str]:
        """Export organizational chart in specified format"""
        if format == "json":
            # Find top-level managers (those without managers)
            top_level = [emp_id for emp_id, emp in self.employees.items() 
                        if not emp.manager_id]
            
            org_chart = {}
            for manager_id in top_level:
                org_chart[manager_id] = self.get_team_hierarchy(manager_id)
            
            # Convert to JSON-serializable format
            def make_serializable(obj):
                if hasattr(obj, '__dict__'):
                    return {k: make_serializable(v) for k, v in obj.__dict__.items()}
                elif isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [make_serializable(item) for item in obj]
                else:
                    return obj
            
            return make_serializable(org_chart)
        
        elif format == "text":
            # Simple text representation
            lines = ["Organizational Chart", "=" * 20, ""]
            
            def add_employee_tree(emp_id: str, indent: int = 0):
                if emp_id not in self.employees:
                    return
                
                employee = self.employees[emp_id]
                prefix = "  " * indent + ("├─ " if indent > 0 else "")
                lines.append(f"{prefix}{employee.name} ({employee.role})")
                
                for report_id in self.organizational_chart.get(emp_id, set()):
                    add_employee_tree(report_id, indent + 1)
            
            # Start with top-level managers
            top_level = [emp_id for emp_id, emp in self.employees.items() 
                        if not emp.manager_id]
            
            for manager_id in top_level:
                add_employee_tree(manager_id)
                lines.append("")  # Add spacing between top-level trees
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def save_database(self, filepath: str):
        """Save hiring database to file"""
        data = {
            "employees": {emp_id: {
                "employee_id": emp.employee_id,
                "persona": emp.persona,
                "business_properties": emp.business_properties
            } for emp_id, emp in self.employees.items()},
            "hiring_events": [
                {
                    "event_id": event.event_id,
                    "employee_id": event.employee_id,
                    "hire_date": event.hire_date.isoformat(),
                    "role": event.role,
                    "department": event.department,
                    "salary": event.salary,
                    "hiring_manager": event.hiring_manager
                }
                for event in self.hiring_events
            ],
            "performance_reviews": [
                {
                    "review_id": review.review_id,
                    "employee_id": review.employee_id,
                    "review_date": review.review_date.isoformat(),
                    "reviewer_id": review.reviewer_id,
                    "rating": review.rating,
                    "goals": review.goals,
                    "achievements": review.achievements,
                    "development_areas": review.development_areas
                }
                for review in self.performance_reviews
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Hiring database saved to {filepath}")