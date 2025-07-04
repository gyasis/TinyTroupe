"""
Demo script for async agent features and CEO interrupt functionality
"""

import asyncio
import sys
import os
import logging
import threading

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tinytroupe.async_agent import AsyncTinyPerson, create_async_agent, run_agents_concurrently
from tinytroupe.async_event_bus import initialize_event_bus, shutdown_event_bus, get_event_bus, EventType
from tinytroupe.ceo_interrupt import start_ceo_monitoring, stop_ceo_monitoring

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo_event_bus():
    """Demonstrate async event bus functionality"""
    print("\n🔧 DEMO: Async Event Bus")
    print("=" * 50)
    
    # Initialize event bus
    bus = await initialize_event_bus()
    
    # Set up event listener
    received_events = []
    
    async def event_listener(event):
        received_events.append(event)
        print(f"📨 Received event: {event.event_type.value} from {event.source}")
        if event.data:
            print(f"   Data: {event.data}")
    
    # Subscribe to events
    await bus.subscribe(EventType.AGENT_MESSAGE, event_listener)
    await bus.subscribe(EventType.CEO_INTERRUPT, event_listener)
    
    # Publish some events
    from tinytroupe.async_event_bus import Event
    
    agent_event = Event(
        event_type=EventType.AGENT_MESSAGE,
        source="demo_agent",
        data={"action": "speaking", "message": "Hello world!"}
    )
    await bus.publish(agent_event)
    
    # Publish CEO interrupt
    await bus.publish_ceo_interrupt(
        message="Demo interrupt - please focus on the technical details",
        override_context=True,
        resume_action="steer"
    )
    
    # Wait for event processing
    await asyncio.sleep(0.1)
    
    print(f"✅ Processed {len(received_events)} events")
    
    # Show event log
    event_log = bus.get_event_log()
    print(f"📋 Event log contains {len(event_log)} entries")
    
    return received_events


async def demo_async_agents():
    """Demonstrate AsyncTinyPerson functionality"""
    print("\n🤖 DEMO: Async Agents")
    print("=" * 50)
    
    # Create async agents (mock the TinyPerson initialization for demo)
    class MockAsyncAgent(AsyncTinyPerson):
        def __init__(self, name):
            # Minimal initialization for demo
            self.name = name
            self.async_state = "IDLE"
            self._async_lock = asyncio.Lock()
            self._state_lock = threading.Lock()  # Use threading lock for sync operations
            self._ceo_interrupt_event = asyncio.Event()
            self._event_bus = None
            self._event_bus_initialized = False
            self._interrupt_context = {}
            self._last_interrupt_message = None
            
        # Mock sync methods
        def listen(self, speech, source=None, max_content_length=None):
            return f"{self.name} heard: '{speech}'"
            
        def act(self, **kwargs):
            return f"{self.name} acted with params: {kwargs}"
            
        def listen_and_act(self, speech, **kwargs):
            return f"{self.name} listened to '{speech}' and acted"
    
    # Create agents
    alice = MockAsyncAgent("Alice")
    bob = MockAsyncAgent("Bob")
    
    # Initialize event bus for agents
    await alice._initialize_event_bus()
    await bob._initialize_event_bus()
    
    print("👥 Created agents: Alice and Bob")
    
    # Test async operations
    print("\n🎯 Testing async operations...")
    
    # Async listen
    result1 = await alice.async_listen("Hello from the demo!")
    print(f"Alice async_listen result: {result1}")
    
    # Async act
    result2 = await bob.async_act(until_done=True, n=3)
    print(f"Bob async_act result: {result2}")
    
    # Async listen and act
    result3 = await alice.async_listen_and_act("Let's work together", return_actions=False)
    print(f"Alice async_listen_and_act result: {result3}")
    
    # Test concurrent operations
    print("\n⚡ Testing concurrent operations...")
    start_time = asyncio.get_event_loop().time()
    
    results = await asyncio.gather(
        alice.async_listen("Concurrent message 1"),
        bob.async_listen("Concurrent message 2"),
        alice.async_act(n=2),
        bob.async_act(n=2)
    )
    
    end_time = asyncio.get_event_loop().time()
    print(f"✅ Completed 4 concurrent operations in {end_time - start_time:.2f} seconds")
    print(f"📊 Results: {results}")
    
    return [alice, bob]


async def demo_ceo_interrupt():
    """Demonstrate CEO interrupt functionality (simulated)"""
    print("\n👔 DEMO: CEO Interrupt System")
    print("=" * 50)
    
    from tinytroupe.ceo_interrupt import CEOInterruptHandler
    
    # Create CEO handler (don't start actual monitoring for demo)
    ceo_handler = CEOInterruptHandler(
        interrupt_keys=['demo'],
        prompt_text="Demo CEO prompt: "
    )
    
    # Initialize event bus
    bus = await get_event_bus()
    ceo_handler.event_bus = bus
    
    # Set up event listener for CEO interrupts
    ceo_events = []
    
    async def ceo_event_listener(event):
        ceo_events.append(event)
        print(f"🚨 CEO Interrupt received: {event.data.get('message', 'No message')}")
    
    await bus.subscribe(EventType.CEO_INTERRUPT, ceo_event_listener)
    
    # Simulate CEO interrupt
    print("📢 Simulating CEO interrupt...")
    await ceo_handler._broadcast_ceo_directive("Demo directive: Focus on security requirements")
    
    # Simulate steering
    print("🎯 Simulating steering directive...")
    await ceo_handler._handle_steering()
    
    await asyncio.sleep(0.1)
    
    print(f"✅ Processed {len(ceo_events)} CEO events")
    
    return ceo_events


async def demo_integration_scenario():
    """Demonstrate complete integration scenario"""
    print("\n🎮 DEMO: Integration Scenario")
    print("=" * 50)
    
    # Create a mock agent for integration demo
    class IntegrationAgent(AsyncTinyPerson):
        def __init__(self, name):
            self.name = name
            self.async_state = "IDLE"
            self._async_lock = asyncio.Lock()
            self._state_lock = threading.Lock()
            self._ceo_interrupt_event = asyncio.Event()
            self._event_bus = None
            self._event_bus_initialized = False
            self._interrupt_context = {}
            self._last_interrupt_message = None
            
        def listen(self, speech, source=None, max_content_length=None):
            return f"[{self.name}] Processing: {speech}"
            
        def act(self, **kwargs):
            return f"[{self.name}] Acting with consideration of current context"
    
    # Create agents for a mock meeting
    agents = [
        IntegrationAgent("Project Manager"),
        IntegrationAgent("Developer"),
        IntegrationAgent("Security Expert")
    ]
    
    # Initialize all agents
    for agent in agents:
        await agent._initialize_event_bus()
    
    print(f"👥 Created {len(agents)} agents for integration demo")
    
    # Simulate meeting discussion
    print("\n💬 Simulating meeting discussion...")
    
    # Agents participate in discussion
    results = await asyncio.gather(
        agents[0].async_listen("We need to discuss the security requirements"),
        agents[1].async_listen("I can implement the technical features"),
        agents[2].async_listen("Let me review the security implications")
    )
    
    print("✅ Initial discussion completed")
    
    # Simulate CEO interrupt during discussion
    print("\n🚨 Simulating CEO interrupt during meeting...")
    
    from tinytroupe.async_event_bus import CEOInterruptEvent
    
    # Create CEO interrupt event
    ceo_event = CEOInterruptEvent(
        message="URGENT: We need to prioritize the encryption features immediately",
        override_context=True,
        resume_action="steer"
    )
    
    # Send interrupt to all agents
    for agent in agents:
        await agent._handle_ceo_interrupt_event(ceo_event)
        await agent._process_ceo_interrupt()
    
    print("✅ CEO interrupt processed by all agents")
    
    # Continue with updated context
    print("\n🔄 Continuing with updated priorities...")
    
    updated_results = await asyncio.gather(
        agents[0].async_act(n=1),
        agents[1].async_listen("Implementing encryption features now"),
        agents[2].async_listen("Reviewing encryption requirements")
    )
    
    print("✅ Integration scenario completed successfully")
    
    # Show final state
    for agent in agents:
        state = await agent.get_async_state()
        print(f"📊 {agent.name} final state: {state.value}")
        print(f"   Last interrupt: {agent._last_interrupt_message}")
    
    return agents


async def main():
    """Main demo function"""
    print("🚀 TinyTroupe Async Features Demo")
    print("=" * 80)
    
    try:
        # Initialize global event bus
        await initialize_event_bus()
        
        # Run demos
        await demo_event_bus()
        await demo_async_agents()
        await demo_ceo_interrupt()
        await demo_integration_scenario()
        
        print("\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as error:
        print(f"\n❌ Demo failed with error: {error}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        await shutdown_event_bus()
        print("\n🧹 Cleanup completed")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())