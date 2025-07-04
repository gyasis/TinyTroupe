"""
CEO Interrupt System for TinyTroupe - Real-time simulation control

This module provides the CEO interrupt functionality allowing real-time 
intervention in TinyTroupe simulations. The CEO can pause, interrupt, and 
redirect agent conversations with keypress controls.
"""

import asyncio
import logging
import sys
import os
import contextlib
from typing import Optional, Callable, Any
from datetime import datetime

# Platform-specific imports for keypress detection
try:
    import aioconsole
    AIOCONSOLE_AVAILABLE = True
except ImportError:
    AIOCONSOLE_AVAILABLE = False
    logging.warning("aioconsole not available - CEO interrupt will use fallback input")

# Platform-specific terminal handling
if sys.platform == "win32":
    try:
        import msvcrt
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    try:
        import termios
        import tty
        import select
        UNIX_AVAILABLE = True
    except ImportError:
        UNIX_AVAILABLE = False

from .async_event_bus import get_event_bus, EventType, CEOInterruptEvent

logger = logging.getLogger("tinytroupe")

# Constants for CEO commands
INTERRUPT_COMMANDS = ['interrupt', 'stop', 'pause']
RESUME_COMMANDS = ['resume', 'continue']
END_COMMANDS = ['end', 'quit', 'exit']
STEER_COMMANDS = ['steer', 'redirect']


class CEOInterruptHandler:
    """
    Handles CEO interrupt functionality with cross-platform keypress detection
    
    Features:
    - Async keypress monitoring (Esc, Space, or custom keys)
    - CEO message input and broadcasting
    - Simulation pause/resume/end controls
    - Cross-platform compatibility (Windows, Linux, macOS)
    - Graceful fallback to standard input if platform features unavailable
    """
    
    def __init__(self, 
                 interrupt_keys: list = None,
                 prompt_text: str = "CEO Interrupt - Enter directive (or 'resume'/'end'): "):
        """
        Initialize CEO interrupt handler
        
        Args:
            interrupt_keys: List of keys that trigger interrupts (default: ['esc', ' '])
            prompt_text: Text to display when requesting CEO input
        """
        self.interrupt_keys = interrupt_keys or ['esc', ' ']  # Escape or Space
        self.prompt_text = prompt_text
        self.monitoring = False
        self.event_bus = None
        self._monitor_task: Optional[asyncio.Task] = None
        self._original_terminal_settings = None
        self._platform_strategy = self._determine_platform_strategy()
        
    async def start_monitoring(self):
        """Start monitoring for CEO interrupt keypresses"""
        if self.monitoring:
            return
            
        self.event_bus = await get_event_bus()
        self.monitoring = True
        
        # Use platform strategy
        method_name, description = self._platform_strategy
        method = getattr(self, method_name)
        self._monitor_task = asyncio.create_task(method())
        logger.info(f"CEO interrupt monitoring started ({description})")
            
    async def stop_monitoring(self):
        """Stop monitoring for CEO interrupt keypresses"""
        if not self.monitoring:
            return
            
        self.monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
                
        # Restore terminal settings if modified
        try:
            if self._original_terminal_settings and UNIX_AVAILABLE:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._original_terminal_settings)
        except Exception as error:
            logger.error(f"Error restoring terminal settings: {error}")
            
        logger.info("CEO interrupt monitoring stopped")
        
    def _determine_platform_strategy(self):
        """Determine the best monitoring strategy for the current platform"""
        if AIOCONSOLE_AVAILABLE:
            return ("_monitor_with_aioconsole", "aioconsole")
        elif sys.platform == "win32" and WIN32_AVAILABLE:
            return ("_monitor_windows", "Windows")
        elif UNIX_AVAILABLE:
            return ("_monitor_unix", "Unix")
        else:
            return ("_monitor_fallback", "fallback mode")
            
    @contextlib.contextmanager
    def _raw_terminal(self):
        """Context manager to set terminal to raw mode and restore settings"""
        if not UNIX_AVAILABLE:
            yield
            return
            
        original_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            yield
        except Exception as error:
            logger.error(f"Error in raw terminal mode: {error}")
        finally:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
            except Exception as error:
                logger.error(f"Error restoring terminal settings: {error}")
        
    async def _monitor_with_aioconsole(self):
        """Monitor keypresses using aioconsole (preferred method)"""
        print("🎯 CEO Interrupt Active - Press Esc or Space to interrupt simulation")
        
        while self.monitoring:
            try:
                # Non-blocking input with aioconsole
                key = await asyncio.wait_for(aioconsole.ainput(""), timeout=0.1)
                
                if self._is_interrupt_key(key):
                    await self._handle_interrupt()
                    
            except asyncio.TimeoutError:
                # Expected - allows checking monitoring flag
                continue
            except Exception as error:
                logger.error(f"Error in aioconsole monitoring: {error}")
                await asyncio.sleep(0.1)
                
    async def _monitor_windows(self):
        """Monitor keypresses on Windows using msvcrt"""
        print("🎯 CEO Interrupt Active - Press Esc or Space to interrupt simulation")
        
        while self.monitoring:
            try:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore')
                    
                    if self._is_interrupt_key(key):
                        await self._handle_interrupt()
                        
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as error:
                logger.error(f"Error in Windows monitoring: {error}")
                await asyncio.sleep(0.1)
                
    async def _monitor_unix(self):
        """Monitor keypresses on Unix systems using termios"""
        print("🎯 CEO Interrupt Active - Press Esc or Space to interrupt simulation")
        
        with self._raw_terminal():
            while self.monitoring:
                try:
                    # Check if input is available
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        
                        if self._is_interrupt_key(key):
                            await self._handle_interrupt()
                            
                    await asyncio.sleep(0.1)
                    
                except Exception as error:
                    logger.error(f"Error in Unix monitoring (key='{key if 'key' in locals() else 'unknown'}'): {error}")
                    await asyncio.sleep(0.1)
                
    async def _monitor_fallback(self):
        """Fallback monitoring using standard input"""
        print("🎯 CEO Interrupt Active - Type 'interrupt' and press Enter to interrupt simulation")
        
        while self.monitoring:
            try:
                # Use a timeout to allow periodic checking
                user_input = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, input, ""), 
                    timeout=1.0
                )
                
                if user_input.lower().strip() in INTERRUPT_COMMANDS:
                    await self._handle_interrupt()
                    
            except asyncio.TimeoutError:
                # Expected - allows checking monitoring flag
                continue
            except Exception as error:
                logger.error(f"Error in fallback monitoring: {error}")
                await asyncio.sleep(0.1)
                
    def _is_interrupt_key(self, key: str) -> bool:
        """Check if the pressed key is an interrupt key"""
        if not key:
            return False
            
        key_lower = key.lower().strip()
        
        # Handle different key representations
        if key_lower in ['esc', 'escape', '\x1b']:  # Escape key
            return 'esc' in [k.lower() for k in self.interrupt_keys]
        elif key == ' ':  # Space key
            return ' ' in self.interrupt_keys
        elif key_lower in [k.lower() for k in self.interrupt_keys]:
            return True
            
        return False
        
    async def _handle_interrupt(self):
        """Handle CEO interrupt - get message and broadcast to agents"""
        try:
            print("\n🚨 CEO INTERRUPT ACTIVATED 🚨")
            print("=" * 50)
            
            # Get CEO directive with input sanitization
            message = await self._get_ceo_input()
            message_clean = message.strip()
            message_lower = message_clean.lower()
            
            if message_lower in END_COMMANDS:
                await self._broadcast_simulation_end()
                self.monitoring = False
                return
            elif message_lower in RESUME_COMMANDS:
                print("✅ Simulation resumed")
                return
            elif message_clean:
                # Broadcast CEO directive
                await self._broadcast_ceo_directive(message_clean)
                
                # Ask for resume action
                resume_action = await self._get_resume_action()
                await self._handle_resume_action(resume_action)
            else:
                print("❌ No message provided - resuming simulation")
                
        except Exception as error:
            logger.error(f"Error handling CEO interrupt: {error}")
            print(f"❌ Error processing interrupt: {error}")
            
    async def _get_ceo_input(self) -> str:
        """Get CEO directive input"""
        return await self._get_input_with_fallback(self.prompt_text)
            
    async def _get_resume_action(self) -> str:
        """Get resume action from CEO"""
        prompt = "Resume action (continue/steer/end): "
        result = await self._get_input_with_fallback(prompt)
        return result if result else "continue"
            
    async def _broadcast_ceo_directive(self, message: str):
        """Broadcast CEO directive to all agents"""
        if self.event_bus:
            await self.event_bus.publish_ceo_interrupt(
                message=message,
                override_context=True,
                resume_action="continue"
            )
            print(f"📢 CEO directive broadcast: {message}")
        else:
            logger.error("Event bus not available for CEO directive")
            
    async def _broadcast_simulation_end(self):
        """Broadcast simulation end event"""
        if self.event_bus:
            from .async_event_bus import Event
            end_event = Event(
                event_type=EventType.SIMULATION_END,
                source="CEO",
                data={"reason": "CEO terminated simulation"}
            )
            await self.event_bus.publish(end_event)
            print("🛑 Simulation terminated by CEO")
        else:
            logger.error("Event bus not available for simulation end")
            
    async def _handle_resume_action(self, action: str):
        """Handle CEO resume action"""
        action_clean = action.lower().strip()
        
        if action_clean in END_COMMANDS:
            await self._broadcast_simulation_end()
            self.monitoring = False
        elif action_clean in STEER_COMMANDS:
            await self._handle_steering()
        else:  # continue or any other input
            print("▶️  Simulation resumed")
            
    async def _handle_steering(self):
        """Handle CEO steering request - get additional context"""
        try:
            steer_prompt = "Enter steering directive (new focus/agenda): "
            steering_message = await self._get_input_with_fallback(steer_prompt)
            
            if steering_message.strip():
                # Broadcast steering directive as high-priority event
                from .async_event_bus import Event
                steer_event = Event(
                    event_type=EventType.SIMULATION_PAUSE,  # Use as steering signal
                    source="CEO",
                    priority=95,  # High priority but below interrupt
                    data={
                        "action": "steer", 
                        "directive": steering_message.strip(),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                if self.event_bus:
                    await self.event_bus.publish(steer_event)
                    print(f"🎯 Steering directive applied: {steering_message.strip()}")
                else:
                    logger.error("Event bus not available for steering")
            else:
                print("🎯 No steering directive provided - continuing with current context")
                
        except Exception as error:
            logger.error(f"Error handling steering: {error}")
            print("🎯 Simulation continuing with original context")
            
    async def _get_input_with_fallback(self, prompt: str) -> str:
        """Get input with proper fallback handling"""
        try:
            if AIOCONSOLE_AVAILABLE:
                return await aioconsole.ainput(prompt)
            else:
                return await asyncio.get_event_loop().run_in_executor(
                    None, input, prompt
                )
        except Exception as error:
            logger.error(f"Error getting input: {error}")
            return ""


# Global CEO interrupt handler
_global_ceo_handler: Optional[CEOInterruptHandler] = None


async def get_ceo_handler() -> CEOInterruptHandler:
    """Get the global CEO interrupt handler"""
    global _global_ceo_handler
    if _global_ceo_handler is None:
        _global_ceo_handler = CEOInterruptHandler()
    return _global_ceo_handler


async def start_ceo_monitoring():
    """Start CEO interrupt monitoring"""
    handler = await get_ceo_handler()
    await handler.start_monitoring()
    return handler


async def stop_ceo_monitoring():
    """Stop CEO interrupt monitoring"""
    global _global_ceo_handler
    if _global_ceo_handler:
        await _global_ceo_handler.stop_monitoring()


# Convenience functions for integration
async def enable_ceo_control():
    """Enable CEO control in simulation"""
    await start_ceo_monitoring()


async def disable_ceo_control():
    """Disable CEO control in simulation"""
    await stop_ceo_monitoring()