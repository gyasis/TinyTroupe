"""
Automated Task Assignment System for Virtual Business Simulation

This module provides intelligent task assignment capabilities that support:
- Automated assignment based on skills, availability, and workload
- Manual assignment with CEO override capabilities  
- Hierarchical delegation and escalation
- Load balancing and optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from tinytroupe.task_management import BusinessTask, TaskManager, TaskPriority, TaskComplexity
from tinytroupe.business_simulation import HiringDatabase, BusinessEmployee

logger = logging.getLogger("tinytroupe.assignment")


class AssignmentStrategy(Enum):
    """Task assignment strategy options"""
    ROUND_ROBIN = "round_robin"
    SKILL_BASED = "skill_based"
    WORKLOAD_BALANCED = "workload_balanced"
    PRIORITY_FIRST = "priority_first"
    OPTIMAL = "optimal"  # Combines multiple factors


@dataclass
class AssignmentScore:
    """Score calculation for task assignment"""
    employee_id: str
    total_score: float
    skill_match: float
    availability: float
    workload: float
    performance: float
    reasons: List[str]


class TaskAssignmentEngine:
    """
    Intelligent task assignment engine that automatically assigns tasks
    to employees based on multiple criteria and strategies.
    """
    
    def __init__(self, task_manager: TaskManager, hiring_database: HiringDatabase):
        self.task_manager = task_manager
        self.hiring_database = hiring_database
        
        # Assignment configuration
        self.max_workload_hours = 40.0  # Max weekly hours per employee
        self.skill_weight = 0.4
        self.availability_weight = 0.3
        self.workload_weight = 0.2
        self.performance_weight = 0.1
        
        # Assignment history for round-robin
        self.last_assigned: Dict[str, str] = {}  # department -> employee_id
        
        logger.info("Initialized TaskAssignmentEngine")
    
    async def auto_assign_task(self, task: BusinessTask, 
                             strategy: AssignmentStrategy = AssignmentStrategy.OPTIMAL,
                             department_filter: Optional[str] = None) -> Optional[str]:
        """
        Automatically assign a task to the best available employee.
        
        Returns the employee_id if assignment successful, None otherwise.
        """
        
        # Get candidate employees
        candidates = self._get_assignment_candidates(task, department_filter)
        
        if not candidates:
            logger.warning(f"No candidates found for task {task.title}")
            return None
        
        # Score candidates based on strategy
        scores = await self._score_candidates(task, candidates, strategy)
        
        if not scores:
            logger.warning(f"No viable candidates for task {task.title}")
            return None
        
        # Select best candidate
        best_candidate = max(scores, key=lambda s: s.total_score)
        
        # Assign the task
        success = self.task_manager.assign_task(
            task.task_id, 
            best_candidate.employee_id,
            "AUTO_ASSIGNMENT"
        )
        
        if success:
            logger.info(f"Auto-assigned task {task.title} to {best_candidate.employee_id} "
                       f"(score: {best_candidate.total_score:.2f})")
            self._log_assignment_reasoning(task, best_candidate)
            return best_candidate.employee_id
        
        return None
    
    async def recommend_assignment(self, task: BusinessTask, 
                                 top_n: int = 3) -> List[AssignmentScore]:
        """
        Recommend top N employees for a task assignment.
        Useful for manual assignment with suggestions.
        """
        candidates = self._get_assignment_candidates(task)
        scores = await self._score_candidates(task, candidates, AssignmentStrategy.OPTIMAL)
        
        # Return top N candidates sorted by score
        return sorted(scores, key=lambda s: s.total_score, reverse=True)[:top_n]
    
    def can_delegate_task(self, task_id: str, from_employee: str, to_employee: str) -> Tuple[bool, str]:
        """
        Check if a task can be delegated from one employee to another.
        Returns (can_delegate, reason).
        """
        
        # Get employee data
        from_emp = self.hiring_database.get_employee(from_employee)
        to_emp = self.hiring_database.get_employee(to_employee)
        
        if not from_emp or not to_emp:
            return False, "Employee not found"
        
        # Check hierarchical authority
        if not self._has_delegation_authority(from_emp, to_emp):
            return False, "No delegation authority"
        
        # Check if target employee can handle the task
        task = self.task_manager.tasks.get(task_id)
        if not task:
            return False, "Task not found"
        
        # Check skill requirements
        if not self._meets_skill_requirements(to_emp, task):
            return False, "Target employee lacks required skills"
        
        # Check workload capacity
        workload = self.task_manager.get_employee_workload(to_employee)
        if workload["estimated_hours"] + task.estimated_hours > self.max_workload_hours:
            return False, "Target employee workload too high"
        
        return True, "Delegation approved"
    
    def optimize_team_workload(self, department: str) -> Dict[str, Any]:
        """
        Optimize workload distribution within a department.
        Returns suggested task reassignments.
        """
        
        department_employees = self.hiring_database.get_employees_by_department(department)
        if not department_employees:
            return {"message": f"No employees in department {department}"}
        
        # Get current workloads
        workloads = {}
        for emp in department_employees:
            workload = self.task_manager.get_employee_workload(emp.employee_id)
            workloads[emp.employee_id] = workload
        
        # Calculate average workload
        total_hours = sum(w["estimated_hours"] for w in workloads.values())
        avg_hours = total_hours / len(workloads) if workloads else 0
        
        # Identify overloaded and underloaded employees
        overloaded = []
        underloaded = []
        
        for emp_id, workload in workloads.items():
            hours = workload["estimated_hours"]
            if hours > avg_hours * 1.2:  # 20% above average
                overloaded.append((emp_id, hours, workload["tasks"]))
            elif hours < avg_hours * 0.8:  # 20% below average
                underloaded.append((emp_id, hours))
        
        # Generate reassignment suggestions
        suggestions = []
        for overloaded_emp, hours, tasks in overloaded:
            # Find tasks that can be reassigned
            for task_info in tasks:
                if task_info["status"] in ["TO_DO", "IN_PROGRESS"]:
                    task = self.task_manager.tasks.get(task_info["id"])
                    if task:
                        # Find best underloaded employee for this task
                        best_target = self._find_best_reassignment_target(
                            task, underloaded, department_employees
                        )
                        if best_target:
                            suggestions.append({
                                "task_id": task.task_id,
                                "task_title": task.title,
                                "from_employee": overloaded_emp,
                                "to_employee": best_target,
                                "estimated_hours": task.estimated_hours,
                                "reason": "Workload balancing"
                            })
        
        return {
            "department": department,
            "average_workload_hours": avg_hours,
            "overloaded_employees": [emp_id for emp_id, _, _ in overloaded],
            "underloaded_employees": [emp_id for emp_id, _ in underloaded],
            "reassignment_suggestions": suggestions
        }
    
    def _get_assignment_candidates(self, task: BusinessTask, 
                                 department_filter: Optional[str] = None) -> List[BusinessEmployee]:
        """Get list of employees who could potentially be assigned the task"""
        
        all_employees = list(self.hiring_database.employees.values())
        
        # Filter by department if specified
        if department_filter:
            all_employees = [emp for emp in all_employees 
                           if emp.department == department_filter]
        
        # Filter by basic availability (not overloaded)
        candidates = []
        for emp in all_employees:
            workload = self.task_manager.get_employee_workload(emp.employee_id)
            if workload["estimated_hours"] + task.estimated_hours <= self.max_workload_hours:
                candidates.append(emp)
        
        return candidates
    
    async def _score_candidates(self, task: BusinessTask, candidates: List[BusinessEmployee],
                              strategy: AssignmentStrategy) -> List[AssignmentScore]:
        """Score candidates for task assignment based on strategy"""
        
        scores = []
        
        for candidate in candidates:
            if strategy == AssignmentStrategy.ROUND_ROBIN:
                score = self._score_round_robin(task, candidate)
            elif strategy == AssignmentStrategy.SKILL_BASED:
                score = self._score_skill_based(task, candidate)
            elif strategy == AssignmentStrategy.WORKLOAD_BALANCED:
                score = self._score_workload_balanced(task, candidate)
            elif strategy == AssignmentStrategy.PRIORITY_FIRST:
                score = self._score_priority_first(task, candidate)
            else:  # OPTIMAL
                score = self._score_optimal(task, candidate)
            
            if score and score.total_score > 0:
                scores.append(score)
        
        return scores
    
    def _score_optimal(self, task: BusinessTask, candidate: BusinessEmployee) -> AssignmentScore:
        """Calculate optimal assignment score combining multiple factors"""
        
        reasons = []
        
        # 1. Skill match score (0-1)
        skill_score = self._calculate_skill_match(task, candidate)
        if skill_score > 0.8:
            reasons.append(f"Excellent skill match ({skill_score:.2f})")
        elif skill_score > 0.6:
            reasons.append(f"Good skill match ({skill_score:.2f})")
        elif skill_score < 0.3:
            reasons.append(f"Poor skill match ({skill_score:.2f})")
        
        # 2. Availability score (0-1)
        availability_score = self._calculate_availability(candidate)
        if availability_score > 0.8:
            reasons.append("High availability")
        elif availability_score < 0.3:
            reasons.append("Low availability")
        
        # 3. Workload score (0-1) - higher score for lower workload
        workload_score = self._calculate_workload_score(candidate)
        if workload_score > 0.8:
            reasons.append("Light workload")
        elif workload_score < 0.3:
            reasons.append("Heavy workload")
        
        # 4. Performance score (0-1)
        performance_score = self._calculate_performance_score(candidate)
        if performance_score > 0.8:
            reasons.append("High performer")
        
        # Calculate weighted total score
        total_score = (
            skill_score * self.skill_weight +
            availability_score * self.availability_weight +
            workload_score * self.workload_weight +
            performance_score * self.performance_weight
        )
        
        return AssignmentScore(
            employee_id=candidate.employee_id,
            total_score=total_score,
            skill_match=skill_score,
            availability=availability_score,
            workload=workload_score,
            performance=performance_score,
            reasons=reasons
        )
    
    def _score_skill_based(self, task: BusinessTask, candidate: BusinessEmployee) -> AssignmentScore:
        """Score based primarily on skill match"""
        skill_score = self._calculate_skill_match(task, candidate)
        
        return AssignmentScore(
            employee_id=candidate.employee_id,
            total_score=skill_score,
            skill_match=skill_score,
            availability=0,
            workload=0,
            performance=0,
            reasons=[f"Skill-based assignment (match: {skill_score:.2f})"]
        )
    
    def _score_workload_balanced(self, task: BusinessTask, candidate: BusinessEmployee) -> AssignmentScore:
        """Score based primarily on workload balance"""
        workload_score = self._calculate_workload_score(candidate)
        
        return AssignmentScore(
            employee_id=candidate.employee_id,
            total_score=workload_score,
            skill_match=0,
            availability=0,
            workload=workload_score,
            performance=0,
            reasons=[f"Workload-balanced assignment (score: {workload_score:.2f})"]
        )
    
    def _score_round_robin(self, task: BusinessTask, candidate: BusinessEmployee) -> AssignmentScore:
        """Score based on round-robin assignment"""
        # Simple round-robin - prefer candidates who haven't been assigned recently
        last_assigned = self.last_assigned.get(candidate.department, "")
        score = 0.5 if candidate.employee_id != last_assigned else 0.1
        
        return AssignmentScore(
            employee_id=candidate.employee_id,
            total_score=score,
            skill_match=0,
            availability=0,
            workload=0,
            performance=0,
            reasons=["Round-robin assignment"]
        )
    
    def _score_priority_first(self, task: BusinessTask, candidate: BusinessEmployee) -> AssignmentScore:
        """Score based on task priority and candidate seniority"""
        # Higher priority tasks go to more experienced employees
        skill_score = self._calculate_skill_match(task, candidate)
        priority_bonus = task.priority.value / 5.0  # Normalize to 0-1
        
        total_score = skill_score * 0.7 + priority_bonus * 0.3
        
        return AssignmentScore(
            employee_id=candidate.employee_id,
            total_score=total_score,
            skill_match=skill_score,
            availability=0,
            workload=0,
            performance=0,
            reasons=[f"Priority-first assignment (priority: {task.priority.name})"]
        )
    
    def _calculate_skill_match(self, task: BusinessTask, candidate: BusinessEmployee) -> float:
        """Calculate how well candidate's skills match task requirements"""
        if not task.required_skills:
            return 0.5  # Neutral score if no specific skills required
        
        candidate_skills = candidate.business_skills
        if not candidate_skills:
            return 0.1  # Low score if candidate has no recorded skills
        
        matches = 0
        total_weight = 0
        
        for required_skill in task.required_skills:
            skill_level = candidate_skills.get(required_skill, 0)
            
            # Weight by minimum required level
            weight = task.minimum_skill_level / 10.0
            total_weight += weight
            
            if skill_level >= task.minimum_skill_level:
                # Bonus for exceeding minimum requirements
                match_score = min(1.0, skill_level / 10.0)
                matches += match_score * weight
        
        return matches / total_weight if total_weight > 0 else 0.1
    
    def _calculate_availability(self, candidate: BusinessEmployee) -> float:
        """Calculate candidate availability (inverse of current workload)"""
        workload = self.task_manager.get_employee_workload(candidate.employee_id)
        current_hours = workload["estimated_hours"]
        
        # Availability decreases as workload approaches maximum
        availability = max(0, (self.max_workload_hours - current_hours) / self.max_workload_hours)
        return availability
    
    def _calculate_workload_score(self, candidate: BusinessEmployee) -> float:
        """Calculate workload score (higher score for lower workload)"""
        return self._calculate_availability(candidate)
    
    def _calculate_performance_score(self, candidate: BusinessEmployee) -> float:
        """Calculate performance score based on historical performance"""
        # Simple performance calculation based on rating
        performance_rating = candidate.performance_rating
        
        rating_scores = {
            "Exceeds Expectations": 1.0,
            "Meets Expectations": 0.7,
            "Below Expectations": 0.3,
            "Not Rated": 0.5
        }
        
        return rating_scores.get(performance_rating, 0.5)
    
    def _meets_skill_requirements(self, employee: BusinessEmployee, task: BusinessTask) -> bool:
        """Check if employee meets minimum skill requirements for task"""
        if not task.required_skills:
            return True
        
        employee_skills = employee.business_skills
        if not employee_skills:
            return False
        
        for required_skill in task.required_skills:
            skill_level = employee_skills.get(required_skill, 0)
            if skill_level < task.minimum_skill_level:
                return False
        
        return True
    
    def _has_delegation_authority(self, from_emp: BusinessEmployee, to_emp: BusinessEmployee) -> bool:
        """Check if from_emp has authority to delegate to to_emp"""
        # Simplified authority check - managers can delegate to their reports
        return to_emp.employee_id in from_emp.direct_reports
    
    def _find_best_reassignment_target(self, task: BusinessTask, underloaded: List[Tuple[str, float]], 
                                     department_employees: List[BusinessEmployee]) -> Optional[str]:
        """Find the best employee to reassign a task to"""
        
        for emp_id, current_hours in underloaded:
            emp = next((e for e in department_employees if e.employee_id == emp_id), None)
            if emp and self._meets_skill_requirements(emp, task):
                return emp_id
        
        return None
    
    def _log_assignment_reasoning(self, task: BusinessTask, assignment: AssignmentScore):
        """Log detailed reasoning for task assignment"""
        logger.info(f"Assignment reasoning for task '{task.title}':")
        logger.info(f"  Assigned to: {assignment.employee_id}")
        logger.info(f"  Total score: {assignment.total_score:.3f}")
        logger.info(f"  Skill match: {assignment.skill_match:.3f}")
        logger.info(f"  Availability: {assignment.availability:.3f}")
        logger.info(f"  Workload: {assignment.workload:.3f}")
        logger.info(f"  Performance: {assignment.performance:.3f}")
        logger.info(f"  Reasons: {', '.join(assignment.reasons)}")


class CEOAssignmentOverride:
    """
    CEO override system for manual task assignment and intervention.
    Provides capabilities for direct assignment, reassignment, and priority changes.
    """
    
    def __init__(self, task_manager: TaskManager, assignment_engine: TaskAssignmentEngine):
        self.task_manager = task_manager
        self.assignment_engine = assignment_engine
        
    def ceo_assign_task(self, task_id: str, employee_id: str, reason: str = "") -> bool:
        """CEO directly assigns a task to an employee, overriding auto-assignment"""
        
        task = self.task_manager.tasks.get(task_id)
        if not task:
            logger.error(f"CEO assignment failed: Task {task_id} not found")
            return False
        
        success = self.task_manager.assign_task(task_id, employee_id, "CEO")
        
        if success:
            # Add CEO override note
            task.add_update("CEO", task.status, f"CEO Override Assignment: {reason}")
            task.metadata["ceo_override"] = True
            task.metadata["ceo_reason"] = reason
            
            logger.info(f"CEO assigned task {task.title} to {employee_id}: {reason}")
            return True
        
        return False
    
    def ceo_reassign_task(self, task_id: str, from_employee: str, to_employee: str, reason: str = "") -> bool:
        """CEO reassigns a task from one employee to another"""
        
        task = self.task_manager.tasks.get(task_id)
        if not task:
            return False
        
        if task.assigned_to != from_employee:
            logger.warning(f"Task {task_id} not assigned to {from_employee}")
            return False
        
        # Reassign the task
        success = self.task_manager.assign_task(task_id, to_employee, "CEO")
        
        if success:
            task.add_update("CEO", task.status, 
                           f"CEO Reassignment: {from_employee} -> {to_employee}. {reason}")
            task.metadata["ceo_reassignment"] = True
            
            logger.info(f"CEO reassigned task {task.title} from {from_employee} to {to_employee}")
            return True
        
        return False
    
    def ceo_change_priority(self, task_id: str, new_priority: TaskPriority, reason: str = "") -> bool:
        """CEO changes task priority"""
        
        task = self.task_manager.tasks.get(task_id)
        if not task:
            return False
        
        old_priority = task.priority
        task.priority = new_priority
        task.add_update("CEO", task.status, 
                       f"CEO Priority Change: {old_priority.name} -> {new_priority.name}. {reason}")
        
        logger.info(f"CEO changed priority for task {task.title}: {old_priority.name} -> {new_priority.name}")
        return True
    
    def get_assignment_recommendations(self, task_id: str) -> List[AssignmentScore]:
        """Get CEO dashboard recommendations for task assignment"""
        task = self.task_manager.tasks.get(task_id)
        if not task:
            return []
        
        return asyncio.run(self.assignment_engine.recommend_assignment(task))