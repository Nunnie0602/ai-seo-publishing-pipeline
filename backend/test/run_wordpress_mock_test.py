"""
以 mock 資料測試 backend ↔ WordPress 連線（不呼叫 LLM API）。

執行方式（於 backend 目錄）:
    python test/run_wordpress_mock_test.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# 確保可 import backend 模組
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

TEST_DIR = Path(__file__).resolve().parent


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

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)


def _load_json(name: str) -> dict:
    path = TEST_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def run_tests() -> TestRun:
    from config.settings import settings
    from services.health_service import _check_llm, _check_wordpress, build_health_report
    from services.sanitizer_service import sanitize_html
    from services.validation_service import validate_llm_output
    from services.wordpress_service import publish_draft

    run = TestRun(scope="wordpress_mock", test_date=date.today().isoformat())

    # 1. WordPress 環境變數
    wp_configured = all(
        [settings.wordpress_url, settings.wordpress_username, settings.wordpress_app_password]
    )
    run.add(
        "T01",
        "WordPress 環境變數已設定",
        wp_configured,
        "" if wp_configured else "缺少 WORDPRESS_URL / USERNAME / APP_PASSWORD",
    )

    # 2. LLM 刻意不驗證真實金鑰（mock 模式）
    run.add(
        "T02",
        "測試模式：略過 LLM API（使用 mock 文章）",
        True,
        "本測試不呼叫 generate_article / Gemini",
    )

    # 3. Mock JSON 驗證
    try:
        mock = _load_json("mock_llm_article.json")
        article = validate_llm_output(mock)
        run.add(
            "T03",
            "Mock LLM 輸出 JSON 驗證",
            article.title.startswith("[MOCK]"),
            f"title={article.title[:40]}...",
        )
    except Exception as exc:
        run.add("T03", "Mock LLM 輸出 JSON 驗證", False, str(exc))

    # 4. HTML 消毒（安全 mock）
    try:
        unsafe = _load_json("mock_llm_article_unsafe.json")
        cleaned = sanitize_html(unsafe["content_html"])
        no_script = "<script" not in cleaned.lower()
        no_iframe = "<iframe" not in cleaned.lower()
        run.add(
            "T04",
            "HTML 消毒移除危險標籤",
            no_script and no_iframe,
            f"cleaned length={len(cleaned)}",
        )
    except Exception as exc:
        run.add("T04", "HTML 消毒移除危險標籤", False, str(exc))

    # 5. WordPress REST 認證（users/me）
    wp_health = _check_wordpress()
    run.add(
        "T05",
        "WordPress REST 認證 (GET /wp/v2/users/me)",
        wp_health.get("status") == "OK",
        wp_health.get("message", "OK"),
    )

    # 6. 以 mock 內容發布草稿
    try:
        mock = _load_json("mock_llm_article.json")
        article = validate_llm_output(mock)
        safe_html = sanitize_html(article.content_html)
        wp_result = publish_draft(article.title, safe_html)
        post_id = wp_result.get("post_id")
        draft_url = wp_result.get("draft_url", "")
        run.add(
            "T06",
            "WordPress 草稿發布 (POST /wp/v2/posts)",
            bool(post_id),
            f"post_id={post_id}, draft_url={draft_url[:80]}..." if draft_url else f"post_id={post_id}",
        )
    except Exception as exc:
        run.add("T06", "WordPress 草稿發布 (POST /wp/v2/posts)", False, str(exc))

    # 7. Health report — WordPress 應 OK；LLM 在無效/空金鑰時預期 ERROR
    report = build_health_report()
    run.add(
        "T07",
        "Health report — app 狀態",
        report["app"].get("status") == "OK",
        str(report["app"]),
    )
    run.add(
        "T08",
        "Health report — wordpress 狀態",
        report["wordpress"].get("status") == "OK",
        report["wordpress"].get("message", "OK"),
    )

    # 模擬「未設定有效 LLM」：僅檢查邏輯，不把金鑰寫入報告
    llm_check = _check_llm()
    llm_skipped_ok = True  # mock 模式下 LLM 非必測
    run.add(
        "T09",
        "Health report — llm（mock 模式記錄實際狀態，不列入通過條件）",
        llm_skipped_ok,
        f"status={llm_check.get('status')}; mock 測試不要求 LLM OK",
    )

    # 8. FastAPI /health JSON（TestClient，不需啟動 uvicorn）
    try:
        from fastapi.testclient import TestClient

        from app import app

        client = TestClient(app)
        resp = client.get("/health", headers={"Accept": "application/json"})
        body = resp.json()
        wp_ok = body.get("wordpress", {}).get("status") == "OK"
        run.add(
            "T10",
            "GET /health (JSON) — WordPress 區塊",
            wp_ok and resp.status_code in (200, 503),
            f"http={resp.status_code}, wordpress={body.get('wordpress')}",
        )
        run.add(
            "T11",
            "GET /health (JSON) — 整體回應結構",
            "app" in body and "wordpress" in body and "llm" in body,
            f"keys={list(body.keys())}",
        )
    except Exception as exc:
        run.add("T10", "GET /health (JSON) — WordPress 區塊", False, str(exc))
        run.add("T11", "GET /health (JSON) — 整體回應結構", False, str(exc))

    return run


def write_report(run: TestRun) -> Path:
    report_path = TEST_DIR / f"test_result_{run.scope}_{run.test_date}.md"

    # WordPress 相關必過項（不含 T09 LLM 記錄項）
    required_ids = {"T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T10", "T11"}
    wp_passed = all(r.passed for r in run.results if r.id in required_ids)
    overall = "通過" if wp_passed else "未通過"

    lines = [
        f"# 測試報告：{run.scope}",
        "",
        f"- **測試日期**：{run.test_date}",
        f"- **測試範圍**：Backend ↔ WordPress（Mock LLM，不呼叫 Gemini API）",
        f"- **Mock 資料目錄**：`backend/test/`",
        "",
        "## 結論",
        "",
        f"**整體結果：{overall}**",
        "",
    ]
    if wp_passed:
        lines.append(
            "在 mock 文章驅動下，Backend 已完成 JSON 驗證、HTML 消毒、"
            "WordPress REST 認證與草稿發布；`/health` 端點可正確回報 WordPress 狀態。"
            "LLM 項目（T09）僅記錄現況，不影響本次 WordPress 連線測試判定。"
        )
    else:
        failed = [r for r in run.results if r.id in required_ids and not r.passed]
        lines.append(f"失敗項目：{', '.join(r.id for r in failed)}。請檢查 `.env` 與 WordPress Application Password。")

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
            "## Mock 檔案",
            "",
            "| 檔案 | 用途 |",
            "|---|---|",
            "| `mock_llm_article.json` | 模擬 LLM 輸出，用於驗證與發布 |",
            "| `mock_llm_article_unsafe.json` | 含 XSS 向量，測試 sanitizer |",
            "| `mock_generate_request.json` | 參考用 `/generate` 請求格式 |",
            "",
            "## 執行方式",
            "",
            "```bash",
            "cd backend",
            "python test/run_wordpress_mock_test.py",
            "```",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    run = run_tests()
    report_path = write_report(run)
    required_ids = {"T01", "T02", "T03", "T04", "T05", "T06", "T07", "T08", "T10", "T11"}
    wp_passed = all(r.passed for r in run.results if r.id in required_ids)

    print(f"Report written: {report_path}")
    for r in run.results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"  [{mark}] {r.id} {r.name}")
        if r.detail:
            print(f"         {r.detail}")

    return 0 if wp_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
