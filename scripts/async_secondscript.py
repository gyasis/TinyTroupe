# %%
import json
import sys
import asyncio
from datetime import timedelta
sys.path.append('..')
import tinytroupe
from tinytroupe.agent import TinyPerson  # Standard agents for regular participants
from tinytroupe.async_adaptive_agent import create_async_adaptive_agent  # NEW: Async + Adaptive agents
from tinytroupe.async_world import AsyncTinyWorld  # NEW: Async world with CEO interrupt
from tinytroupe.environment import TinyWorld, TinySocialNetwork
from tinytroupe.factory import TinyPersonFactory
from tinytroupe.extraction import default_extractor as extractor

# ENABLE CLEAN OUTPUT MODE
TinyPerson.rich_text_display = False  # No Rich text formatting
TinyWorld.debug_display = False       # No debug messages

# ASYNC HYBRID ARCHITECTURE APPROACH:
# This script uses the new async capabilities with the optimal hybrid architecture pattern:
# 1. ORCHESTRATOR: Project Manager (AsyncAdaptive) - manages meeting flow with concurrent processing
# 2. DOMAIN EXPERTS: CTO + Compliance Officer (AsyncAdaptive) - assert authority concurrently
# 3. REGULAR PARTICIPANTS: Developer + Physician (AsyncAdaptive) - participate with async benefits
# 4. CEO INTERRUPT: Real-time steering capability during simulation
# 5. CONCURRENT PROCESSING: All agents think/act simultaneously for faster meetings
# 6. Clean output mode enabled for readable conversation flow

from dotenv import load_dotenv

# Load environment variables from the specified .env file
load_dotenv(
    "/media/gyasis/Blade 15 SSD/Users/gyasi/Google Drive (not syncing)/Collection/chatrepository/.env",
    override=True,
)

async def run_async_healthcare_blockchain_meeting():
    """
    Run the healthcare blockchain meeting using AsyncAdaptiveTinyPerson agents
    with concurrent processing and CEO interrupt capabilities.
    """
    
    print("=== ASYNC HEALTHCARE BLOCKCHAIN MEETING - ENHANCED ARCHITECTURE ===")
    print("🚀 NEW: All agents use AsyncAdaptiveTinyPerson for concurrent processing")
    print("🚨 NEW: CEO interrupt capability (press SPACEBAR during simulation)")
    print("⚡ NEW: Concurrent agent thinking/acting for faster meetings")
    print("🧠 NEW: Adaptive behavior with context-aware meeting intelligence")
    print("🔧 Clean output mode enabled")
    
    # ============================================================================
    # ORCHESTRATOR: Project Manager (AsyncAdaptive)
    # ============================================================================
    # The PM manages meeting flow, facilitates discussion, and drives wrap-up logic
    # NOW with concurrent processing capabilities
    
    project_manager = create_async_adaptive_agent(
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
    # DOMAIN EXPERT: CTO (AsyncAdaptive)
    # ============================================================================
    # Technical domain expert with authority over architecture decisions
    # NOW with concurrent processing and CEO interrupt handling
    
    head_of_technology = create_async_adaptive_agent(
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
    # DOMAIN EXPERT: Compliance Officer (AsyncAdaptive)  
    # ============================================================================
    # Regulatory domain expert with authority over HIPAA and compliance decisions
    # NOW with concurrent processing for faster compliance reviews
    
    michael = create_async_adaptive_agent(
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
    # TECHNICAL EXPERT: Software Developer (AsyncAdaptive)
    # ============================================================================
    # NOW upgraded to AsyncAdaptive for concurrent processing benefits
    
    software_developer = create_async_adaptive_agent(
        name="Lisa Chen",
        occupation="Senior Software Developer specializing in healthcare applications",
        years_experience="8+ years",
        personality_traits=[
            "Detail-oriented with strong technical expertise",
            "Passionate about clean, maintainable code",
            "Healthcare standards compliance focused"
        ],
        professional_interests=[
            "FHIR-compliant application development",
            "Healthcare data interoperability",
            "API development and microservices"
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
    
    # ============================================================================
    # CLINICAL EXPERT: Physician (AsyncAdaptive)
    # ============================================================================
    # NOW upgraded to AsyncAdaptive for concurrent clinical input
    
    sarah = create_async_adaptive_agent(
        name="Dr. Sarah Chen",
        occupation="Physician with healthcare technology expertise",
        years_experience="10+ years",
        personality_traits=[
            "Tech-savvy clinician frustrated with current EHR limitations", 
            "Patient care focused with practical technology perspective",
            "Strong advocate for usable clinical workflows"
        ],
        professional_interests=[
            "Clinical workflow optimization",
            "Patient care technology",
            "Medical records accessibility"
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
    
    # ============================================================================
    # BLOCKCHAIN EXPERT: Blockchain Developer (AsyncAdaptive)
    # ============================================================================
    # NOW upgraded to AsyncAdaptive for concurrent blockchain expertise
    
    alex = create_async_adaptive_agent(
        name="Alex Rodriguez",
        occupation="Senior Blockchain Developer with healthcare specialization",
        years_experience="6+ years",
        personality_traits=[
            "Blockchain expert focused on healthcare applications",
            "Security and scalability focused", 
            "Practical implementation approach"
        ],
        professional_interests=[
            "Blockchain healthcare applications",
            "Ethereum and Hyperledger development",
            "Healthcare supply chain solutions"
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
    
    # ============================================================================
    # CREATE ASYNC HYBRID MEETING ENVIRONMENT WITH CEO INTERRUPT
    # ============================================================================
    
    print("🏗️ Orchestrator: Emily Martinez (PM, AsyncAdaptive)")
    print("🧠 Domain Experts: Dr. James Wilson (CTO, AsyncAdaptive) + Michael Thompson (Compliance, AsyncAdaptive)")
    print("💻 Technical Experts: Lisa Chen (Dev, AsyncAdaptive) + Alex Rodriguez (Blockchain, AsyncAdaptive)")
    print("👩‍⚕️ Clinical Expert: Dr. Sarah Chen (MD, AsyncAdaptive)")
    print("⚡ ALL agents now use concurrent processing")
    print("🚨 CEO interrupt enabled (press SPACEBAR during simulation)")
    
    # Create async world with meeting broadcasting and CEO interrupt enabled
    world = AsyncTinyWorld(
        name="Medical Records Blockchain Project Meeting", 
        agents=[project_manager, head_of_technology, michael, software_developer, sarah, alex],
        max_additional_targets_to_display=None, 
        is_meeting=True,  # Enable cross-agent communication
        enable_ceo_interrupt=True,  # Enable real-time CEO steering
        ceo_interrupt_keys=['space']  # Press spacebar for interrupts
    )
    
    # Make all agents able to communicate with each other
    world.make_everyone_accessible()
    
    # Set meeting context for ALL AGENTS (since they're all AsyncAdaptive now)
    # This ensures all agents recognize this as a technical decision meeting
    all_agents = [project_manager, head_of_technology, michael, software_developer, sarah, alex]
    for agent in all_agents:
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
    
    print("✅ Meeting context set for all async adaptive agents")
    print("✅ Concurrent processing enabled for all participants")
    print("✅ CEO interrupt monitoring active")
    
    # Start the conversation with Project Manager leading
    await project_manager.async_listen("""
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
    
    print("\n--- Async Agent Profiles ---")
    print(f"Emily Martinez (Orchestrator): {project_manager.minibio()}")
    print(f"Dr. James Wilson (Domain Expert): {head_of_technology.minibio()}")
    print(f"Michael Thompson (Domain Expert): {michael.minibio()}")
    print(f"Lisa Chen (Technical Expert): {software_developer.minibio()}")
    print(f"Dr. Sarah Chen (Clinical Expert): {sarah.minibio()}")
    print(f"Alex Rodriguez (Blockchain Expert): {alex.minibio()}")
    
    print("\n" + "="*80)
    print("ASYNC MEETING SIMULATION - CONCURRENT PROCESSING WITH CEO INTERRUPT")
    print("="*80)
    print("💡 All agents process concurrently for faster meetings")
    print("🚨 Press SPACEBAR during simulation for real-time CEO steering")
    print("🧠 Adaptive behavior provides intelligent meeting management")
    print("⚡ Enjoy the speed of concurrent agent processing!")
    
    # Run the async simulation with concurrent processing and CEO interrupt
    await world.async_run(
        steps=10, 
        timedelta_per_step=timedelta(minutes=5),
        enable_ceo_interrupt=True
    )
    
    print("\n" + "="*80)
    print("EXTRACTING STRUCTURED RESULTS FROM ASYNC MEETING")
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
    extractor.save_as_json("../data/extractions/async_healthcare_blockchain_meeting.json")
    
    print("\n--- Meeting Results Summary ---")
    if meeting_results:
        for field, content in meeting_results.items():
            print(f"\n📋 {field.replace('_', ' ').title()}:")
            if isinstance(content, list):
                for item in content:
                    print(f"  • {item}")
            else:
                print(f"  {content}")
    
    # Show async performance metrics
    async_state = world.get_async_state()
    print(f"\n--- Async Performance Metrics ---")
    print(f"⚡ Async agents: {len(async_state['async_agents'])}")
    print(f"🔄 Sync agents: {len(async_state['sync_agents'])}")
    print(f"🚨 CEO monitoring: {async_state['ceo_monitoring']}")
    print(f"⏸️ Simulation paused: {async_state['is_paused']}")
    
    # Show context summaries for all adaptive agents
    print("\n--- Agent Context Summaries ---")
    for agent in all_agents:
        summary = await agent.get_context_summary()
        print(f"🧠 {agent.name}:")
        print(f"   Context: {summary['current_context']}")
        print(f"   Rounds: {summary['conversation_rounds']}")
        print(f"   Messages: {summary['recent_messages']}")
        print(f"   Adaptive: {summary['adaptive_mode']}")
    
    print("\n" + "="*80)
    print("ASYNC EXTRACTION-BASED APPROACH ANALYSIS")
    print("="*80)
    
    print("\n--- Async Hybrid Architecture Benefits ---")
    print("🚀 Concurrent Processing: All agents think/act simultaneously")
    print("🚨 Real-time Control: CEO can interrupt and steer at any time")
    print("🧠 Intelligent Behavior: Context-aware adaptive responses")
    print("⚡ Performance: Faster meetings through parallel processing")
    print("🎛️ Smart Wrap-up: Intelligent meeting conclusions (7+ rounds)")
    print("📊 Rich Insights: Comprehensive context tracking per agent")
    
    print("\n--- Why Async + Adaptive is Superior ---")
    print("✅ Concurrent agent processing (vs sequential)")
    print("✅ Real-time CEO interrupt and steering capability")
    print("✅ Context-aware meeting intelligence")
    print("✅ Natural conversations with intelligent wrap-up")
    print("✅ All agents have adaptive capabilities")
    print("✅ Structured results extracted post-conversation")
    print("✅ JSON output perfect for downstream processing")
    print("✅ Performance metrics and context tracking")
    
    print("\n--- Enhanced Architecture Components ---")
    print("🏗️ Orchestrator (Emily): AsyncAdaptive with meeting facilitation")
    print("🧠 Domain Experts (James, Michael): AsyncAdaptive with authority")  
    print("💻 Technical Experts (Lisa, Alex): AsyncAdaptive with implementation focus")
    print("👩‍⚕️ Clinical Expert (Sarah): AsyncAdaptive with clinical perspective")
    print("📊 Extraction System: Captures structured insights automatically")
    print("🎛️ Smart Wrap-Up Control: Intelligent meeting conclusions")
    print("🚨 CEO Interrupt: Real-time steering and control")
    
    # Clean shutdown
    await world.shutdown()
    
    print("\n=== ASYNC EXTRACTION-BASED MEETING SYSTEM COMPLETE ===")


# %%
# Main execution
if __name__ == "__main__":
    print("🚀 Starting Async Healthcare Blockchain Meeting")
    print("💡 This version uses AsyncAdaptiveTinyPerson for all agents")
    print("⚡ Concurrent processing + CEO interrupt capabilities")
    print("🚨 Press SPACEBAR during simulation for real-time steering")
    print()
    
    try:
        asyncio.run(run_async_healthcare_blockchain_meeting())
    except KeyboardInterrupt:
        print("\n🛑 Meeting interrupted by user")
    except Exception as error:
        print(f"\n❌ Meeting failed: {error}")
        import traceback
        traceback.print_exc()

# %%