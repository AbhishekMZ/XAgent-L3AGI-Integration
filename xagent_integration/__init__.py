"""
XAgent Integration Package
Provides XAgent integration components for L3AGI framework
"""

from .xagent_core import XAgentWrapper, AgentMessage, create_xagent_from_langchain_config
from .l3agi_compatibility import (
    ConversationalXAgent,
    DialogueAgentWithToolsXAgent, 
    XAgentTestInterface,
    LangchainToXAgentMigrator
)

__version__ = "1.0.0"
__author__ = "AbhishekMZ"
__description__ = "XAgent integration for L3AGI framework"

__all__ = [
    "XAgentWrapper",
    "AgentMessage", 
    "create_xagent_from_langchain_config",
    "ConversationalXAgent",
    "DialogueAgentWithToolsXAgent",
    "XAgentTestInterface",
    "LangchainToXAgentMigrator"
]
