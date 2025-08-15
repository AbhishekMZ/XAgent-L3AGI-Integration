"""
L3AGI Compatibility Layer for XAgent Integration
Provides seamless replacement of Langchain REACT agents with XAgent
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from .xagent_core import XAgentWrapper, AgentMessage

class ConversationalXAgent(XAgentWrapper):
    """
    XAgent wrapper for conversational.py replacement
    Maintains L3AGI conversational interface while using XAgent backend
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_context = []
        self.system_prompt = kwargs.get("system_prompt", "You are a helpful AI assistant.")
    
    async def chat(self, message: str, context: List[Dict] = None) -> str:
        """Main chat method for conversational interface"""
        if context:
            self.conversation_context.extend(context)
        
        # Format conversation for XAgent
        formatted_input = self._format_conversation_input(message)
        
        # Execute with XAgent
        response = await self.run(formatted_input)
        
        return self._format_conversation_output(response)
    
    def _format_conversation_input(self, message: str) -> str:
        """Format conversation input for XAgent processing"""
        context_str = ""
        if self.conversation_context:
            context_str = "Previous conversation:\n"
            for msg in self.conversation_context[-5:]:  # Last 5 messages
                context_str += f"- {msg.get('role', 'user')}: {msg.get('content', '')}\n"
        
        return f"{self.system_prompt}\n\n{context_str}\nCurrent message: {message}"
    
    def _format_conversation_output(self, response: str) -> str:
        """Format XAgent response for L3AGI conversation interface"""
        # Remove XAgent internal formatting if present
        if "[Reflection]" in response:
            response = response.split("[Reflection]")[0].strip()
        
        return response


class DialogueAgentWithToolsXAgent(XAgentWrapper):
    """
    XAgent wrapper for dialogue_agent_with_tools.py replacement
    Provides tool-enabled dialogue capabilities using XAgent
    """
    
    def __init__(self, name: str, tools: List[Any], **kwargs):
        super().__init__(agent_name=name, tools=tools, **kwargs)
        self.agent_role = kwargs.get("role", "assistant")
        self.agent_description = kwargs.get("description", f"AI agent {name}")
    
    async def send(self, message: str, **kwargs) -> str:
        """Send message method compatible with L3AGI dialogue agent interface"""
        tool_context = self._prepare_tool_context()
        
        enhanced_message = f"""
Agent Role: {self.agent_role}
Description: {self.agent_description}
Available Tools: {', '.join([str(tool) for tool in self.tools])}

User Message: {message}
"""
        
        response = await self.run(enhanced_message, **kwargs)
        return self._format_dialogue_response(response)
    
    def _prepare_tool_context(self) -> str:
        """Prepare context about available tools"""
        if not self.tools:
            return "No tools available."
        
        tool_descriptions = []
        for tool in self.tools:
            if hasattr(tool, 'description'):
                tool_descriptions.append(f"- {tool.__name__}: {tool.description}")
            else:
                tool_descriptions.append(f"- {str(tool)}")
        
        return "Available tools:\n" + "\n".join(tool_descriptions)
    
    def _format_dialogue_response(self, response: str) -> str:
        """Format response for dialogue agent interface"""
        return f"[{self.agent_name}]: {response}"
    
    def describe(self) -> str:
        """Get agent description - L3AGI compatibility"""
        return f"{self.agent_name} ({self.agent_role}): {self.agent_description}"


class XAgentTestInterface:
    """
    Test interface for test.py replacement
    Provides testing capabilities for XAgent integration
    """
    
    def __init__(self):
        self.test_agents = {}
        self.test_results = []
        self.logger = logging.getLogger("XAgent.TestInterface")
    
    def create_test_agent(self, name: str, config: Dict[str, Any]) -> XAgentWrapper:
        """Create agent for testing"""
        agent = XAgentWrapper(agent_name=name, **config)
        self.test_agents[name] = agent
        return agent
    
    async def run_test_suite(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "test_details": []
        }
        
        for i, test_case in enumerate(test_cases):
            result = await self._run_single_test(test_case, i)
            results["test_details"].append(result)
            
            if result["status"] == "passed":
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        self.test_results.append(results)
        return results
    
    async def _run_single_test(self, test_case: Dict[str, Any], test_id: int) -> Dict[str, Any]:
        """Run single test case"""
        try:
            agent_name = test_case.get("agent", "default_test_agent")
            input_text = test_case.get("input", "")
            expected_output = test_case.get("expected", None)
            
            # Get or create test agent
            if agent_name not in self.test_agents:
                self.test_agents[agent_name] = XAgentWrapper(agent_name=agent_name)
            
            agent = self.test_agents[agent_name]
            
            # Run test
            start_time = datetime.now()
            response = await agent.run(input_text)
            end_time = datetime.now()
            
            # Evaluate result
            status = "passed"
            if expected_output and expected_output not in response:
                status = "failed"
            
            return {
                "test_id": test_id,
                "agent": agent_name,
                "input": input_text,
                "output": response,
                "expected": expected_output,
                "status": status,
                "duration": (end_time - start_time).total_seconds()
            }
        
        except Exception as e:
            return {
                "test_id": test_id,
                "agent": test_case.get("agent", "unknown"),
                "input": test_case.get("input", ""),
                "output": f"Error: {str(e)}",
                "expected": test_case.get("expected", None),
                "status": "failed",
                "duration": 0
            }
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all test results"""
        if not self.test_results:
            return {"message": "No tests run yet"}
        
        latest_results = self.test_results[-1]
        return {
            "latest_test_run": latest_results,
            "total_test_sessions": len(self.test_results),
            "overall_success_rate": latest_results["passed"] / latest_results["total_tests"] * 100
        }


# Migration utilities
class LangchainToXAgentMigrator:
    """Utility class for migrating from Langchain to XAgent"""
    
    @staticmethod
    def migrate_agent_config(langchain_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Langchain agent configuration to XAgent format"""
        xagent_config = {
            "agent_name": langchain_config.get("name", "migrated_agent"),
            "tools": langchain_config.get("tools", []),
            "memory_config": {
                "enable_reflection": langchain_config.get("enable_memory", True),
                "max_history": langchain_config.get("max_memory_length", 100)
            },
            "max_chain_length": langchain_config.get("max_iterations", 10)
        }
        
        # Handle Langchain-specific configurations
        if "llm" in langchain_config:
            xagent_config["llm_config"] = langchain_config["llm"]
        
        if "prompt_template" in langchain_config:
            xagent_config["system_prompt"] = langchain_config["prompt_template"]
        
        return xagent_config
    
    @staticmethod
    def create_replacement_imports() -> str:
        """Generate replacement import statements"""
        return '''
# XAgent replacements for Langchain imports
from xagent_integration.l3agi_compatibility import (
    ConversationalXAgent as ConversationalReActAgent,
    DialogueAgentWithToolsXAgent as DialogueAgentWithTools,
    XAgentTestInterface as TestInterface
)
from xagent_integration.xagent_core import XAgentWrapper as Agent
'''


# Export compatibility classes
__all__ = [
    "ConversationalXAgent",
    "DialogueAgentWithToolsXAgent", 
    "XAgentTestInterface",
    "LangchainToXAgentMigrator"
]
