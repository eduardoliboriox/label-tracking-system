import time
import requests

URL = "https://sistema-de-rastreabilidade-via-etiquetas.onrender.com"

while True:
    try:
        r = requests.get(URL)
        print("Ping OK:", r.status_code)
    except Exception as e:
        print("Erro:", e)
    time.sleep(300)  # 5 minutos
