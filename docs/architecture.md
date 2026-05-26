# Architecture

## Overview

AI SEO Content Publishing Pipeline 採用前後端分離架構，透過 service layer 處理 LLM 生成、驗證、清理與 WordPress 發布。

## Flow

```text
User Input → Frontend Validation → Backend API
  → Prompt Builder → LLM → JSON Validation
  → HTML Sanitization → WordPress Draft → Frontend Display
```

## Layers

| Layer | Responsibility |
|---|---|
| Frontend (React/Vite) | 表單、驗證、Loading/Error/Preview UX |
| Routes | HTTP 端點與請求/回應對應 |
| Services | 業務邏輯（LLM、Prompt、Validation、Sanitizer、WordPress） |
| Models | Pydantic schemas |
| Utils | Retry、Retry Policy（`is_llm_retryable` / `is_wp_retryable`）、Parser、Constants |
| Config | 環境變數與 CORS |

## Design Principles

- **Service separation**: 各步驟獨立模組，便於測試與擴充
- **Fail-safe validation**: Invalid AI output 不進入 publishing flow
- **Classified retry**: LLM 與 WordPress 僅對暫時性錯誤重試；設定類 4xx 立即失敗
- **Observability**: 結構化 logging 於 `backend/logs/`（執行期產出，未納入版控）

## Future Extensions

- Multiple AI providers
- Scheduled publishing
- Human review workflow
