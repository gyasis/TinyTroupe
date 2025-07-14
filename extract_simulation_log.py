#!/usr/bin/env python3
"""
Extract Simulation Log from TinyTroupe Cache
============================================

This script extracts and formats the complete conversation log
from a TinyTroupe simulation cache file.
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any

def extract_agent_conversations(cache_data: Dict) -> List[Dict]:
    """Extract all conversations from the cache data."""
    conversations = []
    
    # Look for agents in the cache
    if 'agents' not in cache_data:
        print("No agents found in cache data")
        return conversations
    
    for agent_data in cache_data['agents']:
        agent_name = agent_data.get('name', 'Unknown Agent')
        
        # Extract episodic memory (conversations)
        if '_episodic_memory' in agent_data:
            episodic_memory = agent_data['_episodic_memory']
            
            if '_memories' in episodic_memory:
                memories = episodic_memory['_memories']
                
                for memory in memories:
                    if 'content' in memory:
                        content = memory['content']
                        timestamp = memory.get('timestamp', 'Unknown time')
                        
                        conversations.append({
                            'agent': agent_name,
                            'timestamp': timestamp,
                            'content': content,
                            'type': 'episodic_memory'
                        })
        
        # Extract action history
        if '_actions_and_results' in agent_data:
            actions = agent_data['_actions_and_results']
            
            for action_result in actions:
                if 'action' in action_result:
                    action = action_result['action']
                    result = action_result.get('result', '')
                    
                    conversations.append({
                        'agent': agent_name,
                        'timestamp': 'Action',
                        'content': f"ACTION: {action}",
                        'result': result,
                        'type': 'action'
                    })
    
    return conversations

def extract_environment_events(cache_data: Dict) -> List[Dict]:
    """Extract environment events from the cache data."""
    events = []
    
    # Look for environments
    if 'environments' not in cache_data:
        return events
    
    for env_data in cache_data['environments']:
        env_name = env_data.get('name', 'Unknown Environment')
        
        # Extract environment history
        if '_displayed_communications' in env_data:
            communications = env_data['_displayed_communications']
            
            for comm in communications:
                events.append({
                    'environment': env_name,
                    'content': comm,
                    'type': 'communication'
                })
    
    return events

def format_conversation_log(conversations: List[Dict], events: List[Dict]) -> str:
    """Format the extracted data into a readable log."""
    
    log_lines = []
    log_lines.append("=" * 80)
    log_lines.append("TINYTROUPE SIMULATION LOG EXTRACT")
    log_lines.append("=" * 80)
    log_lines.append(f"Extracted on: {datetime.now().isoformat()}")
    log_lines.append(f"Total conversations: {len(conversations)}")
    log_lines.append(f"Total environment events: {len(events)}")
    log_lines.append("=" * 80)
    
    # Group by agent
    agents = {}
    for conv in conversations:
        agent = conv['agent']
        if agent not in agents:
            agents[agent] = []
        agents[agent].append(conv)
    
    log_lines.append("\n🎭 AGENT CONVERSATIONS AND ACTIONS")
    log_lines.append("-" * 80)
    
    for agent_name, agent_convs in agents.items():
        log_lines.append(f"\n👤 {agent_name}")
        log_lines.append("-" * 40)
        
        for conv in agent_convs:
            if conv['type'] == 'episodic_memory':
                log_lines.append(f"[{conv['timestamp']}] MEMORY: {conv['content']}")
            elif conv['type'] == 'action':
                log_lines.append(f"[ACTION] {conv['content']}")
                if 'result' in conv and conv['result']:
                    log_lines.append(f"         RESULT: {conv['result']}")
            log_lines.append("")
    
    # Environment events
    if events:
        log_lines.append("\n🌍 ENVIRONMENT EVENTS")
        log_lines.append("-" * 80)
        
        for event in events:
            log_lines.append(f"[{event['environment']}] {event['content']}")
            log_lines.append("")
    
    log_lines.append("=" * 80)
    log_lines.append("END OF SIMULATION LOG")
    log_lines.append("=" * 80)
    
    return "\n".join(log_lines)

def main():
    """Main function to extract and save the log."""
    
    if len(sys.argv) != 2:
        print("Usage: python extract_simulation_log.py <cache_file.json>")
        print("\nAvailable cache files:")
        import os
        cache_files = [f for f in os.listdir('.') if f.endswith('.cache.json')]
        for f in cache_files:
            print(f"  - {f}")
        sys.exit(1)
    
    cache_file = sys.argv[1]
    
    try:
        print(f"Loading cache file: {cache_file}")
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        print("Extracting conversations...")
        conversations = extract_agent_conversations(cache_data)
        
        print("Extracting environment events...")
        events = extract_environment_events(cache_data)
        
        print("Formatting log...")
        log_content = format_conversation_log(conversations, events)
        
        # Save to log file
        log_filename = cache_file.replace('.cache.json', '_full_log.txt')
        with open(log_filename, 'w') as f:
            f.write(log_content)
        
        print(f"✅ Full simulation log saved to: {log_filename}")
        print(f"📊 Extracted {len(conversations)} conversations and {len(events)} environment events")
        
        # Also show a preview
        print("\n" + "="*40)
        print("PREVIEW (first 10 lines):")
        print("="*40)
        lines = log_content.split('\n')
        for line in lines[:10]:
            print(line)
        print("...")
        print(f"(Full log contains {len(lines)} lines)")
        
    except FileNotFoundError:
        print(f"❌ Cache file not found: {cache_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()