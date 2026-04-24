@echo off
echo 🔧 Configurando entorno en Windows...

python -m venv .venv
call .\.venv\Scripts\activate
pip install -r requirements.txt

echo ✅ Entorno virtual activado y dependencias instaladas.
pause
