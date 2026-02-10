"""
Signaux Django pour le module d'authentification.
Gère les événements liés aux utilisateurs et les actions automatiques.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

import logging

# Logger pour la journalisation
logger = logging.getLogger(__name__)

# Récupérer le modèle utilisateur personnalisé
User = get_user_model()


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """
    Signal émis avant qu'un utilisateur soit sauvegardé.
    Utilisé pour la journalisation et les validations.
    
    Args:
        sender: Le modèle qui envoie le signal (User)
        instance: L'instance de l'utilisateur
        **kwargs: Arguments supplémentaires
    """
    # Vérifier si l'utilisateur existe déjà (modification)
    if instance.pk:
        try:
            # Récupérer l'ancienne instance
            old_instance = User.objects.get(pk=instance.pk)
            # Stocker les valeurs originales pour comparaison
            instance._original_role = old_instance.role
            instance._original_is_active = old_instance.is_active
            instance._original_is_blocked = old_instance.is_blocked
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal émis après qu'un utilisateur soit sauvegardé.
    Utilisé pour la journalisation et les notifications.
    
    Args:
        sender: Le modèle qui envoie le signal (User)
        instance: L'instance de l'utilisateur sauvegardé
        created: True si l'utilisateur vient d'être créé
        **kwargs: Arguments supplémentaires
    """
    if created:
        # Nouvel utilisateur créé
        logger.info(f"Nouvel utilisateur créé: {instance.email} (Rôle: {instance.role})")
        # Ajouter ici la logique post-création
        # Ex: envoyer email de Bienvenue, créer profil, etc.
    else:
        # Utilisateur modifié - journaliser les changements
        
        # Changement de rôle
        if hasattr(instance, '_original_role') and instance._original_role != instance.role:
            logger.info(
                f"Rôle utilisateur modifié: {instance.email} "
                f"({instance._original_role} -> {instance.role})"
            )
        
        # Changement de statut actif
        if hasattr(instance, '_original_is_active') and instance._original_is_active != instance.is_active:
            status = "activé" if instance.is_active else "désactivé"
            logger.info(f"Utilisateur {status}: {instance.email}")
        
        # Changement de statut bloqué
        if hasattr(instance, '_original_is_blocked') and instance._original_is_blocked != instance.is_blocked:
            status = "bloqué" if instance.is_blocked else "débloqué"
            logger.info(f"Utilisateur {status}: {instance.email}")


@receiver(pre_save, sender=User)
def update_last_login(sender, instance, **kwargs):
    """
    Signal émis avant la sauvegarde pour mettre à jour la dernière connexion.
    Note: Ceci est géré par le paramètre UPDATE_LAST_LOGIN de SIMPLE_JWT.
    
    Args:
        sender: Le modèle qui envoie le signal (User)
        instance: L'instance de l'utilisateur
        **kwargs: Arguments supplémentaires
    """
    pass
