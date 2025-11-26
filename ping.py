import time
import requests

URL = "https://label-tracking-system.onrender.com"

while True:
    try:
        r = requests.get(URL)
        print("Ping OK:", r.status_code)
    except Exception as e:
        print("Erro:", e)
    time.sleep(600)  # 10 minutos
