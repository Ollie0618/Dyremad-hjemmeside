from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

COLUMNS = ["id", "brand", "meattype", "weight", "image"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DYREMAD = os.path.join(BASE_DIR, "dyremad.db")


# Databaseforbindelse
def get_db_dyremad():
    if "db_dyremad" not in g:
        print(f"Åbner database: {DB_DYREMAD}")  # Debug
        g.db_dyremad = sqlite3.connect(DB_DYREMAD)
        g.db_dyremad.row_factory = sqlite3.Row
    return g.db_dyremad


@app.teardown_appcontext
def close_db(exception):
    db_dyremad = g.pop("db_dyremad", None)
    if db_dyremad is not None:
        db_dyremad.close()


# Opret tabeller hvis de ikke findes
def init_db():
    db = get_db_dyremad() 
    with db: 
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS dyremad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                meattype TEXT NOT NULL,
                weight TEXT NOT NULL,
                image TEXT
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS kattemad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                meattype TEXT NOT NULL,
                weight TEXT NOT NULL,
                image TEXT
            )
            """
        )


@app.route("/")
def front_page():
    return render_template("index.html", title="Forside")


@app.route("/login_page")
def login_page():
    return render_template("login_page.html", title="Login")


@app.route("/kurv_page")
def kurv_page():
    return render_template("kurv_page.html", title="Kurv")

@app.route("/admin_page")
def admin_page():
    return render_template("admin_page.html", title="Admin")


# ---------------- HUNDEMAD ----------------
@app.route("/hundemad_page")
def hundemad_page():
    search_query = request.args.get("search", "")
    db = get_db_dyremad()
    init_db()  # Sørger for tabeller eksisterer

    with db:
        if search_query:
            cur = db.execute(
                f"""
                SELECT {', '.join(COLUMNS)} 
                FROM dyremad
                WHERE id LIKE ?
                   OR brand LIKE ?
                   OR meattype LIKE ? 
                   OR weight LIKE ? 
                   OR image LIKE ?
                """,
                (
                    f"%{search_query}%",
                    f"%{search_query}%",
                    f"%{search_query}%",
                    f"%{search_query}%",
                    f"%{search_query}%",
                ),
            )
        else:
            cur = db.execute(f"SELECT {', '.join(COLUMNS)} FROM dyremad")

        data = cur.fetchall()

    return render_template("hundemad_page.html", title="Hundemad", data=data, search=search_query)


@app.route("/add", methods=["POST"])
def add_kategori():
    db = get_db_dyremad()
    brand = request.form["brand"]
    meattype = request.form["meattype"]
    weight = request.form["weight"]
    image = request.form.get("image", "")  # Valgfrit felt

    db.execute(
        "INSERT INTO dyremad (brand, meattype, weight, image) VALUES (?, ?, ?, ?)",
        (brand, meattype, weight, image),
    )
    db.commit()
    return redirect(url_for("hundemad_page"))


# ---------------- KATTEMAD ----------------
@app.route("/kattemad_page")
def kattemad_page():
    search_query = request.args.get("search", "")
    db = get_db_dyremad()
    init_db()  # Sørger for tabeller eksisterer

    with db:
        if search_query:
            cur = db.execute(
                f"""
                SELECT {', '.join(COLUMNS)} 
                FROM kattemad
                WHERE id LIKE ?
                   OR brand LIKE ?
                   OR meattype LIKE ? 
                   OR weight LIKE ?
                   OR image LIKE ?
                """,
                (
                    f"%{search_query}%",
                    f"%{search_query}%",
                    f"%{search_query}%",
                    f"%{search_query}%",
                    f"%{search_query}%",
                ),
            )
        else:
            cur = db.execute(f"SELECT {', '.join(COLUMNS)} FROM kattemad")

        data = cur.fetchall()

    return render_template("kattemad_page.html", title="Kattemad", data=data, search=search_query)


@app.route("/add_kattemad", methods=["POST"])
def add_kattemad():
    db = get_db_dyremad()
    brand = request.form["brand"]
    meattype = request.form["meattype"]
    weight = request.form["weight"]
    image = request.form.get("image", "")  # Valgfrit felt

    db.execute(
        "INSERT INTO kattemad (brand, meattype, weight, image) VALUES (?, ?, ?, ?)",
        (brand, meattype, weight, image),
    )
    db.commit()
    return redirect(url_for("kattemad_page"))


# ---------------- START APP ----------------
if __name__ == "__main__":
    # Init database ved start
    with sqlite3.connect(DB_DYREMAD) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dyremad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                meattype TEXT NOT NULL,
                weight TEXT NOT NULL,
                image TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kattemad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                meattype TEXT NOT NULL,
                weight TEXT NOT NULL,
                image TEXT
            )
            """
        )
    app.run(host="0.0.0.0", port=8080, debug=True)
