"""
檢查本地 WordPress REST API 與 Application Password (Basic Auth) 設定。

執行：cd backend && python test/check_wordpress_rest_auth.py
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import httpx

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from config.settings import settings
from services.wordpress_service import _auth_header


def _mask(s: str, show: int = 4) -> str:
    if len(s) <= show:
        return "***"
    return s[:show] + "***"


def main() -> int:
    base = settings.wordpress_url.rstrip("/")
    user = settings.wordpress_username
    password = settings.wordpress_app_password

    print("=== WordPress REST / Basic Auth 診斷 ===\n")
    print(f"URL: {base}")
    print(f"Username: {user!r} (len={len(user)})")
    print(
        f"App password: {_mask(password.replace(' ', ''))} "
        f"(len={len(password)}, spaces={password.count(' ')}, "
        f"looks_like_app_pw={len(password.replace(' ', '')) >= 20})"
    )
    if len(password.replace(" ", "")) < 20:
        print(
            "  [!] 密碼長度偏短，可能為「登入密碼」而非 Application Password；"
            "REST API 需使用後台產生的應用程式密碼。"
        )
    print()

    checks: list[tuple[str, bool, str]] = []

    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        # 1. REST 根目錄
        r1 = client.get(f"{base}/wp-json/")
        ok1 = r1.status_code == 200
        name = ""
        if ok1:
            try:
                name = r1.json().get("name", "")
            except json.JSONDecodeError:
                pass
        checks.append(
            (
                "REST API 根 (/wp-json/)",
                ok1,
                f"HTTP {r1.status_code}" + (f", site={name!r}" if name else ""),
            )
        )

        # 2. WP v2 命名空間
        r2 = client.get(f"{base}/wp-json/wp/v2/")
        checks.append(
            (
                "WP v2 命名空間 (/wp-json/wp/v2/)",
                r2.status_code == 200,
                f"HTTP {r2.status_code}",
            )
        )

        # 3. Application Passwords 是否可用（需登入時會 401，但端點存在則 401/200）
        r3 = client.get(f"{base}/wp-json/wp/v2/users/me/application-passwords")
        app_pw_endpoint = r3.status_code in (200, 401, 403)
        checks.append(
            (
                "Application Passwords 端點存在",
                app_pw_endpoint,
                f"HTTP {r3.status_code} (401/403 表示端點存在但未帶認證)",
            )
        )

        # 4. Basic Auth — users/me
        r4 = client.get(f"{base}/wp-json/wp/v2/users/me", headers=_auth_header())
        ok4 = r4.status_code == 200
        detail4 = f"HTTP {r4.status_code}"
        if ok4:
            me = r4.json()
            detail4 += f", id={me.get('id')}, slug={me.get('slug')!r}, roles={me.get('roles')}"
        else:
            detail4 += f", body={r4.text[:180]}"
        checks.append(("Basic Auth (GET /users/me)", ok4, detail4))

        # 5. 若失敗：嘗試常見使用者名稱變體（僅診斷，不輸出密碼）
        if not ok4 and user.lower() != user:
            cred = f"{user.lower()}:{password}"
            token = base64.b64encode(cred.encode()).decode()
            r5 = client.get(
                f"{base}/wp-json/wp/v2/users/me",
                headers={"Authorization": f"Basic {token}"},
            )
            if r5.status_code == 200:
                me = r5.json()
                checks.append(
                    (
                        "Basic Auth（小寫 username 提示）",
                        True,
                        f"使用 {user.lower()!r} 可通過；請將 WORDPRESS_USERNAME 改為小寫",
                    )
                )

        # 6. 無認證 posts 應 401（確認端點需認證）
        r6 = client.post(
            f"{base}/wp-json/wp/v2/posts",
            json={"title": "probe", "content": "x", "status": "draft"},
        )
        checks.append(
            (
                "Posts 端點需認證（無 Auth 應 401）",
                r6.status_code == 401,
                f"HTTP {r6.status_code}",
            )
        )

    print("| 檢查項目 | 結果 | 詳情 |")
    print("|---|---|---|")
    all_ok = True
    critical = {"REST API 根 (/wp-json/)", "Basic Auth (GET /users/me)"}
    for name, ok, detail in checks:
        status = "OK" if ok else "FAIL"
        print(f"| {name} | {status} | {detail} |")
        if name in critical and not ok:
            all_ok = False

    print()
    if not all_ok:
        print("建議：")
        print("  - 確認固定連結非「樸素」、REST API 未遭外掛停用")
        print("  - WordPress 5.6+ 且使用者具 edit_posts")
        print("  - Application Password 重新產生後完整貼入 .env（保留或移除空格皆可，需與 WP 顯示一致）")
        print("  - WORDPRESS_USERNAME 須為登入帳號 slug（本機站為 admin，非顯示名稱 Admin）")
        print("  - 確認已儲存 backend/.env（編輯器未儲存時執行測試仍會讀到舊值）")
        return 1

    print("REST / Basic Auth 檢查通過，可執行 mock 測試。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
