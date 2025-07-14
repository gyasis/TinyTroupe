"""
MCP-Enhanced Present Adaptive Agent for TinyTroupe

This module extends the PresentAdaptiveTinyPerson with MCP (Model Context Protocol)
capabilities, enabling agents to use external MCP tools in addition to built-in
Present Feature tools.
"""

import asyncio
from typing import Dict, List, Any, Optional

from tinytroupe.present_adaptive_agent import PresentAdaptiveTinyPerson
from tinytroupe.mcp_integration import mcp_integration_manager, MCPToolWrapper
from tinytroupe.context_detection import ContextType
from tinytroupe.tools.tool_orchestrator import global_tool_orchestrator
from tinytroupe.tools import logger


class MCPPresentAdaptiveTinyPerson(PresentAdaptiveTinyPerson):
    """
    Enhanced PresentAdaptiveTinyPerson with MCP tool capabilities.
    
    This agent can use both built-in Present Feature tools and external MCP tools,
    providing access to a much broader ecosystem of capabilities while maintaining
    the context-aware behavior and document generation features of the Present Feature.
    """
    
    def __init__(self, name: str = "A Person", **kwargs):
        super().__init__(name, **kwargs)
        
        # Track MCP-specific capabilities
        self.mcp_tools_used = []
        self.mcp_enabled = True
        
        # Initialize MCP tool access
        self._assign_mcp_tools()
    
    def _assign_mcp_tools(self):
        """Assign appropriate MCP tools based on agent role."""
        
        if not self.mcp_enabled:
            return
        
        try:
            # Get MCP tools appropriate for this agent's role
            mcp_integration_manager.assign_mcp_tools_to_role(self.role)
            
            # Set permissions for MCP tools
            mcp_tools = mcp_integration_manager.get_mcp_tools_for_role(self.role)
            
            for tool in mcp_tools:
                # Grant appropriate permissions based on role
                permission_level = self._get_mcp_permission_level(tool)
                global_tool_orchestrator.permission_manager.set_role_permission(
                    self.role, tool.name, permission_level
                )
            
            logger.info(f"Assigned {len(mcp_tools)} MCP tools to {self.name} ({self.role})")
            
        except Exception as e:
            logger.error(f"Failed to assign MCP tools to {self.name}: {e}")
    
    def _get_mcp_permission_level(self, tool: MCPToolWrapper) -> str:
        """Determine appropriate permission level for an MCP tool based on role and tool type."""
        
        # Default permission levels by role
        role_permissions = {
            "compliance_officer": "admin",  # Compliance officers need full access
            "technical_lead": "admin",      # Technical leads need full access
            "project_manager": "write",     # Project managers need write access
            "data_specialist": "write",     # Data specialists need write access
            "team_member": "read"          # Team members get read access
        }
        
        base_permission = role_permissions.get(self.role, "read")
        
        # Adjust based on tool characteristics
        tool_desc = tool.description.lower()
        
        # Be more restrictive with potentially dangerous operations
        if any(word in tool_desc for word in ["delete", "remove", "destroy", "terminate"]):
            if base_permission == "admin":
                return "admin"  # Only admins can use destructive tools
            else:
                return "none"   # Others cannot use destructive tools
        
        # Be more permissive with read-only operations
        if any(word in tool_desc for word in ["read", "get", "list", "show", "display"]):
            return "read"  # Everyone can use read-only tools
        
        return base_permission
    
    def _enhance_configuration_for_context(self, context: ContextType) -> Dict[str, Any]:
        """Enhanced configuration that includes MCP tool guidance."""
        
        # Get base adaptive configuration
        enhanced_config = super()._enhance_configuration_for_context(context)
        
        # Add MCP tool information
        if self.mcp_enabled:
            mcp_tools = mcp_integration_manager.get_mcp_tools_for_role(self.role)
            
            enhanced_config["mcp_capabilities"] = {
                "mcp_enabled": True,
                "available_mcp_tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "server": tool.server_name
                    }
                    for tool in mcp_tools
                ],
                "mcp_tool_count": len(mcp_tools)
            }
            
            # Add MCP-specific guidance
            enhanced_config["mcp_guidance"] = self._get_mcp_guidance_for_context(context, mcp_tools)
        else:
            enhanced_config["mcp_capabilities"] = {"mcp_enabled": False}
        
        return enhanced_config
    
    def _get_mcp_guidance_for_context(self, context: ContextType, mcp_tools: List[MCPToolWrapper]) -> str:
        """Get MCP-specific guidance based on context and available tools."""
        
        if not mcp_tools:
            return "No MCP tools are currently available for your role."
        
        guidance = f"You have access to {len(mcp_tools)} external MCP tools that can help you accomplish tasks:\n\n"
        
        # Group tools by server
        tools_by_server = {}
        for tool in mcp_tools:
            if tool.server_name not in tools_by_server:
                tools_by_server[tool.server_name] = []
            tools_by_server[tool.server_name].append(tool)
        
        for server_name, server_tools in tools_by_server.items():
            guidance += f"**{server_name} Tools:**\n"
            for tool in server_tools:
                guidance += f"- {tool.name}: {tool.description}\n"
            guidance += "\n"
        
        # Add context-specific guidance
        if context == ContextType.BUSINESS_MEETING:
            guidance += """
**MCP Tool Usage in Business Meetings:**
- Use MCP tools to gather real-time information when making decisions
- Consider using MCP tools to generate data or reports that support your arguments
- Remember that MCP tools may access external systems - use appropriately
- Always mention when you're using external tools for transparency
"""
        elif context == ContextType.TECHNICAL_DISCUSSION:
            guidance += """
**MCP Tool Usage in Technical Discussions:**
- Use MCP tools to access technical resources, documentation, or systems
- Leverage MCP tools for code analysis, system monitoring, or debugging
- Consider MCP tools for accessing development environments or repositories
- Share MCP tool results when they provide technical insights
"""
        else:
            guidance += """
**General MCP Tool Usage:**
- Use MCP tools when you need information or capabilities beyond your built-in tools
- Consider the appropriate output mode (PRESENT/TALK/HYBRID) when using MCP tools
- Remember that MCP tools connect to external systems and may have side effects
- Always provide context when sharing results from MCP tools
"""
        
        return guidance
    
    def process_action(self, action: dict) -> bool:
        """Enhanced action processing with MCP tool support."""
        
        action_type = action.get('type', '').upper()
        
        # Check if this is an MCP tool action
        if action_type.startswith('MCP_'):
            return self._process_mcp_action(action)
        
        # Fall back to standard present feature processing
        return super().process_action(action)
    
    def _process_mcp_action(self, action: dict) -> bool:
        """Process MCP tool actions."""
        
        if not self.mcp_enabled:
            self.think("MCP tools are not enabled for me.")
            return False
        
        try:
            action_type = action.get('type', '')
            tool_name = action_type.replace('MCP_', '').lower()
            
            # Check if we have access to this MCP tool
            available_tools = global_tool_orchestrator.get_available_tools(self)
            mcp_tool = None
            
            for tool in available_tools:
                if isinstance(tool, MCPToolWrapper) and tool.name.endswith(tool_name):
                    mcp_tool = tool
                    break
            
            if not mcp_tool:
                self.think(f"I don't have access to MCP tool: {tool_name}")
                return False
            
            # Process the MCP tool action
            success = mcp_tool.process_action(self, action)
            
            if success:
                # Track MCP tool usage
                self.mcp_tools_used.append({
                    'tool_name': mcp_tool.name,
                    'server_name': mcp_tool.server_name,
                    'timestamp': self._get_current_timestamp(),
                    'action': action
                })
                
                self.think(f"Successfully used MCP tool: {mcp_tool.name} from {mcp_tool.server_name}")
            
            return success
            
        except Exception as e:
            self.think(f"Error processing MCP action: {str(e)}")
            return False
    
    def suggest_mcp_action(self, task_description: str, context: ContextType) -> Optional[Dict[str, Any]]:
        """Suggest an appropriate MCP tool action based on task and context."""
        
        if not self.mcp_enabled:
            return None
        
        # Get available MCP tools
        mcp_tools = mcp_integration_manager.get_mcp_tools_for_role(self.role)
        
        if not mcp_tools:
            return None
        
        # Simple keyword matching to suggest appropriate tools
        task_lower = task_description.lower()
        
        for tool in mcp_tools:
            tool_desc_lower = tool.description.lower()
            
            # Check for keyword matches
            if any(word in tool_desc_lower for word in task_lower.split()):
                return {
                    "type": f"MCP_{tool.name.split('_')[-1].upper()}",
                    "content": {
                        "tool": tool.name,
                        "server": tool.server_name,
                        "task": task_description,
                        "output_mode": "hybrid"  # Default to hybrid for MCP tools
                    },
                    "suggestion_reason": f"Tool '{tool.name}' matches task keywords"
                }
        
        return None
    
    def get_mcp_capabilities_summary(self) -> Dict[str, Any]:
        """Get a summary of this agent's MCP capabilities."""
        
        base_summary = self.get_present_capabilities_summary()
        
        if self.mcp_enabled:
            mcp_tools = mcp_integration_manager.get_mcp_tools_for_role(self.role)
            
            mcp_summary = {
                "mcp_enabled": True,
                "available_mcp_tools": len(mcp_tools),
                "mcp_tools_used": len(self.mcp_tools_used),
                "mcp_servers_available": len(set(tool.server_name for tool in mcp_tools)),
                "recent_mcp_usage": self.mcp_tools_used[-5:] if self.mcp_tools_used else []
            }
        else:
            mcp_summary = {"mcp_enabled": False}
        
        return {**base_summary, **mcp_summary}
    
    def enable_mcp(self):
        """Enable MCP tool access for this agent."""
        self.mcp_enabled = True
        self._assign_mcp_tools()
        logger.info(f"Enabled MCP tools for {self.name}")
    
    def disable_mcp(self):
        """Disable MCP tool access for this agent."""
        self.mcp_enabled = False
        logger.info(f"Disabled MCP tools for {self.name}")
    
    def list_available_mcp_tools(self) -> List[Dict[str, str]]:
        """List all MCP tools available to this agent."""
        
        if not self.mcp_enabled:
            return []
        
        mcp_tools = mcp_integration_manager.get_mcp_tools_for_role(self.role)
        
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "server": tool.server_name,
                "permission": global_tool_orchestrator.permission_manager.check_permission(
                    self.role, tool.name, "write"
                )
            }
            for tool in mcp_tools
        ]


def create_mcp_present_adaptive_agent(name: str, role_occupation: str, **kwargs) -> MCPPresentAdaptiveTinyPerson:
    """
    Factory function to create an MCPPresentAdaptiveTinyPerson with role-appropriate configuration.
    
    Args:
        name: Agent name
        role_occupation: The agent's occupation/role (used for tool assignment)
        **kwargs: Additional configuration parameters
    
    Returns:
        Configured MCPPresentAdaptiveTinyPerson instance with MCP capabilities
    """
    
    # Create the MCP-enabled agent (don't pass occupation to constructor)
    agent = MCPPresentAdaptiveTinyPerson(name, **kwargs)
    
    # Set occupation after creation using define method
    agent.define("occupation", role_occupation)
    
    # Additional role-specific configuration (inherited from parent)
    role_configs = {
        "compliance_officer": {
            "expertise_domains": [
                {
                    "domain": "Compliance and External Tools",
                    "competency_level": "Expert",
                    "specific_knowledge": "HIPAA, SOX, PCI-DSS, regulatory auditing, external compliance tools"
                }
            ]
        },
        "technical_lead": {
            "expertise_domains": [
                {
                    "domain": "Software Architecture and External Systems",
                    "competency_level": "Expert", 
                    "specific_knowledge": "System design, technical specifications, external development tools, MCP integrations"
                }
            ]
        },
        "project_manager": {
            "expertise_domains": [
                {
                    "domain": "Project Management and External Resources",
                    "competency_level": "Expert",
                    "specific_knowledge": "Project planning, resource management, external project tools, stakeholder communication"
                }
            ]
        }
    }
    
    # Apply role-specific configuration
    if agent.role in role_configs:
        for key, value in role_configs[agent.role].items():
            agent.define(key, value)
    
    return agent


async def setup_mcp_servers_for_tinytroupe():
    """
    Setup common MCP servers for TinyTroupe usage.
    
    This function configures and connects to commonly useful MCP servers
    that provide tools beneficial for business simulation scenarios.
    """
    
    # Example MCP server configurations
    # Note: These would need to be adapted based on actual available MCP servers
    
    # Example: File system server
    mcp_integration_manager.configure_mcp_server(
        name="filesystem",
        command=["uvx", "mcp-server-filesystem", "--directory", "."]
    )
    
    # Example: Git server
    mcp_integration_manager.configure_mcp_server(
        name="git",
        command=["uvx", "mcp-server-git", "--repository", "."]
    )
    
    # Example: Database server (if available)
    # mcp_integration_manager.configure_mcp_server(
    #     name="database",
    #     command=["uvx", "mcp-server-postgres"],
    #     env={"DATABASE_URL": "postgresql://localhost/tinytroupe"}
    # )
    
    # Connect to configured servers
    try:
        await mcp_integration_manager.connect_to_servers()
        print(f"✅ Connected to {len(mcp_integration_manager.connected_servers)} MCP servers")
        
        # Display integration status
        status = mcp_integration_manager.get_integration_status()
        print(f"📊 MCP Integration Status: {status}")
        
    except Exception as e:
        print(f"❌ Failed to setup MCP servers: {e}")


# Usage example for testing MCP integration
async def test_mcp_integration():
    """Test function to demonstrate MCP integration with TinyTroupe."""
    
    print("🚀 Testing MCP Integration with TinyTroupe...")
    
    # Setup MCP servers
    await setup_mcp_servers_for_tinytroupe()
    
    # Create MCP-enabled agents
    compliance_agent = create_mcp_present_adaptive_agent(
        "Michael Thompson", 
        "Compliance Officer"
    )
    
    tech_agent = create_mcp_present_adaptive_agent(
        "Dr. James Wilson", 
        "Chief Technology Officer"
    )
    
    # Display agent capabilities
    print(f"\n👤 {compliance_agent.name} MCP Capabilities:")
    print(compliance_agent.get_mcp_capabilities_summary())
    
    print(f"\n👤 {tech_agent.name} MCP Capabilities:")
    print(tech_agent.get_mcp_capabilities_summary())
    
    # List available MCP tools
    print(f"\n🔧 {compliance_agent.name} Available MCP Tools:")
    for tool in compliance_agent.list_available_mcp_tools():
        print(f"  - {tool['name']}: {tool['description']} (Server: {tool['server']})")
    
    return compliance_agent, tech_agent


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_mcp_integration())