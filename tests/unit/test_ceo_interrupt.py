"""
Unit tests for CEO interrupt functionality
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tinytroupe.ceo_interrupt import (
    CEOInterruptHandler, get_ceo_handler, start_ceo_monitoring,
    stop_ceo_monitoring, enable_ceo_control, disable_ceo_control,
    INTERRUPT_COMMANDS, RESUME_COMMANDS, END_COMMANDS, STEER_COMMANDS
)
from tinytroupe.async_event_bus import EventType, initialize_event_bus, shutdown_event_bus

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
async def ceo_handler():
    """Create a CEO interrupt handler for testing"""
    await shutdown_event_bus()  # Clean state
    await initialize_event_bus()
    
    handler = CEOInterruptHandler(
        interrupt_keys=['esc', ' ', 'test'],
        prompt_text="Test prompt: "
    )
    yield handler
    
    if handler.monitoring:
        await handler.stop_monitoring()
    await shutdown_event_bus()


@pytest.fixture
async def running_ceo_handler():
    """Create and start a CEO interrupt handler"""
    await shutdown_event_bus()
    await initialize_event_bus()
    
    handler = CEOInterruptHandler()
    # Don't actually start monitoring (would block tests)
    yield handler
    
    if handler.monitoring:
        await handler.stop_monitoring()
    await shutdown_event_bus()


class TestCEOInterruptHandler:
    """Test CEO interrupt handler functionality"""
    
    def test_initialization(self):
        """Test handler initialization"""
        handler = CEOInterruptHandler(
            interrupt_keys=['a', 'b'],
            prompt_text="Custom prompt: "
        )
        
        assert handler.interrupt_keys == ['a', 'b']
        assert handler.prompt_text == "Custom prompt: "
        assert not handler.monitoring
        assert handler.event_bus is None
        assert handler._monitor_task is None
        
    def test_default_initialization(self):
        """Test handler with default parameters"""
        handler = CEOInterruptHandler()
        
        assert handler.interrupt_keys == ['esc', ' ']
        assert "CEO Interrupt" in handler.prompt_text
        
    def test_platform_strategy_determination(self):
        """Test platform strategy selection"""
        handler = CEOInterruptHandler()
        strategy = handler._determine_platform_strategy()
        
        assert isinstance(strategy, tuple)
        assert len(strategy) == 2
        assert strategy[0].startswith('_monitor_')
        assert isinstance(strategy[1], str)
        
    def test_is_interrupt_key(self):
        """Test interrupt key detection"""
        handler = CEOInterruptHandler(interrupt_keys=['esc', ' ', 'x'])
        
        # Test escape key variations
        assert handler._is_interrupt_key('\x1b')  # Escape character
        assert handler._is_interrupt_key('esc')
        assert handler._is_interrupt_key('ESC')
        assert handler._is_interrupt_key('escape')
        
        # Test space key
        assert handler._is_interrupt_key(' ')
        
        # Test custom key
        assert handler._is_interrupt_key('x')
        assert handler._is_interrupt_key('X')
        
        # Test non-interrupt keys
        assert not handler._is_interrupt_key('a')
        assert not handler._is_interrupt_key('1')
        assert not handler._is_interrupt_key('')
        
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, ceo_handler):
        """Test monitoring lifecycle"""
        assert not ceo_handler.monitoring
        assert ceo_handler._monitor_task is None
        
        # Mock the monitoring method to avoid actual keypress monitoring
        with patch.object(ceo_handler, '_monitor_fallback', new_callable=AsyncMock) as mock_monitor:
            # Force fallback strategy for testing
            ceo_handler._platform_strategy = ('_monitor_fallback', 'test')
            
            await ceo_handler.start_monitoring()
            assert ceo_handler.monitoring
            assert ceo_handler._monitor_task is not None
            assert mock_monitor.called
            
            await ceo_handler.stop_monitoring()
            assert not ceo_handler.monitoring
            
    @pytest.mark.asyncio
    async def test_get_input_with_fallback(self, ceo_handler):
        """Test input handling with fallback"""
        # Mock aioconsole availability
        with patch('tinytroupe.ceo_interrupt.AIOCONSOLE_AVAILABLE', False):
            with patch('builtins.input', return_value='test input') as mock_input:
                result = await ceo_handler._get_input_with_fallback("Test prompt: ")
                assert result == 'test input'
                mock_input.assert_called_once_with("Test prompt: ")
                
    @pytest.mark.asyncio
    async def test_handle_interrupt_commands(self, ceo_handler):
        """Test handling different interrupt commands"""
        ceo_handler.event_bus = await initialize_event_bus()
        
        # Test end command
        with patch.object(ceo_handler, '_get_ceo_input', return_value='end'):
            with patch.object(ceo_handler, '_broadcast_simulation_end') as mock_end:
                await ceo_handler._handle_interrupt()
                mock_end.assert_called_once()
                assert not ceo_handler.monitoring
                
        # Reset monitoring state
        ceo_handler.monitoring = True
        
        # Test resume command
        with patch.object(ceo_handler, '_get_ceo_input', return_value='resume'):
            await ceo_handler._handle_interrupt()
            # Should just print message and return
            
        # Test custom message
        with patch.object(ceo_handler, '_get_ceo_input', return_value='Change strategy'):
            with patch.object(ceo_handler, '_broadcast_ceo_directive') as mock_broadcast:
                with patch.object(ceo_handler, '_get_resume_action', return_value='continue'):
                    await ceo_handler._handle_interrupt()
                    mock_broadcast.assert_called_once_with('Change strategy')
                    
    @pytest.mark.asyncio
    async def test_broadcast_ceo_directive(self, ceo_handler):
        """Test CEO directive broadcasting"""
        # Create mock event bus
        mock_event_bus = AsyncMock()
        ceo_handler.event_bus = mock_event_bus
        
        await ceo_handler._broadcast_ceo_directive("Test directive")
        
        mock_event_bus.publish_ceo_interrupt.assert_called_once_with(
            message="Test directive",
            override_context=True,
            resume_action="continue"
        )
        
    @pytest.mark.asyncio
    async def test_broadcast_simulation_end(self, ceo_handler):
        """Test simulation end broadcasting"""
        mock_event_bus = AsyncMock()
        ceo_handler.event_bus = mock_event_bus
        
        await ceo_handler._broadcast_simulation_end()
        
        mock_event_bus.publish.assert_called_once()
        # Check that published event is simulation end
        call_args = mock_event_bus.publish.call_args[0][0]
        assert call_args.event_type == EventType.SIMULATION_END
        assert call_args.source == "CEO"
        
    @pytest.mark.asyncio
    async def test_handle_steering(self, ceo_handler):
        """Test steering functionality"""
        mock_event_bus = AsyncMock()
        ceo_handler.event_bus = mock_event_bus
        
        with patch.object(ceo_handler, '_get_input_with_fallback', return_value='New focus area'):
            await ceo_handler._handle_steering()
            
            mock_event_bus.publish.assert_called_once()
            # Check that published event has steering data
            call_args = mock_event_bus.publish.call_args[0][0]
            assert call_args.data["action"] == "steer"
            assert call_args.data["directive"] == "New focus area"
            
    @pytest.mark.asyncio
    async def test_handle_resume_actions(self, ceo_handler):
        """Test different resume actions"""
        mock_event_bus = AsyncMock()
        ceo_handler.event_bus = mock_event_bus
        ceo_handler.monitoring = True
        
        # Test end action
        await ceo_handler._handle_resume_action('end')
        assert not ceo_handler.monitoring
        
        # Reset
        ceo_handler.monitoring = True
        
        # Test steer action
        with patch.object(ceo_handler, '_handle_steering') as mock_steer:
            await ceo_handler._handle_resume_action('steer')
            mock_steer.assert_called_once()
            
        # Test continue action
        await ceo_handler._handle_resume_action('continue')
        # Should just print message
        
    @pytest.mark.asyncio
    async def test_error_handling(self, ceo_handler):
        """Test error handling in various methods"""
        # Test error in _get_input_with_fallback
        with patch.object(ceo_handler, '_get_input_with_fallback', side_effect=Exception("Test error")):
            # Should not crash
            await ceo_handler._handle_interrupt()
            
        # Test error in broadcasting
        ceo_handler.event_bus = None  # No event bus
        # Should not crash
        await ceo_handler._broadcast_ceo_directive("Test")
        await ceo_handler._broadcast_simulation_end()


class TestCEOInterruptConstants:
    """Test CEO interrupt command constants"""
    
    def test_command_constants(self):
        """Test that command constants are properly defined"""
        assert 'interrupt' in INTERRUPT_COMMANDS
        assert 'stop' in INTERRUPT_COMMANDS
        assert 'pause' in INTERRUPT_COMMANDS
        
        assert 'resume' in RESUME_COMMANDS
        assert 'continue' in RESUME_COMMANDS
        
        assert 'end' in END_COMMANDS
        assert 'quit' in END_COMMANDS
        assert 'exit' in END_COMMANDS
        
        assert 'steer' in STEER_COMMANDS
        assert 'redirect' in STEER_COMMANDS


class TestGlobalCEOFunctions:
    """Test global CEO handler functions"""
    
    @pytest.mark.asyncio
    async def test_get_ceo_handler_singleton(self):
        """Test that get_ceo_handler returns singleton"""
        # Clear global state
        import tinytroupe.ceo_interrupt
        tinytroupe.ceo_interrupt._global_ceo_handler = None
        
        handler1 = await get_ceo_handler()
        handler2 = await get_ceo_handler()
        
        assert handler1 is handler2
        
    @pytest.mark.asyncio
    async def test_start_stop_ceo_monitoring(self):
        """Test global start/stop functions"""
        # Clear global state
        import tinytroupe.ceo_interrupt
        tinytroupe.ceo_interrupt._global_ceo_handler = None
        
        await shutdown_event_bus()
        await initialize_event_bus()
        
        # Mock the actual monitoring to avoid blocking
        with patch.object(CEOInterruptHandler, 'start_monitoring', new_callable=AsyncMock) as mock_start:
            handler = await start_ceo_monitoring()
            assert isinstance(handler, CEOInterruptHandler)
            mock_start.assert_called_once()
            
        with patch.object(CEOInterruptHandler, 'stop_monitoring', new_callable=AsyncMock) as mock_stop:
            await stop_ceo_monitoring()
            mock_stop.assert_called_once()
            
        await shutdown_event_bus()
        
    @pytest.mark.asyncio
    async def test_enable_disable_ceo_control(self):
        """Test convenience enable/disable functions"""
        await shutdown_event_bus()
        await initialize_event_bus()
        
        with patch('tinytroupe.ceo_interrupt.start_ceo_monitoring') as mock_start:
            await enable_ceo_control()
            mock_start.assert_called_once()
            
        with patch('tinytroupe.ceo_interrupt.stop_ceo_monitoring') as mock_stop:
            await disable_ceo_control()
            mock_stop.assert_called_once()
            
        await shutdown_event_bus()


class TestPlatformSpecificMonitoring:
    """Test platform-specific monitoring methods"""
    
    @pytest.mark.asyncio
    async def test_monitor_fallback(self, ceo_handler):
        """Test fallback monitoring method"""
        # Mock the input to simulate user typing 'interrupt'
        ceo_handler.monitoring = True
        
        with patch('builtins.input', side_effect=['interrupt', 'end']):
            with patch.object(ceo_handler, '_handle_interrupt') as mock_handle:
                # Run for a short time
                monitor_task = asyncio.create_task(ceo_handler._monitor_fallback())
                await asyncio.sleep(0.1)
                ceo_handler.monitoring = False
                
                try:
                    await asyncio.wait_for(monitor_task, timeout=1.0)
                except asyncio.TimeoutError:
                    monitor_task.cancel()
                    
                # Should have called interrupt handler
                assert mock_handle.called
                
    def test_raw_terminal_context_manager(self, ceo_handler):
        """Test raw terminal context manager"""
        # Test with Unix not available (fallback)
        with patch('tinytroupe.ceo_interrupt.UNIX_AVAILABLE', False):
            with ceo_handler._raw_terminal():
                # Should not raise any exceptions
                pass
                
        # Test with Unix available but mocked
        with patch('tinytroupe.ceo_interrupt.UNIX_AVAILABLE', True):
            with patch('tinytroupe.ceo_interrupt.termios') as mock_termios:
                mock_termios.tcgetattr.return_value = "mock_settings"
                
                with ceo_handler._raw_terminal():
                    pass
                    
                # Should have called tcgetattr and tcsetattr
                assert mock_termios.tcgetattr.called
                assert mock_termios.tcsetattr.called


@pytest.mark.asyncio
async def test_integration_ceo_interrupt_flow():
    """Integration test for complete CEO interrupt flow"""
    await shutdown_event_bus()
    bus = await initialize_event_bus()
    
    # Create handler
    handler = CEOInterruptHandler()
    handler.event_bus = bus
    
    # Set up event listeners
    published_events = []
    
    async def event_listener(event):
        published_events.append(event)
        
    await bus.subscribe(EventType.CEO_INTERRUPT, event_listener)
    await bus.subscribe(EventType.SIMULATION_END, event_listener)
    
    # Simulate interrupt with directive
    with patch.object(handler, '_get_ceo_input', return_value='Focus on security'):
        with patch.object(handler, '_get_resume_action', return_value='steer'):
            await handler._handle_interrupt()
            
    await asyncio.sleep(0.1)
    
    # Should have published CEO interrupt and steering events
    assert len(published_events) >= 1
    
    # Check CEO interrupt event
    ceo_event = next((e for e in published_events if e.event_type == EventType.CEO_INTERRUPT), None)
    assert ceo_event is not None
    assert ceo_event.data["message"] == "Focus on security"
    
    await shutdown_event_bus()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])