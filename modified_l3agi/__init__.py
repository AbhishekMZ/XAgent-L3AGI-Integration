"""
Modified L3AGI Components with XAgent Integration
Enhanced L3AGI components powered by XAgent autonomous capabilities
"""

from .conversational import ConversationalAgent, TeamConversationalAgent, create_conversational_agent
from .dialogue_agent_with_tools import DialogueAgentWithTools, TeamDialogueAgent, ToolManager, create_dialogue_agent

__version__ = "1.0.0"
__author__ = "AbhishekMZ"
__description__ = "Enhanced L3AGI components with XAgent integration"

__all__ = [
    "ConversationalAgent",
    "TeamConversationalAgent", 
    "create_conversational_agent",
    "DialogueAgentWithTools",
    "TeamDialogueAgent",
    "ToolManager",
    "create_dialogue_agent"
]
