from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / "funnel.db"
OPENCHAT = "https://open.kakao.com/o/gSRhTTBi"

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE / "templates"))

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        kind TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    c.commit()
    return c

@app.get("/")
def root():
    return RedirectResponse("/admin")

@app.get("/go/{source}", response_class=HTMLResponse)
def landing(request: Request, source: str):
    c = connect()
    c.execute("INSERT INTO events(source,kind) VALUES(?,?)", (source, "visit"))
    c.commit()
    c.close()
    return templates.TemplateResponse(
        request=request,
        name="landing.html",
        context={"source": source}
    )

@app.get("/out/{source}")
def outbound(source: str):
    c = connect()
    c.execute("INSERT INTO events(source,kind) VALUES(?,?)", (source, "click"))
    c.commit()
    c.close()
    return RedirectResponse(OPENCHAT)

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    c = connect()
    rows = c.execute("""
        SELECT source,
        SUM(CASE WHEN kind='visit' THEN 1 ELSE 0 END) AS visits,
        SUM(CASE WHEN kind='click' THEN 1 ELSE 0 END) AS clicks
        FROM events
        GROUP BY source
        ORDER BY visits DESC
    """).fetchall()
    c.close()
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"rows": rows}
    )
