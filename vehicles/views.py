from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, FileResponse
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy
from .models import Vehicle, Document
from .forms import VehicleForm, DocumentForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.models import User

class VehicleDocumentsView(DetailView):
    model = Vehicle
    template_name = 'vehicles/vehicle_documents.html'
    context_object_name = 'vehicle'

    def get_queryset(self):
        """Limite l'accès aux véhicules de l'utilisateur connecté"""
        return Vehicle.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = self.get_object()
        context['documents'] = vehicle.documents.all()  # Ajouter les documents associés
        return context

@login_required
def download_document(request, document_id):
    """Permet à un utilisateur de télécharger un document"""
    document = get_object_or_404(Document, id=document_id)

    # Vérification si l'utilisateur est autorisé à télécharger ce document
    if document.vehicle.user != request.user:
        raise Http404("Vous n'êtes pas autorisé à télécharger ce document.")

    response = FileResponse(document.file, as_attachment=True, filename=document.file.name)
    return response

@login_required
def add_document_to_vehicle(request, vehicle_id):
    """Permet d'ajouter un document à un véhicule"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            vehicle.documents.add(document)
            messages.success(request, f"Le document a été ajouté au véhicule {vehicle}.")
            return redirect('vehicle_detail', pk=vehicle.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessus.')
    else:
        form = DocumentForm()

    return render(request, 'vehicles/add_document.html', {'form': form, 'vehicle': vehicle})

class VehicleTransferView(View):
    """Vue pour le transfert de véhicule d'un utilisateur à un autre"""
    def get(self, request, pk):
        vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)

        # Récupérer l'utilisateur destinataire du transfert
        new_user_id = request.GET.get('new_user_id')
        if not new_user_id:
            messages.error(request, "Aucun utilisateur sélectionné pour le transfert.")
            return redirect('vehicle_list')

        try:
            new_user = User.objects.get(id=new_user_id)
        except User.DoesNotExist:
            raise Http404("L'utilisateur cible n'existe pas.")

        # Transfert du véhicule
        vehicle.user = new_user
        vehicle.save()

        messages.success(request, f"Le véhicule {vehicle} a été transféré à {new_user}.")
        return redirect('vehicle_list')

class VehicleUpdateView(UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicle_list')

    def get_queryset(self):
        """Assurez-vous que l'utilisateur ne peut modifier que ses propres véhicules"""
        return Vehicle.objects.filter(user=self.request.user)

class VehicleCreateView(CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicle_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Associe le véhicule à l'utilisateur connecté
        return super().form_valid(form)

class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = 'vehicles/vehicle_detail.html'
    context_object_name = 'vehicle'

    def get_queryset(self):
        """Filtre les véhicules pour que l'utilisateur ne puisse voir que les siens"""
        return Vehicle.objects.filter(user=self.request.user)

class VehicleListView(ListView):
    model = Vehicle
    template_name = 'vehicles/vehicle_list.html'
    context_object_name = 'vehicles'

    def get_queryset(self):
        """Récupère tous les véhicules de l'utilisateur connecté"""
        return Vehicle.objects.filter(user=self.request.user)

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.filter(user=request.user)
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})

@login_required
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)
    insurance_expiring_soon = vehicle.is_insurance_expiring_soon()
    technical_check_due = vehicle.is_technical_control_due()
    return render(request, 'vehicles/vehicle_detail.html', {
        'vehicle': vehicle,
        'insurance_expiring_soon': insurance_expiring_soon,
        'technical_check_due': technical_check_due,
    })

@login_required
def vehicle_add(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.user = request.user
            vehicle.save()
            messages.success(request, 'Véhicule ajouté avec succès.')
            return redirect('vehicle_list')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessus.')
    else:
        form = VehicleForm()

    return render(request, 'vehicles/vehicle_form.html', {'form': form})

@login_required
def vehicle_edit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Véhicule mis à jour avec succès.')
            return redirect('vehicle_detail', vehicle_id=vehicle.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessus.')
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'vehicles/vehicle_form.html', {'form': form})

@login_required
def vehicle_delete(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Véhicule supprimé avec succès.')
        return redirect('vehicle_list')

    return render(request, 'vehicles/vehicle_confirm_delete.html', {'vehicle': vehicle})

@login_required
def document_add(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.save()
            vehicle.documents.add(document)
            vehicle.save()
            messages.success(request, 'Document ajouté avec succès.')
            return redirect('vehicle_detail', vehicle_id=vehicle.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessus.')
    else:
        form = DocumentForm()

    return render(request, 'vehicles/document_form.html', {'form': form, 'vehicle': vehicle})

@login_required
def vehicle_documents(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, user=request.user)
    return render(request, 'vehicles/vehicle_documents.html', {'vehicle': vehicle})

@login_required
def document_detail(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    return render(request, 'vehicles/document_detail.html', {'document': document})
