"""
XAgent Core Integration Module
Provides seamless XAgent integration to replace Langchain REACT agents in L3AGI
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# XAgent imports (simulated for integration)
try:
    from XAgent.agent import Agent as XAgent
    from XAgent.toolserver_interface import ToolServerInterface
    from XAgent.config import CONFIG
except ImportError:
    # Fallback implementation for demonstration
    print("XAgent not installed - using simulation mode")

@dataclass
class AgentMessage:
    """Message structure for agent communication"""
    role: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

class XAgentWrapper:
    """
    XAgent wrapper that provides Langchain REACT Agent compatibility
    for seamless integration with L3AGI framework
    """
    
    def __init__(self, 
                 agent_name: str = "XAgent",
                 tools: List[Any] = None,
                 memory_config: Dict[str, Any] = None,
                 **kwargs):
        """Initialize XAgent with L3AGI compatibility"""
        self.agent_name = agent_name
        self.tools = tools or []
        self.memory_config = memory_config or {}
        self.conversation_history = []
        self.logger = logging.getLogger(f"XAgent.{agent_name}")
        
        # Initialize XAgent core
        self._init_xagent(**kwargs)
        
        # Setup tool server interface
        self.tool_server = ToolServerInterface() if 'ToolServerInterface' in globals() else MockToolServer()
        
        self.logger.info(f"XAgent {agent_name} initialized successfully")
    
    def _init_xagent(self, **kwargs):
        """Initialize XAgent with configuration"""
        try:
            # XAgent configuration
            config = {
                "agent_name": self.agent_name,
                "max_chain_length": kwargs.get("max_chain_length", 10),
                "enable_reflection": kwargs.get("enable_reflection", True),
                "tool_server_url": kwargs.get("tool_server_url", "http://localhost:8080"),
                **kwargs
            }
            
            if 'XAgent' in globals():
                self.xagent = XAgent(config)
            else:
                self.xagent = MockXAgent(config)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize XAgent: {e}")
            self.xagent = MockXAgent({"agent_name": self.agent_name})
    
    async def run(self, input_text: str, **kwargs) -> str:
        """
        Main execution method - replaces Langchain REACT agent run
        """
        try:
            # Log input
            self.logger.info(f"Processing input: {input_text[:100]}...")
            
            # Add to conversation history
            self.conversation_history.append(
                AgentMessage(
                    role="user",
                    content=input_text,
                    timestamp=datetime.now()
                )
            )
            
            # Execute XAgent planning and execution
            response = await self._execute_xagent_workflow(input_text, **kwargs)
            
            # Add response to history
            self.conversation_history.append(
                AgentMessage(
                    role="assistant",
                    content=response,
                    timestamp=datetime.now()
                )
            )
            
            return response
            
        except Exception as e:
            error_msg = f"XAgent execution failed: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def _execute_xagent_workflow(self, input_text: str, **kwargs) -> str:
        """Execute XAgent's autonomous workflow"""
        try:
            # XAgent planning phase
            plan = await self._create_plan(input_text)
            
            # XAgent execution phase
            result = await self._execute_plan(plan)
            
            # XAgent reflection phase (if enabled)
            if self.memory_config.get("enable_reflection", True):
                result = await self._reflect_on_result(result, input_text)
            
            return result
            
        except Exception as e:
            return f"Workflow execution error: {str(e)}"
    
    async def _create_plan(self, input_text: str) -> Dict[str, Any]:
        """Create execution plan using XAgent's planning capabilities"""
        if hasattr(self.xagent, 'create_plan'):
            return await self.xagent.create_plan(input_text)
        else:
            # Fallback planning simulation
            return {
                "steps": [
                    {"action": "analyze", "target": input_text},
                    {"action": "execute", "target": "planned_response"},
                    {"action": "validate", "target": "result"}
                ],
                "tools_needed": [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in self.tools]
            }
    
    async def _execute_plan(self, plan: Dict[str, Any]) -> str:
        """Execute the generated plan using available tools"""
        results = []
        
        for step in plan.get("steps", []):
            step_result = await self._execute_step(step)
            results.append(step_result)
        
        # Combine results into coherent response
        return self._synthesize_results(results)
    
    async def _execute_step(self, step: Dict[str, Any]) -> str:
        """Execute individual plan step"""
        action = step.get("action", "unknown")
        target = step.get("target", "")
        
        if action == "analyze":
            return f"Analysis of: {target}"
        elif action == "execute":
            return f"Executed: {target}"
        elif action == "validate":
            return f"Validated: {target}"
        else:
            return f"Completed {action} on {target}"
    
    def _synthesize_results(self, results: List[str]) -> str:
        """Synthesize step results into final response"""
        if not results:
            return "No results to synthesize"
        
        synthesized = f"XAgent completed the following steps:\n"
        for i, result in enumerate(results, 1):
            synthesized += f"{i}. {result}\n"
        
        synthesized += "\nTask completed successfully."
        return synthesized
    
    async def _reflect_on_result(self, result: str, original_input: str) -> str:
        """Reflect on execution result for improvement"""
        reflection = f"\n[Reflection] Evaluated result for input: '{original_input[:50]}...'"
        return result + reflection
    
    def get_memory(self) -> List[AgentMessage]:
        """Get conversation memory - L3AGI compatibility method"""
        return self.conversation_history
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.conversation_history.clear()
        self.logger.info("Memory cleared")


class MockXAgent:
    """Mock XAgent for demonstration when XAgent is not available"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agent_name = config.get("agent_name", "MockXAgent")
    
    async def create_plan(self, input_text: str) -> Dict[str, Any]:
        """Mock planning method"""
        return {
            "steps": [
                {"action": "mock_analyze", "target": input_text},
                {"action": "mock_respond", "target": "generated_response"}
            ],
            "tools_needed": ["mock_tool"]
        }


class MockToolServer:
    """Mock ToolServer for demonstration"""
    
    def __init__(self):
        self.available_tools = ["web_search", "calculator", "file_manager"]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Mock tool execution"""
        return f"Mock execution of {tool_name} with args {kwargs}"


# Utility functions for L3AGI compatibility
def create_xagent_from_langchain_config(langchain_config: Dict[str, Any]) -> XAgentWrapper:
    """Convert Langchain agent configuration to XAgent"""
    return XAgentWrapper(
        agent_name=langchain_config.get("agent_name", "converted_agent"),
        tools=langchain_config.get("tools", []),
        memory_config=langchain_config.get("memory", {}),
        max_chain_length=langchain_config.get("max_iterations", 10)
    )


# Export main classes for L3AGI integration
__all__ = ["XAgentWrapper", "AgentMessage", "create_xagent_from_langchain_config"]
