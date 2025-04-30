# 📦 Estructura final del sistema ATHACORE

ATHACORE está organizado en módulos independientes para permitir flexibilidad y claridad en operaciones y pruebas. Esta es la estructura lógica y su flujo de uso.

---

## 🧱 Estructura base de carpetas

```
athacore/
├── analisis/               # Backtesting de estrategias
├── decisiones/             # Generación de señales en tiempo real
├── ejecucion/              # Ejecución de órdenes (demo o real)
├── pruebas/                # Tests técnicos y validaciones
main.py                    # Interfaz gráfica con NiceGUI
```

---

## 🔁 Flujo de uso desde la interfaz (modular y explícito)

```
[INTERFAZ]
   │
   ├───▶ 📊 Análisis de estrategia
   │         └──▶ Módulo: ANALISIS
   │               ↳ Simula, genera señales, termina.
   │
   ├───▶ 🧪 Evaluar ahora
   │         └──▶ Módulo: DECISIONES (solo muestra señales)
   │
   └───▶ ⚙️ Ejecutar estrategia
             └──▶ Módulo: DECISIONES
                     └──▶ Módulo: EJECUCION
                             ↳ Ejecuta señales (real o simulado)
```

---

## 📊 Comparativa técnica entre módulos

| Módulo        | Propósito principal         | ¿Cuándo se usa?    | Entrada principal           | Salida principal    | Llama a otro módulo |
|---------------|-----------------------------|--------------------|-----------------------------|---------------------|---------------------|
| `analisis`    | Simular estrategia con datos| Antes de operar    | Ticker, Fechas,             | Señales simuladas   | ❌                  |
|               | históricos                  |                    | Estrategia                  |                     |                     |
| `decisiones`  | Evaluar datos actuales y    | Durante operación  | Ticker actual, Estrategia   | Señales reales      | ✅ (a `ejecucion`)  |
|               | generar señales reales      |                    |                             |                     |                     |
| `ejecucion`   | Ejecutar señales en broker  | Solo si hay señales| Señales generadas           | Orden ejecutada     | ❌                  |
|               | real o modo simulado        |                    |                             |  o simulada         |                     |

---

## ✅ Flujo típico de uso recomendado

```
1. ANALISIS     → validar estrategia (simulación)
2. DECISIONES   → aplicar estrategia en tiempo real (genera señales)
3. EJECUCION    → ejecutar señales (si procede)
```

Este documento resume la lógica operativa actual de ATHACORE y sirve como referencia para desarrollos futuros.