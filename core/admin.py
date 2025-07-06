from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.contrib.auth.hashers import make_password
from django.templatetags.static import static
from django.core.exceptions import ValidationError
from .forms import ExerciceAdminForm  # L'import doit correspondre exactement au nom de la classe
from .models import (
    Utilisateur,
    Investisseur,
    Pays,
    SousSystemeEnseignement,
    Classe,
    Matiere,
    TypeExercice,
    Lecon,
    Exercice
)
from .forms import ExerciceAdminForm

# 1. Définition des formulaires personnalisés
class InvestisseurForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Investisseur
        fields = '__all__'

# 2. Définition des classes Admin
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

class LeconInline(admin.TabularInline):
    model = Lecon
    extra = 1
    fields = ('titre', 'matiere', 'fichier_pdf')
    autocomplete_fields = ['matiere']

class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'classe')
    list_filter = ('classe',)
    search_fields = ('nom', 'code')
    inlines = [LeconInline]

class SousSystemeAdmin(admin.ModelAdmin):
    list_display = ('pays', 'nom')
    list_filter = ('pays',)
    search_fields = ('nom',)

class ClasseAdmin(admin.ModelAdmin):
    list_display = ('sous_systeme', 'nom')
    list_filter = ('sous_systeme',)
    search_fields = ('nom',)

class TypeExerciceForm(forms.ModelForm):
    class Meta:
        model = TypeExercice
        fields = '__all__'
        widgets = {
            'matiere': forms.Select(attrs={'class': 'matiere-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'matiere' in self.fields:
            if self.instance and self.instance.pk:
                self.fields['matiere'].queryset = Matiere.objects.filter(
                    classe=self.instance.matiere.classe
                )
            else:
                self.fields['matiere'].queryset = Matiere.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        matiere = cleaned_data.get('matiere')
        
        if matiere and not matiere.classe:
            raise ValidationError("La matière doit être associée à une classe valide")
        
        return cleaned_data

class TypeExerciceAdmin(admin.ModelAdmin):
    form = TypeExerciceForm
    list_display = ('nom', 'matiere', 'classe_display')
    list_filter = ('matiere__classe', 'matiere')
    search_fields = ('nom', 'matiere__nom')
    autocomplete_fields = ['matiere']
    
    def classe_display(self, obj):
        return obj.matiere.classe if obj.matiere else '-'
    classe_display.short_description = 'Classe'
    classe_display.admin_order_field = 'matiere__classe'
    
    class Media:
        js = ('js/exercice_admin.js',)

class ExerciceAdminForm(forms.ModelForm):
    class Meta:
        model = Exercice
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'matiere' in self.fields and 'type_exercice' in self.fields:
            if self.instance and self.instance.pk:
                self.fields['type_exercice'].queryset = TypeExercice.objects.filter(
                    matiere=self.instance.matiere
                )
            else:
                self.fields['type_exercice'].queryset = TypeExercice.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        matiere = cleaned_data.get('matiere')
        type_exercice = cleaned_data.get('type_exercice')
        
        if matiere and type_exercice and type_exercice.matiere != matiere:
            raise ValidationError(
                "Le type d'exercice doit correspondre à la matière sélectionnée"
            )
        
        return cleaned_data

class ExerciceAdmin(admin.ModelAdmin):
    form = ExerciceAdminForm
    list_display = ('matiere', 'type_exercice', 'difficulte', 'classe_display')
    list_filter = ('matiere__classe', 'matiere', 'difficulte')
    search_fields = ('enonce_latex', 'corrige_latex')
    raw_id_fields = ('lecons',)
    autocomplete_fields = ['matiere', 'type_exercice']
    
    def classe_display(self, obj):
        return obj.matiere.classe if obj.matiere else '-'
    classe_display.short_description = 'Classe'
    classe_display.admin_order_field = 'matiere__classe'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'matiere', 'type_exercice', 'matiere__classe'
        )
    
    class Media:
        css = {
            'all': ('admin/css/overrides.css',)
        }
        js = ('js/exercice_admin.js',)

class LeconAdmin(admin.ModelAdmin):
    list_display = ('titre', 'matiere', 'classe_display')
    list_filter = ('matiere__classe', 'matiere')
    search_fields = ('titre', 'contenu_latex')
    autocomplete_fields = ['matiere']
    
    def classe_display(self, obj):
        return obj.matiere.classe if obj.matiere else '-'
    classe_display.short_description = 'Classe'
    classe_display.admin_order_field = 'matiere__classe'

class PaysAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)

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

# Configuration de l'AdminSite personnalisé
class CISAdminSite(admin.AdminSite):
    site_header = "CIS: Correcteur Intelligent de Sujets"
    site_title = "CIS Admin"
    index_title = "Administration CIS"
    enable_nav_sidebar = True

    @property
    def media(self):
        media = super().media
        media.add_css({
            'all': static('core/css/cis-admin.css'),
        })
        media.add_js(('js/admin-dynamic-filters.js',))
        return media

# Création et configuration de l'instance admin
admin_site = CISAdminSite(name='cis_admin')

# Enregistrement des modèles
admin_site.register(Utilisateur, UtilisateurAdmin)
admin_site.register(Investisseur, InvestisseurAdmin)
admin_site.register(Pays, PaysAdmin)
admin_site.register(SousSystemeEnseignement, SousSystemeAdmin)
admin_site.register(Classe, ClasseAdmin)
admin_site.register(Matiere, MatiereAdmin)
admin_site.register(TypeExercice, TypeExerciceAdmin)
admin_site.register(Lecon, LeconAdmin)
admin_site.register(Exercice, ExerciceAdmin)

# Configuration de l'admin par défaut
admin.site = admin_site