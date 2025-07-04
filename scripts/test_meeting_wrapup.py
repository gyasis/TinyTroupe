#!/usr/bin/env python3

import sys
sys.path.append('..')
from datetime import timedelta
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.environment import TinyWorld

# Create a short test meeting to verify wrap-up behavior
world = TinyWorld("Quick Test Meeting", max_additional_targets_to_display=1)

# Create just 2 agents for a quick test
pm = create_adaptive_agent(
    name="Alice PM",
    occupation="Project Manager",
    years_experience="5+ years"
)

dev = create_adaptive_agent(
    name="Bob Dev", 
    occupation="Senior Developer",
    years_experience="8+ years"
)

world.add_agents([pm, dev])
world.make_everyone_accessible()

# Set meeting context and force business meeting detection
for agent in [pm, dev]:
    agent.set_environment_context(
        meeting_type="technical_decision",
        agenda_items=["Quick Decision", "Next Steps"],
        participant_roles=["PM", "Developer"]
    )
    # Force context detection to business meeting
    from tinytroupe.context_detection import ContextType
    agent.context_detector.current_context = ContextType.BUSINESS_MEETING
    agent.context_detector.context_confidence = 0.9

# Start meeting
pm.listen("We need to quickly decide on our API architecture. Bob, what's your recommendation?")

print("=== TESTING MEETING WRAP-UP BEHAVIOR ===")
print("Running 4 rounds to test wrap-up prompts...")

# Run only 4 rounds to test wrap-up behavior
# Round 3 should trigger "1 minute left" 
# Round 4 should trigger meeting conclusion
world.run(4, timedelta_per_step=timedelta(minutes=5))

# Print conversation transcript to see wrap-up
print("\n=== FINAL CONVERSATION TRANSCRIPT ===")
for agent in world.agents:
    interactions = agent.pretty_current_interactions(max_content_length=None)
    lines = interactions.split('\n')
    for line in lines:
        if '[TALK]' in line and 'acts:' in line:
            # Extract speaker and message
            parts = line.split(' acts: [TALK]')
            if len(parts) == 2:
                speaker = parts[0].split(']')[-1].strip()
                print(f"\n{speaker} said:")
                # Get the message content
                idx = lines.index(line)
                msg_idx = idx + 1
                while msg_idx < len(lines) and lines[msg_idx].strip().startswith('>'):
                    print(lines[msg_idx].strip()[1:].strip())
                    msg_idx += 1

print("\n=== MEETING COMPLETE ===")
print("Check if round 3 asks for final considerations and round 4 provides summary!")