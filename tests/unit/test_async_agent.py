"""
Unit tests for AsyncTinyPerson functionality
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import threading
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tinytroupe.async_agent import (
    AsyncTinyPerson, AsyncAgentState, create_async_agent, 
    run_agents_concurrently
)
from tinytroupe.async_event_bus import EventType, initialize_event_bus, shutdown_event_bus
from tinytroupe.agent import TinyPerson

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
async def async_agent():
    """Create an AsyncTinyPerson for testing"""
    await shutdown_event_bus()
    await initialize_event_bus()
    
    # Mock the asyncio.create_task call in __init__ to avoid actual event bus init
    with patch('asyncio.create_task'):
        agent = AsyncTinyPerson("test_agent")
        
    yield agent
    
    # Cleanup
    await agent.cancel_async_operations()
    await shutdown_event_bus()


@pytest.fixture
async def mock_tiny_person():
    """Create a mock TinyPerson for testing inheritance"""
    mock_person = Mock(spec=TinyPerson)
    mock_person.name = "mock_agent"
    mock_person.listen = Mock(return_value="mock_listen_result")
    mock_person.act = Mock(return_value="mock_act_result")
    mock_person.listen_and_act = Mock(return_value="mock_listen_and_act_result")
    mock_person.PP_TEXT_WIDTH = 100
    return mock_person


class TestAsyncAgentState:
    """Test AsyncAgentState enum"""
    
    def test_agent_state_values(self):
        """Test that agent state enum has correct values"""
        assert AsyncAgentState.IDLE.value == "IDLE"
        assert AsyncAgentState.LISTENING.value == "LISTENING"
        assert AsyncAgentState.ACTING.value == "ACTING"
        assert AsyncAgentState.CEO_INSTRUCTION_FOLLOWING.value == "CEO_INSTRUCTION_FOLLOWING"


class TestAsyncTinyPersonInitialization:
    """Test AsyncTinyPerson initialization"""
    
    def test_basic_initialization(self):
        """Test basic initialization without event bus"""
        with patch('asyncio.create_task'):  # Prevent actual task creation
            agent = AsyncTinyPerson("test_agent")
            
        assert agent.name == "test_agent"
        assert agent.async_state == AsyncAgentState.IDLE
        assert not agent._event_bus_initialized
        assert agent._event_bus is None
        assert agent._last_interrupt_message is None
        
    def test_inheritance_from_tiny_person(self):
        """Test that AsyncTinyPerson properly inherits from TinyPerson"""
        with patch('asyncio.create_task'):
            agent = AsyncTinyPerson("test_agent")
            
        assert isinstance(agent, TinyPerson)
        assert hasattr(agent, 'listen')  # Inherited method
        assert hasattr(agent, 'act')     # Inherited method
        assert hasattr(agent, 'listen_and_act')  # Inherited method
        
    def test_async_specific_attributes(self):
        """Test async-specific attributes are properly initialized"""
        with patch('asyncio.create_task'):
            agent = AsyncTinyPerson("test_agent")
            
        # Check async-specific attributes
        assert hasattr(agent, '_async_lock')
        assert isinstance(agent._async_lock, asyncio.Lock)
        assert hasattr(agent, '_state_lock')
        assert isinstance(agent._state_lock, threading.Lock)
        assert hasattr(agent, '_ceo_interrupt_event')
        assert isinstance(agent._ceo_interrupt_event, asyncio.Event)


class TestAsyncTinyPersonAsyncMethods:
    """Test async methods of AsyncTinyPerson"""
    
    @pytest.mark.asyncio
    async def test_async_listen(self, async_agent):
        """Test async_listen method"""
        # Mock the sync listen method
        with patch.object(async_agent, 'listen', return_value="listen_result") as mock_listen:
            with patch.object(async_agent, '_publish_agent_event', new_callable=AsyncMock) as mock_publish:
                result = await async_agent.async_listen("test speech", source="test_source")
                
        assert result == "listen_result"
        mock_listen.assert_called_once()
        mock_publish.assert_called_once()
        
        # Check state transitions
        assert async_agent.async_state == AsyncAgentState.IDLE  # Should return to original state
        
    @pytest.mark.asyncio
    async def test_async_act(self, async_agent):
        """Test async_act method"""
        with patch.object(async_agent, 'act', return_value="act_result") as mock_act:
            with patch.object(async_agent, '_publish_agent_event', new_callable=AsyncMock) as mock_publish:
                result = await async_agent.async_act(until_done=True, n=5)
                
        assert result == "act_result"
        mock_act.assert_called_once()
        mock_publish.assert_called_once()
        
        # Check state transitions
        assert async_agent.async_state == AsyncAgentState.IDLE
        
    @pytest.mark.asyncio
    async def test_async_listen_and_act(self, async_agent):
        """Test async_listen_and_act method"""
        with patch.object(async_agent, 'listen_and_act', return_value="listen_and_act_result") as mock_method:
            with patch.object(async_agent, '_publish_agent_event', new_callable=AsyncMock) as mock_publish:
                result = await async_agent.async_listen_and_act("test speech", return_actions=True)
                
        assert result == "listen_and_act_result"
        mock_method.assert_called_once()
        mock_publish.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_async_methods_with_ceo_interrupt(self, async_agent):
        """Test async methods handle CEO interrupts"""
        # Set up CEO interrupt
        async_agent._ceo_interrupt_event.set()
        async_agent._interrupt_context = {"message": "Stop now!", "override_context": True}
        
        with patch.object(async_agent, '_process_ceo_interrupt', new_callable=AsyncMock) as mock_process:
            result = await async_agent.async_listen("test speech")
            
        mock_process.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_concurrent_async_operations(self, async_agent):
        """Test concurrent async operations are handled safely"""
        # Mock the sync methods to simulate work
        with patch.object(async_agent, 'listen', side_effect=lambda *args: asyncio.sleep(0.1)) as mock_listen:
            with patch.object(async_agent, 'act', side_effect=lambda *args: asyncio.sleep(0.1)) as mock_act:
                with patch.object(async_agent, '_publish_agent_event', new_callable=AsyncMock):
                    # Start concurrent operations
                    task1 = asyncio.create_task(async_agent.async_listen("speech1"))
                    task2 = asyncio.create_task(async_agent.async_act())
                    
                    # Wait for both to complete
                    results = await asyncio.gather(task1, task2)
                    
        # Both operations should complete
        assert len(results) == 2


class TestSyncMethodWrappers:
    """Test sync method wrappers"""
    
    @pytest.mark.asyncio
    async def test_sync_listen_wrapper(self, async_agent):
        """Test sync listen wrapper with thread safety"""
        with patch.object(async_agent, 'listen', return_value="wrapped_result") as mock_listen:
            result = async_agent._sync_listen_wrapper("speech", "source", 100)
            
        assert result == "wrapped_result"
        mock_listen.assert_called_once_with("speech", "source", 100)
        
    @pytest.mark.asyncio
    async def test_sync_act_wrapper(self, async_agent):
        """Test sync act wrapper with thread safety"""
        with patch.object(async_agent, 'act', return_value="wrapped_result") as mock_act:
            result = async_agent._sync_act_wrapper(True, 5, False, 100, 1, 10)
            
        assert result == "wrapped_result"
        mock_act.assert_called_once_with(
            until_done=True, n=5, return_actions=False, 
            max_content_length=100, current_round=1, total_rounds=10
        )
        
    @pytest.mark.asyncio
    async def test_sync_wrapper_error_handling(self, async_agent):
        """Test error handling in sync wrappers"""
        with patch.object(async_agent, 'listen', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                async_agent._sync_listen_wrapper("speech", "source", 100)


class TestCEOInterruptHandling:
    """Test CEO interrupt handling in AsyncTinyPerson"""
    
    @pytest.mark.asyncio
    async def test_handle_ceo_interrupt_event(self, async_agent):
        """Test handling CEO interrupt events from event bus"""
        # Create mock CEO interrupt event
        mock_event = Mock()
        mock_event.data = {
            "message": "Change direction!",
            "override_context": True,
            "resume_action": "steer"
        }
        mock_event.timestamp = "2023-01-01T12:00:00"
        
        await async_agent._handle_ceo_interrupt_event(mock_event)
        
        # Check interrupt context is stored
        assert async_agent._interrupt_context["message"] == "Change direction!"
        assert async_agent._interrupt_context["override_context"] is True
        assert async_agent._ceo_interrupt_event.is_set()
        
    @pytest.mark.asyncio
    async def test_process_ceo_interrupt(self, async_agent):
        """Test processing CEO interrupt"""
        # Set up interrupt context
        async_agent._interrupt_context = {
            "message": "New directive",
            "override_context": True,
            "timestamp": "2023-01-01T12:00:00"
        }
        async_agent._ceo_interrupt_event.set()
        
        with patch.object(async_agent, '_publish_agent_event', new_callable=AsyncMock) as mock_publish:
            await async_agent._process_ceo_interrupt()
            
        # Check state changes
        assert async_agent.async_state == AsyncAgentState.IDLE  # Should return to idle
        assert not async_agent._ceo_interrupt_event.is_set()
        assert async_agent._last_interrupt_message == "New directive"
        mock_publish.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_ceo_interrupt_task_cancellation(self, async_agent):
        """Test that current async task is cancelled on interrupt"""
        # Create a mock task
        mock_task = Mock()
        mock_task.done.return_value = False
        async_agent._current_async_task = mock_task
        
        mock_event = Mock()
        mock_event.data = {"message": "Stop!", "override_context": True}
        mock_event.timestamp = "2023-01-01T12:00:00"
        
        await async_agent._handle_ceo_interrupt_event(mock_event)
        
        mock_task.cancel.assert_called_once()


class TestEventBusIntegration:
    """Test event bus integration"""
    
    @pytest.mark.asyncio
    async def test_event_bus_initialization(self, async_agent):
        """Test event bus initialization"""
        # Mock event bus
        mock_event_bus = AsyncMock()
        
        with patch('tinytroupe.async_agent.get_event_bus', return_value=mock_event_bus):
            await async_agent._ensure_event_bus()
            
        assert async_agent._event_bus is mock_event_bus
        mock_event_bus.subscribe.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_publish_agent_event(self, async_agent):
        """Test publishing agent events"""
        # Set up mock event bus
        mock_event_bus = AsyncMock()
        async_agent._event_bus = mock_event_bus
        
        await async_agent._publish_agent_event("test_action", {"key": "value"})
        
        mock_event_bus.publish.assert_called_once()
        # Check published event structure
        call_args = mock_event_bus.publish.call_args[0][0]
        assert call_args.event_type == EventType.AGENT_MESSAGE
        assert call_args.source == "test_agent"
        assert call_args.data["action"] == "test_action"
        assert call_args.data["agent_state"] == AsyncAgentState.IDLE.value


class TestAsyncAgentUtilities:
    """Test utility methods"""
    
    @pytest.mark.asyncio
    async def test_get_async_state(self, async_agent):
        """Test getting async state"""
        assert await async_agent.get_async_state() == AsyncAgentState.IDLE
        
        async_agent.async_state = AsyncAgentState.LISTENING
        assert await async_agent.get_async_state() == AsyncAgentState.LISTENING
        
    @pytest.mark.asyncio
    async def test_wait_for_completion(self, async_agent):
        """Test waiting for async operations to complete"""
        # Create a mock task that completes quickly
        async def mock_task():
            await asyncio.sleep(0.1)
            return "completed"
            
        async_agent._current_async_task = asyncio.create_task(mock_task())
        
        # Should complete without timeout
        await async_agent.wait_for_completion(timeout=1.0)
        assert async_agent._current_async_task.done()
        
    @pytest.mark.asyncio
    async def test_wait_for_completion_timeout(self, async_agent):
        """Test timeout in wait_for_completion"""
        # Create a mock task that takes too long
        async def long_task():
            await asyncio.sleep(10)
            return "completed"
            
        async_agent._current_async_task = asyncio.create_task(long_task())
        
        # Should timeout and cancel task
        await async_agent.wait_for_completion(timeout=0.1)
        assert async_agent._current_async_task.cancelled()
        
    @pytest.mark.asyncio
    async def test_cancel_async_operations(self, async_agent):
        """Test cancelling async operations"""
        # Create a mock task
        async def mock_task():
            await asyncio.sleep(10)
            return "completed"
            
        async_agent._current_async_task = asyncio.create_task(mock_task())
        
        await async_agent.cancel_async_operations()
        assert async_agent._current_async_task.cancelled()


class TestGlobalAsyncAgentFunctions:
    """Test global async agent functions"""
    
    @pytest.mark.asyncio
    async def test_create_async_agent(self):
        """Test create_async_agent function"""
        await shutdown_event_bus()
        await initialize_event_bus()
        
        with patch.object(AsyncTinyPerson, '_ensure_event_bus', new_callable=AsyncMock) as mock_ensure:
            agent = await create_async_agent("test_agent", age=30)
            
        assert isinstance(agent, AsyncTinyPerson)
        assert agent.name == "test_agent"
        mock_ensure.assert_called_once()
        
        await shutdown_event_bus()
        
    @pytest.mark.asyncio
    async def test_run_agents_concurrently(self):
        """Test running multiple agents concurrently"""
        await shutdown_event_bus()
        await initialize_event_bus()
        
        # Create mock agents
        agents = []
        for i in range(3):
            with patch('asyncio.create_task'):  # Prevent event bus init
                agent = AsyncTinyPerson(f"agent_{i}")
            agents.append(agent)
            
        stimuli = ["stimulus_0", "stimulus_1", "stimulus_2"]
        
        # Mock the async_listen_and_act method
        for i, agent in enumerate(agents):
            agent.async_listen_and_act = AsyncMock(return_value=f"result_{i}")
            
        results = await run_agents_concurrently(agents, stimuli)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result == f"result_{i}"
            
        # Check that all agents were called with correct stimuli
        for i, agent in enumerate(agents):
            agent.async_listen_and_act.assert_called_once_with(f"stimulus_{i}")
            
        await shutdown_event_bus()
        
    @pytest.mark.asyncio
    async def test_run_agents_concurrently_mismatched_inputs(self):
        """Test error handling for mismatched agents and stimuli"""
        agents = [AsyncTinyPerson("agent1"), AsyncTinyPerson("agent2")]
        stimuli = ["stimulus1"]  # Fewer stimuli than agents
        
        with pytest.raises(ValueError, match="Number of agents must match number of stimuli"):
            await run_agents_concurrently(agents, stimuli)
            
    @pytest.mark.asyncio
    async def test_run_agents_concurrently_timeout(self):
        """Test timeout handling in concurrent execution"""
        await shutdown_event_bus()
        await initialize_event_bus()
        
        # Create mock agents that take too long
        agents = []
        for i in range(2):
            with patch('asyncio.create_task'):
                agent = AsyncTinyPerson(f"agent_{i}")
                # Mock method that takes too long
                agent.async_listen_and_act = AsyncMock(side_effect=lambda x: asyncio.sleep(10))
            agents.append(agent)
            
        stimuli = ["stimulus_0", "stimulus_1"]
        
        with pytest.raises(asyncio.TimeoutError):
            await run_agents_concurrently(agents, stimuli, timeout=0.1)
            
        await shutdown_event_bus()


class TestThreadSafety:
    """Test thread safety of AsyncTinyPerson"""
    
    @pytest.mark.asyncio
    async def test_state_lock_usage(self, async_agent):
        """Test that state locks are properly used"""
        # Test that _state_lock is used in sync wrappers
        with patch.object(async_agent._state_lock, '__enter__') as mock_enter:
            with patch.object(async_agent._state_lock, '__exit__') as mock_exit:
                with patch.object(async_agent, 'listen', return_value="result"):
                    async_agent._sync_listen_wrapper("speech", "source", 100)
                    
        mock_enter.assert_called_once()
        mock_exit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_async_lock_usage(self, async_agent):
        """Test that async locks are properly acquired"""
        # The async lock should be acquired during async operations
        with patch.object(async_agent, 'listen', return_value="result"):
            with patch.object(async_agent, '_publish_agent_event', new_callable=AsyncMock):
                # This should acquire the async lock
                await async_agent.async_listen("test speech")
                
        # If we get here without deadlock, the locking is working


@pytest.mark.asyncio
async def test_integration_async_agent_workflow():
    """Integration test for complete async agent workflow"""
    await shutdown_event_bus()
    bus = await initialize_event_bus()
    
    # Create async agent
    with patch('asyncio.create_task'):
        agent = AsyncTinyPerson("integration_agent")
        
    # Set up event collection
    published_events = []
    
    async def event_collector(event):
        published_events.append(event)
        
    await bus.subscribe(EventType.AGENT_MESSAGE, event_collector)
    await bus.subscribe(EventType.CEO_INTERRUPT, event_collector)
    
    # Mock sync methods
    with patch.object(agent, 'listen', return_value="listen_result"):
        with patch.object(agent, 'act', return_value="act_result"):
            with patch.object(agent, 'listen_and_act', return_value="listen_and_act_result"):
                # Test full workflow
                await agent._initialize_event_bus()
                
                # Perform async operations
                listen_result = await agent.async_listen("Hello world")
                act_result = await agent.async_act(n=3)
                combined_result = await agent.async_listen_and_act("Test message")
                
                # Simulate CEO interrupt
                ceo_event = Mock()
                ceo_event.data = {"message": "Priority change!", "override_context": True}
                ceo_event.timestamp = "2023-01-01T12:00:00"
                
                await agent._handle_ceo_interrupt_event(ceo_event)
                await agent._process_ceo_interrupt()
                
    await asyncio.sleep(0.1)
    
    # Verify results
    assert listen_result == "listen_result"
    assert act_result == "act_result"
    assert combined_result == "listen_and_act_result"
    
    # Verify events were published
    agent_events = [e for e in published_events if e.event_type == EventType.AGENT_MESSAGE]
    assert len(agent_events) >= 3  # Should have published events for each async operation
    
    # Verify agent state transitions
    assert agent.async_state == AsyncAgentState.IDLE
    assert agent._last_interrupt_message == "Priority change!"
    
    await shutdown_event_bus()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])