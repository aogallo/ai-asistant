import anthropic
from anthropic.types import Message

from app.core.config import settings
from app.core.logging import logger


class LLMService:
    def __init__(self) -> None:
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key
        )

    async def summarize(self, prompt: str) -> str:
        try:
            response: Message = await self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=500,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
            )

            message = response.content[0]

            return message.text

        except Exception as e:
            logger.error("llm_error", error=str(e))
            raise
