# WordPress Setup

## Prerequisites

- WordPress 5.6+ with REST API enabled
- Application Passwords enabled (Users → Profile → Application Passwords)

## Authentication

使用 **Basic Authentication** 搭配 Application Password：

```text
Authorization: Basic base64(username:application_password)
```

## REST Endpoint

```text
POST {WORDPRESS_URL}/wp-json/wp/v2/posts
```

## Request Body

```json
{
  "title": "Article Title",
  "content": "<h1>HTML content</h1>",
  "status": "draft"
}
```

## Environment Variables

```env
WORDPRESS_URL=https://your-site.example.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

## Troubleshooting

| Issue | Solution |
|---|---|
| 401 Unauthorized | 確認 Application Password 正確 |
| 403 Forbidden | 確認使用者有 `edit_posts` 權限 |
| REST API disabled | 檢查 permalink 與 REST API 外掛設定 |
