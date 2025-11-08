"""Agent that processes user inputs."""

import logging

logger = logging.getLogger(__name__)


class Agent:
    """Basic agent for processing user inputs.

    Currently echoes messages. Will be extended with Claude API integration.
    """

    def __init__(self, system_prompt: str) -> None:
        """Initialize agent with a system prompt.

        Args:
            system_prompt: Initial system prompt to guide agent behavior.
        """
        self.system_prompt = system_prompt
        logger.info(f"Agent initialized with system prompt: {system_prompt}")

    def process_message(self, user_input: str) -> str:
        """Process user input and return response.

        Currently echoes the input. Future versions will call Claude API.

        Args:
            user_input: User message to process.

        Returns:
            Response message from agent.
        """
        logger.info(f"Processing message: {user_input}")
        # For now, echo the message
        return f"Echo: {user_input}"

    def send_welcome_message(self) -> str:
        """Generate welcome message on client connection.

        Returns:
            Welcome message for the client.
        """
        return "Welcome to Agentic Calculator. Ready to assist."
