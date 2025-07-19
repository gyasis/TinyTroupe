#!/usr/bin/env python3
"""
Test script to verify Emily's wrap-up control works correctly.
- With < 7 rounds: NO wrap-up behavior
- With >= 7 rounds: Wrap-up only in second-to-last round
"""

import sys
sys.path.append('..')
from tinytroupe.agent import TinyPerson
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld
from datetime import timedelta

# Clean output
TinyPerson.rich_text_display = False
TinyWorld.debug_display = False

print("=== TESTING EMILY'S WRAP-UP CONTROL ===")

# Create simple test agents
emily = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager",
    personality_traits=["Organized", "Facilitator"]
)

alex = TinyPerson("Alex Chen")
alex.define("occupation", "Developer")

# Create world
world = TinyWorld("Test Meeting", is_meeting=True)
world.add_agents([emily, alex])
world.make_everyone_accessible()

# Set business meeting context for Emily
emily.set_environment_context(
    meeting_type="technical_decision",
    participant_roles=["Emily Martinez (Project Manager)", "Alex Chen (Developer)"]
)

print("\n🧪 TEST 1: Short meeting (5 rounds) - Emily should NOT wrap up")
print("Expected: No wrap-up behavior, natural conversation only")

# Reset for test
emily.listen("Let's discuss our project timeline quickly.")

# Test with 5 rounds (< 7, so no wrap-up)
world.run(5, timedelta_per_step=timedelta(minutes=2))

print("\n" + "="*60)
print("🧪 TEST 2: Longer meeting (8 rounds) - Emily should wrap up in round 7")
print("Expected: Normal discussion, then wrap-up prompt in round 7")

# Create fresh world for second test
world2 = TinyWorld("Test Meeting 2", is_meeting=True) 
emily2 = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager", 
    personality_traits=["Organized", "Facilitator"]
)

alex2 = TinyPerson("Alex Chen")
alex2.define("occupation", "Developer")

world2.add_agents([emily2, alex2])
world2.make_everyone_accessible()

emily2.set_environment_context(
    meeting_type="technical_decision",
    participant_roles=["Emily Martinez (Project Manager)", "Alex Chen (Developer)"]
)

emily2.listen("Let's have a detailed discussion about our project architecture.")

# Test with 8 rounds (>= 7, so wrap-up should trigger in round 7)
world2.run(8, timedelta_per_step=timedelta(minutes=3))

print("\n" + "="*60)
print("✅ WRAP-UP CONTROL TEST COMPLETE")
print("\n📊 Results Summary:")
print("- Test 1 (5 rounds): Emily should NOT have triggered wrap-up")
print("- Test 2 (8 rounds): Emily should have triggered wrap-up in round 7")
print("\n💡 This prevents premature meeting conclusions in short discussions!")