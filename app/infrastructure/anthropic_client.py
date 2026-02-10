import anthropic

from app.core.config import Settings


def get_anthropic_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=Settings.anthropic_api_key)
