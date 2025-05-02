from athacore.analisis.datos.fuente_datos import obtener_datos
from athacore.decisiones.estrategias.estrategia_basica_medias import estrategia_basica_medias


def ejecutar_analisis(estrategia, ticker, inicio, fin):
    print(f"📊 ANALISIS — Estrategia: {estrategia} — Ticker: {ticker} — Periodo: {inicio} a {fin}")

    df = obtener_datos(ticker, inicio, fin)
    if df.empty:
        print("❌ No se pudieron obtener datos.")
        return

    if estrategia == "estrategia_basica_medias":
        señales = estrategia_basica_medias(df)
    else:
        print(f"❌ Estrategia no implementada: {estrategia}")
        return

    print("📋 Señales generadas:")
    for fecha, señal in señales:
        print(f"{fecha.date()} → {señal}")

    print(f"✅ Total señales generadas: {len(señales)}")


if __name__ == "__main__":
    ejecutar_analisis()
