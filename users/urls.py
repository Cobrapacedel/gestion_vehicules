from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Vue d'inscription
    path('register/', views.SignUpView.as_view(), name='signup'),
    
    path('', views.index, name='index'),
    
    # Vue de connexion
    path('login/', views.login_view, name='login'),
    
    # Vue de déconnexion
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Vue pour la mise à jour du profil utilisateur (protégée par login)
    path('profile/update/', login_required(views.UserUpdateView.as_view()), name='profile_update'),
    
    # Vue pour la page d'accueil (protégée par login)
    path('', login_required(views.home), name='home'),
]
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('pay-toll/<int:vehicle_id>/<int:station_id>/', views.process_toll_payment, name='pay_toll'),
]
# urls.py (dans l'app users)
from django.urls import path
from . import views

urlpatterns = [
    path('transaction-history/', views.transaction_history, name='transaction_history'),
    path('add-funds/', views.add_funds, name='add_funds'),
]