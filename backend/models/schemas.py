from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    keywords: list[str] = Field(..., min_length=1)
    target_audience: str = Field(..., min_length=1)
    call_to_action: str = Field(..., min_length=1, max_length=500)


class LLMArticleOutput(BaseModel):
    title: str = Field(..., min_length=1)
    content_html: str = Field(..., min_length=1)


class GenerateSuccessResponse(BaseModel):
    status: str = "success"
    post_id: int
    draft_url: str
    title: str
    preview_html: str


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
