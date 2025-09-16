import requests

url = "https://zoltar-u7du.onrender.com/api/teacher"

payload = {
    "text": "¿Cómo aplicar el modelo UbD en un programa de estudios judaicos?",
    "history": ""
}

resp = requests.post(url, json=payload)

print("Código de estado:", resp.status_code)
print("Respuesta del servidor:", resp.json())
