#!/usr/bin/env python3
"""
Test script to verify agents can RECALL commitments made by other agents in meetings.
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

# Create world and add agents
world = TinyWorld("Test Meeting", max_additional_targets_to_display=1)
world.add_agents([emily, alex])
world.make_everyone_accessible()

# Set business meeting context
for agent in [emily, alex]:
    agent.set_environment_context(
        meeting_type="technical_decision",
        agenda_items=["Task Assignment Test"],
        participant_roles=["Project Manager", "Developer"]
    )

print("=== TESTING RECALL OF COMMITMENTS ===")

# Simulate Alex making a commitment
print("\n--- Step 1: Alex makes a commitment ---")
alex.listen("We need someone to handle the database migration task.")
alex.act()

alex.listen("I can handle the database migration. I have experience with PostgreSQL and can complete it by Friday.")
alex.act()

print(f"Alex's recent actions: {alex.pretty_current_interactions()}")

# Now test if Emily can recall Alex's commitment
print("\n--- Step 2: Emily tries to recall Alex's commitment ---")
emily.listen("We need to assign the database migration task to someone.")

# Force Emily to think about checking memory
emily.think("I need to check if anyone already volunteered for the database migration task.")

# Check Emily's memory for the commitment
print("\n--- Step 3: Check Emily's memory contents ---")
memories = emily.retrieve_relevant_memories("database migration Alex volunteer", top_k=5)
print(f"Emily's relevant memories about database migration: {memories}")

# Check all of Emily's recent memories
recent_memories = emily.retrieve_recent_memories()
print(f"\nEmily's recent memories: {recent_memories}")

# Check episodic memory directly
print(f"\nEmily's episodic memory count: {len(emily.episodic_memory.memory)}")
if emily.episodic_memory.memory:
    print("Recent episodic entries:")
    for i, entry in enumerate(emily.episodic_memory.memory[-5:]):
        print(f"  {i}: {entry}")

# CRITICAL: Check if Emily heard Alex's conversations!
print("\n--- Step 4: CRITICAL - Did Emily hear Alex's messages? ---")
print("Looking for Alex's voice in Emily's memory...")
for i, entry in enumerate(emily.episodic_memory.memory):
    if 'Alex' in str(entry):
        print(f"Found Alex mention in entry {i}: {entry}")

# Test Emily's response after recall
emily.act()
print(f"Emily's response after recall: {emily.pretty_current_interactions()}")

print("\n=== TEST COMPLETE ===")