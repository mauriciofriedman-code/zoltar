# test_pipeline.py
import importlib
import pkgutil
from pathlib import Path
from backend import config

print("=== 🔍 TEST DEL PIPELINE RAG ===")

# --- Rutas principales ---
print(f"BASE_DIR:   {config.BASE_DIR}")
print(f"DOCS_DIR:   {config.DOCS_DIR} -> {'✅ existe' if config.DOCS_DIR.exists() else '❌ no existe'}")
print(f"CHROMA_DIR: {config.CHROMA_DIR} -> {'✅ existe' if config.CHROMA_DIR.exists() else '❌ no existe'}")

# --- Listar PDFs en DOCS_DIR ---
if config.DOCS_DIR.exists():
    pdfs = list(config.DOCS_DIR.glob("*.pdf"))
    if pdfs:
        print("\n📑 Archivos PDF encontrados:")
        for pdf in pdfs:
            print(" -", pdf)
    else:
        print("\n⚠️ No hay PDFs en DOCS_DIR.")
else:
    print("\n⚠️ DOCS_DIR no existe.")

# --- Listar archivos en CHROMA_DIR ---
if config.CHROMA_DIR.exists():
    files = list(config.CHROMA_DIR.glob("*"))
    if files:
        print(f"\n📦 Archivos en CHROMA_DIR ({len(files)}):")
        for f in files:
            print(" -", f)
    else:
        print("\n⚠️ CHROMA_DIR está vacío (se llenará tras la ingesta).")
else:
    print("\n⚠️ CHROMA_DIR no existe todavía.")

# --- Verificar módulo retrieve ---
print("\n=== 🔍 Verificación del módulo retrieve ===")
try:
    module = importlib.import_module("backend.routes.retrieve")
    print("✅ backend.routes.retrieve se importó correctamente.")

    if hasattr(module, "get_retriever"):
        print("✅ Función get_retriever encontrada en retrieve.py")
    else:
        print("❌ No se encontró la función get_retriever en retrieve.py")

    if hasattr(module, "ingest_docs"):
        print("✅ Función ingest_docs encontrada en retrieve.py")
    else:
        print("⚠️ No se encontró la función ingest_docs en retrieve.py")

except ModuleNotFoundError:
    print("❌ No existe el módulo backend.routes.retrieve")

# --- Listar todos los módulos de backend.routes ---
print("\n=== 📂 Archivos en backend/routes/ ===")
routes_path = Path(config.BASE_DIR) / "routes"
if routes_path.exists():
    for module_info in pkgutil.iter_modules([str(routes_path)]):
        print(" -", module_info.name)
else:
    print("⚠️ No existe la carpeta backend/routes")
