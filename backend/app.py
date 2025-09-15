from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción podrías poner tu dominio
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
# Servir frontend estático
# ========================================
frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


