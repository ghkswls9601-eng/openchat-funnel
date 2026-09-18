import os, sqlite3, secrets, csv, io, hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app=FastAPI()
app.mount("/static",StaticFiles(directory="static"),name="static")
templates=Jinja2Templates(directory="templates")

OPENCHAT_URL=os.getenv("OPENCHAT_URL","https://open.kakao.com/o/gSRhTTBi")
BASE_URL=os.getenv("BASE_URL","https://openchat-funnel.onrender.com").rstrip("/")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD","CHANGE-ME-NOW")
COOKIE_SECRET=os.getenv("COOKIE_SECRET","CHANGE-COOKIE-SECRET")
DB_PATH=os.getenv("DB_PATH","funnel.db")

def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init():
    c=conn()
    c.executescript("""CREATE TABLE IF NOT EXISTS events(
      id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT NOT NULL,kind TEXT NOT NULL,
      ts TEXT NOT NULL,iphash TEXT);
    CREATE TABLE IF NOT EXISTS campaigns(
      id INTEGER PRIMARY KEY AUTOINCREMENT,code TEXT UNIQUE NOT NULL,title TEXT NOT NULL,
      channel TEXT NOT NULL,created_at TEXT NOT NULL);""")
    c.commit(); c.close()
init()

def authed(r): return r.cookies.get("bk_admin")==COOKIE_SECRET
def iphash(r):
    raw=((r.client.host if r.client else "")+COOKIE_SECRET).encode()
    return hashlib.sha256(raw).hexdigest()[:16]
def log(r,source,kind):
    c=conn(); c.execute("INSERT INTO events(source,kind,ts,iphash) VALUES(?,?,?,?)",
      (source,kind,datetime.now().isoformat(timespec="seconds"),iphash(r))); c.commit(); c.close()

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("landing.html",{"request":request,"source":"direct","base_url":BASE_URL})

@app.get("/go/{source}",response_class=HTMLResponse)
def go(source:str,request:Request):
    log(request,source,"visit")
    return templates.TemplateResponse("landing.html",{"request":request,"source":source,"base_url":BASE_URL})

@app.get("/out/{source}")
def out(source:str,request:Request):
    log(request,source,"click")
    return RedirectResponse(OPENCHAT_URL,302)

@app.get("/login",response_class=HTMLResponse)
def login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request,"error":False})

@app.post("/login")
def login(request:Request,password:str=Form(...)):
    if secrets.compare_digest(password,ADMIN_PASSWORD):
        resp=RedirectResponse("/admin",303)
        resp.set_cookie("bk_admin",COOKIE_SECRET,httponly=True,samesite="lax",secure=True,max_age=43200)
        return resp
    return templates.TemplateResponse("login.html",{"request":request,"error":True},status_code=401)

@app.get("/logout")
def logout():
    r=RedirectResponse("/login",303); r.delete_cookie("bk_admin"); return r

def get_stats(days):
    since=(datetime.now()-timedelta(days=days)).isoformat(timespec="seconds")
    c=conn()
    rows=c.execute("""SELECT source,
      SUM(CASE WHEN kind='visit' THEN 1 ELSE 0 END) visits,
      SUM(CASE WHEN kind='click' THEN 1 ELSE 0 END) clicks
      FROM events WHERE ts>=? GROUP BY source ORDER BY clicks DESC,visits DESC""",(since,)).fetchall()
    camps={x["code"]:dict(x) for x in c.execute("SELECT * FROM campaigns").fetchall()}
    c.close()
    out=[]
    for x in rows:
        d=dict(x); d["rate"]=round(d["clicks"]*100/d["visits"],1) if d["visits"] else 0
        d["title"]=camps.get(d["source"],{}).get("title","")
        d["channel"]=camps.get(d["source"],{}).get("channel","")
        out.append(d)
    return out

@app.get("/admin",response_class=HTMLResponse)
def admin(request:Request,days:int=30):
    if not authed(request): return RedirectResponse("/login",303)
    days=days if days in (1,7,30) else 30
    rows=get_stats(days); visits=sum(x["visits"] for x in rows); clicks=sum(x["clicks"] for x in rows)
    camps=conn(); campaigns=camps.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall(); camps.close()
    return templates.TemplateResponse("admin.html",{"request":request,"rows":rows,"campaigns":campaigns,
      "days":days,"visits":visits,"clicks":clicks,"base_url":BASE_URL})

@app.post("/campaign")
def campaign(request:Request,title:str=Form(...),channel:str=Form(...),code:str=Form(...)):
    if not authed(request): return RedirectResponse("/login",303)
    safe="".join(x for x in code.lower().strip().replace(" ","-") if x.isalnum() or x in "-_")
    if safe:
        c=conn()
        try:
            c.execute("INSERT INTO campaigns(code,title,channel,created_at) VALUES(?,?,?,?)",
              (safe,title.strip(),channel.strip(),datetime.now().isoformat(timespec="seconds"))); c.commit()
        except sqlite3.IntegrityError: pass
        c.close()
    return RedirectResponse("/admin",303)

@app.get("/export.csv")
def export(request:Request):
    if not authed(request): return RedirectResponse("/login",303)
    c=conn(); rows=c.execute("SELECT id,source,kind,ts FROM events ORDER BY id DESC").fetchall(); c.close()
    s=io.StringIO(); w=csv.writer(s); w.writerow(["id","source","event","timestamp"])
    for x in rows:w.writerow(list(x))
    return StreamingResponse(iter([s.getvalue()]),media_type="text/csv",
      headers={"Content-Disposition":"attachment; filename=bunyangknock_stats.csv"})
