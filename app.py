from flask import Flask, request, redirect, render_template, session
import sqlite3
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "OP")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "OP")


def init_db():
    with sqlite3.connect("reponses.db") as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS personnes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL
            )
        """)


@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/envoyer", methods=["POST"])
def envoyer():
    prenom = request.form.get("prenom", "").strip()
    nom = request.form.get("nom", "").strip()

    if prenom and nom:
        with sqlite3.connect("reponses.db") as db:
            db.execute(
                "INSERT INTO personnes (prenom, nom) VALUES (?, ?)",
                (prenom, nom)
            )

    return """
    <h1>Merci !</h1>
    <p>Vos informations ont bien été enregistrées.</p>
    """


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/reponses")

        return "Mot de passe incorrect.", 401

    return render_template("login.html")


@app.route("/reponses")
def reponses():
    if not session.get("admin"):
        return redirect("/admin")

    with sqlite3.connect("reponses.db") as db:
        personnes = db.execute(
            "SELECT id, prenom, nom FROM personnes ORDER BY id DESC"
        ).fetchall()

    return render_template("reponses.html", personnes=personnes)


@app.route("/deconnexion")
def deconnexion():
    session.clear()
    return redirect("/admin")


if __name__ == "__main__":
    init_db()
    app.run()