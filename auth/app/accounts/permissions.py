from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'  # Vérifie si l'utilisateur est authentifié et a le rôle d'administrateur
    

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated  # Vérifie si l'utilisateur est authentifié