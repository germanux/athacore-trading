from dotenv import load_dotenv
import os

load_dotenv()  # Carga variables del archivo .env

api_key = os.getenv("FINNHUB_API_KEY")
print(f"Clave Finnhub cargada: {api_key}")
