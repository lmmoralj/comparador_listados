# Comparador de Fallecidos vs Citas

## Ejecucion de pruebas local (Windows)
Si el entorno de ejecucion remoto no permite instalar dependencias, correr localmente:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
```

## Build portable
```bat
build_portable.bat
```

Comando de compilacion usado por el script:

```bat
pyinstaller --noconsole --onedir --name "Comparador_Fallecidos_Citas" app/main.py
```

Salida esperada:
`dist\Comparador_Fallecidos_Citas\Comparador_Fallecidos_Citas.exe`
