"""
Configuration des URLs pour le module d'authentification.
Points de terminaison API pour l'authentification et la gestion des utilisateurs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    HealthCheckView, RegisterView, LoginView, LogoutView,
    ProfileView, ProfileUpdateView, PasswordChangeView,
    PasswordResetRequestView, PasswordResetConfirmView,
    EmailVerificationRequestView, UserListView, UserDetailView,
    AdminUserUpdateView, UserViewSet
)

# Créer un routeur pour le ViewSet
router = DefaultRouter()
# Enregistrer le ViewSet des utilisateurs avec le routeur
router.register(r'users', UserViewSet, basename='user')

# Liste des URLs de l'application
urlpatterns = [
    # ==================== Vérification de l'état du service ====================
    # Point de terminaison pour vérifier que le service fonctionne
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # ==================== Points de terminaison d'authentification ====================
    # Inscription d'un nouvel utilisateur
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # Connexion d'un utilisateur
    path('auth/login/', LoginView.as_view(), name='login'),
    
    # Déconnexion d'un utilisateur
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # Rafraîchissement du token d'accès
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # ==================== Gestion du mot de passe ====================
    # Changement de mot de passe (authentifié)
    path('auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
    
    # Demande de réinitialisation du mot de passe
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    
    # Confirmation de la réinitialisation du mot de passe
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # ==================== Vérification de l'email ====================
    # Demande d'envoi de l'email de vérification
    path('auth/email/verify/', EmailVerificationRequestView.as_view(), name='email-verify-request'),
    
    # ==================== Points de terminaison du profil ====================
    # Récupération du profil de l'utilisateur actuel
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Mise à jour du profil de l'utilisateur actuel
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    
    # ==================== Points de terminaison d'administration ====================
    # Liste de tous les utilisateurs (admin uniquement)
    path('admin/users/', UserListView.as_view(), name='user-list'),
    
    # Détails d'un utilisateur spécifique (admin uniquement)
    path('admin/users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    
    # Mise à jour d'un utilisateur spécifique (admin uniquement)
    path('admin/users/<int:user_id>/update/', AdminUserUpdateView.as_view(), name='admin-user-update'),
    
    # ==================== URLs du ViewSet ====================
    # Inclure les URLs générées par le routeur
    path('', include(router.urls)),
]

# Ajouter les URLs du routeur à la liste principale
urlpatterns += router.urls
