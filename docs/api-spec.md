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

```json
{
  "status": "ok"
}
```
