#!/usr/bin/env python3
"""
Debug the targeting mechanism in TinyWorld conversations.
"""

import sys
sys.path.append('..')
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld

# Create test agents
alex = create_adaptive_agent(
    name="Alex Rodriguez", 
    occupation="Developer",
    personality_traits=["Technical", "Proactive"]
)

emily = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager", 
    personality_traits=["Organized", "Detail-oriented"]
)

# Create world and add agents
world = TinyWorld("Debug Meeting", max_additional_targets_to_display=1)
world.add_agents([alex, emily])
world.make_everyone_accessible()

print("=== DEBUGGING TARGET PARSING ===")

# Test 1: Check agent names in world
print(f"Agents in world: {list(world.name_to_agent.keys())}")
print(f"Alex lookup: {world.get_agent_by_name('Alex Rodriguez')}")
print(f"Emily lookup: {world.get_agent_by_name('Emily Martinez')}")

# Test 2: Use the world.run() method to properly simulate conversation
print(f"\n--- Step 1: Give Alex a stimulus to respond to Emily ---")
alex.listen("Please respond to me Emily about the database task.")

print(f"\n--- Step 2: Run world simulation for 1 step ---")
world.run(steps=1)

# Test 3: Check Emily's memory after the simulation
print(f"\n--- Step 3: Check Emily's memory after world.run() ---")
print(f"Emily's memory count: {len(emily.episodic_memory.memory)}")
for i, entry in enumerate(emily.episodic_memory.memory):
    print(f"  {i}: {entry}")

# Test 4: Check Alex's recent actions through world
print(f"\n--- Step 4: Check Alex's recent actions ---")
alex_actions = alex.pop_latest_actions()
print(f"Alex's popped actions: {alex_actions}")

print("\n=== DEBUG COMPLETE ===")