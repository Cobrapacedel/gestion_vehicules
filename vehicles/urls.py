from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Route pour afficher la liste des véhicules d'un utilisateur
    path('my-vehicles/', login_required(views.VehicleListView.as_view()), name='vehicle_list'),
    
    path('', views.index, name='index'),
    
    # Inclure les URLs de l'app "users" pour la gestion des utilisateurs
    path('users/', include('users.urls')),  

    # Route pour afficher le détail d'un véhicule spécifique
    path('vehicle/<int:pk>/', login_required(views.VehicleDetailView.as_view()), name='vehicle_detail'),

    # Route pour ajouter un nouveau véhicule
    path('add-vehicle/', login_required(views.VehicleCreateView.as_view()), name='vehicle_create'),

    # Route pour modifier un véhicule existant
    path('edit-vehicle/<int:pk>/', login_required(views.VehicleUpdateView.as_view()), name='vehicle_update'),

    # Route pour supprimer (transférer) un véhicule à un autre utilisateur
    path('transfer-vehicle/<int:pk>/', login_required(views.VehicleTransferView.as_view()), name='vehicle_transfer'),

    # Route pour ajouter un document à un véhicule
    path('add-document/<int:vehicle_id>/', login_required(views.add_document_to_vehicle), name='add_document_to_vehicle'),

    # Route pour télécharger un document associé à un véhicule
    path('download-document/<int:document_id>/', login_required(views.download_document), name='download_document'),

    # Route pour gérer les documents associés à un véhicule
    path('documents/<int:vehicle_id>/', login_required(views.VehicleDocumentsView.as_view()), name='vehicle_documents'),
]
