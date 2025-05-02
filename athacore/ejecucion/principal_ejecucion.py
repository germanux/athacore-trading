def ejecutar_orden_simulada(señal, ticker):
    # Aquí se integrará con Interactive Brokers en el futuro para el modo simulado
    print(f"📄 Simulando orden: {señal} en {ticker}")


def ejecutar_orden_real_ibkr(señal, ticker):
    # Aquí se integrará con Interactive Brokers en el futuro para el modo real
    print(f"📢 Ejecutando orden REAL: {señal} en {ticker}")


def ejecutar_desde_estrategia(señal, ticker, modo):
    if modo == "simulacion":
        ejecutar_orden_simulada(señal, ticker)
    elif modo == "real":
        ejecutar_orden_real_ibkr(señal, ticker)
    else:
        print(f"❌ Modo desconocido: {modo}. Abortando ejecución.")
    print("✅ Ejecución completada.")


if __name__ == "__main__":
    ejecutar_desde_estrategia()
