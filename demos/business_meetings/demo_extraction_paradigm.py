#!/usr/bin/env python3
"""
Demo: TinyTroupe Extraction Paradigm
Shows how to let agents have natural conversations and extract structured results afterward.
"""

import sys
sys.path.append('..')
from tinytroupe.agent import TinyPerson
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld
from tinytroupe.extraction import default_extractor
from datetime import timedelta

# ENABLE CLEAN OUTPUT MODE
TinyPerson.rich_text_display = False
TinyWorld.debug_display = False

print("=== TINYTROUPE EXTRACTION PARADIGM DEMO ===")
print("Let agents have natural conversations, then extract structured results\n")

# Create a simple technical discussion
print("--- Creating Agents ---")

# Hybrid approach: Adaptive facilitator + Standard participants
facilitator = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager", 
    personality_traits=["Organized", "Facilitator"]
)

developer = TinyPerson("Alex Chen")
developer.define("occupation", "Senior Developer")
developer.define("personality_traits", [{"trait": "Technical expert"}])

designer = TinyPerson("Jordan Smith")
designer.define("occupation", "UX Designer")
designer.define("personality_traits", [{"trait": "User-focused"}])

print(f"✅ {facilitator.name} (Adaptive Facilitator)")
print(f"✅ {developer.name} (Standard Participant)")
print(f"✅ {designer.name} (Standard Participant)")

# Create world with meeting broadcasting
world = TinyWorld("Product Feature Discussion", is_meeting=True)
world.add_agents([facilitator, developer, designer])
world.make_everyone_accessible()

# Set context for adaptive agent only
facilitator.set_environment_context(
    meeting_type="technical_decision",
    agenda_items=["New Dashboard Feature Design"],
    participant_roles=["Project Manager", "Developer", "Designer"]
)

print("\n--- Starting Natural Discussion ---")

# Start with a simple prompt - no forced structure
facilitator.listen("""We need to discuss the new analytics dashboard feature. 
What are your thoughts on the key requirements and technical approach?""")

# Let conversation flow naturally
world.run(3, timedelta_per_step=timedelta(minutes=5))

print("\n" + "="*60)
print("EXTRACTING STRUCTURED RESULTS")
print("="*60)

# Extract different types of information from the same conversation
print("\n--- Extraction 1: Technical Decisions ---")
tech_results = default_extractor.extract_results_from_world(
    world,
    extraction_objective="Extract all technical decisions and implementation details discussed",
    fields=["technologies", "architecture", "technical_requirements"],
    verbose=True
)

print("\n--- Extraction 2: User Requirements ---")
ux_results = default_extractor.extract_results_from_world(
    world,
    extraction_objective="Extract user experience requirements and design considerations",
    fields=["user_needs", "ui_components", "user_flows"],
    verbose=False
)

print("\n--- Extraction 3: Action Items ---")
action_results = default_extractor.extract_results_from_world(
    world,
    extraction_objective="Extract specific action items with assigned owners",
    fields=["action_items", "deadlines", "responsibilities"],
    verbose=False
)

print("\n--- Combined Results ---")
all_results = {
    "technical": tech_results,
    "user_experience": ux_results,
    "actions": action_results
}

# Display results
for category, results in all_results.items():
    print(f"\n📊 {category.replace('_', ' ').title()}:")
    if results:
        for field, content in results.items():
            print(f"  • {field}: {content}")

# Save all extractions
default_extractor.save_as_json("../data/extractions/dashboard_meeting_demo.json")
print("\n✅ Results saved to dashboard_meeting_demo.json")

print("\n" + "="*60)
print("KEY INSIGHTS")
print("="*60)

print("\n🎯 Extraction Paradigm Benefits:")
print("1. Natural conversation flow - no artificial structure")
print("2. Multiple perspectives from single simulation")
print("3. Structured JSON output for easy processing")
print("4. Agents focus on expertise, not meeting management")
print("5. Post-processing flexibility for different use cases")

print("\n✨ This is the TRUE power of TinyTroupe!")
print("   Let agents be themselves, extract insights afterward")

print("\n=== DEMO COMPLETE ===")