# AI SEO Content Publishing Pipeline

## Project Overview

本專案為一個 AI 驅動的 SEO 文章生成與 WordPress 發布流程系統。

使用者可透過前端輸入 SEO 發文需求，後端負責：

1. 將需求轉換為 Prompt
2. 呼叫 LLM 生成 HTML SEO 文章
3. 驗證與清理 AI 輸出內容
4. 發布至 WordPress 草稿文章

本專案重點：穩定的 AI Output Handling、SEO-Oriented Prompt Engineering、WordPress 發文流程、Error Handling 與系統韌性。

---

## Getting Started

### 必要條件

| 項目 | 版本 / 說明 |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| WordPress | 5.6+，REST API 與 Application Password 已啟用 |
| Gemini API Key | [Google AI Studio](https://aistudio.google.com/) 取得 |

<a id="env-vars"></a>

### 環境變數

複製 `backend/.env.example` 為 `backend/.env` 並填入：

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
WORDPRESS_URL=http://your-wordpress-site.local
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
CORS_ORIGINS=http://localhost:5173
LLM_TEMPERATURE=0.2
LLM_MAX_RETRIES=3
```

| 說明 | 細節 |
|---|---|
| 載入路徑 | 後端**固定讀取** `backend/.env`（不受執行目錄影響）；修改後需重啟 uvicorn |
| Docker | `docker compose` 使用**根目錄** `.env`（可參考 `.env.example`） |
| 建議模型 | 使用 `gemini-2.5-flash`；實測 `gemini-2.0-flash` 免費配額已用盡（429） |

WordPress Application Password 設定見 [docs/wordpress-setup.md](docs/wordpress-setup.md)。

### 安裝依賴

```bash
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

<a id="start-local"></a>

### 啟動服務（本機）

**後端**（終端機 1）：

```bash
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

**前端**（終端機 2）：

```bash
cd frontend
npm run dev
```

- 後端：`http://127.0.0.1:8000`
- 前端：`http://localhost:5173`

### Docker Compose（可選）

```bash
docker compose up --build
```

### 健康檢查

瀏覽器開啟 [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)，確認 App、WordPress、LLM 三項皆為 **OK**。

命令列（JSON）：

```bash
python -c "import httpx; r=httpx.get('http://127.0.0.1:8000/health', headers={'Accept':'application/json'}); print(r.status_code, r.json())"
```

任一依賴非 OK 時 HTTP 狀態碼為 `503`。詳細規格見 [docs/api-spec.md](docs/api-spec.md)。

<a id="troubleshooting"></a>

### 常見啟動問題

| 現象 | 處置 |
|---|---|
| Gemini 429 | 確認 `GEMINI_MODEL=gemini-2.5-flash`；檢查 [AI Studio](https://aistudio.google.com/) 用量 |
| WordPress 401 | 見 [docs/wordpress-setup.md](docs/wordpress-setup.md) Troubleshooting |
| CORS 錯誤 | 確認 `CORS_ORIGINS` 含前端實際 origin（如 `http://localhost:5173`） |

---

## Testing

| 類型 | 說明 |
|---|---|
| Full-Stack Live | `python full-stack-testcases/run_full_stack_live_test.py`（真實 Gemini + WordPress，會消耗配額） |
| Backend Mock | `backend/test/run_*_mock_test.py` |
| 最新報告 | `full-stack-testcases/test_result_full_stack_live_*.md` |

自動化測試、手動 UI 驗證、WordPress 草稿檢視與測試檢查清單，見 **[docs/testguide.md](docs/testguide.md)**。

---

## Core User Flow

```text
User Input → Frontend Validation → Backend API → Prompt Builder
  → LLM Generation → JSON Validation → HTML Sanitization
  → WordPress Draft Publishing → Frontend Result Display
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React / Vite（En / 繁中 i18n） |
| Backend | FastAPI |
| AI Service | Gemini API（`gemini-2.5-flash`，temperature 0.2，最多 3 次 retry） |
| CMS | WordPress REST API |
| HTML Sanitizer | bleach |
| Deployment | Docker Compose |
| Authentication | WordPress Application Password |

---

## Functional Requirements

### 1. SEO Content Input Form

| Field | Type | UI 說明 |
|---|---|---|
| Topic | string | 必填 |
| Keywords | string[] | 必填；表單為**每行一個關鍵字** |
| Target Audience | string | 必填 |
| Call To Action | string | 必填；最多 200 字元 |

前端支援 **En / 繁中** 切換（`LangToggle`）。

**API 請求範例**：

```json
{
  "topic": "Tainan Food Travel Guide",
  "keywords": ["Tainan food", "Taiwan travel"],
  "target_audience": "Foreign tourists visiting Taiwan",
  "call_to_action": "Book your Tainan trip today"
}
```

### 2. Frontend Validation

| Rule | Description |
|---|---|
| 必填欄位 | Topic、Keywords、Target Audience、Call To Action 不可為空 |
| CTA 長度 | 最多 200 字元 |
| 重複送出 | Loading 時禁用按鈕 |

**錯誤訊息範例**（依語系）：

```text
Topic is empty. Please enter the required text.
```

```text
主題為空。請輸入必填文字。
```

### 3. Prompt Engineering

詳見 [docs/prompt-strategy.md](docs/prompt-strategy.md)。System / User Prompt 與 `backend/utils/constants.py` 一致。

### 4–5. LLM 生成與 JSON 驗證

**預期 LLM 輸出**：

```json
{
  "title": "string",
  "content_html": "string"
}
```

| 驗證 | 說明 |
|---|---|
| title / content_html | 必填且為非空字串 |
| 格式錯誤 | 拒絕進入發布流程 |

穩定策略：JSON Schema、Retry、低 temperature、Response Parsing、HTML Sanitization。

### 6. HTML Sanitization

使用 `bleach`。允許標籤：

`h1`, `h2`, `h3`, `p`, `ul`, `ol`, `li`, `strong`, `em`, `a`, `br`

移除 `<script>` 與不安全屬性。

### 7. WordPress Draft Publishing

```text
POST {WORDPRESS_URL}/wp-json/wp/v2/posts
```

認證：Basic Auth + Application Password。詳見 [docs/wordpress-setup.md](docs/wordpress-setup.md)。

### 8–9. HTML Preview 與 Pipeline

Pipeline 步驟（英文 UI）：

```text
Generating article... → Validating JSON... → Sanitizing HTML...
Publishing draft... → Completed
```

### 10. Error Handling

| Scenario | Handling |
|---|---|
| 空欄位 | 前端驗證 |
| LLM 失敗 | Retry + 500 錯誤訊息 |
| JSON 無效 | 400 驗證拒絕 |
| WordPress 失敗 | `WordPress publishing failed.` |

### 11. System Logging

範例：`[INFO] Building prompt` → `Calling Gemini API` → `JSON validation passed` → `HTML sanitized` → `Publishing to WordPress` → `Draft created successfully`

日誌檔：`backend/logs/app.log`

---

## Project Structure

```text
ai-seo-publishing-pipeline/
├── README.md
├── revision.md
├── .gitignore
├── docker-compose.yml
├── .env.example                 # Docker 用
├── docs/
│   ├── architecture.md
│   ├── api-spec.md
│   ├── prompt-strategy.md
│   ├── wordpress-setup.md
│   └── testguide.md
├── full-stack-testcases/        # Full-Stack Live 測試
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/generate_route.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── prompt_service.py
│   │   ├── validation_service.py
│   │   ├── sanitizer_service.py
│   │   ├── wordpress_service.py
│   │   └── health_service.py
│   ├── models/schemas.py
│   ├── utils/{retry,parser,constants}.py
│   ├── config/settings.py
│   ├── test/                    # Mock 測試腳本
│   └── logs/app.log
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.local.example
│   └── src/
│       ├── main.jsx
│       ├── app/{layout,page}.jsx
│       ├── components/
│       │   ├── SeoForm.jsx, KeywordInput.jsx, LangToggle.jsx
│       │   ├── LoadingPipeline.jsx, HtmlPreview.jsx
│       │   └── ErrorAlert.jsx, SuccessToast.jsx
│       ├── i18n/{translations.js,LanguageContext.jsx}
│       ├── services/api.js
│       ├── hooks/useGenerateArticle.js
│       └── utils/validators.js
└── screenshots/                 # 待補截圖
    ├── frontend-form.png        # (planned)
    ├── loading-state.png
    ├── html-preview.png
    └── wordpress-draft.png
```

---

## API Design

Base URL：`http://localhost:8000`。完整規格見 [docs/api-spec.md](docs/api-spec.md)。

### POST /generate

**Request**：見上方 SEO 表單 JSON 範例。

**Success (200)**：

```json
{
  "status": "success",
  "post_id": 123,
  "draft_url": "https://example.com/?p=123",
  "title": "Generated Title",
  "preview_html": "<h1>...</h1>"
}
```

**Error (400 / 500)**：FastAPI 回傳 `detail` 物件：

```json
{
  "detail": {
    "status": "error",
    "message": "Generation failed. Please retry."
  }
}
```

### GET /health

- 預設：HTML 狀態頁（App / WordPress / LLM）
- `Accept: application/json`：JSON 格式
- 任一依賴 ERROR → HTTP `503`

---

## Related Documentation

| 文件 | 說明 |
|---|---|
| [docs/architecture.md](docs/architecture.md) | 系統架構 |
| [docs/api-spec.md](docs/api-spec.md) | API 規格 |
| [docs/prompt-strategy.md](docs/prompt-strategy.md) | Prompt 策略 |
| [docs/wordpress-setup.md](docs/wordpress-setup.md) | WordPress 設定 |
| [docs/testguide.md](docs/testguide.md) | Full-Stack 與手動測試流程 |

