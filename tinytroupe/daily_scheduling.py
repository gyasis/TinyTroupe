"""
Daily Scheduling System - Employee Schedule Management and Time Tracking

This module provides comprehensive scheduling capabilities for the Virtual Business Simulation:
- Predefined employee schedules and working hours
- Task time logging and tracking
- Activity summaries and time allocation
- Schedule conflict detection and resolution
- Calendar integration and meeting scheduling
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, time, date
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import calendar

from tinytroupe.task_management import TaskManager, BusinessTask, TaskStatus
from tinytroupe.business_simulation import HiringDatabase

logger = logging.getLogger("tinytroupe.daily_scheduling")


class ActivityType(Enum):
    """Types of activities that can be scheduled"""
    TASK_WORK = "task_work"
    MEETING = "meeting"
    BREAK = "break"
    TRAINING = "training"
    ADMIN = "admin"
    PERSONAL = "personal"
    BLOCKED = "blocked"  # Unavailable time


class ScheduleConflictType(Enum):
    """Types of schedule conflicts"""
    DOUBLE_BOOKING = "double_booking"
    OVERTIME = "overtime"
    INSUFFICIENT_BREAK = "insufficient_break"
    AFTER_HOURS = "after_hours"
    HOLIDAY_CONFLICT = "holiday_conflict"


@dataclass
class WorkingHours:
    """Defines working hours for an employee"""
    start_time: time
    end_time: time
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    lunch_start: Optional[time] = None
    lunch_end: Optional[time] = None
    timezone: str = "UTC"
    
    def total_working_hours(self) -> float:
        """Calculate total working hours per day"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        total_minutes = end_minutes - start_minutes
        
        # Subtract breaks
        if self.break_start and self.break_end:
            break_minutes = (self.break_end.hour * 60 + self.break_end.minute) - \
                          (self.break_start.hour * 60 + self.break_start.minute)
            total_minutes -= break_minutes
            
        if self.lunch_start and self.lunch_end:
            lunch_minutes = (self.lunch_end.hour * 60 + self.lunch_end.minute) - \
                          (self.lunch_start.hour * 60 + self.lunch_start.minute)
            total_minutes -= lunch_minutes
            
        return total_minutes / 60.0
    
    def is_within_hours(self, check_time: time) -> bool:
        """Check if a time is within working hours"""
        if self.start_time <= check_time <= self.end_time:
            # Check if it's during break time
            if self.break_start and self.break_end:
                if self.break_start <= check_time <= self.break_end:
                    return False
            if self.lunch_start and self.lunch_end:
                if self.lunch_start <= check_time <= self.lunch_end:
                    return False
            return True
        return False


@dataclass
class ScheduledActivity:
    """Represents a scheduled activity for an employee"""
    activity_id: str
    employee_id: str
    activity_type: ActivityType
    title: str
    description: str = ""
    start_datetime: datetime = field(default_factory=datetime.now)
    end_datetime: Optional[datetime] = None
    duration_hours: float = 1.0
    
    # Task-specific fields
    task_id: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    
    # Meeting-specific fields
    attendees: List[str] = field(default_factory=list)
    meeting_location: Optional[str] = None
    
    # Status tracking
    is_completed: bool = False
    is_blocked: bool = False
    blocked_reason: Optional[str] = None
    notes: str = ""
    
    def __post_init__(self):
        """Set end_datetime if not provided"""
        if self.end_datetime is None:
            self.end_datetime = self.start_datetime + timedelta(hours=self.duration_hours)
    
    def get_actual_duration(self) -> float:
        """Get actual duration in hours"""
        if self.actual_hours is not None:
            return self.actual_hours
        elif self.end_datetime:
            return (self.end_datetime - self.start_datetime).total_seconds() / 3600
        return self.duration_hours
    
    def is_overrunning(self) -> bool:
        """Check if activity is taking longer than estimated"""
        if self.actual_hours and self.estimated_hours:
            return self.actual_hours > self.estimated_hours * 1.2  # 20% tolerance
        return False


@dataclass
class ScheduleConflict:
    """Represents a schedule conflict"""
    conflict_id: str
    conflict_type: ScheduleConflictType
    employee_id: str
    conflicting_activities: List[str]
    conflict_datetime: datetime
    severity: str  # "low", "medium", "high", "critical"
    description: str
    suggested_resolution: str
    is_resolved: bool = False
    resolution_notes: str = ""


@dataclass
class DailySchedule:
    """Complete daily schedule for an employee"""
    employee_id: str
    schedule_date: date
    working_hours: WorkingHours
    activities: List[ScheduledActivity] = field(default_factory=list)
    conflicts: List[ScheduleConflict] = field(default_factory=list)
    total_scheduled_hours: float = 0.0
    total_actual_hours: float = 0.0
    productivity_score: float = 0.0
    
    def add_activity(self, activity: ScheduledActivity):
        """Add an activity to the schedule"""
        self.activities.append(activity)
        self.total_scheduled_hours += activity.duration_hours
        self._update_metrics()
    
    def remove_activity(self, activity_id: str):
        """Remove an activity from the schedule"""
        self.activities = [a for a in self.activities if a.activity_id != activity_id]
        self._recalculate_totals()
    
    def _recalculate_totals(self):
        """Recalculate total hours"""
        self.total_scheduled_hours = sum(a.duration_hours for a in self.activities)
        self.total_actual_hours = sum(a.get_actual_duration() for a in self.activities if a.is_completed)
        self._update_metrics()
    
    def _update_metrics(self):
        """Update productivity and efficiency metrics"""
        if self.total_scheduled_hours > 0:
            completed_hours = sum(a.get_actual_duration() for a in self.activities if a.is_completed)
            self.productivity_score = (completed_hours / self.total_scheduled_hours) * 100
        else:
            self.productivity_score = 0.0


class DailySchedulingSystem:
    """
    Comprehensive Daily Scheduling System for Virtual Business Simulation
    
    Manages employee schedules, time tracking, conflict detection, and productivity analysis.
    """
    
    def __init__(self, task_manager: TaskManager, hiring_database: HiringDatabase):
        self.task_manager = task_manager
        self.hiring_database = hiring_database
        
        # Schedule storage
        self.daily_schedules: Dict[str, Dict[str, DailySchedule]] = {}  # {employee_id: {date_str: schedule}}
        self.working_hours: Dict[str, WorkingHours] = {}  # {employee_id: working_hours}
        self.activity_templates: Dict[str, Dict[str, Any]] = {}
        
        # Conflict tracking
        self.conflicts: List[ScheduleConflict] = []
        self.conflict_counter = 0
        
        # Time tracking
        self.time_logs: Dict[str, List[Dict[str, Any]]] = {}  # {employee_id: [time_entries]}
        
        # Initialize default working hours
        self._setup_default_working_hours()
    
    def _setup_default_working_hours(self):
        """Setup default working hours for all employees"""
        default_hours = WorkingHours(
            start_time=time(9, 0),    # 9:00 AM
            end_time=time(17, 0),     # 5:00 PM
            lunch_start=time(12, 0),  # 12:00 PM
            lunch_end=time(13, 0),    # 1:00 PM
            break_start=time(15, 0),  # 3:00 PM
            break_end=time(15, 15)    # 3:15 PM
        )
        
        for employee_id in self.hiring_database.employees.keys():
            self.working_hours[employee_id] = default_hours
    
    async def set_employee_working_hours(self, employee_id: str, working_hours: WorkingHours) -> bool:
        """Set custom working hours for an employee"""
        if employee_id not in self.hiring_database.employees:
            logger.error(f"Employee {employee_id} not found")
            return False
        
        self.working_hours[employee_id] = working_hours
        logger.info(f"Working hours updated for employee {employee_id}")
        return True
    
    async def create_daily_schedule(self, employee_id: str, schedule_date: date) -> Optional[DailySchedule]:
        """Create a daily schedule for an employee"""
        if employee_id not in self.hiring_database.employees:
            logger.error(f"Employee {employee_id} not found")
            return None
        
        if employee_id not in self.working_hours:
            await self._setup_default_working_hours()
        
        schedule = DailySchedule(
            employee_id=employee_id,
            schedule_date=schedule_date,
            working_hours=self.working_hours[employee_id]
        )
        
        # Store schedule
        if employee_id not in self.daily_schedules:
            self.daily_schedules[employee_id] = {}
        
        date_str = schedule_date.isoformat()
        self.daily_schedules[employee_id][date_str] = schedule
        
        logger.info(f"Created daily schedule for {employee_id} on {schedule_date}")
        return schedule
    
    async def schedule_task_work(self, employee_id: str, task_id: str, 
                               start_datetime: datetime, estimated_hours: float,
                               priority_override: bool = False) -> Optional[ScheduledActivity]:
        """Schedule task work for an employee"""
        if task_id not in self.task_manager.tasks:
            logger.error(f"Task {task_id} not found")
            return None
        
        task = self.task_manager.tasks[task_id]
        schedule_date = start_datetime.date()
        
        # Get or create daily schedule
        schedule = await self.get_daily_schedule(employee_id, schedule_date)
        if not schedule:
            schedule = await self.create_daily_schedule(employee_id, schedule_date)
        
        # Create activity
        activity = ScheduledActivity(
            activity_id=f"task_{task_id}_{datetime.now().timestamp()}",
            employee_id=employee_id,
            activity_type=ActivityType.TASK_WORK,
            title=f"Work on: {task.title}",
            description=task.description,
            start_datetime=start_datetime,
            duration_hours=estimated_hours,
            task_id=task_id,
            estimated_hours=estimated_hours
        )
        
        # Check for conflicts
        conflicts = await self._detect_schedule_conflicts(employee_id, activity)
        
        if conflicts and not priority_override:
            logger.warning(f"Schedule conflicts detected for {employee_id}: {len(conflicts)} conflicts")
            for conflict in conflicts:
                self.conflicts.append(conflict)
            return None
        
        # Add to schedule
        schedule.add_activity(activity)
        
        logger.info(f"Scheduled task work for {employee_id}: {task.title}")
        return activity
    
    async def schedule_meeting(self, organizer_id: str, attendee_ids: List[str],
                             meeting_title: str, start_datetime: datetime, 
                             duration_hours: float, location: str = "Conference Room") -> Dict[str, Any]:
        """Schedule a meeting with multiple attendees"""
        meeting_id = f"meeting_{datetime.now().timestamp()}"
        scheduled_attendees = []
        conflicts = []
        
        for attendee_id in [organizer_id] + attendee_ids:
            if attendee_id not in self.hiring_database.employees:
                logger.warning(f"Employee {attendee_id} not found, skipping")
                continue
            
            schedule_date = start_datetime.date()
            schedule = await self.get_daily_schedule(attendee_id, schedule_date)
            if not schedule:
                schedule = await self.create_daily_schedule(attendee_id, schedule_date)
            
            # Create meeting activity
            activity = ScheduledActivity(
                activity_id=f"{meeting_id}_{attendee_id}",
                employee_id=attendee_id,
                activity_type=ActivityType.MEETING,
                title=meeting_title,
                description=f"Meeting organized by {self.hiring_database.employees[organizer_id].name}",
                start_datetime=start_datetime,
                duration_hours=duration_hours,
                attendees=[organizer_id] + attendee_ids,
                meeting_location=location
            )
            
            # Check conflicts for this attendee
            attendee_conflicts = await self._detect_schedule_conflicts(attendee_id, activity)
            if attendee_conflicts:
                conflicts.extend(attendee_conflicts)
                logger.warning(f"Meeting conflicts for {attendee_id}")
            else:
                schedule.add_activity(activity)
                scheduled_attendees.append(attendee_id)
        
        result = {
            "meeting_id": meeting_id,
            "scheduled_attendees": scheduled_attendees,
            "conflicts": conflicts,
            "success": len(scheduled_attendees) > 0
        }
        
        if conflicts:
            result["conflict_resolution"] = await self._suggest_meeting_alternatives(
                attendee_ids, start_datetime, duration_hours
            )
        
        logger.info(f"Meeting scheduled: {len(scheduled_attendees)}/{len(attendee_ids + [organizer_id])} attendees")
        return result
    
    async def log_time_entry(self, employee_id: str, activity_id: str, 
                           start_time: datetime, end_time: datetime,
                           notes: str = "") -> bool:
        """Log actual time spent on an activity"""
        if employee_id not in self.hiring_database.employees:
            return False
        
        duration_hours = (end_time - start_time).total_seconds() / 3600
        
        time_entry = {
            "entry_id": f"time_{datetime.now().timestamp()}",
            "employee_id": employee_id,
            "activity_id": activity_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_hours": duration_hours,
            "notes": notes,
            "logged_at": datetime.now().isoformat()
        }
        
        if employee_id not in self.time_logs:
            self.time_logs[employee_id] = []
        
        self.time_logs[employee_id].append(time_entry)
        
        # Update activity if found
        await self._update_activity_actual_time(activity_id, duration_hours)
        
        logger.info(f"Time logged for {employee_id}: {duration_hours:.2f} hours")
        return True
    
    async def get_daily_schedule(self, employee_id: str, schedule_date: date) -> Optional[DailySchedule]:
        """Get daily schedule for an employee"""
        if employee_id not in self.daily_schedules:
            return None
        
        date_str = schedule_date.isoformat()
        return self.daily_schedules[employee_id].get(date_str)
    
    async def get_schedule_conflicts(self, employee_id: str = None, 
                                   date_range: Tuple[date, date] = None) -> List[ScheduleConflict]:
        """Get schedule conflicts with optional filtering"""
        conflicts = self.conflicts.copy()
        
        if employee_id:
            conflicts = [c for c in conflicts if c.employee_id == employee_id]
        
        if date_range:
            start_date, end_date = date_range
            conflicts = [c for c in conflicts 
                        if start_date <= c.conflict_datetime.date() <= end_date]
        
        return conflicts
    
    async def generate_activity_summary(self, employee_id: str, 
                                      date_range: Tuple[date, date]) -> Dict[str, Any]:
        """Generate comprehensive activity summary for an employee"""
        start_date, end_date = date_range
        current_date = start_date
        
        summary = {
            "employee_id": employee_id,
            "date_range": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_days": (end_date - start_date).days + 1,
            "scheduled_hours": 0.0,
            "actual_hours": 0.0,
            "productivity_score": 0.0,
            "activity_breakdown": {},
            "task_completion": {},
            "conflicts": 0,
            "overtime_hours": 0.0
        }
        
        while current_date <= end_date:
            schedule = await self.get_daily_schedule(employee_id, current_date)
            if schedule:
                summary["scheduled_hours"] += schedule.total_scheduled_hours
                summary["actual_hours"] += schedule.total_actual_hours
                summary["conflicts"] += len(schedule.conflicts)
                
                # Activity breakdown
                for activity in schedule.activities:
                    activity_type = activity.activity_type.value
                    if activity_type not in summary["activity_breakdown"]:
                        summary["activity_breakdown"][activity_type] = {
                            "count": 0, "scheduled_hours": 0.0, "actual_hours": 0.0
                        }
                    
                    summary["activity_breakdown"][activity_type]["count"] += 1
                    summary["activity_breakdown"][activity_type]["scheduled_hours"] += activity.duration_hours
                    summary["activity_breakdown"][activity_type]["actual_hours"] += activity.get_actual_duration()
                
                # Check for overtime
                working_hours_per_day = schedule.working_hours.total_working_hours()
                if schedule.total_actual_hours > working_hours_per_day:
                    summary["overtime_hours"] += schedule.total_actual_hours - working_hours_per_day
            
            current_date += timedelta(days=1)
        
        # Calculate overall productivity
        if summary["scheduled_hours"] > 0:
            summary["productivity_score"] = (summary["actual_hours"] / summary["scheduled_hours"]) * 100
        
        return summary
    
    async def detect_schedule_conflicts_for_date(self, schedule_date: date) -> List[ScheduleConflict]:
        """Detect all schedule conflicts for a specific date"""
        date_conflicts = []
        
        for employee_id in self.daily_schedules:
            schedule = await self.get_daily_schedule(employee_id, schedule_date)
            if schedule:
                for activity in schedule.activities:
                    conflicts = await self._detect_schedule_conflicts(employee_id, activity)
                    date_conflicts.extend(conflicts)
        
        return date_conflicts
    
    async def _detect_schedule_conflicts(self, employee_id: str, 
                                       new_activity: ScheduledActivity) -> List[ScheduleConflict]:
        """Detect conflicts for a new activity"""
        conflicts = []
        schedule_date = new_activity.start_datetime.date()
        schedule = await self.get_daily_schedule(employee_id, schedule_date)
        
        if not schedule:
            return conflicts
        
        # Check against existing activities
        for existing_activity in schedule.activities:
            if existing_activity.activity_id == new_activity.activity_id:
                continue
            
            # Time overlap check
            if self._activities_overlap(existing_activity, new_activity):
                conflict = ScheduleConflict(
                    conflict_id=f"conflict_{self.conflict_counter}",
                    conflict_type=ScheduleConflictType.DOUBLE_BOOKING,
                    employee_id=employee_id,
                    conflicting_activities=[existing_activity.activity_id, new_activity.activity_id],
                    conflict_datetime=new_activity.start_datetime,
                    severity="high",
                    description=f"Double booking: '{existing_activity.title}' and '{new_activity.title}'",
                    suggested_resolution=f"Reschedule one of the activities"
                )
                conflicts.append(conflict)
                self.conflict_counter += 1
        
        # Check working hours
        working_hours = schedule.working_hours
        if not working_hours.is_within_hours(new_activity.start_datetime.time()):
            conflict = ScheduleConflict(
                conflict_id=f"conflict_{self.conflict_counter}",
                conflict_type=ScheduleConflictType.AFTER_HOURS,
                employee_id=employee_id,
                conflicting_activities=[new_activity.activity_id],
                conflict_datetime=new_activity.start_datetime,
                severity="medium",
                description=f"Activity '{new_activity.title}' scheduled outside working hours",
                suggested_resolution="Reschedule to working hours or approve overtime"
            )
            conflicts.append(conflict)
            self.conflict_counter += 1
        
        return conflicts
    
    def _activities_overlap(self, activity1: ScheduledActivity, activity2: ScheduledActivity) -> bool:
        """Check if two activities overlap in time"""
        start1, end1 = activity1.start_datetime, activity1.end_datetime
        start2, end2 = activity2.start_datetime, activity2.end_datetime
        
        if not end1 or not end2:
            return False
        
        return start1 < end2 and start2 < end1
    
    async def _update_activity_actual_time(self, activity_id: str, actual_hours: float):
        """Update actual time for an activity"""
        for employee_id in self.daily_schedules:
            for date_str in self.daily_schedules[employee_id]:
                schedule = self.daily_schedules[employee_id][date_str]
                for activity in schedule.activities:
                    if activity.activity_id == activity_id:
                        activity.actual_hours = actual_hours
                        schedule._recalculate_totals()
                        return
    
    async def _suggest_meeting_alternatives(self, attendee_ids: List[str], 
                                          preferred_time: datetime, 
                                          duration_hours: float) -> List[Dict[str, Any]]:
        """Suggest alternative meeting times"""
        alternatives = []
        search_date = preferred_time.date()
        
        # Search for alternative times in the same day
        for hour in range(9, 17):  # 9 AM to 5 PM
            alt_time = datetime.combine(search_date, time(hour, 0))
            if alt_time == preferred_time:
                continue
            
            conflicts_found = False
            for attendee_id in attendee_ids:
                temp_activity = ScheduledActivity(
                    activity_id="temp",
                    employee_id=attendee_id,
                    activity_type=ActivityType.MEETING,
                    title="Alternative Meeting",
                    start_datetime=alt_time,
                    duration_hours=duration_hours
                )
                
                conflicts = await self._detect_schedule_conflicts(attendee_id, temp_activity)
                if conflicts:
                    conflicts_found = True
                    break
            
            if not conflicts_found:
                alternatives.append({
                    "suggested_time": alt_time.isoformat(),
                    "available_attendees": len(attendee_ids),
                    "conflicts": 0
                })
                
                if len(alternatives) >= 3:  # Limit to 3 suggestions
                    break
        
        return alternatives


# Convenience factory function
def create_daily_scheduling_system(task_manager: TaskManager, 
                                 hiring_database: HiringDatabase) -> DailySchedulingSystem:
    """Create a daily scheduling system with standard configuration"""
    return DailySchedulingSystem(task_manager, hiring_database)