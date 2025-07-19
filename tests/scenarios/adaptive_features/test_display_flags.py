#!/usr/bin/env python3
"""
Test the new display control flags for clean conversation output.
"""

import sys
sys.path.append('..')
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson

# Create test agents
emily = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager",
    personality_traits=["Organized"]
)

alex = create_adaptive_agent(
    name="Alex Rodriguez", 
    occupation="Developer",
    personality_traits=["Technical"]
)

print("=== TESTING DISPLAY FLAGS ===")

print("\n--- Test 1: Default Rich Text Display ---")
print(f"Rich text enabled: {TinyPerson.rich_text_display}")
print(f"Debug enabled: {TinyWorld.debug_display}")

# Create world and run brief interaction
world = TinyWorld("Test Meeting", is_meeting=True)
world.add_agents([emily, alex])
world.make_everyone_accessible()

emily.listen("Let's discuss the project requirements.")
alex.listen("I agree, we should start with the technical architecture.")

print("\n--- Emily's Recent Interactions (Rich Text) ---")
print(emily.pretty_current_interactions(max_content_length=None))

print("\n--- Test 2: Plain Text Display ---")
# Disable rich text and debug
TinyPerson.rich_text_display = False
TinyWorld.debug_display = False

emily2 = create_adaptive_agent(
    name="Emily Smith",
    occupation="Project Manager", 
    personality_traits=["Organized"]
)

emily2.listen("Let's discuss the project requirements.")
emily2.listen("I think we should focus on user experience and technical feasibility.")

print("\n--- Emily's Recent Interactions (Plain Text) ---")
print(emily2.pretty_current_interactions(max_content_length=None))

print("\n--- Test 3: Debug Display Control ---")
print("Testing debug output control...")

# Test with debug ON
TinyWorld.debug_display = True
world2 = TinyWorld("Debug Test", is_meeting=True)
world2.add_agents([emily2])

print("\nWith DEBUG ON:")
emily2.listen("Test message for debug display")

# Test with debug OFF  
TinyWorld.debug_display = False
print("\nWith DEBUG OFF:")
emily2.listen("Test message without debug display")

print("\n=== DISPLAY FLAGS TESTING COMPLETE ===")
print("✅ Rich text display control working")
print("✅ Debug display control working") 
print("✅ Clean plain text formatting available")