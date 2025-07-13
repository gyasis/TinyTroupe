"""
Performance Tracking System - Employee Metrics and Analytics

This module provides comprehensive performance tracking capabilities for the Virtual Business Simulation:
- Employee performance metrics and KPIs
- Team analytics and collaboration insights
- Quality scores and trend analysis
- Performance goal setting and tracking
- Productivity analytics and benchmarking
- Skills development tracking
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import statistics
import uuid

from tinytroupe.task_management import TaskManager, BusinessTask, TaskStatus, TaskPriority
from tinytroupe.business_simulation import HiringDatabase

logger = logging.getLogger("tinytroupe.performance_tracking")


class MetricType(Enum):
    """Types of performance metrics"""
    PRODUCTIVITY = "productivity"
    QUALITY = "quality"
    COLLABORATION = "collaboration"
    EFFICIENCY = "efficiency"
    INNOVATION = "innovation"
    LEADERSHIP = "leadership"
    CUSTOMER_SATISFACTION = "customer_satisfaction"


class PerformanceTrend(Enum):
    """Performance trend indicators"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class GoalStatus(Enum):
    """Status of performance goals"""
    DRAFT = "draft"
    ACTIVE = "active"
    ACHIEVED = "achieved"
    MISSED = "missed"
    CANCELLED = "cancelled"


@dataclass
class PerformanceMetric:
    """Individual performance metric measurement"""
    metric_id: str
    employee_id: str
    metric_type: MetricType
    name: str
    value: float
    target_value: Optional[float] = None
    unit: str = ""
    measurement_date: datetime = field(default_factory=datetime.now)
    
    # Context and metadata
    period: str = "monthly"  # daily, weekly, monthly, quarterly, yearly
    category: str = "general"
    source: str = "system"  # system, self-assessment, peer-review, manager
    
    # Additional details
    notes: str = ""
    confidence_score: float = 1.0  # 0.0 to 1.0
    
    def get_achievement_percentage(self) -> Optional[float]:
        """Calculate achievement percentage vs target"""
        if self.target_value and self.target_value > 0:
            return (self.value / self.target_value) * 100
        return None
    
    def is_target_achieved(self) -> bool:
        """Check if target is achieved"""
        if self.target_value:
            return self.value >= self.target_value
        return False


@dataclass
class PerformanceGoal:
    """Performance goal for an employee"""
    goal_id: str
    employee_id: str
    set_by: str
    title: str
    description: str
    metric_type: MetricType
    
    # Goal specifics
    target_value: float
    current_value: float = 0.0
    unit: str = ""
    
    # Timeline
    start_date: datetime = field(default_factory=datetime.now)
    target_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=90))
    
    # Status tracking
    status: GoalStatus = GoalStatus.DRAFT
    priority: str = "medium"  # low, medium, high, critical
    
    # Progress tracking
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    progress_notes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Review and approval
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    
    def get_progress_percentage(self) -> float:
        """Calculate progress towards goal"""
        if self.target_value > 0:
            return min((self.current_value / self.target_value) * 100, 100.0)
        return 0.0
    
    def get_days_remaining(self) -> int:
        """Get days remaining to achieve goal"""
        return max((self.target_date - datetime.now()).days, 0)
    
    def is_overdue(self) -> bool:
        """Check if goal is overdue"""
        return datetime.now() > self.target_date and self.status not in [GoalStatus.ACHIEVED, GoalStatus.CANCELLED]


@dataclass
class TeamMetrics:
    """Aggregated metrics for a team/department"""
    team_id: str
    team_name: str
    department: str
    measurement_date: datetime
    
    # Team composition
    total_members: int
    active_members: int
    
    # Performance metrics
    avg_productivity: float = 0.0
    avg_quality_score: float = 0.0
    avg_collaboration_score: float = 0.0
    
    # Team dynamics
    internal_communication_score: float = 0.0
    knowledge_sharing_score: float = 0.0
    team_satisfaction: float = 0.0
    
    # Project metrics
    completed_projects: int = 0
    on_time_delivery_rate: float = 0.0
    budget_adherence_rate: float = 0.0
    
    # Trends
    productivity_trend: PerformanceTrend = PerformanceTrend.UNKNOWN
    quality_trend: PerformanceTrend = PerformanceTrend.UNKNOWN
    satisfaction_trend: PerformanceTrend = PerformanceTrend.UNKNOWN


@dataclass
class SkillAssessment:
    """Skill assessment for an employee"""
    assessment_id: str
    employee_id: str
    assessor_id: str
    skill_name: str
    
    # Assessment details
    current_level: int  # 1-10 scale
    target_level: int
    assessment_date: datetime = field(default_factory=datetime.now)
    
    # Development tracking
    strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    development_plan: str = ""
    
    # Assessment context
    assessment_type: str = "annual"  # annual, quarterly, project-based
    assessor_role: str = "manager"  # manager, peer, self, customer
    
    def get_skill_gap(self) -> int:
        """Calculate skill gap"""
        return max(self.target_level - self.current_level, 0)
    
    def get_proficiency_percentage(self) -> float:
        """Calculate proficiency as percentage"""
        return (self.current_level / 10.0) * 100


class PerformanceTrackingSystem:
    """
    Comprehensive Performance Tracking System for Virtual Business Simulation
    
    Tracks employee performance, team analytics, and provides insights for improvement.
    """
    
    def __init__(self, task_manager: TaskManager, hiring_database: HiringDatabase):
        self.task_manager = task_manager
        self.hiring_database = hiring_database
        
        # Performance data storage
        self.metrics: Dict[str, List[PerformanceMetric]] = {}  # {employee_id: [metrics]}
        self.goals: Dict[str, List[PerformanceGoal]] = {}      # {employee_id: [goals]}
        self.skill_assessments: Dict[str, List[SkillAssessment]] = {}  # {employee_id: [assessments]}
        self.team_metrics: Dict[str, List[TeamMetrics]] = {}   # {team_id: [metrics]}
        
        # Benchmarks and standards
        self.performance_benchmarks: Dict[str, Dict[str, float]] = {}
        self.industry_standards: Dict[str, float] = {}
        
        # Analytics cache
        self._analytics_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        
        # Initialize default benchmarks
        self._setup_default_benchmarks()
    
    def _setup_default_benchmarks(self):
        """Setup default performance benchmarks"""
        self.performance_benchmarks = {
            "software_engineer": {
                "productivity": 85.0,
                "quality": 90.0,
                "collaboration": 80.0,
                "efficiency": 85.0,
                "innovation": 75.0
            },
            "project_manager": {
                "productivity": 80.0,
                "quality": 85.0,
                "collaboration": 95.0,
                "leadership": 85.0,
                "efficiency": 90.0
            },
            "qa_engineer": {
                "productivity": 80.0,
                "quality": 95.0,
                "collaboration": 85.0,
                "efficiency": 85.0
            },
            "marketing_manager": {
                "productivity": 75.0,
                "quality": 80.0,
                "collaboration": 90.0,
                "leadership": 80.0,
                "customer_satisfaction": 85.0
            }
        }
        
        self.industry_standards = {
            "task_completion_rate": 85.0,
            "on_time_delivery": 80.0,
            "quality_score": 85.0,
            "customer_satisfaction": 80.0,
            "team_collaboration": 80.0
        }
    
    async def record_metric(self, employee_id: str, metric_type: MetricType,
                          name: str, value: float, target_value: float = None,
                          unit: str = "", period: str = "monthly",
                          source: str = "system") -> str:
        """Record a performance metric for an employee"""
        if employee_id not in self.hiring_database.employees:
            logger.error(f"Employee {employee_id} not found")
            return None
        
        metric_id = f"metric_{uuid.uuid4().hex[:8]}"
        
        metric = PerformanceMetric(
            metric_id=metric_id,
            employee_id=employee_id,
            metric_type=metric_type,
            name=name,
            value=value,
            target_value=target_value,
            unit=unit,
            period=period,
            source=source
        )
        
        if employee_id not in self.metrics:
            self.metrics[employee_id] = []
        
        self.metrics[employee_id].append(metric)
        
        # Invalidate analytics cache
        self._invalidate_cache(employee_id)
        
        logger.info(f"Recorded metric for {employee_id}: {name} = {value}")
        return metric_id
    
    async def set_performance_goal(self, employee_id: str, set_by: str,
                                 title: str, description: str, metric_type: MetricType,
                                 target_value: float, unit: str = "",
                                 target_date: datetime = None,
                                 priority: str = "medium") -> str:
        """Set a performance goal for an employee"""
        if employee_id not in self.hiring_database.employees:
            logger.error(f"Employee {employee_id} not found")
            return None
        
        if target_date is None:
            target_date = datetime.now() + timedelta(days=90)  # Default 3 months
        
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        
        goal = PerformanceGoal(
            goal_id=goal_id,
            employee_id=employee_id,
            set_by=set_by,
            title=title,
            description=description,
            metric_type=metric_type,
            target_value=target_value,
            unit=unit,
            target_date=target_date,
            priority=priority
        )
        
        if employee_id not in self.goals:
            self.goals[employee_id] = []
        
        self.goals[employee_id].append(goal)
        
        logger.info(f"Set goal for {employee_id}: {title}")
        return goal_id
    
    async def update_goal_progress(self, goal_id: str, current_value: float,
                                 notes: str = "") -> bool:
        """Update progress on a performance goal"""
        for employee_id, goals in self.goals.items():
            for goal in goals:
                if goal.goal_id == goal_id:
                    old_value = goal.current_value
                    goal.current_value = current_value
                    goal.last_reviewed = datetime.now()
                    
                    # Add progress note
                    progress_note = {
                        "date": datetime.now().isoformat(),
                        "previous_value": old_value,
                        "current_value": current_value,
                        "notes": notes
                    }
                    goal.progress_notes.append(progress_note)
                    
                    # Check if goal is achieved
                    if goal.current_value >= goal.target_value and goal.status == GoalStatus.ACTIVE:
                        goal.status = GoalStatus.ACHIEVED
                        logger.info(f"Goal achieved: {goal.title}")
                    
                    return True
        
        return False
    
    async def conduct_skill_assessment(self, employee_id: str, assessor_id: str,
                                     skill_name: str, current_level: int,
                                     target_level: int, assessment_type: str = "annual") -> str:
        """Conduct a skill assessment for an employee"""
        if employee_id not in self.hiring_database.employees:
            logger.error(f"Employee {employee_id} not found")
            return None
        
        assessment_id = f"skill_{uuid.uuid4().hex[:8]}"
        
        assessment = SkillAssessment(
            assessment_id=assessment_id,
            employee_id=employee_id,
            assessor_id=assessor_id,
            skill_name=skill_name,
            current_level=current_level,
            target_level=target_level,
            assessment_type=assessment_type
        )
        
        if employee_id not in self.skill_assessments:
            self.skill_assessments[employee_id] = []
        
        self.skill_assessments[employee_id].append(assessment)
        
        logger.info(f"Skill assessment completed: {employee_id} - {skill_name}")
        return assessment_id
    
    async def generate_employee_performance_report(self, employee_id: str,
                                                 period_days: int = 90) -> Dict[str, Any]:
        """Generate comprehensive performance report for an employee"""
        if employee_id not in self.hiring_database.employees:
            return {}
        
        employee = self.hiring_database.employees[employee_id]
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        # Get recent metrics
        employee_metrics = self.metrics.get(employee_id, [])
        recent_metrics = [m for m in employee_metrics if m.measurement_date >= cutoff_date]
        
        # Get active goals
        employee_goals = self.goals.get(employee_id, [])
        active_goals = [g for g in employee_goals if g.status == GoalStatus.ACTIVE]
        
        # Get recent skill assessments
        employee_skills = self.skill_assessments.get(employee_id, [])
        recent_skills = [s for s in employee_skills if s.assessment_date >= cutoff_date]
        
        # Calculate performance metrics
        report = {
            "employee_info": {
                "employee_id": employee_id,
                "name": employee.name,
                "role": employee.role,
                "department": employee.department
            },
            "period": {
                "days": period_days,
                "start_date": cutoff_date.isoformat(),
                "end_date": datetime.now().isoformat()
            },
            "performance_summary": await self._calculate_performance_summary(employee_id, recent_metrics),
            "goal_progress": await self._analyze_goal_progress(active_goals),
            "skill_development": await self._analyze_skill_development(recent_skills),
            "productivity_analysis": await self._analyze_productivity(employee_id, period_days),
            "quality_metrics": await self._analyze_quality_metrics(employee_id, recent_metrics),
            "collaboration_score": await self._calculate_collaboration_score(employee_id, period_days),
            "trends": await self._identify_performance_trends(employee_id, period_days),
            "recommendations": await self._generate_performance_recommendations(employee_id, recent_metrics, active_goals)
        }
        
        return report
    
    async def generate_team_analytics(self, department: str = None,
                                    team_ids: List[str] = None) -> Dict[str, Any]:
        """Generate team performance analytics"""
        if department:
            employees = [emp for emp in self.hiring_database.employees.values() 
                        if emp.department == department]
        elif team_ids:
            # For simplicity, treating team_ids as employee_ids
            employees = [self.hiring_database.employees.get(tid) for tid in team_ids if tid in self.hiring_database.employees]
            employees = [emp for emp in employees if emp is not None]
        else:
            employees = list(self.hiring_database.employees.values())
        
        if not employees:
            return {}
        
        team_name = department or "Custom Team"
        
        analytics = {
            "team_info": {
                "name": team_name,
                "total_members": len(employees),
                "departments": list(set(emp.department for emp in employees))
            },
            "performance_overview": await self._calculate_team_performance_overview(employees),
            "productivity_metrics": await self._calculate_team_productivity(employees),
            "collaboration_analysis": await self._analyze_team_collaboration(employees),
            "skill_distribution": await self._analyze_team_skills(employees),
            "goal_achievement": await self._analyze_team_goal_achievement(employees),
            "performance_distribution": await self._analyze_performance_distribution(employees),
            "improvement_opportunities": await self._identify_team_improvements(employees),
            "benchmarking": await self._benchmark_team_performance(employees)
        }
        
        return analytics
    
    async def get_performance_trends(self, employee_id: str = None,
                                   metric_type: MetricType = None,
                                   period_days: int = 180) -> Dict[str, Any]:
        """Get performance trends analysis"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        if employee_id:
            employee_metrics = self.metrics.get(employee_id, [])
            metrics = [m for m in employee_metrics if m.measurement_date >= cutoff_date]
        else:
            metrics = []
            for emp_metrics in self.metrics.values():
                metrics.extend([m for m in emp_metrics if m.measurement_date >= cutoff_date])
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        trends = {
            "period": {"days": period_days, "end_date": datetime.now().isoformat()},
            "total_metrics": len(metrics),
            "trends_by_type": {},
            "overall_trend": PerformanceTrend.STABLE.value,
            "key_insights": []
        }
        
        # Group metrics by type
        by_type = {}
        for metric in metrics:
            metric_type_val = metric.metric_type.value
            if metric_type_val not in by_type:
                by_type[metric_type_val] = []
            by_type[metric_type_val].append(metric)
        
        # Analyze trends for each type
        for metric_type_val, type_metrics in by_type.items():
            type_trend = await self._calculate_metric_trend(type_metrics)
            trends["trends_by_type"][metric_type_val] = type_trend
        
        return trends
    
    async def get_performance_leaderboard(self, metric_type: MetricType = None,
                                        department: str = None,
                                        limit: int = 10) -> List[Dict[str, Any]]:
        """Get performance leaderboard"""
        leaderboard = []
        
        for employee_id, employee in self.hiring_database.employees.items():
            if department and employee.department != department:
                continue
            
            # Calculate recent performance score
            recent_metrics = self.metrics.get(employee_id, [])
            cutoff_date = datetime.now() - timedelta(days=30)  # Last 30 days
            recent_metrics = [m for m in recent_metrics if m.measurement_date >= cutoff_date]
            
            if metric_type:
                recent_metrics = [m for m in recent_metrics if m.metric_type == metric_type]
            
            if not recent_metrics:
                continue
            
            avg_score = statistics.mean([m.value for m in recent_metrics])
            
            leaderboard.append({
                "employee_id": employee_id,
                "name": employee.name,
                "role": employee.role,
                "department": employee.department,
                "score": avg_score,
                "metrics_count": len(recent_metrics)
            })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return leaderboard[:limit]
    
    async def _calculate_performance_summary(self, employee_id: str, 
                                           metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate performance summary for an employee"""
        if not metrics:
            return {"overall_score": 0.0, "metric_scores": {}, "targets_met": 0}
        
        # Group metrics by type
        by_type = {}
        for metric in metrics:
            metric_type = metric.metric_type.value
            if metric_type not in by_type:
                by_type[metric_type] = []
            by_type[metric_type].append(metric)
        
        # Calculate average scores by type
        metric_scores = {}
        targets_met = 0
        total_targets = 0
        
        for metric_type, type_metrics in by_type.items():
            avg_score = statistics.mean([m.value for m in type_metrics])
            metric_scores[metric_type] = avg_score
            
            # Count targets met
            for metric in type_metrics:
                if metric.target_value:
                    total_targets += 1
                    if metric.is_target_achieved():
                        targets_met += 1
        
        overall_score = statistics.mean(metric_scores.values()) if metric_scores else 0.0
        
        return {
            "overall_score": overall_score,
            "metric_scores": metric_scores,
            "targets_met": targets_met,
            "total_targets": total_targets,
            "target_achievement_rate": (targets_met / total_targets * 100) if total_targets > 0 else 0.0
        }
    
    async def _analyze_goal_progress(self, goals: List[PerformanceGoal]) -> Dict[str, Any]:
        """Analyze goal progress"""
        if not goals:
            return {"total_goals": 0, "on_track": 0, "at_risk": 0, "overdue": 0}
        
        on_track = 0
        at_risk = 0
        overdue = 0
        
        for goal in goals:
            if goal.is_overdue():
                overdue += 1
            elif goal.get_progress_percentage() >= 70:  # On track if >70% progress
                on_track += 1
            else:
                at_risk += 1
        
        return {
            "total_goals": len(goals),
            "on_track": on_track,
            "at_risk": at_risk,
            "overdue": overdue,
            "average_progress": statistics.mean([g.get_progress_percentage() for g in goals])
        }
    
    async def _analyze_skill_development(self, assessments: List[SkillAssessment]) -> Dict[str, Any]:
        """Analyze skill development"""
        if not assessments:
            return {"total_skills": 0, "average_level": 0.0, "skills_above_target": 0}
        
        skills_above_target = sum(1 for a in assessments if a.current_level >= a.target_level)
        avg_level = statistics.mean([a.current_level for a in assessments])
        avg_gap = statistics.mean([a.get_skill_gap() for a in assessments])
        
        return {
            "total_skills": len(assessments),
            "average_level": avg_level,
            "skills_above_target": skills_above_target,
            "average_skill_gap": avg_gap,
            "skills_by_level": self._group_skills_by_level(assessments)
        }
    
    def _group_skills_by_level(self, assessments: List[SkillAssessment]) -> Dict[str, int]:
        """Group skills by proficiency level"""
        levels = {"beginner": 0, "intermediate": 0, "advanced": 0, "expert": 0}
        
        for assessment in assessments:
            if assessment.current_level <= 3:
                levels["beginner"] += 1
            elif assessment.current_level <= 6:
                levels["intermediate"] += 1
            elif assessment.current_level <= 8:
                levels["advanced"] += 1
            else:
                levels["expert"] += 1
        
        return levels
    
    async def _analyze_productivity(self, employee_id: str, period_days: int) -> Dict[str, Any]:
        """Analyze employee productivity"""
        # Get tasks completed by employee in period
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        employee_tasks = [
            task for task in self.task_manager.tasks.values()
            if task.assigned_to == employee_id and 
               any(update.new_status == TaskStatus.COMPLETED and 
                   datetime.fromisoformat(update.timestamp) >= cutoff_date
                   for update in task.status_updates)
        ]
        
        total_tasks = len(employee_tasks)
        on_time_tasks = sum(1 for task in employee_tasks 
                          if task.due_date and datetime.now() <= task.due_date)
        
        productivity = {
            "total_tasks_completed": total_tasks,
            "on_time_completion_rate": (on_time_tasks / total_tasks * 100) if total_tasks > 0 else 0.0,
            "average_tasks_per_week": (total_tasks / period_days) * 7 if period_days > 0 else 0.0,
            "task_complexity_distribution": self._analyze_task_complexity(employee_tasks)
        }
        
        return productivity
    
    def _analyze_task_complexity(self, tasks: List[BusinessTask]) -> Dict[str, int]:
        """Analyze task complexity distribution"""
        complexity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for task in tasks:
            if task.priority == TaskPriority.LOW:
                complexity["low"] += 1
            elif task.priority == TaskPriority.MEDIUM:
                complexity["medium"] += 1
            elif task.priority == TaskPriority.HIGH:
                complexity["high"] += 1
            elif task.priority == TaskPriority.CRITICAL:
                complexity["critical"] += 1
        
        return complexity
    
    async def _analyze_quality_metrics(self, employee_id: str, 
                                     metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Analyze quality metrics"""
        quality_metrics = [m for m in metrics if m.metric_type == MetricType.QUALITY]
        
        if not quality_metrics:
            return {"average_quality": 0.0, "quality_trend": "unknown"}
        
        avg_quality = statistics.mean([m.value for m in quality_metrics])
        quality_trend = await self._calculate_metric_trend(quality_metrics)
        
        return {
            "average_quality": avg_quality,
            "quality_trend": quality_trend["trend"],
            "quality_consistency": quality_trend["consistency"]
        }
    
    async def _calculate_collaboration_score(self, employee_id: str, period_days: int) -> float:
        """Calculate collaboration score based on various factors"""
        # This is a simplified calculation
        # In a real system, this would consider meeting participation, 
        # peer feedback, cross-functional work, etc.
        
        collaboration_metrics = []
        if employee_id in self.metrics:
            collaboration_metrics = [
                m for m in self.metrics[employee_id] 
                if m.metric_type == MetricType.COLLABORATION
            ]
        
        if collaboration_metrics:
            return statistics.mean([m.value for m in collaboration_metrics])
        
        return 75.0  # Default collaboration score
    
    async def _identify_performance_trends(self, employee_id: str, period_days: int) -> Dict[str, str]:
        """Identify performance trends"""
        trends = {}
        
        if employee_id in self.metrics:
            employee_metrics = self.metrics[employee_id]
            cutoff_date = datetime.now() - timedelta(days=period_days)
            recent_metrics = [m for m in employee_metrics if m.measurement_date >= cutoff_date]
            
            # Group by metric type
            by_type = {}
            for metric in recent_metrics:
                metric_type = metric.metric_type.value
                if metric_type not in by_type:
                    by_type[metric_type] = []
                by_type[metric_type].append(metric)
            
            # Calculate trend for each type
            for metric_type, type_metrics in by_type.items():
                trend_data = await self._calculate_metric_trend(type_metrics)
                trends[metric_type] = trend_data["trend"]
        
        return trends
    
    async def _calculate_metric_trend(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """Calculate trend for a list of metrics"""
        if len(metrics) < 2:
            return {"trend": PerformanceTrend.UNKNOWN.value, "consistency": 0.0}
        
        # Sort by date
        sorted_metrics = sorted(metrics, key=lambda m: m.measurement_date)
        values = [m.value for m in sorted_metrics]
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        change_percent = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        if change_percent > 5:
            trend = PerformanceTrend.IMPROVING.value
        elif change_percent < -5:
            trend = PerformanceTrend.DECLINING.value
        else:
            trend = PerformanceTrend.STABLE.value
        
        # Calculate consistency (inverse of standard deviation)
        consistency = max(0, 100 - (statistics.stdev(values) / statistics.mean(values) * 100)) if len(values) > 1 else 0
        
        return {"trend": trend, "consistency": consistency, "change_percent": change_percent}
    
    async def _generate_performance_recommendations(self, employee_id: str,
                                                  metrics: List[PerformanceMetric],
                                                  goals: List[PerformanceGoal]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Analyze metric performance
        if metrics:
            performance_summary = await self._calculate_performance_summary(employee_id, metrics)
            
            if performance_summary["overall_score"] < 70:
                recommendations.append("Focus on improving overall performance - consider additional training or support")
            
            if performance_summary["target_achievement_rate"] < 50:
                recommendations.append("Review and adjust performance targets to be more achievable")
        
        # Analyze goal progress
        if goals:
            at_risk_goals = [g for g in goals if g.get_progress_percentage() < 50 and not g.is_overdue()]
            overdue_goals = [g for g in goals if g.is_overdue()]
            
            if at_risk_goals:
                recommendations.append(f"Focus on {len(at_risk_goals)} at-risk goals - consider breaking them into smaller milestones")
            
            if overdue_goals:
                recommendations.append(f"Address {len(overdue_goals)} overdue goals - reassess feasibility and timeline")
        
        # Default recommendations if no specific issues found
        if not recommendations:
            recommendations.append("Continue current performance level and consider stretch goals for further development")
        
        return recommendations
    
    async def _calculate_team_performance_overview(self, employees: List[Any]) -> Dict[str, Any]:
        """Calculate team performance overview"""
        total_metrics = 0
        total_score = 0.0
        
        for employee in employees:
            employee_metrics = self.metrics.get(employee.employee_id, [])
            recent_metrics = [m for m in employee_metrics 
                            if m.measurement_date >= datetime.now() - timedelta(days=30)]
            
            if recent_metrics:
                avg_score = statistics.mean([m.value for m in recent_metrics])
                total_score += avg_score
                total_metrics += 1
        
        return {
            "team_average_score": total_score / total_metrics if total_metrics > 0 else 0.0,
            "active_members": total_metrics,
            "performance_distribution": "balanced"  # Simplified
        }
    
    async def _calculate_team_productivity(self, employees: List[Any]) -> Dict[str, Any]:
        """Calculate team productivity metrics"""
        total_tasks = 0
        completed_tasks = 0
        
        for employee in employees:
            employee_tasks = [
                task for task in self.task_manager.tasks.values()
                if task.assigned_to == employee.employee_id
            ]
            
            total_tasks += len(employee_tasks)
            completed_tasks += sum(1 for task in employee_tasks 
                                 if task.status == TaskStatus.COMPLETED)
        
        return {
            "total_tasks": total_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0,
            "average_tasks_per_member": total_tasks / len(employees) if employees else 0.0
        }
    
    async def _analyze_team_collaboration(self, employees: List[Any]) -> Dict[str, Any]:
        """Analyze team collaboration"""
        collaboration_scores = []
        
        for employee in employees:
            score = await self._calculate_collaboration_score(employee.employee_id, 30)
            collaboration_scores.append(score)
        
        return {
            "average_collaboration": statistics.mean(collaboration_scores) if collaboration_scores else 0.0,
            "collaboration_distribution": "good"  # Simplified
        }
    
    async def _analyze_team_skills(self, employees: List[Any]) -> Dict[str, Any]:
        """Analyze team skill distribution"""
        all_skills = {}
        
        for employee in employees:
            employee_skills = self.skill_assessments.get(employee.employee_id, [])
            for assessment in employee_skills:
                if assessment.skill_name not in all_skills:
                    all_skills[assessment.skill_name] = []
                all_skills[assessment.skill_name].append(assessment.current_level)
        
        skill_summary = {}
        for skill_name, levels in all_skills.items():
            skill_summary[skill_name] = {
                "average_level": statistics.mean(levels),
                "team_members": len(levels)
            }
        
        return skill_summary
    
    async def _analyze_team_goal_achievement(self, employees: List[Any]) -> Dict[str, Any]:
        """Analyze team goal achievement"""
        total_goals = 0
        achieved_goals = 0
        
        for employee in employees:
            employee_goals = self.goals.get(employee.employee_id, [])
            total_goals += len(employee_goals)
            achieved_goals += sum(1 for goal in employee_goals 
                                if goal.status == GoalStatus.ACHIEVED)
        
        return {
            "total_goals": total_goals,
            "achievement_rate": (achieved_goals / total_goals * 100) if total_goals > 0 else 0.0
        }
    
    async def _analyze_performance_distribution(self, employees: List[Any]) -> Dict[str, Any]:
        """Analyze performance distribution across team"""
        performance_scores = []
        
        for employee in employees:
            employee_metrics = self.metrics.get(employee.employee_id, [])
            if employee_metrics:
                recent_metrics = [m for m in employee_metrics 
                                if m.measurement_date >= datetime.now() - timedelta(days=30)]
                if recent_metrics:
                    avg_score = statistics.mean([m.value for m in recent_metrics])
                    performance_scores.append(avg_score)
        
        if not performance_scores:
            return {"distribution": "no_data"}
        
        return {
            "mean": statistics.mean(performance_scores),
            "median": statistics.median(performance_scores),
            "std_dev": statistics.stdev(performance_scores) if len(performance_scores) > 1 else 0.0,
            "range": max(performance_scores) - min(performance_scores)
        }
    
    async def _identify_team_improvements(self, employees: List[Any]) -> List[str]:
        """Identify team improvement opportunities"""
        improvements = [
            "Implement regular peer feedback sessions",
            "Establish cross-functional collaboration initiatives", 
            "Create skill-sharing workshops",
            "Set team-based performance goals"
        ]
        
        return improvements
    
    async def _benchmark_team_performance(self, employees: List[Any]) -> Dict[str, Any]:
        """Benchmark team performance against standards"""
        # Simplified benchmarking
        return {
            "vs_industry_standard": "above_average",
            "vs_company_average": "average",
            "improvement_potential": "moderate"
        }
    
    def _invalidate_cache(self, employee_id: str):
        """Invalidate analytics cache for an employee"""
        if employee_id in self._analytics_cache:
            del self._analytics_cache[employee_id]
        if employee_id in self._cache_expiry:
            del self._cache_expiry[employee_id]


# Convenience factory function
def create_performance_tracking_system(task_manager: TaskManager, 
                                     hiring_database: HiringDatabase) -> PerformanceTrackingSystem:
    """Create a performance tracking system with standard configuration"""
    return PerformanceTrackingSystem(task_manager, hiring_database)