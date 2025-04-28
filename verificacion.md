# ✅ Checklist de verificación – Proyecto ATHACORE

Este documento sirve para comprobar que la base del sistema está correctamente configurada y funcionando.

> 📌 También referenciado en el `README.md` como herramienta de validación rápida.

---

## 1. Entorno virtual
- [ ] `.venv` existe en la raíz del proyecto
- [ ] Entorno activado correctamente

## 2. Instalación de dependencias
- [ ] Ejecutado `pip install -r requirements.txt`
- [ ] Paquetes disponibles: `nicegui`, `yfinance`, `pandas`

## 3. Interfaz NiceGUI
- [ ] Ejecutado `python main.py`
- [ ] Navegador abre en `http://localhost:8080`
- [ ] Menú permite elegir estrategia y modo

## 4. Modo SIMULACIÓN
- [ ] Seleccionado `estrategia_basica_medias` y `simulacion`
- [ ] Se muestran señales tipo `BUY` / `SELL` en consola

## 5. Modo TEST
- [ ] Seleccionado modo `test` desde interfaz
- [ ] Se imprime mensaje "🧪 MODO TEST" y señales generadas

## 6. Modo REAL/DEMO
- [ ] Seleccionado modo `real`
- [ ] Se imprime en consola:
  ```
  2023-06-01 → BUY
  📤 Ejecutando orden: BUY en AAPL
  ```

## 7. Ejecución de test manual
- [ ] Ejecutado: `python -m athacore.pruebas.test_estrategia`
- [ ] Resultado similar a:
  ```
  ✅ Test OK: X señales detectadas
  ```

---

## Resultado final
- [ ] Todo funciona correctamente y está listo para expandirse 🚀