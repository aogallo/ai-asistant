from pydantic import BaseModel


class SummarizeResponse(BaseModel):
    text: str


class SummarizeRequest(BaseModel):
    text: str
