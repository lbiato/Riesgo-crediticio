"""Corrige tus soluciones de SQL contra la base de práctica.

Uso (desde la carpeta ruta-riesgo-crediticio):
    python sql/verificar.py          -> revisa los 10 ejercicios
    python sql/verificar.py 5        -> revisa solo el ejercicio 5

Compara el resultado de tu consulta (sql/mis_soluciones/ejNN.sql) con el de la
solución de referencia: cantidad de filas, cantidad de columnas y valores
(sin importar el orden de las filas, y redondeando a 1 decimal).
Usa solo la biblioteca estándar de Python: no hay nada que instalar.
"""
import re
import sqlite3
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "datos" / "cartera_creditos.db"
MIS = BASE / "sql" / "mis_soluciones"
REF = BASE / "_referencia" / "soluciones_sql.sql"


def referencias():
    texto = REF.read_text(encoding="utf-8")
    bloques = re.split(r"^-- (\d+)\. .*$", texto, flags=re.M)
    return {int(bloques[i]): bloques[i + 1].strip() for i in range(1, len(bloques), 2)}


def normalizar(filas):
    def celda(v):
        if isinstance(v, float):
            return round(v, 1)
        return v
    return sorted((tuple(celda(v) for v in f) for f in filas), key=repr)


def limpiar(sql):
    sin_comentarios = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    return sin_comentarios.strip().rstrip(";")


def revisar(n, refs, con):
    archivo = MIS / f"ej{n:02d}.sql"
    mio = limpiar(archivo.read_text(encoding="utf-8")) if archivo.exists() else ""
    if not mio:
        return "·", "sin resolver todavía"
    try:
        cur = con.execute(mio)
        mis_filas = cur.fetchall()
        mis_cols = len(cur.description or [])
    except sqlite3.Error as e:
        return "✗", f"error de SQL: {e}"
    cur = con.execute(refs[n])
    ref_filas = cur.fetchall()
    ref_cols = len(cur.description)
    if len(mis_filas) != len(ref_filas):
        return "✗", f"devuelve {len(mis_filas)} filas y se esperaban {len(ref_filas)}"
    if mis_cols != ref_cols:
        return "~", f"filas OK ({len(mis_filas)}), pero tiene {mis_cols} columnas y la referencia {ref_cols}"
    if normalizar(mis_filas) != normalizar(ref_filas):
        return "~", "cantidad de filas y columnas OK, pero algunos valores no coinciden (revisá filtros, redondeos o el orden de las columnas)"
    return "✓", "correcto"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    refs = referencias()
    pedidos = [int(a) for a in sys.argv[1:]] or sorted(refs)
    con = sqlite3.connect(DB)
    ok = 0
    for n in pedidos:
        marca, msg = revisar(n, refs, con)
        ok += marca == "✓"
        print(f" {marca}  Ejercicio {n:>2}: {msg}")
    print(f"\n {ok}/{len(pedidos)} correctos")


if __name__ == "__main__":
    main()
