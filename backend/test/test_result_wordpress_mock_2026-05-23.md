# 測試報告：wordpress_mock

- **測試日期**：2026-05-23
- **測試範圍**：Backend ↔ WordPress（Mock LLM，不呼叫 Gemini API）
- **Mock 資料目錄**：`backend/test/`

## 結論

**整體結果：通過**

在 mock 文章驅動下，Backend 已完成 JSON 驗證、HTML 消毒、WordPress REST 認證與草稿發布；`/health` 端點可正確回報 WordPress 狀態。LLM 項目（T09）僅記錄現況，不影響本次 WordPress 連線測試判定。

## 測試項目與結果

| ID | 測試項目 | 結果 | 備註 |
|---|---|---|---|
| T01 | WordPress 環境變數已設定 | PASS | — |
| T02 | 測試模式：略過 LLM API（使用 mock 文章） | PASS | 本測試不呼叫 generate_article / Gemini |
| T03 | Mock LLM 輸出 JSON 驗證 | PASS | title=[MOCK] Backend WordPress 連線測試文章... |
| T04 | HTML 消毒移除危險標籤 | PASS | cleaned length=36 |
| T05 | WordPress REST 認證 (GET /wp/v2/users/me) | PASS | OK |
| T06 | WordPress 草稿發布 (POST /wp/v2/posts) | PASS | post_id=8, draft_url=http://ai-seo-cy310.local/?p=8... |
| T07 | Health report — app 狀態 | PASS | {'status': 'OK'} |
| T08 | Health report — wordpress 狀態 | PASS | OK |
| T09 | Health report — llm（mock 模式記錄實際狀態，不列入通過條件） | PASS | status=ERROR; mock 測試不要求 LLM OK |
| T10 | GET /health (JSON) — WordPress 區塊 | PASS | http=503, wordpress={'status': 'OK'} |
| T11 | GET /health (JSON) — 整體回應結構 | PASS | keys=['app', 'wordpress', 'llm'] |

## Mock 檔案

| 檔案 | 用途 |
|---|---|
| `mock_llm_article.json` | 模擬 LLM 輸出，用於驗證與發布 |
| `mock_llm_article_unsafe.json` | 含 XSS 向量，測試 sanitizer |
| `mock_generate_request.json` | 參考用 `/generate` 請求格式 |

## 執行方式

```bash
cd backend
python test/run_wordpress_mock_test.py
```
