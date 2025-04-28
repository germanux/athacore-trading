from athacore.analisis.datos.fuente_datos import obtener_datos
from athacore.decisiones.estrategias.estrategia_basica_medias import estrategia_basica_medias
import os

def ejecutar_simulacion(ticker, inicio, fin, estrategia):
    df = obtener_datos(ticker, inicio, fin)
    if df.empty:
        return

    if estrategia == "estrategia_basica_medias":
        señales = estrategia_basica_medias(df)
    else:
        print("❌ Estrategia no encontrada.")
        return

    for fecha, señal in señales:
        print(f"{fecha.date()} → {señal}")
    print(f"✅ Total señales: {len(señales)}")

if __name__ == "__main__":
    estrategia = os.getenv("ESTRATEGIA", "estrategia_basica_medias")
    ticker = os.getenv("TICKER", "AAPL")
    inicio = os.getenv("FECHA_INICIO", "2023-01-01")
    fin = os.getenv("FECHA_FIN", "2023-12-31")
    ejecutar_simulacion(ticker, inicio, fin, estrategia)
