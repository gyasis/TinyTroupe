"""
Meeting structure frameworks for different types of business meetings.
Provides structured phases and agendas to guide productive business discussions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class MeetingPhase:
    """Represents a phase in a structured meeting."""
    name: str
    duration_minutes: int
    objectives: List[str]
    required_outputs: List[str]
    phase_prompt: str
    success_criteria: List[str]

@dataclass  
class MeetingAgendaItem:
    """Represents an agenda item with expected outcomes."""
    title: str
    duration_minutes: int
    owner: str
    objective: str
    required_decisions: List[str]
    deliverables: List[str]

class TechnicalDecisionMeeting:
    """Framework for technical decision-making meetings."""
    
    def __init__(self, decision_topic: str, technical_domains: List[str], 
                 urgency: str = "medium", complexity: str = "medium"):
        self.decision_topic = decision_topic
        self.technical_domains = technical_domains
        self.urgency = urgency
        self.complexity = complexity
        self.total_duration = self._calculate_duration()
        self.phases = self._create_phases()
        
    def _calculate_duration(self) -> int:
        """Calculate meeting duration based on complexity and urgency."""
        base_duration = 60  # minutes
        
        if self.complexity == "high":
            base_duration += 30
        if self.urgency == "high":
            base_duration += 15
        if len(self.technical_domains) > 3:
            base_duration += 20
            
        return base_duration
        
    def _create_phases(self) -> List[MeetingPhase]:
        """Create structured phases for technical decision meeting."""
        
        return [
            MeetingPhase(
                name="Problem Definition",
                duration_minutes=10,
                objectives=[
                    "Clearly define the technical problem or decision required",
                    "Establish success criteria and constraints",
                    "Identify stakeholders and their requirements"
                ],
                required_outputs=[
                    "Specific problem statement",
                    "Technical constraints and requirements",
                    "Success criteria with measurable outcomes"
                ],
                phase_prompt=f"""
                MEETING PHASE: Problem Definition
                OBJECTIVE: Define the technical problem requiring a decision
                
                As experts in {', '.join(self.technical_domains)}, you must:
                
                1. STATE THE PROBLEM PRECISELY
                   - What specific technical decision needs to be made?
                   - What are the business drivers behind this decision?
                   - What happens if we don't decide or decide incorrectly?
                
                2. DEFINE CONSTRAINTS
                   - Technical constraints (existing systems, standards, protocols)
                   - Business constraints (budget, timeline, resources)
                   - Regulatory constraints (compliance, security, privacy)
                
                3. ESTABLISH SUCCESS CRITERIA
                   - How will we measure if the decision was correct?
                   - What are the key performance indicators?
                   - What are the risk factors to avoid?
                
                EXPERT AUTHORITY: Assert your domain expertise to shape problem definition
                DEMAND SPECIFICS: Don't accept vague problem statements
                """,
                success_criteria=[
                    "All participants agree on the specific problem statement",
                    "Technical constraints are clearly documented",
                    "Success criteria are measurable and specific"
                ]
            ),
            
            MeetingPhase(
                name="Option Generation",
                duration_minutes=20,
                objectives=[
                    "Generate specific technical alternatives",
                    "Document implementation requirements for each option",
                    "Identify pros and cons based on expert knowledge"
                ],
                required_outputs=[
                    "3+ specific technical options with implementation details",
                    "Resource requirements for each option",
                    "Risk assessment for each approach"
                ],
                phase_prompt=f"""
                MEETING PHASE: Option Generation
                OBJECTIVE: Create specific, implementable technical alternatives
                
                Each expert must propose concrete options in their domain:
                
                1. TECHNICAL SPECIFICATIONS
                   - Exact technologies, frameworks, or approaches
                   - Integration requirements with existing systems
                   - Performance characteristics and scalability
                
                2. IMPLEMENTATION DETAILS
                   - Required resources (time, people, budget)
                   - Implementation timeline with milestones
                   - Dependencies and prerequisites
                
                3. RISK ANALYSIS
                   - Technical risks and mitigation strategies
                   - Implementation risks and contingencies
                   - Operational risks and support requirements
                
                EXPERT RESPONSIBILITY: Propose options in your specialty area
                CHALLENGE OTHERS: Question options that seem technically unfeasible
                BE SPECIFIC: Include exact specifications, not general concepts
                """,
                success_criteria=[
                    "Each option has specific technical implementation details",
                    "Resource requirements are realistic and detailed",
                    "Risks are identified with mitigation strategies"
                ]
            ),
            
            MeetingPhase(
                name="Expert Analysis",
                duration_minutes=20,
                objectives=[
                    "Expert evaluation of each option",
                    "Technical feasibility assessment",
                    "Cross-domain impact analysis"
                ],
                required_outputs=[
                    "Expert evaluation matrix with scores/rankings",
                    "Technical feasibility assessment for each option",
                    "Cross-domain integration analysis"
                ],
                phase_prompt=f"""
                MEETING PHASE: Expert Analysis
                OBJECTIVE: Evaluate options using domain expertise
                
                Each expert must analyze ALL options from their domain perspective:
                
                1. DOMAIN EXPERT EVALUATION
                   - Rate technical feasibility in your domain (1-10)
                   - Identify integration challenges with your systems
                   - Flag any deal-breakers or non-starters
                
                2. CROSS-DOMAIN ANALYSIS  
                   - How does each option affect other domains?
                   - What dependencies exist between domains?
                   - Where do domain requirements conflict?
                
                3. IMPLEMENTATION REALITY CHECK
                   - Are the proposed timelines realistic?
                   - Do we have the required expertise and resources?
                   - What additional capabilities would we need to develop?
                
                AUTHORITY ASSERTION: Use your expertise to guide evaluation
                OVERRIDE INCORRECT ASSESSMENTS: Correct misconceptions in your domain
                DEMAND EVIDENCE: Require proof for claims made outside your expertise
                """,
                success_criteria=[
                    "Each option evaluated by all relevant domain experts",
                    "Technical feasibility confirmed or challenged with specifics",
                    "Cross-domain impacts and dependencies identified"
                ]
            ),
            
            MeetingPhase(
                name="Decision Resolution",
                duration_minutes=15,
                objectives=[
                    "Make final decision based on expert analysis",
                    "Document decision rationale",
                    "Create implementation plan"
                ],
                required_outputs=[
                    "Final selected option with full justification",
                    "Implementation plan with timeline and ownership",
                    "Success metrics and review points"
                ],
                phase_prompt=f"""
                MEETING PHASE: Decision Resolution
                OBJECTIVE: Make final decision and create implementation plan
                
                DECISION AUTHORITY HIERARCHY:
                1. Domain experts have authority in their technical areas
                2. Senior/Executive roles make final business decisions
                3. Project managers coordinate implementation planning
                
                DECISION PROCESS:
                1. IDENTIFY THE BEST OPTION
                   - Based on expert analysis and business criteria
                   - Consider technical feasibility and resource constraints
                   - Resolve any conflicts between domain experts
                
                2. DOCUMENT DECISION RATIONALE
                   - Why was this option chosen over alternatives?
                   - What were the key deciding factors?
                   - What risks were accepted and why?
                
                3. CREATE IMPLEMENTATION PLAN
                   - Specific milestones with dates and owners
                   - Resource allocation and team assignments
                   - Success metrics and review checkpoints
                
                FORCE RESOLUTION: Don't leave without a specific decision
                ACCEPT AUTHORITY: Defer to senior experts in their domains
                COMMIT TO ACTION: Ensure everyone understands their role
                """,
                success_criteria=[
                    "Specific option selected with clear rationale",
                    "Implementation plan has owners and deadlines",
                    "Success metrics are defined and measurable"
                ]
            )
        ]

class ArchitectureReviewMeeting:
    """Framework for architecture review and design meetings."""
    
    def __init__(self, architecture_scope: str, stakeholder_groups: List[str]):
        self.architecture_scope = architecture_scope
        self.stakeholder_groups = stakeholder_groups
        self.phases = self._create_architecture_phases()
        
    def _create_architecture_phases(self) -> List[MeetingPhase]:
        """Create phases specific to architecture review."""
        
        return [
            MeetingPhase(
                name="Requirements Validation",
                duration_minutes=15,
                objectives=[
                    "Validate functional and non-functional requirements",
                    "Identify missing requirements from each stakeholder perspective",
                    "Prioritize requirements based on business impact"
                ],
                required_outputs=[
                    "Validated requirements list with priorities",
                    "Non-functional requirements (performance, security, scalability)",
                    "Stakeholder sign-off on requirements"
                ],
                phase_prompt="""
                ARCHITECTURE PHASE: Requirements Validation
                
                Each stakeholder must validate requirements from their perspective:
                - Clinical stakeholders: Workflow and safety requirements
                - Technical stakeholders: Performance and integration requirements  
                - Compliance stakeholders: Regulatory and security requirements
                - Business stakeholders: Cost and timeline requirements
                
                ASSERT YOUR DOMAIN NEEDS: Don't let requirements be watered down
                CHALLENGE UNREALISTIC REQUIREMENTS: Push back on impossible demands
                PRIORITIZE RUTHLESSLY: Not everything can be highest priority
                """,
                success_criteria=[
                    "All stakeholder groups have validated requirements",
                    "Requirements are prioritized and realistic",
                    "Conflicts between requirements are resolved"
                ]
            ),
            
            MeetingPhase(
                name="Architecture Options",
                duration_minutes=25,
                objectives=[
                    "Present alternative architectural approaches",
                    "Analyze trade-offs between approaches",
                    "Map approaches to requirements satisfaction"
                ],
                required_outputs=[
                    "2-3 distinct architectural approaches",
                    "Trade-off analysis matrix",
                    "Requirements satisfaction mapping"
                ],
                phase_prompt="""
                ARCHITECTURE PHASE: Architecture Options
                
                Technical experts must present concrete architectural alternatives:
                
                1. HIGH-LEVEL DESIGN
                   - System components and their interactions
                   - Data flow and integration patterns
                   - Technology stack and platform choices
                
                2. TRADE-OFF ANALYSIS
                   - Performance vs. complexity trade-offs
                   - Cost vs. capability trade-offs
                   - Security vs. usability trade-offs
                
                3. REQUIREMENTS MAPPING
                   - How does each approach satisfy key requirements?
                   - Where do approaches fall short of requirements?
                   - What requirements drive architectural choices?
                
                BE ARCHITECTURALLY HONEST: Don't oversell capabilities
                CHALLENGE UNREALISTIC DESIGNS: Question overly complex or simple solutions
                """,
                success_criteria=[
                    "Multiple viable architectural approaches presented",
                    "Trade-offs clearly understood by all stakeholders",
                    "Requirements satisfaction explicitly mapped"
                ]
            ),
            
            MeetingPhase(
                name="Architecture Decision",
                duration_minutes=20,
                objectives=[
                    "Select preferred architectural approach",
                    "Plan implementation phases",
                    "Define architecture governance"
                ],
                required_outputs=[
                    "Selected architecture with detailed rationale",
                    "Implementation roadmap with phases",
                    "Architecture governance and review process"
                ],
                phase_prompt="""
                ARCHITECTURE PHASE: Architecture Decision
                
                DECISION AUTHORITY:
                - Chief Architect/CTO has final architectural authority
                - Domain experts have veto power in their areas
                - Stakeholders must accept business trade-offs
                
                IMPLEMENTATION PLANNING:
                1. Phase the implementation to reduce risk
                2. Define clear deliverables for each phase
                3. Establish architecture review checkpoints
                4. Plan for evolutionary architecture changes
                
                GOVERNANCE STRUCTURE:
                - Who approves architectural changes?
                - How are architectural standards enforced?
                - What review processes ensure compliance?
                
                MAKE THE CALL: Senior architect decides, others commit
                PLAN FOR REALITY: Implementation must be realistic and phased
                """,
                success_criteria=[
                    "Architecture selected with stakeholder buy-in",
                    "Implementation plan is realistic and phased",
                    "Governance process established for ongoing decisions"
                ]
            )
        ]

class ProblemSolvingMeeting:
    """Framework for complex problem-solving sessions."""
    
    def __init__(self, problem_domain: str, problem_complexity: str, 
                 time_constraint: str):
        self.problem_domain = problem_domain
        self.problem_complexity = problem_complexity
        self.time_constraint = time_constraint
        self.phases = self._create_problem_solving_phases()
        
    def _create_problem_solving_phases(self) -> List[MeetingPhase]:
        """Create phases for structured problem solving."""
        
        return [
            MeetingPhase(
                name="Problem Analysis", 
                duration_minutes=15,
                objectives=[
                    "Root cause analysis of the problem",
                    "Impact assessment and urgency evaluation",
                    "Constraint identification"
                ],
                required_outputs=[
                    "Root cause analysis with evidence",
                    "Impact assessment with metrics", 
                    "Constraint documentation"
                ],
                phase_prompt="""
                PROBLEM SOLVING PHASE: Problem Analysis
                
                Systematically analyze the problem using your expertise:
                
                1. ROOT CAUSE ANALYSIS
                   - What is the fundamental cause of this problem?
                   - What evidence supports your root cause hypothesis?
                   - What other potential causes have been ruled out?
                
                2. IMPACT ASSESSMENT
                   - What are the business/technical/user impacts?
                   - How urgent is resolution (hours, days, weeks)?
                   - What happens if the problem isn't solved?
                
                3. CONSTRAINT IDENTIFICATION
                   - What limits our solution options?
                   - What resources/capabilities do we have available?
                   - What must we preserve while solving the problem?
                
                USE YOUR EXPERTISE: Bring domain-specific analysis to bear
                CHALLENGE ASSUMPTIONS: Question stated causes and impacts
                BE EVIDENCE-BASED: Support analysis with data and facts
                """,
                success_criteria=[
                    "Root cause identified with supporting evidence",
                    "Impact quantified with specific metrics",
                    "Solution constraints clearly understood"
                ]
            ),
            
            MeetingPhase(
                name="Solution Generation",
                duration_minutes=20,
                objectives=[
                    "Generate multiple solution approaches", 
                    "Evaluate solution feasibility and impact",
                    "Identify quick wins vs. long-term solutions"
                ],
                required_outputs=[
                    "Multiple solution options with implementation details",
                    "Feasibility assessment for each solution",
                    "Short-term vs. long-term solution classification"
                ],
                phase_prompt="""
                PROBLEM SOLVING PHASE: Solution Generation
                
                Generate concrete solutions using your domain expertise:
                
                1. SOLUTION BRAINSTORMING
                   - Generate multiple approaches from your domain perspective
                   - Consider both immediate fixes and long-term solutions
                   - Think beyond obvious solutions to innovative approaches
                
                2. FEASIBILITY ANALYSIS
                   - Can each solution actually be implemented?
                   - What resources and timeline would be required?
                   - What risks does each solution introduce?
                
                3. IMPACT PREDICTION
                   - How effectively does each solution address the root cause?
                   - What side effects or unintended consequences might occur?
                   - How do solutions interact with existing systems/processes?
                
                LEVERAGE YOUR EXPERTISE: Propose solutions others might miss
                BE REALISTIC: Don't propose solutions that can't be implemented
                CONSIDER DEPENDENCIES: Account for how solutions affect other areas
                """,
                success_criteria=[
                    "Multiple feasible solutions identified",
                    "Solutions mapped to impact on root causes",
                    "Implementation feasibility assessed realistically"
                ]
            ),
            
            MeetingPhase(
                name="Solution Selection and Planning",
                duration_minutes=15,
                objectives=[
                    "Select optimal solution approach",
                    "Create detailed implementation plan",
                    "Establish success metrics and monitoring"
                ],
                required_outputs=[
                    "Selected solution with implementation plan",
                    "Success metrics and monitoring approach",
                    "Risk mitigation and contingency plans"
                ],
                phase_prompt="""
                PROBLEM SOLVING PHASE: Solution Selection and Planning
                
                Make decisions and create actionable implementation plans:
                
                1. SOLUTION SELECTION
                   - Choose the optimal solution based on analysis
                   - Consider resource constraints and urgency
                   - Balance immediate needs with long-term sustainability
                
                2. IMPLEMENTATION PLANNING
                   - Define specific implementation steps with owners
                   - Set realistic timelines with milestones
                   - Identify required resources and dependencies
                
                3. SUCCESS MONITORING
                   - Define metrics to measure solution effectiveness
                   - Establish monitoring and review processes
                   - Plan for iterative improvement and adjustment
                
                MAKE THE DECISION: Don't leave without a chosen solution
                PLAN REALISTICALLY: Ensure implementation is actually feasible  
                MONITOR OUTCOMES: Plan how to measure success and adjust course
                """,
                success_criteria=[
                    "Solution selected with clear rationale",
                    "Implementation plan has specific steps and owners",
                    "Success metrics defined with monitoring approach"
                ]
            )
        ]

class MeetingFrameworkFactory:
    """Factory for creating appropriate meeting frameworks based on meeting type."""
    
    @staticmethod
    def create_meeting_framework(meeting_type: str, context: Dict[str, Any]) -> Any:
        """Create appropriate meeting framework based on type and context."""
        
        if meeting_type == "technical_decision":
            return TechnicalDecisionMeeting(
                decision_topic=context.get("decision_topic", "Technical Decision"),
                technical_domains=context.get("technical_domains", ["general"]),
                urgency=context.get("urgency", "medium"),
                complexity=context.get("complexity", "medium")
            )
            
        elif meeting_type == "architecture_review":
            return ArchitectureReviewMeeting(
                architecture_scope=context.get("architecture_scope", "System Architecture"),
                stakeholder_groups=context.get("stakeholder_groups", ["technical", "business"])
            )
            
        elif meeting_type == "problem_solving":
            return ProblemSolvingMeeting(
                problem_domain=context.get("problem_domain", "General"),
                problem_complexity=context.get("problem_complexity", "medium"),
                time_constraint=context.get("time_constraint", "normal")
            )
            
        else:
            # Default to technical decision framework
            return TechnicalDecisionMeeting(
                decision_topic="General Business Decision",
                technical_domains=["general"],
                urgency="medium",
                complexity="medium"
            )