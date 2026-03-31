import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
 
app = Flask(__name__)
CORS(app)  # Permet au site web de lire les données sans erreur CORS
 
DB_NAME = "mesures.db"
 
 
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mesure (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature  REAL,
            vent         INTEGER,
            humidite     REAL,
            pression     REAL,
            qualite_air  REAL,
            date_heure   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
 
 
# ── RÉCEPTION DES DONNÉES (client.py → Flask) ──────────────────────────
@app.route('/receive_data', methods=["POST", "GET"])
def receive_data():
    if request.method == 'POST':
        temp     = request.form.get('temperature')
        vent     = request.form.get('vent')
        humidite = request.form.get('humidite',    0)
        pression = request.form.get('pression',    0)
        qualite  = request.form.get('qualite_air', 0)
 
        if temp is None or vent is None:
            return "Erreur : température et vent requis", 400
 
        try:
            temp     = float(temp)
            vent     = int(float(vent))
            humidite = float(humidite)
            pression = float(pression)
            qualite  = float(qualite)
        except ValueError:
            return "Erreur : valeurs invalides", 400
 
        if temp > 150 and vent > 25:
            return "Erreur 432 : valeurs hors limites", 432
 
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mesure (temperature, vent, humidite, pression, qualite_air) VALUES (?,?,?,?,?)",
            (temp, vent, humidite, pression, qualite)
        )
        conn.commit()
        conn.close()
 
        return f'Données reçues : {temp}°C | {vent}km/h | {humidite}% | {pression}hPa | IAQ:{qualite}', 200
 
    # GET → affiche les 10 dernières mesures pour vérif rapide dans le navigateur
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mesure ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "Aucune mesure enregistrée."
    result = "<h2>10 dernières mesures</h2><ul>"
    for r in rows:
        result += f"<li>#{r[0]} — {r[1]}°C | {r[2]}km/h | {r[3]}% | {r[4]}hPa | IAQ:{r[5]} — {r[6]}</li>"
    result += "</ul>"
    return result
 
 
# ── API POUR LE SITE WEB (mesures.html → Flask) ─────────────────────────
@app.route('/api/mesures')
def api_mesures():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, temperature, vent, humidite, pression, qualite_air, date_heure
        FROM mesure
        ORDER BY id DESC
        LIMIT 500
    """)
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {
            "id":          r[0],
            "temperature": r[1],
            "vent":        r[2],
            "humidite":    r[3],
            "pression":    r[4],
            "qualite_air": r[5],
            "date_heure":  r[6]
        }
        for r in rows
    ])
 
 
# ── VIDER LA BASE ────────────────────────────────────────────────────────
@app.route('/clear_db', methods=["POST"])
def clear_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mesure")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='mesure'")
    conn.commit()
    conn.close()
    return "Base de données vidée", 200
 
 
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
 