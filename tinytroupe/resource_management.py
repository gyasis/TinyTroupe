"""
Resource Management System - Budget, Time, and Equipment Tracking

This module provides comprehensive resource management capabilities for the Virtual Business Simulation:
- Budget tracking and allocation
- Time allocation monitoring  
- Equipment assignment and utilization
- Resource conflict detection and resolution
- Cost center management
- Resource optimization recommendations
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

from tinytroupe.task_management import TaskManager, BusinessTask
from tinytroupe.business_simulation import HiringDatabase

logger = logging.getLogger("tinytroupe.resource_management")


class ResourceType(Enum):
    """Types of resources that can be managed"""
    BUDGET = "budget"
    TIME = "time"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    PERSONNEL = "personnel"
    SPACE = "space"


class AllocationStatus(Enum):
    """Status of resource allocations"""
    PLANNED = "planned"
    ALLOCATED = "allocated"
    IN_USE = "in_use"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERRUN = "overrun"


class ResourceConflictType(Enum):
    """Types of resource conflicts"""
    DOUBLE_ALLOCATION = "double_allocation"
    INSUFFICIENT_BUDGET = "insufficient_budget"
    EQUIPMENT_UNAVAILABLE = "equipment_unavailable"
    OVER_CAPACITY = "over_capacity"
    TIME_CONFLICT = "time_conflict"


@dataclass
class Resource:
    """Represents a resource in the system"""
    resource_id: str
    name: str
    resource_type: ResourceType
    description: str = ""
    
    # Capacity and availability
    total_capacity: float = 0.0
    available_capacity: float = 0.0
    unit: str = ""  # "hours", "USD", "units", etc.
    
    # Cost information
    unit_cost: float = 0.0
    total_value: float = 0.0
    
    # Metadata
    location: Optional[str] = None
    department: Optional[str] = None
    managed_by: Optional[str] = None
    created_date: datetime = field(default_factory=datetime.now)
    
    # Status tracking
    is_active: bool = True
    maintenance_schedule: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_utilization_percentage(self) -> float:
        """Calculate resource utilization percentage"""
        if self.total_capacity > 0:
            used_capacity = self.total_capacity - self.available_capacity
            return (used_capacity / self.total_capacity) * 100
        return 0.0
    
    def is_available(self, required_amount: float) -> bool:
        """Check if resource has required capacity available"""
        return self.available_capacity >= required_amount


@dataclass
class ResourceAllocation:
    """Represents an allocation of resources to a task/project"""
    allocation_id: str
    resource_id: str
    allocated_to: str  # task_id, project_id, or employee_id
    allocated_by: str  # employee_id who made the allocation
    
    # Allocation details
    allocated_amount: float
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_days: Optional[int] = None
    
    # Cost tracking
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    
    # Status and tracking
    status: AllocationStatus = AllocationStatus.PLANNED
    purpose: str = ""
    notes: str = ""
    
    # Approval workflow
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    
    # Time tracking
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate duration if end_date is provided"""
        if self.end_date and not self.duration_days:
            self.duration_days = (self.end_date - self.start_date).days + 1
        elif self.duration_days and not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.duration_days - 1)
    
    def get_daily_cost(self) -> float:
        """Calculate daily cost of this allocation"""
        if self.duration_days and self.duration_days > 0:
            return self.estimated_cost / self.duration_days
        return self.estimated_cost
    
    def is_overrun(self) -> bool:
        """Check if allocation is over budget"""
        return self.actual_cost > self.estimated_cost * 1.1  # 10% tolerance


@dataclass
class ResourceConflict:
    """Represents a resource conflict"""
    conflict_id: str
    conflict_type: ResourceConflictType
    resource_id: str
    conflicting_allocations: List[str]
    detected_date: datetime
    severity: str  # "low", "medium", "high", "critical"
    description: str
    impact_assessment: str
    suggested_resolution: str
    
    # Resolution tracking
    is_resolved: bool = False
    resolved_by: Optional[str] = None
    resolution_date: Optional[datetime] = None
    resolution_notes: str = ""


@dataclass
class BudgetCategory:
    """Budget category for tracking expenses"""
    category_id: str
    name: str
    department: str
    total_budget: float
    allocated_budget: float = 0.0
    spent_budget: float = 0.0
    
    # Time period
    fiscal_year: int = datetime.now().year
    fiscal_quarter: Optional[int] = None
    
    # Approval limits
    approval_threshold: float = 1000.0  # Amount requiring approval
    approver_id: Optional[str] = None
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget amount"""
        return self.total_budget - self.allocated_budget
    
    def get_budget_utilization(self) -> float:
        """Get budget utilization percentage"""
        if self.total_budget > 0:
            return (self.allocated_budget / self.total_budget) * 100
        return 0.0
    
    def is_over_budget(self) -> bool:
        """Check if category is over budget"""
        return self.allocated_budget > self.total_budget


class ResourceManagementSystem:
    """
    Comprehensive Resource Management System for Virtual Business Simulation
    
    Manages budgets, equipment, time allocation, and other business resources.
    """
    
    def __init__(self, task_manager: TaskManager, hiring_database: HiringDatabase):
        self.task_manager = task_manager
        self.hiring_database = hiring_database
        
        # Resource storage
        self.resources: Dict[str, Resource] = {}
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.budget_categories: Dict[str, BudgetCategory] = {}
        
        # Conflict tracking
        self.conflicts: List[ResourceConflict] = []
        self.conflict_counter = 0
        
        # Cost centers and departments
        self.cost_centers: Dict[str, Dict[str, Any]] = {}
        
        # Approval workflows
        self.pending_approvals: List[str] = []  # allocation_ids
        
        # Initialize default resources
        asyncio.create_task(self._setup_default_resources())
    
    async def _setup_default_resources(self):
        """Setup default resources for the simulation"""
        # Default budget categories
        await self.create_budget_category(
            name="Engineering",
            department="Engineering", 
            total_budget=500000.0,
            approval_threshold=5000.0
        )
        
        await self.create_budget_category(
            name="Marketing",
            department="Marketing",
            total_budget=200000.0,
            approval_threshold=2000.0
        )
        
        await self.create_budget_category(
            name="Operations",
            department="Operations",
            total_budget=150000.0,
            approval_threshold=3000.0
        )
        
        # Default equipment resources
        await self.create_resource(
            name="Development Laptops",
            resource_type=ResourceType.EQUIPMENT,
            total_capacity=20.0,
            unit="units",
            unit_cost=2000.0,
            department="Engineering"
        )
        
        await self.create_resource(
            name="Conference Room A",
            resource_type=ResourceType.SPACE,
            total_capacity=8.0,
            unit="hours",
            department="General"
        )
        
        await self.create_resource(
            name="Cloud Computing Credits",
            resource_type=ResourceType.SOFTWARE,
            total_capacity=10000.0,
            unit="USD",
            unit_cost=1.0,
            department="Engineering"
        )
    
    async def create_resource(self, name: str, resource_type: ResourceType,
                            total_capacity: float, unit: str,
                            unit_cost: float = 0.0, department: str = "General",
                            description: str = "") -> str:
        """Create a new resource"""
        resource_id = f"resource_{uuid.uuid4().hex[:8]}"
        
        resource = Resource(
            resource_id=resource_id,
            name=name,
            resource_type=resource_type,
            description=description,
            total_capacity=total_capacity,
            available_capacity=total_capacity,
            unit=unit,
            unit_cost=unit_cost,
            total_value=total_capacity * unit_cost,
            department=department
        )
        
        self.resources[resource_id] = resource
        logger.info(f"Created resource: {name} ({resource_id})")
        return resource_id
    
    async def create_budget_category(self, name: str, department: str,
                                   total_budget: float, approval_threshold: float = 1000.0,
                                   fiscal_year: int = None) -> str:
        """Create a budget category"""
        if fiscal_year is None:
            fiscal_year = datetime.now().year
        
        category_id = f"budget_{uuid.uuid4().hex[:8]}"
        
        category = BudgetCategory(
            category_id=category_id,
            name=name,
            department=department,
            total_budget=total_budget,
            fiscal_year=fiscal_year,
            approval_threshold=approval_threshold
        )
        
        self.budget_categories[category_id] = category
        logger.info(f"Created budget category: {name} (${total_budget:,.2f})")
        return category_id
    
    async def allocate_resource(self, resource_id: str, allocated_to: str,
                              allocated_amount: float, allocated_by: str,
                              start_date: datetime, duration_days: int,
                              purpose: str = "", requires_approval: bool = False) -> Optional[str]:
        """Allocate a resource to a task/project"""
        if resource_id not in self.resources:
            logger.error(f"Resource {resource_id} not found")
            return None
        
        resource = self.resources[resource_id]
        
        # Check availability
        if not resource.is_available(allocated_amount):
            logger.warning(f"Insufficient capacity for resource {resource_id}")
            return None
        
        allocation_id = f"allocation_{uuid.uuid4().hex[:8]}"
        end_date = start_date + timedelta(days=duration_days - 1)
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            resource_id=resource_id,
            allocated_to=allocated_to,
            allocated_by=allocated_by,
            allocated_amount=allocated_amount,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            estimated_cost=allocated_amount * resource.unit_cost * duration_days,
            purpose=purpose,
            requires_approval=requires_approval
        )
        
        # Check for conflicts
        conflicts = await self._detect_resource_conflicts(allocation)
        if conflicts:
            logger.warning(f"Resource conflicts detected for allocation {allocation_id}")
            for conflict in conflicts:
                self.conflicts.append(conflict)
        
        # Store allocation
        self.allocations[allocation_id] = allocation
        
        # Update resource availability
        resource.available_capacity -= allocated_amount
        
        # Add to approval queue if required
        if requires_approval:
            self.pending_approvals.append(allocation_id)
            allocation.status = AllocationStatus.PLANNED
        else:
            allocation.status = AllocationStatus.ALLOCATED
        
        logger.info(f"Resource allocated: {resource.name} -> {allocated_to}")
        return allocation_id
    
    async def allocate_budget(self, category_id: str, amount: float,
                            allocated_to: str, allocated_by: str,
                            purpose: str = "") -> Optional[str]:
        """Allocate budget from a category"""
        if category_id not in self.budget_categories:
            logger.error(f"Budget category {category_id} not found")
            return None
        
        category = self.budget_categories[category_id]
        
        # Check if budget is available
        if category.get_remaining_budget() < amount:
            logger.warning(f"Insufficient budget in category {category.name}")
            return None
        
        # Check if approval is required
        requires_approval = amount >= category.approval_threshold
        
        # Create allocation (using budget as a resource)
        allocation_id = await self.allocate_resource(
            resource_id=f"budget_{category_id}",
            allocated_to=allocated_to,
            allocated_amount=amount,
            allocated_by=allocated_by,
            start_date=datetime.now(),
            duration_days=1,  # Budget allocations are typically instantaneous
            purpose=purpose,
            requires_approval=requires_approval
        )
        
        if allocation_id:
            # Update budget category
            category.allocated_budget += amount
        
        return allocation_id
    
    async def approve_allocation(self, allocation_id: str, approved_by: str) -> bool:
        """Approve a pending resource allocation"""
        if allocation_id not in self.allocations:
            return False
        
        allocation = self.allocations[allocation_id]
        
        if allocation.status != AllocationStatus.PLANNED:
            logger.warning(f"Allocation {allocation_id} is not pending approval")
            return False
        
        allocation.approved_by = approved_by
        allocation.approval_date = datetime.now()
        allocation.status = AllocationStatus.ALLOCATED
        allocation.last_updated = datetime.now()
        
        # Remove from pending approvals
        if allocation_id in self.pending_approvals:
            self.pending_approvals.remove(allocation_id)
        
        logger.info(f"Allocation {allocation_id} approved by {approved_by}")
        return True
    
    async def start_resource_usage(self, allocation_id: str) -> bool:
        """Mark resource allocation as in use"""
        if allocation_id not in self.allocations:
            return False
        
        allocation = self.allocations[allocation_id]
        
        if allocation.status != AllocationStatus.ALLOCATED:
            logger.warning(f"Allocation {allocation_id} is not ready for use")
            return False
        
        allocation.status = AllocationStatus.IN_USE
        allocation.last_updated = datetime.now()
        
        logger.info(f"Resource usage started for allocation {allocation_id}")
        return True
    
    async def complete_resource_usage(self, allocation_id: str, actual_cost: float = None) -> bool:
        """Complete resource usage and update costs"""
        if allocation_id not in self.allocations:
            return False
        
        allocation = self.allocations[allocation_id]
        resource = self.resources.get(allocation.resource_id)
        
        if allocation.status != AllocationStatus.IN_USE:
            logger.warning(f"Allocation {allocation_id} is not currently in use")
            return False
        
        # Update status
        allocation.status = AllocationStatus.COMPLETED
        allocation.last_updated = datetime.now()
        
        # Update actual cost
        if actual_cost is not None:
            allocation.actual_cost = actual_cost
        else:
            allocation.actual_cost = allocation.estimated_cost
        
        # Return resource capacity
        if resource:
            resource.available_capacity += allocation.allocated_amount
        
        # Check for cost overruns
        if allocation.is_overrun():
            await self._create_overrun_alert(allocation)
        
        logger.info(f"Resource usage completed for allocation {allocation_id}")
        return True
    
    async def get_resource_utilization(self, resource_id: str = None,
                                     department: str = None) -> Dict[str, Any]:
        """Get resource utilization statistics"""
        if resource_id:
            resources = [self.resources[resource_id]] if resource_id in self.resources else []
        else:
            resources = list(self.resources.values())
        
        if department:
            resources = [r for r in resources if r.department == department]
        
        utilization_data = {
            "total_resources": len(resources),
            "average_utilization": 0.0,
            "high_utilization": [],  # >80% utilization
            "low_utilization": [],   # <20% utilization
            "by_type": {},
            "by_department": {}
        }
        
        if not resources:
            return utilization_data
        
        total_utilization = 0.0
        
        for resource in resources:
            utilization = resource.get_utilization_percentage()
            total_utilization += utilization
            
            # Track high/low utilization
            if utilization > 80:
                utilization_data["high_utilization"].append({
                    "resource_id": resource.resource_id,
                    "name": resource.name,
                    "utilization": utilization
                })
            elif utilization < 20:
                utilization_data["low_utilization"].append({
                    "resource_id": resource.resource_id,
                    "name": resource.name,
                    "utilization": utilization
                })
            
            # By type
            resource_type = resource.resource_type.value
            if resource_type not in utilization_data["by_type"]:
                utilization_data["by_type"][resource_type] = {
                    "count": 0, "total_utilization": 0.0
                }
            utilization_data["by_type"][resource_type]["count"] += 1
            utilization_data["by_type"][resource_type]["total_utilization"] += utilization
            
            # By department
            dept = resource.department or "Unknown"
            if dept not in utilization_data["by_department"]:
                utilization_data["by_department"][dept] = {
                    "count": 0, "total_utilization": 0.0
                }
            utilization_data["by_department"][dept]["count"] += 1
            utilization_data["by_department"][dept]["total_utilization"] += utilization
        
        # Calculate averages
        utilization_data["average_utilization"] = total_utilization / len(resources)
        
        for type_data in utilization_data["by_type"].values():
            if type_data["count"] > 0:
                type_data["average_utilization"] = type_data["total_utilization"] / type_data["count"]
        
        for dept_data in utilization_data["by_department"].values():
            if dept_data["count"] > 0:
                dept_data["average_utilization"] = dept_data["total_utilization"] / dept_data["count"]
        
        return utilization_data
    
    async def get_budget_status(self, department: str = None) -> Dict[str, Any]:
        """Get comprehensive budget status"""
        categories = list(self.budget_categories.values())
        
        if department:
            categories = [c for c in categories if c.department == department]
        
        status = {
            "total_categories": len(categories),
            "total_budget": 0.0,
            "allocated_budget": 0.0,
            "spent_budget": 0.0,
            "remaining_budget": 0.0,
            "over_budget_categories": [],
            "low_budget_categories": [],  # <10% remaining
            "categories": []
        }
        
        for category in categories:
            status["total_budget"] += category.total_budget
            status["allocated_budget"] += category.allocated_budget
            status["spent_budget"] += category.spent_budget
            
            remaining = category.get_remaining_budget()
            utilization = category.get_budget_utilization()
            
            category_info = {
                "category_id": category.category_id,
                "name": category.name,
                "department": category.department,
                "total_budget": category.total_budget,
                "allocated_budget": category.allocated_budget,
                "remaining_budget": remaining,
                "utilization_percentage": utilization
            }
            
            status["categories"].append(category_info)
            
            # Track problematic categories
            if category.is_over_budget():
                status["over_budget_categories"].append(category_info)
            elif remaining / category.total_budget < 0.1:  # <10% remaining
                status["low_budget_categories"].append(category_info)
        
        status["remaining_budget"] = status["total_budget"] - status["allocated_budget"]
        
        return status
    
    async def get_resource_conflicts(self, resolved: bool = False) -> List[ResourceConflict]:
        """Get resource conflicts"""
        return [c for c in self.conflicts if c.is_resolved == resolved]
    
    async def resolve_conflict(self, conflict_id: str, resolved_by: str, 
                             resolution_notes: str = "") -> bool:
        """Resolve a resource conflict"""
        for conflict in self.conflicts:
            if conflict.conflict_id == conflict_id:
                conflict.is_resolved = True
                conflict.resolved_by = resolved_by
                conflict.resolution_date = datetime.now()
                conflict.resolution_notes = resolution_notes
                
                logger.info(f"Conflict {conflict_id} resolved by {resolved_by}")
                return True
        
        return False
    
    async def generate_resource_recommendations(self) -> List[Dict[str, Any]]:
        """Generate resource optimization recommendations"""
        recommendations = []
        
        # Analyze resource utilization
        utilization = await self.get_resource_utilization()
        
        # High utilization recommendations
        for resource_info in utilization["high_utilization"]:
            recommendations.append({
                "type": "capacity_expansion",
                "priority": "high",
                "resource_id": resource_info["resource_id"],
                "resource_name": resource_info["resource_name"],
                "current_utilization": resource_info["utilization"],
                "recommendation": f"Consider increasing capacity for {resource_info['resource_name']} (currently {resource_info['utilization']:.1f}% utilized)",
                "impact": "Reduce bottlenecks and improve productivity"
            })
        
        # Low utilization recommendations
        for resource_info in utilization["low_utilization"]:
            recommendations.append({
                "type": "capacity_reduction",
                "priority": "medium",
                "resource_id": resource_info["resource_id"],
                "resource_name": resource_info["resource_name"],
                "current_utilization": resource_info["utilization"],
                "recommendation": f"Consider reducing capacity or reallocating {resource_info['resource_name']} (currently {resource_info['utilization']:.1f}% utilized)",
                "impact": "Reduce costs and improve resource efficiency"
            })
        
        # Budget recommendations
        budget_status = await self.get_budget_status()
        for category in budget_status["over_budget_categories"]:
            recommendations.append({
                "type": "budget_adjustment",
                "priority": "critical",
                "category_id": category["category_id"],
                "category_name": category["name"],
                "current_utilization": category["utilization_percentage"],
                "recommendation": f"Budget category '{category['name']}' is over budget - review allocations",
                "impact": "Prevent budget overruns and maintain financial control"
            })
        
        return recommendations
    
    async def _detect_resource_conflicts(self, new_allocation: ResourceAllocation) -> List[ResourceConflict]:
        """Detect conflicts for a new resource allocation"""
        conflicts = []
        
        # Check for double allocation of equipment/space
        resource = self.resources.get(new_allocation.resource_id)
        if not resource:
            return conflicts
        
        if resource.resource_type in [ResourceType.EQUIPMENT, ResourceType.SPACE]:
            # Check for overlapping time periods
            for allocation_id, existing_allocation in self.allocations.items():
                if (existing_allocation.resource_id == new_allocation.resource_id and
                    existing_allocation.status in [AllocationStatus.ALLOCATED, AllocationStatus.IN_USE]):
                    
                    # Check time overlap
                    if self._allocations_overlap(existing_allocation, new_allocation):
                        conflict = ResourceConflict(
                            conflict_id=f"conflict_{self.conflict_counter}",
                            conflict_type=ResourceConflictType.DOUBLE_ALLOCATION,
                            resource_id=new_allocation.resource_id,
                            conflicting_allocations=[existing_allocation.allocation_id, new_allocation.allocation_id],
                            detected_date=datetime.now(),
                            severity="high",
                            description=f"Double allocation of {resource.name}",
                            impact_assessment="Resource unavailable for one of the conflicting allocations",
                            suggested_resolution="Reschedule one allocation or find alternative resource"
                        )
                        conflicts.append(conflict)
                        self.conflict_counter += 1
        
        return conflicts
    
    def _allocations_overlap(self, allocation1: ResourceAllocation, allocation2: ResourceAllocation) -> bool:
        """Check if two allocations overlap in time"""
        start1, end1 = allocation1.start_date, allocation1.end_date
        start2, end2 = allocation2.start_date, allocation2.end_date
        
        if not end1 or not end2:
            return False
        
        return start1 <= end2 and start2 <= end1
    
    async def _create_overrun_alert(self, allocation: ResourceAllocation):
        """Create alert for cost overruns"""
        resource = self.resources.get(allocation.resource_id)
        overrun_amount = allocation.actual_cost - allocation.estimated_cost
        overrun_percentage = (overrun_amount / allocation.estimated_cost) * 100
        
        logger.warning(f"Cost overrun detected: {allocation.allocation_id} "
                      f"(${overrun_amount:,.2f}, {overrun_percentage:.1f}%)")


# Convenience factory function
def create_resource_management_system(task_manager: TaskManager, 
                                    hiring_database: HiringDatabase) -> ResourceManagementSystem:
    """Create a resource management system with standard configuration"""
    return ResourceManagementSystem(task_manager, hiring_database)