from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent  # points to project root (pvninja)
templates = Jinja2Templates(directory=str(BASE_DIR / "ui" / "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/stream")
async def stream():
    async def event_generator():
        for i in range(10):
            yield {"data": f"Message {i}"}
            await asyncio.sleep(1)  # simulate some work
    return EventSourceResponse(event_generator())

@app.post("/submit")
async def receive_data(request: Request):
    data = await request.json()
    print("Received from frontend:", data)
    return {"status": "ok", "echo": data}
