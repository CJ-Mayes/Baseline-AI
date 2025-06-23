"""
OpenAI Bypass Module

This module provides functionality to bypass OpenAI API calls for testing and development purposes.
When enabled, it returns mock responses instead of making actual API calls to OpenAI.

Usage:
    Set BYPASS_OPENAI=true in your .env file to enable bypass mode.
    Set BYPASS_OPENAI=false or remove the line to disable bypass mode.
"""

import os
import random
from typing import List

# Mock responses for bypass mode
MOCK_RESPONSES: List[str] = [
    "This is a mock response from the bypass mode. The OpenAI API is currently disabled.",
    "I'm running in demo mode right now. In production, I would analyze your Wimbledon 2012 data.",
    "OpenAI integration is temporarily disabled. This is a test response.",
    "Demo mode active: I would normally query the Wimbledon dataset for you.",
    "Mock response: The AI agent is currently bypassed for testing purposes.",
    "Bypass mode: I would typically connect to your Tableau data source for real insights.",
    "Test mode enabled: No actual AI processing is happening right now.",
    "Demo response: In live mode, I'd provide detailed analysis of your tennis data.",
    "Bypass active: This simulates what the AI would say about your Wimbledon queries.",
    "Mock mode: The real AI would analyze match statistics, player performance, and trends."
]

def is_bypass_enabled() -> bool:
    """
    Check if OpenAI bypass mode is enabled.
    
    Returns:
        bool: True if BYPASS_OPENAI environment variable is set to 'true'
    """
    return os.getenv('BYPASS_OPENAI', 'false').lower() == 'true'

def get_mock_response() -> str:
    """
    Get a random mock response for bypass mode.
    
    Returns:
        str: A randomly selected mock response
    """
    return random.choice(MOCK_RESPONSES)

def get_bypass_status() -> dict:
    """
    Get the current bypass status and information.
    
    Returns:
        dict: Dictionary containing bypass status and available responses
    """
    return {
        "bypass_enabled": is_bypass_enabled(),
        "total_mock_responses": len(MOCK_RESPONSES),
        "description": "OpenAI API calls are bypassed when enabled"
    } 