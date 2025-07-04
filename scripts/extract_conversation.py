#!/usr/bin/env python3
"""
Simple conversation extractor for TinyTroupe
Extracts just the talking points without formatting
"""

def extract_clean_conversation(world):
    """Extract clean conversation transcript showing just who said what."""
    
    conversations = []
    
    for agent in world.agents:
        interactions = agent.pretty_current_interactions(max_content_length=None)
        lines = interactions.split('\n')
        
        for i, line in enumerate(lines):
            if '[TALK]' in line and 'acts:' in line:
                # Extract speaker
                parts = line.split(' acts:')
                if len(parts) >= 2:
                    speaker_part = parts[0]
                    # Extract name from the line
                    if ']' in speaker_part:
                        speaker = speaker_part.split(']')[-1].strip()
                    else:
                        speaker = speaker_part.strip()
                    
                    # Get message content
                    message_lines = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith('>'):
                        content = lines[j].strip()[1:].strip()
                        if content:
                            message_lines.append(content)
                        j += 1
                    
                    if message_lines:
                        full_message = ' '.join(message_lines)
                        # Add timestamp if available
                        timestamp = None
                        for k in range(max(0, i-5), i):
                            if 'Date and time' in lines[k]:
                                timestamp = lines[k].split('Date and time of events:')[1].strip()
                                break
                        
                        conversations.append({
                            'speaker': speaker,
                            'message': full_message,
                            'timestamp': timestamp
                        })
    
    return conversations


def print_clean_transcript(world):
    """Print a clean, readable transcript of the conversation."""
    
    print("\n" + "="*60)
    print("CLEAN MEETING TRANSCRIPT")
    print("="*60)
    
    conversations = extract_clean_conversation(world)
    
    # Sort by timestamp if available
    if conversations and conversations[0].get('timestamp'):
        conversations.sort(key=lambda x: x['timestamp'] or '')
    
    for i, conv in enumerate(conversations, 1):
        print(f"\n{i}. {conv['speaker']}:")
        print(f"   {conv['message']}")
        if conv.get('timestamp'):
            print(f"   ({conv['timestamp']})")


def extract_decisions_and_actions(world):
    """Extract key decisions and action items from the conversation."""
    
    from tinytroupe.extraction import default_extractor
    import json
    
    try:
        summary = default_extractor.extract_results_from_world(
            world,
            extraction_objective="Extract key decisions made and action items assigned",
            fields=["decisions", "action_items", "next_steps"],
            fields_hints={
                "decisions": "Specific technical or business decisions made",
                "action_items": "Tasks assigned with owner and deadline",
                "next_steps": "Follow-up actions or meetings planned"
            }
        )
        
        print("\n" + "="*60)
        print("MEETING OUTCOMES")
        print("="*60)
        print(json.dumps(summary, indent=2))
        
    except Exception as e:
        print(f"Could not extract summary: {e}")


# Example usage:
if __name__ == "__main__":
    # This would be used after running a simulation
    # from tinytroupe.environment import TinyWorld
    # world = ... # your world after simulation
    # print_clean_transcript(world)
    # extract_decisions_and_actions(world)
    print("Import this module and use:")
    print("  - extract_clean_conversation(world) for raw data")
    print("  - print_clean_transcript(world) for formatted output") 
    print("  - extract_decisions_and_actions(world) for summary")