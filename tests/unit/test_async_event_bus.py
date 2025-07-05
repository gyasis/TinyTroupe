"""
Unit tests for async event bus functionality
"""

import pytest
import pytest_asyncio
import asyncio
import logging
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tinytroupe.async_event_bus import (
    AsyncEventBus, Event, EventType, CEOInterruptEvent,
    get_event_bus, initialize_event_bus, shutdown_event_bus
)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def event_bus():
    """Create a fresh event bus for each test"""
    bus = AsyncEventBus()
    await bus.start()
    yield bus
    await bus.stop()


@pytest_asyncio.fixture
async def running_event_bus():
    """Create and start event bus, then cleanup"""
    await shutdown_event_bus()  # Ensure clean state
    bus = await initialize_event_bus()
    yield bus
    await shutdown_event_bus()


class TestEvent:
    """Test Event class functionality"""
    
    def test_event_creation(self):
        """Test basic event creation"""
        event = Event(
            event_type=EventType.AGENT_MESSAGE,
            source="test_agent",
            data={"message": "test"}
        )
        
        assert event.event_type == EventType.AGENT_MESSAGE
        assert event.source == "test_agent"
        assert event.data["message"] == "test"
        assert event.priority == 0
        assert isinstance(event.timestamp, datetime)
        
    def test_event_to_dict(self):
        """Test event serialization"""
        event = Event(
            event_type=EventType.CEO_INTERRUPT,
            source="CEO",
            data={"message": "Stop everything!"},
            priority=100
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_type"] == "ceo_interrupt"
        assert event_dict["source"] == "CEO"
        assert event_dict["data"]["message"] == "Stop everything!"
        assert event_dict["priority"] == 100
        assert "timestamp" in event_dict


class TestCEOInterruptEvent:
    """Test CEO interrupt event functionality"""
    
    def test_ceo_interrupt_creation(self):
        """Test CEO interrupt event creation"""
        event = CEOInterruptEvent(
            message="Change direction now!",
            override_context=True,
            resume_action="steer"
        )
        
        assert event.event_type == EventType.CEO_INTERRUPT
        assert event.message == "Change direction now!"
        assert event.override_context is True
        assert event.resume_action == "steer"
        assert event.priority == 100  # Highest priority
        
    def test_ceo_interrupt_data_update(self):
        """Test that data dict is properly updated"""
        event = CEOInterruptEvent(message="Test message")
        
        assert event.data["message"] == "Test message"
        assert event.data["override_context"] is True
        assert event.data["resume_action"] == "continue"


class TestAsyncEventBus:
    """Test AsyncEventBus functionality"""
    
    @pytest.mark.asyncio
    async def test_event_bus_start_stop(self):
        """Test event bus lifecycle"""
        bus = AsyncEventBus()
        assert not bus.running
        
        await bus.start()
        assert bus.running
        
        await bus.stop()
        assert not bus.running
        
    @pytest.mark.asyncio
    async def test_subscribe_unsubscribe(self, event_bus):
        """Test event subscription and unsubscription"""
        callback_called = False
        received_event = None
        
        async def test_callback(event):
            nonlocal callback_called, received_event
            callback_called = True
            received_event = event
            
        # Subscribe
        await event_bus.subscribe(EventType.AGENT_MESSAGE, test_callback)
        
        # Publish event
        test_event = Event(event_type=EventType.AGENT_MESSAGE, source="test")
        await event_bus.publish(test_event)
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        assert callback_called
        assert received_event.event_type == EventType.AGENT_MESSAGE
        
        # Unsubscribe
        await event_bus.unsubscribe(EventType.AGENT_MESSAGE, test_callback)
        
        # Reset callback state
        callback_called = False
        
        # Publish another event
        await event_bus.publish(test_event)
        await asyncio.sleep(0.1)
        
        assert not callback_called  # Should not be called after unsubscribe
        
    @pytest.mark.asyncio
    async def test_priority_event_handling(self, event_bus):
        """Test that events are processed by priority"""
        processed_events = []
        
        async def priority_callback(event):
            processed_events.append(event.priority)
            
        await event_bus.subscribe(EventType.AGENT_MESSAGE, priority_callback)
        
        # Publish events with different priorities
        low_priority = Event(event_type=EventType.AGENT_MESSAGE, priority=1)
        high_priority = Event(event_type=EventType.AGENT_MESSAGE, priority=100)
        medium_priority = Event(event_type=EventType.AGENT_MESSAGE, priority=50)
        
        # Publish in random order
        await event_bus.publish(low_priority)
        await event_bus.publish(high_priority)
        await event_bus.publish(medium_priority)
        
        # Wait for processing
        await asyncio.sleep(0.2)
        
        # Should be processed in priority order (high to low)
        assert processed_events == [100, 50, 1]
        
    @pytest.mark.asyncio
    async def test_concurrent_event_delivery(self, event_bus):
        """Test concurrent event delivery to multiple subscribers"""
        callback1_called = asyncio.Event()
        callback2_called = asyncio.Event()
        
        async def callback1(event):
            await asyncio.sleep(0.1)  # Simulate processing time
            callback1_called.set()
            
        async def callback2(event):
            await asyncio.sleep(0.1)  # Simulate processing time
            callback2_called.set()
            
        # Subscribe both callbacks
        await event_bus.subscribe(EventType.AGENT_MESSAGE, callback1)
        await event_bus.subscribe(EventType.AGENT_MESSAGE, callback2)
        
        # Publish event
        test_event = Event(event_type=EventType.AGENT_MESSAGE)
        start_time = asyncio.get_event_loop().time()
        await event_bus.publish(test_event)
        
        # Wait for both callbacks
        await asyncio.gather(
            asyncio.wait_for(callback1_called.wait(), timeout=1.0),
            asyncio.wait_for(callback2_called.wait(), timeout=1.0)
        )
        
        end_time = asyncio.get_event_loop().time()
        
        # Should take ~0.1 seconds (concurrent), not 0.2 (sequential)
        assert end_time - start_time < 0.15
        
    @pytest.mark.asyncio
    async def test_error_handling_in_callbacks(self, event_bus):
        """Test that errors in callbacks don't crash the event bus"""
        good_callback_called = False
        
        async def failing_callback(event):
            raise Exception("Test error")
            
        async def good_callback(event):
            nonlocal good_callback_called
            good_callback_called = True
            
        await event_bus.subscribe(EventType.AGENT_MESSAGE, failing_callback)
        await event_bus.subscribe(EventType.AGENT_MESSAGE, good_callback)
        
        # Publish event
        test_event = Event(event_type=EventType.AGENT_MESSAGE)
        await event_bus.publish(test_event)
        
        await asyncio.sleep(0.1)
        
        # Good callback should still be called despite error in failing callback
        assert good_callback_called
        
    @pytest.mark.asyncio
    async def test_event_log(self, event_bus):
        """Test event logging functionality"""
        # Publish several events
        for i in range(5):
            event = Event(
                event_type=EventType.AGENT_MESSAGE,
                source=f"agent_{i}",
                data={"count": i}
            )
            await event_bus.publish(event)
            
        await asyncio.sleep(0.1)
        
        # Check event log
        event_log = event_bus.get_event_log()
        assert len(event_log) == 5
        
        # Check log structure
        for i, log_entry in enumerate(event_log):
            assert log_entry["event_type"] == "agent_message"
            assert log_entry["source"] == f"agent_{i}"
            assert log_entry["data"]["count"] == i
            
        # Test log clearing
        event_bus.clear_event_log()
        assert len(event_bus.get_event_log()) == 0
        
    @pytest.mark.asyncio
    async def test_ceo_interrupt_convenience_method(self, event_bus):
        """Test CEO interrupt convenience method"""
        received_interrupt = None
        
        async def interrupt_callback(event):
            nonlocal received_interrupt
            received_interrupt = event
            
        await event_bus.subscribe(EventType.CEO_INTERRUPT, interrupt_callback)
        
        # Use convenience method
        await event_bus.publish_ceo_interrupt(
            message="Emergency stop!",
            override_context=True,
            resume_action="end"
        )
        
        await asyncio.sleep(0.1)
        
        assert received_interrupt is not None
        assert received_interrupt.event_type == EventType.CEO_INTERRUPT
        assert received_interrupt.data["message"] == "Emergency stop!"
        assert received_interrupt.data["override_context"] is True
        assert received_interrupt.data["resume_action"] == "end"
        assert received_interrupt.source == "CEO"
        
    @pytest.mark.asyncio
    async def test_wait_for_event(self, event_bus):
        """Test wait_for_event utility method"""
        # Start waiting for event in background
        wait_task = asyncio.create_task(
            event_bus.wait_for_event(EventType.CEO_INTERRUPT, timeout=1.0)
        )
        
        # Wait a bit then publish the event
        await asyncio.sleep(0.1)
        test_event = CEOInterruptEvent(message="Test interrupt")
        await event_bus.publish(test_event)
        
        # Should receive the event
        received_event = await wait_task
        assert received_event is not None
        assert received_event.data["message"] == "Test interrupt"
        
    @pytest.mark.asyncio
    async def test_wait_for_event_timeout(self, event_bus):
        """Test wait_for_event timeout"""
        # Wait for event that never comes
        received_event = await event_bus.wait_for_event(
            EventType.CEO_INTERRUPT, 
            timeout=0.1
        )
        
        assert received_event is None


class TestGlobalEventBus:
    """Test global event bus functions"""
    
    @pytest.mark.asyncio
    async def test_global_event_bus_singleton(self):
        """Test that global event bus is a singleton"""
        await shutdown_event_bus()  # Clean state
        
        bus1 = await get_event_bus()
        bus2 = await get_event_bus()
        
        assert bus1 is bus2  # Should be same instance
        
        await shutdown_event_bus()
        
    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self):
        """Test global event bus initialization and shutdown"""
        await shutdown_event_bus()  # Clean state
        
        # Initialize
        bus = await initialize_event_bus()
        assert bus.running
        
        # Get same instance
        same_bus = await get_event_bus()
        assert same_bus is bus
        
        # Shutdown
        await shutdown_event_bus()
        assert not bus.running
        
    @pytest.mark.asyncio 
    async def test_concurrent_initialization(self):
        """Test concurrent initialization is safe"""
        await shutdown_event_bus()  # Clean state
        
        # Try to initialize concurrently
        tasks = [
            asyncio.create_task(get_event_bus()),
            asyncio.create_task(get_event_bus()),
            asyncio.create_task(get_event_bus())
        ]
        
        buses = await asyncio.gather(*tasks)
        
        # All should be the same instance
        assert all(bus is buses[0] for bus in buses)
        
        await shutdown_event_bus()


@pytest.mark.asyncio
async def test_integration_scenario():
    """Integration test simulating real usage"""
    await shutdown_event_bus()
    
    # Initialize event bus
    bus = await initialize_event_bus()
    
    # Set up agent message handler
    agent_messages = []
    async def agent_handler(event):
        agent_messages.append(event.data)
        
    # Set up CEO interrupt handler
    ceo_interrupts = []
    async def ceo_handler(event):
        ceo_interrupts.append(event.data)
        
    await bus.subscribe(EventType.AGENT_MESSAGE, agent_handler)
    await bus.subscribe(EventType.CEO_INTERRUPT, ceo_handler)
    
    # Simulate agent activity
    agent_event = Event(
        event_type=EventType.AGENT_MESSAGE,
        source="alice",
        data={"action": "speaking", "message": "Hello everyone"}
    )
    await bus.publish(agent_event)
    
    # Simulate CEO interrupt
    await bus.publish_ceo_interrupt(
        message="Let's focus on the technical details",
        override_context=True,
        resume_action="steer"
    )
    
    # Wait for processing
    await asyncio.sleep(0.1)
    
    # Verify results
    assert len(agent_messages) == 1
    assert agent_messages[0]["action"] == "speaking"
    
    assert len(ceo_interrupts) == 1
    assert ceo_interrupts[0]["message"] == "Let's focus on the technical details"
    
    # Check event log
    event_log = bus.get_event_log()
    assert len(event_log) == 2
    
    await shutdown_event_bus()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])