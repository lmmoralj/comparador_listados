@echo off
setlocal
cd /d %~dp0

if not exist .venv (
  py -3.11 -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest -q
if errorlevel 1 (
  echo Las pruebas fallaron. Se cancela la compilacion.
  exit /b 1
)

if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

pyinstaller --noconsole --onedir --name "Comparador_Fallecidos_Citas" app/main.py

if not exist dist\Comparador_Fallecidos_Citas\reportes_generados mkdir dist\Comparador_Fallecidos_Citas\reportes_generados
if not exist dist\Comparador_Fallecidos_Citas\logs mkdir dist\Comparador_Fallecidos_Citas\logs
if exist README.md copy README.md dist\Comparador_Fallecidos_Citas\README.md >nul
if exist VERSION.txt copy VERSION.txt dist\Comparador_Fallecidos_Citas\VERSION.txt >nul

echo Build portable completado en dist\Comparador_Fallecidos_Citas
endlocal
