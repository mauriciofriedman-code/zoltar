from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Importar rutas desde backend
from backend.routes.generate import router as generate_router
from backend.routes.teacher import router as teacher_router
from backend.routes.answer import router as answer_router

# Crear instancia de la app
app = FastAPI(title="ZOLTAR • Dos Chatbots", version="1.0.0")

# ========================================
# Configuración de CORS
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: reemplaza con el dominio real
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

# ========================================
# Ruta de salud
# ========================================
@app.get("/health")
def health():
    return {"status": "healthy"}

# ========================================
# Servir Archivos Estáticos y Frontend
# ========================================
frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
static_dir = frontend_dir / "static"

# Servir carpetas de recursos estáticos
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/img", StaticFiles(directory=static_dir / "img"), name="img")
app.mount("/sounds", StaticFiles(directory=static_dir / "sounds"), name="sounds")

# ========================================
# Servir index.html en "/"
# ========================================
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse("<h1>Frontend not found</h1>", status_code=404)
