from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    keywords: list[str] = Field(..., min_length=1)
    target_audience: str = Field(..., min_length=1)
    call_to_action: str = Field(..., min_length=1, max_length=200)


class LLMArticleOutput(BaseModel):
    title: str = Field(..., min_length=1, description="WordPress post title (metadata)")
    content_html: str = Field(
        ...,
        min_length=1,
        description="Article body HTML; no <h1>, starts with intro paragraph",
    )


class GenerateSuccessResponse(BaseModel):
    status: str = "success"
    post_id: int
    draft_url: str
    title: str
    preview_html: str


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
