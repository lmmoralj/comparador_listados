import re
import unicodedata
from dataclasses import dataclass

@dataclass(frozen=True)
class NombreNorm:
    con_espacios: str
    compacto: str


def quitar_tildes(txt: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')


def normalizar_encabezado(name: str) -> str:
    n = quitar_tildes(str(name or '')).upper().strip()
    return re.sub(r'\s+', ' ', n)


def normalizar_cedula(value):
    if value is None:
        return '', False
    text = str(value).strip()
    if text.lower() in {'', 'nan', 'none', 'null'}:
        return '', False
    if text.endswith('.0') and text[:-2].replace('.', '', 1).isdigit():
        text = text[:-2]
    text = text.replace('-', '').replace(' ', '')
    text = re.sub(r'[^0-9]', '', text)
    if not text:
        return '', False
    return text, text != '0' and int(text) != 0


def normalizar_nombre(value) -> NombreNorm:
    t = quitar_tildes(str(value or '')).upper()
    t = re.sub(r'[^A-Z0-9\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return NombreNorm(t, t.replace(' ', ''))
