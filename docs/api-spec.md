# API Specification

## Base URL

```text
http://localhost:8000
```

## POST /generate

產生 SEO 文章並發布至 WordPress 草稿。

### Request

```json
{
  "topic": "Tainan Food Travel Guide",
  "keywords": ["Tainan food", "Taiwan travel"],
  "target_audience": "Foreign tourists visiting Taiwan",
  "call_to_action": "Book your Tainan trip today"
}
```

### Success Response (200)

```json
{
  "status": "success",
  "post_id": 123,
  "draft_url": "https://example.com/wp-admin/post.php?post=123&action=edit",
  "title": "Generated Title",
  "preview_html": "<h1>...</h1>"
}
```

### Error Response (4xx/5xx)

```json
{
  "status": "error",
  "message": "Generation failed. Please retry."
}
```

## Health Check

### GET /health

預設回傳 HTML 頁面，顯示 `app`、`wordpress`、`llm` 三項狀態；若 `Accept` 含 `application/json` 則回傳 JSON。

任一依賴（WordPress 或 LLM）非 `OK` 時 HTTP 狀態碼為 `503`。

```json
{
  "app": { "status": "OK" },
  "wordpress": { "status": "OK" },
  "llm": { "status": "OK" }
}
```

錯誤範例：

```json
{
  "app": { "status": "OK" },
  "wordpress": {
    "status": "ERROR",
    "message": "WordPress credentials are not configured"
  },
  "llm": { "status": "OK" }
}
```
