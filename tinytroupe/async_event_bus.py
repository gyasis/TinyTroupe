"""
Async Event Bus for TinyTroupe - Handles CEO interrupts and agent communication

This module provides the core event-driven architecture for async agent interactions
and CEO interrupt functionality. It enables real-time simulation control and
concurrent agent processing.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import collections

logger = logging.getLogger("tinytroupe")


class EventType(Enum):
    """Types of events that can be published through the event bus"""
    CEO_INTERRUPT = "ceo_interrupt"
    AGENT_MESSAGE = "agent_message"
    SIMULATION_PAUSE = "simulation_pause"
    SIMULATION_RESUME = "simulation_resume"
    SIMULATION_END = "simulation_end"
    AGENT_STATE_CHANGE = "agent_state_change"


@dataclass
class Event:
    """Base event class for all events in the system"""
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    target: Optional[str] = None
    priority: int = 0  # Higher numbers = higher priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "source": self.source,
            "target": self.target,
            "priority": self.priority
        }


@dataclass
class CEOInterruptEvent(Event):
    """CEO interrupt event with specific message and override instructions"""
    message: str = ""
    override_context: bool = True
    resume_action: str = "continue"  # "continue", "steer", "end"
    
    def __init__(self, message: str = "", override_context: bool = True, resume_action: str = "continue", **kwargs):
        # Initialize parent with CEO interrupt event type
        super().__init__(
            event_type=EventType.CEO_INTERRUPT,
            priority=100,  # Highest priority
            **kwargs
        )
        self.message = message
        self.override_context = override_context
        self.resume_action = resume_action
        
        # Update data dict
        self.data.update({
            "message": self.message,
            "override_context": self.override_context,
            "resume_action": self.resume_action
        })


class AsyncEventBus:
    """
    Async event bus for managing events between agents and CEO control
    
    Features:
    - Concurrent event delivery
    - Priority-based event handling
    - CEO interrupt support
    - Agent subscription management
    - Event logging and audit trail
    """
    
    def __init__(self, max_log_size: int = 1000):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running = False
        self.event_log: collections.deque = collections.deque(maxlen=max_log_size)
        self.max_log_size = max_log_size
        self._processor_task: Optional[asyncio.Task] = None
        self._bus_lock = asyncio.Lock()  # Protect critical sections
        
    async def subscribe(self, event_type: EventType, callback: Callable[[Event], Any]):
        """Subscribe to events of a specific type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type.value} events")
        
    async def unsubscribe(self, event_type: EventType, callback: Callable[[Event], Any]):
        """Unsubscribe from events of a specific type"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed from {event_type.value} events")
            except ValueError:
                logger.warning(f"Callback not found for {event_type.value} events")
                
    async def publish(self, event: Event):
        """Publish an event to the event bus"""
        try:
            # Add to event log (deque handles maxlen automatically)
            self.event_log.append(event)
            
            # Add to priority queue (negative priority for max-heap behavior)
            await self.event_queue.put((-event.priority, event.timestamp, event))
            
            logger.debug(f"Published event: {event.event_type.value} from {event.source}")
        except Exception as error:
            logger.error(f"Error publishing event: {error}")
            raise
        
    async def start(self):
        """Start the event bus processor"""
        if self.running:
            return
            
        self.running = True
        self._processor_task = asyncio.create_task(self._process_events())
        logger.info("Event bus started")
        
    async def stop(self):
        """Stop the event bus processor"""
        if not self.running:
            return
            
        self.running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Event bus stopped")
        
    async def _process_events(self):
        """Process events from the queue"""
        while self.running:
            try:
                # Wait for events with timeout to allow graceful shutdown
                priority, timestamp, event = await asyncio.wait_for(
                    self.event_queue.get(), timeout=1.0
                )
                
                # Deliver event to subscribers
                await self._deliver_event(event)
                
            except asyncio.TimeoutError:
                # Timeout is expected - allows checking running flag
                continue
            except asyncio.CancelledError:
                logger.debug("Event processor cancelled")
                break
            except Exception as error:
                logger.error(f"Error processing event: {error}")
                
    async def _deliver_event(self, event: Event):
        """Deliver event to all subscribers"""
        if event.event_type not in self.subscribers:
            logger.debug(f"No subscribers for event type: {event.event_type.value}")
            return
            
        # Create tasks for concurrent delivery
        tasks = []
        for callback in self.subscribers[event.event_type]:
            task = asyncio.create_task(self._safe_callback(callback, event))
            tasks.append(task)
            
        # Wait for all callbacks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _safe_callback(self, callback: Callable, event: Event):
        """Safely execute callback with error handling"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as error:
            logger.error(f"Error in event callback: {error}")
            
    async def publish_ceo_interrupt(self, message: str, override_context: bool = True, 
                                   resume_action: str = "continue"):
        """Convenience method for publishing CEO interrupt events"""
        try:
            event = CEOInterruptEvent(
                message=message,
                override_context=override_context,
                resume_action=resume_action,
                source="CEO"
            )
            await self.publish(event)
        except Exception as error:
            logger.error(f"Error publishing CEO interrupt: {error}")
            raise
        
    def get_event_log(self) -> List[Dict[str, Any]]:
        """Get event log as serializable dictionaries"""
        return [event.to_dict() for event in self.event_log]
        
    def clear_event_log(self):
        """Clear the event log"""
        self.event_log.clear()
        
    async def wait_for_event(self, event_type: EventType, timeout: float = None) -> Optional[Event]:
        """Wait for a specific event type (useful for testing)"""
        event_queue: asyncio.Queue[Event] = asyncio.Queue()
        
        async def event_handler(event: Event):
            await event_queue.put(event)
            
        await self.subscribe(event_type, event_handler)
        
        try:
            return await asyncio.wait_for(event_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            await self.unsubscribe(event_type, event_handler)


# Global event bus instance
_global_event_bus: Optional[AsyncEventBus] = None
_global_event_bus_lock = asyncio.Lock()


async def get_event_bus() -> AsyncEventBus:
    """Get the global event bus instance (thread-safe)"""
    global _global_event_bus
    async with _global_event_bus_lock:
        if _global_event_bus is None:
            _global_event_bus = AsyncEventBus()
    return _global_event_bus


async def initialize_event_bus():
    """Initialize and start the global event bus"""
    event_bus = await get_event_bus()
    await event_bus.start()
    return event_bus


async def shutdown_event_bus():
    """Shutdown the global event bus"""
    global _global_event_bus
    async with _global_event_bus_lock:
        if _global_event_bus:
            await _global_event_bus.stop()
            _global_event_bus = None