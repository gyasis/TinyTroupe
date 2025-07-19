#!/usr/bin/env python3
"""
Test script to verify meeting-wide broadcasting functionality.
"""

import sys
sys.path.append('..')
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld

# Create test agents
emily = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager",
    personality_traits=["Organized", "Detail-oriented"]
)

alex = create_adaptive_agent(
    name="Alex Rodriguez", 
    occupation="Developer",
    personality_traits=["Technical", "Proactive"]
)

# Create world WITH meeting flag enabled
world = TinyWorld("Meeting Test", is_meeting=True)
world.add_agents([emily, alex])
world.make_everyone_accessible()

print("=== TESTING MEETING-WIDE BROADCASTING ===")
print(f"World is_meeting flag: {world.is_meeting}")

# Test 1: Alex talks to Emily, but in meeting mode everyone should hear
print("\n--- Test 1: Alex talks to Emily in meeting mode ---")
alex.listen("We need to discuss the database migration task.")

# Use world.run() to properly simulate the conversation flow
print("\n--- Running world simulation for 1 step ---")
world.run(steps=1)

# Check if Emily heard Alex's message
print(f"\n--- Emily's memory after Alex's message ---")
print(f"Emily's memory count: {len(emily.episodic_memory.memory)}")
for i, entry in enumerate(emily.episodic_memory.memory):
    print(f"  {i}: {entry}")

# Test 2: Emily responds and Alex should hear it
print("\n--- Test 2: Emily responds ---")
emily.listen("I can coordinate with the team on this.")
world.run(steps=1)

# Check if Alex heard Emily's message
print(f"\n--- Alex's memory after Emily's response ---")
print(f"Alex's memory count: {len(alex.episodic_memory.memory)}")
for i, entry in enumerate(alex.episodic_memory.memory):
    print(f"  {i}: {entry}")

print("\n=== TESTING COMPLETE ===")