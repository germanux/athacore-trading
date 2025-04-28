# 📈 ATHACORE – Plataforma modular de trading algorítmico

Sistema estructurado por módulos para backtesting, decisión y ejecución de operaciones.

---

## 🚀 Requisitos iniciales

1. Python 3.10+
2. Crear y activar entorno virtual:

```bash
# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar entorno (modo simplificado):

```bash
# Windows
setup.bat

# Linux / Mac
./setup.sh
```

---

## 🧠 ¿Qué hace cada módulo?

| Módulo           | Ruta                              | Función principal                                |
|------------------|-----------------------------------|--------------------------------------------------|
| Análisis         | `athacore/analisis/`              | Simulación y métricas sobre históricos          |
| Decisiones       | `athacore/decisiones/`            | Motor de estrategias (reglas, IA, señales)      |
| Ejecución        | `athacore/ejecucion/`             | Ejecuta órdenes reales o en modo demo           |
| Interfaz gráfica | `main.py`                         | UI web con NiceGUI para controlar todo          |

---

## 💻 Uso general (con interfaz web)

Lanza la app con NiceGUI:

```bash
python main.py
```

Luego abre tu navegador en: [http://localhost:8080](http://localhost:8080)

Ahí podrás:
- Elegir una estrategia (ej: cruce de medias)
- Seleccionar modo: `simulación`, `real` o `test`
- Ver notificaciones del sistema

---

## ⚙️ Variables opcionales por entorno (modo simulación)

Puedes configurar variables de entorno para ajustar los datos:

```bash
set ESTRATEGIA=estrategia_basica_medias
set TICKER=AAPL
set FECHA_INICIO=2023-01-01
set FECHA_FIN=2023-12-31
```

---

## 📁 Estructura recomendada

```
/athacore/
├── analisis/              # Módulo Athalyzer (backtesting)
├── decisiones/            # Módulo Athavest (estrategias)
├── ejecucion/             # Módulo Tradergon (broker/demo)
├── interfaz/              # NiceGUI (opcional si main.py crece mucho)
├── config/                # Parámetros y entorno
├── logs/                  # Logs de operaciones y errores
├── pruebas/               # Tests técnicos

main.py                   # Punto de entrada global (UI)
requirements.txt          # Librerías necesarias
README.md                 # Este documento
.gitignore                # Exclusiones para Git
setup.sh                  # Script Linux/Mac para entorno
setup.bat                 # Script Windows para entorno
verificacion.md           # ✅ Checklist de pruebas del sistema
```

---

## ✅ Estado actual

- [x] Interfaz web básica lista
- [x] Estrategia simple funcional (cruce de medias)
- [x] Descarga de datos históricos con yfinance
- [ ] Conexión a broker real (IBKR)
- [ ] Sistema completo de métricas y visualización

---

## 🔧 Verificación del sistema

Puedes usar el documento `verificacion.md` para comprobar paso a paso que todo está correctamente montado:

```bash
start verificacion.md   # En Windows
# o
open verificacion.md    # En Mac
# o
xdg-open verificacion.md  # En Linux
```

---

## 👨‍💼 Autor / Contacto

> Proyecto educativo y experimental  
> Versión inicial modularizada 2025