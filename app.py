"""
Teams Bot with Azure OpenAI Integration

A Microsoft Teams bot that leverages Azure OpenAI for intelligent responses.
Includes infrastructure deployment templates and authentication setup.
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List
from aiohttp import web
from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    UserState,
    ConversationState,
    MemoryStorage,
    MessageFactory,
)
from botbuilder.core.adapter_with_error_handler import AdapterWithErrorHandler
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from botbuilder.core.conversation_state import ConversationState
from botbuilder.core.user_state import UserState
from config import DefaultConfig
from azure_openai_client import AzureOpenAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TeamsBot(ActivityHandler):
    """
    Teams bot that integrates with Azure OpenAI for intelligent responses.
    """

    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        self.conversation_state = conversation_state
        self.user_state = user_state
        self.openai_client = AzureOpenAIClient()

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Handle incoming message activities.
        """
        try:
            user_message = turn_context.activity.text
            logger.info(f"Received message: {user_message}")

            # Get response from Azure OpenAI
            response = await self.openai_client.get_completion(user_message)
            
            # Send response back to user
            await turn_context.send_activity(MessageFactory.text(response))

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await turn_context.send_activity(
                MessageFactory.text("Sorry, I encountered an error processing your request.")
            )

    async def on_members_added_activity(
        self, members_added: List[ChannelAccount], turn_context: TurnContext
    ):
        """
        Handle when new members are added to the conversation.
        """
        welcome_text = "Hello! I'm your AI assistant powered by Azure OpenAI. How can I help you today?"
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(MessageFactory.text(welcome_text))


def init_func(argv):
    """Initialize the bot application."""
    config = DefaultConfig()

    # Create adapter
    settings = ConfigurationBotFrameworkAuthentication(config)
    adapter = AdapterWithErrorHandler(settings)

    # Create storage and state
    memory_storage = MemoryStorage()
    conversation_state = ConversationState(memory_storage)
    user_state = UserState(memory_storage)

    # Create the bot
    bot = TeamsBot(conversation_state, user_state)

    # Listen for incoming requests
    async def messages(req: web.Request) -> web.Response:
        if "application/json" in req.headers["Content-Type"]:
            body = await req.json()
        else:
            return web.Response(status=415)

        activity = Activity().deserialize(body)
        auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

        response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        if response:
            return web.json_response(data=response.body, status=response.status)
        return web.Response(status=201)

    # Create the application
    app = web.Application()
    app.router.add_post("/api/messages", messages)

    # Listen for requests
    try:
        web.run_app(app, host="localhost", port=config.PORT)
    except Exception as e:
        raise e


if __name__ == "__main__":
    try:
        init_func(None)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        sys.exit(1)