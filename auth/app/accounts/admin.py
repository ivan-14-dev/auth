"""
Configuration Django Admin pour le module d'authentification.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuration admin personnalisée pour le modèle User.
    Fournit une gestion complète des utilisateurs dans Django Admin.
    """
    
    # Champs affichés dans la liste des utilisateurs
    list_display = ('email', 'username', 'role', 'is_active', 'is_blocked', 'created_at')
    
    # Filtres disponibles dans la liste
    list_filter = ('role', 'is_active', 'is_blocked', 'created_at')
    
    # Champs de recherche
    search_fields = ('email', 'username', 'phone_number')
    
    # Tri par défaut
    ordering = ('-created_at',)
    
    # Champs en lecture seule
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    # Sections du formulaire d'édition
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {
            'fields': (
                'username', 'email_recuperation', 'phone_number',
                'address', 'country', 'avatar', 'bio'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'role', 'is_active', 'is_blocked',
                'is_email_verified', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )
    
    # Configuration du formulaire d'ajout
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )
    
    # Actions personnalisées
    actions = ['activate_users', 'deactivate_users', 'block_users', 'unblock_users']
    
    def activate_users(self, request, queryset):
        """Active les utilisateurs sélectionnés."""
        queryset.update(is_active=True)
    activate_users.short_description = _('Activer les utilisateurs sélectionnés')
    
    def deactivate_users(self, request, queryset):
        """Désactive les utilisateurs sélectionnés."""
        queryset.update(is_active=False)
    deactivate_users.short_description = _('Désactiver les utilisateurs sélectionnés')
    
    def block_users(self, request, queryset):
        """Bloque les utilisateurs sélectionnés."""
        queryset.update(is_blocked=True)
    block_users.short_description = _('Bloquer les utilisateurs sélectionnés')
    
    def unblock_users(self, request, queryset):
        """Débloque les utilisateurs sélectionnés."""
        queryset.update(is_blocked=False)
    unblock_users.short_description = _('Débloquer les utilisateurs sélectionnés')
