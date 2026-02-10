from collections.abc import AsyncGenerator
import anthropic
from fastapi import Depends
from app.infrastructure.anthropic_client import get_anthropic_client
from app.utils.anthropic_stream_parser import ClaudeStreamParser


class LLMStreamService:
    def __init__(
        self, client: anthropic.AsyncAnthropic = Depends(get_anthropic_client)
    ) -> None:
        self.client = client

    async def stream_completation(
        self, prompt: str
    ) -> AsyncGenerator[str, None]:
        parser = ClaudeStreamParser

        async with self.client.message.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for event in stream:
                chunk = parser.process_event(event=event)

                if chunk:
                    yield chunk
