import os
import sqlite3
import hashlib
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


# =========================================================
# 기본 설정
# =========================================================

app = FastAPI(title="분양노크 OpenChat Funnel")

OPENCHAT_URL = os.getenv(
    "OPENCHAT_URL",
    "https://open.kakao.com/o/gSRhTTBi"
)

BASE_URL = os.getenv(
    "BASE_URL",
    "https://openchat-funnel.onrender.com"
).rstrip("/")

DB_PATH = os.getenv("DB_PATH", "funnel.db")


# =========================================================
# Static
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# DB
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            kind TEXT NOT NULL,
            ts TEXT NOT NULL,
            iphash TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================================================
# 방문자 기록
# =========================================================

def record_event(request: Request, source: str, kind: str):

    ip = ""

    if request.client:
        ip = request.client.host or ""

    forwarded = request.headers.get("x-forwarded-for")

    if forwarded:
        ip = forwarded.split(",")[0].strip()

    iphash = hashlib.sha256(
        ip.encode("utf-8")
    ).hexdigest()[:16]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO events(source, kind, ts, iphash)
        VALUES (?, ?, ?, ?)
        """,
        (
            source,
            kind,
            datetime.now().isoformat(timespec="seconds"),
            iphash
        )
    )

    conn.commit()
    conn.close()


# =========================================================
# 메인
# =========================================================

@app.get("/")
def home():

    return RedirectResponse(
        url="/admin",
        status_code=302
    )


# =========================================================
# 홍보용 랜딩페이지
#
# 사용 예:
#
# /go/naver01
# /go/blog01
# /go/instagram01
# /go/youtube01
# =========================================================

@app.get(
    "/go/{source}",
    response_class=HTMLResponse
)
def landing(
    request: Request,
    source: str
):

    record_event(
        request,
        source,
        "visit"
    )

    preview_image = (
        f"{BASE_URL}/static/"
        f"bunyangknock-preview.jpg"
    )

    out_url = f"{BASE_URL}/out/{source}"

    html = f"""
<!DOCTYPE html>

<html lang="ko">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
내 집 마련을 위한 첫 노크 | 분양노크
</title>


<!-- 카카오톡 / SNS 미리보기 -->

<meta
    property="og:type"
    content="website"
>

<meta
    property="og:title"
    content="내 집 마련을 위한 첫 노크 | 분양노크"
>

<meta
    property="og:description"
    content="전국 아파트 분양 정보와 부동산 정보를 한곳에서 확인하세요."
>

<meta
    property="og:image"
    content="{preview_image}"
>

<meta
    property="og:image:secure_url"
    content="{preview_image}"
>

<meta
    property="og:url"
    content="{BASE_URL}/go/{source}"
>

<meta
    property="og:site_name"
    content="분양노크"
>


<!-- Twitter / 기타 미리보기 -->

<meta
    name="twitter:card"
    content="summary_large_image"
>

<meta
    name="twitter:title"
    content="내 집 마련을 위한 첫 노크 | 분양노크"
>

<meta
    name="twitter:description"
    content="전국 아파트 분양 정보와 부동산 정보를 한곳에서 확인하세요."
>

<meta
    name="twitter:image"
    content="{preview_image}"
>


<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;
    padding: 0;

    background:
        linear-gradient(
            180deg,
            #f7f8fa 0%,
            #ffffff 100%
        );

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        "Noto Sans KR",
        Arial,
        sans-serif;

    color: #111;
}}

.container {{

    max-width: 720px;

    margin: 0 auto;

    padding:
        55px
        22px
        80px;

}}

.brand {{

    font-size: 15px;

    font-weight: 800;

    letter-spacing: -0.3px;

    margin-bottom: 28px;

}}

h1 {{

    margin: 0;

    font-size: 38px;

    line-height: 1.25;

    letter-spacing: -1.7px;

}}

.highlight {{

    display: block;

    margin-top: 7px;

    font-weight: 900;

}}

.sub {{

    margin-top: 20px;

    font-size: 17px;

    line-height: 1.7;

    color: #555;

}}

.preview {{

    width: 100%;

    margin-top: 32px;

    border-radius: 20px;

    display: block;

    box-shadow:
        0 15px 40px
        rgba(0,0,0,0.08);

}}

.card {{

    margin-top: 28px;

    padding: 24px;

    background: #fff;

    border:
        1px solid
        #eeeeee;

    border-radius: 20px;

}}

.card-title {{

    font-size: 20px;

    font-weight: 800;

    margin-bottom: 12px;

}}

.card-text {{

    color: #666;

    font-size: 15px;

    line-height: 1.7;

}}

.button {{

    display: block;

    width: 100%;

    margin-top: 25px;

    padding: 19px 20px;

    border-radius: 14px;

    text-decoration: none;

    text-align: center;

    font-size: 17px;

    font-weight: 900;

    background: #FEE500;

    color: #191919;

    transition: 0.15s;

}}

.button:hover {{

    transform:
        translateY(-1px);

}}

.notice {{

    margin-top: 16px;

    text-align: center;

    color: #999;

    font-size: 12px;

}}

.footer {{

    margin-top: 50px;

    text-align: center;

    font-size: 12px;

    color: #aaa;

}}

@media(max-width:600px) {{

    .container {{
        padding-top: 38px;
    }}

    h1 {{
        font-size: 31px;
    }}

}}

</style>

</head>


<body>

<div class="container">

    <div class="brand">
        분양노크
    </div>


    <h1>

        내 집 마련을 위한

        <span class="highlight">
            첫 노크.
        </span>

    </h1>


    <div class="sub">

        부동산 정보가 너무 많아
        무엇부터 확인해야 할지
        고민되셨나요?

        <br><br>

        분양노크 정보방에서
        아파트 분양과 부동산 정보를
        편하게 확인해보세요.

    </div>


    <img
        class="preview"
        src="{preview_image}"
        alt="분양노크"
    >


    <div class="card">

        <div class="card-title">
            분양노크 정보방
        </div>

        <div class="card-text">

            분양 정보 · 부동산 이슈 ·
            시장 정보 등을 공유합니다.

            <br>

            아래 버튼을 누르면
            카카오톡 오픈채팅으로 이동합니다.

        </div>


        <a
            class="button"
            href="{out_url}"
        >

            카카오톡 정보방 입장하기

        </a>

    </div>


    <div class="notice">

        버튼 클릭 시
        카카오톡 오픈채팅으로 이동합니다.

    </div>


    <div class="footer">

        분양노크 ·
        내 집 마련을 위한 첫 노크

    </div>

</div>

</body>

</html>
"""

    return HTMLResponse(
        content=html,
        status_code=200
    )


# =========================================================
# 카카오 오픈채팅 이동
# =========================================================

@app.get("/out/{source}")
def openchat(
    request: Request,
    source: str
):

    record_event(
        request,
        source,
        "click"
    )

    return RedirectResponse(
        url=OPENCHAT_URL,
        status_code=302
    )


# =========================================================
# 관리자 대시보드
# =========================================================

@app.get(
    "/admin",
    response_class=HTMLResponse
)
def admin():

    conn = get_db()

    rows = conn.execute(
        """
        SELECT

            source,

            SUM(
                CASE
                    WHEN kind='visit'
                    THEN 1
                    ELSE 0
                END
            ) AS visits,

            SUM(
                CASE
                    WHEN kind='click'
                    THEN 1
                    ELSE 0
                END
            ) AS clicks

        FROM events

        GROUP BY source

        ORDER BY visits DESC
        """
    ).fetchall()

    conn.close()


    table_rows = ""


    for row in rows:

        visits = row["visits"] or 0

        clicks = row["clicks"] or 0


        if visits:

            conversion = (
                clicks /
                visits *
                100
            )

        else:

            conversion = 0


        table_rows += f"""

        <tr>

            <td>
                {row["source"]}
            </td>

            <td>
                {visits}
            </td>

            <td>
                {clicks}
            </td>

            <td>
                {conversion:.1f}%
            </td>

        </tr>

        """


    if not table_rows:

        table_rows = """

        <tr>

            <td colspan="4">

                아직 유입 데이터가 없습니다.

            </td>

        </tr>

        """


    html = f"""

<!DOCTYPE html>

<html lang="ko">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1"
>

<title>
분양노크 유입 대시보드
</title>


<style>

body {{

    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        "Noto Sans KR",
        sans-serif;

    background: #f7f8fa;

    margin: 0;

    color: #111;

}}

.wrap {{

    max-width: 1100px;

    margin: 60px auto;

    padding: 0 25px;

}}

h1 {{

    font-size: 36px;

    letter-spacing: -1px;

}}

.description {{

    color: #666;

    margin-bottom: 30px;

}}

.links {{

    padding: 20px;

    background: #fff;

    border-radius: 15px;

    margin-bottom: 25px;

    line-height: 1.9;

}}

code {{

    background: #f1f3f5;

    padding: 5px 8px;

    border-radius: 6px;

}}

table {{

    width: 100%;

    border-collapse: collapse;

    background: white;

    border-radius: 15px;

    overflow: hidden;

}}

th,
td {{

    padding: 18px;

    border-bottom:
        1px solid
        #eeeeee;

    text-align: center;

}}

th {{

    background: #fafafa;

}}

</style>

</head>


<body>

<div class="wrap">

<h1>
분양노크 유입 대시보드
</h1>


<div class="description">

홍보 채널별 방문 →
오픈채팅 클릭 전환을 확인합니다.

</div>


<div class="links">

<strong>
홍보 링크 예시
</strong>

<br>

네이버 블로그:
<code>
{BASE_URL}/go/naver01
</code>

<br>

네이버 카페:
<code>
{BASE_URL}/go/cafe01
</code>

<br>

인스타그램:
<code>
{BASE_URL}/go/instagram01
</code>

<br>

유튜브:
<code>
{BASE_URL}/go/youtube01
</code>

</div>


<table>

<thead>

<tr>

<th>
유입 코드
</th>

<th>
방문
</th>

<th>
오픈채팅 클릭
</th>

<th>
전환율
</th>

</tr>

</thead>


<tbody>

{table_rows}

</tbody>

</table>

</div>

</body>

</html>

"""

    return HTMLResponse(html)


# =========================================================
# Render Health Check
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "bunyangknock"
    }
