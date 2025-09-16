from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from backend.routes.generate import router as generate_router
from backend.routes.teacher import router as teacher_router
from backend.routes.answer import router as answer_router

app = FastAPI(title="ZOLTAR • Dos Chatbots", version="1.0.0")

# ========================================
# CORS Config
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# API Routes
# ========================================
app.include_router(generate_router, prefix="/api", tags=["generate"])
app.include_router(teacher_router,  prefix="/api", tags=["teacher"])
app.include_router(answer_router,   prefix="/api", tags=["answer"])

@app.get("/health")
def health():
    return {"status": "healthy"}

# ========================================
# Serve Static Frontend (HTML, JS, CSS, IMG, Sounds)
# ========================================
frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
static_dir = frontend_dir / "static"

# Serve static files (images, sounds, js, css)
app.mount("/img", StaticFiles(directory=static_dir / "img"), name="img")
app.mount("/sounds", StaticFiles(directory=static_dir / "sounds"), name="sounds")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)
