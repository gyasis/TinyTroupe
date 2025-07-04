#!/usr/bin/env python3
"""
Demo clean conversation output with new display flags.
"""

import sys
sys.path.append('..')
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson
from datetime import timedelta

# ENABLE CLEAN OUTPUT MODE
TinyPerson.rich_text_display = False  # No Rich text formatting
TinyWorld.debug_display = False       # No debug messages

print("=== CLEAN CONVERSATION OUTPUT DEMO ===")
print("Rich text: OFF | Debug: OFF")

# Create minimal test agents
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

# Create world with meeting broadcasting
world = TinyWorld("Demo Meeting", is_meeting=True)
world.add_agents([emily, alex])
world.make_everyone_accessible()

# Set business meeting context
for agent in [emily, alex]:
    agent.set_environment_context(
        meeting_type="technical_decision",
        agenda_items=["Platform Selection"],
        participant_roles=["Project Manager", "Developer"]
    )

print("\n--- CLEAN CONVERSATION OUTPUT ---")

# Give initial stimulus
emily.listen("We need to decide on the platform for our blockchain medical records project.")

# Run 2 rounds to see clean conversation flow
world.run(2, timedelta_per_step=timedelta(minutes=5))

print("\n--- FINAL CONVERSATION SUMMARY ---")
print("Emily's interactions:")
print(emily.pretty_current_interactions(max_content_length=None))

print("\nAlex's interactions:")  
print(alex.pretty_current_interactions(max_content_length=None))

print("\n=== DEMO COMPLETE ===")
print("✅ No annoying > line breaks")
print("✅ No Rich text markup clutter")
print("✅ No debug noise")
print("✅ Clean, readable conversation flow")