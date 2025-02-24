from django.shortcuts import render

def search_vehicles(request):
    return render(request, 'search.html')
