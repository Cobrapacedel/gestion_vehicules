from django.conf import settings
from django.db import models
import datetime

# Modèle pour la marque du véhicule
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Modèle pour le modèle spécifique du véhicule (lié à la marque)
class VehicleModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.brand.name} {self.name}"


# Modèle pour les documents associés à un véhicule
class Document(models.Model):
    document_type = models.CharField(max_length=100)  # Type de document (ex : "purchase", "registration", etc.)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return f'{self.document_type} document'


# Modèle principal pour les véhicules
class Vehicle(models.Model):
    # Relation avec l'utilisateur
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')

    # Informations sur le véhicule
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True, db_index=True)  # Ajout d'un index pour améliorer la recherche
    color = models.CharField(max_length=50)
    vin_number = models.CharField(max_length=50, unique=True, db_index=True)  # Ajout d'un index pour améliorer la recherche
    purchase_date = models.DateField()
    mileage = models.PositiveIntegerField()

    # Documents associés au véhicule (achat, vignette, immatriculation)
    purchase_document = models.FileField(upload_to='vehicle_documents/purchase/', null=True, blank=True)
    vignette_document = models.FileField(upload_to='vehicle_documents/vignette/', null=True, blank=True)
    registration_document = models.FileField(upload_to='vehicle_documents/registration/', null=True, blank=True)
    documents = models.ManyToManyField(Document, related_name="vehicles")

    # Informations sur l'assurance
    fuel_type = models.CharField(
        max_length=50,
        choices=[('Essence', 'Essence'),
                 ('Diesel', 'Diesel'),
                 ('Hybride', 'Hybride'),
                 ('Électrique', 'Électrique'),
                 ('GPL', 'GPL')],
    )
    insurance_company = models.CharField(max_length=100)
    insurance_policy_number = models.CharField(max_length=50)
    insurance_expiry_date = models.DateField()

    # Contrôle technique
    last_technical_check = models.DateField()
    next_technical_check = models.DateField()

    # Méthodes pour vérifier l'état des documents
    def is_insurance_expiring_soon(self):
        if self.insurance_expiry_date:
            return (self.insurance_expiry_date - datetime.date.today()).days <= 30  # Moins de 30 jours
        return False

    def is_technical_control_due(self):
        if self.next_technical_check:
            return (self.next_technical_check - datetime.date.today()).days <= 30  # Moins de 30 jours
        return False

    def get_full_name(self):
        return f"{self.brand.name} {self.model.name} ({self.year})"

    def get_remaining_days_until_insurance_expiry(self):
        if self.insurance_expiry_date:
            return (self.insurance_expiry_date - datetime.date.today()).days
        return None

    def get_remaining_days_until_technical_control(self):
        if self.next_technical_check:
            return (self.next_technical_check - datetime.date.today()).days
        return None

    # Méthode pour afficher le véhicule de manière lisible
    def __str__(self):
        return self.get_full_name()

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
# models.py/vehicules
from django.db import models
from users.models import User  # Assurez-vous que l'import est correct
from vehicles.models import Vehicle  # Vérifie si le modèle Vehicle existe

class TollTransaction(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="vehicle_tolltransaction_set")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicle_tolltransaction_set")  # Correction ici
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vehicle} - {self.amount}€ - {self.date}"

# models.py/vehicules
from django.core.mail import send_mail
from django.utils.timezone import now

def check_expired_vehicles():
    expired_vehicles = Vehicle.objects.filter(insurance_expiration__lt=now().date())
    for vehicle in expired_vehicles:
        send_mail("Renouvellement de Carte Grise", f"Votre carte grise pour {vehicle.model} a expire. Veuillez effectuer un paiement.", "noreply@gestionvehicules.com", [vehicle.owner.email])
        
class Vehicle(models.Model):
    ...
    toll_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_balance(self, amount):
        self.toll_balance -= amount
        self.save()
