from django.urls import path, include  # Ajout de 'include' ici
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from core.views import (  # Import depuis votre app core
    filter_matieres,
    filter_lecons
)

urlpatterns = [
    # Interface d'administration
    path('admin/', admin.site.urls),
    
    # API pour le filtrage dynamique
    path('admin/filter-matieres/', filter_matieres, name='filter_matieres'),
    path('admin/filter-lecons/', filter_lecons, name='filter_lecons'),
    
    # Ajoutez ici vos autres URLs
    # path('votre_app/', include('votre_app.urls')),
]

# Debug Toolbar (uniquement en développement)
#if settings.DEBUG:
    #urlpatterns += [
        #path('__debug__/', include('debug_toolbar.urls')),
    #]
    # Servir les fichiers média/statiques
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)