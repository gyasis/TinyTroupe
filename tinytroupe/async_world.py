"""
AsyncTinyWorld - Async version of TinyWorld for concurrent agent simulations
with CEO interrupt and event-driven architecture support.

This module extends TinyWorld with async capabilities while maintaining
full backward compatibility with existing TinyTroupe functionality.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import threading

from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson
from tinytroupe.async_agent import AsyncTinyPerson
from tinytroupe.async_event_bus import get_event_bus, EventType, Event
from tinytroupe.ceo_interrupt import start_ceo_monitoring, stop_ceo_monitoring, CEOInterruptHandler
import tinytroupe.control as control
from tinytroupe.control import transactional

logger = logging.getLogger("tinytroupe")


class AsyncTinyWorld(TinyWorld):
    """
    Async version of TinyWorld that supports concurrent agent processing
    with CEO interrupt and real-time simulation control.
    
    Features:
    - Concurrent agent execution using asyncio
    - CEO interrupt handling with simulation steering
    - Event-driven architecture for agent communication
    - Backward compatibility with synchronous TinyWorld
    - Thread-safe state management
    """
    
    def __init__(self, name: str = "An Async TinyWorld", agents=[], 
                 initial_datetime=datetime.now(),
                 broadcast_if_no_target=True,
                 max_additional_targets_to_display=3,
                 is_meeting=False,
                 enable_ceo_interrupt=True,
                 ceo_interrupt_keys=['space']):
        """
        Initialize AsyncTinyWorld with async capabilities.
        
        Args:
            name: World name
            agents: List of agents (can be mix of TinyPerson and AsyncTinyPerson)
            initial_datetime: Starting simulation time
            broadcast_if_no_target: Whether to broadcast when target not found
            max_additional_targets_to_display: Max targets in communication display
            is_meeting: Whether this is a meeting context (broadcasts all TALK actions)
            enable_ceo_interrupt: Whether to enable CEO interrupt monitoring
            ceo_interrupt_keys: Keys that trigger CEO interrupt
        """
        super().__init__(
            name=name,
            agents=[],  # Don't add agents yet, we'll handle this in add_agents
            initial_datetime=initial_datetime,
            broadcast_if_no_target=broadcast_if_no_target,
            max_additional_targets_to_display=max_additional_targets_to_display,
            is_meeting=is_meeting
        )
        
        # Async-specific attributes
        self._async_lock = asyncio.Lock()
        self._state_lock = threading.Lock()  # For sync operations
        self._event_bus = None
        self._event_bus_initialized = False
        
        # CEO interrupt support
        self.enable_ceo_interrupt = enable_ceo_interrupt
        self.ceo_interrupt_keys = ceo_interrupt_keys
        self._ceo_handler: Optional[CEOInterruptHandler] = None
        self._ceo_monitoring_active = False
        
        # Simulation state
        self.is_async_simulation_running = False
        self._simulation_task: Optional[asyncio.Task] = None
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Start unpaused
        
        # Add agents after initialization
        if agents:
            self.add_agents(agents)
    
    async def _initialize_event_bus(self):
        """Initialize the event bus for this world."""
        if not self._event_bus_initialized:
            self._event_bus = await get_event_bus()
            self._event_bus_initialized = True
            logger.debug(f"[{self.name}] Event bus initialized")
    
    def add_agent(self, agent: Union[TinyPerson, AsyncTinyPerson]):
        """
        Add an agent to the world, setting up async capabilities if needed.
        
        Args:
            agent: TinyPerson or AsyncTinyPerson to add
        """
        # Use parent method for basic adding
        super().add_agent(agent)
        
        # If this is an AsyncTinyPerson, ensure it has event bus access
        if isinstance(agent, AsyncTinyPerson):
            # Event bus will be initialized when needed
            logger.debug(f"[{self.name}] Added async agent: {agent.name}")
        else:
            logger.debug(f"[{self.name}] Added sync agent: {agent.name}")
        
        return self
    
    async def async_step(self, timedelta_per_step=None, current_round=None, total_rounds=None):
        """
        Perform a single async simulation step with concurrent agent processing.
        
        Args:
            timedelta_per_step: Time increment per step
            current_round: Current round number
            total_rounds: Total number of rounds
            
        Returns:
            Dict mapping agent names to their actions
        """
        async with self._async_lock:
            # Advance time
            self._advance_datetime(timedelta_per_step)
            
            # Initialize event bus if needed
            await self._initialize_event_bus()
            
            logger.debug(f"[{self.name}] Starting async step {current_round}/{total_rounds}")
            
            # Separate sync and async agents
            async_agents = [agent for agent in self.agents if isinstance(agent, AsyncTinyPerson)]
            sync_agents = [agent for agent in self.agents if not isinstance(agent, AsyncTinyPerson)]
            
            agents_actions = {}
            
            # Process async agents concurrently
            if async_agents:
                async_tasks = []
                for agent in async_agents:
                    # Ensure agent has event bus access
                    if not agent._event_bus_initialized:
                        await agent._initialize_event_bus()
                    
                    # Create task for agent action
                    task = asyncio.create_task(
                        self._async_agent_act(agent, current_round, total_rounds)
                    )
                    async_tasks.append((agent, task))
                
                # Wait for all async agents to complete
                for agent, task in async_tasks:
                    try:
                        actions = await task
                        agents_actions[agent.name] = actions
                        
                        # Handle actions in the world
                        latest_actions = agent.pop_latest_actions()
                        self._handle_actions(agent, latest_actions)
                        
                    except Exception as error:
                        logger.error(f"[{self.name}] Error in async agent {agent.name}: {error}")
                        agents_actions[agent.name] = []
            
            # Process sync agents sequentially (for compatibility)
            for agent in sync_agents:
                try:
                    logger.debug(f"[{self.name}] Agent {agent.name} is acting (sync).")
                    actions = agent.act(return_actions=True, current_round=current_round, total_rounds=total_rounds)
                    agents_actions[agent.name] = actions
                    
                    # Handle actions
                    self._handle_actions(agent, agent.pop_latest_actions())
                    
                except Exception as error:
                    logger.error(f"[{self.name}] Error in sync agent {agent.name}: {error}")
                    agents_actions[agent.name] = []
            
            return agents_actions
    
    async def _async_agent_act(self, agent: AsyncTinyPerson, current_round=None, total_rounds=None):
        """Helper method to run async agent action."""
        try:
            # Check for pause
            await self._pause_event.wait()
            
            # Check for CEO interrupts
            if agent._ceo_interrupt_event.is_set():
                await agent._process_ceo_interrupt()
            
            # Execute agent action
            actions = await agent.async_act(
                return_actions=True,
                current_round=current_round,
                total_rounds=total_rounds
            )
            
            return actions
            
        except Exception as error:
            logger.error(f"[{self.name}] Error in async agent {agent.name}: {error}")
            return []
    
    async def async_run(self, steps: int, timedelta_per_step=None, return_actions=False, 
                       enable_ceo_interrupt=None):
        """
        Run the world asynchronously for a given number of steps.
        
        Args:
            steps: Number of simulation steps
            timedelta_per_step: Time per step
            return_actions: Whether to return all actions
            enable_ceo_interrupt: Override CEO interrupt setting
            
        Returns:
            List of agent actions per step if return_actions=True
        """
        if enable_ceo_interrupt is None:
            enable_ceo_interrupt = self.enable_ceo_interrupt
        
        # Start CEO monitoring if enabled
        if enable_ceo_interrupt:
            await self._start_ceo_monitoring()
        
        try:
            self.is_async_simulation_running = True
            agents_actions_over_time = []
            
            for i in range(steps):
                logger.info(f"[{self.name}] Running async world simulation step {i+1} of {steps}.")
                
                # Display step information if enabled
                if TinyWorld.communication_display:
                    logger.info(f"[{self.name}] Step {i+1}/{steps} - Running async simulation")
                
                # Run async step
                agents_actions = await self.async_step(
                    timedelta_per_step=timedelta_per_step,
                    current_round=i+1,
                    total_rounds=steps
                )
                
                if return_actions:
                    agents_actions_over_time.append(agents_actions)
                
                # Brief pause to allow CEO interrupts to be processed
                await asyncio.sleep(0.01)
            
            if return_actions:
                return agents_actions_over_time
                
        finally:
            self.is_async_simulation_running = False
            # Stop CEO monitoring
            if enable_ceo_interrupt:
                await self._stop_ceo_monitoring()
    
    async def _start_ceo_monitoring(self):
        """Start CEO interrupt monitoring."""
        if not self._ceo_monitoring_active:
            try:
                await self._initialize_event_bus()
                
                # Subscribe to CEO interrupt events
                await self._event_bus.subscribe(EventType.CEO_INTERRUPT, self._handle_ceo_interrupt_event)
                
                # Start monitoring task
                self._ceo_handler = CEOInterruptHandler(
                    interrupt_keys=self.ceo_interrupt_keys,
                    prompt_text=f"[{self.name}] CEO Command: "
                )
                self._ceo_handler.event_bus = self._event_bus
                
                await start_ceo_monitoring()
                self._ceo_monitoring_active = True
                
                logger.info(f"[{self.name}] CEO interrupt monitoring started (keys: {self.ceo_interrupt_keys})")
                
            except Exception as error:
                logger.error(f"[{self.name}] Failed to start CEO monitoring: {error}")
    
    async def _stop_ceo_monitoring(self):
        """Stop CEO interrupt monitoring."""
        if self._ceo_monitoring_active:
            try:
                await stop_ceo_monitoring()
                
                # Unsubscribe from events
                if self._event_bus:
                    await self._event_bus.unsubscribe(EventType.CEO_INTERRUPT, self._handle_ceo_interrupt_event)
                
                self._ceo_monitoring_active = False
                self._ceo_handler = None
                
                logger.info(f"[{self.name}] CEO interrupt monitoring stopped")
                
            except Exception as error:
                logger.error(f"[{self.name}] Error stopping CEO monitoring: {error}")
    
    async def _handle_ceo_interrupt_event(self, event: Event):
        """Handle CEO interrupt events for the world."""
        logger.info(f"[{self.name}] CEO interrupt received: {event.data.get('message', 'No message')}")
        
        # Handle different types of CEO commands
        message = event.data.get('message', '').lower()
        
        if 'pause' in message:
            await self.pause_simulation()
        elif 'resume' in message:
            await self.resume_simulation()
        elif 'stop' in message or 'end' in message:
            await self.stop_simulation()
        elif 'steer' in message:
            # Forward to all async agents
            await self._broadcast_ceo_interrupt_to_agents(event)
        else:
            # Default: forward to all agents
            await self._broadcast_ceo_interrupt_to_agents(event)
    
    async def _broadcast_ceo_interrupt_to_agents(self, event: Event):
        """Broadcast CEO interrupt to all async agents."""
        async_agents = [agent for agent in self.agents if isinstance(agent, AsyncTinyPerson)]
        
        for agent in async_agents:
            await agent._handle_ceo_interrupt_event(event)
    
    async def pause_simulation(self):
        """Pause the simulation."""
        self._pause_event.clear()
        logger.info(f"[{self.name}] Simulation paused")
        
        # Publish pause event
        if self._event_bus:
            pause_event = Event(
                event_type=EventType.SIMULATION_PAUSE,
                source=self.name,
                data={"timestamp": datetime.now().isoformat()}
            )
            await self._event_bus.publish(pause_event)
    
    async def resume_simulation(self):
        """Resume the simulation."""
        self._pause_event.set()
        logger.info(f"[{self.name}] Simulation resumed")
        
        # Publish resume event
        if self._event_bus:
            resume_event = Event(
                event_type=EventType.SIMULATION_RESUME,
                source=self.name,
                data={"timestamp": datetime.now().isoformat()}
            )
            await self._event_bus.publish(resume_event)
    
    async def stop_simulation(self):
        """Stop the simulation."""
        self.is_async_simulation_running = False
        logger.info(f"[{self.name}] Simulation stopped by CEO command")
        
        # Publish stop event
        if self._event_bus:
            stop_event = Event(
                event_type=EventType.SIMULATION_END,
                source=self.name,
                data={"timestamp": datetime.now().isoformat(), "reason": "CEO_INTERRUPT"}
            )
            await self._event_bus.publish(stop_event)
    
    # Convenience methods that wrap async_run
    async def async_run_minutes(self, minutes: int):
        """Run the world asynchronously for a given number of minutes."""
        await self.async_run(steps=minutes, timedelta_per_step=timedelta(minutes=1))
    
    async def async_run_hours(self, hours: int):
        """Run the world asynchronously for a given number of hours."""
        await self.async_run(steps=hours, timedelta_per_step=timedelta(hours=1))
    
    async def async_run_days(self, days: int):
        """Run the world asynchronously for a given number of days."""
        await self.async_run(steps=days, timedelta_per_step=timedelta(days=1))
    
    # Backward compatibility: sync methods that call async versions
    @transactional  
    def run(self, steps: int, timedelta_per_step=None, return_actions=False):
        """
        Synchronous run method for backward compatibility.
        
        This method will use async execution if any AsyncTinyPerson agents are present,
        otherwise falls back to the parent's synchronous implementation.
        """
        # Check if we have any async agents
        has_async_agents = any(isinstance(agent, AsyncTinyPerson) for agent in self.agents)
        
        if has_async_agents:
            # Use async execution
            try:
                # Get or create event loop
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run async simulation
                result = loop.run_until_complete(
                    self.async_run(steps=steps, timedelta_per_step=timedelta_per_step, 
                                 return_actions=return_actions)
                )
                return result
                
            except Exception as error:
                logger.error(f"[{self.name}] Error in async simulation, falling back to sync: {error}")
                # Fall back to sync execution
                return super().run(steps=steps, timedelta_per_step=timedelta_per_step, 
                                 return_actions=return_actions)
        else:
            # Use parent's synchronous implementation
            return super().run(steps=steps, timedelta_per_step=timedelta_per_step, 
                             return_actions=return_actions)
    
    def get_async_state(self):
        """Get current async simulation state."""
        return {
            "is_running": self.is_async_simulation_running,
            "is_paused": not self._pause_event.is_set(),
            "ceo_monitoring": self._ceo_monitoring_active,
            "async_agents": [agent.name for agent in self.agents if isinstance(agent, AsyncTinyPerson)],
            "sync_agents": [agent.name for agent in self.agents if not isinstance(agent, AsyncTinyPerson)]
        }
    
    async def shutdown(self):
        """Clean shutdown of async world and all resources."""
        logger.info(f"[{self.name}] Shutting down async world")
        
        # Stop simulation if running
        if self.is_async_simulation_running:
            await self.stop_simulation()
        
        # Stop CEO monitoring
        await self._stop_ceo_monitoring()
        
        # Shutdown all async agents
        async_agents = [agent for agent in self.agents if isinstance(agent, AsyncTinyPerson)]
        for agent in async_agents:
            if hasattr(agent, 'shutdown'):
                await agent.shutdown()
        
        logger.info(f"[{self.name}] Async world shutdown complete")


# Convenience functions
async def create_async_world(name: str, agents=[], **kwargs) -> AsyncTinyWorld:
    """
    Create and initialize an AsyncTinyWorld.
    
    Args:
        name: World name
        agents: List of agents to add
        **kwargs: Additional arguments passed to AsyncTinyWorld constructor
    
    Returns:
        Initialized AsyncTinyWorld
    """
    world = AsyncTinyWorld(name=name, agents=agents, **kwargs)
    await world._initialize_event_bus()
    return world


async def run_concurrent_worlds(worlds: List[AsyncTinyWorld], steps: int, **kwargs):
    """
    Run multiple AsyncTinyWorld instances concurrently.
    
    Args:
        worlds: List of AsyncTinyWorld instances
        steps: Number of steps to run each world
        **kwargs: Additional arguments passed to async_run
    
    Returns:
        Dict mapping world names to their results
    """
    logger.info(f"Starting concurrent simulation of {len(worlds)} worlds")
    
    # Create tasks for each world
    tasks = {}
    for world in worlds:
        task = asyncio.create_task(world.async_run(steps=steps, **kwargs))
        tasks[world.name] = task
    
    # Wait for all worlds to complete
    results = {}
    for world_name, task in tasks.items():
        try:
            result = await task
            results[world_name] = result
            logger.info(f"World '{world_name}' completed successfully")
        except Exception as error:
            logger.error(f"World '{world_name}' failed: {error}")
            results[world_name] = None
    
    return results