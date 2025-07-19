#!/usr/bin/env python3
"""
Test wrap-up logic detection in adaptive agents.
"""

import sys
sys.path.append('..')
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld

# Create a test agent
emily = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager",
    personality_traits=["Organized", "Detail-oriented"]
)

# Check adaptive agent properties
print("=== ADAPTIVE AGENT DEBUG INFO ===")
print(f"Emily adaptive_mode_enabled: {emily.adaptive_mode_enabled}")
print(f"Emily context_detector.current_context: {emily.context_detector.current_context}")

# Set environment context to ensure business meeting detection
emily.set_environment_context(
    meeting_type="technical_decision",
    agenda_items=["Test Agenda Item"],
    participant_roles=["Project Manager"]
)

print(f"After set_environment_context:")
print(f"Emily context_detector.current_context: {emily.context_detector.current_context}")

# Test the act method with wrap-up round numbers
print("\n=== TESTING WRAP-UP LOGIC ===")
print("Testing round 2/3 (should trigger wrap-up)")
emily.act(current_round=2, total_rounds=3)

print("\nTesting round 3/3 (should trigger conclusion)")  
emily.act(current_round=3, total_rounds=3)

print("\n=== TEST COMPLETE ===")