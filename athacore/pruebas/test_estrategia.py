from athacore.analisis.datos.fuente_datos import obtener_datos
from athacore.decisiones.estrategias.estrategia_basica_medias import estrategia_basica_medias

def test_basico():
    df = obtener_datos("AAPL", "2023-01-01", "2023-12-31")
    señales = estrategia_basica_medias(df)
    assert isinstance(señales, list)
    print(f"✅ Test OK: {len(señales)} señales detectadas")

if __name__ == "__main__":
    test_basico()
