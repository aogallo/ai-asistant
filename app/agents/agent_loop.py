from typing import AsyncGenerator
import anthropic
from fastapi import Depends

from app.infrastructure.anthropic_client import get_anthropic_client
from app.utils.anthropic_stream_parser import ClaudeStreamParser
from app.agents.tool_setup import registry


class ClaudeAgentLoop:
    def __init__(
        self, client: anthropic.AsyncAnthropic = Depends(get_anthropic_client)
    ) -> None:
        self.client = client

    async def run(self, prompt: str) -> AsyncGenerator[str, None]:
        while True:
            messages = [{"role": "user", "content": prompt}]
            parser = ClaudeStreamParser()

            async with self.client.messages.stream(
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                model="claude-opus-4-6",
            ) as stream:
                tool_call_detected = None

                async for event in stream:
                    result = parser.process_event(event)

                    if not result:
                        continue

                    event_type, payload = result

                    # --- text stream ---
                    if event_type == "text":
                        yield payload

                    # --- tool call ---
                    if event_type == "tool_call":
                        tool_call_detected = payload

                # Exit streaming context first

            # ----- IF TOOL WAS REQUESTED -----
            if tool_call_detected:
                tool_name = tool_call_detected["name"]
                tool_input = tool_call_detected["input"]
                tool_id = tool_call_detected["id"]

                tool_result = registry.execute(tool_name, tool_input)

                messages.append(
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": tool_id,
                                "name": tool_name,
                                "input": tool_input,
                            }
                        ],
                    }
                )

                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": str(tool_result),
                            }
                        ],
                    }
                )

                continue
            break
