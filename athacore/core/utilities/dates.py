from datetime import timedelta

format_map = {
    "1min": "1m",
    "5min": "5m",
    "15min": "15m",
    "30min": "30m",
    "1h": "1h",
    "1d": "1d",
    "1w": "1wk",
    "1m": "1mo"
}

def to_timedelta(interval_str):
    """
    Convierte strings tipo '1m', '30m', '1h', '1d', '1wk', '1mo' a timedelta.
    Solo soporta minutos, horas, días y semanas.
    """
    try:
        # Mapeamos si nos dan la clave larga
        if interval_str in format_map:
            interval_str = format_map[interval_str]

        # Extraer número y unidad
        number = int(''.join(filter(str.isdigit, interval_str)))
        unit = ''.join(filter(str.isalpha, interval_str))

        if unit == "m":  # minutos
            return timedelta(minutes=number)
        elif unit == "h":  # horas
            return timedelta(hours=number)
        elif unit == "d":  # días
            return timedelta(days=number)
        elif unit == "wk":  # semanas
            return timedelta(weeks=number)
        elif unit == "mo":  # meses no soportado en timedelta, asumimos 30 días
            return timedelta(days=30 * number)
        else:
            raise ValueError(f"Unidad no soportada: {unit}")

    except Exception as e:
        print(f"Error procesando '{interval_str}': {e}")
        return None