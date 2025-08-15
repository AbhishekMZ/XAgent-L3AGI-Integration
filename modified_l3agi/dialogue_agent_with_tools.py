"""
Modified Dialogue Agent with Tools - XAgent Integration
Replaces Langchain REACT Agent with XAgent for tool-enabled dialogue
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

# XAgent integration imports
from xagent_integration.l3agi_compatibility import DialogueAgentWithToolsXAgent
from xagent_integration.xagent_core import XAgentWrapper

class DialogueAgentWithTools:
    """
    Tool-enabled dialogue agent using XAgent backend
    Maintains L3AGI interface while leveraging XAgent's advanced tool integration
    """
    
    def __init__(self,
                 name: str,
                 system_message: str,
                 tools: List[Any] = None,
                 **kwargs):
        """Initialize dialogue agent with XAgent backend"""
        
        self.name = name
        self.system_message = system_message
        self.tools = tools or []
        self.model_config = kwargs.get("model_config", {})
        
        # Initialize XAgent wrapper
        self.xagent = DialogueAgentWithToolsXAgent(
            name=name,
            tools=self.tools,
            system_prompt=system_message,
            role=kwargs.get("role", "assistant"),
            description=kwargs.get("description", f"Tool-enabled agent {name}"),
            **kwargs
        )
        
        self.dialogue_history = []
        self.tool_usage_stats = {}
        self.logger = logging.getLogger(f"L3AGI.DialogueTools.{name}")
        
        self.logger.info(f"Dialogue agent {name} initialized with {len(self.tools)} tools")
    
    async def send(self, message: str, **kwargs) -> str:
        """
        Send message method - L3AGI interface maintained
        Enhanced with XAgent's intelligent tool selection and usage
        """
        try:
            # Log incoming message
            self.logger.info(f"Processing message: {message[:100]}...")
            
            # Use XAgent for intelligent response generation
            response = await self.xagent.send(message, **kwargs)
            
            # Track dialogue history
            self.dialogue_history.append({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "response": response,
                "tools_available": len(self.tools)
            })
            
            # Update tool usage statistics
            self._update_tool_stats(response)
            
            return response
            
        except Exception as e:
            error_msg = f"Dialogue send failed: {str(e)}"
            self.logger.error(error_msg)
            return f"I encountered an error processing your message: {str(e)}"
    
    def _update_tool_stats(self, response: str):
        """Update tool usage statistics based on response"""
        for tool in self.tools:
            tool_name = getattr(tool, '__name__', str(tool))
            if tool_name.lower() in response.lower():
                self.tool_usage_stats[tool_name] = self.tool_usage_stats.get(tool_name, 0) + 1
    
    async def generate_reply(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate reply method - L3AGI compatibility"""
        if not messages:
            return "No messages to respond to."
        
        # Format messages for XAgent
        latest_message = messages[-1].get("content", "")
        return await self.send(latest_message, **kwargs)
    
    def add_tool(self, tool: Any, description: str = None):
        """Add tool to agent - L3AGI interface"""
        self.tools.append(tool)
        self.xagent.tools.append(tool)
        
        # Update tool description if provided
        if description and hasattr(tool, 'description'):
            tool.description = description
        
        self.logger.info(f"Tool added: {getattr(tool, '__name__', str(tool))}")
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove tool from agent"""
        for i, tool in enumerate(self.tools):
            if getattr(tool, '__name__', str(tool)) == tool_name:
                removed_tool = self.tools.pop(i)
                self.xagent.tools.remove(removed_tool)
                self.logger.info(f"Tool removed: {tool_name}")
                return True
        return False
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        tools_info = []
        for tool in self.tools:
            tool_info = {
                "name": getattr(tool, '__name__', str(tool)),
                "description": getattr(tool, 'description', 'No description available'),
                "usage_count": self.tool_usage_stats.get(getattr(tool, '__name__', str(tool)), 0)
            }
            tools_info.append(tool_info)
        return tools_info
    
    def describe(self) -> str:
        """Get agent description - L3AGI interface"""
        return self.xagent.describe()
    
    def get_dialogue_history(self) -> List[Dict[str, Any]]:
        """Get dialogue history"""
        return self.dialogue_history
    
    def clear_history(self):
        """Clear dialogue history"""
        self.dialogue_history.clear()
        self.xagent.clear_memory()
        self.logger.info("Dialogue history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.name,
            "total_dialogues": len(self.dialogue_history),
            "tools_count": len(self.tools),
            "tool_usage_stats": self.tool_usage_stats,
            "backend": "XAgent",
            "last_activity": self.dialogue_history[-1]["timestamp"] if self.dialogue_history else None
        }


class TeamDialogueAgent(DialogueAgentWithTools):
    """
    Team-enabled dialogue agent for multi-agent collaboration
    Enhanced with XAgent's team coordination capabilities
    """
    
    def __init__(self, name: str, system_message: str, team_role: str, tools: List[Any] = None, **kwargs):
        # Enhance system message for team context
        team_system_message = f"""
{system_message}

TEAM ROLE: {team_role}
You are part of a collaborative team of AI agents. Coordinate effectively with team members,
share relevant information, and leverage team expertise to solve complex problems.
"""
        
        super().__init__(name, team_system_message, tools, **kwargs)
        self.team_role = team_role
        self.team_coordination_history = []
        
        self.logger.info(f"Team dialogue agent {name} initialized with role: {team_role}")
    
    async def coordinate_with_team(self, coordination_message: str, target_agents: List[str] = None) -> str:
        """Coordinate with team members"""
        coordination_context = {
            "type": "team_coordination",
            "from_agent": self.name,
            "role": self.team_role,
            "target_agents": target_agents or [],
            "message": coordination_message
        }
        
        # Process coordination with XAgent
        response = await self.send(
            f"Team coordination required: {coordination_message}",
            coordination_context=coordination_context
        )
        
        # Track coordination history
        self.team_coordination_history.append({
            "timestamp": datetime.now().isoformat(),
            "coordination_message": coordination_message,
            "response": response,
            "target_agents": target_agents
        })
        
        return response
    
    def get_team_stats(self) -> Dict[str, Any]:
        """Get team-specific statistics"""
        base_stats = self.get_stats()
        base_stats.update({
            "team_role": self.team_role,
            "coordination_count": len(self.team_coordination_history),
            "last_coordination": self.team_coordination_history[-1]["timestamp"] if self.team_coordination_history else None
        })
        return base_stats


class ToolManager:
    """
    Tool manager for dialogue agents
    Provides centralized tool management and registration
    """
    
    def __init__(self):
        self.registered_tools = {}
        self.tool_categories = {}
        self.logger = logging.getLogger("L3AGI.ToolManager")
    
    def register_tool(self, tool: Any, category: str = "general", description: str = None):
        """Register a tool with the manager"""
        tool_name = getattr(tool, '__name__', str(tool))
        
        self.registered_tools[tool_name] = {
            "tool": tool,
            "category": category,
            "description": description or getattr(tool, 'description', 'No description'),
            "registered_at": datetime.now().isoformat()
        }
        
        # Update category mapping
        if category not in self.tool_categories:
            self.tool_categories[category] = []
        self.tool_categories[category].append(tool_name)
        
        self.logger.info(f"Tool registered: {tool_name} in category {category}")
    
    def get_tools_by_category(self, category: str) -> List[Any]:
        """Get tools by category"""
        if category not in self.tool_categories:
            return []
        
        tools = []
        for tool_name in self.tool_categories[category]:
            if tool_name in self.registered_tools:
                tools.append(self.registered_tools[tool_name]["tool"])
        
        return tools
    
    def create_agent_with_tools(self, name: str, system_message: str, tool_categories: List[str]) -> DialogueAgentWithTools:
        """Create agent with tools from specified categories"""
        tools = []
        for category in tool_categories:
            tools.extend(self.get_tools_by_category(category))
        
        return DialogueAgentWithTools(name, system_message, tools)


# Factory functions for L3AGI integration
def create_dialogue_agent(config: Dict[str, Any]) -> DialogueAgentWithTools:
    """Factory function to create dialogue agents"""
    agent_type = config.get("type", "standard")
    
    if agent_type == "team":
        return TeamDialogueAgent(
            name=config.get("name", "TeamDialogueAgent"),
            system_message=config.get("system_message", "You are a helpful AI assistant."),
            team_role=config.get("team_role", "member"),
            tools=config.get("tools", [])
        )
    else:
        return DialogueAgentWithTools(
            name=config.get("name", "DialogueAgent"),
            system_message=config.get("system_message", "You are a helpful AI assistant."),
            tools=config.get("tools", [])
        )


# Export classes for L3AGI integration
__all__ = [
    "DialogueAgentWithTools", 
    "TeamDialogueAgent", 
    "ToolManager",
    "create_dialogue_agent"
]
