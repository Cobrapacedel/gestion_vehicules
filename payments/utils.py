import requests
import hashlib
import hmac
import time
from django.conf import settings
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration CoinPayments à partir des variables d'environnement
API_KEY = os.getenv("COINPAYMENTS_API_KEY")
API_SECRET = os.getenv("COINPAYMENTS_API_SECRET")
API_URL = os.getenv("COINPAYMENTS_API_URL")

def generate_signature(params):
    """ Génère une signature HMAC pour sécuriser les requêtes API """
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    return hmac.new(API_SECRET.encode(), sorted_params.encode(), hashlib.sha512).hexdigest()

def create_transaction(user, vehicle, amount, currency="BTC"):
    """ Crée une transaction CoinPayments """
    payload = {
        "version": 1,
        "cmd": "create_transaction",
        "key": API_KEY,
        "amount": amount,
        "currency1": currency,
        "currency2": currency,
        "buyer_email": user.email,
        "format": "json",
        "nonce": str(int(time.time()))  # Ajout du nonce basé sur le timestamp
    }

    # Générer la signature HMAC à partir des paramètres
    signature = generate_signature(payload)
    headers = {"hmac": signature}

    # Envoi de la requête API
    try:
        response = requests.post(API_URL, data=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data["error"] == "ok":
                return data["result"]  # Retourne les infos de la transaction
            else:
                return {"error": data["error"]}

        else:
            return {"error": f"API request failed with status {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request exception: {str(e)}"}
