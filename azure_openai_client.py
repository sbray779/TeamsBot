"""
Azure OpenAI client for handling AI completions.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from openai import AsyncAzureOpenAI
from config import DefaultConfig

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI services."""

    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.config = DefaultConfig()
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
            api_key=self.config.AZURE_OPENAI_API_KEY,
            api_version=self.config.AZURE_OPENAI_API_VERSION,
        )
        self.deployment_name = self.config.AZURE_OPENAI_DEPLOYMENT_NAME

    async def get_completion(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Get completion from Azure OpenAI.
        
        Args:
            prompt: The user's input prompt
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            The AI's response text
        """
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant integrated into Microsoft Teams. "
                              "Provide clear, concise, and helpful responses to user questions."
                },
                {"role": "user", "content": prompt}
            ]

            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error getting completion from Azure OpenAI: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."

    async def get_completion_with_context(
        self, 
        prompt: str, 
        conversation_history: list,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Get completion with conversation context.
        
        Args:
            prompt: The user's input prompt
            conversation_history: Previous messages in the conversation
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            The AI's response text
        """
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant integrated into Microsoft Teams. "
                              "Provide clear, concise, and helpful responses to user questions. "
                              "Consider the conversation context when responding."
                }
            ]
            
            # Add conversation history
            messages.extend(conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error getting completion with context from Azure OpenAI: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later."