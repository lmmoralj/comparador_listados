# Comparador de Fallecidos vs Citas

## Ejecucion de pruebas local (Windows)
Si el entorno de ejecucion remoto no permite instalar dependencias, correr localmente:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
```

## Build portable local
```bat
build_portable.bat
```

Comando de compilacion usado por el script:

```bat
pyinstaller --noconsole --onedir --name "Comparador_Fallecidos_Citas" app/main.py
```

Salida esperada:
`dist\Comparador_Fallecidos_Citas\Comparador_Fallecidos_Citas.exe`

## Build automatico con GitHub Actions (Windows)
Este repositorio incluye el workflow:
- `.github/workflows/build-windows.yml`

Que realiza automaticamente:
1. Runner `windows-latest`.
2. Python `3.11`.
3. Instalacion de dependencias desde `requirements.txt`.
4. Pruebas con `python -m pytest -q`.
5. Compilacion con PyInstaller en modo `--onedir`.
6. Publicacion del artefacto descargable:
   `Comparador_Fallecidos_Citas_PORTABLE_WINDOWS`.

### Como descargar el .exe portable
1. Ir a la pestaña **Actions** del repositorio en GitHub.
2. Abrir la ejecucion del workflow **Build Portable Windows**.
3. En la seccion **Artifacts**, descargar:
   **Comparador_Fallecidos_Citas_PORTABLE_WINDOWS**.
4. Descomprimir el artefacto y abrir:
   `Comparador_Fallecidos_Citas.exe` dentro de `dist/Comparador_Fallecidos_Citas`.

## Privacidad y operacion local
- La aplicacion se ejecuta localmente en Windows y **no requiere internet en tiempo de ejecucion**.
- El workflow solo usa internet durante CI para instalar dependencias y subir artefactos de build.
- No incluir archivos Excel reales en el repositorio.
- No incluir reportes generados en el repositorio.
