from athacore.analisis.datos.fuente_datos import obtener_datos
from athacore.decisiones.estrategias.estrategia_basica_medias import estrategia_basica_medias

if __name__ == "__main__":
    print("🧪 MODO TEST – Ejecutando estrategia básica")

    df = obtener_datos("AAPL", "2023-01-01", "2023-12-31")
    señales = estrategia_basica_medias(df)

    for fecha, señal in señales:
        print(f"{fecha.date()} → {señal}")

    print(f"✅ Test finalizado. Total señales: {len(señales)}")
