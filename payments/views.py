from django.shortcuts import render, redirect
from django.http import JsonResponse
from payments.utils import create_transaction
from payments.models import TollTransaction
from vehicles.models import Vehicle
from users.models import User
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import hmac
from django.views.decorators.csrf import csrf_exempt

def pay_toll(request, vehicle_id):
    user = request.user

    # Vérification de l'existence du véhicule
    try:
        vehicle = Vehicle.objects.get(id=vehicle_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Véhicule non trouvé"}, status=404)

    amount = 0.01  # Exemple : péage à 0.01 BTC

    transaction_data = create_transaction(user, vehicle, amount, "BTC")

    if "error" not in transaction_data:
        transaction = TollTransaction.objects.create(
            user=user,
            vehicle=vehicle,
            amount=amount,
            currency="BTC",
            transaction_id=transaction_data["txn_id"],
            status="pending"
        )
        return redirect(transaction_data["checkout_url"])  # Redirige l'utilisateur vers le paiement
    else:
        return JsonResponse({"error": transaction_data["error"]}, status=400)

IPN_SECRET = "TON_IPN_SECRET"

@csrf_exempt
def coinpayments_ipn(request):
    """ Gère les notifications IPN de CoinPayments """
    if request.method == "POST":
        received_hmac = request.headers.get("HMAC")
        payload = request.body.decode()

        # Calcul du HMAC à partir de la charge utile
        calculated_hmac = hmac.new(IPN_SECRET.encode(), payload.encode(), hashlib.sha512).hexdigest()

        if received_hmac == calculated_hmac:
            # Récupérer les données IPN depuis le corps de la requête
            data = request.POST
            txn_id = data.get("txn_id")
            status = int(data.get("status"))

            try:
                transaction = TollTransaction.objects.get(transaction_id=txn_id)
                if status >= 100:  # Paiement réussi
                    transaction.status = "completed"
                elif status < 0:  # Paiement échoué
                    transaction.status = "failed"
                transaction.save()
                return JsonResponse({"status": "success"}, status=200)

            except TollTransaction.DoesNotExist:
                return JsonResponse({"error": "Transaction non trouvée"}, status=404)

    return JsonResponse({"error": "Invalid IPN"}, status=400)
