from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Rutas de API
from backend.routes.generate import router as generate_router
from backend.routes.teacher import router as teacher_router
from backend.routes.answer import router as answer_router  # (opcional)

# Crear la app
app = FastAPI(
    title="ZOLTAR • Dos Chatbots",
    version="1.0.0"
)

# ========================================
# Middleware CORS (permite llamadas del frontend)
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ En producción reemplaza con la URL real del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# Incluir rutas de la API
# ========================================
app.include_router(generate_router, prefix="/api", tags=["generate"])  # Chat simple
app.include_router(teacher_router,  prefix="/api", tags=["teacher"])   # Chat con RAG
app.include_router(answer_router,   prefix="/api", tags=["answer"])    # Extra (si lo usas)

# ========================================
# Ruta de prueba para saber si está corriendo
# ========================================
@app.get("/health")
def health():
    return {"status": "healthy"}

# ========================================
# Servir frontend y archivos estáticos
# ========================================
# Ruta absoluta al directorio frontend
frontend_dir = Path(__file__).resolve().parent / "frontend"
static_dir = frontend_dir / "static"

# Montar recursos estáticos
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/img", StaticFiles(directory=static_dir / "img"), name="img")
app.mount("/sounds", StaticFiles(directory=static_dir / "sounds"), name="sounds")

# Servir el index.html si accedes a "/"
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"), status_code=200)
    return HTMLResponse("<h1>Frontend no encontrado</h1>", status_code=404)

