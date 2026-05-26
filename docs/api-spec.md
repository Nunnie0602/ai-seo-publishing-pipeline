# API Specification

## Base URL

```text
http://localhost:8000
```

## POST /generate

產生 SEO 文章並發布至 WordPress 草稿。

**內部韌性行為**（對外 API 契約不變）：

- Gemini 單次請求逾時：`LLM_REQUEST_TIMEOUT_SECONDS`（預設 60s）
- LLM 可重試錯誤（timeout、429、5xx、JSON 解析錯誤等）最多 `LLM_MAX_RETRIES` 次；401/400/403 不重試
- WordPress 發布對 502/503/504、連線逾時最多 `WP_MAX_RETRIES` 次；401/400/403 不重試
- 重試耗盡後仍回傳既有 400/500 與 `detail.message` 格式

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
