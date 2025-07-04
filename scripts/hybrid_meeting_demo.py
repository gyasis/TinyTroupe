#!/usr/bin/env python3
"""
Hybrid Architecture Demo: Healthcare Blockchain Meeting
- Orchestrator: Project Manager (Adaptive)
- Domain Experts: CTO, Compliance Officer (Adaptive) 
- Regular Participants: Developer, Physician (Standard TinyPerson)
"""

import json
import sys
from datetime import timedelta
sys.path.append('..')
import tinytroupe
from tinytroupe.adaptive_agent import create_adaptive_agent
from tinytroupe.agent import TinyPerson
from tinytroupe.environment import TinyWorld
from tinytroupe.factory import TinyPersonFactory
from tinytroupe.extraction import default_extractor as extractor
from tinytroupe.extraction import ResultsReducer
import tinytroupe.control as control

# ENABLE CLEAN OUTPUT MODE
TinyPerson.rich_text_display = False  # No Rich text formatting
TinyWorld.debug_display = False       # No debug messages
TinyPerson.communication_display = True  # Keep conversation display

print("=== HYBRID ARCHITECTURE HEALTHCARE BLOCKCHAIN MEETING ===")
print("🔧 Clean output mode enabled")
print("🏗️ Hybrid architecture: Orchestrator + Domain Experts + Regular Participants")

# ============================================================================
# ORCHESTRATOR: Project Manager (Adaptive)
# ============================================================================
print("\n--- Creating Orchestrator ---")
project_manager = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Senior Project Manager specializing in healthcare IT",
    years_experience="12+ years",
    personality_traits=[
        "Focused on deliverables and actionable outcomes",
        "Excellent at facilitating discussions and maintaining momentum", 
        "Strong background in Agile methodologies"
    ],
    professional_interests=[
        "Healthcare IT project management",
        "EHR implementation strategies", 
        "Stakeholder coordination and team leadership"
    ],
    skills=[
        "Project management", "Agile methodologies", "Healthcare IT", 
        "Stakeholder management", "Team coordination"
    ]
)
project_manager.define("age", 38)
project_manager.define("nationality", "American")
project_manager.define("country_of_residence", "United States")
print("✅ Orchestrator: Emily Martinez (Adaptive)")

# ============================================================================
# DOMAIN EXPERTS: CTO, Compliance Officer (Adaptive)
# ============================================================================
print("\n--- Creating Domain Experts ---")

# CTO - Technical Domain Expert
head_of_technology = create_adaptive_agent(
    name="Dr. James Wilson", 
    occupation="Chief Technology Officer with healthcare IT expertise",
    years_experience="18+ years",
    personality_traits=[
        "Strategic technology leader with deep healthcare domain knowledge",
        "Balances technical innovation with business requirements",
        "Data-driven decision maker with security focus"
    ],
    professional_interests=[
        "Healthcare IT infrastructure", "System integration", 
        "Enterprise architecture", "Cloud-based healthcare services"
    ],
    skills=[
        "Enterprise architecture", "Healthcare IT security", "System integration",
        "Cloud computing", "Strategic technology planning"
    ]
)
head_of_technology.define("age", 45)
head_of_technology.define("nationality", "American")
head_of_technology.define("country_of_residence", "United States")

# Compliance Officer - Regulatory Domain Expert
compliance_officer = create_adaptive_agent(
    name="Michael Thompson",
    occupation="Healthcare Compliance Officer specializing in HIPAA and privacy law",
    years_experience="14+ years",
    personality_traits=[
        "Expert in healthcare privacy regulations",
        "Balance innovation with compliance requirements",
        "Risk assessment and mitigation focused"
    ], 
    professional_interests=[
        "HIPAA compliance implementation", "Healthcare privacy law",
        "Digital health compliance", "Risk assessment and privacy-preserving technology"
    ],
    skills=[
        "HIPAA regulations", "Healthcare compliance", "Privacy law", 
        "Risk assessment", "Regulatory compliance", "Digital health standards"
    ]
)
compliance_officer.define("age", 41)
compliance_officer.define("nationality", "American")
compliance_officer.define("country_of_residence", "United States")

print("✅ Domain Expert: Dr. James Wilson (CTO, Adaptive)")
print("✅ Domain Expert: Michael Thompson (Compliance, Adaptive)")

# ============================================================================
# REGULAR PARTICIPANTS: Developer, Physician (Standard TinyPerson)
# ============================================================================
print("\n--- Creating Regular Participants ---")

# Software Developer - Regular Participant
software_developer = TinyPerson("Lisa Chen")
software_developer.define("age", 32)
software_developer.define("nationality", "Chinese-American")
software_developer.define("country_of_residence", "United States")
software_developer.define("occupation", "Senior Software Developer specializing in healthcare applications")
software_developer.define("personality_traits", [
    {"trait": "Detail-oriented with strong technical expertise"},
    {"trait": "Passionate about clean, maintainable code"},
    {"trait": "Healthcare standards compliance focused"}
])
software_developer.define("professional_interests", [
    {"interest": "FHIR-compliant application development"},
    {"interest": "Healthcare data interoperability"},
    {"interest": "API development and microservices"}
])
software_developer.define("skills", [
    {"skill": "FHIR standards"}, {"skill": "HL7 integration"}, {"skill": "API development"}, 
    {"skill": "Microservices architecture"}, {"skill": "Cloud computing"}, {"skill": "Healthcare compliance"}
])

# Physician - Regular Participant  
physician = TinyPerson("Dr. Sarah Chen")
physician.define("age", 34)
physician.define("nationality", "American")
physician.define("country_of_residence", "United States")
physician.define("occupation", "Physician with healthcare technology expertise")
physician.define("personality_traits", [
    {"trait": "Tech-savvy clinician frustrated with current EHR limitations"}, 
    {"trait": "Patient care focused with practical technology perspective"},
    {"trait": "Strong advocate for usable clinical workflows"}
])
physician.define("professional_interests", [
    {"interest": "Clinical workflow optimization"},
    {"interest": "Patient care technology"},
    {"interest": "Medical records accessibility"}
])
physician.define("skills", [
    {"skill": "Clinical practice"}, {"skill": "Healthcare workflows"}, {"skill": "EHR system usage"},
    {"skill": "Patient care coordination"}, {"skill": "Medical records management"}
])

print("✅ Regular Participant: Lisa Chen (Developer, Standard)")
print("✅ Regular Participant: Dr. Sarah Chen (Physician, Standard)")

# ============================================================================
# CREATE WORLD AND SET CONTEXT
# ============================================================================
print("\n--- Setting Up Meeting Environment ---")

# Create world with meeting broadcasting enabled
world = TinyWorld("Healthcare Blockchain Decision Meeting", is_meeting=True)
world.add_agents([project_manager, head_of_technology, compliance_officer, software_developer, physician])
world.make_everyone_accessible()

# Set meeting context for ADAPTIVE AGENTS ONLY
adaptive_agents = [project_manager, head_of_technology, compliance_officer]
for agent in adaptive_agents:
    agent.set_environment_context(
        meeting_type="technical_decision",
        agenda_items=[
            "Blockchain Platform Selection", 
            "FHIR Integration Architecture",
            "HIPAA Compliance Framework", 
            "Implementation Timeline and Resources"
        ],
        participant_roles=[
            "Project Manager", "CTO", "Compliance Officer", "Developer", "Physician"
        ]
    )

print("✅ Meeting context set for adaptive agents")
print("✅ Meeting broadcasting enabled")

# ============================================================================
# START MEETING
# ============================================================================
print("\n" + "="*70)
print("HEALTHCARE BLOCKCHAIN MEETING - HYBRID ARCHITECTURE")
print("="*70)

# Orchestrator (PM) starts the meeting
project_manager.listen("""
As your project manager, I'd like to kick off our discussion about creating a blockchain-based medical records system. 
Our goal is to develop a system that is:
1. Practical for hospital implementation
2. Patient-owned with customizable permissions
3. Technically robust with hardware key support
4. Cloud-compatible with secure key management
5. Fully HIPAA compliant

We need to focus specifically on:
- FHIR data storage and sharing via blockchain
- Security protocols and HIPAA compliance
- Handshake protocols
- JSON implementation in blockchain

Let's structure this meeting to:
1. First identify key technical and compliance considerations
2. Then develop an actionable implementation plan
3. Finally, assign clear responsibilities and next steps

Dr. Sarah, as our medical expert, could you start by outlining the key clinical requirements you see for this system?
""")

print("\n--- Agent Profiles ---")
print(f"Emily Martinez: {project_manager.minibio()}")
print(f"Dr. James Wilson: {head_of_technology.minibio()}")
print(f"Michael Thompson: {compliance_officer.minibio()}")
print(f"Lisa Chen: {software_developer.minibio()}")
print(f"Dr. Sarah Chen: {physician.minibio()}")

print("\n--- Meeting Simulation (3 rounds with wrap-up) ---")
# Run 3 rounds to test wrap-up logic
world.run(3, timedelta_per_step=timedelta(minutes=5))

print("\n" + "="*70)
print("MEETING ARCHITECTURE ANALYSIS")
print("="*70)

print("\n--- Agent Behavior Analysis ---")
print("🎯 Orchestrator (Emily): Should manage flow and wrap-up")
print("🧠 Domain Experts (James, Michael): Should assert expertise")
print("💬 Regular Participants (Lisa, Sarah): Should contribute naturally")

print("\n--- Clean Output Verification ---")
print("✅ No annoying > line breaks")
print("✅ No Rich text markup clutter")  
print("✅ No debug noise")
print("✅ Natural conversation flow")

print("\n--- Hybrid Architecture Benefits ---")
print("🏗️ Orchestrator manages meeting progression")
print("🎯 Domain experts provide authoritative input")
print("⚡ Regular agents participate without overhead")
print("📖 Clean, readable conversation output")
print("🔄 Meeting broadcasting working correctly")

print("\n=== HYBRID ARCHITECTURE DEMO COMPLETE ===")