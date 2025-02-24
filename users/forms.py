import re
import uuid
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from PIL import Image
import pytesseract  # Utilisé pour l'OCR
import phonenumbers
from .models import CustomUser

# Fonction de validation du numéro de téléphone (validation internationale)
def validate_phone_number(value):
    """
    Validates the phone number using the phonenumbers library.
    """
    try:
        phone = phonenumbers.parse(value, None)
        if not phonenumbers.is_valid_number(phone):
            raise ValidationError("Le numéro de téléphone est invalide.")
    except phonenumbers.NumberParseException:
        raise ValidationError("Le numéro de téléphone est invalide.")

# Fonction de validation du document d'identité avec OCR
def validate_identity_document(value):
    """
    Validate identity document by extension, size, and OCR text content.
    """
    allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
    extension = value.name.split('.')[-1].lower()
    if extension not in allowed_extensions:
        raise ValidationError("Le document d'identité doit être au format PDF, JPG, JPEG ou PNG.")
    if value.size > 5 * 1024 * 1024:  # Limite de 5 Mo
        raise ValidationError("Le document d'identité ne doit pas dépasser 5 Mo.")
    
    # Tentative de reconnaissance OCR pour vérifier si le fichier contient des informations pertinentes
    try:
        img = Image.open(value)
        text = pytesseract.image_to_string(img)
        if len(text.strip()) == 0:
            raise ValidationError("Le fichier d'identité ne contient pas de texte pertinent.")
    except Exception as e:
        raise ValidationError(f"Erreur lors de la validation du document d'identité : {str(e)}")

# Définition des chemins de téléchargement pour éviter les collisions de noms
def identity_document_upload_path(instance, filename):
    extension = filename.split('.')[-1]
    return f"identity_documents/{instance.id}_{uuid.uuid4()}.{extension}"

def avatar_upload_path(instance, filename):
    extension = filename.split('.')[-1]
    return f"avatars/{instance.id}_{uuid.uuid4()}.{extension}"

class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire de création d'un utilisateur personnalisé.
    """
    phone_number = forms.CharField(
        max_length=15, 
        required=False, 
        validators=[RegexValidator(r'^\+?\d{9,15}$', message="Le numéro de téléphone doit être valide.")]
    )
    avatar = forms.ImageField(required=False)
    identity_document = forms.FileField(required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'phone_number', 'avatar', 'identity_document', 'address', 'bio']

    def clean_password1(self):
        """
        Validation du mot de passe lors de la création.
        """
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(_(" ".join(e.messages)))
        return password

    def clean_identity_document(self):
        """
        Validation personnalisée du document d'identité.
        """
        identity_document = self.cleaned_data.get('identity_document')
        if identity_document:
            validate_identity_document(identity_document)
        return identity_document

    def clean_phone_number(self):
        """
        Validation du numéro de téléphone.
        """
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            validate_phone_number(phone_number)
        return phone_number

    def save(self, commit=True):
        """
        Sauvegarde personnalisée de l'utilisateur.
        """
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Formulaire de modification d'un utilisateur personnalisé.
    """
    phone_number = forms.CharField(
        max_length=15, 
        required=False, 
        validators=[RegexValidator(r'^\+?\d{9,15}$', message="Le numéro de téléphone doit être valide.")]
    )
    avatar = forms.ImageField(required=False)
    identity_document = forms.FileField(required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'avatar', 'identity_document', 'address', 'bio']

    def clean_identity_document(self):
        """
        Validation du document d'identité lors de la mise à jour.
        """
        identity_document = self.cleaned_data.get('identity_document')
        if identity_document:
            validate_identity_document(identity_document)
        return identity_document

    def clean_phone_number(self):
        """
        Validation du numéro de téléphone lors de la mise à jour.
        """
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            validate_phone_number(phone_number)
        return phone_number

    def save(self, commit=True):
        """
        Sauvegarde personnalisée lors de la mise à jour.
        """
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
