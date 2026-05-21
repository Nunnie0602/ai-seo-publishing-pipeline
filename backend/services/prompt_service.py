from utils.constants import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def build_prompts(
    topic: str,
    keywords: list[str],
    target_audience: str,
    call_to_action: str,
) -> tuple[str, str]:
    keywords_text = "\n".join(f"- {kw}" for kw in keywords)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        topic=topic,
        keywords=keywords_text,
        target_audience=target_audience,
        call_to_action=call_to_action,
    )
    return SYSTEM_PROMPT, user_prompt
