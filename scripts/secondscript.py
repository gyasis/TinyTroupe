# %%
import json
import sys
from datetime import timedelta
sys.path.append('..')
import tinytroupe
# from tinytroupe.agent import TinyPerson  # Original agent - commented out for adaptive enhancement
from tinytroupe.adaptive_agent import create_adaptive_agent  # Enhanced agents for business decision-making
from tinytroupe.environment import TinyWorld, TinySocialNetwork
from tinytroupe.factory import TinyPersonFactory
from tinytroupe.extraction import default_extractor as extractor
from tinytroupe.extraction import ResultsReducer
import tinytroupe.control as control

# WHY ADAPTIVE AGENTS ARE NEEDED HERE:
# This script simulates a healthcare blockchain technical decision meeting where:
# 1. Technical experts need to make specific architecture decisions (blockchain platform, FHIR integration)
# 2. Compliance experts need to assert HIPAA requirements that override technical preferences
# 3. The goal is concrete "actionable implementation plan" and "clear responsibilities"
# 4. Without adaptive agents, this type of meeting often gets stuck in circular "let's coordinate" discussions
# 5. Adaptive agents enable expert authority and decision-forcing for productive business outcomes

from dotenv import load_dotenv

# Load environment variables from the specified .env file
load_dotenv(
    "/media/gyasis/Blade 15 SSD/Users/gyasi/Google Drive (not syncing)/Collection/chatrepository/.env",
    override=True,
)

# Creating adaptive agents for enhanced business decision-making
# These agents will automatically detect this as a technical decision meeting and:
# - Assert expert authority in their domains
# - Make concrete technical recommendations instead of vague coordination talk
# - Force specific decisions when discussions become circular

project_manager = create_adaptive_agent(
    name="Emily Martinez",
    occupation="Senior Project Manager specializing in healthcare IT",
    years_experience="12+ years",
    personality_traits=[
        "Focused on deliverables and actionable outcomes",
        "Excellent at facilitating discussions and maintaining momentum", 
        "Strong background in Agile methodologies",
        "Keeps teams focused while ensuring all voices are heard"
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

# Add demographic information
project_manager.define("age", 38)
project_manager.define("nationality", "American")
project_manager.define("country_of_residence", "United States")

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

# Add demographic information
head_of_technology.define("age", 45)
head_of_technology.define("nationality", "American")
head_of_technology.define("country_of_residence", "United States")

software_developer = create_adaptive_agent(
    name="Lisa Chen",
    occupation="Senior Software Developer specializing in healthcare applications",
    years_experience="8+ years", 
    personality_traits=[
        "Detail-oriented with strong technical expertise",
        "Passionate about clean, maintainable code",
        "Healthcare standards compliance focused"
    ],
    professional_interests=[
        "FHIR-compliant application development", "Healthcare data interoperability",
        "API development and microservices", "Open-source healthcare projects"
    ],
    skills=[
        "FHIR standards", "HL7 integration", "API development", 
        "Microservices architecture", "Cloud computing", "Healthcare compliance"
    ]
)

# Add demographic information
software_developer.define("age", 32)
software_developer.define("nationality", "Chinese-American")
software_developer.define("country_of_residence", "United States")

sarah = create_adaptive_agent(
    name="Dr. Sarah Chen",
    occupation="Physician with healthcare technology expertise",
    years_experience="10+ years",
    personality_traits=[
        "Tech-savvy clinician frustrated with current EHR limitations", 
        "Patient care focused with practical technology perspective",
        "Strong advocate for usable clinical workflows"
    ],
    professional_interests=[
        "Clinical workflow optimization", "Patient care technology",
        "Medical records accessibility", "Healthcare system interoperability"
    ],
    skills=[
        "Clinical practice", "Healthcare workflows", "EHR system usage",
        "Patient care coordination", "Medical records management"
    ]
)

# Add demographic information
sarah.define("age", 34)
sarah.define("nationality", "American")
sarah.define("country_of_residence", "United States")

alex = create_adaptive_agent(
    name="Alex Rodriguez",
    occupation="Senior Blockchain Developer with healthcare specialization",
    years_experience="6+ years",
    personality_traits=[
        "Blockchain expert focused on healthcare applications",
        "Security and scalability focused", 
        "Practical implementation approach"
    ],
    professional_interests=[
        "Blockchain healthcare applications", "Ethereum and Hyperledger development",
        "Healthcare supply chain solutions", "Scalable blockchain architecture"
    ],
    skills=[
        "Blockchain development", "Ethereum", "Hyperledger", "Smart contracts",
        "Healthcare blockchain applications", "System scalability"
    ]
)

# Add demographic information
alex.define("age", 29)
alex.define("nationality", "Hispanic-American")
alex.define("country_of_residence", "United States")

michael = create_adaptive_agent(
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

# Add demographic information
michael.define("age", 41)
michael.define("nationality", "American")
michael.define("country_of_residence", "United States")

# Create a world and add the agents
world = TinyWorld("Medical Records Blockchain Project Meeting", max_additional_targets_to_display=1)
world.add_agents([project_manager, head_of_technology, software_developer, sarah, alex, michael])

# Make all agents able to communicate with each other
world.make_everyone_accessible()

# Set explicit meeting context for optimal adaptive behavior
# This ensures agents recognize this as a technical decision meeting requiring:
# - Expert authority assertion
# - Concrete decision-making
# - Specific technical recommendations
for agent in [project_manager, head_of_technology, software_developer, sarah, alex, michael]:
    agent.set_environment_context(
        meeting_type="technical_decision",
        agenda_items=[
            "Blockchain Platform Selection", 
            "FHIR Integration Architecture",
            "HIPAA Compliance Framework", 
            "Implementation Timeline and Resources"
        ],
        participant_roles=[
            "Project Manager", "CTO", "Software Developer", 
            "Physician", "Blockchain Expert", "Compliance Officer"
        ]
    )

# Start the conversation with Project Manager leading
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

print(project_manager.minibio())
print(head_of_technology.minibio())
print(software_developer.minibio())
print(sarah.minibio())
print(alex.minibio())
print(michael.minibio())

# Run the simulation with 5-minute rounds  
# Rounds 14 and 15 should trigger wrap-up behavior
world.run(15, timedelta_per_step=timedelta(minutes=5))

# Extract just the final round conversations to see if wrap-up worked
print("\n" + "="*60)
print("FINAL ROUND CONVERSATIONS")
print("="*60)

# Get Emily's (PM) final statements
emily_interactions = project_manager.pretty_current_interactions(max_content_length=None)
lines = emily_interactions.split('\n')
talk_count = 0
for i, line in enumerate(lines):
    if '[TALK]' in line and 'Emily Martinez' in line:
        talk_count += 1
        # Get the last few TALK actions
        if talk_count >= len([l for l in lines if '[TALK]' in l and 'Emily Martinez' in l]) - 2:
            print(f"\nEmily Martinez (Round ~{talk_count}):")
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('>'):
                print(lines[j].strip()[1:].strip())
                j += 1

# %%
