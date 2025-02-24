from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()  # ✅ Solution propre

def check_user_activation(user):
    """
    Vérifie si l'utilisateur a activé son compte.
    """
    if not user.is_active:
        messages.error(user.request, "Votre compte n'est pas activé. Veuillez vérifier votre email.")
        return False
    return True

class SignUpView(CreateView):
    """
    Vue pour l'inscription d'un nouvel utilisateur avec activation par email.
    """
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False  # Désactive le compte jusqu'à confirmation email
        user.save()
        messages.success(self.request, "Votre compte a été créé. Vérifiez votre email pour l'activer.")
        # Envoyer un email d'activation ici (à implémenter)
        return redirect('login')

def login_view(request):
    """
    Vue pour la connexion d'un utilisateur avec vérification de l'activation.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not check_user_activation(user):
                return redirect('login')
            login(request, user)
            messages.success(request, "Vous êtes maintenant connecté.")
            return redirect('home')
        else:
            messages.error(request, "Identifiants incorrects. Veuillez réessayer.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

class UserUpdateView(UpdateView):
    """
    Vue pour la mise à jour des informations utilisateur.
    """
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        """
        Retourne l'objet utilisateur uniquement si l'utilisateur est authentifié.
        """
        if self.request.user.is_authenticated:
            return self.request.user
        raise PermissionDenied("Vous n'êtes pas autorisé à modifier ces informations.")
        

    def form_valid(self, form):
        """
        Validation du formulaire avec un message de succès.
        """
        form.save()
        messages.success(self.request, "Vos informations ont été mises à jour avec succès.")
        return redirect(self.success_url)

class CustomLogoutView(LogoutView):
    """
    Vue pour la déconnexion sécurisée.
    """
    next_page = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Affichage d'un message de succès après déconnexion.
        """
        messages.success(request, "Vous avez été déconnecté avec succès.")
        return super().dispatch(request, *args, **kwargs)

@login_required
def home(request):
    """
    Vue pour la page d'accueil sécurisée.
    """
    # Optimisation : vérifier que l'utilisateur a des véhicules associés à son compte.
    user_vehicles = request.user.vehicles.all()
    if not user_vehicles.exists():
        messages.warning(request, "Vous n'avez pas encore ajouté de véhicule.")
    return render(request, 'home.html', {'vehicles': user_vehicles})
# views.py
from django.core.mail import send_mail

def send_payment_notification(user_email, transaction):
    send_mail(
        'Confirmation de Péage',
        f'Votre paiement de {transaction.amount}€ pour le péage {transaction.toll_station.name} a été effectué avec succès.',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )
            # views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import TollStation, Vehicle, TollTransaction
import stripe

# Assurez-vous de configurer Stripe dans votre settings.py
stripe.api_key = 'votre_cle_secrète'

def process_toll_payment(request, vehicle_id, station_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    toll_station = get_object_or_404(TollStation, id=station_id)
    
    # Vérification si le véhicule a assez de fonds pour payer
    if vehicle.toll_balance >= toll_station.fee:
        # Déduire le montant du solde du véhicule
        vehicle.update_balance(toll_station.fee)
        
        # Enregistrer la transaction
        transaction = TollTransaction.objects.create(
            vehicle=vehicle,
            toll_station=toll_station,
            amount=toll_station.fee,
            paid=True,
            payment_method="Carte"
        )

        # Simuler un paiement via Stripe
        try:
            stripe.Charge.create(
                amount=int(toll_station.fee * 100),  # Convertir en centimes
                currency="eur",
                description=f"Péage {toll_station.name} pour {vehicle.registration_number}",
                source=request.POST['stripeToken'],  # Utilise un token Stripe généré côté client
            )
        except stripe.error.StripeError as e:
            # En cas d'erreur de paiement
            return JsonResponse({'error': str(e)}, status=400)
        
        return JsonResponse({'message': 'Péage payé avec succès', 'transaction_id': transaction.id})
    else:
        return JsonResponse({'error': 'Solde insuffisant pour ce péage'}, status=400)
        # views.py
from django.core.mail import send_mail

def send_payment_notification(user_email, transaction):
    send_mail(
        'Confirmation de Péage',
        f'Votre paiement de {transaction.amount}€ pour le péage {transaction.toll_station.name} a été effectué avec succès.',
        'from@example.com',
        [user_email],
        fail_silently=False,
    )
    # views.py
def transaction_history(request):
    user = request.user
    vehicles = user.vehicles.all()  # Assurez-vous que l'utilisateur a des véhicules associés
    transactions = TollTransaction.objects.filter(vehicle__in=vehicles)
    
    return render(request, 'transactions_history.html', {'transactions': transactions})
    # views.py (dans l'app users)
from django.shortcuts import render
from .models import UserProfile
from vehicles.models import TollTransaction

def transaction_history(request):
    user_profile = request.user.userprofile  # Récupérer le profil utilisateur
    transactions = TollTransaction.objects.filter(vehicle__owner=request.user)
    
    return render(request, 'users/transaction_history.html', {'transactions': transactions})
    # views.py (dans l'app users)
from django.shortcuts import render
from .models import UserProfile
from django.http import JsonResponse

def add_funds(request):
    if request.method == 'POST':
        amount = request.POST.get('amount', 0)
        if amount:
            user_profile = request.user.userprofile
            user_profile.add_funds(float(amount))
            return JsonResponse({'message': 'Fonds ajoutés avec succès', 'new_balance': user_profile.toll_balance})
        else:
            return JsonResponse({'error': 'Montant invalide'}, status=400)
    return render(request, 'users/add_funds.html')
    