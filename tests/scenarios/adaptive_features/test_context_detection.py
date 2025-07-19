#!/usr/bin/env python3
"""
Test context detection with actual business meeting messages.
"""

import sys
sys.path.append('..')
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.context_detection import ContextType

# Create test agent
emily = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Project Manager",
    personality_traits=["Organized", "Detail-oriented"]
)

# Set environment context
emily.set_environment_context(
    meeting_type="technical_decision",
    agenda_items=["Blockchain Platform Selection", "Implementation Timeline"],
    participant_roles=["Project Manager", "CTO", "Developer"]
)

print("=== TESTING CONTEXT DETECTION ===")
print(f"Initial context: {emily.context_detector.current_context}")

# Add business meeting messages to conversation history
business_messages = [
    "We need to decide on the blockchain platform for our medical records system",
    "What should we implement for HIPAA compliance requirements?",
    "Let's make a decision about the architecture and timeline",
    "We need to choose between Ethereum and Hyperledger for our implementation"
]

for msg in business_messages:
    emily.conversation_history.append(msg)

print(f"After adding business messages:")
print(f"Conversation history: {emily.conversation_history}")

# Manually trigger context detection
participants = ["Emily Martinez", "Dr. James Wilson", "Lisa Chen"]
environment_hints = {
    "meeting_type": "technical_decision",
    "agenda_items": ["Blockchain Platform Selection", "Implementation Timeline"],
    "participant_roles": ["Project Manager", "CTO", "Developer"]
}

detected_context = emily.context_detector.detect_context(
    messages=emily.conversation_history,
    participants=participants,
    environment_hints=environment_hints
)

print(f"Detected context: {detected_context}")
print(f"Context confidence: {emily.context_detector.context_confidence}")

# Now test if wrap-up logic triggers
print(f"\n=== TESTING WRAP-UP LOGIC WITH BUSINESS CONTEXT ===")
if detected_context == ContextType.BUSINESS_MEETING:
    print("✅ Business meeting context detected!")
    print("Testing round 2/3 (should trigger wrap-up)")
    emily.act(current_round=2, total_rounds=3)
else:
    print("❌ Business meeting context NOT detected")
    print(f"Current context: {detected_context}")

print("\n=== TEST COMPLETE ===")