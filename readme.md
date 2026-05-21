# AI SEO Content Publishing Pipeline

## Project Overview

本專案為一個 AI 驅動的 SEO 文章生成與 WordPress 發布流程系統。

使用者可透過前端輸入 SEO 發文需求，後端負責：

1. 將需求轉換為 Prompt
2. 呼叫 LLM 生成 HTML SEO 文章
3. 驗證與清理 AI 輸出內容
4. 發布至 WordPress 草稿文章

本專案重點：

- 穩定的 AI Output Handling
- SEO-Oriented Prompt Engineering
- WordPress 發文流程
- Error Handling 與系統韌性
- Production-Oriented 架構設計

---

# Core User Flow

```text
User Input
    ↓
Frontend Validation
    ↓
Backend API
    ↓
Prompt Builder
    ↓
LLM Generation
    ↓
JSON Validation
    ↓
HTML Sanitization
    ↓
WordPress Draft Publishing
    ↓
Frontend Result Display
```

---

# Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React / Vite |
| Backend | FastAPI |
| AI Service | Gemini API |
| CMS | WordPress REST API |
| HTML Sanitizer | bleach |
| Deployment | Docker Compose |
| Authentication | WordPress Application Password |

---

# Functional Requirements

# 1. SEO Content Input Form

## Description

使用者可透過前端輸入 SEO 發文需求。

## Required Fields

| Field | Type |
|---|---|
| Topic | string |
| Keywords | string[] |
| Target Audience | string |
| Call To Action | string |

## Example Request

```json
{
  "topic": "Tainan Food Travel Guide",
  "keywords": [
    "Tainan food",
    "Taiwan travel"
  ],
  "target_audience": "Foreign tourists visiting Taiwan",
  "call_to_action": "Book your Tainan trip today"
}
```

---

# 2. Frontend Validation

## Description

前端需於送出前進行基本驗證。

## Validation Rules

| Rule | Description |
|---|---|
| Topic Required | 不可為空 |
| Keywords Required | 至少一組 keyword |
| CTA Length Limit | 避免 prompt 過長 |
| Disable Duplicate Submit | Loading 時不可重複送出 |

## Error Examples

```text
Topic is required.
```

```text
Please enter at least one keyword.
```

---

# 3. Prompt Engineering Strategy

## Description

後端將結構化資料轉換為穩定的 SEO Prompt。

---

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

---

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

---

## Stability Strategy

| Strategy | Purpose |
|---|---|
| JSON Schema Validation | 防止格式錯誤 |
| Retry Mechanism | 修復偶發不穩定輸出 |
| Low Temperature | 提升輸出穩定性 |
| Response Parsing | 確保 JSON-only response |
| HTML Sanitization | 避免危險 HTML |

---

# 4. LLM Content Generation

## Description

後端呼叫 LLM 生成 SEO HTML 文章。

## Expected Output

```json
{
  "title": "string",
  "content_html": "string"
}
```

## Requirements

- JSON 格式固定
- HTML only
- 禁止 markdown
- 必須包含 semantic HTML structure

---

# 5. JSON Validation

## Description

於發布前驗證 LLM Output。

## Validation Rules

| Rule | Description |
|---|---|
| title Required | 必填 |
| content_html Required | 必填 |
| content_html Type | 必須為 string |
| Invalid Response Rejection | 拒絕 malformed response |

## Goal

避免 AI 不穩定輸出造成 downstream workflow failure。

---

# 6. HTML Sanitization

## Description

發布前清理 AI 生成 HTML。

## Sanitization Rules

- Remove script tags
- Remove unsafe attributes
- 僅允許 semantic HTML tags

## Library

```python
bleach
```

## Goal

降低 AI-generated HTML 帶來的安全與格式風險。

---

# 7. WordPress Draft Publishing

## Description

透過 WordPress REST API 建立 draft post。

## WordPress REST Endpoint

```text
POST /wp-json/wp/v2/posts
```

## Important Fields

| Field | Description |
|---|---|
| title | LLM 生成標題 |
| content | HTML 文章內容 |
| status | draft |

## Authentication

- Basic Authentication
- WordPress Application Password

## Example Response

```json
{
  "post_id": 123,
  "draft_url": "...",
  "status": "draft"
}
```

---

# 8. HTML Preview

## Description

前端顯示 HTML Preview。

## Goal

模擬 CMS workflow 並提升內容可視性。

---

# 9. Status Pipeline Display

## Description

前端需顯示 workflow progress state。

## Example

```text
Generating article...
Validating JSON...
Sanitizing HTML...
Publishing draft...
Completed
```

## Goal

提升 UX 與 workflow observability。

---

# 10. Error Handling

## Description

系統需處理常見失敗情境。

## Scenarios

| Scenario | Handling |
|---|---|
| Empty Input | Frontend validation |
| LLM Timeout | Retry + Error Response |
| Invalid JSON | Validation rejection |
| WordPress API Failure | Error feedback |
| HTML Validation Failure | Sanitization rejection |

## Example Messages

```text
Generation failed. Please retry.
```

```text
WordPress publishing failed.
```

---

# 11. System Logging

## Description

顯示輕量系統 log。

## Example Logs

```text
[INFO] Building prompt
[INFO] Calling Gemini API
[INFO] JSON validation passed
[INFO] HTML sanitized
[INFO] Publishing to WordPress
[INFO] Draft created successfully
```

## Goal

提升 observability 並展示工程流程。

---

# Non-Functional Requirements

## Reliability

- 防止 invalid AI output 進入 publishing flow
- API failure graceful handling

## Maintainability

- Service-layer architecture
- Modular backend design

## Extensibility

架構需支援未來擴充：

- Multiple AI Providers
- Scheduled Publishing
- Human Review Workflow

---

# Project Structure

```text
ai-seo-publishing-pipeline/
├── README.md
├── .gitignore
├── docker-compose.yml       
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── api-spec.md
│   ├── prompt-strategy.md
│   └── wordpress-setup.md    
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   └── generate_route.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── prompt_service.py
│   │   ├── validation_service.py
│   │   ├── sanitizer_service.py
│   │   └── wordpress_service.py   
│   ├── models/
│   │   └── schemas.py             
│   ├── utils/
│   │   ├── retry.py
│   │   ├── parser.py
│   │   └── constants.py
│   ├── config/
│   │   └── settings.py            <-- 內含 CORS 設定
│   └── logs/
│       └── app.log
│
├── frontend/                     
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.local.example
│   └── src/
│       ├── app/
│       │   ├── layout.js
│       │   └── page.js           
│       ├── components/
│       │   ├── SeoForm.jsx
│       │   ├── KeywordInput.jsx
│       │   ├── LoadingPipeline.jsx
│       │   ├── HtmlPreview.jsx
│       │   ├── ErrorAlert.jsx
│       │   └── SuccessToast.jsx
│       ├── services/
│       │   └── api.js
│       ├── hooks/
│       │   └── useGenerateArticle.js 
│       └── utils/
│           └── validators.js
│
└── screenshots/
    ├── frontend-form.png
    ├── loading-state.png
    ├── html-preview.png
    └── wordpress-draft.png
```

---

# API Design

## POST /generate

### Request

```json
{
  "topic": "Tainan Food Travel Guide",
  "keywords": [
    "Tainan food",
    "Taiwan travel"
  ],
  "target_audience": "Foreign tourists visiting Taiwan",
  "call_to_action": "Book your Tainan trip today"
}
```

---

## Response

```json
{
  "status": "success",
  "post_id": 123,
  "draft_url": "...",
  "title": "...",
  "preview_html": "..."
}
```

---

# Demo Focus

本專案重點：

- AI SEO workflow engineering
- Stable LLM integration
- Prompt engineering
- WordPress publishing automation
- Reliable content pipeline
- Production-oriented architecture


---

# Development Timeline & Engineering Priority

| Priority | Area | Score Weight | Estimated Effort | Completion Indicator |
|---|---|---|---|---|
| P0 | End-to-end workflow demo | 20% | 1.5 Days | 可完整建立 WordPress Draft |
| P0 | Prompt engineering + LLM integration | 25% | 1.5 Days | 穩定輸出 valid HTML JSON |
| P0 | Error handling + validation | 30% | 1.5 Days | Invalid input 不會 crash |
| P1 | WordPress integration understanding | 25% | 1 Day | REST API draft publishing 成功 |
| P1 | Frontend UX | Demo Critical | 1 Day | Loading/Error/Preview 正常 |
| P2 | Logging + observability | Bonus | 0.5 Day | 可展示 workflow logs |
| P2 | Docker setup + README | Bonus | 0.5 Day | 可快速本機啟動 |

---

# Suggested 6-Day Development Schedule

| Day | Focus | Deliverables | Success Criteria |
|---|---|---|---|
| Day 1 | Architecture setup | React + FastAPI + WordPress setup | Frontend/backend 可連線 |
| Day 2 | Prompt engineering | Prompt builder + Gemini integration | 穩定生成 JSON |
| Day 3 | Validation pipeline | Validation + Sanitization + Retry | Invalid output 可處理 |
| Day 4 | WordPress publishing | REST API publishing | Draft 出現在 WordPress |
| Day 5 | Frontend polish | Loading/Error/Preview | 完整 workflow 可操作 |
| Day 6 | Testing & demo prep | README + Demo script + Logs | Demo 可穩定展示 |

---

# Demo Success Indicators

| Category | Demo Goal |
|---|---|
| Frontend | SEO form submission 正常 |
| Backend | Prompt generation stable |
| LLM | Semantic HTML 穩定輸出 |
| Validation | Invalid response 不 crash |
| WordPress | Draft article 成功建立 |
| UX | Loading/Error state 清楚 |
| Architecture | Service separation 可解釋 |

---
# 開發策略重點

## 優先確保：

```text
Frontend
→ Backend
→ LLM
→ Validation
→ WordPress Draft
```

完整穩定可 demo。

---

## Demo 成功關鍵

- 不 crash
- Loading 明確
- Error message 清楚
- WordPress draft 可成功建立
- 能解釋 Prompt 與 Validation 設計原因