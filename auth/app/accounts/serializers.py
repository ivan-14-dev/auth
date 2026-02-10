"""
Sérialiseurs pour le module d'authentification.
Sérialiseurs complets pour l'authentification et la gestion du profil utilisateur.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Récupérer le modèle utilisateur personnalisé
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'inscription des utilisateurs.
    Valide la force du mot de passe et crée de nouveaux utilisateurs.
    """
    
    # Champ mot de passe (écriture seule, minimum 8 caractères)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text=_('Le mot de passe doit contenir au moins 8 caractères.')
    )
    
    # Champ confirmation du mot de passe
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_('Confirmez votre mot de passe.')
    )
    
    class Meta:
        # Utiliser le modèle User personnalisé
        model = User
        # Champs inclus dans le sérialiseur
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'email_recuperation', 'phone_number', 'address', 'country', 'role'
        ]
        # Champs optionnels
        extra_kwargs = {
            'email_recuperation': {'required': False},
            'phone_number': {'required': False},
            'address': {'required': False},
            'country': {'required': False},
            'role': {'required': False},
        }
    
    def validate(self, attrs):
        """
        Validation des données avant création.
        Vérifie que les mots de passe correspondent et sont valides.
        """
        # Vérifier que les mots de passe correspondent
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': _("Les mots de passe ne correspondent pas.")
            })
        
        # Valider la force du mot de passe
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Création de l'utilisateur.
        Le mot de passe est haché automatiquement.
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Sérialiseur pour la connexion des utilisateurs.
    Authentifie l'utilisateur avec email et mot de passe.
    """
    
    # Champ email requis
    email = serializers.EmailField(required=True)
    
    # Champ mot de passe (écriture seule)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Validation des identifiants.
        Vérifie que l'utilisateur existe et est actif.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Vérifier que les deux champs sont remplis
        if not email or not password:
            raise serializers.ValidationError({
                'detail': _('Les deux champs email et mot de passe sont requis.')
            })
        
        # Authentifier l'utilisateur
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )
        
        # Vérifier si l'authentification a réussi
        if user is None:
            raise serializers.ValidationError({
                'detail': _('Email ou mot de passe invalide.')
            })
        
        # Vérifier si le compte est actif
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': _('Le compte utilisateur est désactivé.')
            })
        
        # Vérifier si le compte n'est pas bloqué
        if user.is_blocked:
            raise serializers.ValidationError({
                'detail': _('Le compte utilisateur est bloqué. Veuillez contacter le support.')
            })
        
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les détails de l'utilisateur.
    Utilisé pour afficher les informations de l'utilisateur.
    """
    
    class Meta:
        # Utiliser le modèle User
        model = User
        # Champs à sérialiser
        fields = [
            'id', 'username', 'email', 'email_recuperation',
            'phone_number', 'address', 'country', 'avatar', 'bio',
            'role', 'is_email_verified', 'is_active', 'is_blocked',
            'last_login', 'created_at', 'updated_at'
        ]
        # Champs en lecture seule (ne peuvent pas être modifiés)
        read_only_fields = [
            'id', 'email', 'is_email_verified', 'is_active', 'is_blocked',
            'last_login', 'created_at', 'updated_at'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la mise à jour du profil utilisateur.
    Permet aux utilisateurs de modifier leurs informations.
    """
    
    class Meta:
        model = User
        fields = [
            'username', 'email_recuperation', 'phone_number',
            'address', 'country', 'avatar', 'bio'
        ]
        extra_kwargs = {
            'username': {'required': False},
        }
    
    def validate_username(self, value):
        """Valide que le nom d'utilisateur est unique."""
        if value and User.objects.filter(username=value).exclude(
            id=self.instance.id
        ).exists():
            raise serializers.ValidationError(
                _('Un utilisateur avec ce nom d\'utilisateur existe déjà.')
            )
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Sérialiseur pour le changement de mot de passe.
    Requiert le mot de passe actuel pour la sécurité.
    """
    
    # Ancien mot de passe
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_('Votre mot de passe actuel.')
    )
    
    # Nouveau mot de passe
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text=_('Nouveau mot de passe (minimum 8 caractères).')
    )
    
    # Confirmation du nouveau mot de passe
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_('Confirmez le nouveau mot de passe.')
    )
    
    def validate_old_password(self, value):
        """Vérifie que l'ancien mot de passe est correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Le mot de passe actuel est incorrect.')
            )
        return value
    
    def validate(self, attrs):
        """Valide que les nouveaux mots de passe correspondent."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _("Les nouveaux mots de passe ne correspondent pas.")
            })
        
        # Valider la force du nouveau mot de passe
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs
    
    def save(self):
        """Met à jour le mot de passe de l'utilisateur."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Sérialiseur pour la demande de réinitialisation du mot de passe.
    Envoie un email avec le lien de réinitialisation.
    """
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Valide que l'email existe (sans révéler l'existence)."""
        if not User.objects.filter(email=value).exists():
            # Ne pas révéler si l'utilisateur existe
            return value
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Sérialiseur pour la confirmation de réinitialisation du mot de passe.
    Valide le token et définit le nouveau mot de passe.
    """
    
    token = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text=_('Nouveau mot de passe (minimum 8 caractères).')
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text=_('Confirmez le nouveau mot de passe.')
    )
    
    def validate(self, attrs):
        """Valide que les nouveaux mots de passe correspondent."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': _("Les mots de passe ne correspondent pas.")
            })
        
        # Valider la force du nouveau mot de passe
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs


class EmailVerificationRequestSerializer(serializers.Serializer):
    """
    Sérialiseur pour la demande de vérification d'email.
    Envoie un email de vérification.
    """
    
    email = serializers.EmailField(required=True)


class TokenRefreshSerializer(serializers.Serializer):
    """
    Sérialiseur pour le renouvellement du token.
    Échange le refresh token pour un nouveau access token.
    """
    
    refresh = serializers.CharField(required=True)


class LogoutSerializer(serializers.Serializer):
    """
    Sérialiseur pour la déconnexion.
    Met le refresh token en liste noire.
    """
    
    refresh = serializers.CharField(required=True)


class UserListSerializer(serializers.ModelSerializer):
    """
    Sérialiser pour la liste des utilisateurs (admin).
    Champs limités pour l'affichage en liste.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'is_active', 'is_blocked', 'created_at'
        ]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la mise à jour utilisateur par l'admin.
    Permet de modifier le rôle et le statut.
    """
    
    class Meta:
        model = User
        fields = ['role', 'is_active', 'is_blocked']
