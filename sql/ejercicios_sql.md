# Práctica SQL — Cartera de créditos (datos ficticios)

Base: `../datos/cartera_creditos.db` (SQLite). Fecha de corte de la cartera: **30/09/2026**.
Los datos son inventados, pero imitan una cartera B2B real: 300 clientes, ~4.700 facturas, pagos (algunos parciales o en dos partes), gestiones de cobranza y algunos clientes que entran en mora.

## Cómo abrirla

- **En el navegador, sin instalar nada:** entrá a sqliteonline.com → menú *File* → *Open DB* → elegí `cartera_creditos.db`.
- **En la PC:** instalá *DB Browser for SQLite* (gratis) → *Abrir base de datos* → pestaña *Ejecutar SQL*.

Los CSV de la carpeta `datos/` tienen los mismos datos; los vas a usar después en Python.

## Las tablas

**clientes** — `cliente_id`, `razon_social`, `segmento` (Corporativo / PyME / Agencia / Revendedor), `rubro`, `provincia`, `fecha_alta`, `cantidad_empleados`, `score_externo` (1 a 999, tipo buró; puede faltar), `limite_credito`, `plazo_pago_dias`, `vendedor`

**facturas** — `factura_id`, `cliente_id`, `fecha_emision`, `fecha_vencimiento`, `importe`, `anulada` (1 = anulada, no cuenta)

**pagos** — `pago_id`, `factura_id`, `fecha_pago`, `importe`, `medio_pago`. Una factura puede tener 0, 1 o 2 pagos.

**gestiones** — `gestion_id`, `cliente_id`, `fecha`, `canal`, `resultado`

Las fechas están como texto `AAAA-MM-DD`. En SQLite, para restar fechas usá `julianday(fecha1) - julianday(fecha2)`, y para sacar el mes, `strftime('%Y-%m', fecha)`.

**Para corregirte:** desde la carpeta `ruta-riesgo-crediticio`, corré `python sql/verificar.py` (o `python sql/verificar.py 5` para uno solo). Te dice si cada ejercicio está correcto, si le faltan filas o si algún valor no coincide.

Cada ejercicio trae además la **cantidad de filas esperada** para que te autocontroles. Guardá cada solución tuya en `mis_soluciones/ejNN.sql`. Las soluciones de referencia están en `../_referencia/soluciones_sql.sql` (no se suben a GitHub): abrilas recién cuando lo hayas intentado.

---

## Nivel 1 — Básico

**1. Clientes por segmento.** Cuántos clientes hay en cada segmento y cuál es el límite de crédito promedio. Ordená de mayor a menor cantidad. *(4 filas; PyME tiene 147)*

**2. Datos faltantes.** Listá los clientes que no tienen `score_externo` o no tienen `provincia`. *(15 filas)* — Pista: `= NULL` no funciona; se usa `IS NULL`.

**3. Top 10 por facturación.** Los 10 clientes que más facturaron, sin contar facturas anuladas. Mostrá razón social, cantidad de facturas y total facturado. *(10 filas)* — Primer `JOIN`.

## Nivel 2 — Intermedio

**4. Saldo pendiente por factura.** Para cada factura no anulada, mostrá importe, total pagado y saldo; dejá solo las que tienen saldo mayor a 0,01. *(632 filas)*
Pista: primero sumá los pagos por factura y después cruzá con `LEFT JOIN` (las facturas sin pagos también tienen que aparecer). `COALESCE` te sirve para convertir el NULL en 0.

**5. Aging de la cartera.** Con los saldos del ejercicio 4, armá el aging al 30/09/2026 por tramos: A vencer, 1-30, 31-60, 61-90 y +90 días de vencido. Mostrá cantidad de facturas, saldo y % sobre el total. *(5 filas; "A vencer" es el 73,4%)*
Pista: `CASE WHEN` para los tramos y un `WITH` (CTE) para no repetir la lógica del 4.

**6. Clientes excedidos de límite.** Clientes cuyo saldo total adeudado supera su límite de crédito, con el % de uso del límite, de mayor a menor. *(25 filas)*

**7. Comportamiento de pago por segmento.** Para las facturas que tienen al menos un pago, tomá la fecha del **último** pago y calculá por segmento: cantidad de facturas, atraso promedio en días (pago menos vencimiento) y % de facturas pagadas después del vencimiento. Mostrá solo segmentos con 50 facturas o más. *(4 filas; Revendedor es el que más se atrasa)* — `HAVING`.

**8. Clientes difíciles de contactar.** Clientes con 3 o más gestiones con resultado "Sin respuesta". Mostrá razón social, vendedor, total de gestiones y cuántas fueron sin respuesta. *(19 filas)*

## Nivel 3 — Avanzado (funciones de ventana)

**9. Evolución mensual de la facturación.** Por mes: total facturado, el del mes anterior, la variación % y el acumulado del año (que arranque de cero en enero). *(21 filas)*
Pista: `LAG()` y `SUM() OVER (PARTITION BY año ORDER BY mes)`.

**10. Ranking de morosos por segmento.** Por segmento, los 3 clientes con más saldo vencido a más de 90 días. Mostrá segmento, razón social, saldo total, saldo +90 y puesto. *(9 filas)*
Pista: `RANK() OVER (PARTITION BY segmento ORDER BY ...)` dentro de un CTE, y filtrás afuera.

---

**Cuando termines:** con lo de los ejercicios 5 a 7 ya tenés armadas las variables (atraso promedio, uso del límite, antigüedad, score externo) del modelo de scoring. Ese es el próximo paso, en Python.
