import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField
from django.conf import settings
from PIL import Image
import pytesseract  # OCR pour validation de document
import phonenumbers
import re
import django.apps
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model





# Fonction de validation du numéro de téléphone
def validate_phone_number(value):
    try:
        phone = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(phone):
            raise ValidationError("Le numéro de téléphone est invalide.")
    except phonenumbers.NumberParseException:
        raise ValidationError("Le numéro de téléphone est invalide.")


# Fonction de validation du fichier d'identité avec OCR
def validate_identity_document(value):
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
    extension = value.name.split('.')[-1].lower()
    if extension not in allowed_extensions:
        raise ValidationError("Le document d'identité doit être au format PDF, JPG, JPEG ou PNG.")
    if value.size > 5 * 1024 * 1024:  # Limite de 5 Mo
        raise ValidationError("Le document d'identité ne doit pas dépasser 5 Mo.")

    # Vérification OCR
    try:
        img = Image.open(value)
        text = pytesseract.image_to_string(img)
        if len(text.strip()) == 0:
            raise ValidationError("Le fichier d'identité ne contient pas de texte pertinent.")
    except Exception as e:
        raise ValidationError(f"Erreur OCR : {str(e)}")


# Fonction pour renommer les fichiers d'identité
def identity_document_upload_path(instance, filename):
    extension = filename.split('.')[-1]
    return f"identity_documents/{instance.id}_{uuid.uuid4()}.{extension}"


# Fonction pour renommer les avatars
def avatar_upload_path(instance, filename):
    extension = filename.split('.')[-1]
    return f"avatars/{instance.id}_{uuid.uuid4()}.{extension}"


# Modèle utilisateur personnalisé
class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(
        max_length=15, blank=True, null=True,
        validators=[RegexValidator(r'^\+?\d{9,15}$', message="Le numéro de téléphone doit être valide.")],
        unique=True
    )
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    identity_document = models.FileField(
        upload_to=identity_document_upload_path, blank=True, null=True,
        validators=[validate_identity_document]
    )
    is_verified = models.BooleanField(default=False, help_text="Indique si l'utilisateur a été vérifié via KYC.")
    is_active = models.BooleanField(default=False, help_text="Compte activé après vérification.")
    role = models.CharField(
        max_length=10, choices=[('admin', 'Administrateur'), ('user', 'Utilisateur')],
        default='user', help_text="Rôle de l'utilisateur."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """
        Validation du mot de passe
        """
        super().clean()
        if self.password:
            if len(self.password) < 8:
                raise ValidationError(_("Le mot de passe doit contenir au moins 8 caractères."))
            if not re.search(r"[A-Z]", self.password):
                raise ValidationError(_("Le mot de passe doit contenir au moins une lettre majuscule."))
            if not re.search(r"[a-z]", self.password):
                raise ValidationError(_("Le mot de passe doit contenir au moins une lettre minuscule."))
            if not re.search(r"[0-9]", self.password):
                raise ValidationError(_("Le mot de passe doit contenir au moins un chiffre."))
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", self.password):
                raise ValidationError(_("Le mot de passe doit contenir au moins un caractère spécial."))

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() if self.first_name and self.last_name else self.username

    def __str__(self):
        return f"{self.username} ({self.email})"

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

User = get_user_model()  # Utilise la fonction get_user_model() pour récupérer le modèle d'utilisateur personnalisé
# Modèle de station de péage
class TollStation(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    route = models.CharField(max_length=255)

    def __str__(self):
        return self.name


# Modèle de véhicule
class Vehicle(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_vehicles")
    registration_number = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=100, unique=True)
    toll_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"

    def update_balance(self, amount):
        """Met à jour le solde du véhicule pour le péage"""
        self.toll_balance -= amount
        self.save()


# Modèle de transaction de péage
class TollTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="toll_transactions")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="toll_transactions")
    toll_station = models.ForeignKey(TollStation, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.vehicle} - {self.amount}€"


# Modèle de profil utilisateur
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    toll_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vehicles = models.ManyToManyField(Vehicle, related_name="owners")
    transactions = models.ManyToManyField(TollTransaction, related_name="user_profiles", through='UserProfileTollTransaction')

    def __str__(self):
        return self.user.username

    def add_funds(self, amount):
        """Ajoute des fonds au solde de péage de l'utilisateur."""
        self.toll_balance += amount
        self.save()

    def deduct_funds(self, amount):
        """Déduit des fonds du solde de péage de l'utilisateur."""
        self.toll_balance -= amount
        self.save()


# Modèle intermédiaire pour la relation UserProfile-TollTransaction
class UserProfileTollTransaction(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    toll_transaction = models.ForeignKey(TollTransaction, on_delete=models.CASCADE)

    def __str__(self):
        return f"Transaction de {self.user_profile} - {self.toll_transaction}"
