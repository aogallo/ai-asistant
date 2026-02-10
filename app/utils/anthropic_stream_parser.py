class StreamResult:
    def __init__(self) -> None:
        self.text_chunks: list[str] = []
        self.tool_call: dict | None = None


class ClaudeStreamParser:
    def __init__(self) -> None:
        self.result = StreamResult()

    def process_event(self, event):
        """
        Returns new text chunk if available
        """

        # --- TEXT AREA ---
        if event.type == "content_block_delta":
            delta = event.delta

            # Only text deltas contain `.text`
            if hasattr(delta, "text") and delta.text:
                self.result.text_chunks.append(delta.text)
                return ("text", delta.text)

        # --- TOOL TO CALL ---
        if event.type == "content_block_start":
            block = event.content_block_start

            if block.type == "tool_use":
                self.result.tool_call = {
                    "name": block.name,
                    "input": block.input,
                    "id": block.id,
                }

                return ("tool_call", self.result.tool_call)

        return None

    def get_full_text(self) -> str:
        return "".join(self._current_text)
