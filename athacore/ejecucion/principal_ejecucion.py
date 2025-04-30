import os


def ejecutar_orden_simulada(señal, ticker):
    print(f"📄 Simulando orden: {señal} en {ticker}")


def ejecutar_orden_real_ibkr(señal, ticker):
    # Aquí se integrará con Interactive Brokers en el futuro
    print(f"📢 Ejecutando orden REAL: {señal} en {ticker}")


def ejecutar_desde_estrategia():
    modo = os.getenv("MODO_OPERACION", "simulacion")
    ticker = os.getenv("TICKER", "AAPL")

    # Señales de ejemplo (en el futuro vendrán del módulo de decisiones en tiempo real)
    señales = [("2023-06-01", "BUY"), ("2023-08-15", "SELL")]

    print(f"🚀 Modo de ejecución: {modo.upper()}")

    for fecha, señal in señales:
        print(f"{fecha} → {señal}")
        if modo == "simulacion":
            ejecutar_orden_simulada(señal, ticker)
        elif modo == "real":
            ejecutar_orden_real_ibkr(señal, ticker)
        else:
            print(f"❌ Modo desconocido: {modo}. Abortando ejecución.")
            break

    print("✅ Ejecución completada.")


if __name__ == "__main__":
    ejecutar_desde_estrategia()
