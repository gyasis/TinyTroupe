# TinyTroupe Demos

This directory contains demonstration scripts and examples for TinyTroupe features.

## Directory Structure

### `/showcases`
Complete business simulation showcases demonstrating multi-day scenarios:
- `basic_3day_showcase.py` - Core features only, stable implementation
- `simple_3day_showcase.py` - Simple business simulation with Present Feature
- `comprehensive_3day_simulation.py` - Full-featured simulation with all capabilities
- `extract_simulation_log.py` - Utility to extract and organize simulation logs

### `/business_meetings`
Examples of business meeting simulations with adaptive agents:
- `business_meeting_agents.py` - Pre-configured business meeting agents
- `business_meeting_environment.py` - Meeting environment setup
- `demo_clean_output.py` - Clean output formatting demonstration
- `demo_extraction_paradigm.py` - Results extraction pattern demo
- `intelligent_meeting_termination.py` - Smart meeting conclusion logic
- Various meeting framework examples

### `/present_feature`
Demonstrations of the Present Feature for document generation:
- `test_mcp_integration.py` - MCP (Model Context Protocol) integration demo
- `simple_present_test.py` - Basic Present Feature usage

## Running Demos

All demos can be run directly:

```bash
# Run a showcase
python demos/showcases/basic_3day_showcase.py

# Run a business meeting demo
python demos/business_meetings/demo_clean_output.py

# Test Present Feature
python demos/present_feature/test_mcp_integration.py
```

## Requirements

- Configured TinyTroupe installation
- Valid API keys in environment or config.ini
- Python 3.10+

See individual demo files for specific requirements and usage instructions.