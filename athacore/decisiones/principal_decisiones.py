import os
from athacore.analisis.datos.fuente_datos import obtener_datos
from athacore.decisiones.estrategias.estrategia_basica_medias import estrategia_basica_medias
from athacore.ejecucion.principal_ejecucion import ejecutar_orden_simulada, ejecutar_orden_real_ibkr


def ejecutar_decision():
    estrategia = os.getenv("ESTRATEGIA", "estrategia_basica_medias")
    ticker = os.getenv("TICKER", "AAPL")
    modo = os.getenv("MODO_OPERACION", "test")

    print(f"🧠 MODO: {modo.upper()} — Estrategia: {estrategia} — Ticker: {ticker}")

    df = obtener_datos(ticker, "2023-01-01", "2023-12-31")
    if df.empty:
        print("❌ No se pudieron obtener datos.")
        return

    if estrategia == "estrategia_basica_medias":
        señales = estrategia_basica_medias(df)
    else:
        print(f"❌ Estrategia no implementada: {estrategia}")
        return

    if modo == "test":
        print("📋 Señales generadas (solo evaluación):")
        for fecha, señal in señales:
            print(f"{fecha.date()} → {señal}")
    elif modo in ["simulacion", "real"]:
        for fecha, señal in señales:
            print(f"{fecha.date()} → {señal}")
            if modo == "simulacion":
                ejecutar_orden_simulada(señal, ticker)
            elif modo == "real":
                ejecutar_orden_real_ibkr(señal, ticker)
    else:
        print(f"❌ Modo desconocido: {modo}")


if __name__ == "__main__":
    ejecutar_decision()
