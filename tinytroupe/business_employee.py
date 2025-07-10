"""
AsyncBusinessEmployee - Business extension of AsyncAdaptiveTinyPerson

Extends AsyncAdaptiveTinyPerson with essential business properties while
maintaining all existing adaptive and async capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from tinytroupe.async_adaptive_agent import AsyncAdaptiveTinyPerson

logger = logging.getLogger("tinytroupe.business")


class AsyncBusinessEmployee(AsyncAdaptiveTinyPerson):
    """
    Business employee that extends AsyncAdaptiveTinyPerson with essential business attributes.
    
    Maintains all existing async and adaptive capabilities while adding:
    - Employee ID and organizational position
    - Department and role information
    - Manager and direct report relationships
    - Basic business skills and performance data
    """
    
    def __init__(self, name: str, employee_id: str, role: str, department: str, 
                 manager_id: Optional[str] = None, **kwargs):
        """
        Initialize business employee with essential business properties.
        
        Args:
            name: Employee name
            employee_id: Unique employee identifier  
            role: Job title/role
            department: Department name
            manager_id: Manager's employee ID (optional)
            **kwargs: Additional arguments passed to AsyncAdaptiveTinyPerson
        """
        # Initialize _configuration before calling super().__init__ 
        # (required by TinyPerson.generate_agent_system_prompt during _post_init)
        self._configuration = {}
        
        super().__init__(name, **kwargs)
        
        # Core business properties
        self.employee_id = employee_id
        self.role = role
        self.department = department
        self.manager_id = manager_id
        self.direct_reports: List[str] = []
        
        # Basic business tracking
        self.business_skills: Dict[str, int] = {}
        self.performance_rating: str = "Not Rated"
        self.hire_date: Optional[datetime] = None
        
        # Set default occupation using define method
        self.define("occupation", f"You work as a {role} in the {department} department.")
        
        logger.debug(f"Created AsyncBusinessEmployee: {self.name} ({self.employee_id})")
    
    def add_direct_report(self, employee_id: str):
        """Add a direct report"""
        if employee_id not in self.direct_reports:
            self.direct_reports.append(employee_id)
    
    def remove_direct_report(self, employee_id: str):
        """Remove a direct report"""
        if employee_id in self.direct_reports:
            self.direct_reports.remove(employee_id)
    
    def update_business_skill(self, skill: str, level: int):
        """Update a business skill level (1-10)"""
        self.business_skills[skill] = max(1, min(10, level))
    
    def get_business_info(self) -> Dict[str, Any]:
        """Get summary of business information"""
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "role": self.role,
            "department": self.department,
            "manager_id": self.manager_id,
            "direct_reports": self.direct_reports,
            "business_skills": self.business_skills,
            "performance_rating": self.performance_rating,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None
        }


def create_business_employee(name: str, employee_id: str, role: str, department: str,
                           occupation: str = "", personality_traits: List[str] = None,
                           professional_interests: List[str] = None, skills: List[str] = None,
                           manager_id: Optional[str] = None, **kwargs) -> AsyncBusinessEmployee:
    """
    Factory function to create a business employee from basic parameters.
    
    Args:
        name: Employee name
        employee_id: Unique employee identifier
        role: Job title/role  
        department: Department name
        occupation: Detailed occupation description
        personality_traits: List of personality traits
        professional_interests: List of professional interests
        skills: List of skills
        manager_id: Manager's employee ID (optional)
        **kwargs: Additional arguments for AsyncAdaptiveTinyPerson
    
    Returns:
        AsyncBusinessEmployee instance
    """
    
    # Use role as occupation if not provided
    if not occupation:
        occupation = f"You work as a {role} in the {department} department."
    
    employee = AsyncBusinessEmployee(
        name=name,
        employee_id=employee_id,
        role=role,
        department=department,
        manager_id=manager_id,
        **kwargs
    )
    
    # Set basic attributes if provided
    if personality_traits:
        employee.define("personality_traits", personality_traits)
    
    if professional_interests:
        employee.define("professional_interests", professional_interests)
    
    if skills:
        employee.define("skills", skills)
    
    # Set occupation
    employee.define("occupation", occupation)
    
    return employee