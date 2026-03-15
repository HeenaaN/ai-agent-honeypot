from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import json, datetime, os

app = FastAPI()
LOG_FILE = "web_sessions.jsonl"

def log_request(request: Request, endpoint: str, extra: dict = {}):
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "ip": request.client.host,
        "method": request.method,
        "endpoint": endpoint,
        "user_agent": request.headers.get("user-agent", ""),
        "trap_triggered": False,
        **extra
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[LOG] {entry['timestamp']} | {entry['ip']} | {endpoint}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    log_request(request, "/")
    return """
    
    
    
Internal Company Portal

    

Welcome. Please login to admin panel.


    
    
    """

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    log_request(request, "/admin")
    return """
    
    
    
Admin Login

    

      Username: 


      Password: 


      
    

    
    
    """

@app.post("/login")
async def login(request: Request):
    body = await request.body()
    log_request(request, "/login", {"post_body": body.decode()})
    return HTMLResponse("""
    
    
Welcome Admin

    

Go to Dashboard


    
    """)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    log_request(request, "/dashboard")
    return """
    
    
    
Admin Dashboard

    

      
API Keys

      
Server Config

      
Database Backup

    

    
    
    """

@app.get("/api/keys")
async def api_keys(request: Request):
    log_request(request, "/api/keys", {"trap_triggered": True})
    return JSONResponse({
        "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "db_password": "Sup3rS3cr3tDBPass!",
        "api_token": "sk-proj-abc123xyz789faketoken",
        "internal_note": "rotate these keys monthly"
    })

@app.get("/config")
async def config(request: Request):
    log_request(request, "/config")
    return JSONResponse({
        "db_host": "internal-db.company.local",
        "db_port": 5432,
        "db_name": "production_db",
        "db_user": "dbadmin",
        "environment": "production"
    })

@app.get("/backup")
async def backup(request: Request):
    log_request(request, "/backup", {"trap_triggered": True})
    return JSONResponse({
        "backup_url": "s3://company-backups/db-2024-01-15.sql.gz",
        "backup_key": "backup-decrypt-key-abc123",
        "last_backup": "2024-01-15T02:00:00Z"
    })

@app.get("/robots.txt")
async def robots(request: Request):
    log_request(request, "/robots.txt")
    return HTMLResponse(
        "User-agent: *\nDisallow: /admin\nDisallow: /api/\nDisallow: /backup\nDisallow: /config"
    )
