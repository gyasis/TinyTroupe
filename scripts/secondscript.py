# %%
import json
import sys
from datetime import timedelta
sys.path.append('..')
import tinytroupe
from tinytroupe.agent import TinyPerson  # Standard agents for regular participants
from tinytroupe.adaptive_agent import create_adaptive_agent  # Enhanced agents for orchestrators and domain experts
from tinytroupe.environment import TinyWorld, TinySocialNetwork
from tinytroupe.factory import TinyPersonFactory
from tinytroupe.extraction import default_extractor as extractor

# ENABLE CLEAN OUTPUT MODE
TinyPerson.rich_text_display = False  # No Rich text formatting
TinyWorld.debug_display = False       # No debug messages

# HYBRID ARCHITECTURE APPROACH:
# This script uses the optimal hybrid architecture pattern:
# 1. ORCHESTRATOR: Project Manager (Adaptive) - manages meeting flow and wrap-up
# 2. DOMAIN EXPERTS: CTO + Compliance Officer (Adaptive) - assert authority in their domains  
# 3. REGULAR PARTICIPANTS: Developer + Physician (Standard) - participate naturally
# 4. This provides intelligent meeting management without unnecessary overhead
# 5. Clean output mode enabled for readable conversation flow

from dotenv import load_dotenv

# Load environment variables from the specified .env file
load_dotenv(
    "/media/gyasis/Blade 15 SSD/Users/gyasi/Google Drive (not syncing)/Collection/chatrepository/.env",
    override=True,
)

# ============================================================================
# ORCHESTRATOR: Project Manager (Adaptive)
# ============================================================================
# The PM manages meeting flow, facilitates discussion, and drives wrap-up logic

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

# ============================================================================
# DOMAIN EXPERT: CTO (Adaptive)
# ============================================================================
# Technical domain expert with authority over architecture decisions

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

# ============================================================================
# DOMAIN EXPERT: Compliance Officer (Adaptive)  
# ============================================================================
# Regulatory domain expert with authority over HIPAA and compliance decisions

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

# ============================================================================
# REGULAR PARTICIPANT: Software Developer (Standard TinyPerson)
# ============================================================================
# Contributes technical implementation perspective without adaptive overhead

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

# ============================================================================
# REGULAR PARTICIPANT: Physician (Standard TinyPerson)
# ============================================================================
# Provides clinical requirements perspective without adaptive complexity

sarah = TinyPerson("Dr. Sarah Chen")
sarah.define("age", 34)
sarah.define("nationality", "American")
sarah.define("country_of_residence", "United States")
sarah.define("occupation", "Physician with healthcare technology expertise")
sarah.define("personality_traits", [
    {"trait": "Tech-savvy clinician frustrated with current EHR limitations"}, 
    {"trait": "Patient care focused with practical technology perspective"},
    {"trait": "Strong advocate for usable clinical workflows"}
])
sarah.define("professional_interests", [
    {"interest": "Clinical workflow optimization"},
    {"interest": "Patient care technology"},
    {"interest": "Medical records accessibility"}
])
sarah.define("skills", [
    {"skill": "Clinical practice"}, {"skill": "Healthcare workflows"}, {"skill": "EHR system usage"},
    {"skill": "Patient care coordination"}, {"skill": "Medical records management"}
])

# ============================================================================
# REGULAR PARTICIPANT: Blockchain Developer (Standard TinyPerson)
# ============================================================================
# Provides blockchain technical expertise without adaptive overhead

alex = TinyPerson("Alex Rodriguez")
alex.define("age", 29)
alex.define("nationality", "Hispanic-American")
alex.define("country_of_residence", "United States")
alex.define("occupation", "Senior Blockchain Developer with healthcare specialization")
alex.define("personality_traits", [
    {"trait": "Blockchain expert focused on healthcare applications"},
    {"trait": "Security and scalability focused"}, 
    {"trait": "Practical implementation approach"}
])
alex.define("professional_interests", [
    {"interest": "Blockchain healthcare applications"},
    {"interest": "Ethereum and Hyperledger development"},
    {"interest": "Healthcare supply chain solutions"}
])
alex.define("skills", [
    {"skill": "Blockchain development"}, {"skill": "Ethereum"}, {"skill": "Hyperledger"}, {"skill": "Smart contracts"},
    {"skill": "Healthcare blockchain applications"}, {"skill": "System scalability"}
])

# ============================================================================
# CREATE HYBRID MEETING ENVIRONMENT 
# ============================================================================

print("=== HEALTHCARE BLOCKCHAIN MEETING - HYBRID ARCHITECTURE ===")
print("🏗️ Orchestrator: Emily Martinez (PM, Adaptive)")
print("🧠 Domain Experts: Dr. James Wilson (CTO, Adaptive) + Michael Thompson (Compliance, Adaptive)")
print("💬 Regular Participants: Lisa Chen (Dev, Standard) + Dr. Sarah Chen (MD, Standard) + Alex Rodriguez (Blockchain, Standard)")
print("🔧 Clean output mode enabled")

# Create world with meeting broadcasting enabled
world = TinyWorld("Medical Records Blockchain Project Meeting", max_additional_targets_to_display=None, is_meeting=True)
world.add_agents([project_manager, head_of_technology, michael, software_developer, sarah, alex])

# Make all agents able to communicate with each other
world.make_everyone_accessible()

# Set meeting context for ADAPTIVE AGENTS ONLY (hybrid approach)
# This ensures the orchestrator and domain experts recognize this as a technical decision meeting
adaptive_agents = [project_manager, head_of_technology, michael]
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
            "Emily Martinez (Project Manager)", "Dr. James Wilson (CTO)", 
            "Michael Thompson (Compliance Officer)", "Lisa Chen (Software Developer)", 
            "Dr. Sarah Chen (Physician)", "Alex Rodriguez (Blockchain Expert)"
        ]
    )

print("✅ Meeting context set for adaptive agents only")
print("✅ Regular participants contribute naturally without context overhead")

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

Dr. Sarah Chen, as our medical expert, could you start by outlining the key clinical requirements you see for this system?
""")

print("\n--- Agent Profiles ---")
print(f"Emily Martinez (Orchestrator): {project_manager.minibio()}")
print(f"Dr. James Wilson (Domain Expert): {head_of_technology.minibio()}")
print(f"Michael Thompson (Domain Expert): {michael.minibio()}")
print(f"Lisa Chen (Regular): {software_developer.minibio()}")
print(f"Dr. Sarah Chen (Regular): {sarah.minibio()}")
print(f"Alex Rodriguez (Regular): {alex.minibio()}")

print("\n" + "="*80)
print("MEETING SIMULATION - HYBRID ARCHITECTURE WITH CLEAN OUTPUT")
print("="*80)

# Run the simulation with natural conversation flow
world.run(10, timedelta_per_step=timedelta(minutes=5))

print("\n" + "="*80)
print("EXTRACTING STRUCTURED RESULTS FROM MEETING")
print("="*80)

# Extract technical decisions and action items
print("\n--- Extracting Meeting Results ---")
meeting_results = extractor.extract_results_from_world(
    world,
    extraction_objective="Extract key technical decisions, implementation strategies, compliance requirements, and action items from the healthcare blockchain meeting discussion",
    fields=[
        "technical_decisions",
        "blockchain_platform_choice", 
        "fhir_integration_approach",
        "hipaa_compliance_strategy",
        "action_items_with_owners",
        "timeline_and_milestones",
        "risks_and_concerns",
        "next_steps"
    ],
    fields_hints={
        "technical_decisions": "Specific technology choices made (blockchain platform, consensus mechanism, architecture)",
        "blockchain_platform_choice": "Which blockchain platform was recommended and why",
        "fhir_integration_approach": "How FHIR data will be integrated with blockchain",
        "hipaa_compliance_strategy": "Specific HIPAA compliance measures and privacy protections discussed",
        "action_items_with_owners": "Specific tasks assigned to team members with deadlines",
        "timeline_and_milestones": "Project timeline with key milestones and deliverables",
        "risks_and_concerns": "Technical, regulatory, or implementation risks identified",
        "next_steps": "Immediate next actions and follow-up meetings"
    },
    verbose=True
)

print("\n--- Saving Extraction Results ---")
extractor.save_as_json("../data/extractions/healthcare_blockchain_meeting.json")

print("\n--- Meeting Results Summary ---")
if meeting_results:
    for field, content in meeting_results.items():
        print(f"\n📋 {field.replace('_', ' ').title()}:")
        if isinstance(content, list):
            for item in content:
                print(f"  • {item}")
        else:
            print(f"  {content}")

print("\n" + "="*80)
print("EXTRACTION-BASED APPROACH ANALYSIS")
print("="*80)

print("\n--- Smart Wrap-Up Control Analysis ---")
print("🎯 Emily will NOT wrap up meetings with < 7 rounds")
print("✅ Prevents premature meeting conclusions in short discussions") 
print("✅ Only triggers wrap-up in second-to-last round of longer meetings")
print("✅ Maintains natural conversation flow without forced structure")

print("\n--- Why Extraction + Smart Wrap-Up Control is Superior ---")
print("✅ Natural conversations without premature wrap-up")
print("✅ Orchestrator only concludes when appropriate (7+ rounds)")
print("✅ Agents focus on domain expertise, not meeting management")
print("✅ Structured results extracted post-conversation")
print("✅ Multiple extraction objectives possible from same simulation")
print("✅ JSON output perfect for downstream processing")
print("✅ Simple prompt engineering solution vs complex algorithms")

print("\n--- Hybrid Architecture Benefits ---")
print("🏗️ Orchestrator (Emily): Facilitates discussion naturally")
print("🧠 Domain Experts (James, Michael): Provide authoritative expertise")  
print("💬 Regular Participants (Lisa, Sarah, Alex): Contribute freely")
print("📊 Extraction System: Captures structured insights automatically")
print("🎛️ Smart Wrap-Up Control: Only concludes longer meetings appropriately")

print("\n=== EXTRACTION-BASED MEETING SYSTEM COMPLETE ===")

# %%
