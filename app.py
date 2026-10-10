"""Sistema de Tickets de Soporte Técnico.

Aplicación web hecha con Flask (backend en Python) y SQLite (base de datos).
Flujo: el navegador pide una página -> Flask recibe la petición en una "ruta"
-> consulta la base con SQL -> arma el HTML con una plantilla -> lo devuelve.
"""

import sqlite3
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

from reportes import REPORTES

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "soporte.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

ESTADOS = ["Abierto", "En proceso", "Resuelto"]

app = Flask(__name__)
app.secret_key = "clave-de-desarrollo"  # necesaria para los mensajes flash


# ---------------------------------------------------------------------------
#  Conexión a la base de datos
# ---------------------------------------------------------------------------

def get_db():
    """Abre una conexión por petición y la reutiliza durante esa petición."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row          # permite fila["columna"]
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite no valida FK si no se activa
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    """Cierra la conexión al terminar cada petición."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas y carga los datos de ejemplo desde schema.sql."""
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    con.close()


@app.cli.command("init-db")
def init_db_command():
    """Uso: flask --app app init-db  (borra y recrea la base)."""
    init_db()
    print("Base de datos creada en", DB_PATH)


# ---------------------------------------------------------------------------
#  Rutas (páginas)
# ---------------------------------------------------------------------------

@app.route("/")
def inicio():
    db = get_db()
    resumen = db.execute(
        "SELECT estado, COUNT(*) FROM tickets GROUP BY estado"
    ).fetchall()
    totales = {fila[0]: fila[1] for fila in resumen}
    facturado = db.execute(
        "SELECT SUM(costo) FROM tickets WHERE estado = 'Resuelto'"
    ).fetchone()[0] or 0  # si no hay resueltos, SUM devuelve NULL (None)
    return render_template("inicio.html", totales=totales, estados=ESTADOS, facturado=facturado)


@app.route("/tickets")
def tickets():
    estado = request.args.get("estado", "")
    # clientes y tecnicos tienen las dos una columna "nombre": con AS se le
    # pone un nombre distinto a cada una para no confundirlas.
    # LEFT JOIN con tecnicos: así también aparecen los tickets sin técnico.
    sql = """
        SELECT tickets.id, tickets.fecha_ingreso, tickets.problema,
               tickets.estado, tickets.costo,
               equipos.tipo, equipos.marca, equipos.modelo,
               clientes.nombre AS cliente,
               tecnicos.nombre AS tecnico
        FROM tickets
        JOIN equipos       ON tickets.equipo_id = equipos.id
        JOIN clientes      ON equipos.cliente_id = clientes.id
        LEFT JOIN tecnicos ON tickets.tecnico_id = tecnicos.id
    """
    parametros = []
    if estado in ESTADOS:
        sql += " WHERE tickets.estado = ?"
        parametros.append(estado)
    sql += " ORDER BY tickets.fecha_ingreso DESC"

    filas = get_db().execute(sql, parametros).fetchall()
    return render_template("tickets.html", tickets=filas, estados=ESTADOS, estado_actual=estado)


@app.route("/tickets/nuevo", methods=["GET", "POST"])
def nuevo_ticket():
    db = get_db()
    if request.method == "POST":
        equipo_id = request.form.get("equipo_id")
        tecnico_id = request.form.get("tecnico_id") or None
        problema = request.form.get("problema", "").strip()
        costo = request.form.get("costo") or 0

        if not equipo_id or not problema:
            flash("El equipo y el problema son obligatorios.", "error")
        else:
            # Los "?" son parámetros: evitan la inyección SQL
            db.execute(
                "INSERT INTO tickets (equipo_id, tecnico_id, problema, costo) VALUES (?, ?, ?, ?)",
                (equipo_id, tecnico_id, problema, costo),
            )
            db.commit()
            flash("Ticket creado correctamente.", "ok")
            return redirect(url_for("tickets"))

    equipos = db.execute("""
        SELECT equipos.id, equipos.tipo, equipos.marca, equipos.modelo, clientes.nombre
        FROM equipos
        JOIN clientes ON equipos.cliente_id = clientes.id
        ORDER BY clientes.nombre
    """).fetchall()
    tecnicos = db.execute("SELECT id, nombre, especialidad FROM tecnicos ORDER BY nombre").fetchall()
    return render_template("ticket_form.html", equipos=equipos, tecnicos=tecnicos)


@app.route("/tickets/<int:ticket_id>/estado", methods=["POST"])
def cambiar_estado(ticket_id):
    nuevo_estado = request.form.get("estado")
    if nuevo_estado in ESTADOS:
        db = get_db()
        db.execute("UPDATE tickets SET estado = ? WHERE id = ?", (nuevo_estado, ticket_id))
        db.commit()
        flash(f"Ticket #{ticket_id} pasó a '{nuevo_estado}'.", "ok")
    return redirect(request.referrer or url_for("tickets"))


@app.route("/tickets/<int:ticket_id>/eliminar", methods=["POST"])
def eliminar_ticket(ticket_id):
    db = get_db()
    db.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    db.commit()
    flash(f"Ticket #{ticket_id} eliminado.", "ok")
    return redirect(url_for("tickets"))


@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    db = get_db()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        email = request.form.get("email", "").strip() or None
        if not nombre:
            flash("El nombre es obligatorio.", "error")
        else:
            try:
                db.execute(
                    "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
                    (nombre, telefono, email),
                )
                db.commit()
                flash("Cliente agregado.", "ok")
            except sqlite3.IntegrityError:
                flash("Ya existe un cliente con ese email.", "error")
        return redirect(url_for("clientes"))

    filas = db.execute(
        "SELECT id, nombre, telefono, email FROM clientes ORDER BY nombre"
    ).fetchall()
    return render_template("clientes.html", clientes=filas)


@app.route("/reportes")
def reportes():
    db = get_db()
    resultados = []
    for reporte in REPORTES:
        cursor = db.execute(reporte["sql"])
        columnas = [col[0] for col in cursor.description]
        resultados.append({**reporte, "columnas": columnas, "filas": cursor.fetchall()})
    return render_template("reportes.html", reportes=resultados)


@app.route("/arquitectura")
def arquitectura():
    """Documentación del sistema: stack, arquitectura y modelo de datos."""
    db = get_db()
    # Los nombres de tabla son fijos (no vienen del usuario), por eso se
    # pueden armar en el texto de la consulta sin riesgo de inyección SQL.
    conteos = {}
    for tabla in ["clientes", "equipos", "tecnicos", "tickets"]:
        conteos[tabla] = db.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    return render_template("arquitectura.html", conteos=conteos)


@app.route("/consulta", methods=["GET", "POST"])
def consulta():
    """Permite escribir un SELECT libre. La conexión es de SOLO LECTURA,
    así que aunque se escriba un DELETE o DROP, la base no se modifica."""
    sql = request.form.get("sql", "SELECT * FROM clientes;")
    columnas, filas, error = [], [], None

    if request.method == "POST":
        con = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
        try:
            cursor = con.execute(sql)
            if cursor.description:
                columnas = [col[0] for col in cursor.description]
                filas = cursor.fetchmany(200)
        except sqlite3.Error as e:
            error = str(e)
        finally:
            con.close()

    return render_template("consulta.html", sql=sql, columnas=columnas, filas=filas, error=error)


if __name__ == "__main__":
    if not DB_PATH.exists():
        init_db()
        print("Base de datos creada con datos de ejemplo.")
    app.run(debug=True)
