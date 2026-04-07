import serial
import requests
import time
 
PORT      = "COM40"              # Windows → COM3, COM4... | Linux/Mac → "/dev/ttyACM0"
BAUD      = 9600
FLASK_URL = "http://127.0.0.1:5000/receive_data"
 
# Le vent n'est pas câblé sur le BME680 — valeur fixe en attendant ton capteur vent
VENT_FIXE = 0  # [REMPLACER] par ta lecture capteur vent quand tu l'auras branché
 
 
def parse_ligne(line):
    """
    Parse les lignes du format Adafruit :
      'Temp : 25.30 °C'
      'Humidité : 60.10 %'
      'Pression : 1013.25 hPa'
      'Gaz : 45230 Ω'
    Retourne un dict avec les valeurs trouvées.
    """
    line = line.strip()
 
    if line.startswith("Temp"):
        val = line.split(":")[1].replace("°C", "").strip()
        return ("temperature", float(val))
 
    elif line.startswith("Humidité") or line.startswith("Humidite"):
        val = line.split(":")[1].replace("%", "").strip()
        return ("humidite", float(val))
 
    elif line.startswith("Pression"):
        val = line.split(":")[1].replace("hPa", "").strip()
        return ("pression", float(val))
 
    elif line.startswith("Gaz"):
        # Résistance gaz en Ohms → on convertit en kΩ pour l'affichage
        val = line.split(":")[1].replace("Ω", "").strip()
        return ("qualite_air", round(float(val) / 1000, 2))  # kΩ

    elif line.startswith("Luminosite"):
        val = line.split(":")[1].replace("%", "").strip()
        return ("luminosite", float(val))
 
    return None
 
 
def envoyer(data):
    data["vent"] = VENT_FIXE
    try:
        response = requests.post(FLASK_URL, data=data, timeout=5)
        print(
            f"✅ ({response.status_code}) "
            f"→ {data.get('temperature','?')}°C | "
            f"{data.get('vent','?')} km/h | "
            f"{data.get('humidite','?')}% | "
            f"{data.get('pression','?')} hPa | "
            f"{data.get('qualite_air','?')} kΩ"
        )
    except requests.exceptions.ConnectionError:
        print("❌ Flask inaccessible — relance server.py")
    except requests.exceptions.Timeout:
        print("❌ Timeout Flask")
 
 
def main():
    print(f"📡 Connexion au port {PORT}...")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=5)
        time.sleep(2)  # laisse l'Arduino s'initialiser
        print("✅ Arduino connecté — lecture en cours...\n")
    except serial.SerialException as e:
        print(f"❌ Impossible d'ouvrir {PORT} : {e}")
        print("   → Vérifier le port dans le Gestionnaire de périphériques")
        return
 
    # On accumule les 4 valeurs du BME680 avant d'envoyer
    mesure_en_cours = {}
 
    while True:
        try:
            raw  = ser.readline()
            line = raw.decode('utf-8', errors='replace').strip()
 
            if not line:
                continue
 
            if "non trouvé" in line or "Échec" in line:
                print(f"⚠️  Arduino : {line}")
                continue
 
            result = parse_ligne(line)
            if result:
                key, val = result
                mesure_en_cours[key] = val
                print(f"   ↳ {key} = {val}")
 
            # Quand on a les 4 valeurs du capteur → on envoie
            if all(k in mesure_en_cours for k in ("temperature", "humidite", "pression", "qualite_air", "luminosite")):
                envoyer(mesure_en_cours.copy())
                mesure_en_cours = {}  # reset pour la prochaine mesure
                print()
 
        except (ValueError, UnicodeDecodeError) as e:
            print(f"⚠️  Erreur parsing : {e} | ligne : {line!r}")
        except serial.SerialException as e:
            print(f"❌ Perte connexion série : {e}")
            break
 
 
if __name__ == '__main__':
    main()