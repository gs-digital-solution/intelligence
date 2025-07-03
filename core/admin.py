from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import *

class InvestisseurForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Investisseur
        fields = '__all__'

@admin.register(Investisseur)
class InvestisseurAdmin(admin.ModelAdmin):
    form = InvestisseurForm
    list_display = ('nom', 'email', 'pourcentage', 'date_investissement')
    search_fields = ('nom', 'email')
    list_filter = ('date_investissement',)
    fieldsets = (
        (None, {
            'fields': ('nom', 'telephone', 'email')
        }),
        ('Investissement', {
            'fields': ('pourcentage', 'date_investissement', 'date_cloture')
        }),
        ('Accès', {
            'fields': ('password',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'gmail', 'type_compte', 'statut_abonnement')
    list_filter = ('type_compte', 'statut_abonnement')
    search_fields = ('username', 'email', 'gmail')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'gmail', 'telephone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Métadonnées', {'fields': ('type_compte', 'statut_abonnement', 'last_login', 'date_joined')}),
    )

admin.site.register(Utilisateur, UtilisateurAdmin)

class LeconInline(admin.TabularInline):
    model = Lecon
    extra = 1

@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    filter_horizontal = ('classes',)
    list_display = ('nom', 'code')
    search_fields = ('nom', 'code')
    inlines = [LeconInline]

@admin.register(SousSystemeEnseignement)
class SousSystemeAdmin(admin.ModelAdmin):
    list_display = ('pays', 'type_systeme', 'nom')
    list_filter = ('pays', 'type_systeme')
    search_fields = ('nom',)

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('sous_systeme', 'nom')
    list_filter = ('sous_systeme',)
    search_fields = ('nom',)

@admin.register(TypeExercice)
class TypeExerciceAdmin(admin.ModelAdmin):
    list_display = ('matiere', 'nom')
    list_filter = ('matiere',)
    search_fields = ('nom', 'description')

class ExerciceAdminForm(forms.ModelForm):
    class Meta:
        model = Exercice
        fields = '__all__'
        widgets = {
            'lecons': forms.CheckboxSelectMultiple,
        }

@admin.register(Exercice)
class ExerciceAdmin(admin.ModelAdmin):
    form = ExerciceAdminForm
    list_display = ('type_exercice', 'difficulte', 'date_creation')
    list_filter = ('type_exercice', 'difficulte')
    search_fields = ('enonce_latex', 'corrige_latex')
    filter_horizontal = ('lecons',)

@admin.register(Lecon)
class LeconAdmin(admin.ModelAdmin):
    list_display = ('matiere', 'classe', 'titre')
    list_filter = ('matiere', 'classe')
    search_fields = ('titre', 'contenu_latex')

@admin.register(Pays)
class PaysAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code')
    search_fields = ('nom', 'code')