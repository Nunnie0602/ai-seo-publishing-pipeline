from models.schemas import LLMArticleOutput


def validate_llm_output(data: dict) -> LLMArticleOutput:
    return LLMArticleOutput.model_validate(data)
