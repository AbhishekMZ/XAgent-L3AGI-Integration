"""
Modified Conversational Agent - XAgent Integration
Replaces Langchain REACT Agent with XAgent for L3AGI Framework
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# XAgent integration imports
from xagent_integration.l3agi_compatibility import ConversationalXAgent
from xagent_integration.xagent_core import AgentMessage

class ConversationalAgent:
    """
    Conversational Agent using XAgent backend
    Maintains L3AGI interface while leveraging XAgent capabilities
    """
    
    def __init__(self, 
                 name: str = "ConversationalAgent",
                 system_prompt: str = None,
                 memory_enabled: bool = True,
                 tools: List[Any] = None,
                 **kwargs):
        """Initialize conversational agent with XAgent backend"""
        
        self.name = name
        self.system_prompt = system_prompt or "You are a helpful AI assistant that collaborates effectively with other agents."
        self.memory_enabled = memory_enabled
        self.tools = tools or []
        
        # Initialize XAgent wrapper
        self.xagent = ConversationalXAgent(
            agent_name=name,
            system_prompt=self.system_prompt,
            tools=self.tools,
            memory_config={"enabled": memory_enabled},
            **kwargs
        )
        
        self.conversation_history = []
        self.logger = logging.getLogger(f"L3AGI.Conversational.{name}")
        
        self.logger.info(f"Conversational Agent {name} initialized with XAgent backend")
    
    async def chat(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Main chat method - L3AGI interface maintained
        Uses XAgent for enhanced conversation capabilities
        """
        try:
            # Prepare context for XAgent
            chat_context = self._prepare_context(context)
            
            # Execute with XAgent backend
            response = await self.xagent.chat(message, chat_context)
            
            # Store in conversation history if memory enabled
            if self.memory_enabled:
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user_message": message,
                    "agent_response": response,
                    "context": context
                })
            
            self.logger.info(f"Chat completed successfully: {len(response)} chars")
            return response
            
        except Exception as e:
            error_msg = f"Conversational chat failed: {str(e)}"
            self.logger.error(error_msg)
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _prepare_context(self, context: Dict[str, Any] = None) -> List[Dict]:
        """Prepare conversation context for XAgent"""
        xagent_context = []
        
        # Add recent conversation history
        if self.memory_enabled and self.conversation_history:
            for entry in self.conversation_history[-5:]:  # Last 5 exchanges
                xagent_context.extend([
                    {"role": "user", "content": entry["user_message"]},
                    {"role": "assistant", "content": entry["agent_response"]}
                ])
        
        # Add additional context if provided
        if context:
            if "previous_messages" in context:
                xagent_context.extend(context["previous_messages"])
            
            if "team_context" in context:
                xagent_context.append({
                    "role": "system", 
                    "content": f"Team context: {context['team_context']}"
                })
        
        return xagent_context
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response method - L3AGI compatibility"""
        return await self.chat(prompt, kwargs.get("context"))
    
    def get_memory(self) -> List[Dict]:
        """Get conversation memory - L3AGI interface"""
        return self.conversation_history
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.conversation_history.clear()
        self.xagent.clear_memory()
        self.logger.info("Memory cleared")
    
    def set_system_prompt(self, prompt: str):
        """Update system prompt"""
        self.system_prompt = prompt
        self.xagent.system_prompt = prompt
        self.logger.info("System prompt updated")
    
    def add_tool(self, tool: Any):
        """Add tool to agent - L3AGI compatibility"""
        self.tools.append(tool)
        self.xagent.tools.append(tool)
        self.logger.info(f"Tool added: {str(tool)}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information - L3AGI interface"""
        return {
            "name": self.name,
            "type": "ConversationalAgent",
            "backend": "XAgent",
            "memory_enabled": self.memory_enabled,
            "tools_count": len(self.tools),
            "conversation_length": len(self.conversation_history),
            "system_prompt": self.system_prompt[:100] + "..." if len(self.system_prompt) > 100 else self.system_prompt
        }


class TeamConversationalAgent(ConversationalAgent):
    """
    Team-aware conversational agent for multi-agent scenarios
    Enhanced with XAgent's collaborative capabilities
    """
    
    def __init__(self, name: str, team_role: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self.team_role = team_role
        self.team_members = {}
        self.shared_context = {}
        
        # Update system prompt for team awareness
        team_prompt = f"""
{self.system_prompt}

You are part of a team of AI agents. Your specific role is: {team_role}
Collaborate effectively with other team members and maintain team context.
"""
        self.set_system_prompt(team_prompt)
        
        self.logger.info(f"Team agent {name} initialized with role: {team_role}")
    
    def register_team_member(self, member_name: str, member_info: Dict[str, Any]):
        """Register a team member"""
        self.team_members[member_name] = member_info
        self.logger.info(f"Team member registered: {member_name}")
    
    def update_shared_context(self, context: Dict[str, Any]):
        """Update shared team context"""
        self.shared_context.update(context)
        self.logger.info("Shared context updated")
    
    async def team_chat(self, message: str, sender: str = None, **kwargs) -> str:
        """Enhanced chat with team context"""
        # Prepare team-aware context
        team_context = {
            "team_role": self.team_role,
            "team_members": list(self.team_members.keys()),
            "shared_context": self.shared_context,
            "sender": sender
        }
        
        # Merge with provided context
        full_context = {**kwargs.get("context", {}), "team_context": team_context}
        
        return await self.chat(message, full_context)


# Factory function for L3AGI integration
def create_conversational_agent(config: Dict[str, Any]) -> ConversationalAgent:
    """Factory function to create conversational agents"""
    agent_type = config.get("type", "standard")
    
    if agent_type == "team":
        return TeamConversationalAgent(
            name=config.get("name", "TeamAgent"),
            team_role=config.get("team_role", "member"),
            system_prompt=config.get("system_prompt"),
            memory_enabled=config.get("memory_enabled", True),
            tools=config.get("tools", [])
        )
    else:
        return ConversationalAgent(
            name=config.get("name", "Agent"),
            system_prompt=config.get("system_prompt"),
            memory_enabled=config.get("memory_enabled", True),
            tools=config.get("tools", [])
        )


# Export classes for L3AGI integration
__all__ = ["ConversationalAgent", "TeamConversationalAgent", "create_conversational_agent"]
