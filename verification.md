# ✅ Verification checklist – ATHACORE project

This document is used to check that the system’s foundation is correctly configured and functioning.

> 📌 Also referenced in the `README.md` as a quick validation tool.

---

## 1. Virtual environment
- [ ] `.venv` exists in the project root\
- [ ] Environment correctly activated\
\
## 2. Installation of dependencies\
- [ ] `pip install -r requirements.txt` executed\
- [ ] Packages available: `nicegui`, `yfinance`, `pandas`\
\
## 3. NiceGUI interface
- [ ] `python main.py` executed
- [ ] Browser opens at `http://localhost:8080`
- [ ] Menu allows selection of strategy and mode

## 4. SIMULATION mode
- [ ] `basic_moving_averages_strategy` and `simulation` selected
- [ ] `BUY` / `SELL` signals are displayed in the console

## 5. TEST Mode
- [ ] `test` mode selected from the interface
- [ ] The message ‘🧪 TEST MODE’ and generated signals are printed

## 6. REAL/DEMO Mode
- [ ] `real` mode selected
- [ ] The following is printed to the console:
  ```
  2023-06-01 → BUY
  📤 Executing order: BUY on AAPL
  ```
  
  
## 7. Manual test execution
- [ ] Executed: `python -m athacore.tests.test_strategy`
- [ ] Result similar to:
  ```
  ✅ Test OK: X signals detected
  ```
  
---
  
## Final result
- [ ] Everything is working correctly and is ready to scale 🚀

Translated with DeepL.com (free version)