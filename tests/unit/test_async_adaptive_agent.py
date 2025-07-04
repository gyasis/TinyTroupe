"""
Tests for AsyncAdaptiveTinyPerson - combines async and adaptive capabilities
"""

import pytest
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tinytroupe.async_adaptive_agent import AsyncAdaptiveTinyPerson, create_async_adaptive_agent
from tinytroupe.async_event_bus import initialize_event_bus, shutdown_event_bus, CEOInterruptEvent
from tinytroupe.context_detection import ContextType


@pytest.mark.asyncio
class TestAsyncAdaptiveTinyPerson:
    
    async def setup_method(self):
        """Setup for each test method."""
        # Initialize event bus
        await initialize_event_bus()
    
    async def teardown_method(self):
        """Cleanup after each test method."""
        # Shutdown event bus
        await shutdown_event_bus()
    
    async def test_agent_creation_and_basic_properties(self):
        """Test creating an async adaptive agent with basic properties."""
        
        agent = create_async_adaptive_agent(
            name="Dr. Sarah Wilson",
            occupation="Senior Healthcare Data Scientist",
            personality_traits=["analytical", "collaborative", "detail-oriented"],
            professional_interests=["machine learning", "healthcare informatics", "clinical research"],
            skills=["Python", "R", "SQL", "medical statistics"],
            years_experience="8+ years"
        )
        
        # Test basic properties
        assert agent.name == "Dr. Sarah Wilson"
        assert agent._configuration["occupation"] == "Senior Healthcare Data Scientist"
        assert agent.adaptive_mode_enabled == True
        assert agent.round_count == 0
        assert len(agent.conversation_history) == 0
        
        # Test async properties
        assert hasattr(agent, '_async_lock')
        assert hasattr(agent, '_state_lock')
        assert hasattr(agent, '_adaptive_lock')
        
        # Test that it has both async and adaptive capabilities
        assert hasattr(agent, 'async_listen')
        assert hasattr(agent, 'async_act')
        assert hasattr(agent, 'get_current_context')
        assert hasattr(agent, 'context_detector')
    
    async def test_async_listen_with_conversation_tracking(self):
        """Test async_listen tracks conversation history."""
        
        agent = create_async_adaptive_agent(
            name="Emily Chen",
            occupation="Project Manager"
        )
        
        # Test async listen with conversation tracking
        await agent.async_listen("Let's discuss the project requirements")
        
        assert len(agent.conversation_history) == 1
        assert "project requirements" in agent.conversation_history[0]
        
        # Test multiple messages
        await agent.async_listen("We need to focus on security compliance")
        await agent.async_listen("What about the timeline?")
        
        assert len(agent.conversation_history) == 3
        assert agent.conversation_history[-1] == "What about the timeline?"
    
    async def test_context_detection_integration(self):
        """Test that context detection works with conversation history."""
        
        agent = create_async_adaptive_agent(
            name="Michael Thompson",
            occupation="Compliance Officer"
        )
        
        # Simulate business meeting conversation
        business_messages = [
            "Let's review the compliance requirements",
            "We need to ensure HIPAA compliance",
            "What are the audit requirements?",
            "I can handle the regulatory documentation"
        ]
        
        for message in business_messages:
            await agent.async_listen(message)
        
        # Check context detection
        context = agent.get_current_context()
        # Should detect business meeting or technical discussion context
        assert context in [ContextType.BUSINESS_MEETING, ContextType.TECHNICAL_DISCUSSION]
        
        # Test context confidence
        confidence = agent.get_context_confidence()
        assert 0.0 <= confidence <= 1.0
    
    async def test_adaptive_mode_control(self):
        """Test enabling/disabling adaptive mode."""
        
        agent = create_async_adaptive_agent(
            name="Alex Rodriguez",
            occupation="Software Architect"
        )
        
        # Test initial state
        assert agent.adaptive_mode_enabled == True
        
        # Test disabling
        agent.disable_adaptive_mode()
        assert agent.adaptive_mode_enabled == False
        
        # Test enabling
        agent.enable_adaptive_mode()
        assert agent.adaptive_mode_enabled == True
    
    async def test_ceo_interrupt_with_adaptive_context(self):
        """Test CEO interrupt handling with adaptive context awareness."""
        
        agent = create_async_adaptive_agent(
            name="Dr. James Wilson",
            occupation="CTO"
        )
        
        # Initialize agent event bus
        await agent._initialize_event_bus()
        
        # Set up some conversation context
        await agent.async_listen("We're discussing the technical architecture")
        
        # Create CEO interrupt event
        ceo_event = CEOInterruptEvent(
            message="Focus on security requirements immediately",
            override_context=True,
            resume_action="steer"
        )
        
        # Handle CEO interrupt
        await agent._handle_ceo_interrupt_event(ceo_event)
        
        # Check that interrupt was processed
        assert agent._ceo_interrupt_event.is_set()
        assert agent._last_interrupt_message == "Focus on security requirements immediately"
        
        # Process the interrupt
        await agent._process_ceo_interrupt()
        
        # Check context is preserved
        context = agent.get_current_context()
        assert context is not None
    
    async def test_meeting_wrap_up_logic(self):
        """Test meeting wrap-up logic in business context."""
        
        agent = create_async_adaptive_agent(
            name="Sarah Martinez",
            occupation="Project Manager"
        )
        
        # Initialize and set business meeting context
        await agent.async_listen("Let's review our project status")
        agent.set_environment_context(
            meeting_type="business_meeting",
            agenda_items=["status review", "next steps"],
            participant_roles=["project_manager", "developer", "compliance"]
        )
        
        # Test wrap-up behavior (second to last round)
        with pytest.LoggingCapture() as logs:
            await agent.async_act(current_round=6, total_rounds=7)
        
        # Should trigger wrap-up logic for business meetings with 7+ rounds
        assert any("wrap-up" in log.lower() for log in logs.get_logs())
    
    async def test_concurrent_async_adaptive_agents(self):
        """Test running multiple async adaptive agents concurrently."""
        
        # Create different types of agents
        agents = [
            create_async_adaptive_agent("PM", "Project Manager"),
            create_async_adaptive_agent("Dev", "Senior Developer"),
            create_async_adaptive_agent("Compliance", "Compliance Officer")
        ]
        
        # Initialize all agents
        for agent in agents:
            await agent._initialize_event_bus()
        
        # Create concurrent tasks
        tasks = []
        for i, agent in enumerate(agents):
            task = asyncio.create_task(
                agent.async_listen_and_act(f"Please provide input on requirement {i+1}")
            )
            tasks.append(task)
        
        # Run concurrently
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = asyncio.get_event_loop().time()
        
        # Check results
        assert len(results) == 3
        
        # Should complete quickly due to concurrent execution
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should be very fast in mock mode
        
        # All agents should have conversation history
        for agent in agents:
            assert len(agent.conversation_history) > 0
    
    async def test_context_summary_and_state(self):
        """Test getting context summary and state information."""
        
        agent = create_async_adaptive_agent(
            name="Lisa Park",
            occupation="Data Scientist",
            skills=["machine learning", "statistics"]
        )
        
        # Add some conversation history
        await agent.async_listen("Let's analyze the data requirements")
        await agent.async_act(current_round=1, total_rounds=5)
        
        # Get context summary
        summary = agent.get_context_summary()
        
        # Check summary structure
        assert "agent_name" in summary
        assert "agent_type" in summary
        assert "current_context" in summary
        assert "conversation_rounds" in summary
        assert "adaptive_mode" in summary
        assert "async_state" in summary
        
        # Check values
        assert summary["agent_name"] == "Lisa Park"
        assert summary["agent_type"] == "AsyncAdaptiveTinyPerson"
        assert summary["adaptive_mode"] == True
        assert summary["conversation_rounds"] == 1
    
    async def test_environment_context_setting(self):
        """Test explicitly setting environment context."""
        
        agent = create_async_adaptive_agent(
            name="Robert Kim",
            occupation="Senior Software Engineer"
        )
        
        # Set explicit environment context
        agent.set_environment_context(
            meeting_type="technical_review",
            agenda_items=["architecture review", "security assessment"],
            participant_roles=["engineer", "architect", "security_expert"]
        )
        
        # Should influence context detection
        context = agent.get_current_context()
        assert context in [ContextType.TECHNICAL_DISCUSSION, ContextType.BUSINESS_MEETING]
    
    async def test_conversation_context_reset(self):
        """Test resetting conversation context."""
        
        agent = create_async_adaptive_agent(
            name="Maria Gonzalez",
            occupation="Clinical Researcher"
        )
        
        # Build up conversation history
        await agent.async_listen("Let's discuss the clinical trial")
        await agent.async_listen("We need to review the patient data")
        await agent.async_act(current_round=1, total_rounds=3)
        
        # Check initial state
        assert len(agent.conversation_history) > 0
        assert agent.round_count > 0
        
        # Reset context
        agent.reset_conversation_context()
        
        # Check reset state
        assert len(agent.conversation_history) == 0
        assert agent.round_count == 0
        assert agent.forced_decision_count == 0
    
    async def test_experience_and_seniority_inference(self):
        """Test automatic inference of experience and seniority."""
        
        # Test senior role
        senior_agent = create_async_adaptive_agent(
            name="Senior Engineer",
            occupation="Senior Software Engineer"
        )
        assert senior_agent._configuration["seniority_level"] == "Senior"
        assert "8+ years" in senior_agent._configuration["years_experience"]
        
        # Test leadership role
        manager_agent = create_async_adaptive_agent(
            name="Tech Director",
            occupation="Technical Director"
        )
        assert manager_agent._configuration["seniority_level"] == "Leadership"
        assert "12+ years" in manager_agent._configuration["years_experience"]
        
        # Test executive role
        cto_agent = create_async_adaptive_agent(
            name="CTO",
            occupation="Chief Technology Officer"
        )
        assert cto_agent._configuration["seniority_level"] == "Executive"
        assert "15+ years" in cto_agent._configuration["years_experience"]


# Mock class for testing without actual TinyPerson dependencies
class MockAsyncAdaptiveTinyPerson(AsyncAdaptiveTinyPerson):
    def __init__(self, name):
        # Minimal initialization for testing
        self.name = name
        self.async_state = "IDLE"
        self._async_lock = asyncio.Lock()
        self._state_lock = threading.Lock()
        self._adaptive_lock = asyncio.Lock()
        self._ceo_interrupt_event = asyncio.Event()
        self._event_bus = None
        self._event_bus_initialized = False
        self._interrupt_context = {}
        self._last_interrupt_message = None
        
        # Adaptive features
        self.context_detector = ContextDetector()
        self.conversation_history = []
        self.round_count = 0
        self.forced_decision_count = 0
        self.adaptive_mode_enabled = True
        self._configuration = {"occupation": "Test Role"}
    
    # Mock methods for testing
    def listen(self, speech, source=None, max_content_length=None):
        return f"[{self.name}] Mock listened to: '{speech}'"
    
    def act(self, **kwargs):
        return f"[{self.name}] Mock acted with params: {kwargs}"
    
    def reset_prompt(self):
        pass  # Mock implementation


@pytest.mark.asyncio
class TestAsyncAdaptiveMockIntegration:
    """Test async adaptive features with mock implementations."""
    
    async def test_mock_async_adaptive_agent(self):
        """Test mock async adaptive agent for integration testing."""
        
        agent = MockAsyncAdaptiveTinyPerson("Test Agent")
        
        # Test basic functionality
        assert agent.name == "Test Agent"
        assert agent.adaptive_mode_enabled == True
        
        # Test async listen
        await agent.async_listen("Hello world")
        assert len(agent.conversation_history) == 1
        
        # Test context detection
        context = agent.get_current_context()
        assert isinstance(context, ContextType)
        
        # Test state management
        state = await agent.get_async_state()
        assert state["state"] == "IDLE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])