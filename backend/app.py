from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import time
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Utilidades
from backend.utils.logger import logger, log_request
from backend.config import FRONTEND_ORIGIN

# Rutas de API
from backend.routes.generate import router as generate_router
from backend.routes.teacher import router as teacher_router
from backend.routes.answer import router as answer_router  # (opcional)
from backend.routes.stream import router as stream_router

# Crear la app
app = FastAPI(
    title="ZOLTAR • Dos Chatbots",
    version="2.0.0",
    description="""
    ## Oráculo educativo con dos modos de operación:
    
    ### Oráculo Simple
    Respuestas directas sin contexto de documentos. Ideal para preguntas generales.
    
    ### Maestro Docente
    Respuestas basadas en RAG (Retrieval Augmented Generation) con documentos educativos.
    Proporciona respuestas fundamentadas en documentos académicos sobre IA y educación.
    
    ## Características principales:
    
    - ✅ **Streaming de respuestas**: Respuestas en tiempo real usando Server-Sent Events
    - ✅ **Caché inteligente**: Respuestas frecuentes se cachean para mejor rendimiento
    - ✅ **Rate limiting**: Protección contra abuso (20 req/min para simple, 15 req/min para RAG)
    - ✅ **Logging estructurado**: Monitoreo completo de peticiones y métricas
    - ✅ **Compresión gzip**: Respuestas comprimidas para menor ancho de banda
    - ✅ **Sanitización de entrada**: Protección contra XSS e inyecciones
    - ✅ **Validación robusta**: Validación de entrada en todos los endpoints
    
    ## Endpoints principales:
    
    - `POST /api/generate`: Chatbot simple (baseline/engineered)
    - `POST /api/teacher`: Chatbot con RAG basado en documentos
    - `GET /api/stream`: Streaming de respuestas (SSE)
    - `GET /api/cache/stats`: Estadísticas del caché
    - `POST /api/cache/clear`: Limpiar caché (solo desarrollo)
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========================================
# Rate Limiting
# ========================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ========================================
# Middleware CORS (permite llamadas del frontend)
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if FRONTEND_ORIGIN == "*" else [FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# Middleware de Compresión
# ========================================
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ========================================
# Middleware de Logging
# ========================================
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware para registrar todas las peticiones HTTP."""
    start_time = time.time()
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular duración
    duration_ms = (time.time() - start_time) * 1000
    
    # Registrar petición
    log_request(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=response.status_code,
        duration_ms=duration_ms,
        client_ip=get_remote_address(request)
    )
    
    return response

# ========================================
# Incluir rutas de la API
# ========================================
app.include_router(generate_router, prefix="/api", tags=["generate"])  # Chat simple
app.include_router(teacher_router,  prefix="/api", tags=["teacher"])   # Chat con RAG
app.include_router(answer_router,   prefix="/api", tags=["answer"])    # Extra (si lo usas)
app.include_router(stream_router,  prefix="/api", tags=["stream"])    # Streaming SSE

# ========================================
# Rutas de utilidad
# ========================================
@app.get("/health")
def health():
    """Endpoint de salud para verificar que el servidor está funcionando."""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/api/cache/stats")
def cache_stats():
    """Endpoint para ver estadísticas del caché (solo para desarrollo/debug)."""
    from backend.utils import get_cache_stats
    return get_cache_stats()

@app.post("/api/cache/clear")
def clear_cache_endpoint():
    """Endpoint para limpiar el caché (solo para desarrollo/debug)."""
    from backend.utils import clear_cache
    clear_cache()
    return {"message": "Caché limpiado exitosamente"}

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

