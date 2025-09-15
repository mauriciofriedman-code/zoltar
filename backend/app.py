from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.ingest import ensure_index
from backend.routes.generate import router as generate_router
from backend.routes.teacher import router as teacher_router
from backend.routes.answer import router as answer_router

# ========================================
# Crear la aplicación
# ========================================
app = FastAPI(title="ZOLTAR • Dos Chatbots", version="1.0.0")

# ========================================
# Configuración CORS
# ========================================
# Al servir frontend y backend en el mismo dominio, puedes relajar CORS.
# Si prefieres, reemplaza ["*"] por la URL final que Render te asigne.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# Rutas API
# ========================================
app.include_router(generate_router, prefix="/api", tags=["generate"])
app.include_router(teacher_router,  prefix="/api", tags=["teacher"])
app.include_router(answer_router,   prefix="/api", tags=["answer"])

@app.get("/health")
def health():
    return {"status": "healthy"}

# ========================================
# Startup: construir índice si falta
# ========================================
@app.on_event("startup")
async def _startup_build_index_if_needed():
    try:
        ensure_index()
    except Exception as e:
        print(f"[startup] No se pudo construir el índice automáticamente: {e}")

# ========================================
# Servir frontend estático
# ========================================
# Monta la carpeta 'frontend' en la raíz '/'
# Importante: NO definas un @app.get("/") adicional.
frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
