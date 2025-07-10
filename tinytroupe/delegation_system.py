"""
Hierarchical Task Delegation and Escalation System

This module provides comprehensive delegation and escalation capabilities for 
the Virtual Business Simulation, including:
- Hierarchical delegation based on organizational structure
- Automatic escalation workflows with configurable triggers
- Authority validation and delegation chains
- Workload-based delegation decisions
- Performance impact tracking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

from tinytroupe.task_management import BusinessTask, TaskManager, TaskPriority, TaskStatus
from tinytroupe.business_simulation import HiringDatabase, BusinessEmployee
from tinytroupe.task_assignment import TaskAssignmentEngine, AssignmentScore, AssignmentStrategy

logger = logging.getLogger("tinytroupe.delegation")


class DelegationReason(Enum):
    """Reasons for task delegation"""
    WORKLOAD_BALANCE = "workload_balance"
    SKILL_MATCH = "skill_match"
    DEVELOPMENT_OPPORTUNITY = "development_opportunity"
    ESCALATION = "escalation"
    MANAGER_DIRECTIVE = "manager_directive"
    AVAILABILITY = "availability"
    PRIORITY_CONFLICT = "priority_conflict"


class EscalationTrigger(Enum):
    """Triggers for automatic task escalation"""
    OVERDUE = "overdue"
    BLOCKED_TOO_LONG = "blocked_too_long"
    WORKLOAD_EXCEEDED = "workload_exceeded"
    SKILL_MISMATCH = "skill_mismatch"
    RESOURCE_UNAVAILABLE = "resource_unavailable"
    QUALITY_CONCERNS = "quality_concerns"
    MANUAL_REQUEST = "manual_request"


@dataclass
class DelegationRecord:
    """Record of a task delegation event"""
    delegation_id: str
    task_id: str
    from_employee: str
    to_employee: str
    delegated_by: str  # Who initiated the delegation
    delegation_date: datetime
    reason: DelegationReason
    authority_level_required: int
    authority_level_granted: int
    delegation_message: str
    accepted: Optional[bool] = None
    acceptance_date: Optional[datetime] = None
    completion_impact: Optional[Dict[str, Any]] = None


@dataclass
class EscalationRecord:
    """Record of a task escalation event"""
    escalation_id: str
    task_id: str
    escalated_by: str
    escalated_to: str
    escalation_date: datetime
    trigger: EscalationTrigger
    escalation_message: str
    previous_assignments: List[str]
    resolution_required_by: Optional[datetime] = None
    resolved: bool = False
    resolution_date: Optional[datetime] = None
    resolution_action: Optional[str] = None


@dataclass
class DelegationChain:
    """Complete delegation chain for a task"""
    task_id: str
    original_assignee: str
    current_assignee: str
    delegation_history: List[DelegationRecord]
    escalation_history: List[EscalationRecord]
    chain_depth: int
    max_depth_allowed: int = 5


class HierarchicalDelegationSystem:
    """
    Comprehensive system for hierarchical task delegation and escalation
    that integrates with the organizational structure and task management.
    """
    
    def __init__(self, hiring_database: HiringDatabase, task_manager: TaskManager,
                 assignment_engine: TaskAssignmentEngine):
        self.hiring_database = hiring_database
        self.task_manager = task_manager
        self.assignment_engine = assignment_engine
        
        # Delegation tracking
        self.delegation_chains: Dict[str, DelegationChain] = {}
        self.delegation_records: Dict[str, DelegationRecord] = {}
        self.escalation_records: Dict[str, EscalationRecord] = {}
        
        # Configuration
        self.max_delegation_depth = 5
        self.escalation_config = {
            EscalationTrigger.OVERDUE: {"threshold_hours": 24, "enabled": True},
            EscalationTrigger.BLOCKED_TOO_LONG: {"threshold_hours": 8, "enabled": True},
            EscalationTrigger.WORKLOAD_EXCEEDED: {"threshold_tasks": 10, "enabled": True},
            EscalationTrigger.SKILL_MISMATCH: {"threshold_score": 0.3, "enabled": True},
        }
        
        # Performance tracking
        self.delegation_stats = {
            "total_delegations": 0,
            "successful_delegations": 0,
            "failed_delegations": 0,
            "total_escalations": 0,
            "escalations_resolved": 0,
            "average_delegation_depth": 0.0
        }
        
        logger.info("Initialized HierarchicalDelegationSystem")
    
    async def delegate_task(self, task_id: str, from_employee: str, to_employee: str,
                          delegated_by: str, reason: DelegationReason,
                          delegation_message: str = "") -> Tuple[bool, str]:
        """
        Delegate a task from one employee to another with hierarchical validation.
        
        Args:
            task_id: ID of task to delegate
            from_employee: Current task assignee
            to_employee: Target employee for delegation
            delegated_by: Employee initiating delegation (for authority check)
            reason: Reason for delegation
            delegation_message: Optional message explaining delegation
            
        Returns:
            Tuple of (success, message)
        """
        # Validate task exists
        if task_id not in self.task_manager.tasks:
            return False, f"Task {task_id} not found"
        
        task = self.task_manager.tasks[task_id]
        
        # Check if delegation is allowed
        can_delegate, validation_message = await self._validate_delegation(
            task, from_employee, to_employee, delegated_by, reason
        )
        
        if not can_delegate:
            return False, validation_message
        
        # Create delegation record
        delegation_record = DelegationRecord(
            delegation_id=f"del_{task_id}_{len(self.delegation_records)}",
            task_id=task_id,
            from_employee=from_employee,
            to_employee=to_employee,
            delegated_by=delegated_by,
            delegation_date=datetime.now(),
            reason=reason,
            authority_level_required=self._get_required_authority_level(task, reason),
            authority_level_granted=self._get_employee_authority_level(delegated_by),
            delegation_message=delegation_message
        )
        
        # Update delegation chain
        await self._update_delegation_chain(task_id, delegation_record)
        
        # Perform the delegation
        success = await self._execute_delegation(task, delegation_record)
        
        if success:
            delegation_record.accepted = True
            delegation_record.acceptance_date = datetime.now()
            self.delegation_stats["total_delegations"] += 1
            self.delegation_stats["successful_delegations"] += 1
            
            logger.info(f"Successfully delegated task {task_id} from {from_employee} to {to_employee}")
            return True, f"Task successfully delegated to {to_employee}"
        else:
            delegation_record.accepted = False
            self.delegation_stats["failed_delegations"] += 1
            return False, f"Delegation failed - {to_employee} could not accept task"
    
    async def escalate_task(self, task_id: str, escalated_by: str, 
                          trigger: EscalationTrigger, escalation_message: str = "") -> Tuple[bool, str]:
        """
        Escalate a task through the organizational hierarchy.
        
        Args:
            task_id: ID of task to escalate
            escalated_by: Employee requesting escalation
            trigger: Reason for escalation
            escalation_message: Optional explanation
            
        Returns:
            Tuple of (success, message)
        """
        if task_id not in self.task_manager.tasks:
            return False, f"Task {task_id} not found"
        
        task = self.task_manager.tasks[task_id]
        
        # Find escalation target
        escalation_target = await self._find_escalation_target(task, escalated_by)
        if not escalation_target:
            return False, "No suitable escalation target found"
        
        # Create escalation record
        escalation_record = EscalationRecord(
            escalation_id=f"esc_{task_id}_{len(self.escalation_records)}",
            task_id=task_id,
            escalated_by=escalated_by,
            escalated_to=escalation_target,
            escalation_date=datetime.now(),
            trigger=trigger,
            escalation_message=escalation_message,
            previous_assignments=self._get_task_assignment_history(task_id),
            resolution_required_by=datetime.now() + timedelta(hours=24)
        )
        
        # Record escalation
        self.escalation_records[escalation_record.escalation_id] = escalation_record
        
        # Update delegation chain
        if task_id in self.delegation_chains:
            self.delegation_chains[task_id].escalation_history.append(escalation_record)
        
        # Execute escalation (reassign task)
        success = await self._execute_escalation(task, escalation_record)
        
        if success:
            self.delegation_stats["total_escalations"] += 1
            
            # Add escalation note to task
            task.add_update(escalated_by, task.status, 
                          f"Escalated to {escalation_target}: {escalation_message}")
            task.metadata["escalated"] = True
            task.metadata["escalated_to"] = escalation_target
            task.metadata["escalation_trigger"] = trigger.value
            
            logger.info(f"Successfully escalated task {task_id} to {escalation_target}")
            return True, f"Task escalated to {escalation_target}"
        else:
            return False, "Escalation failed - target could not accept task"
    
    async def auto_escalate_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Automatically escalate tasks that meet escalation criteria"""
        escalated_tasks = []
        
        for task_id, task in self.task_manager.tasks.items():
            # Check each escalation trigger
            for trigger, config in self.escalation_config.items():
                if not config["enabled"]:
                    continue
                    
                should_escalate, reason = await self._check_escalation_trigger(task, trigger, config)
                if should_escalate:
                    success, message = await self.escalate_task(
                        task_id, task.assigned_to or "system", trigger,
                        f"Automatic escalation: {reason}"
                    )
                    
                    escalated_tasks.append({
                        "task_id": task_id,
                        "trigger": trigger.value,
                        "reason": reason,
                        "success": success,
                        "message": message
                    })
                    
                    if success:
                        break  # Only escalate once per task per cycle
        
        return escalated_tasks
    
    async def suggest_delegation_opportunities(self, manager_id: str) -> List[Dict[str, Any]]:
        """Suggest delegation opportunities for a manager based on team workload and development"""
        suggestions = []
        
        # Get manager's direct reports
        direct_reports = self._get_direct_reports(manager_id)
        if not direct_reports:
            return suggestions
        
        # Get tasks assigned to manager
        manager_tasks = [
            task for task in self.task_manager.tasks.values()
            if task.assigned_to == manager_id and task.status in [TaskStatus.TO_DO, TaskStatus.IN_PROGRESS]
        ]
        
        for task in manager_tasks:
            # Evaluate delegation potential
            delegation_candidates = await self._evaluate_delegation_candidates(task, direct_reports)
            
            if delegation_candidates:
                best_candidate = delegation_candidates[0]
                suggestions.append({
                    "task_id": task.task_id,
                    "task_title": task.title,
                    "recommended_assignee": best_candidate["employee_id"],
                    "recommendation_reason": best_candidate["reason"],
                    "delegation_score": best_candidate["score"],
                    "development_opportunity": best_candidate["development_value"]
                })
        
        return suggestions
    
    def get_delegation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive delegation and escalation analytics"""
        # Calculate delegation chain statistics
        chain_depths = [chain.chain_depth for chain in self.delegation_chains.values()]
        avg_depth = sum(chain_depths) / len(chain_depths) if chain_depths else 0
        self.delegation_stats["average_delegation_depth"] = avg_depth
        
        # Delegation reasons analysis
        delegation_reasons = {}
        for record in self.delegation_records.values():
            reason = record.reason.value
            delegation_reasons[reason] = delegation_reasons.get(reason, 0) + 1
        
        # Escalation triggers analysis
        escalation_triggers = {}
        for record in self.escalation_records.values():
            trigger = record.trigger.value
            escalation_triggers[trigger] = escalation_triggers.get(trigger, 0) + 1
        
        # Top delegators and escalators
        delegators = {}
        escalators = {}
        for record in self.delegation_records.values():
            delegators[record.delegated_by] = delegators.get(record.delegated_by, 0) + 1
        for record in self.escalation_records.values():
            escalators[record.escalated_by] = escalators.get(record.escalated_by, 0) + 1
        
        return {
            "delegation_stats": self.delegation_stats,
            "delegation_reasons": delegation_reasons,
            "escalation_triggers": escalation_triggers,
            "top_delegators": sorted(delegators.items(), key=lambda x: x[1], reverse=True)[:5],
            "top_escalators": sorted(escalators.items(), key=lambda x: x[1], reverse=True)[:5],
            "chain_depth_distribution": {
                "min": min(chain_depths) if chain_depths else 0,
                "max": max(chain_depths) if chain_depths else 0,
                "average": avg_depth
            }
        }
    
    # Private helper methods
    
    async def _validate_delegation(self, task: BusinessTask, from_employee: str, 
                                 to_employee: str, delegated_by: str, 
                                 reason: DelegationReason) -> Tuple[bool, str]:
        """Validate if a delegation is allowed"""
        # Check if employees exist
        if from_employee not in self.hiring_database.employees:
            return False, f"Employee {from_employee} not found"
        if to_employee not in self.hiring_database.employees:
            return False, f"Employee {to_employee} not found"
        if delegated_by not in self.hiring_database.employees:
            return False, f"Delegating employee {delegated_by} not found"
        
        # Check authority
        required_authority = self._get_required_authority_level(task, reason)
        delegator_authority = self._get_employee_authority_level(delegated_by)
        
        if delegator_authority < required_authority:
            return False, f"Insufficient authority level ({delegator_authority} < {required_authority})"
        
        # Check delegation chain depth
        if task.task_id in self.delegation_chains:
            chain = self.delegation_chains[task.task_id]
            if chain.chain_depth >= self.max_delegation_depth:
                return False, f"Maximum delegation depth ({self.max_delegation_depth}) exceeded"
        
        # Check target employee capacity
        target_workload = await self._calculate_employee_workload(to_employee)
        if target_workload > 10:  # Configurable threshold
            return False, f"Target employee {to_employee} is at capacity ({target_workload} tasks)"
        
        return True, "Delegation validated"
    
    def _get_required_authority_level(self, task: BusinessTask, reason: DelegationReason) -> int:
        """Determine required authority level for delegation"""
        base_authority = 3  # Basic delegation authority
        
        # Adjust based on task priority
        if task.priority == TaskPriority.CRITICAL:
            base_authority += 3
        elif task.priority == TaskPriority.HIGH:
            base_authority += 2
        elif task.priority == TaskPriority.MEDIUM:
            base_authority += 1
        
        # Adjust based on delegation reason
        if reason == DelegationReason.ESCALATION:
            base_authority += 2
        elif reason == DelegationReason.MANAGER_DIRECTIVE:
            base_authority += 1
        
        return min(base_authority, 10)  # Cap at 10
    
    def _get_employee_authority_level(self, employee_id: str) -> int:
        """Get employee's authority level from their role/position"""
        if employee_id not in self.hiring_database.employees:
            return 0
        
        employee = self.hiring_database.employees[employee_id]
        role = employee.role.lower()
        
        # Authority levels based on role
        if "ceo" in role:
            return 10
        elif "vp" in role or "vice president" in role:
            return 8
        elif "director" in role:
            return 7
        elif "manager" in role:
            return 6
        elif "lead" in role or "senior" in role:
            return 5
        elif "principal" in role:
            return 4
        else:
            return 3  # Default authority level
    
    async def _update_delegation_chain(self, task_id: str, delegation_record: DelegationRecord):
        """Update or create delegation chain for a task"""
        if task_id not in self.delegation_chains:
            # Create new chain
            task = self.task_manager.tasks[task_id]
            self.delegation_chains[task_id] = DelegationChain(
                task_id=task_id,
                original_assignee=delegation_record.from_employee,
                current_assignee=delegation_record.to_employee,
                delegation_history=[delegation_record],
                escalation_history=[],
                chain_depth=1
            )
        else:
            # Update existing chain
            chain = self.delegation_chains[task_id]
            chain.current_assignee = delegation_record.to_employee
            chain.delegation_history.append(delegation_record)
            chain.chain_depth += 1
        
        # Store delegation record
        self.delegation_records[delegation_record.delegation_id] = delegation_record
    
    async def _execute_delegation(self, task: BusinessTask, delegation_record: DelegationRecord) -> bool:
        """Execute the actual task delegation"""
        try:
            # Update task assignment
            task.assigned_to = delegation_record.to_employee
            task.add_update(
                delegation_record.delegated_by, 
                task.status,
                f"Delegated to {delegation_record.to_employee}: {delegation_record.delegation_message}"
            )
            
            # Update task metadata
            task.metadata["delegated"] = True
            task.metadata["delegation_chain_depth"] = self.delegation_chains[task.task_id].chain_depth
            
            return True
        except Exception as e:
            logger.error(f"Failed to execute delegation: {e}")
            return False
    
    async def _find_escalation_target(self, task: BusinessTask, escalated_by: str) -> Optional[str]:
        """Find appropriate escalation target in organizational hierarchy"""
        if escalated_by not in self.hiring_database.employees:
            return None
        
        employee = self.hiring_database.employees[escalated_by]
        manager_id = employee.manager_id
        
        # If no direct manager, find highest authority employee
        if not manager_id:
            highest_authority = 0
            highest_authority_employee = None
            
            for emp_id, emp in self.hiring_database.employees.items():
                authority = self._get_employee_authority_level(emp_id)
                if authority > highest_authority:
                    highest_authority = authority
                    highest_authority_employee = emp_id
            
            return highest_authority_employee
        
        return manager_id
    
    async def _execute_escalation(self, task: BusinessTask, escalation_record: EscalationRecord) -> bool:
        """Execute task escalation"""
        try:
            # Update task assignment
            task.assigned_to = escalation_record.escalated_to
            
            # Increase task priority if not already at max
            if task.priority != TaskPriority.CRITICAL:
                if task.priority == TaskPriority.HIGH:
                    task.priority = TaskPriority.CRITICAL
                elif task.priority == TaskPriority.MEDIUM:
                    task.priority = TaskPriority.HIGH
                else:
                    task.priority = TaskPriority.MEDIUM
            
            return True
        except Exception as e:
            logger.error(f"Failed to execute escalation: {e}")
            return False
    
    async def _check_escalation_trigger(self, task: BusinessTask, trigger: EscalationTrigger, 
                                      config: Dict[str, Any]) -> Tuple[bool, str]:
        """Check if a task meets escalation criteria"""
        now = datetime.now()
        
        if trigger == EscalationTrigger.OVERDUE:
            if task.due_date and now > task.due_date:
                hours_overdue = (now - task.due_date).total_seconds() / 3600
                if hours_overdue >= config["threshold_hours"]:
                    return True, f"Task overdue by {hours_overdue:.1f} hours"
        
        elif trigger == EscalationTrigger.BLOCKED_TOO_LONG:
            if task.status == TaskStatus.BLOCKED:
                last_update = task.status_updates[-1]['timestamp'] if task.status_updates else task.created_date
                hours_blocked = (now - last_update).total_seconds() / 3600
                if hours_blocked >= config["threshold_hours"]:
                    return True, f"Task blocked for {hours_blocked:.1f} hours"
        
        elif trigger == EscalationTrigger.WORKLOAD_EXCEEDED:
            if task.assigned_to:
                workload = await self._calculate_employee_workload(task.assigned_to)
                if workload >= config["threshold_tasks"]:
                    return True, f"Assignee has {workload} tasks (threshold: {config['threshold_tasks']})"
        
        return False, ""
    
    def _get_task_assignment_history(self, task_id: str) -> List[str]:
        """Get history of employees assigned to this task"""
        history = []
        if task_id in self.delegation_chains:
            chain = self.delegation_chains[task_id]
            history.append(chain.original_assignee)
            for delegation in chain.delegation_history:
                history.append(delegation.to_employee)
        return history
    
    def _get_direct_reports(self, manager_id: str) -> List[str]:
        """Get list of direct reports for a manager"""
        return list(self.hiring_database.organizational_chart.get(manager_id, set()))
    
    async def _calculate_employee_workload(self, employee_id: str) -> int:
        """Calculate current workload for an employee"""
        active_tasks = [
            task for task in self.task_manager.tasks.values()
            if task.assigned_to == employee_id and task.status in [TaskStatus.TO_DO, TaskStatus.IN_PROGRESS]
        ]
        return len(active_tasks)
    
    async def _evaluate_delegation_candidates(self, task: BusinessTask, candidates: List[str]) -> List[Dict[str, Any]]:
        """Evaluate potential delegation candidates for a task"""
        candidate_scores = []
        
        for candidate_id in candidates:
            if candidate_id not in self.hiring_database.employees:
                continue
            
            # Use assignment engine to score candidate
            candidate_employee = self.hiring_database.employees[candidate_id]
            scores = await self.assignment_engine._score_candidates(task, [candidate_employee], AssignmentStrategy.OPTIMAL)
            if scores:
                candidate_score = scores[0]
                
                # Calculate development value
                employee = self.hiring_database.employees[candidate_id]
                development_value = self._calculate_development_value(task, employee)
                
                candidate_scores.append({
                    "employee_id": candidate_id,
                    "score": candidate_score.total_score,
                    "skill_match": candidate_score.skill_match,
                    "availability": candidate_score.availability,
                    "development_value": development_value,
                    "reason": f"Score: {candidate_score.total_score:.2f}, Skills: {candidate_score.skill_match:.2f}"
                })
        
        # Sort by combined score (assignment score + development value)
        candidate_scores.sort(key=lambda x: x["score"] + x["development_value"], reverse=True)
        return candidate_scores
    
    def _calculate_development_value(self, task: BusinessTask, employee: BusinessEmployee) -> float:
        """Calculate development value of assigning task to employee"""
        development_value = 0.0
        
        # Handle both list and dict formats for required_skills
        if isinstance(task.required_skills, dict):
            # Dict format: {skill: required_level}
            for skill, required_level in task.required_skills.items():
                current_level = employee.business_skills.get(skill, 0)
                if required_level > current_level:
                    development_value += (required_level - current_level) * 0.2
        elif isinstance(task.required_skills, list):
            # List format: [skill1, skill2, ...]
            for skill in task.required_skills:
                current_level = employee.business_skills.get(skill, 0)
                # Assume required level is 5 for development calculation
                required_level = 5
                if required_level > current_level:
                    development_value += (required_level - current_level) * 0.2
        
        return min(development_value, 1.0)  # Cap at 1.0