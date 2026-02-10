"""
Fonctions utilitaires pour le module d'authentification.
Fonctions d'aide pour les tâches courantes d'authentification.
"""

import secrets
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

import logging

# Logger pour la journalisation
logger = logging.getLogger(__name__)


def generate_random_password(length=12):
    """
    Génère un mot de passe aléatoire sécurisé.
    
    Args:
        length: Longueur du mot de passe (défaut: 12)
    
    Returns:
        str: Mot de passe aléatoire
    """
    # Caractères autorisés: lettres majuscules, minuscules, chiffres, symboles
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        # Générer un mot de passe aléatoire
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Vérifier qu'il contient au moins une minuscule, une majuscule et un chiffre
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password)):
            return password


def generate_verification_token():
    """
    Génère un jeton de vérification d'email sécurisé.
    
    Returns:
        str: Jeton URL-safe aléatoire
    """
    return secrets.token_urlsafe(32)


def generate_password_reset_token():
    """
    Génère un jeton de réinitialisation de mot de passe sécurisé.
    
    Returns:
        str: Jeton URL-safe aléatoire
    """
    return secrets.token_urlsafe(32)


def send_welcome_email(user):
    """
    Envoie un email de bienvenida à un nouvel utilisateur.
    
    Args:
        user: Instance de l'utilisateur
    """
    try:
        subject = _('Bienvenue sur notre plateforme !')
        context = {
            'user': user,
            'login_url': settings.FRONTEND_URL + '/login'
        }
        # Rendre le template HTML
        html_message = render_to_string('accounts/email/welcome.html', context)
        # Version texte brut du message
        plain_message = strip_tags(html_message)
        
        # Envoyer l'email
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True
        )
        logger.info(f"Email de bienvenue envoyé à {user.email}")
    except Exception as e:
        logger.error(f"Échec de l'envoi de l'email de bienvenue à {user.email}: {e}")


def send_password_reset_email(user, reset_url):
    """
    Envoie un email de réinitialisation de mot de passe.
    
    Args:
        user: Instance de l'utilisateur
        reset_url: URL de réinitialisation du mot de passe
    """
    try:
        subject = _('Demande de réinitialisation de mot de passe')
        context = {
            'user': user,
            'reset_url': reset_url
        }
        html_message = render_to_string('accounts/email/password_reset.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True
        )
        logger.info(f"Email de réinitialisation envoyé à {user.email}")
    except Exception as e:
        logger.error(f"Échec de l'envoi de l'email de réinitialisation à {user.email}: {e}")


def send_verification_email(user, verify_url):
    """
    Envoie un email de vérification d'adresse email.
    
    Args:
        user: Instance de l'utilisateur
        verify_url: URL de vérification de l'email
    """
    try:
        subject = _('Vérifiez votre adresse email')
        context = {
            'user': user,
            'verify_url': verify_url
        }
        html_message = render_to_string('accounts/email/email_verification.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True
        )
        logger.info(f"Email de vérification envoyé à {user.email}")
    except Exception as e:
        logger.error(f"Échec de l'envoi de l'email de vérification à {user.email}: {e}")


def invalidate_user_tokens(user):
    """
    Invalide tous les tokens d'un utilisateur (déconnexion universelle).
    
    Args:
        user: Instance de l'utilisateur
    
    Returns:
        int: Nombre de tokens mis en liste noire
    """
    try:
        # Récupérer tous les refresh tokens de l'utilisateur
        refresh_tokens = RefreshToken.objects.filter(user=user)
        count = refresh_tokens.count()
        # Mettre chaque token en liste noire
        for token in refresh_tokens:
            token.blacklist()
        logger.info(f"Invalidation de {count} tokens pour l'utilisateur {user.email}")
        return count
    except Exception as e:
        logger.error(f"Échec de l'invalidation des tokens pour {user.email}: {e}")
        return 0


def get_client_ip(request):
    """
    Récupère l'adresse IP du client à partir de la requête.
    
    Args:
        request: Objet de requête HTTP
    
    Returns:
        str: Adresse IP du client
    """
    # Vérifier si la requête passe par un proxy
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Prendre la première IP (celle du client)
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def log_user_action(user, action, request, details=''):
    """
    Journalise une action utilisateur pour l'audit.
    
    Args:
        user: Instance de l'utilisateur
        action: Action effectuée
        request: Objet de requête HTTP
        details: Détails supplémentaires
    """
    logger.info(
        f"Action utilisateur: {user.email} | Action: {action} | "
        f"IP: {get_client_ip(request)} | Détails: {details}"
    )


class RateLimiter:
    """
    Limiteur de débit simple pour prévenir les attaques par force brute.
    """
    
    def __init__(self, max_requests=5, time_window=60):
        """
        Initialise le limiteur de débit.
        
        Args:
            max_requests: Nombre maximal de requêtes autorisées
            time_window: Fenêtre de temps en secondes
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_rate_limited(self, key):
        """
        Vérifie si la clé est limitée en débit.
        
        Args:
            key: Identifiant unique (ex: IP, ID utilisateur)
        
        Returns:
            bool: True si limité, False sinon
        """
        now = timezone.now()
        window_start = now - timezone.timedelta(seconds=self.time_window)
        
        # Initialiser la liste des requêtes pour cette clé
        if key not in self.requests:
            self.requests[key] = []
        
        # Supprimer les requêtes anciennes hors de la fenêtre
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Vérifier si la limite est dépassée
        if len(self.requests[key]) >= self.max_requests:
            return True
        
        # Ajouter la requête actuelle
        self.requests[key].append(now)
        return False
    
    def get_remaining_requests(self, key):
        """
        Récupère le nombre de requêtes restantes pour la clé.
        
        Args:
            key: Identifiant unique
        
        Returns:
            int: Nombre de requêtes restantes
        """
        now = timezone.now()
        window_start = now - timezone.timedelta(seconds=self.time_window)
        
        if key not in self.requests:
            return self.max_requests
        
        recent_requests = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(recent_requests))
