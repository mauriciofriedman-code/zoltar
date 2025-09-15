import os
from pathlib import Path
from dotenv import load_dotenv

# ============================
# Carga variables de entorno
# ============================
load_dotenv()

# ========================================
# Paths base
# ========================================

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

# DATA_DIR puede venir de variable de entorno (ej. /data en Render con Disk)
DATA_DIR = Path(os.getenv("DATA_DIR", str(BACKEND_DIR / "data")))

# Subcarpetas
DOCS_DIR = DATA_DIR / "docs"
CHROMA_DIR = DATA_DIR / "chroma"

# Asegura que existan
DOCS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ========================================
# Modelos y parámetros de embeddings/chat
# ========================================

# Proveedor de embeddings (ej: "openai")
EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", "openai")

# Modelo de embeddings por defecto
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-large")

# Modelo de chat por defecto
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# Temperatura para generación (0 = determinista, >0 = más creativo)
CHAT_TEMPERATURE = float(os.getenv("CHAT_TEMPERATURE", "0.2"))

# ========================================
# CORS
# ========================================

# Durante pruebas: "*"
# En producción: pon la URL real del frontend
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")








