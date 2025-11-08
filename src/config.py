"""Configuration module for environment variables."""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_anthropic_api_key() -> str:
    """Get Anthropic API key from environment.

    Returns:
        API key string.

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment. " "Please set it in .env file."
        )
    return api_key
