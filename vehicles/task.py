from celery import shared_task
from django.core.mail import send_mail
from datetime import date, timedelta
from .models import Vehicle
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    # Utilisation d'un paramètre d'URL dynamique (site_url)
    activation_link = f'{settings.SITE_URL}/activate/{uid}/{token}/'
    
    subject = 'Activez votre compte'
    message = render_to_string('activation_email.html', {
        'activation_link': activation_link,
        'user': user,
    })
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_confirmation_email(user_email):
    subject = 'Bienvenue sur notre site !'
    message = 'Merci de vous être inscrit sur notre plateforme.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_vehicle_reminders():
    today = timezone.now().date()
    reminder_days = 30  # Nombre de jours avant expiration pour envoyer un rappel

    # Optimisation des requêtes en utilisant un seul filtre
    vehicles = Vehicle.objects.filter(
        insurance_expiry_date__lte=today + timedelta(days=reminder_days)
    ) | Vehicle.objects.filter(
        technical_control_date__lte=today + timedelta(days=reminder_days)
    )

    for vehicle in vehicles:
        user_email = vehicle.user.email
        subject = "🔔 Rappel de maintenance de votre véhicule"
        message = f"""
        Bonjour {vehicle.user.username},

        Nous vous rappelons que votre véhicule {vehicle.brand} {vehicle.model} (Plaque : {vehicle.license_plate})
        nécessite une mise à jour : 

        - Assurance expirant le {vehicle.insurance_expiry_date} 🚗
        - Contrôle technique prévu le {vehicle.technical_control_date} 🔧

        Merci de prendre les mesures nécessaires.

        L'équipe Gestion Véhicules.
        """

        send_mail(subject, message, "noreply@gestion-vehicules.com", [user_email])
    
    return f"{len(vehicles)} notifications envoyées."


@shared_task
def my_test_task():
    print("Test task is running.")
    

@shared_task
def send_confirmation_email_task(user_email):
    send_confirmation_email(user_email)
