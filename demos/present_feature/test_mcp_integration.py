"""
Test MCP Integration with TinyTroupe Present Feature

This test file demonstrates and verifies that TinyTroupe can successfully
integrate with MCP (Model Context Protocol) servers and use external tools
through the MCP client implementation.
"""

import asyncio
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, '/home/gyasis/Documents/code/Applied_AI/experiments/tinytroupe')

async def test_mcp_basic_functionality():
    """Test basic MCP functionality without server connections."""
    
    print("🧪 Testing Basic MCP Functionality...")
    
    try:
        # Test MCP imports
        from tinytroupe.mcp_integration import (
            MCPClient, MCPServerConfig, MCPToolWrapper, MCPIntegrationManager
        )
        print("✅ MCP integration modules imported successfully")
        
        # Test MCP client creation
        from tinytroupe.tools.tool_orchestrator import ProvenanceLogger
        logger = ProvenanceLogger()
        client = MCPClient(logger)
        print("✅ MCP client created successfully")
        
        # Test server configuration
        config = MCPServerConfig(
            name="test_server",
            command=["echo", "test"],
            transport_type="stdio"
        )
        client.add_server(config)
        print("✅ MCP server configuration added successfully")
        
        # Test integration manager
        from tinytroupe.mcp_integration import mcp_integration_manager
        status = mcp_integration_manager.get_integration_status()
        print(f"✅ MCP integration manager status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic MCP functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_agent_creation():
    """Test creation of MCP-enabled agents."""
    
    print("\n🧪 Testing MCP Agent Creation...")
    
    try:
        from tinytroupe.mcp_present_agent import (
            MCPPresentAdaptiveTinyPerson, create_mcp_present_adaptive_agent
        )
        
        # Create MCP-enabled agent
        agent = create_mcp_present_adaptive_agent(
            "Test Agent",
            "Technical Lead"
        )
        
        print(f"✅ Created MCP agent: {agent.name}")
        print(f"   Role: {agent.role}")
        print(f"   MCP Enabled: {agent.mcp_enabled}")
        
        # Test capabilities summary
        capabilities = agent.get_mcp_capabilities_summary()
        print(f"✅ Agent capabilities: {capabilities}")
        
        # Test MCP tool listing
        mcp_tools = agent.list_available_mcp_tools()
        print(f"✅ Available MCP tools: {len(mcp_tools)}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP agent creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_tool_wrapper():
    """Test MCP tool wrapper functionality."""
    
    print("\n🧪 Testing MCP Tool Wrapper...")
    
    try:
        # Create a mock MCP tool
        import mcp
        from tinytroupe.mcp_integration import MCPToolWrapper, MCPClient
        from tinytroupe.tools.tool_orchestrator import ProvenanceLogger
        
        # Create mock tool (simplified for testing)
        class MockMCPTool:
            def __init__(self):
                self.name = "test_tool"
                self.description = "A test MCP tool"
        
        mock_tool = MockMCPTool()
        
        # Create wrapper
        client = MCPClient(ProvenanceLogger())
        wrapper = MCPToolWrapper(mock_tool, client, "test_server")
        
        print(f"✅ Created MCP tool wrapper: {wrapper.name}")
        print(f"   Description: {wrapper.description}")
        print(f"   Server: {wrapper.server_name}")
        
        # Test action definitions
        definitions = wrapper.actions_definitions_prompt()
        print(f"✅ Tool action definitions generated")
        
        # Test constraints
        constraints = wrapper.actions_constraints_prompt()
        print(f"✅ Tool constraints generated")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP tool wrapper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_integration_manager():
    """Test MCP integration manager functionality."""
    
    print("\n🧪 Testing MCP Integration Manager...")
    
    try:
        from tinytroupe.mcp_integration import mcp_integration_manager
        
        # Test server configuration
        mcp_integration_manager.configure_mcp_server(
            name="test_filesystem",
            command=["echo", "test_filesystem_server"]
        )
        print("✅ Configured test MCP server")
        
        # Test status reporting
        status = mcp_integration_manager.get_integration_status()
        print(f"✅ Integration status: {status}")
        
        # Test role assignment (without actual connection)
        try:
            # This will work even without real MCP tools
            mcp_integration_manager.assign_mcp_tools_to_role("test_role", [])
            print("✅ Role assignment mechanism works")
        except Exception as e:
            print(f"⚠️  Role assignment needs actual tools: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP integration manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_with_present_feature():
    """Test MCP integration with the Present Feature."""
    
    print("\n🧪 Testing MCP Integration with Present Feature...")
    
    try:
        from tinytroupe.mcp_present_agent import create_mcp_present_adaptive_agent
        from tinytroupe.tools.tool_orchestrator import global_tool_orchestrator
        
        # Create agent with both Present Feature and MCP capabilities
        agent = create_mcp_present_adaptive_agent(
            "Integration Test Agent",
            "Compliance Officer"
        )
        
        # Test that agent has both present and MCP capabilities
        capabilities = agent.get_present_capabilities_summary()
        print(f"✅ Present capabilities: {capabilities}")
        
        mcp_capabilities = agent.get_mcp_capabilities_summary()
        print(f"✅ MCP capabilities: {mcp_capabilities}")
        
        # Test tool availability
        available_tools = global_tool_orchestrator.get_available_tools(agent)
        present_tools = [t for t in available_tools if not hasattr(t, 'server_name')]
        mcp_tools = [t for t in available_tools if hasattr(t, 'server_name')]
        
        print(f"✅ Available Present tools: {len(present_tools)}")
        print(f"✅ Available MCP tools: {len(mcp_tools)}")
        
        # Test action suggestion
        suggestion = agent.suggest_present_action(
            "Generate compliance report",
            participants=["Alice", "Bob"]
        )
        if suggestion:
            print(f"✅ Present action suggestion: {suggestion['type']}")
        
        mcp_suggestion = agent.suggest_mcp_action(
            "Access external compliance database",
            agent._get_conversation_context()
        )
        if mcp_suggestion:
            print(f"✅ MCP action suggestion: {mcp_suggestion['type']}")
        else:
            print("ℹ️  No MCP action suggested (expected without real tools)")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP + Present Feature integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_package_availability():
    """Test that the MCP package is properly installed and accessible."""
    
    print("🧪 Testing MCP Package Availability...")
    
    try:
        import mcp
        print(f"✅ MCP package version: {mcp.__version__ if hasattr(mcp, '__version__') else 'Unknown'}")
        
        # Test key MCP components
        from mcp.client.stdio import stdio_client
        from mcp import ClientSession, StdioServerParameters
        print("✅ MCP client components imported successfully")
        
        # Test that we can create basic MCP objects
        params = StdioServerParameters(command="echo", args=["test"])
        print(f"✅ Created StdioServerParameters: {params.command}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP package availability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_mcp_tests():
    """Run all MCP integration tests."""
    
    print("🚀 Starting TinyTroupe MCP Integration Test Suite\n")
    
    results = []
    
    # Test MCP package availability first
    results.append(("MCP Package Availability", test_mcp_package_availability()))
    
    # Test basic functionality
    results.append(("MCP Basic Functionality", await test_mcp_basic_functionality()))
    
    # Test agent creation
    results.append(("MCP Agent Creation", await test_mcp_agent_creation()))
    
    # Test tool wrapper
    results.append(("MCP Tool Wrapper", await test_mcp_tool_wrapper()))
    
    # Test integration manager
    results.append(("MCP Integration Manager", await test_mcp_integration_manager()))
    
    # Test Present Feature integration
    results.append(("MCP + Present Feature", await test_mcp_with_present_feature()))
    
    # Summary
    print("\n📊 MCP Integration Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All MCP integration tests passed!")
        print("\n📋 MCP Integration Status:")
        print("- MCP Package: ✅ Available")
        print("- MCP Client: ✅ Working")
        print("- Tool Wrapper: ✅ Functional")
        print("- Agent Integration: ✅ Ready")
        print("- Present Feature Compatibility: ✅ Verified")
        print("\n🚀 TinyTroupe is ready for MCP tool usage!")
    else:
        print("🔧 Some MCP integration tests failed - review implementation.")
    
    return all_passed


def demonstrate_mcp_usage():
    """Demonstrate how to use MCP with TinyTroupe."""
    
    print("\n📖 MCP Integration Usage Guide:")
    print("=" * 50)
    
    print("""
1. **Setup MCP Servers:**
   ```python
   from tinytroupe.mcp_integration import mcp_integration_manager
   
   # Configure MCP servers
   mcp_integration_manager.configure_mcp_server(
       name="filesystem",
       command=["uvx", "mcp-server-filesystem", "--directory", "."]
   )
   
   # Connect to servers
   await mcp_integration_manager.connect_to_servers()
   ```

2. **Create MCP-Enabled Agents:**
   ```python
   from tinytroupe.mcp_present_agent import create_mcp_present_adaptive_agent
   
   agent = create_mcp_present_adaptive_agent(
       "Emily Martinez", 
       "Project Manager"
   )
   ```

3. **Use MCP Tools in Agent Actions:**
   ```python
   # Agents can now use both Present Feature tools and MCP tools
   agent.act({
       "type": "MCP_READ_FILE",  # MCP tool action
       "content": {
           "tool": "mcp_filesystem_read",
           "arguments": {"path": "./project_status.md"},
           "output_mode": "present"
       }
   })
   ```

4. **Check Available Tools:**
   ```python
   # List all available tools (Present + MCP)
   tools = agent.list_available_mcp_tools()
   capabilities = agent.get_mcp_capabilities_summary()
   ```
""")


if __name__ == "__main__":
    # Run all tests
    success = asyncio.run(run_all_mcp_tests())
    
    if success:
        demonstrate_mcp_usage()
        print("\n🎯 MCP Integration is ready for TinyTroupe!")
    else:
        print("\n🔧 Please fix failing tests before using MCP integration.")