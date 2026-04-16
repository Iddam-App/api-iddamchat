from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routes import auth, files

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CloudDrive", docs_url="/api/docs")

app.include_router(auth.router)
app.include_router(files.router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}
