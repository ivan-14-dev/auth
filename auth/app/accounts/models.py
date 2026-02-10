"""
Modèles de données pour le module d'authentification.
Ce module définit le modèle utilisateur personnalisé avec tous les champs nécessaires.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour l'authentification.
    
    Hérite de AbstractUser pour ajouter des champs supplémentaires:
    - Rôle (admin, moderator, user)
    - Email de récupération
    - Numéro de téléphone
    - Adresse et pays
    - Avatar et biographie
    - Statut de vérification d'email
    - Statut de blocage
    """
    
    class Role(models.TextChoices):
        # Définition des rôles disponibles pour les utilisateurs
        ADMIN = 'admin', _('Admin')
        MODERATOR = 'moderator', _('Moderateur')
        USER = 'user', _('Utilisateur')
    
    class Meta:
        # Configuration du modèle pour Django Admin
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')
        # Tri par défaut: du plus récent au plus ancien
        ordering = ['-created_at']
    
    # ==================== Champs d'authentification ====================
    # Nom d'utilisateur unique (150 caractères max)
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text=_('Requis. 150 caractères ou moins. Lettres, chiffres et @/./+/-/_ uniquement.'),
        validators=[AbstractUser.username_validator]
    )
    
    # Email unique comme identifiant principal
    email = models.EmailField(
        unique=True,
        help_text=_('Requis. Une adresse email valide.')
    )
    
    # ==================== Champs de récupération ====================
    # Email de récupération optionnel
    email_recuperation = models.EmailField(
        blank=True,
        null=True,
        verbose_name=_('Email de récupération'),
        help_text=_('Adresse email de récupération optionnelle.')
    )
    
    # Numéro de téléphone avec code pays
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Numéro de téléphone'),
        help_text=_('Numéro de téléphone avec indicatif pays optionnel.')
    )
    
    # ==================== Champs du profil ====================
    # Adresse physique
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Adresse'),
        help_text=_('Adresse physique.')
    )
    
    # Pays de résidence
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Pays'),
        help_text=_('Pays de résidence.')
    )
    
    # Avatar/image de profil
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Avatar'),
        help_text=_('Photo de profil.')
    )
    
    # Biographie courte
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Biographie'),
        help_text=_('Courte biographie.')
    )
    
    # ==================== Contrôle d'accès par rôle ====================
    # Rôle de l'utilisateur pour le contrôle d'accès
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name=_('Rôle'),
        help_text=_('Rôle utilisateur pour le contrôle d\'accès.')
    )
    
    # ==================== Champs de statut ====================
    # Vérification de l'email
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email vérifié'),
        help_text=_('Indique si l\'utilisateur a vérifié son email.')
    )
    
    # Compte actif
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Actif'),
        help_text=_('Indique si ce compte doit être considéré comme actif.')
    )
    
    # Compte bloqué
    is_blocked = models.BooleanField(
        default=False,
        verbose_name=_('Bloqué'),
        help_text=_('Indique si ce compte est bloqué.')
    )
    
    # ==================== Champs de date/horodatage ====================
    # Dernière connexion
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Dernière connexion')
    )
    
    # Date de création (automatique)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Créé le')
    )
    
    # Date de mise à jour (automatique)
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Mis à jour le')
    )
    
    # ==================== Configuration Django ====================
    # Utiliser l'email comme champ d'identification
    USERNAME_FIELD = 'email'
    # Champs requis lors de la création (en plus de l'email et password)
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        """
        Représentation string de l'utilisateur.
        Retourne l'email.
        """
        return self.email
    
    @property
    def is_admin(self):
        """Vérifie si l'utilisateur est admin."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_moderator(self):
        """Vérifie si l'utilisateur est modérateur."""
        return self.role == self.Role.MODERATOR
    
    @property
    def is_staff(self):
        """Vérifie si l'utilisateur est staff (admin ou modérateur)."""
        return self.role in [self.Role.ADMIN, self.Role.MODERATOR]
