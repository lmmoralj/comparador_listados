from __future__ import annotations
import pandas as pd
from .normalizer import normalizar_encabezado

class ReaderError(ValueError):
    pass


def _map_cols(cols):
    return {normalizar_encabezado(c): c for c in cols}


def _validar_required(mapped, req, label):
    faltan = [r for r in req if r not in mapped]
    if faltan:
        raise ReaderError(f'{label}: faltan columnas obligatorias: {faltan}')


def read_fallecidos(path: str, sheet='FALLECIDOS'):
    logs = []
    df = pd.read_excel(path, sheet_name=sheet, dtype=str)
    logs.append(f'Hoja archivo1: {sheet}')
    if len(df.columns) == 1 and not df.empty:
        col = df.columns[0]
        first = str(df.iloc[0, 0])
        if ',' in first:
            spl = df[col].fillna('').astype(str).str.split(',', expand=True)
            spl.columns = [str(c).strip() for c in spl.iloc[0].tolist()]
            df = spl.iloc[1:].reset_index(drop=True)
            logs.append('Archivo1 convertido desde una columna CSV')
    mapped = _map_cols(df.columns)
    _validar_required(mapped, ['CEDULA', 'NOMBRE DIFUNTO'], 'Archivo1')
    return df, logs


def read_citas(path: str, sheet='C.E.'):
    logs = []
    df = pd.read_excel(path, sheet_name=sheet, dtype=str)
    logs.append(f'Hoja archivo2: {sheet}')
    mapped = _map_cols(df.columns)
    _validar_required(mapped, ['CEDULA', 'PRIMER APELLIDO', 'SEGUNDO APELLIDO', 'NOMBRE', 'FECHA ATENCION'], 'Archivo2')
    return df, logs
