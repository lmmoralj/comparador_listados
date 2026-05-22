from app.normalizer import normalizar_cedula, normalizar_nombre


def test_normalizacion_basica():
    c, ok = normalizar_cedula('00123.0')
    assert c == '00123'
    assert ok is True
    n = normalizar_nombre(' José  Pérez ')
    assert n.con_espacios == 'JOSE PEREZ'
