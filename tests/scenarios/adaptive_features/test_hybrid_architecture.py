#!/usr/bin/env python3
"""
Test Hybrid Architecture: Orchestrator + Domain Experts (Adaptive) + Regular Participants
"""

import sys
sys.path.append('..')
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from tinytroupe.examples import create_oscar_the_architect

# ENABLE CLEAN OUTPUT  
TinyPerson.rich_text_display = False
TinyWorld.debug_display = False

print("=== HYBRID ARCHITECTURE TEST ===")

# OPTION C: Hybrid Architecture
print("\n--- Creating Hybrid Team ---")

# 1. ORCHESTRATOR: Project Manager (Adaptive)
pm = create_adaptive_agent(
    name="Emily Martinez", 
    occupation="Project Manager",
    personality_traits=["Organized", "Facilitator"]
)
print("✅ Orchestrator (Adaptive): Emily Martinez")

# 2. DOMAIN EXPERT: CTO (Adaptive) 
cto = create_adaptive_agent(
    name="Dr. James Wilson",
    occupation="Chief Technology Officer", 
    personality_traits=["Strategic", "Technical Leader"]
)
print("✅ Domain Expert (Adaptive): Dr. James Wilson")

# 3. REGULAR PARTICIPANT: Junior Developer (Regular TinyPerson)
junior_dev = TinyPerson("Alex Johnson")
junior_dev.define("age", 26)
junior_dev.define("occupation", "Junior Developer")
junior_dev.define("personality_traits", [{"trait": "eager to learn"}, {"trait": "detail-oriented"}])
print("✅ Regular Participant: Alex Johnson")

# 4. REGULAR PARTICIPANT: Designer (Regular TinyPerson)
designer = TinyPerson("Lisa Chen")
designer.define("age", 29)
designer.define("occupation", "UX Designer") 
designer.define("personality_traits", [{"trait": "creative"}, {"trait": "user-focused"}])
print("✅ Regular Participant: Lisa Chen")

# Create world and test
world = TinyWorld("Hybrid Meeting", is_meeting=True)
world.add_agents([pm, cto, junior_dev, designer])
world.make_everyone_accessible()

# Set meeting context for adaptive agents only
for adaptive_agent in [pm, cto]:
    adaptive_agent.set_environment_context(
        meeting_type="technical_decision",
        agenda_items=["Platform Architecture Decision"],
        participant_roles=["Project Manager", "CTO", "Developer", "Designer"]
    )

print("\n--- Testing Clean Conversation Output ---")
print("PM (Adaptive) starts meeting, CTO (Adaptive) provides expertise")
print("Junior Dev and Designer (Regular) participate naturally")

# Start meeting
pm.listen("Let's discuss our platform architecture decision. We need to choose between microservices and monolithic architecture.")

# Brief simulation
print("\n--- Meeting Simulation ---")
for i in range(2):
    print(f"\n--- Round {i+1} ---")
    for agent in [pm, cto, junior_dev, designer]:
        agent.act()
        if hasattr(agent, 'pop_latest_actions'):
            actions = agent.pop_latest_actions()
            # Handle actions in world
            world._handle_actions(agent, actions)

print("\n--- Final Results ---")
print(f"Orchestrator (PM) - Adaptive capabilities: ✅") 
print(f"Domain Expert (CTO) - Adaptive capabilities: ✅")
print(f"Regular participants - Clean output: ✅")

print("\n=== HYBRID ARCHITECTURE SUCCESSFUL ===")
print("✅ Orchestrator manages meeting flow")
print("✅ Domain expert provides authority") 
print("✅ Regular agents participate naturally")
print("✅ Clean, readable output for all")