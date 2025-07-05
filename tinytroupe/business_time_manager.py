"""
BusinessTimeManager - Virtual Time Management for Multi-Day Business Simulation

This module provides comprehensive virtual time management that enables:
- Persistent business calendar across multiple simulation days
- Virtual date/time independent of real execution time
- Business day/weekend/holiday awareness
- Integration with calendar events and task scheduling
"""

import logging
from datetime import datetime, timedelta, time, date
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger("tinytroupe.time")


class DayType(Enum):
    """Types of business days"""
    WEEKDAY = "weekday"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"
    SPECIAL = "special"  # Company events, all-hands, etc.


class TimeZone(Enum):
    """Business time zones"""
    PST = "PST"
    EST = "EST"
    UTC = "UTC"
    LOCAL = "LOCAL"


@dataclass
class BusinessHours:
    """Business operating hours configuration"""
    start_time: time = time(9, 0)      # 9:00 AM
    end_time: time = time(17, 0)       # 5:00 PM
    lunch_start: time = time(12, 0)    # 12:00 PM
    lunch_end: time = time(13, 0)      # 1:00 PM
    timezone: TimeZone = TimeZone.PST
    
    def is_business_hours(self, check_time: time) -> bool:
        """Check if given time is within business hours"""
        if check_time < self.start_time or check_time > self.end_time:
            return False
        # Check if it's lunch time
        if self.lunch_start <= check_time <= self.lunch_end:
            return False
        return True
    
    def get_total_business_hours(self) -> float:
        """Get total business hours per day (excluding lunch)"""
        total_minutes = (
            (datetime.combine(date.today(), self.end_time) - 
             datetime.combine(date.today(), self.start_time)).total_seconds() / 60
        )
        lunch_minutes = (
            (datetime.combine(date.today(), self.lunch_end) - 
             datetime.combine(date.today(), self.lunch_start)).total_seconds() / 60
        )
        return (total_minutes - lunch_minutes) / 60


@dataclass
class BusinessDay:
    """Represents a single business day with metadata"""
    date: date
    day_type: DayType
    is_working_day: bool
    business_hours: BusinessHours
    special_events: List[str] = field(default_factory=list)
    notes: str = ""
    
    def get_working_hours(self) -> float:
        """Get total working hours for this day"""
        if not self.is_working_day:
            return 0.0
        return self.business_hours.get_total_business_hours()


class BusinessCalendar:
    """
    Business calendar that tracks holidays, special events, and working days.
    Supports different business calendar configurations.
    """
    
    def __init__(self, timezone: TimeZone = TimeZone.PST):
        self.timezone = timezone
        self.holidays: Dict[date, str] = {}  # date -> holiday name
        self.special_days: Dict[date, List[str]] = {}  # date -> list of events
        self.business_hours = BusinessHours(timezone=timezone)
        self.custom_working_days: Dict[date, bool] = {}  # Override working day status
        
        # Load default US holidays
        self._load_default_holidays()
    
    def _load_default_holidays(self):
        """Load common US business holidays"""
        # 2024 holidays (can be extended or loaded from external source)
        year = 2024
        self.holidays.update({
            date(year, 1, 1): "New Year's Day",
            date(year, 1, 15): "Martin Luther King Jr. Day",
            date(year, 2, 19): "Presidents Day",
            date(year, 5, 27): "Memorial Day",
            date(year, 7, 4): "Independence Day",
            date(year, 9, 2): "Labor Day",
            date(year, 10, 14): "Columbus Day",
            date(year, 11, 11): "Veterans Day",
            date(year, 11, 28): "Thanksgiving",
            date(year, 12, 25): "Christmas Day"
        })
    
    def add_holiday(self, holiday_date: date, name: str):
        """Add a custom holiday"""
        self.holidays[holiday_date] = name
        logger.info(f"Added holiday: {name} on {holiday_date}")
    
    def add_special_event(self, event_date: date, event_name: str):
        """Add a special business event"""
        if event_date not in self.special_days:
            self.special_days[event_date] = []
        self.special_days[event_date].append(event_name)
        logger.info(f"Added special event: {event_name} on {event_date}")
    
    def set_custom_working_day(self, day_date: date, is_working: bool):
        """Override default working day status"""
        self.custom_working_days[day_date] = is_working
        logger.info(f"Set {day_date} as {'working' if is_working else 'non-working'} day")
    
    def get_business_day(self, day_date: date) -> BusinessDay:
        """Get complete business day information"""
        # Check if it's a holiday
        if day_date in self.holidays:
            return BusinessDay(
                date=day_date,
                day_type=DayType.HOLIDAY,
                is_working_day=False,
                business_hours=self.business_hours,
                notes=f"Holiday: {self.holidays[day_date]}"
            )
        
        # Check for custom working day override
        if day_date in self.custom_working_days:
            is_working = self.custom_working_days[day_date]
            day_type = DayType.SPECIAL if is_working else DayType.WEEKEND
        else:
            # Check if it's a weekend
            is_weekend = day_date.weekday() >= 5  # Saturday=5, Sunday=6
            is_working = not is_weekend
            day_type = DayType.WEEKEND if is_weekend else DayType.WEEKDAY
        
        # Get special events
        special_events = self.special_days.get(day_date, [])
        
        return BusinessDay(
            date=day_date,
            day_type=day_type,
            is_working_day=is_working,
            business_hours=self.business_hours,
            special_events=special_events
        )
    
    def get_next_working_day(self, from_date: date) -> date:
        """Get the next working day after the given date"""
        current_date = from_date + timedelta(days=1)
        while True:
            business_day = self.get_business_day(current_date)
            if business_day.is_working_day:
                return current_date
            current_date += timedelta(days=1)
            
            # Safety check to prevent infinite loop
            if (current_date - from_date).days > 365:
                logger.error("Could not find next working day within a year")
                return from_date + timedelta(days=1)
    
    def get_working_days_between(self, start_date: date, end_date: date) -> List[date]:
        """Get all working days between start and end date (inclusive)"""
        working_days = []
        current_date = start_date
        
        while current_date <= end_date:
            business_day = self.get_business_day(current_date)
            if business_day.is_working_day:
                working_days.append(current_date)
            current_date += timedelta(days=1)
        
        return working_days


class BusinessTimeManager:
    """
    Central time management system for persistent multi-day business simulation.
    
    Provides virtual time tracking, business calendar integration, and
    simulation scheduling capabilities.
    """
    
    def __init__(self, start_date: date = None, 
                 timezone: TimeZone = TimeZone.PST,
                 simulation_speed: float = 1.0):
        """
        Initialize BusinessTimeManager.
        
        Args:
            start_date: Starting virtual date for simulation
            timezone: Business timezone
            simulation_speed: Speed multiplier (1.0 = real time, 2.0 = 2x speed)
        """
        self.current_virtual_date = start_date or date.today()
        self.current_virtual_time = time(9, 0)  # Start at 9 AM
        self.simulation_start_time = datetime.now()
        self.simulation_speed = simulation_speed
        
        # Business calendar
        self.calendar = BusinessCalendar(timezone)
        
        # Time tracking
        self.simulation_days_elapsed = 0
        self.total_business_hours_simulated = 0.0
        
        # Event tracking
        self.daily_events: Dict[date, List[Dict[str, Any]]] = {}
        
        logger.info(f"Initialized BusinessTimeManager starting {self.current_virtual_date}")
    
    def get_current_virtual_datetime(self) -> datetime:
        """Get current virtual date and time as datetime object"""
        return datetime.combine(self.current_virtual_date, self.current_virtual_time)
    
    def get_current_business_day(self) -> BusinessDay:
        """Get current business day information"""
        return self.calendar.get_business_day(self.current_virtual_date)
    
    def advance_to_next_business_day(self) -> BusinessDay:
        """Advance to the next business day and return it"""
        self.current_virtual_date = self.calendar.get_next_working_day(self.current_virtual_date)
        self.current_virtual_time = self.calendar.business_hours.start_time
        self.simulation_days_elapsed += 1
        
        business_day = self.get_current_business_day()
        logger.info(f"Advanced to next business day: {self.current_virtual_date} ({business_day.day_type.value})")
        
        return business_day
    
    def advance_to_next_day(self) -> BusinessDay:
        """Advance to the next calendar day (including weekends/holidays)"""
        self.current_virtual_date += timedelta(days=1)
        self.current_virtual_time = self.calendar.business_hours.start_time
        self.simulation_days_elapsed += 1
        
        business_day = self.get_current_business_day()
        logger.info(f"Advanced to next day: {self.current_virtual_date} ({business_day.day_type.value})")
        
        return business_day
    
    def advance_time(self, hours: float) -> bool:
        """
        Advance virtual time by specified hours.
        
        Returns True if still within business hours, False if day ended.
        """
        current_datetime = self.get_current_virtual_datetime()
        new_datetime = current_datetime + timedelta(hours=hours)
        
        # Check if we've moved to a new day
        if new_datetime.date() != self.current_virtual_date:
            # Move to end of current business day
            self.current_virtual_time = self.calendar.business_hours.end_time
            return False
        
        self.current_virtual_time = new_datetime.time()
        
        # Check if still in business hours
        business_day = self.get_current_business_day()
        if business_day.is_working_day:
            return business_day.business_hours.is_business_hours(self.current_virtual_time)
        
        return False
    
    def set_virtual_date(self, new_date: date):
        """Set virtual date directly (for loading saved states)"""
        old_date = self.current_virtual_date
        self.current_virtual_date = new_date
        logger.info(f"Set virtual date: {old_date} → {new_date}")
    
    def is_business_hours(self) -> bool:
        """Check if current virtual time is within business hours"""
        business_day = self.get_current_business_day()
        if not business_day.is_working_day:
            return False
        return business_day.business_hours.is_business_hours(self.current_virtual_time)
    
    def get_remaining_business_hours_today(self) -> float:
        """Get remaining business hours in current day"""
        business_day = self.get_current_business_day()
        if not business_day.is_working_day:
            return 0.0
        
        current_datetime = self.get_current_virtual_datetime()
        end_datetime = datetime.combine(self.current_virtual_date, business_day.business_hours.end_time)
        
        if current_datetime >= end_datetime:
            return 0.0
        
        remaining_hours = (end_datetime - current_datetime).total_seconds() / 3600
        
        # Account for lunch break if we haven't passed it yet
        lunch_start = datetime.combine(self.current_virtual_date, business_day.business_hours.lunch_start)
        lunch_end = datetime.combine(self.current_virtual_date, business_day.business_hours.lunch_end)
        
        if current_datetime < lunch_start and end_datetime > lunch_end:
            lunch_duration = (lunch_end - lunch_start).total_seconds() / 3600
            remaining_hours -= lunch_duration
        
        return max(0.0, remaining_hours)
    
    def schedule_event(self, event_date: date, event_data: Dict[str, Any]):
        """Schedule an event for a specific date"""
        if event_date not in self.daily_events:
            self.daily_events[event_date] = []
        
        self.daily_events[event_date].append({
            **event_data,
            "scheduled_time": datetime.now(),
            "event_id": f"evt_{len(self.daily_events[event_date])}"
        })
        
        logger.info(f"Scheduled event for {event_date}: {event_data.get('title', 'Untitled')}")
    
    def get_events_for_date(self, event_date: date) -> List[Dict[str, Any]]:
        """Get all scheduled events for a specific date"""
        return self.daily_events.get(event_date, [])
    
    def get_events_for_current_day(self) -> List[Dict[str, Any]]:
        """Get all scheduled events for current virtual date"""
        return self.get_events_for_date(self.current_virtual_date)
    
    def calculate_business_days_until(self, target_date: date) -> int:
        """Calculate number of business days from current date to target date"""
        if target_date <= self.current_virtual_date:
            return 0
        
        working_days = self.calendar.get_working_days_between(
            self.current_virtual_date + timedelta(days=1), 
            target_date
        )
        return len(working_days)
    
    def get_time_summary(self) -> Dict[str, Any]:
        """Get comprehensive time tracking summary"""
        current_business_day = self.get_current_business_day()
        
        return {
            "current_virtual_date": self.current_virtual_date.isoformat(),
            "current_virtual_time": self.current_virtual_time.isoformat(),
            "current_datetime": self.get_current_virtual_datetime().isoformat(),
            "day_type": current_business_day.day_type.value,
            "is_working_day": current_business_day.is_working_day,
            "is_business_hours": self.is_business_hours(),
            "remaining_business_hours_today": self.get_remaining_business_hours_today(),
            "simulation_days_elapsed": self.simulation_days_elapsed,
            "total_business_hours_simulated": self.total_business_hours_simulated,
            "timezone": self.calendar.timezone.value,
            "events_today": len(self.get_events_for_current_day()),
            "special_events": current_business_day.special_events
        }
    
    def save_state(self) -> Dict[str, Any]:
        """Save complete time manager state for persistence"""
        return {
            "current_virtual_date": self.current_virtual_date.isoformat(),
            "current_virtual_time": self.current_virtual_time.isoformat(),
            "simulation_days_elapsed": self.simulation_days_elapsed,
            "total_business_hours_simulated": self.total_business_hours_simulated,
            "simulation_speed": self.simulation_speed,
            "timezone": self.calendar.timezone.value,
            "daily_events": {
                date_str: events for date_str, events in 
                [(d.isoformat(), evts) for d, evts in self.daily_events.items()]
            },
            "custom_holidays": {
                d.isoformat(): name for d, name in self.calendar.holidays.items()
            },
            "custom_working_days": {
                d.isoformat(): working for d, working in self.calendar.custom_working_days.items()
            }
        }
    
    def load_state(self, state_data: Dict[str, Any]):
        """Load time manager state from saved data"""
        self.current_virtual_date = date.fromisoformat(state_data["current_virtual_date"])
        self.current_virtual_time = time.fromisoformat(state_data["current_virtual_time"])
        self.simulation_days_elapsed = state_data.get("simulation_days_elapsed", 0)
        self.total_business_hours_simulated = state_data.get("total_business_hours_simulated", 0.0)
        self.simulation_speed = state_data.get("simulation_speed", 1.0)
        
        # Load timezone
        timezone_str = state_data.get("timezone", "PST")
        self.calendar.timezone = TimeZone(timezone_str)
        
        # Load daily events
        self.daily_events = {}
        for date_str, events in state_data.get("daily_events", {}).items():
            event_date = date.fromisoformat(date_str)
            self.daily_events[event_date] = events
        
        # Load custom holidays
        for date_str, name in state_data.get("custom_holidays", {}).items():
            holiday_date = date.fromisoformat(date_str)
            self.calendar.holidays[holiday_date] = name
        
        # Load custom working days
        for date_str, working in state_data.get("custom_working_days", {}).items():
            working_date = date.fromisoformat(date_str)
            self.calendar.custom_working_days[working_date] = working
        
        logger.info(f"Loaded time manager state for {self.current_virtual_date}")


# Convenience functions for common operations
def create_business_time_manager(start_date: date = None) -> BusinessTimeManager:
    """Create a standard business time manager with common settings"""
    return BusinessTimeManager(
        start_date=start_date or date.today(),
        timezone=TimeZone.PST,
        simulation_speed=1.0
    )


def get_business_day_info(check_date: date, timezone: TimeZone = TimeZone.PST) -> BusinessDay:
    """Get business day information for a specific date"""
    calendar = BusinessCalendar(timezone)
    return calendar.get_business_day(check_date)