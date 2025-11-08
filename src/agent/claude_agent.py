"""Claude Agent implementation using Anthropic SDK."""

import logging

from anthropic import Anthropic
from anthropic.types import TextBlock

logger = logging.getLogger(__name__)


class ClaudeAgent:
    """Agent backed by Claude using the Anthropic SDK.

    Maintains conversation context across multiple messages.
    """

    def __init__(self, system_prompt: str, api_key: str) -> None:
        """Initialize agent with system prompt and API key.

        Args:
            system_prompt: Initial system prompt to guide agent behavior.
            api_key: Anthropic API key for authentication.
        """
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=api_key)
        self.conversation_history: list[dict[str, str]] = []
        logger.info(f"ClaudeAgent initialized with system prompt: {system_prompt}")

    def process_message(self, user_input: str) -> str:
        """Process user input and return Claude's response.

        Args:
            user_input: User message to send to Claude.

        Returns:
            Claude's response text.
        """
        logger.info(f"Processing message: {user_input}")

        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Get response from Claude
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=self.system_prompt,
            messages=self.conversation_history,  # type: ignore[arg-type]
        )

        # Extract response text from first content block
        first_block = response.content[0]
        if isinstance(first_block, TextBlock):
            response_text = first_block.text
        else:
            response_text = str(first_block)

        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response_text})

        logger.info(f"Claude response: {response_text}")
        return response_text

    def send_welcome_message(self) -> str:
        """Generate welcome message on client connection.

        Returns:
            Welcome message for the client.
        """
        return "Welcome to Agentic Calculator. I'm Claude, ready to assist."
