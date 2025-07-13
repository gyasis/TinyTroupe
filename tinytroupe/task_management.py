"""
Comprehensive Task Management System for Virtual Business Simulation

This module provides a complete task management framework that supports:
- Task creation with priorities, deadlines, and dependencies
- Automated and manual task assignment
- Hierarchical delegation and escalation
- Resource allocation and tracking
- Performance metrics and analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger("tinytroupe.tasks")


class TaskStatus(Enum):
    """Task status enumeration"""
    TO_DO = "to_do"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TaskPriority(Enum):
    """Task priority enumeration"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINOR = 1


class TaskComplexity(Enum):
    """Task complexity levels"""
    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    EXPERT = 5


@dataclass
class TaskResource:
    """Resource allocation for tasks"""
    resource_type: str  # "budget", "time", "equipment", "personnel"
    amount: float
    unit: str  # "USD", "hours", "units", "people"
    allocated_date: datetime = field(default_factory=datetime.now)
    consumed: float = 0.0
    
    @property
    def remaining(self) -> float:
        return max(0, self.amount - self.consumed)
    
    @property
    def utilization_percentage(self) -> float:
        return (self.consumed / self.amount * 100) if self.amount > 0 else 0


@dataclass 
class TaskUpdate:
    """Task status update record"""
    update_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    updater_id: str = ""
    old_status: TaskStatus = TaskStatus.TO_DO
    new_status: TaskStatus = TaskStatus.TO_DO
    notes: str = ""
    time_spent: Optional[float] = None  # hours


@dataclass
class BusinessTask:
    """
    Comprehensive business task with all necessary attributes for realistic simulation.
    
    Supports the PRD requirements for automated assignment, hierarchical delegation,
    CEO oversight, and business day simulation.
    """
    
    # Core task identification
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    
    # Assignment and ownership
    assigned_to: Optional[str] = None  # employee_id
    created_by: str = ""  # employee_id or "CEO"
    delegated_by: Optional[str] = None  # employee_id for hierarchical delegation
    
    # Scheduling and timing
    created_date: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    estimated_hours: float = 1.0
    actual_hours: float = 0.0
    
    # Classification and requirements
    priority: TaskPriority = TaskPriority.MEDIUM
    complexity: TaskComplexity = TaskComplexity.MODERATE
    status: TaskStatus = TaskStatus.TO_DO
    required_skills: List[str] = field(default_factory=list)
    minimum_skill_level: int = 1  # 1-10 scale
    
    # Dependencies and relationships
    dependencies: List[str] = field(default_factory=list)  # task_ids that must complete first
    blocks: List[str] = field(default_factory=list)  # task_ids that depend on this task
    parent_task: Optional[str] = None  # for subtasks
    subtasks: List[str] = field(default_factory=list)
    project_id: Optional[str] = None
    
    # Resources and tracking
    resources: List[TaskResource] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    updates: List[TaskUpdate] = field(default_factory=list)
    
    # Business context
    department: Optional[str] = None
    business_impact: str = "medium"  # "low", "medium", "high", "critical"
    customer_facing: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_resource(self, resource_type: str, amount: float, unit: str):
        """Add a resource allocation to the task"""
        resource = TaskResource(
            resource_type=resource_type,
            amount=amount,
            unit=unit
        )
        self.resources.append(resource)
    
    def add_update(self, updater_id: str, new_status: TaskStatus, 
                   notes: str = "", time_spent: Optional[float] = None):
        """Add a status update to the task"""
        update = TaskUpdate(
            updater_id=updater_id,
            old_status=self.status,
            new_status=new_status,
            notes=notes,
            time_spent=time_spent
        )
        self.updates.append(update)
        self.status = new_status
        
        if time_spent:
            self.actual_hours += time_spent
        
        if new_status == TaskStatus.COMPLETED:
            self.completed_date = datetime.now()
    
    def is_ready_to_start(self, completed_tasks: Set[str]) -> bool:
        """Check if all dependencies are completed"""
        return all(dep_id in completed_tasks for dep_id in self.dependencies)
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date or self.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            return False
        return datetime.now() > self.due_date
    
    def get_progress_percentage(self) -> float:
        """Calculate task progress percentage"""
        if self.status == TaskStatus.COMPLETED:
            return 100.0
        elif self.status == TaskStatus.IN_PROGRESS:
            if self.estimated_hours > 0:
                return min(100.0, (self.actual_hours / self.estimated_hours) * 100)
            else:
                return 50.0  # Default progress for in-progress tasks
        else:
            return 0.0
    
    def get_resource_utilization(self, resource_type: str) -> Dict[str, float]:
        """Get resource utilization for a specific resource type"""
        matching_resources = [r for r in self.resources if r.resource_type == resource_type]
        if not matching_resources:
            return {"allocated": 0, "consumed": 0, "remaining": 0, "utilization": 0}
        
        total_allocated = sum(r.amount for r in matching_resources)
        total_consumed = sum(r.consumed for r in matching_resources)
        total_remaining = sum(r.remaining for r in matching_resources)
        utilization = (total_consumed / total_allocated * 100) if total_allocated > 0 else 0
        
        return {
            "allocated": total_allocated,
            "consumed": total_consumed,
            "remaining": total_remaining,
            "utilization": utilization
        }


class TaskManager:
    """
    Central task management system that handles task lifecycle,
    assignment, delegation, and performance tracking.
    """
    
    def __init__(self):
        self.tasks: Dict[str, BusinessTask] = {}
        self.completed_tasks: Set[str] = set()
        self.employee_workloads: Dict[str, List[str]] = {}  # employee_id -> task_ids
        self.projects: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.task_metrics: Dict[str, Any] = {
            "total_created": 0,
            "total_completed": 0,
            "total_overdue": 0,
            "average_completion_time": 0.0,
            "completion_rate": 0.0
        }
    
    def create_task(self, title: str, description: str, created_by: str,
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   complexity: TaskComplexity = TaskComplexity.MODERATE,
                   due_date: Optional[datetime] = None,
                   required_skills: List[str] = None,
                   estimated_hours: float = 1.0,
                   **kwargs) -> BusinessTask:
        """Create a new business task"""
        
        task = BusinessTask(
            title=title,
            description=description,
            created_by=created_by,
            priority=priority,
            complexity=complexity,
            due_date=due_date,
            required_skills=required_skills or [],
            estimated_hours=estimated_hours,
            **kwargs
        )
        
        self.tasks[task.task_id] = task
        self.task_metrics["total_created"] += 1
        
        logger.info(f"Created task: {task.title} ({task.task_id})")
        return task
    
    def assign_task(self, task_id: str, employee_id: str, assigned_by: str = "CEO") -> bool:
        """Manually assign a task to an employee"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        
        # Remove from previous assignee if any
        if task.assigned_to:
            self._remove_from_workload(task.assigned_to, task_id)
        
        # Assign to new employee
        task.assigned_to = employee_id
        task.add_update(assigned_by, TaskStatus.TO_DO, f"Assigned to {employee_id}")
        
        # Add to employee workload
        self._add_to_workload(employee_id, task_id)
        
        logger.info(f"Assigned task {task.title} to {employee_id}")
        return True
    
    def delegate_task(self, task_id: str, from_employee: str, to_employee: str) -> bool:
        """Delegate a task from one employee to another (hierarchical)"""
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        
        # Verify delegation authority (simplified - assumes manager can delegate)
        task.delegated_by = from_employee
        old_assignee = task.assigned_to
        
        # Remove from current assignee
        if old_assignee:
            self._remove_from_workload(old_assignee, task_id)
        
        # Assign to new employee
        task.assigned_to = to_employee
        task.add_update(from_employee, TaskStatus.TO_DO, 
                       f"Delegated from {old_assignee} to {to_employee}")
        
        # Add to new employee workload
        self._add_to_workload(to_employee, task_id)
        
        logger.info(f"Delegated task {task.title} from {from_employee} to {to_employee}")
        return True
    
    def start_task(self, task_id: str, employee_id: str) -> bool:
        """Start working on a task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task.assigned_to != employee_id:
            logger.warning(f"Employee {employee_id} trying to start unassigned task {task_id}")
            return False
        
        if not task.is_ready_to_start(self.completed_tasks):
            logger.warning(f"Task {task_id} dependencies not met")
            return False
        
        task.start_date = datetime.now()
        task.add_update(employee_id, TaskStatus.IN_PROGRESS, "Started working on task")
        
        logger.info(f"Started task {task.title} by {employee_id}")
        return True
    
    def complete_task(self, task_id: str, employee_id: str, notes: str = "") -> bool:
        """Complete a task"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        if task.assigned_to != employee_id:
            logger.warning(f"Employee {employee_id} trying to complete unassigned task {task_id}")
            return False
        
        # Calculate time spent if task was started
        time_spent = None
        if task.start_date:
            time_spent = (datetime.now() - task.start_date).total_seconds() / 3600
        
        task.add_update(employee_id, TaskStatus.COMPLETED, notes, time_spent)
        self.completed_tasks.add(task_id)
        self.task_metrics["total_completed"] += 1
        
        # Remove from employee workload
        self._remove_from_workload(employee_id, task_id)
        
        # Update completion rate
        self._update_metrics()
        
        logger.info(f"Completed task {task.title} by {employee_id}")
        return True
    
    def block_task(self, task_id: str, blocker_reason: str, blocked_by: str) -> bool:
        """Block a task due to dependencies or issues"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.add_update(blocked_by, TaskStatus.BLOCKED, f"Blocked: {blocker_reason}")
        
        logger.info(f"Blocked task {task.title}: {blocker_reason}")
        return True
    
    def escalate_task(self, task_id: str, escalated_by: str, escalated_to: str, reason: str) -> bool:
        """Escalate a task to higher management"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        
        # Add escalation note
        task.add_update(escalated_by, task.status, 
                       f"Escalated to {escalated_to}: {reason}")
        
        # Update metadata
        task.metadata["escalated"] = True
        task.metadata["escalated_to"] = escalated_to
        task.metadata["escalation_reason"] = reason
        
        logger.info(f"Escalated task {task.title} to {escalated_to}")
        return True
    
    def get_employee_workload(self, employee_id: str) -> Dict[str, Any]:
        """Get current workload for an employee"""
        task_ids = self.employee_workloads.get(employee_id, [])
        tasks = [self.tasks[tid] for tid in task_ids if tid in self.tasks]
        
        total_hours = sum(task.estimated_hours for task in tasks)
        in_progress = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
        overdue = len([t for t in tasks if t.is_overdue()])
        
        return {
            "employee_id": employee_id,
            "total_tasks": len(tasks),
            "in_progress": in_progress,
            "overdue": overdue,
            "estimated_hours": total_hours,
            "tasks": [{"id": t.task_id, "title": t.title, "priority": t.priority.name, 
                      "status": t.status.name} for t in tasks]
        }
    
    def get_task_analytics(self) -> Dict[str, Any]:
        """Get comprehensive task analytics"""
        all_tasks = list(self.tasks.values())
        
        # Status distribution
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.name] = len([t for t in all_tasks if t.status == status])
        
        # Priority distribution  
        priority_counts = {}
        for priority in TaskPriority:
            priority_counts[priority.name] = len([t for t in all_tasks if t.priority == priority])
        
        # Overdue tasks
        overdue_tasks = [t for t in all_tasks if t.is_overdue()]
        
        # Average completion time
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        if completed_tasks:
            completion_times = []
            for task in completed_tasks:
                if task.start_date and task.completed_date:
                    completion_time = (task.completed_date - task.start_date).total_seconds() / 3600
                    completion_times.append(completion_time)
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        else:
            avg_completion_time = 0
        
        return {
            "total_tasks": len(all_tasks),
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "overdue_count": len(overdue_tasks),
            "completion_rate": self.task_metrics["completion_rate"],
            "average_completion_time_hours": avg_completion_time,
            "overdue_tasks": [{"id": t.task_id, "title": t.title, "days_overdue": 
                             (datetime.now() - t.due_date).days if t.due_date else 0} 
                             for t in overdue_tasks]
        }
    
    def get_tasks_by_criteria(self, assigned_to: Optional[str] = None,
                            status: Optional[TaskStatus] = None,
                            priority: Optional[TaskPriority] = None,
                            overdue_only: bool = False) -> List[BusinessTask]:
        """Get tasks matching specific criteria"""
        tasks = list(self.tasks.values())
        
        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        if overdue_only:
            tasks = [t for t in tasks if t.is_overdue()]
        
        return tasks

    # ===== CEO INTERVENTION SUPPORT METHODS =====

    async def reassign_task(self, task_id: str, new_assignee_id: str) -> bool:
        """
        Reassign a task to a different employee (CEO intervention support)
        
        Args:
            task_id: ID of the task to reassign
            new_assignee_id: Employee ID of the new assignee
            
        Returns:
            True if reassignment successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        old_assignee = task.assigned_to
        
        try:
            # Remove from old assignee's workload
            if old_assignee:
                self._remove_from_workload(old_assignee, task_id)
            
            # Update task assignment
            task.assigned_to = new_assignee_id
            task.add_update(
                updater_id="CEO",
                new_status=task.status,  # Keep current status
                notes=f"Task reassigned from {old_assignee} to {new_assignee_id}"
            )
            
            # Add to new assignee's workload
            self._add_to_workload(new_assignee_id, task_id)
            
            logger.info(f"Task {task_id} reassigned from {old_assignee} to {new_assignee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error reassigning task {task_id}: {e}")
            return False

    async def update_task_priority(self, task_id: str, new_priority: TaskPriority) -> bool:
        """
        Update task priority (CEO intervention support)
        
        Args:
            task_id: ID of the task to update
            new_priority: New priority level
            
        Returns:
            True if priority update successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        old_priority = task.priority
        
        try:
            # Update task priority
            task.priority = new_priority
            task.add_update(
                updater_id="CEO",
                new_status=task.status,  # Keep current status
                notes=f"Priority changed from {old_priority.value} to {new_priority.value}"
            )
            
            logger.info(f"Task {task_id} priority updated from {old_priority.value} to {new_priority.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating task {task_id} priority: {e}")
            return False

    async def update_task_deadline(self, task_id: str, new_deadline: datetime) -> bool:
        """
        Update task deadline (CEO intervention support)
        
        Args:
            task_id: ID of the task to update
            new_deadline: New deadline for the task
            
        Returns:
            True if deadline update successful, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        old_deadline = task.due_date
        
        try:
            # Update task deadline
            task.due_date = new_deadline
            task.add_update(
                updater_id="CEO",
                new_status=task.status,  # Keep current status
                notes=f"Deadline updated from {old_deadline.isoformat() if old_deadline else 'None'} to {new_deadline.isoformat()}"
            )
            
            logger.info(f"Task {task_id} deadline updated")
            return True
            
        except Exception as e:
            logger.error(f"Error updating task {task_id} deadline: {e}")
            return False
    
    def _add_to_workload(self, employee_id: str, task_id: str):
        """Add task to employee workload"""
        if employee_id not in self.employee_workloads:
            self.employee_workloads[employee_id] = []
        if task_id not in self.employee_workloads[employee_id]:
            self.employee_workloads[employee_id].append(task_id)
    
    def _remove_from_workload(self, employee_id: str, task_id: str):
        """Remove task from employee workload"""
        if employee_id in self.employee_workloads:
            if task_id in self.employee_workloads[employee_id]:
                self.employee_workloads[employee_id].remove(task_id)
    
    def _update_metrics(self):
        """Update task performance metrics"""
        total_tasks = len(self.tasks)
        if total_tasks > 0:
            self.task_metrics["completion_rate"] = (
                self.task_metrics["total_completed"] / total_tasks * 100
            )
        
        # Count overdue tasks
        overdue_count = len([t for t in self.tasks.values() if t.is_overdue()])
        self.task_metrics["total_overdue"] = overdue_count