"""
Tool Orchestration Layer for TinyTroupe Present Feature

This module provides centralized tool management, orchestration, and provenance logging
for agent tool usage in the TinyTroupe simulation environment.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from tinytroupe.tools import logger
from tinytroupe.tools.tiny_tool import TinyTool
from tinytroupe.utils import JsonSerializableRegistry


class OutputMode(Enum):
    """Output modes for present feature tools."""
    PRESENT = "present"  # Detailed document generation
    TALK = "talk"       # Conversational summary
    HYBRID = "hybrid"   # Summary with document references


@dataclass
class ProvenanceRecord:
    """Records the provenance of tool usage and outputs."""
    timestamp: str
    agent_name: str
    tool_name: str
    action_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    output_mode: str
    reasoning_trace: Optional[str] = None
    confidence_score: Optional[float] = None
    references: Optional[List[str]] = None
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class ProvenanceLogger:
    """Logs and manages provenance records for tool usage."""
    
    def __init__(self):
        self.records: List[ProvenanceRecord] = []
        self.session_id = f"session_{int(time.time())}"
    
    def log_tool_usage(self, 
                      agent_name: str,
                      tool_name: str, 
                      action_type: str,
                      input_data: Dict[str, Any],
                      output_data: Dict[str, Any],
                      output_mode: OutputMode,
                      reasoning_trace: Optional[str] = None,
                      confidence_score: Optional[float] = None,
                      references: Optional[List[str]] = None) -> str:
        """
        Log a tool usage event.
        
        Returns:
            str: Unique record ID for this provenance entry
        """
        timestamp = datetime.now().isoformat()
        record = ProvenanceRecord(
            timestamp=timestamp,
            agent_name=agent_name,
            tool_name=tool_name,
            action_type=action_type,
            input_data=input_data,
            output_data=output_data,
            output_mode=output_mode.value,
            reasoning_trace=reasoning_trace,
            confidence_score=confidence_score,
            references=references,
            session_id=self.session_id
        )
        
        self.records.append(record)
        record_id = f"{self.session_id}_{len(self.records)}"
        
        logger.info(f"Logged tool usage: {agent_name} used {tool_name} in {output_mode.value} mode")
        logger.debug(f"Provenance record {record_id}: {record.to_dict()}")
        
        return record_id
    
    def get_records_by_agent(self, agent_name: str) -> List[ProvenanceRecord]:
        """Get all records for a specific agent."""
        return [r for r in self.records if r.agent_name == agent_name]
    
    def get_records_by_tool(self, tool_name: str) -> List[ProvenanceRecord]:
        """Get all records for a specific tool."""
        return [r for r in self.records if r.tool_name == tool_name]
    
    def export_provenance(self, filepath: str):
        """Export all provenance records to JSON file."""
        with open(filepath, 'w') as f:
            json.dump([r.to_dict() for r in self.records], f, indent=2)
        logger.info(f"Exported {len(self.records)} provenance records to {filepath}")


class ToolPermissionManager:
    """Manages role-based permissions for tool access."""
    
    def __init__(self):
        # Role -> Tool Name -> Permission Level mapping
        self.permissions: Dict[str, Dict[str, str]] = {
            "default": {},  # Default permissions for all agents
        }
        
        # Built-in permission levels
        self.permission_levels = {
            "none": 0,
            "read": 1, 
            "write": 2,
            "admin": 3
        }
    
    def set_role_permission(self, role: str, tool_name: str, permission_level: str):
        """Set permission level for a role and tool."""
        if permission_level not in self.permission_levels:
            raise ValueError(f"Invalid permission level: {permission_level}")
        
        if role not in self.permissions:
            self.permissions[role] = {}
        
        self.permissions[role][tool_name] = permission_level
        logger.debug(f"Set {role} permission for {tool_name}: {permission_level}")
    
    def check_permission(self, agent_role: str, tool_name: str, required_level: str = "read") -> bool:
        """Check if an agent role has required permission for a tool."""
        # Check role-specific permissions first
        if agent_role in self.permissions and tool_name in self.permissions[agent_role]:
            granted_level = self.permissions[agent_role][tool_name]
        # Fall back to default permissions
        elif tool_name in self.permissions["default"]:
            granted_level = self.permissions["default"][tool_name]
        else:
            # No explicit permission set - default to 'read' for safety
            granted_level = "read"
        
        granted_value = self.permission_levels.get(granted_level, 0)
        required_value = self.permission_levels.get(required_level, 1)
        
        has_permission = granted_value >= required_value
        logger.debug(f"Permission check: {agent_role} -> {tool_name} ({required_level}): {has_permission}")
        
        return has_permission


class PresentTool(TinyTool):
    """
    Base class for tools that support the Present Feature's dual output modes.
    
    Extends TinyTool with capabilities for generating both detailed documents
    and conversational summaries, with full provenance tracking.
    """
    
    def __init__(self, name: str, description: str, owner=None, 
                 real_world_side_effects=False, exporter=None, enricher=None,
                 supported_modes: List[OutputMode] = None):
        super().__init__(name, description, owner, real_world_side_effects, exporter, enricher)
        
        if supported_modes is None:
            self.supported_modes = [OutputMode.PRESENT, OutputMode.TALK]
        else:
            self.supported_modes = supported_modes
        
        self.provenance_logger = None  # Will be set by ToolOrchestrator
    
    def supports_mode(self, mode: OutputMode) -> bool:
        """Check if this tool supports the given output mode."""
        return mode in self.supported_modes
    
    def _process_present_action(self, agent, action: dict, output_mode: OutputMode) -> Dict[str, Any]:
        """
        Process a present-mode action and return structured output.
        
        Subclasses must implement this method to handle their specific logic.
        
        Returns:
            Dict containing 'content', 'format', 'references', and metadata
        """
        raise NotImplementedError("Subclasses must implement _process_present_action")
    
    def _determine_output_mode(self, agent, action: dict) -> OutputMode:
        """
        Determine the appropriate output mode based on action content and context.
        
        Can be overridden by subclasses for custom logic.
        """
        # Check if mode is explicitly specified
        if 'output_mode' in action:
            mode_str = action['output_mode'].lower()
            try:
                return OutputMode(mode_str)
            except ValueError:
                logger.warning(f"Invalid output mode '{mode_str}', falling back to PRESENT")
        
        # Check action type for hints
        action_type = action.get('type', '').upper()
        if 'SUMMARIZE' in action_type or 'TALK' in action_type:
            return OutputMode.TALK
        elif 'PRESENT' in action_type or 'DOCUMENT' in action_type:
            return OutputMode.PRESENT
        
        # Default to PRESENT mode
        return OutputMode.PRESENT
    
    def process_action(self, agent, action: dict) -> bool:
        """
        Enhanced process_action that handles dual output modes and provenance logging.
        """
        # Standard TinyTool checks
        self._protect_real_world()
        self._enforce_ownership(agent)
        
        # Determine output mode
        output_mode = self._determine_output_mode(agent, action)
        
        if not self.supports_mode(output_mode):
            logger.error(f"Tool {self.name} does not support {output_mode.value} mode")
            return False
        
        try:
            # Process the action with the determined mode
            result = self._process_present_action(agent, action, output_mode)
            
            # Log provenance if logger is available
            if self.provenance_logger:
                self.provenance_logger.log_tool_usage(
                    agent_name=agent.name,
                    tool_name=self.name,
                    action_type=action.get('type', 'UNKNOWN'),
                    input_data=action,
                    output_data=result,
                    output_mode=output_mode,
                    reasoning_trace=result.get('reasoning_trace'),
                    confidence_score=result.get('confidence_score'),
                    references=result.get('references')
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing present action in {self.name}: {e}")
            return False


class ToolOrchestrator(JsonSerializableRegistry):
    """
    Central orchestrator for managing tools, permissions, and provenance in TinyTroupe.
    
    Provides a unified interface for tool registration, discovery, and execution
    with full support for the Present Feature's dual output modes.
    """
    
    def __init__(self):
        self.tools: Dict[str, TinyTool] = {}
        self.present_tools: Dict[str, PresentTool] = {}
        self.permission_manager = ToolPermissionManager()
        self.provenance_logger = ProvenanceLogger()
        
        # Role-based tool assignments
        self.role_tool_assignments: Dict[str, List[str]] = {}
    
    def register_tool(self, tool: TinyTool):
        """Register a tool with the orchestrator."""
        self.tools[tool.name] = tool
        
        # If it's a PresentTool, register separately and set provenance logger
        if isinstance(tool, PresentTool):
            self.present_tools[tool.name] = tool
            tool.provenance_logger = self.provenance_logger
        
        logger.info(f"Registered tool: {tool.name}")
    
    def assign_tools_to_role(self, role: str, tool_names: List[str]):
        """Assign a list of tools to a specific role."""
        self.role_tool_assignments[role] = tool_names
        logger.info(f"Assigned tools to {role}: {tool_names}")
    
    def get_tools_for_role(self, role: str) -> List[TinyTool]:
        """Get all tools assigned to a specific role."""
        tool_names = self.role_tool_assignments.get(role, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
    
    def get_available_tools(self, agent) -> List[TinyTool]:
        """
        Get all tools available to an agent based on role and permissions.
        """
        agent_role = getattr(agent, 'role', 'default')
        available_tools = []
        
        # Get role-assigned tools
        role_tools = self.get_tools_for_role(agent_role)
        
        for tool in role_tools:
            if self.permission_manager.check_permission(agent_role, tool.name, "read"):
                available_tools.append(tool)
        
        # Add any tools owned by the agent
        if agent is not None:
            for tool in self.tools.values():
                if tool.owner and tool.owner.name == agent.name:
                    if tool not in available_tools:
                        available_tools.append(tool)
        
        return available_tools
    
    def process_tool_action(self, agent, action: dict) -> bool:
        """
        Process a tool action through the orchestrator.
        
        This is the main entry point for all tool usage in the present feature.
        """
        action_type = action.get('type')
        
        # Try each available tool until one processes the action
        available_tools = self.get_available_tools(agent)
        
        for tool in available_tools:
            try:
                if tool.process_action(agent, action):
                    logger.debug(f"Action {action_type} processed by tool {tool.name}")
                    return True
            except Exception as e:
                logger.error(f"Error in tool {tool.name}: {e}")
                continue
        
        logger.debug(f"No tool could process action {action_type}")
        return False
    
    def get_tool_definitions_prompt(self, agent) -> str:
        """Get action definitions for all tools available to the agent."""
        available_tools = self.get_available_tools(agent)
        
        prompt = "Available Tools and Actions:\n"
        for tool in available_tools:
            prompt += f"\n{tool.name.upper()} TOOL:\n"
            prompt += tool.actions_definitions_prompt()
        
        return prompt
    
    def get_tool_constraints_prompt(self, agent) -> str:
        """Get action constraints for all tools available to the agent."""
        available_tools = self.get_available_tools(agent)
        
        prompt = "Tool Usage Constraints:\n"
        for tool in available_tools:
            prompt += f"\n{tool.name.upper()} TOOL CONSTRAINTS:\n"
            prompt += tool.actions_constraints_prompt()
        
        return prompt
    
    def export_usage_report(self, filepath: str):
        """Export a comprehensive usage report with provenance data."""
        report = {
            "session_id": self.provenance_logger.session_id,
            "total_tools": len(self.tools),
            "present_tools": len(self.present_tools),
            "total_actions": len(self.provenance_logger.records),
            "tools": {name: {"type": type(tool).__name__} for name, tool in self.tools.items()},
            "role_assignments": self.role_tool_assignments,
            "provenance_records": [r.to_dict() for r in self.provenance_logger.records]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Exported tool usage report to {filepath}")


# Global orchestrator instance
global_tool_orchestrator = ToolOrchestrator()