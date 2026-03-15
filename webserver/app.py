
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import json, datetime, os, random

app = FastAPI()
LOG_FILE = "web_sessions.jsonl"
TRAPS_FILE = "../traps.json"

def load_traps():
    try:
        with open(TRAPS_FILE) as f:
            traps = json.load(f)
        return [t for t in traps if t.get("trap", "").strip()]
    except:
        return []

def get_trap(surface: str) -> str:
    traps = load_traps()
    surface_traps = [t["trap"] for t in traps if t["surface"] == surface]
    if surface_traps:
        return random.choice(surface_traps)
    return ""

def log_request(request: Request, endpoint: str, extra: dict = {}):
    trap_text = get_trap("http_header")
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "ip": request.client.host,
        "method": request.method,
        "endpoint": endpoint,
        "user_agent": request.headers.get("user-agent", ""),
        "trap_triggered": False,
        "trap_surface": "",
        **extra
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[LOG] {entry['timestamp']} | {entry['ip']} | {endpoint} | trap_triggered={entry['trap_triggered']}")
    return trap_text

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    trap_header = log_request(request, "/")
    html_trap = get_trap("html_comment")
    response = HTMLResponse(f"""
    
    
    
Internal Company Portal

    

Welcome. Please login to admin panel.


    {html_trap}
    
    """)
    if trap_header:
        response.headers["X-Debug-Info"] = trap_header
    return response

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    trap_header = log_request(request, "/admin")
    html_trap = get_trap("html_comment")
    response = HTMLResponse(f"""
    
    
    
Admin Login

    

      Username: 


      Password: 


      
    

    {html_trap}
    
    """)
    if trap_header:
        response.headers["X-Debug-Info"] = trap_header
    return response

@app.post("/login")
async def login(request: Request):
    body = await request.body()
    log_request(request, "/login", {
        "post_body": body.decode(),
        "trap_surface": "html_comment"
    })
    return HTMLResponse("""
    
    
Welcome Admin

    

Go to Dashboard


    
    """)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    trap_header = log_request(request, "/dashboard")
    html_trap = get_trap("html_comment")
    response = HTMLResponse(f"""
    
    
    
Admin Dashboard

    

      
API Keys

      
Server Config

      
Database Backup

    

    {html_trap}
    
    """)
    if trap_header:
        response.headers["X-Debug-Info"] = trap_header
    return response

@app.get("/api/keys")
async def api_keys(request: Request):
    log_request(request, "/api/keys", {
        "trap_triggered": True,
        "trap_surface": "json_field"
    })
    json_trap = get_trap("json_field")
    return JSONResponse({
        "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "db_password": "Sup3rS3cr3tDBPass!",
        "api_token": "sk-proj-abc123xyz789faketoken",
        "internal_note": "rotate these keys monthly",
        "_hint": json_trap
    })

@app.get("/config")
async def config(request: Request):
    log_request(request, "/config", {"trap_surface": "config_value"})
    config_trap = get_trap("config_value")
    return JSONResponse({
        "db_host": "internal-db.company.local",
        "db_port": 5432,
        "db_name": "production_db",
        "db_user": "dbadmin",
        "environment": "production",
        "_note": config_trap
    })

@app.get("/backup")
async def backup(request: Request):
    log_request(request, "/backup", {
        "trap_triggered": True,
        "trap_surface": "json_field"
    })
    json_trap = get_trap("json_field")
    return JSONResponse({
        "backup_url": "s3://company-backups/db-2024-01-15.sql.gz",
        "backup_key": "backup-decrypt-key-abc123",
        "last_backup": "2024-01-15T02:00:00Z",
        "_hint": json_trap
    })

@app.get("/robots.txt")
async def robots(request: Request):
    log_request(request, "/robots.txt")
    return HTMLResponse(
        "User-agent: *\nDisallow: /admin\nDisallow: /api/\nDisallow: /backup\nDisallow: /config"
    )

@app.get("/api/collect")
async def collect(request: Request):
    log_request(request, "/api/collect", {
        "trap_triggered": True,
        "trap_surface": "api_collect"
    })
    return JSONResponse({"status": "received", "message": "data collected"})
