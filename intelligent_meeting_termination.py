#!/usr/bin/env python3
"""
Intelligent Meeting Termination for TinyTroupe
Extends TinyWorld with early termination capabilities to detect repetitive conversations.
"""

import sys
sys.path.append('..')
from tinytroupe.environment import TinyWorld
from tinytroupe.agent import TinyPerson
from datetime import timedelta
import logging

logger = logging.getLogger("tinytroupe")

class IntelligentTinyWorld(TinyWorld):
    """
    Enhanced TinyWorld with intelligent meeting termination capabilities.
    Detects when conversations become repetitive and terminates early.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.terminated_early = False
        self.termination_reason = None
        
    def run_adaptive(self, steps: int, 
                    timedelta_per_step=None, 
                    return_actions=False,
                    early_termination=True,
                    repetition_threshold=3,
                    similarity_threshold=0.7,
                    all_done_threshold=2,
                    verbose=True):
        """
        Runs the environment with intelligent early termination.
        
        Args:
            steps (int): Maximum number of steps to run
            early_termination (bool): Enable early termination detection
            repetition_threshold (int): Consecutive rounds of similar messages to trigger termination
            similarity_threshold (float): Similarity score threshold (0.0-1.0)
            all_done_threshold (int): Rounds where all agents only do DONE to trigger termination
            verbose (bool): Print termination messages
        """
        if verbose:
            print(f"🚀 Starting adaptive meeting simulation (max {steps} rounds)")
            print(f"📊 Early termination: {early_termination}")
            if early_termination:
                print(f"   - Repetition threshold: {repetition_threshold} rounds")
                print(f"   - Similarity threshold: {similarity_threshold}")
                print(f"   - All-done threshold: {all_done_threshold} rounds")
        
        agents_actions_over_time = []
        previous_messages = []  # Store messages from recent rounds
        consecutive_done_rounds = 0
        
        for i in range(steps):
            current_round = i + 1
            
            if TinyWorld.communication_display:
                self._display_communication(cur_step=current_round, total_steps=steps, 
                                           kind='step', timedelta_per_step=timedelta_per_step)
            
            # Execute the simulation step
            agents_actions = self._step(timedelta_per_step=timedelta_per_step, 
                                      current_round=current_round, total_rounds=steps)
            agents_actions_over_time.append(agents_actions)
            
            # Early termination checks
            if early_termination and current_round >= 2:  # Need at least 2 rounds for comparison
                
                # Check 1: All agents only doing DONE actions
                done_count = self._count_done_actions(agents_actions)
                if done_count == len(self.agents):
                    consecutive_done_rounds += 1
                    if consecutive_done_rounds >= all_done_threshold:
                        self.terminated_early = True
                        self.termination_reason = f"All agents inactive for {consecutive_done_rounds} consecutive rounds"
                        if verbose:
                            print(f"✅ Early termination: {self.termination_reason}")
                        break
                else:
                    consecutive_done_rounds = 0
                
                # Check 2: Repetitive conversation detection
                current_messages = self._extract_talk_messages(agents_actions)
                if current_messages:  # Only check if there are actual messages
                    previous_messages.append(current_messages)
                    
                    # Keep only recent rounds for comparison
                    if len(previous_messages) > repetition_threshold:
                        previous_messages.pop(0)
                    
                    # Check for repetitive patterns
                    if len(previous_messages) >= repetition_threshold:
                        avg_similarity = self._calculate_conversation_similarity(previous_messages)
                        if avg_similarity > similarity_threshold:
                            self.terminated_early = True
                            self.termination_reason = f"Repetitive conversation detected (similarity: {avg_similarity:.2f})"
                            if verbose:
                                print(f"🔄 Early termination: {self.termination_reason}")
                            break
        
        if verbose:
            if self.terminated_early:
                print(f"🏁 Meeting terminated early after {current_round} rounds")
                print(f"💡 Reason: {self.termination_reason}")
            else:
                print(f"⏰ Meeting completed full {steps} rounds")
        
        if return_actions:
            return agents_actions_over_time
    
    def _count_done_actions(self, agents_actions):
        """Count how many agents only performed DONE actions this round."""
        done_count = 0
        for agent_name, actions in agents_actions.items():
            if len(actions) == 1 and actions[0].get('type') == 'DONE':
                done_count += 1
        return done_count
    
    def _extract_talk_messages(self, agents_actions):
        """Extract TALK action content from all agents this round."""
        messages = []
        for agent_name, actions in agents_actions.items():
            for action in actions:
                if action.get('type') == 'TALK' and 'content' in action:
                    messages.append(action['content'])
        return messages
    
    def _calculate_conversation_similarity(self, message_rounds):
        """
        Calculate average similarity across recent conversation rounds.
        Uses Jaccard similarity for efficiency.
        """
        if len(message_rounds) < 2:
            return 0.0
        
        similarities = []
        latest_round = message_rounds[-1]
        
        # Compare latest round with each previous round
        for prev_round in message_rounds[:-1]:
            round_similarity = self._calculate_round_similarity(latest_round, prev_round)
            similarities.append(round_similarity)
        
        return sum(similarities) / len(similarities)
    
    def _calculate_round_similarity(self, messages1, messages2):
        """Calculate similarity between two rounds of messages."""
        if not messages1 or not messages2:
            return 0.0
        
        # Combine all messages in each round
        combined1 = " ".join(messages1)
        combined2 = " ".join(messages2)
        
        return self._jaccard_similarity(combined1, combined2)
    
    def _jaccard_similarity(self, text1, text2):
        """
        Calculate Jaccard similarity between two text strings.
        Simple but effective for detecting repetitive phrases.
        """
        # Tokenize and normalize
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        # Remove common stopwords to improve accuracy
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                    'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
                    'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                    'would', 'could', 'should', 'i', 'you', 'he', 'she', 'it', 
                    'we', 'they', 'this', 'that', 'these', 'those'}
        
        tokens1 = tokens1 - stopwords
        tokens2 = tokens2 - stopwords
        
        if not tokens1 and not tokens2:
            return 1.0  # Both empty after stopword removal
        if not tokens1 or not tokens2:
            return 0.0  # One empty, one not
        
        # Calculate Jaccard index
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0

# Example usage and testing
if __name__ == "__main__":
    print("=== INTELLIGENT MEETING TERMINATION DEMO ===")
    
    # Import adaptive agent for testing
    from tinytroupe.adaptive_agent import create_adaptive_agent
    
    # Create test agents
    facilitator = create_adaptive_agent(
        name="Emily Martinez",
        occupation="Project Manager",
        personality_traits=["Organized", "Facilitator"]
    )
    
    participant = TinyPerson("Alex Chen")
    participant.define("occupation", "Developer")
    
    # Create intelligent world
    world = IntelligentTinyWorld("Test Meeting", is_meeting=True)
    world.add_agents([facilitator, participant])
    world.make_everyone_accessible()
    
    # Test early termination
    facilitator.listen("Let's discuss our project status.")
    
    print("\n--- Testing Adaptive Termination ---")
    world.run_adaptive(
        steps=15,  # Max 15 rounds
        early_termination=True,
        repetition_threshold=2,
        similarity_threshold=0.6,
        verbose=True
    )
    
    print(f"\n✅ Terminated early: {world.terminated_early}")
    if world.terminated_early:
        print(f"📝 Reason: {world.termination_reason}")
    
    print("\n=== DEMO COMPLETE ===")