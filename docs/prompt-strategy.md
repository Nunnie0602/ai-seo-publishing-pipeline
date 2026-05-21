# Prompt Strategy

## System Prompt

```text
You are an SEO content writer.

Requirements:
- Return valid JSON only
- Generate semantic HTML
- Use <h1>, <h2>, <p>, <ul>
- Naturally include ALL provided keywords
- Avoid markdown
- No script tags
- Write coherent SEO-friendly content
```

## User Prompt Template

```text
Topic:
{topic}

Keywords:
{keywords}

Target Audience:
{target_audience}

Call To Action:
{call_to_action}
```

## Expected LLM Output

```json
{
  "title": "string",
  "content_html": "string"
}
```

## Stability Strategy

| Strategy | Purpose |
|---|---|
| JSON Schema Validation | 防止格式錯誤 |
| Retry Mechanism | 修復偶發不穩定輸出 |
| Low Temperature | 提升輸出穩定性 |
| Response Parsing | 確保 JSON-only response |
| HTML Sanitization | 避免危險 HTML |
