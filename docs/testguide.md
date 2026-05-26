# Full-Stack 測試指南

本指南說明如何執行真實 API 端到端測試、Backend Mock 錯誤處理驗證，並在 WordPress 檢視生成結果。

> 環境準備、依賴安裝、服務啟動與健康檢查，請先完成 **[README.md — Getting Started](../README.md#getting-started)**。  
> 最後驗證日期：2026-05-26

---

## 1. 自動化測試

### 1.1 Full-Stack Live

於**專案根目錄**執行本機 Full-Stack Live 測試腳本（需已完成 README 環境設定與 `GET /health` 三項 OK；會消耗 Gemini 配額並建立 WordPress 草稿）。腳本與產出檔案為本機測試資源，**未納入 Git 版控**。

若前後端已啟動，可設定環境變數後一併驗證 HTTP 連線：

```powershell
# PowerShell
$env:BACKEND_BASE_URL="http://127.0.0.1:8000"
$env:FRONTEND_BASE_URL="http://127.0.0.1:5173"
# 執行本機 Full-Stack Live 測試腳本
```

```bash
# Bash
BACKEND_BASE_URL=http://127.0.0.1:8000 FRONTEND_BASE_URL=http://127.0.0.1:5173 \
  # 執行本機 Full-Stack Live 測試腳本
```

### 1.2 測試範圍（Full-Stack Live）

| 階段 | 說明 |
|---|---|
| T01–T04 | 前端 mock 表單 → API 欄位轉換 → schema 驗證 |
| T05–T08 | 環境變數、LLM / WordPress health check |
| T09–T14 | **真實 Gemini API** → JSON 驗證 → HTML 消毒 → WordPress 草稿 |
| T15–T16 | 可選：已啟動的前後端 HTTP 連線 |
| T18 | 測試後 Gemini 配額探測 |

> **注意**：T09 會消耗 Gemini API 配額並在 WordPress 建立真實草稿，請勿在 CI 中頻繁執行。

### 1.3 測試產出

| 產出 | 內容 |
|---|---|
| Full-Stack Live 報告 | 測試摘要與通過／失敗紀錄（本機產出，未納入版控） |
| LLM / API / WP 快照 | JSON 輸出與 `/generate` 回應（本機產出，未納入版控） |
| Backend Mock（§1.4） | 終端驗證輸出；涵蓋 LLM 逾時／分類 retry、WP 503 重試 |

### 1.4 Backend Mock — 錯誤處理（LLM 逾時／分類 retry、WP retry）

於 `backend` 目錄驗證 **§3.4 / §3.5** 行為，**不需**真實 Gemini API 與 WordPress：

```bash
cd backend
python -c "
from utils.retry_policy import is_llm_retryable, is_wp_retryable
import httpx, json

assert is_llm_retryable(TimeoutError('t'))
assert is_llm_retryable(json.JSONDecodeError('x', 'y', 0))
assert not is_llm_retryable(RuntimeError('unexpected'))
assert is_wp_retryable(httpx.TimeoutException('timeout'))
req = httpx.Request('POST', 'https://example.com')
assert is_wp_retryable(httpx.HTTPStatusError('503', request=req, response=httpx.Response(503, request=req)))
assert not is_wp_retryable(httpx.HTTPStatusError('401', request=req, response=httpx.Response(401, request=req)))
print('Backend Mock (retry policy): OK')
"
```

| 驗證項 | 預期 |
|---|---|
| `TimeoutError` / `JSONDecodeError` | `is_llm_retryable` → True |
| 未知 `RuntimeError` | `is_llm_retryable` → False |
| `httpx.TimeoutException` / HTTP 503 | `is_wp_retryable` → True |
| HTTP 401 | `is_wp_retryable` → False |

實作位置：`utils/retry_policy.py`、`services/llm_service.py`（逾時 + 分類 retry）、`services/wordpress_service.py`（有限 retry）。若本機另有 mock 單元測試腳本，可一併執行；通過時終端應顯示全部 OK。

---

## 2. 手動 UI 測試（前端 → WordPress）

### 2.1 開啟前端表單

1. 確認 [README — 啟動服務](../README.md#start-local) 已完成
2. 瀏覽器前往 [http://localhost:5173](http://localhost:5173)
3. 確認頁面載入 SEO 文章生成表單

### 2.2 填寫表單

| 欄位 | 範例值 |
|---|---|
| Topic | 高雄美食旅遊指南 |
| Keywords | 高雄美食、台灣旅遊（每行一個） |
| Target Audience | 來台觀光的旅客 |
| Call To Action | 立即規劃你的高雄之旅 |

### 2.3 送出並觀察 Pipeline

點擊生成按鈕後，前端應依序顯示：

```text
Generating article... → Validating JSON... → Sanitizing HTML...
Publishing draft... → Completed
```

成功後頁面會顯示：

- 文章標題
- HTML Preview（消毒後內容）
- WordPress 草稿連結

### 2.4 錯誤情境

| 現象 | 可能原因 |
|---|---|
| `Generation failed. Please retry.` | Gemini 配額用盡或 API Key 無效（429 會先 retry） |
| `WordPress publishing failed.` | Application Password 錯誤或 REST API 401 |
| 前端無法連線 | 後端未啟動或 CORS 設定不符（見 [README — 常見啟動問題](../README.md#troubleshooting)） |

---

## 3. WordPress 檢視生成結果

### 3.1 從前端連結

生成成功後，點擊回應中的 **draft_url**。

### 3.2 從 WordPress 後台

1. 登入 WordPress 後台
2. 左側選單 → **文章** → **所有文章**
3. 篩選狀態：**草稿**
4. 找到剛建立的文章（標題應與 LLM 生成一致）
5. 點擊 **預覽** 或 **編輯**，確認 HTML 結構（`<h1>`、`<h2>`、`<p>`、`<ul>` 等）

### 3.3 REST API 驗證（可選）

於 `backend` 目錄，以 `settings` 讀取憑證後 GET 指定 `post_id`：

```bash
cd backend
python -c "
import httpx, base64
from config.settings import settings
creds = f'{settings.wordpress_username}:{settings.wordpress_app_password}'
token = base64.b64encode(creds.encode()).decode()
post_id = 11  # 改為實際 post_id
r = httpx.get(
    f'{settings.wordpress_url.rstrip(\"/\")}/wp-json/wp/v2/posts/{post_id}',
    headers={'Authorization': f'Basic {token}'},
)
print(r.status_code, r.json().get('status'), r.json().get('title', {}).get('rendered', '')[:50])
"
```

---

## 4. 測試期間疑難排解

### 4.1 Gemini 429（測試執行中）

**症狀**：`/generate` 回傳 500，後端 log 出現 `429 You exceeded your current quota`

**處置**：

1. 後端對 429 會**先自動 retry**，仍失敗才回 500
2. 至 [Google AI Studio](https://aistudio.google.com/) 或 [Rate Limit Dashboard](https://ai.dev/rate-limit) 檢查用量
3. 確認 `GEMINI_MODEL=gemini-2.5-flash`（見 [README — 環境變數](../README.md#env-vars)）
4. 等待免費方案配額重置（每分鐘 / 每日）
5. 暫停 Full-Stack Live 測試，避免連續呼叫
6. 考慮啟用付費方案

### 4.2 WordPress 401

請參考 [wordpress-setup.md](./wordpress-setup.md) 的 Troubleshooting 章節。

---

## 5. 測試檢查清單

- [ ] 已完成 [README Getting Started](../README.md#getting-started)
- [ ] `GET /health` 三項皆 OK
- [ ] 前端 `http://localhost:5173` 可開啟
- [ ] §1.4 Backend Mock（retry policy）終端輸出 OK
- [ ] （可選）本機 Full-Stack Live 測試通過
- [ ] 手動 UI 送出表單成功
- [ ] WordPress 後台可見新草稿
- [ ] 草稿 HTML 結構正確、無 `<script>` 等危險標籤

---

## 6. 相關文件

| 文件 | 說明 |
|---|---|
| [README.md](../README.md) | 專案說明、Getting Started、API 摘要 |
| [architecture.md](./architecture.md) | 系統架構 |
| [api-spec.md](./api-spec.md) | API 規格 |
| [wordpress-setup.md](./wordpress-setup.md) | WordPress 設定 |
| [prompt-strategy.md](./prompt-strategy.md) | Prompt 策略 |
