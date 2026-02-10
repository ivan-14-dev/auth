"""
Configuration des URLs principales pour le projet Auth.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schéma de documentation API
schema_view = get_schema_view(
    openapi.Info(
        title="API d'Authentification",
        default_version='v1',
        description="Documentation complète de l'API du module d'authentification",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="Licence MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Liste des URLs principales
urlpatterns = [
    # ==================== Administration Django ====================
    # Interface d'administration Django
    path('admin/', admin.site.urls),
    
    # ==================== Documentation de l'API ====================
    # Interface Swagger UI pour la documentation interactive
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    
    # Interface ReDoc pour la documentation alternative
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api-redoc'),
    
    # ==================== API d'authentification ====================
    # Inclure les URLs de l'application accounts
    path('api/v1/', include('app.accounts.urls')),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
