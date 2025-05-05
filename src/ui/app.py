from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE = Path(__file__).parent
app  = FastAPI(title="PVNINJA‑UI")

# Serve the SPA / static assets
app.mount("/static", StaticFiles(directory=BASE/"static"), name="static")

@app.get("/")
def index():
    return FileResponse(BASE/"static"/"index.html")
