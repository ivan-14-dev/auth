"""
Configuration de l'application Django pour le module d'authentification.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Configuration de l'application accounts.
    Inclut l'enregistrement des signaux au démarrage.
    """
    
    # Type de champ de clé primaire par défaut
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nom de l'application
    name = 'app.accounts'
    
    # Nom affiché dans Django Admin
    verbose_name = 'Authentification'
    
    def ready(self):
        """
        Méthode appelée quand l'application est prête.
        Importe les signaux pour les enregistrer.
        """
        # Importer les signaux pour les enregistrer avec Django
        from . import signals  # noqa: F401
