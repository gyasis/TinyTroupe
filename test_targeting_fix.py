#!/usr/bin/env python3
"""
Test script to verify TALK action targeting works correctly.
"""

import sys
sys.path.append('..')
from tinytroupe.agent import TinyPerson
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld

# Create minimal test scenario
emily = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager",
    personality_traits=["Organized"]
)

james = TinyPerson("Dr. James Wilson") 
james.define("occupation", "CTO")

sarah = TinyPerson("Dr. Sarah Chen")
sarah.define("occupation", "Physician")

# Create world
world = TinyWorld("Test Meeting", is_meeting=True)
world.add_agents([emily, james, sarah])
world.make_everyone_accessible()

# Set context with full names
emily.set_environment_context(
    meeting_type="technical_decision",
    participant_roles=[
        "Emily Martinez (Project Manager)", 
        "Dr. James Wilson (CTO)", 
        "Dr. Sarah Chen (Physician)"
    ]
)

print("=== TESTING TALK TARGETING ===")
print("Agent order:")
print("1. Emily Martinez")  
print("2. Dr. James Wilson")
print("3. Dr. Sarah Chen")

print("\n--- Test: Emily addressing Dr. Sarah Chen by full name ---")

# Test the targeting with full name
emily.listen("Dr. Sarah Chen, could you please share your clinical requirements?")

# Check Emily's action
emily.act()

print("\n--- Checking if targeting is correct ---")
print("Expected: Emily --> Dr. Sarah Chen")
print("Let's see what actually happens...")

# Run one round to see the targeting
world.run(1)

print("\n=== TEST COMPLETE ===")