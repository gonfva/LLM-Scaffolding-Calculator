"""Claude Agent implementation using Anthropic SDK."""

import logging
from typing import Any

from anthropic import Anthropic
from anthropic.types import TextBlock, ToolUseBlock

from src.agent.tool_executor import ToolExecutor
from src.agent.tools import TOOLS
from src.agent.ui_state import UIState

logger = logging.getLogger(__name__)


class ClaudeAgent:
    """Agent backed by Claude using the Anthropic SDK.

    Maintains conversation context across multiple messages and handles tool use.
    """

    def __init__(self, system_prompt: str, api_key: str) -> None:
        """Initialize agent with system prompt and API key.

        Args:
            system_prompt: Initial system prompt to guide agent behavior.
            api_key: Anthropic API key for authentication.
        """
        self.system_prompt = system_prompt
        self.client = Anthropic(api_key=api_key)
        self.conversation_history: list[dict[str, Any]] = []
        self.ui_state = UIState()
        self.tool_executor = ToolExecutor(self.ui_state)
        logger.info(f"ClaudeAgent initialized with system prompt: {system_prompt}")

    def process_message(self, user_input: str) -> str:
        """Process user input and return Claude's response.

        Handles tool use - Claude can call tools to modify UI state.

        Args:
            user_input: User message to send to Claude.

        Returns:
            Claude's response text.
        """
        logger.info(f"Processing message: {user_input}")

        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Agentic loop: keep asking Claude until it stops using tools
        final_response = ""
        max_iterations = 10  # Prevent infinite loops

        for iteration in range(max_iterations):
            logger.info(f"Iteration {iteration + 1}")

            # Get response from Claude
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=self.system_prompt,
                tools=TOOLS,  # type: ignore[arg-type]
                messages=self.conversation_history,  # type: ignore[arg-type]
            )

            # Process response content blocks
            assistant_content: list[dict[str, Any]] = []
            tool_calls: list[dict[str, Any]] = []
            tool_calls_made = False

            for block in response.content:
                if isinstance(block, TextBlock):
                    final_response = block.text
                    assistant_content.append({"type": "text", "text": block.text})
                elif isinstance(block, ToolUseBlock):
                    tool_calls_made = True
                    assistant_content.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

                    # Execute the tool and collect results
                    tool_result = self.tool_executor.execute_tool(
                        block.name, block.input
                    )
                    logger.info(f"Tool result: {tool_result}")

                    tool_calls.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": tool_result,
                        }
                    )

            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_content})

            # If tool calls were made, add all tool results in a single user message
            if tool_calls:
                self.conversation_history.append({"role": "user", "content": tool_calls})

            # If no tool calls were made, we're done
            if not tool_calls_made:
                break

        logger.info(f"Final response: {final_response}")
        return final_response

    def send_welcome_message(self) -> str:
        """Generate welcome message on client connection.

        Returns:
            Welcome message for the client.
        """
        return "Welcome to Agentic Calculator. I'm Claude, ready to assist."

    def get_ui_state(self) -> dict[str, Any]:
        """Get current UI state.

        Returns:
            Dictionary representing the current UI elements.
        """
        return self.ui_state.get_state()

    def reset_ui(self) -> None:
        """Reset UI state for a new session."""
        self.ui_state.reset()
