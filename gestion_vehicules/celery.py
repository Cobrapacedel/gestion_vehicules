import os
from datetime import timedelta
from celery import Celery

# Définir le module de configuration par défaut pour Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_vehicules.settings")

app = Celery("gestion_vehicules")

# Charger les configurations depuis settings.py
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discovery des tâches Celery dans les applications Django
app.autodiscover_tasks()

# Configuration du fuseau horaire de Celery (important pour la planification des tâches)
app.conf.timezone = 'UTC'  # Ou 'Europe/Paris' si tu veux utiliser l'heure locale

# Planification des tâches périodiques avec Celery Beat
app.conf.beat_schedule = {
    "send-vehicle-reminders-every-day": {
        "task": "vehicles.tasks.send_vehicle_reminders",  # Assurez-vous que cette tâche existe
        "schedule": timedelta(days=1),  # Exécuter tous les jours
    },
}
