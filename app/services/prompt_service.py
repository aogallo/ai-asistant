def build_summary_prompt(text: str) -> str:
    return f"""
        You are an expert assistant.

        Summarize the following text clearly and concisely:

        {text}
        """
