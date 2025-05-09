# Athacore Trading Project

Proyecto modular de sistema de trading algorítmico desarrollado en Python con NiceGUI para interfaz gráfica.

---

## 📁 Estructura del proyecto

```
athacore-trading/
├── core/
│   ├── data/
│   │   └── market_data.py          # Obtención de datos de mercado (yfinance)
│   ├── strategy/
│   │   └── strategy_engine.py      # Motor de estrategias (generar señales, ejecutar análisis)
│   ├── execution/
│   │   └── order_executor.py       # Ejecución de órdenes simuladas o reales
│   ├── backtesting/
│   │   └── backtester.py           # Módulo de backtesting sobre señales generadas
│   ├── indicators/
│   │   └── indicators.py           # Indicadores técnicos (SMA, EMA, RSI, MACD)
│   └── graphics/
│       ├── charts/
│       │   └── volume_chart.py     # Generación de gráfica de volumen
│
├── gui/
│   └── tabs/
│       ├── dashboard.py            # Pestaña de resumen general
│       ├── data_view.py             # Pestaña de datos de mercado
│       ├── graphics_view.py         # Pestaña de generación de gráficas
│       ├── strategy_view.py         # Pestaña de estrategias de trading
│       ├── execution_view.py        # Pestaña de ejecución de órdenes
│       ├── backtesting_view.py      # Pestaña de backtesting de estrategias
│       ├── logs_view.py             # Pestaña de logs del sistema
│       └── settings_view.py         # Pestaña de configuración
│
├── main.py                          # Punto de entrada principal de la aplicación
└── README.md                        # Documentación principal del proyecto
```

---

## 📄 Descripción de los módulos principales

### `core/data/market_data.py`
- Descarga datos históricos de mercado (acciones) usando `yfinance`.
- Devuelve un `DataFrame` limpio y listo para usar en estrategias o gráficas.

### `core/strategy/strategy_engine.py`
- Contiene la definición de estrategias de trading (medias móviles, RSI, MACD).
- Función `run_analysis()` orquesta la ejecución de estrategias sobre datos.

### `core/execution/order_executor.py`
- Permite ejecutar órdenes de compra/venta.
- Funciona en modo de simulación o modo real (preparado para integración con Interactive Brokers).

### `core/backtesting/backtester.py`
- Realiza backtesting de estrategias usando datos históricos.
- Calcula resultados financieros básicos: beneficio neto, número de operaciones.

### `core/indicators/indicators.py`
- Implementa indicadores técnicos como SMA, EMA, RSI y MACD.
- Funciones reutilizables para estrategias y análisis.

### `core/graphics/`
- `charts/volume_chart.py`: generación de gráficas de volumen de activos con `plotly`.
- En el futuro incluirá comparativas, gráficas anuales, diferenciales, etc.

---

## 📄 Descripción de las pestañas (`gui/tabs/`)

- **Dashboard**: Resumen general del sistema.
- **Datos de mercado**: Consulta interactiva de datos históricos.
- **Gráficas**: Creación y visualización de gráficas financieras.
- **Estrategias**: Configuración y ejecución de estrategias de trading.
- **Ejecución**: Panel de ejecución de órdenes en simulación o real.
- **Backtesting**: Evaluación de estrategias en histórico.
- **Logs**: Registro de eventos y acciones del sistema.
- **Configuración**: Personalización y ajustes del sistema.

---

## 📄 Esquema de flujo entre pestañas (`gui/tabs/`)

[ Dashboard ]
      ↓
[ Datos de mercado ]
      ↓
[ Gráficas ] ←
      ↓       ↘
[ Estrategias ] → (Genera señales) → [ Ejecución (Simulada/Real) ]
      ↓
[ Backtesting ] → (Evalúa históricamente rendimiento)
      ↓
[ Logs ]
      ↓
[ Configuración ]

---

## 🧠 Interpretación del flujo:

El usuario consulta datos y genera gráficas para inspirarse o analizar.

Ejecuta estrategias para generar señales inmediatas.

Si quiere actuar → Ejecuta órdenes reales o simuladas desde Ejecución.

Antes o después puede hacer Backtesting para analizar estadísticamente la calidad de esas estrategias.

Logs registra todo lo que ocurre.

Configuración permite ajustar parámetros del sistema.

---

## 🚀 Cómo arrancar el proyecto

1. Instalar dependencias:

```bash
pip install nicegui yfinance plotly pandas ib_insync
```

2. Ejecutar la aplicación:

```bash
python main.py
```

---

## ✅ Buenas prácticas para continuar

- Mantener separación clara entre lógica de datos (`core/data`), estrategias (`core/strategy`), ejecución (`core/execution`) y presentación (`gui/`).
- Añadir nuevas estrategias registrándolas en `strategy_engine.py`.
- Añadir nuevas gráficas creando módulos en `core/graphics/charts/`.
- Documentar cualquier nueva función o módulo.
- Crear `__init__.py` en cada carpeta para garantizar correcto funcionamiento de imports.

---
