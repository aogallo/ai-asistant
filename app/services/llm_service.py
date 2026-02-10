import anthropic

from app.core.config import settings
from app.core.logging import logger


class LLMService:
    def __init__(self) -> None:
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key
        )

    async def summarize(self, prompt: str) -> str:
        try:
            response = await self.client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=500,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text

        except Exception as e:
            logger.error("llm_error", error=str(e))
            raise
