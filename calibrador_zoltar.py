import re
from pathlib import Path

# === Calibración Zoltar ===
calibracion = {
    "gabinete-bg": {
        "top": "-55px",
        "left": "-100px",
        "width": "100%"
    },
    "zoltar-img": {
        "top": "220px",
        "left": "240px",
        "width": "35%"
    },
    "coin-slot": {
        "bottom": "40px",
        "left": "410px"
    },
    "coinBtn": {
        "width": "60px",
        "height": "60px"
    },
    "slot": {
        "width": "28px",
        "height": "60px"
    }
}

# Ruta al archivo CSS
css_path = Path("backend/frontend/static/style.css")

if not css_path.exists():
    print(f"❌ El archivo {css_path} no existe.")
    exit(1)

css_content = css_path.read_text(encoding="utf-8")

# Función para reemplazar un bloque de clase completo
def reemplazar_estilos(clase, nuevas_prop):
    pattern = re.compile(rf"\.{clase}\s*\{{(.*?)\}}", re.DOTALL)
    propiedades = "\n  ".join(f"{k}: {v};" for k, v in nuevas_prop.items())
    nuevo_bloque = f".{clase} {{\n  {propiedades}\n}}"
    return pattern.sub(nuevo_bloque, css_content)

# Reemplazo de cada clase
css_content = reemplazar_estilos("gabinete-bg", calibracion["gabinete-bg"])
css_content = reemplazar_estilos("zoltar-img", calibracion["zoltar-img"])
css_content = reemplazar_estilos("coin-slot", calibracion["coin-slot"])

# Reemplazo específico para ID coinBtn
css_content = re.sub(
    r"#coinBtn\s*\{.*?\}", 
    "#coinBtn {\n  width: 60px;\n  height: 60px;\n  cursor: pointer;\n  transition: transform 0.2s;\n}", 
    css_content,
    flags=re.DOTALL
)

# Reemplazo específico para ID slot
css_content = re.sub(
    r"#slot\s*\{.*?\}",
    "#slot {\n  width: 28px;\n  height: 60px;\n  background: linear-gradient(180deg, #333, #000);\n"
    "  border: 2px solid #888;\n  border-radius: 4px;\n  box-shadow: inset 0 0 10px #000;\n  position: relative;\n}",
    css_content,
    flags=re.DOTALL
)

# Guardar el archivo
css_path.write_text(css_content, encoding="utf-8")
print("✅ Archivo style.css calibrado con éxito.")







