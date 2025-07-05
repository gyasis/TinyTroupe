"""
Async Agent Extensions for TinyTroupe - Concurrent agent processing

This module provides AsyncTinyPerson class that extends TinyPerson with
asynchronous capabilities while maintaining full backward compatibility.
Users can choose between sync and async methods as needed.
"""

import asyncio
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime
import threading
from enum import Enum

# Import base classes
from .agent import TinyPerson, AgentOrWorld
from .async_event_bus import get_event_bus, EventType, Event, CEOInterruptEvent
from . import openai_utils
from .control import current_simulation

logger = logging.getLogger("tinytroupe")


class AsyncAgentState(Enum):
    """Enum for async agent states"""
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    ACTING = "ACTING"
    CEO_INSTRUCTION_FOLLOWING = "CEO_INSTRUCTION_FOLLOWING"


class AsyncTinyPerson(TinyPerson):
    """
    Async-enabled TinyPerson that coexists with synchronous version
    
    Features:
    - Async versions of listen(), act(), listen_and_act()
    - CEO interrupt handling and event bus integration
    - Concurrent agent processing capabilities
    - Full backward compatibility with sync methods
    - Thread-safe state management
    """
    
    def __init__(self, name: str = None, **kwargs):
        """
        Initialize AsyncTinyPerson with async capabilities
        
        Args:
            name: Agent name
            **kwargs: Additional arguments passed to TinyPerson
        """
        super().__init__(name, **kwargs)
        
        # Async-specific attributes
        self._async_lock = asyncio.Lock()  # Protect async state access
        self._state_lock = threading.Lock()  # Protect sync state access
        self._async_actions_buffer = []  # Async-specific action buffer
        self._ceo_interrupt_event = asyncio.Event()  # CEO interrupt signal
        self._current_async_task: Optional[asyncio.Task] = None
        self._event_bus = None  # Will be set when needed
        self._interrupt_context = {}  # Store interrupt context
        
        # Agent state for async operations
        self.async_state = AsyncAgentState.IDLE
        self._last_interrupt_message = None
        self._event_bus_initialized = False  # Track initialization
        
        logger.debug(f"AsyncTinyPerson {self.name} initialized")
        
        # Initialize event bus once during creation
        asyncio.create_task(self._initialize_event_bus())
        
    async def _initialize_event_bus(self):
        """Initialize the event bus and subscribe to events (called once)"""
        if not self._event_bus_initialized:
            await self._ensure_event_bus()
            self._event_bus_initialized = True
            
    async def _ensure_event_bus(self):
        """Ensure event bus is available for async operations"""
        if self._event_bus is None:
            self._event_bus = await get_event_bus()
            # Subscribe to CEO interrupt events
            await self._event_bus.subscribe(EventType.CEO_INTERRUPT, self._handle_ceo_interrupt_event)
            
    async def async_listen(self, 
                          speech: str,
                          source: AgentOrWorld = None,
                          max_content_length: int = None) -> Any:
        """
        Async version of listen() method
        
        Args:
            speech: The stimulus/message to listen to
            source: Source of the message (agent or world)
            max_content_length: Maximum content length for display
            
        Returns:
            Result of listening operation
        """
        # Ensure event bus is available (no-op if already initialized)
        if not self._event_bus_initialized:
            await self._ensure_event_bus()
        
        async with self._async_lock:
            old_state = self.async_state
            self.async_state = AsyncAgentState.LISTENING
            
            try:
                logger.debug(f"AsyncTinyPerson {self.name} async_listen started")
                
                # Check for CEO interrupt before processing
                if self._ceo_interrupt_event.is_set():
                    await self._process_ceo_interrupt()
                    
                # Run sync listen in executor to avoid blocking event loop
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None, 
                    self._sync_listen_wrapper,
                    speech, source, max_content_length
                )
                
                # Publish agent message event
                await self._publish_agent_event("message_received", {
                    "speech": speech,
                    "source": source.name if hasattr(source, 'name') else str(source),
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.debug(f"AsyncTinyPerson {self.name} async_listen completed")
                return result
                
            except Exception as error:
                logger.error(f"Error in async_listen for {self.name}: {error}")
                raise
            finally:
                # Fix race condition: restore state inside lock
                self.async_state = old_state
                
    def _sync_listen_wrapper(self, speech, source, max_content_length):
        """Wrapper for sync listen method with thread safety"""
        try:
            with self._state_lock:
                max_len = max_content_length or self.__class__.PP_TEXT_WIDTH
                return self.listen(speech, source, max_len)
        except Exception as error:
            logger.exception(f"Error in _sync_listen_wrapper for {self.name}: {error}")
            raise
            
    async def async_act(self, 
                       until_done: bool = True,
                       n: Optional[int] = None,
                       return_actions: bool = False,
                       max_content_length: int = None,
                       current_round: Optional[int] = None,
                       total_rounds: Optional[int] = None) -> Any:
        """
        Async version of act() method
        
        Args:
            until_done: Act until agent is done
            n: Number of actions to perform
            return_actions: Whether to return actions
            max_content_length: Maximum content length for display
            current_round: Current simulation round
            total_rounds: Total simulation rounds
            
        Returns:
            Result of acting operation
        """
        # Ensure event bus is available (no-op if already initialized)
        if not self._event_bus_initialized:
            await self._ensure_event_bus()
        
        async with self._async_lock:
            old_state = self.async_state
            self.async_state = AsyncAgentState.ACTING
            
            try:
                logger.debug(f"AsyncTinyPerson {self.name} async_act started")
                
                # Check for CEO interrupt before processing
                if self._ceo_interrupt_event.is_set():
                    await self._process_ceo_interrupt()
                    return [] if return_actions else None
                    
                # Run sync act in executor
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None,
                    self._sync_act_wrapper,
                    until_done, n, return_actions, max_content_length,
                    current_round, total_rounds
                )
                
                # Publish agent action event
                await self._publish_agent_event("action_performed", {
                    "until_done": until_done,
                    "n": n,
                    "current_round": current_round,
                    "total_rounds": total_rounds,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.debug(f"AsyncTinyPerson {self.name} async_act completed")
                return result
                
            except Exception as error:
                logger.error(f"Error in async_act for {self.name}: {error}")
                raise
            finally:
                # Fix race condition: restore state inside lock
                self.async_state = old_state
                
    def _sync_act_wrapper(self, until_done, n, return_actions, max_content_length,
                         current_round, total_rounds):
        """Wrapper for sync act method with thread safety"""
        try:
            with self._state_lock:
                max_len = max_content_length or self.__class__.PP_TEXT_WIDTH
                return self.act(
                    until_done=until_done,
                    n=n,
                    return_actions=return_actions,
                    max_content_length=max_len,
                    current_round=current_round,
                    total_rounds=total_rounds
                )
        except Exception as error:
            logger.exception(f"Error in _sync_act_wrapper for {self.name}: {error}")
            raise
            
    async def async_listen_and_act(self,
                                  speech: str,
                                  return_actions: bool = False,
                                  max_content_length: int = None) -> Any:
        """
        Async version of listen_and_act() method
        
        Args:
            speech: The stimulus/message to listen to
            return_actions: Whether to return actions
            max_content_length: Maximum content length for display
            
        Returns:
            Result of listen and act operation
        """
        # Ensure event bus is available (no-op if already initialized)
        if not self._event_bus_initialized:
            await self._ensure_event_bus()
        
        async with self._async_lock:
            old_state = self.async_state
            self.async_state = AsyncAgentState.LISTENING
            
            try:
                logger.debug(f"AsyncTinyPerson {self.name} async_listen_and_act started")
                
                # Check for CEO interrupt
                if self._ceo_interrupt_event.is_set():
                    await self._process_ceo_interrupt()
                    return [] if return_actions else None
                    
                # Run sync listen_and_act in executor
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None,
                    self._sync_listen_and_act_wrapper,
                    speech, return_actions, max_content_length
                )
                
                # Publish combined event
                await self._publish_agent_event("listen_and_act_performed", {
                    "speech": speech,
                    "return_actions": return_actions,
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.debug(f"AsyncTinyPerson {self.name} async_listen_and_act completed")
                return result
                
            except Exception as error:
                logger.error(f"Error in async_listen_and_act for {self.name}: {error}")
                raise
            finally:
                # Fix race condition: restore state inside lock
                self.async_state = old_state
                
    def _sync_listen_and_act_wrapper(self, speech, return_actions, max_content_length):
        """Wrapper for sync listen_and_act method with thread safety"""
        try:
            with self._state_lock:
                max_len = max_content_length or self.__class__.PP_TEXT_WIDTH
                return self.listen_and_act(
                    speech=speech,
                    return_actions=return_actions,
                    max_content_length=max_len
                )
        except Exception as error:
            logger.exception(f"Error in _sync_listen_and_act_wrapper for {self.name}: {error}")
            raise
            
    async def _handle_ceo_interrupt_event(self, event: CEOInterruptEvent):
        """Handle incoming CEO interrupt events from event bus"""
        try:
            logger.info(f"AsyncTinyPerson {self.name} received CEO interrupt: {event.data.get('message', '')}")
            
            # Store interrupt context
            self._interrupt_context = {
                "message": event.data.get("message", ""),
                "override_context": event.data.get("override_context", True),
                "resume_action": event.data.get("resume_action", "continue"),
                "timestamp": event.timestamp
            }
            
            # Set interrupt event to signal async methods
            self._ceo_interrupt_event.set()
            
            # Cancel current async task if running
            if self._current_async_task and not self._current_async_task.done():
                self._current_async_task.cancel()
                logger.debug(f"Cancelled current async task for {self.name}")
                
        except Exception as error:
            logger.error(f"Error handling CEO interrupt event for {self.name}: {error}")
            
    async def _process_ceo_interrupt(self):
        """Process CEO interrupt when detected during async operations"""
        try:
            if not self._interrupt_context:
                logger.warning(f"CEO interrupt event set but no context for {self.name}")
                return
                
            old_state = self.async_state
            self.async_state = AsyncAgentState.CEO_INSTRUCTION_FOLLOWING
            
            message = self._interrupt_context.get("message", "")
            override_context = self._interrupt_context.get("override_context", True)
            
            logger.info(f"AsyncTinyPerson {self.name} processing CEO interrupt: {message}")
            
            if override_context and message:
                # Update agent context with CEO directive
                if hasattr(self, '_configuration'):
                    self._configuration["current_context"] = [
                        f"CEO DIRECTIVE: {message}",
                        f"Interrupt received at: {self._interrupt_context.get('timestamp', 'unknown')}"
                    ]
                    
                # Store the message for potential use in next actions
                self._last_interrupt_message = message
                
            # Clear interrupt event
            self._ceo_interrupt_event.clear()
            self._interrupt_context = {}
            
            # Publish state change event
            await self._publish_agent_event("ceo_interrupt_processed", {
                "message": message,
                "override_context": override_context,
                "previous_state": old_state,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.debug(f"AsyncTinyPerson {self.name} CEO interrupt processed")
            
        except Exception as error:
            logger.error(f"Error processing CEO interrupt for {self.name}: {error}")
            # Always clear the event to prevent infinite loops
            self._ceo_interrupt_event.clear()
            
    async def _publish_agent_event(self, action: str, data: Dict[str, Any]):
        """Publish agent events to the event bus"""
        try:
            if self._event_bus:
                event = Event(
                    event_type=EventType.AGENT_MESSAGE,
                    source=self.name,
                    data={
                        "action": action,
                        "agent_state": self.async_state.value,  # Convert enum to string
                        **data
                    }
                )
                await self._event_bus.publish(event)
        except Exception as error:
            logger.error(f"Error publishing agent event for {self.name}: {error}")
            
    async def get_async_state(self) -> AsyncAgentState:
        """Get current async state of the agent"""
        return self.async_state
        
    async def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for any running async operations to complete"""
        if self._current_async_task and not self._current_async_task.done():
            try:
                await asyncio.wait_for(self._current_async_task, timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout waiting for {self.name} async task completion")
                self._current_async_task.cancel()
                
    async def cancel_async_operations(self):
        """Cancel any running async operations"""
        if self._current_async_task and not self._current_async_task.done():
            self._current_async_task.cancel()
            try:
                await self._current_async_task
            except asyncio.CancelledError:
                pass
            logger.debug(f"Cancelled async operations for {self.name}")
            
    def __del__(self):
        """Cleanup async resources"""
        try:
            # Cancel any pending async operations
            if hasattr(self, '_current_async_task') and self._current_async_task:
                if not self._current_async_task.done():
                    self._current_async_task.cancel()
        except Exception:
            # Ignore errors during cleanup
            pass


# Utility functions for creating async agents
async def create_async_agent(name: str, **kwargs) -> AsyncTinyPerson:
    """
    Create an AsyncTinyPerson instance with event bus setup
    
    Args:
        name: Agent name
        **kwargs: Additional arguments for TinyPerson initialization
        
    Returns:
        Configured AsyncTinyPerson instance
    """
    agent = AsyncTinyPerson(name, **kwargs)
    await agent._ensure_event_bus()
    logger.info(f"Created async agent: {name}")
    return agent


async def run_agents_concurrently(agents: List[AsyncTinyPerson], 
                                 stimuli: List[str],
                                 timeout: Optional[float] = None) -> List[Any]:
    """
    Run multiple async agents concurrently with stimuli
    
    Args:
        agents: List of AsyncTinyPerson instances
        stimuli: List of stimuli (one per agent)
        timeout: Optional timeout for all operations
        
    Returns:
        List of results from each agent
    """
    if len(agents) != len(stimuli):
        raise ValueError("Number of agents must match number of stimuli")
        
    tasks = []
    for agent, stimulus in zip(agents, stimuli):
        task = asyncio.create_task(agent.async_listen_and_act(stimulus))
        tasks.append(task)
        
    try:
        results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)
        logger.info(f"Completed concurrent execution for {len(agents)} agents")
        return results
    except asyncio.TimeoutError:
        logger.warning(f"Timeout during concurrent agent execution")
        # Cancel all tasks
        for task in tasks:
            task.cancel()
        raise


# Backward compatibility - users can import and use both sync and async versions
__all__ = [
    'AsyncTinyPerson',
    'create_async_agent', 
    'run_agents_concurrently'
]