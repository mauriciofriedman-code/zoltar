from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Importar tus rutas desde backend
from backend.routes.generate import router as generate_router
from backend.routes.teacher import router as teacher_router
from backend.routes.answer import router as answer_router

app = FastAPI(title="ZOLTAR • Dos Chatbots", version="1.0.0")

# ========================================
# CORS Configuración
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, puedes limitar esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# Rutas de API
# ========================================
app.include_router(generate_router, prefix="/api", tags=["generate"])
app.include_router(teacher_router,  prefix="/api", tags=["teacher"])
app.include_router(answer_router,   prefix="/api", tags=["answer"])

@app.get("/health")
def health():
    return {"status": "healthy"}

# ========================================
# Servir Archivos Estáticos
# ========================================
frontend_dir = Path(__file__).resolve().parent / "frontend"
static_dir = frontend_dir / "static"

# Servir carpetas de recursos estáticos
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/img", StaticFiles(directory=static_dir / "img"), name="img")
app.mount("/sounds", StaticFiles(directory=static_dir / "sounds"), name="sounds")

# ========================================
# Servir index.html (desde carpeta raíz /frontend)
# ========================================
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>Frontend no encontrado</h1>", status_code=404)

