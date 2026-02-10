class ClaudeStreamParser:
    def __init__(self) -> None:
        self._current_text = list[str] = []

    def process_event(self, event):
        """
        Returns new text chunk if available
        """

        if event.type == "content_block_delta":
            delta = event.delta

            # Only text deltas contain `.text`
            if hasattr(delta, "text") and delta.text:
                self._current_text.append(delta.text)
                return delta.text

        return None

    def get_full_text(self) -> str:
        return "".join(self._current_text)
