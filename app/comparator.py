from __future__ import annotations
from collections import defaultdict
import pandas as pd
from rapidfuzz import fuzz
from .normalizer import normalizar_cedula, normalizar_nombre, normalizar_encabezado


def compare_data(fallecidos: pd.DataFrame, citas: pd.DataFrame, threshold=90, solo_pendientes=True):
    logs = []
    f = fallecidos.copy()
    c = citas.copy()
    fmap = {normalizar_encabezado(x): x for x in f.columns}
    cmap = {normalizar_encabezado(x): x for x in c.columns}

    if solo_pendientes and 'ESTADO CITA' in cmap:
        c = c[c[cmap['ESTADO CITA']].fillna('').str.strip().str.upper().eq('PENDIENTE')].copy()
        logs.append('Filtro: solo pendientes')

    f['cedula_norm'], f['cedula_ok'] = zip(*f[fmap['CEDULA']].map(normalizar_cedula))
    c['cedula_norm'], c['cedula_ok'] = zip(*c[cmap['CEDULA']].map(normalizar_cedula))

    f['nom_norm'] = f[fmap['NOMBRE DIFUNTO']].map(lambda x: normalizar_nombre(x).con_espacios)
    f['nom_comp'] = f[fmap['NOMBRE DIFUNTO']].map(lambda x: normalizar_nombre(x).compacto)

    c['nombre_completo'] = (c[cmap['NOMBRE']].fillna('') + ' ' + c[cmap['PRIMER APELLIDO']].fillna('') + ' ' + c[cmap['SEGUNDO APELLIDO']].fillna('')).str.strip()
    c['nombre_alt'] = (c[cmap['PRIMER APELLIDO']].fillna('') + ' ' + c[cmap['SEGUNDO APELLIDO']].fillna('') + ' ' + c[cmap['NOMBRE']].fillna('')).str.strip()
    c['nom_norm'] = c['nombre_completo'].map(lambda x: normalizar_nombre(x).con_espacios)
    c['nom_alt_norm'] = c['nombre_alt'].map(lambda x: normalizar_nombre(x).con_espacios)
    c['nom_comp'] = c['nombre_completo'].map(lambda x: normalizar_nombre(x).compacto)
    c['nom_alt_comp'] = c['nombre_alt'].map(lambda x: normalizar_nombre(x).compacto)

    by_ced = defaultdict(list)
    by_name = defaultdict(list)
    bucket = defaultdict(list)
    for idx, r in c.iterrows():
        if r['cedula_ok']:
            by_ced[r['cedula_norm']].append(idx)
        for nm in {r['nom_norm'], r['nom_alt_norm']}:
            by_name[nm].append(idx)
            if nm:
                bucket[nm[0]].append(idx)

    cedula, cedula_nom_diff, nombre100, posibles, sin = [], [], [], [], []

    for _, fr in f.iterrows():
        match = False
        if fr['cedula_ok'] and fr['cedula_norm'] in by_ced:
            for idx in by_ced[fr['cedula_norm']]:
                cr = c.loc[idx]
                sc = max(fuzz.ratio(fr['nom_comp'], cr['nom_comp']), fuzz.ratio(fr['nom_comp'], cr['nom_alt_comp']))
                row = _out_row(fr, cr)
                row.update({'Tipo Coincidencia':'CEDULA','Porcentaje Coincidencia':100,'Verificación Requerida':'NO','Observación':'Persona fallecida con cita registrada.'})
                cedula.append(row)
                if sc < 70:
                    row2 = dict(row)
                    row2.update({'Tipo Coincidencia':'CEDULA_COINCIDE_NOMBRE_DIFERENTE','Verificación Requerida':'SI','Observación':'Cédula coincide, nombre diferente.'})
                    cedula_nom_diff.append(row2)
                match = True
        if not match:
            for idx in set(by_name.get(fr['nom_norm'], [])):
                cr = c.loc[idx]
                row = _out_row(fr, cr)
                row.update({'Tipo Coincidencia':'NOMBRE_EXACTO','Porcentaje Coincidencia':100,'Verificación Requerida':'SI','Observación':'Nombre coincide, validar cédula.'})
                nombre100.append(row)
                match = True
        if not match:
            cand = set(bucket.get(fr['nom_norm'][:1] if fr['nom_norm'] else '', []))
            best = None
            for idx in cand:
                cr = c.loc[idx]
                s = max(fuzz.token_sort_ratio(fr['nom_norm'], cr['nom_norm']), fuzz.token_set_ratio(fr['nom_norm'], cr['nom_norm']), fuzz.ratio(fr['nom_comp'], cr['nom_comp']))
                if s >= threshold and (best is None or s > best[0]):
                    best = (s, idx)
            if best:
                cr = c.loc[best[1]]
                row = _out_row(fr, cr)
                row.update({'Tipo Coincidencia':'POSIBLE_NOMBRE','Porcentaje Coincidencia':best[0],'Método Similitud':'token_sort/token_set/compact','Verificación Requerida':'SI','Observación':'Posible coincidencia por similitud.'})
                posibles.append(row)
                match = True
        if not match:
            sin.append({'Cedula Archivo1': fr.get(fmap['CEDULA'], ''), 'Nombre Difunto': fr.get(fmap['NOMBRE DIFUNTO'], '')})

    return {'cedula':pd.DataFrame(cedula), 'cedula_nombre_diff':pd.DataFrame(cedula_nom_diff), 'nombre_exacto':pd.DataFrame(nombre100), 'posible_nombre':pd.DataFrame(posibles), 'sin_coincidencia':pd.DataFrame(sin), 'fallecidos':f, 'citas':c, 'logs':logs}


def _out_row(f, c):
    return {
        'Cedula Archivo1': f.get('cedula_norm',''), 'Nombre Difunto': f.get('nom_norm',''), 'Fecha Emision Defunción': f.get('Fecha Emision',''),
        'Cedula Archivo2': c.get('cedula_norm',''), 'Nombre Completo Archivo2': c.get('nombre_completo',''), 'Fecha Cita': c.get('Fecha Cita',''),
        'Fecha Atención': c.get('Fecha Atención',''), 'Estado Cita': c.get('Estado Cita',''), 'Dsc. Servicio': c.get('Dsc. Servicio',''),
        'Dsc. Especialidad': c.get('Dsc. Especialidad',''), 'TIPO CONSULTA': c.get('TIPO CONSULTA',''), 'Nombre Profesional': c.get('Nombre Profesional',''),
        'Dsc. Tipo Cupo': c.get('Dsc. Tipo Cupo',''), 'HORA CUPO': c.get('HORA CUPO',''), 'Tipo Medicina': c.get('Tipo Medicina','')
    }
