from athacore.analisis.datos.fuente_datos import obtener_datos
from athacore.decisiones.estrategias.estrategia_basica_medias import estrategia_basica_medias
from athacore.ejecucion import principal_ejecucion


def ejecutar_decision(estrategia, ticker, modo):
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
        print(f"🚀 Modo de ejecución: {modo.upper()}")
        for fecha, señal in señales:
            print(f"{fecha.date()} → {señal}")
            principal_ejecucion.ejecutar_desde_estrategia(señal, ticker, modo)
    else:
        print(f"❌ Modo desconocido: {modo}")


if __name__ == "__main__":
    ejecutar_decision()
