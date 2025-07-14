"""
MCP (Model Context Protocol) Integration for TinyTroupe

This module provides MCP client capabilities for TinyTroupe agents, enabling them
to connect to and use tools from MCP servers. This extends the Present Feature's
tool orchestration with external MCP tool capabilities.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from contextlib import asynccontextmanager

import mcp
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp import ClientSession, StdioServerParameters

from tinytroupe.tools.tool_orchestrator import PresentTool, OutputMode, ProvenanceLogger
from tinytroupe.tools import logger


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server connection."""
    name: str
    command: List[str]
    args: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None
    transport_type: str = "stdio"  # "stdio" or "sse"
    url: Optional[str] = None  # For SSE transport


class MCPToolWrapper(PresentTool):
    """
    Wraps an MCP tool to work with TinyTroupe's tool orchestration system.
    
    This adapter allows MCP tools to be used seamlessly within TinyTroupe's
    Present Feature architecture while maintaining full provenance tracking.
    """
    
    def __init__(self, mcp_tool: mcp.Tool, mcp_client: 'MCPClient', server_name: str):
        super().__init__(
            name=f"mcp_{server_name}_{mcp_tool.name}",
            description=f"MCP Tool: {mcp_tool.description}",
            real_world_side_effects=True,  # MCP tools may have side effects
            supported_modes=[OutputMode.PRESENT, OutputMode.TALK, OutputMode.HYBRID]
        )
        
        self.mcp_tool = mcp_tool
        self.mcp_client = mcp_client
        self.server_name = server_name
        
        # Store original MCP tool info for reference
        self.mcp_tool_info = {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "schema": mcp_tool.inputSchema if hasattr(mcp_tool, 'inputSchema') else None
        }
    
    def _process_present_action(self, agent, action: dict, output_mode: OutputMode) -> Dict[str, Any]:
        """Process action using the MCP tool."""
        
        try:
            # Extract MCP tool parameters from action
            content = action.get('content', {})
            
            # Handle different input formats
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    content = {"input": content}
            
            # Prepare MCP tool arguments
            mcp_arguments = content.get('arguments', content.get('params', content))
            
            # Call MCP tool asynchronously (we'll need to handle this)
            result = asyncio.run(self._call_mcp_tool_async(mcp_arguments))
            
            # Format result based on output mode
            if output_mode == OutputMode.PRESENT:
                return self._format_present_result(result, mcp_arguments)
            elif output_mode == OutputMode.TALK:
                return self._format_talk_result(result, mcp_arguments)
            else:  # HYBRID
                return self._format_hybrid_result(result, mcp_arguments)
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {self.mcp_tool.name}: {e}")
            return {
                "content": f"Error calling MCP tool: {str(e)}",
                "format": "text",
                "references": [],
                "confidence_score": 0.0,
                "error": str(e)
            }
    
    async def _call_mcp_tool_async(self, arguments: Dict[str, Any]) -> Any:
        """Call the MCP tool asynchronously."""
        return await self.mcp_client.call_tool(self.server_name, self.mcp_tool.name, arguments)
    
    def _format_present_result(self, result: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Format MCP result for PRESENT mode (detailed output)."""
        
        # Try to extract content from MCP result
        content = self._extract_content_from_result(result)
        
        return {
            "content": f"MCP Tool Result: {self.mcp_tool.name}\n\n{content}",
            "format": "markdown",
            "references": [f"MCP Server: {self.server_name}", f"Tool: {self.mcp_tool.name}"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Called MCP tool {self.mcp_tool.name} with arguments: {arguments}",
            "mcp_result": result,
            "tool_info": self.mcp_tool_info
        }
    
    def _format_talk_result(self, result: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Format MCP result for TALK mode (conversational output)."""
        
        content = self._extract_content_from_result(result)
        
        # Create a conversational summary
        summary = f"I used the {self.mcp_tool.name} tool and got: {content}"
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        return {
            "content": summary,
            "format": "text",
            "references": [f"MCP Tool: {self.mcp_tool.name}"],
            "confidence_score": 0.85,
            "reasoning_trace": f"Summarized result from MCP tool {self.mcp_tool.name}"
        }
    
    def _format_hybrid_result(self, result: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Format MCP result for HYBRID mode (summary with detailed reference)."""
        
        content = self._extract_content_from_result(result)
        
        # Create hybrid response
        hybrid_content = f"I executed the {self.mcp_tool.name} tool successfully. "
        
        if len(content) > 100:
            hybrid_content += f"Here's a summary: {content[:100]}... "
            hybrid_content += "The full detailed results are available for reference."
        else:
            hybrid_content += f"Result: {content}"
        
        return {
            "content": hybrid_content,
            "format": "text",
            "references": [f"MCP Tool: {self.mcp_tool.name}", f"Detailed Result Available"],
            "confidence_score": 0.9,
            "reasoning_trace": f"Hybrid response from MCP tool {self.mcp_tool.name}",
            "detailed_result": result
        }
    
    def _extract_content_from_result(self, result: Any) -> str:
        """Extract readable content from MCP tool result."""
        
        if isinstance(result, dict):
            # Look for common content fields
            for field in ['content', 'text', 'result', 'output', 'data']:
                if field in result:
                    content = result[field]
                    if isinstance(content, (str, int, float)):
                        return str(content)
                    elif isinstance(content, list):
                        return '\n'.join(str(item) for item in content)
            
            # If no standard field, return JSON representation
            return json.dumps(result, indent=2)
        
        elif isinstance(result, list):
            return '\n'.join(str(item) for item in result)
        
        else:
            return str(result)
    
    def actions_definitions_prompt(self) -> str:
        """Generate action definitions for this MCP tool."""
        
        schema_info = ""
        if self.mcp_tool_info.get('schema'):
            schema_info = f"\n  Schema: {json.dumps(self.mcp_tool_info['schema'], indent=2)}"
        
        return f"""
        - {self.name.upper()}: {self.mcp_tool_info['description']}
          * arguments: Parameters for the MCP tool{schema_info}
          * output_mode: "present", "talk", or "hybrid"
        """
    
    def actions_constraints_prompt(self) -> str:
        """Generate action constraints for this MCP tool."""
        
        return f"""
        - When using {self.name}, provide appropriate arguments based on the tool's requirements
        - This is an external MCP tool that may have real-world side effects
        - Use "present" mode for detailed results, "talk" mode for summaries
        """


class MCPClient:
    """
    MCP client for TinyTroupe that manages connections to MCP servers
    and provides tool discovery and execution capabilities.
    """
    
    def __init__(self, provenance_logger: Optional[ProvenanceLogger] = None):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.sessions: Dict[str, ClientSession] = {}
        self.available_tools: Dict[str, MCPToolWrapper] = {}
        self.provenance_logger = provenance_logger
        
        # Track server capabilities
        self.server_capabilities: Dict[str, Dict] = {}
        self.server_resources: Dict[str, List] = {}
    
    def add_server(self, config: MCPServerConfig):
        """Add an MCP server configuration."""
        self.servers[config.name] = config
        logger.info(f"Added MCP server configuration: {config.name}")
    
    async def connect_to_server(self, server_name: str) -> bool:
        """Connect to an MCP server and discover its tools."""
        
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not configured")
            return False
        
        config = self.servers[server_name]
        
        try:
            if config.transport_type == "stdio":
                # Create stdio connection
                server_params = StdioServerParameters(
                    command=config.command[0],
                    args=config.command[1:] if len(config.command) > 1 else [],
                    env=config.env or {}
                )
                
                # Use async context manager for stdio client
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        # Initialize connection
                        await session.initialize()
                        
                        # Store session for later use
                        self.sessions[server_name] = session
                        
                        # Discover tools
                        await self._discover_tools(server_name, session)
                        
                        # Discover resources
                        await self._discover_resources(server_name, session)
                        
                        logger.info(f"Successfully connected to MCP server: {server_name}")
                        return True
            
            elif config.transport_type == "sse":
                # Handle SSE transport (if needed)
                if not config.url:
                    logger.error(f"SSE transport requires URL for server {server_name}")
                    return False
                
                # SSE implementation would go here
                logger.warning(f"SSE transport not yet implemented for server {server_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            return False
    
    async def _discover_tools(self, server_name: str, session: ClientSession):
        """Discover tools from an MCP server."""
        
        try:
            # List available tools
            tools_result = await session.list_tools()
            
            logger.info(f"Discovered {len(tools_result.tools)} tools from {server_name}")
            
            for tool in tools_result.tools:
                # Wrap MCP tool for TinyTroupe
                wrapper = MCPToolWrapper(tool, self, server_name)
                tool_key = f"{server_name}_{tool.name}"
                self.available_tools[tool_key] = wrapper
                
                logger.debug(f"Added MCP tool: {tool_key} - {tool.description}")
                
        except Exception as e:
            logger.error(f"Failed to discover tools from {server_name}: {e}")
    
    async def _discover_resources(self, server_name: str, session: ClientSession):
        """Discover resources from an MCP server."""
        
        try:
            # List available resources
            resources_result = await session.list_resources()
            
            self.server_resources[server_name] = resources_result.resources
            logger.info(f"Discovered {len(resources_result.resources)} resources from {server_name}")
            
        except Exception as e:
            logger.error(f"Failed to discover resources from {server_name}: {e}")
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on an MCP server."""
        
        if server_name not in self.sessions:
            raise ValueError(f"Not connected to server {server_name}")
        
        session = self.sessions[server_name]
        
        try:
            # Create tool call request
            result = await session.call_tool(tool_name, arguments)
            
            # Log the tool call for provenance
            if self.provenance_logger:
                self.provenance_logger.log_tool_usage(
                    agent_name="mcp_client",
                    tool_name=f"{server_name}_{tool_name}",
                    action_type="MCP_TOOL_CALL",
                    input_data=arguments,
                    output_data=result.content if hasattr(result, 'content') else result,
                    output_mode=OutputMode.PRESENT
                )
            
            return result.content if hasattr(result, 'content') else result
            
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name} on {server_name}: {e}")
            raise
    
    def get_available_tools(self) -> List[MCPToolWrapper]:
        """Get all available MCP tools as TinyTroupe-compatible wrappers."""
        return list(self.available_tools.values())
    
    def get_tool_by_name(self, tool_name: str) -> Optional[MCPToolWrapper]:
        """Get an MCP tool wrapper by name."""
        return self.available_tools.get(tool_name)
    
    async def disconnect_all(self):
        """Disconnect from all MCP servers."""
        
        for server_name in list(self.sessions.keys()):
            try:
                # Sessions will be cleaned up by context managers
                del self.sessions[server_name]
                logger.info(f"Disconnected from MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {server_name}: {e}")
        
        self.sessions.clear()
        self.available_tools.clear()


class MCPIntegrationManager:
    """
    High-level manager for MCP integration with TinyTroupe.
    
    Handles the lifecycle of MCP connections and integrates MCP tools
    with TinyTroupe's tool orchestration system.
    """
    
    def __init__(self, tool_orchestrator=None):
        from tinytroupe.tools.tool_orchestrator import global_tool_orchestrator
        
        self.tool_orchestrator = tool_orchestrator or global_tool_orchestrator
        self.mcp_client = MCPClient(self.tool_orchestrator.provenance_logger)
        self.connected_servers: List[str] = []
    
    def configure_mcp_server(self, name: str, command: List[str], **kwargs):
        """Configure an MCP server for connection."""
        
        config = MCPServerConfig(
            name=name,
            command=command,
            **kwargs
        )
        
        self.mcp_client.add_server(config)
        logger.info(f"Configured MCP server: {name}")
    
    async def connect_to_servers(self, server_names: Optional[List[str]] = None):
        """Connect to MCP servers and register their tools."""
        
        if server_names is None:
            server_names = list(self.mcp_client.servers.keys())
        
        for server_name in server_names:
            try:
                success = await self.mcp_client.connect_to_server(server_name)
                if success:
                    self.connected_servers.append(server_name)
                    
                    # Register MCP tools with the tool orchestrator
                    mcp_tools = self.mcp_client.get_available_tools()
                    for tool in mcp_tools:
                        if tool.server_name == server_name:
                            self.tool_orchestrator.register_tool(tool)
                    
                    logger.info(f"Integrated MCP server {server_name} with TinyTroupe")
                    
            except Exception as e:
                logger.error(f"Failed to connect to MCP server {server_name}: {e}")
    
    async def disconnect_from_servers(self):
        """Disconnect from all MCP servers."""
        await self.mcp_client.disconnect_all()
        self.connected_servers.clear()
        logger.info("Disconnected from all MCP servers")
    
    def get_mcp_tools_for_role(self, role: str) -> List[MCPToolWrapper]:
        """Get MCP tools appropriate for a specific role."""
        
        all_mcp_tools = self.mcp_client.get_available_tools()
        
        # Filter based on role (this could be enhanced with more sophisticated logic)
        role_keywords = {
            "compliance_officer": ["compliance", "audit", "regulation", "policy"],
            "technical_lead": ["code", "system", "technical", "debug", "deploy"],
            "project_manager": ["schedule", "project", "task", "timeline", "resource"],
            "data_specialist": ["data", "analyze", "query", "database", "report"]
        }
        
        keywords = role_keywords.get(role, [])
        if not keywords:
            return all_mcp_tools  # Return all tools if no specific role mapping
        
        filtered_tools = []
        for tool in all_mcp_tools:
            tool_desc = tool.description.lower()
            if any(keyword in tool_desc for keyword in keywords):
                filtered_tools.append(tool)
        
        return filtered_tools
    
    def assign_mcp_tools_to_role(self, role: str, tool_names: Optional[List[str]] = None):
        """Assign MCP tools to a specific role in the tool orchestrator."""
        
        if tool_names is None:
            # Auto-assign based on tool descriptions
            mcp_tools = self.get_mcp_tools_for_role(role)
            tool_names = [tool.name for tool in mcp_tools]
        
        # Add to existing role tools
        existing_tools = self.tool_orchestrator.role_tool_assignments.get(role, [])
        combined_tools = list(set(existing_tools + tool_names))
        
        self.tool_orchestrator.assign_tools_to_role(role, combined_tools)
        logger.info(f"Assigned {len(tool_names)} MCP tools to role {role}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the current status of MCP integration."""
        
        return {
            "connected_servers": self.connected_servers,
            "total_mcp_tools": len(self.mcp_client.available_tools),
            "tools_by_server": {
                server: len([t for t in self.mcp_client.available_tools.values() 
                           if t.server_name == server])
                for server in self.connected_servers
            },
            "server_resources": {
                server: len(resources) 
                for server, resources in self.mcp_client.server_resources.items()
            }
        }


# Global MCP integration manager instance
mcp_integration_manager = MCPIntegrationManager()