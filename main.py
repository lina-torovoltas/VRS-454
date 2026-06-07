import os
import logging
import hashlib
import hmac

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.middleware.gzip import GZipMiddleware
from rcssmin import cssmin
import uvicorn

from libs.encoder import process_message
from libs.tables import gen_tables, generate_codemap
from logger import LOGGING_CONFIG

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)



# ==== CACHE ====

current_message_cache = None
history_cache = None
archive_cache = None
manager_guide_cache = None
robots_page_cache = None
previous_messages_cache = []



# === FILES ====

CALLSIGN_FILE = "data/callsign.txt"
HISTORY_FILE = "data/logs/history.txt"
LOGS_FILE = "data/logs/logs.txt"
PASSWORD_HASH_FILE = "data/password.hash"
MESSAGES_FILE = "data/messages.txt"
GUIDE_PAGE = "templates/guide.txt"
TEMP_FILE = "data/logs/temp.txt"
CODEMAP_FILE = "data/codemap.txt"



templates = Jinja2Templates(directory="templates")

os.makedirs("tables", exist_ok=True)
os.makedirs("data/logs", exist_ok=True)
os.makedirs("archives", exist_ok=True)

for name in ("history.txt", "logs.txt", "temp.txt"):
    path = f"data/logs/{name}"
    if not os.path.exists(path):
        open(path, "w").close()

if not os.path.exists(MESSAGES_FILE):
    open(MESSAGES_FILE, "w").close()

if not os.listdir("tables"):
    gen_tables()

if not os.path.exists(CODEMAP_FILE):
    generate_codemap(CODEMAP_FILE)

if os.path.exists(CALLSIGN_FILE):
    with open(CALLSIGN_FILE, "r", encoding="utf-8") as f:
        CALLSIGN = f.read().strip()
else:
    CALLSIGN = "VSR-454"

if os.path.exists(PASSWORD_HASH_FILE):
    with open(PASSWORD_HASH_FILE, "r", encoding="utf-8") as f:
        PASSWORD_HASH = f.read().strip()
else:
    PASSWORD_HASH = hashlib.sha256("change-password!".encode()).hexdigest()
    with open(PASSWORD_HASH_FILE, "w", encoding="utf-8") as f:
        f.write(PASSWORD_HASH)



# ==== FUNC ====


def check_password(password: str):
    hash_try = hashlib.sha256(password.encode()).hexdigest()
    if not hmac.compare_digest(hash_try, PASSWORD_HASH):
        raise HTTPException(status_code=403, detail="Wrong password")


def load_current_message():
    global current_message_cache

    if os.path.exists(TEMP_FILE):
        with open(TEMP_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if lines:
                current_message_cache = lines[-1]
            else:
                current_message_cache = "No messages yet."
    else:
        current_message_cache = "No messages yet."


def load_previous_messages():
    global previous_messages_cache

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            previous_messages_cache = lines[1:11] if len(lines) > 1 else []
    else:
        previous_messages_cache = []


def load_history():
    global history_cache

    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, "w").close()
        history_cache = ""
    else:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history_cache = f.read()
    return


def load_archive():
    global archive_cache

    folder = "archives"
    if not os.path.exists(folder):
        archive_cache = None
        return
    archives = sorted([f for f in os.listdir(folder) if f.startswith("archive_") and f.endswith(".tar.xz")])
    if archives:
        with open(os.path.join(folder, archives[-1]), "rb") as f:
            archive_cache = f.read()
    else:
        archive_cache = None


def load_guide():
    global manager_guide_cache

    if not os.path.exists(GUIDE_PAGE):
        open(GUIDE_PAGE, "w").close()
        manager_guide_cache = ""
    else:
        with open(GUIDE_PAGE, "r", encoding="utf-8") as f:
            manager_guide_cache = f.read()
    return



# === HTTP FUNC ===


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    if not previous_messages_cache:
        load_previous_messages()
    if current_message_cache is None:
        load_current_message()

    previous_messages_fmt = "</br>".join(previous_messages_cache)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_message": current_message_cache, 
            "previous_messages": previous_messages_fmt
        }
    )



# === HTTP FILES ===


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(
        "templates/favicon.svg",
        media_type="image/svg+xml"
    )


@app.get("/style.css", include_in_schema=False)
async def css():
    return FileResponse(
        "templates/style.css",
        media_type="text/css"
    )


@app.get("/manager_guide")
def get_guide():
    if manager_guide_cache is None:
        load_guide()
    return PlainTextResponse(manager_guide_cache)


@app.get("/history")
def get_history():
    if history_cache is None:
        load_history()
    return PlainTextResponse(history_cache)


@app.get("/logs")
def get_mlogs(password: str = Query(...)):
    check_password(password)

    if not os.path.exists(LOGS_FILE):
        open(LOGS_FILE, "w").close()
    return FileResponse(LOGS_FILE, media_type="text/plain")


@app.get("/archive")
async def get_archive():
    if archive_cache is None:
        load_archive()
    if archive_cache is None:
        return PlainTextResponse("No archive yet")
    return Response(content=archive_cache, media_type="application/x-xz")


@app.get("/queue")
async def get_queue(password: str = Query(...)):
    check_password(password)
    
    if not os.path.exists(MESSAGES_FILE):
        return PlainTextResponse("")
    
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    return PlainTextResponse(content)


# ===== POST =====


@app.post("/change_password")
async def change_password(request: Request):
    global PASSWORD_HASH
    data = await request.json()
    
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="Missing fields")
    
    check_password(old_password)
    new_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    with open(PASSWORD_HASH_FILE, "w", encoding="utf-8") as f:
        f.write(new_hash)
    
    PASSWORD_HASH = new_hash
    
    return {"status": "ok", "message": "Password changed successfully"}


@app.post("/regenerate_message")
async def regenerate_message(request: Request):
    data = await request.json()
    global current_message_cache


    password = data.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="No password provided")
    
    check_password(password)

    status = process_message(CALLSIGN)

    print(status)

    if status == "failure":
        return {"status": "empty"}

    current_message_cache = status
    load_history()
    load_previous_messages()

    return {"status": "ok"}


@app.post("/regenerate_tables")
async def regenerate_tables(request: Request):
    data = await request.json()
    
    password = data.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="No password provided")
    
    check_password(password)

    gen_tables()
    generate_codemap(CODEMAP_FILE)
    load_current_message()
    load_history()
    load_archive()

    return {"status": "ok"}


@app.post("/change_callsign")
async def change_callsign(request: Request):
    global CALLSIGN
    
    data = await request.json()
    
    password = data.get("password")
    new_callsign = data.get("callsign")
    if not password or not new_callsign:
        raise HTTPException(status_code=400, detail="Missing fields")
    
    check_password(password)

    CALLSIGN = new_callsign
    with open(CALLSIGN_FILE, "w", encoding="utf-8") as f:
        f.write(CALLSIGN)

    return {"status": "ok", "callsign": CALLSIGN}


@app.post("/add_messages")
async def add_messages(request: Request):
    data = await request.json()
    
    password = data.get("password")
    message = data.get("message")
    
    if not password or not message:
        raise HTTPException(status_code=400, detail="Missing fields")
    
    check_password(password)
    
    os.makedirs("data", exist_ok=True)
    
    with open(MESSAGES_FILE, "a", encoding="utf-8") as f:
        f.write(message.strip() + "\n")
    
    return {"status": "ok", "message": "Message added"}


@app.post("/clear_queue")
async def clear_queue(request: Request):
    data = await request.json()
    
    password = data.get("password")
    if not password:
        raise HTTPException(status_code=400, detail="No password provided")
    
    check_password(password)
    
    with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
        f.write("")
    
    return {"status": "ok", "message": "Queue cleared"}


# ===== HANDLERS =====


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return PlainTextResponse("What are you looking for here?",status_code=451)


@app.head("/")
async def head_index():
    return {"status": "ok"}


app.add_middleware(GZipMiddleware, minimum_size=200)


@app.middleware("http")
async def custom_headers(request, call_next):
    response = await call_next(request)
    if current_message_cache is None:
        load_current_message()
    response.headers["current-message"] = f"{current_message_cache}"
    response.headers["server"] = "VRS-454 Station Manager"

    if request.url.path.endswith(".css"):
        response.headers["Cache-Control"] = "public, max-age=600"
        response.headers["Pragma"] = "cache"
    return response



# ==== MAIN FUNC ====


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5501, reload=True, server_header=False, log_config=LOGGING_CONFIG)
