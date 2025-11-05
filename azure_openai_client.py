"""
Azure OpenAI client for handling AI completions.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import aiohttp
from openai import AsyncAzureOpenAI
from azure.identity.aio import DefaultAzureCredential
from config import DefaultConfig

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI services."""

    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.config = DefaultConfig()
        # If an API key is provided, use it. Otherwise, attempt to acquire a token
        # using the environment's managed identity (DefaultAzureCredential) and
        # pass that token to the client. Note: Azure OpenAI accepts either an
        # api-key header or Bearer token. We'll supply the token as the api_key
        # parameter when a managed identity token is acquired.
        api_key = self.config.AZURE_OPENAI_API_KEY
        if not api_key:
            # Acquire token using Managed Identity / DefaultAzureCredential
            logger.info("No AZURE_OPENAI_API_KEY found — attempting to use managed identity via DefaultAzureCredential")
            try:
                # Acquire token for cognitive services scope
                credential = DefaultAzureCredential()
                # scope for Azure Cognitive Services
                scope = "https://cognitiveservices.azure.com/.default"
                # Use async get_token in the event loop when using this file in async context
                # We'll perform a synchronous token acquisition by running the coroutine
                # using asyncio loop here to keep initialization simple.
                import asyncio

                token = asyncio.get_event_loop().run_until_complete(credential.get_token(scope))
                api_key = token.token
            except Exception as e:
                logger.error(f"Failed to acquire managed identity token for Azure OpenAI: {e}")
                api_key = ''

        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT,
            api_key=api_key,
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