from pathlib import Path
from datetime import datetime

VALID_EXTENSIONS = {'.xlsx','.xls','.xlsm'}

def ensure_dirs(base: Path):
    (base / 'reportes_generados').mkdir(exist_ok=True, parents=True)
    (base / 'logs').mkdir(exist_ok=True, parents=True)

def ts_name():
    return datetime.now().strftime('%Y-%m-%d_%H%M')
