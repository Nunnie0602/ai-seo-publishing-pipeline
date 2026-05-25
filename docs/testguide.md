# Full-Stack 測試指南



本指南說明如何執行真實 API 端到端測試，並在 WordPress 檢視生成結果。



> 環境準備、依賴安裝、服務啟動與健康檢查，請先完成 **[README.md — Getting Started](../README.md#getting-started)**。  

> 最後驗證日期：2026-05-24 | 測試報告：`full-stack-testcases/test_result_full_stack_live_2026-05-24.md`



---



## 1. 自動化 Full-Stack 測試



### 1.1 執行測試腳本



於**專案根目錄**執行（需已完成 README 中的環境設定與 `GET /health` 三項 OK）：



```bash

python full-stack-testcases/run_full_stack_live_test.py

```



若前後端已啟動，可一併驗證 HTTP 連線：



```powershell

# PowerShell

$env:BACKEND_BASE_URL="http://127.0.0.1:8000"

$env:FRONTEND_BASE_URL="http://127.0.0.1:5173"

python full-stack-testcases/run_full_stack_live_test.py

```



```bash

# Bash

BACKEND_BASE_URL=http://127.0.0.1:8000 FRONTEND_BASE_URL=http://127.0.0.1:5173 \

  python full-stack-testcases/run_full_stack_live_test.py

```



### 1.2 測試範圍



| 階段 | 說明 |
|---|---|
| T01–T04 | 前端 mock 表單 → API 欄位轉換 → schema 驗證 |
| T05–T08 | 環境變數、LLM / WordPress health check |
| T09–T14 | **真實 Gemini API** → JSON 驗證 → HTML 消毒 → WordPress 草稿 |
| T15–T16 | 可選：已啟動的前後端 HTTP 連線 |
| T18 | 測試後 Gemini 配額探測 |



### 1.3 測試產出



測試完成後，`full-stack-testcases/` 目錄會產生：



| 檔案 | 內容 |
|---|---|
| `test_result_full_stack_live_YYYY-MM-DD.md` | 測試報告 |
| `live_llm_article_YYYY-MM-DD.json` | LLM 輸出快照 |
| `generate_response_YYYY-MM-DD.json` | `/generate` 完整回應 |
| `wordpress_post_YYYY-MM-DD.json` | WordPress 草稿讀回驗證 |

> **注意**：T09 會消耗 Gemini API 配額並在 WordPress 建立真實草稿，請勿在 CI 中頻繁執行。



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

Generating articl → Validating JSON → Sanitizing HTML → Publishing draft → Completed

```


成功後頁面會顯示：

- 文章標題

- HTML Preview（消毒後內容）

- WordPress 草稿連結



### 2.4 錯誤情境

| 現象 | 可能原因 |
|---|---|
| `Generation failed. Please retry.` | Gemini 配額用盡或 API Key 無效 |
| `WordPress publishing failed.` | Application Password 錯誤或 REST API 401 |
| 前端無法連線 | 後端未啟動或 CORS 設定不符（見 [README — 常見啟動問題](../README.md#troubleshooting)） |



---



## 3. WordPress 檢視生成結果


### 3.1 從前端連結


生成成功後，點擊回應中的 **draft_url**（例如 `http://ai-seo-cy310.local/?p=11`）。


### 3.2 從 WordPress 後台



1. 登入 WordPress 後台

2. 左側選單 → **文章** → **所有文章**

3. 篩選狀態：**草稿**

4. 找到剛建立的文章（標題應與 LLM 生成一致）

5. 點擊 **預覽** 或 **編輯**，確認 HTML 結構（`<h1>`、`<h2>`、`<p>`、`<ul>` 等）



### 3.3 REST API 驗證（可選）



```bash

cd backend

python test/check_wordpress_rest_auth.py

```



或使用測試報告中的 `post_id`：



```bash

python -c "

import httpx, base64, os

from config.settings import settings

creds = f'{settings.wordpress_username}:{settings.wordpress_app_password}'

token = __import__('base64').b64encode(creds.encode()).decode()

r = httpx.get(f'{settings.wordpress_url.rstrip(\"/\")}/wp-json/wp/v2/posts/11', headers={'Authorization': f'Basic {token}'})

print(r.status_code, r.json().get('status'), r.json().get('title',{}).get('rendered','')[:50])

"

```



---



## 4. 測試期間疑難排解



### 4.1 Gemini 429（測試執行中）



**症狀**：`/generate` 回傳 500，後端 log 出現 `429 You exceeded your current quota`



**處置**：



1. 至 [Google AI Studio](https://aistudio.google.com/) 或 [Rate Limit Dashboard](https://ai.dev/rate-limit) 檢查用量

2. 確認 `GEMINI_MODEL=gemini-2.5-flash`（見 [README — 環境變數](../README.md#env-vars)）

3. 等待免費方案配額重置（每分鐘 / 每日）

4. **暫停** `run_full_stack_live_test.py`，避免連續呼叫

5. 考慮啟用付費方案



### 4.2 WordPress 401



請參考 [wordpress-setup.md](./wordpress-setup.md) 的 Troubleshooting 章節。



---



## 5. 測試檢查清單



- [ ] 已完成 [README Getting Started](../README.md#getting-started)

- [ ] `GET /health` 三項皆 OK

- [ ] 前端 `http://localhost:5173` 可開啟

- [ ] 自動化測試 `run_full_stack_live_test.py` 通過

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
| [revision.md](../revision.md) | Full-Stack 實測變更紀錄 |
| `full-stack-testcases/test_result_full_stack_live_*.md` | 最新測試報告 |


