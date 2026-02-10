"""
Permissions personnalisées pour le module d'authentification.
Permissions basées sur les rôles et les fonctionnalités.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated
from django.utils.translation import gettext_lazy as _


class IsAdmin(BasePermission):
    """
    Classe de permission pour les administrateurs.
    Autorise l'accès uniquement aux utilisateurs avec le rôle admin.
    """
    
    # Message d'erreur affiché si l'accès est refusé
    message = _('Vous devez être administrateur pour effectuer cette action.')
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur est authentifié et est admin.
        
        Args:
            request: La requête HTTP
            view: La vue concernée
        
        Returns:
            bool: True si l'utilisateur est admin, False sinon
        """
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsModerator(BasePermission):
    """
    Classe de permission pour les modérateurs.
    Autorise l'accès aux utilisateurs avec rôle modérateur ou admin.
    """
    
    message = _('Vous devez être modérateur pour effectuer cette action.')
    
    def has_permission(self, request, view):
        """Vérifie si l'utilisateur est modérateur ou admin."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['moderator', 'admin']
        )


class IsStaff(BasePermission):
    """
    Classe de permission pour le personnel.
    Autorise l'accès aux utilisateurs avec rôle modérateur ou admin.
    """
    
    message = _('Vous devez être membre du personnel pour effectuer cette action.')
    
    def has_permission(self, request, view):
        """Vérifie si l'utilisateur fait partie du staff."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['moderator', 'admin']
        )


class IsActive(BasePermission):
    """
    Classe de permission pour les utilisateurs actifs.
    Vérifie si le compte utilisateur est actif.
    """
    
    message = _('Votre compte est inactif. Veuillez contacter le support.')
    
    def has_permission(self, request, view):
        """Vérifie si le compte est actif."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )


class IsNotBlocked(BasePermission):
    """
    Classe de permission pour les utilisateurs non bloqués.
    Vérifie si le compte utilisateur n'est pas bloqué.
    """
    
    message = _('Votre compte a été bloqué. Veuillez contacter le support.')
    
    def has_permission(self, request, view):
        """Vérifie que le compte n'est pas bloqué."""
        return (
            request.user and
            request.user.is_authenticated and
            not request.user.is_blocked
        )


class IsVerified(BasePermission):
    """
    Classe de permission pour les utilisateurs vérifiés.
    Vérifie si l'utilisateur a vérifié son email.
    """
    
    message = _('Veuillez vérifier votre email pour accéder à cette ressource.')
    
    def has_permission(self, request, view):
        """Vérifie que l'email est vérifié."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_email_verified
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Classe de permission pour l'accès au niveau objet.
    Les propriétaires ont un accès complet, les autres lecture seule.
    """
    
    message = _('Vous n\'avez pas la permission d\'accéder à cette ressource.')
    
    def has_object_permission(self, request, view, obj):
        """
        Vérifie les permissions au niveau de l'objet.
        
        Args:
            request: La requête HTTP
            view: La vue concernée
            obj: L'objet concerné
        
        Returns:
            bool: True si accès autorisé
        """
        # Les méthodes sûres (GET, HEAD, OPTIONS) sont toujours autorisées
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Sinon, vérifier que l'utilisateur est propriétaire
        return obj.id == request.user.id


class IsAdminOrOwner(BasePermission):
    """
    Classe de permission pour admin ou propriétaire.
    Les admins ont un accès complet, les propriétaires peuvent modifier leurs données.
    """
    
    message = _('Vous n\'avez pas la permission d\'accéder à cette ressource.')
    
    def has_object_permission(self, request, view, obj):
        """Vérifie si l'utilisateur est admin ou propriétaire de l'objet."""
        if request.user.role == 'admin':
            return True
        return obj.id == request.user.id


class RateLimitExceeded(BasePermission):
    """
    Classe de permission pour la limitation de débit.
    Vérifie si l'utilisateur a dépassé sa limite de taux.
    """
    
    message = _('Limite de taux dépassée. Veuillez réessayer plus tard.')
    
    def has_permission(self, request, view):
        """
        Vérifie si l'utilisateur n'a pas dépassé sa limite.
        La limitation de débit est gérée par le middleware.
        """
        return True


class IsNotAuthenticated(BasePermission):
    """
    Classe de permission pour les utilisateurs non authentifiés.
    Autorise l'accès uniquement aux utilisateurs non connectés.
    """
    
    message = _('Vous êtes déjà authentifié.')
    
    def has_permission(self, request, view):
        """Vérifie que l'utilisateur n'est pas connecté."""
        return not request.user.is_authenticated


class UserPermissions:
    """
    Classe utilitaire qui fournit des combinaisons de permissions courantes.
    Facilite l'utilisation des permissions dans les vues.
    """
    
    @staticmethod
    def public():
        """
        Accès public - aucune authentification requise.
        
        Returns:
            list: Liste vide de permissions
        """
        return []
    
    @staticmethod
    def authenticated():
        """
        Authentification requise.
        
        Returns:
            list: [IsAuthenticated]
        """
        return [IsAuthenticated]
    
    @staticmethod
    def active():
        """
        Compte actif requis.
        
        Returns:
            list: [IsAuthenticated, IsActive]
        """
        return [IsAuthenticated, IsActive]
    
    @staticmethod
    def verified():
        """
        Email vérifié requis.
        
        Returns:
            list: [IsAuthenticated, IsActive, IsVerified]
        """
        return [IsAuthenticated, IsActive, IsVerified]
    
    @staticmethod
    def admin():
        """
        Rôle admin requis.
        
        Returns:
            list: [IsAuthenticated, IsAdmin]
        """
        return [IsAuthenticated, IsAdmin]
    
    @staticmethod
    def staff():
        """
        Rôle modérateur ou admin requis.
        
        Returns:
            list: [IsAuthenticated, IsModerator]
        """
        return [IsAuthenticated, IsModerator]
    
    @staticmethod
    def owner_or_admin():
        """
        Admin ou propriétaire de l'objet.
        
        Returns:
            list: [IsAuthenticated, IsAdminOrOwner]
        """
        return [IsAuthenticated, IsAdminOrOwner]
