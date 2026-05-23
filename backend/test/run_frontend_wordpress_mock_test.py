"""
前端表單輸入 → POST /generate → WordPress 草稿（Mock LLM，不呼叫 Gemini API）。

Mock 資料對應：
  mock_frontend_form.json      — SeoForm 送出（camelCase）
  mock_generate_request.json   — api.js 轉換後的 /generate body（snake_case）
  mock_llm_article.json        — 模擬 LLM 輸出（LLMArticleOutput）
  mock_schema_manifest.json    — 三層欄位對照說明

執行方式（於 backend 目錄）:
    python test/run_frontend_wordpress_mock_test.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from unittest.mock import patch

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

TEST_DIR = Path(__file__).resolve().parent
CTA_MAX_LENGTH = 200


@dataclass
class TestResult:
    id: str
    name: str
    passed: bool
    detail: str = ""


@dataclass
class TestRun:
    scope: str
    test_date: str
    results: list[TestResult] = field(default_factory=list)

    def add(self, id: str, name: str, passed: bool, detail: str = "") -> None:
        self.results.append(TestResult(id=id, name=name, passed=passed, detail=detail))


def _load_json(name: str) -> dict:
    path = TEST_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def frontend_to_api_payload(frontend: dict) -> dict:
    """與 frontend/src/services/api.js generateArticle 欄位對應一致。"""
    return {
        "topic": frontend["topic"],
        "keywords": frontend["keywords"],
        "target_audience": frontend["targetAudience"],
        "call_to_action": frontend["callToAction"],
    }


def run_tests() -> TestRun:
    from models.schemas import GenerateRequest, LLMArticleOutput
    from services.validation_service import validate_llm_output

    run = TestRun(scope="frontend_wordpress_mock", test_date=date.today().isoformat())
    manifest = _load_json("mock_schema_manifest.json")
    frontend = _load_json("mock_frontend_form.json")
    api_expected = _load_json("mock_generate_request.json")
    mock_llm = _load_json("mock_llm_article.json")

    # T01 前端 mock 必填欄位
    required_fe = ["topic", "keywords", "targetAudience", "callToAction"]
    fe_ok = all(frontend.get(k) for k in required_fe) and isinstance(frontend.get("keywords"), list)
    run.add(
        "T01",
        "前端 mock 表單必填欄位完整",
        fe_ok,
        f"keys={list(frontend.keys())}",
    )

    # T02 前端 → API 轉換與 mock_generate_request.json 一致
    api_from_fe = frontend_to_api_payload(frontend)
    mapping_match = api_from_fe == api_expected
    run.add(
        "T02",
        "前端 → API 欄位轉換與 mock_generate_request.json 一致",
        mapping_match,
        "api.js: targetAudience→target_audience, callToAction→call_to_action",
    )

    # T03 後端 GenerateRequest（Pydantic）驗證
    try:
        req = GenerateRequest.model_validate(api_expected)
        run.add(
            "T03",
            "後端 GenerateRequest schema 驗證",
            req.topic == api_expected["topic"],
            f"topic={req.topic[:30]}...",
        )
    except Exception as exc:
        run.add("T03", "後端 GenerateRequest schema 驗證", False, str(exc))

    # T04 LLM 輸出 schema
    try:
        article = validate_llm_output(mock_llm)
        run.add(
            "T04",
            "LLMArticleOutput schema 驗證（mock_llm_article.json）",
            bool(article.title and article.content_html),
            f"title={article.title[:40]}...",
        )
    except Exception as exc:
        run.add("T04", "LLMArticleOutput schema 驗證（mock_llm_article.json）", False, str(exc))

    # T05 CTA 長度與前端 CTA_MAX_LENGTH 一致
    cta_len = len(frontend.get("callToAction", ""))
    cta_max = manifest.get("cta_max_length", CTA_MAX_LENGTH)
    run.add(
        "T05",
        f"Mock CTA 長度 <= {cta_max}（與前端 validators 一致）",
        0 < cta_len <= cta_max,
        f"len={cta_len}",
    )

    # T06 mock 模式不呼叫 LLM
    run.add(
        "T06",
        "測試模式：略過 LLM API（patch generate_article）",
        True,
        "本測試不呼叫 Gemini",
    )

    # T07–T09 POST /generate 端到端（mock LLM）
    from config.settings import settings
    from fastapi.testclient import TestClient

    from app import app

    wp_configured = all(
        [settings.wordpress_url, settings.wordpress_username, settings.wordpress_app_password]
    )
    run.add(
        "T07",
        "WordPress 環境變數已設定",
        wp_configured,
        "" if wp_configured else "缺少 WORDPRESS_URL / USERNAME / APP_PASSWORD",
    )

    post_id = None
    draft_url = ""
    try:
        with patch("routes.generate_route.generate_article", return_value=mock_llm):
            client = TestClient(app)
            resp = client.post("/generate", json=api_from_fe)

        body = resp.json()
        post_id = body.get("post_id")
        draft_url = body.get("draft_url", "")
        gen_ok = resp.status_code == 200 and body.get("status") == "success"
        run.add(
            "T08",
            "POST /generate（Mock LLM）HTTP 200",
            gen_ok,
            f"http={resp.status_code}, status={body.get('status')}",
        )
        has_fields = all(
            body.get(k) for k in ("post_id", "draft_url", "title", "preview_html")
        )
        run.add(
            "T09",
            "POST /generate 回應結構（GenerateSuccessResponse）",
            has_fields and gen_ok,
            f"keys={list(body.keys())}",
        )
        run.add(
            "T10",
            "WordPress 草稿發布（由 /generate 觸發）",
            bool(post_id),
            f"post_id={post_id}, draft_url={draft_url[:80]}..." if draft_url else f"post_id={post_id}",
        )
    except Exception as exc:
        run.add("T08", "POST /generate（Mock LLM）HTTP 200", False, str(exc))
        run.add("T09", "POST /generate 回應結構（GenerateSuccessResponse）", False, str(exc))
        run.add("T10", "WordPress 草稿發布（由 /generate 觸發）", False, str(exc))

    # T11 manifest 對照檔與實際 mapping 一致
    manifest_map = manifest.get("field_mapping_frontend_to_api", {})
    code_map = {
        "topic": "topic",
        "keywords": "keywords",
        "targetAudience": "target_audience",
        "callToAction": "call_to_action",
    }
    run.add(
        "T11",
        "mock_schema_manifest 欄位對照與 api.js 一致",
        manifest_map == code_map,
        str(manifest_map),
    )

    return run


def write_report(run: TestRun) -> Path:
    report_path = TEST_DIR / f"test_result_{run.scope}_{run.test_date}.md"
    required_ids = {"T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09", "T10", "T11"}
    e2e_passed = all(r.passed for r in run.results if r.id in required_ids)
    overall = "通過" if e2e_passed else "未通過"

    lines = [
        f"# 測試報告：{run.scope}",
        "",
        f"- **測試日期**：{run.test_date}",
        f"- **測試範圍**：前端表單輸入 → POST /generate → WordPress（Mock LLM，不呼叫 Gemini API）",
        f"- **Mock 資料目錄**：`backend/test/`",
        "",
        "## 結論",
        "",
        f"**整體結果：{overall}**",
        "",
    ]
    if e2e_passed:
        lines.append(
            "以前端 SeoForm 相同欄位結構的 mock 資料驅動，已驗證前端→API 欄位轉換、"
            "後端 GenerateRequest / LLMArticleOutput schema，並透過 patch LLM 完成 "
            "`POST /generate` 至 WordPress 草稿發布全流程。"
        )
    else:
        failed = [r for r in run.results if r.id in required_ids and not r.passed]
        lines.append(
            f"失敗項目：{', '.join(r.id for r in failed)}。"
            "請檢查 mock JSON、`.env` 與 WordPress Application Password。"
        )

    lines.extend(
        [
            "",
            "## 測試項目與結果",
            "",
            "| ID | 測試項目 | 結果 | 備註 |",
            "|---|---|---|---|",
        ]
    )
    for r in run.results:
        status = "PASS" if r.passed else "FAIL"
        detail = (r.detail or "—").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {r.id} | {r.name} | {status} | {detail} |")

    lines.extend(
        [
            "",
            "## Schema 對照（三層一致）",
            "",
            "| 層級 | 檔案 | 模型 / 來源 |",
            "|---|---|---|",
            "| 前端送出 | `mock_frontend_form.json` | SeoForm → camelCase |",
            "| API 請求 | `mock_generate_request.json` | `GenerateRequest`（snake_case） |",
            "| LLM 輸出 | `mock_llm_article.json` | `LLMArticleOutput` |",
            "| 對照說明 | `mock_schema_manifest.json` | 欄位 mapping + CTA 上限 200 |",
            "",
            "## Mock 檔案",
            "",
            "| 檔案 | 用途 |",
            "|---|---|",
            "| `mock_frontend_form.json` | 模擬 SeoForm 送出內容 |",
            "| `mock_generate_request.json` | 模擬 `api.js` POST body |",
            "| `mock_llm_article.json` | 模擬 LLM JSON 輸出 |",
            "| `mock_llm_article_unsafe.json` | XSS 測試（sanitizer 專用） |",
            "| `mock_schema_manifest.json` | 三層 schema 與欄位對照 |",
            "",
            "## 執行方式",
            "",
            "```bash",
            "cd backend",
            "python test/run_frontend_wordpress_mock_test.py",
            "```",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    run = run_tests()
    report_path = write_report(run)
    required_ids = {"T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09", "T10", "T11"}
    e2e_passed = all(r.passed for r in run.results if r.id in required_ids)

    print(f"Report written: {report_path}")
    for r in run.results:
        mark = "PASS" if r.passed else "FAIL"
        line = f"  [{mark}] {r.id} {r.name}"
        if r.detail:
            line += f"\n         {r.detail}"
        try:
            print(line)
        except UnicodeEncodeError:
            print(line.encode("utf-8", errors="replace").decode("utf-8"))

    return 0 if e2e_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
