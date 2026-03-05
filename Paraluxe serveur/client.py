import requests
import time

FLASK_URL = "http://127.0.0.1:5000/receive_data"
INTERVALLE_SECONDES = 10  # fréquence d'envoi


def lire_capteur():
    """
    Remplace ce bloc par ta vraie lecture de capteur.

    Exemple avec un DHT11 sur Raspberry Pi :
        import Adafruit_DHT
        capteur = Adafruit_DHT.DHT11
        pin = 4
        _, temperature = Adafruit_DHT.read(capteur, pin)
        vent = <lecture de ton capteur vent>
        return temperature, vent
    """
    temperature = 21  # ← remplacer par lecture réelle du capteur
    vent = 10         # ← remplacer par lecture réelle du capteur
    return temperature, vent


def envoyer_donnees():
    temp, vent = lire_capteur()

    if temp is None or vent is None:
        print("  Capteur non disponible, envoi annulé")
        return

    try:
        response = requests.post(
            FLASK_URL,
            data={"temperature": temp, "vent": vent},
            timeout=5
        )
        print(f" Réponse serveur ({response.status_code}) : {response.text}")

    except requests.exceptions.ConnectionError:
        print(" Erreur : impossible de joindre le serveur Flask")
    except requests.exceptions.Timeout:
        print(" Erreur : le serveur n'a pas répondu à temps")


if __name__ == '__main__':
    print(f" Démarrage de l'envoi toutes les {INTERVALLE_SECONDES} secondes...")
    while True:
        envoyer_donnees()
        time.sleep(INTERVALLE_SECONDES)