# 測試報告：frontend_wordpress_mock

- **測試日期**：2026-05-23
- **測試範圍**：前端表單輸入 → POST /generate → WordPress（Mock LLM，不呼叫 Gemini API）
- **Mock 資料目錄**：`backend/test/`

## 結論

**整體結果：通過**

以前端 SeoForm 相同欄位結構的 mock 資料驅動，已驗證前端→API 欄位轉換、後端 GenerateRequest / LLMArticleOutput schema，並透過 patch LLM 完成 `POST /generate` 至 WordPress 草稿發布全流程。

## 測試項目與結果

| ID | 測試項目 | 結果 | 備註 |
|---|---|---|---|
| T01 | 前端 mock 表單必填欄位完整 | PASS | keys=['topic', 'keywords', 'targetAudience', 'callToAction'] |
| T02 | 前端 → API 欄位轉換與 mock_generate_request.json 一致 | PASS | api.js: targetAudience→target_audience, callToAction→call_to_action |
| T03 | 後端 GenerateRequest schema 驗證 | PASS | topic=高雄美食旅遊指南（Mock）... |
| T04 | LLMArticleOutput schema 驗證（mock_llm_article.json） | PASS | title=[MOCK] 高雄美食旅遊指南（Mock）... |
| T05 | Mock CTA 長度 <= 200（與前端 validators 一致） | PASS | len=10 |
| T06 | 測試模式：略過 LLM API（patch generate_article） | PASS | 本測試不呼叫 Gemini |
| T07 | WordPress 環境變數已設定 | PASS | — |
| T08 | POST /generate（Mock LLM）HTTP 200 | PASS | http=200, status=success |
| T09 | POST /generate 回應結構（GenerateSuccessResponse） | PASS | keys=['status', 'post_id', 'draft_url', 'title', 'preview_html'] |
| T10 | WordPress 草稿發布（由 /generate 觸發） | PASS | post_id=10, draft_url=http://ai-seo-cy310.local/?p=10... |
| T11 | mock_schema_manifest 欄位對照與 api.js 一致 | PASS | {'topic': 'topic', 'keywords': 'keywords', 'targetAudience': 'target_audience', 'callToAction': 'call_to_action'} |

## Schema 對照（三層一致）

| 層級 | 檔案 | 模型 / 來源 |
|---|---|---|
| 前端送出 | `mock_frontend_form.json` | SeoForm → camelCase |
| API 請求 | `mock_generate_request.json` | `GenerateRequest`（snake_case） |
| LLM 輸出 | `mock_llm_article.json` | `LLMArticleOutput` |
| 對照說明 | `mock_schema_manifest.json` | 欄位 mapping + CTA 上限 200 |

## Mock 檔案

| 檔案 | 用途 |
|---|---|
| `mock_frontend_form.json` | 模擬 SeoForm 送出內容 |
| `mock_generate_request.json` | 模擬 `api.js` POST body |
| `mock_llm_article.json` | 模擬 LLM JSON 輸出 |
| `mock_llm_article_unsafe.json` | XSS 測試（sanitizer 專用） |
| `mock_schema_manifest.json` | 三層 schema 與欄位對照 |

## 執行方式

```bash
cd backend
python test/run_frontend_wordpress_mock_test.py
```
