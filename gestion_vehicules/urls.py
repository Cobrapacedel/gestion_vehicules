from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from . import views

# Test view
def test_view(request):
    return JsonResponse({'status': 'ok'})

# URLs principales
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("core.urls")),  # Ajout de la page d'accueil
    path("users/", include("users.urls")),
    path('vehicles/', include('vehicles.urls')),
    path('accounts/', include('allauth.urls')),  # Ajout de Allauth
    path('payments/', include("payments.urls")),
    path('', views.index, name='index'),  # Index personnalisé
    path('test/', test_view),  # Test view
]

# Configurer les fichiers médias
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
