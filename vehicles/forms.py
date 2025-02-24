from django import forms
from .models import Vehicle, Document, Brand, VehicleModel
from django.core.exceptions import ValidationError
import datetime
import re

# Formulaire pour ajouter ou modifier un véhicule
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'brand', 'model', 'year', 'license_plate', 'color', 'vin_number',
            'purchase_date', 'mileage', 'fuel_type', 'insurance_company', 
            'insurance_policy_number', 'insurance_expiry_date', 'last_technical_check', 
            'next_technical_check', 'purchase_document', 'vignette_document', 'registration_document'
        ]
        
        widgets = {
            'insurance_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'last_technical_check': forms.DateInput(attrs={'type': 'date'}),
            'next_technical_check': forms.DateInput(attrs={'type': 'date'}),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_license_plate(self):
        license_plate = self.cleaned_data.get('license_plate')
        # Validation: Vérifier que la plaque d'immatriculation est unique et respecter un format
        if Vehicle.objects.filter(license_plate=license_plate).exists():
            raise ValidationError("Cette plaque d'immatriculation est déjà enregistrée.")
        
        # Validation : vérifier un format standard de plaque d'immatriculation
        pattern = r'^[A-Z0-9]{2,7}$'  # Format simple, peut être ajusté
        if not re.match(pattern, license_plate):
            raise ValidationError("Le format de la plaque d'immatriculation est invalide.")
        
        return license_plate

    def clean_vin_number(self):
        vin_number = self.cleaned_data.get('vin_number')
        # Validation : Vérifier que le numéro VIN est unique
        if Vehicle.objects.filter(vin_number=vin_number).exists():
            raise ValidationError("Ce numéro de série est déjà enregistré.")
        
        # Validation : vérifier un format standard du VIN (17 caractères alphanumériques)
        if len(vin_number) != 17 or not vin_number.isalnum():
            raise ValidationError("Le numéro de série (VIN) doit comporter 17 caractères alphanumériques.")
        
        return vin_number

    def clean_insurance_expiry_date(self):
        insurance_expiry_date = self.cleaned_data.get('insurance_expiry_date')
        # Validation: L'assurance ne peut pas être dans le passé
        if insurance_expiry_date and insurance_expiry_date < datetime.date.today():
            raise ValidationError("La date d'expiration de l'assurance ne peut pas être dans le passé.")
        return insurance_expiry_date

    def clean_mileage(self):
        mileage = self.cleaned_data.get('mileage')
        # Validation: Le kilométrage ne peut pas être négatif
        if mileage and mileage < 0:
            raise ValidationError("Le kilométrage ne peut pas être négatif.")
        return mileage

    def clean_purchase_date(self):
        purchase_date = self.cleaned_data.get('purchase_date')
        # Validation: La date d'achat ne peut pas être dans le futur
        if purchase_date and purchase_date > datetime.date.today():
            raise ValidationError("La date d'achat ne peut pas être dans le futur.")
        return purchase_date

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        # Validation : Vérifier les extensions du fichier
        if file:
            allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            extension = file.name.split('.')[-1].lower()
            if extension not in allowed_extensions:
                raise ValidationError("Les formats autorisés sont PDF, JPG, JPEG, PNG.")
            
            # Limite de taille du fichier (5 Mo)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("Le fichier ne doit pas dépasser 5 Mo.")
        
        return file

class VehicleSelectionForm(forms.Form):
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=True)
    model = forms.ModelChoiceField(queryset=VehicleModel.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        brand = kwargs.get('brand')
        super().__init__(*args, **kwargs)
        if brand:
            self.fields['model'].queryset = VehicleModel.objects.filter(brand=brand)

    def clean(self):
        cleaned_data = super().clean()
        brand = cleaned_data.get('brand')
        model = cleaned_data.get('model')

        # Validation pour vérifier que le modèle correspond bien à la marque
        if brand and model and model.brand != brand:
            raise ValidationError("Le modèle sélectionné n'appartient pas à la marque choisie.")

        return cleaned_data
