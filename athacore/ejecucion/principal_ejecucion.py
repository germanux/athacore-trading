import os

def ejecutar_orden(señal, ticker):
    # Simulación de ejecución (puedes conectar con IBKR aquí en el futuro)
    print(f"📤 Ejecutando orden: {señal} en {ticker}")


def ejecutar_desde_estrategia():
    # Ejemplo de señales que normalmente vendrían del motor de decisiones
    señales = [("2023-06-01", "BUY"), ("2023-08-15", "SELL")]
    ticker = os.getenv("TICKER", "AAPL")

    print("🚀 Modo REAL/DEMO – Simulación de ejecución de órdenes")
    for fecha, señal in señales:
        print(f"{fecha} → {señal}")
        ejecutar_orden(señal, ticker)

    print("✅ Ejecución finalizada.")


if __name__ == "__main__":
    ejecutar_desde_estrategia()
