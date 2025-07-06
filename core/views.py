from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from .models import Matiere, Lecon

def filter_matieres(request):
    classe_id = request.GET.get('classe_id')
    matieres = Matiere.objects.filter(classe_id=classe_id).values('id', 'nom')
    return JsonResponse({'matieres': list(matieres)})

def filter_lecons(request):
    matiere_id = request.GET.get('matiere_id')
    lecons = Lecon.objects.filter(matiere_id=matiere_id).values('id', 'titre')
    return JsonResponse({'lecons': list(lecons)})