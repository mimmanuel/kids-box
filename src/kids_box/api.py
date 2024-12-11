import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from kids_box.spotify import get_authorize_url, get_devices, parse_tokens, start_song, is_authenticated


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create a task that runs in the background
    task = asyncio.create_task(background_task())
    
    try:
        yield
    finally:
        # Cancel the task when the application shuts down
        _ = task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def background_task():
    count = 0
    try:
        while True:
            print(count)
            await asyncio.sleep(5)
            count = count + 1
            if count > 600:
                break
    except asyncio.CancelledError:
        print("Background task was cancelled")


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def handle_root(request: Request):
    if not is_authenticated():
        return RedirectResponse(url="/auth")

    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/devices", response_class=HTMLResponse)
async def handle_devices(request: Request):
    devices = get_devices()

    ctx = {
            "devices": [{"name": d["name"], "id": d["id"]} for d in devices],
            "request": request
            }

    return templates.TemplateResponse(name="devices.html", context=ctx)

@app.post("/play", response_class=HTMLResponse)
async def handle_play(device: Annotated[str, Form()]):
    print(device)
    try:
        start_song(device)
    except Exception as e:
        return HTMLResponse(f"Could not start {e}")

    return HTMLResponse("Started!")


@app.get("/auth")
async def auth():
    authorize_url = get_authorize_url()
    return HTMLResponse(content=f'<a href="{authorize_url}">Authorize Spotify</a>')


@app.get("/callback", response_class=RedirectResponse)
async def callback(request: Request):
    global access_token, refresh_token
    code = request.query_params.get("code")

    if not code:
        return RedirectResponse(status_code=500, url="/")

    try:
        await parse_tokens(code)
    except Exception as e:
        return RedirectResponse(status_code=500, url="/")

    return RedirectResponse(url="/")
