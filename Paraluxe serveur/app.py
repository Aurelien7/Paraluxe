import sqlite3
from flask import Flask, request

app = Flask(__name__)
DB_NAME = "mesures.db"

# Création de la table si elle n'existe pas encore
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature INTEGER,
            vent INTEGER,
            date_heure TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@app.route('/receive_data', methods=["POST", "GET"])
def receive_data():
    if request.method == 'POST':
        temp = request.form.get('temperature')
        vent = request.form.get('vent')

        # Vérification que les valeurs existent
        if temp is None or vent is None:
            return "Erreur : paramètres 'temperature' et 'vent' requis", 400

        try:
            temp = int(temp)*100
            vent = int(vent)*100
        except ValueError:
            return "Erreur : les valeurs doivent être des nombres entiers", 400

        # Vérification des seuils
        if temp > 150 and vent > 25:
            return "Erreur 432 : valeurs hors limites", 432

        # Insertion en base
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mesure (temperature, vent) VALUES (?, ?)", (temp, vent)
        )
        conn.commit()
        conn.close()

        return f'Données reçues et enregistrées : {temp}°C, {vent}km/h', 200

    else:
        # Affiche les 10 dernières mesures dans le navigateur
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mesure ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "Aucune mesure enregistrée pour le moment."

        result = "<h2>10 dernières mesures</h2><ul>"
        for row in rows:
            result += f"<li>ID {row[0]} — {row[1]}°C, {row[2]} km/h — {row[3]}</li>"
        result += "</ul>"
        return result

@app.route('/clear_db', methods=['POST'])
def clear_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mesures")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='mesure'")
    conn.commit()
    conn.close()
    return "base de données vidée !", 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)