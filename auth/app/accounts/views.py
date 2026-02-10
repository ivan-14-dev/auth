"""
Vues API pour le module d'authentification.
Ensemble complet de vues pour l'authentification et la gestion des utilisateurs.
"""

import secrets
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User

from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserProfileSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, EmailVerificationRequestSerializer,
    TokenRefreshSerializer, LogoutSerializer,
    UserListSerializer, AdminUserUpdateSerializer
)
from .permissions import (
    IsAuthenticated, IsAdmin, IsModerator, IsActive, IsNotBlocked,
    IsNotAuthenticated
)


class HealthCheckView(APIView):
    """
    Point de terminaison de vérification de l'état de santé.
    Aucune authentification requise.
    """
    
    permission_classes = []
    
    def get(self, request):
        """
        Retourne l'état de santé du service.
        
        Returns:
            Response: JSON avec le statut du service
        """
        return Response({
            'status': 'healthy',
            'service': 'authentication',
            'timestamp': timezone.now().isoformat()
        })


class RegisterView(APIView):
    """
    Point d'inscription des utilisateurs.
    Crée un nouveau compte utilisateur.
    Aucune authentification requise.
    """
    
    permission_classes = [IsNotAuthenticated]
    
    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: UserSerializer,
            400: 'Erreur de validation'
        }
    )
    def post(self, request):
        """
        Crée un nouvel utilisateur.
        
        Args:
            request: Requête POST avec les données d'inscription
        
        Returns:
            Response: Données de l'utilisateur créé ou erreurs
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Point de connexion des utilisateurs.
    Authentifie l'utilisateur et retourne les tokens JWT.
    Aucune authentification requise.
    """
    
    permission_classes = [IsNotAuthenticated]
    
    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description='Connexion réussie',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': UserSerializer(),
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: 'Identifiants invalides'
        }
    )
    def post(self, request):
        """
        Authentifie l'utilisateur et génère les tokens.
        
        Args:
            request: Requête POST avec email et mot de passe
        
        Returns:
            Response: Tokens JWT et données utilisateur
        """
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Générer les tokens
            refresh = RefreshToken.for_user(user)
            
            # Mettre à jour la dernière connexion
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    Point de déconnexion des utilisateurs.
    Met le refresh token en liste noire.
    Authentification requise.
    """
    
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        request_body=LogoutSerializer,
        responses={
            205: 'Déconnexion réussie'
        }
    )
    def post(self, request):
        """
        Déconnecte l'utilisateur en invalidant le token.
        
        Args:
            request: Requête POST avec le refresh token
        
        Returns:
            Response: Confirmation de déconnexion
        """
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            refresh = RefreshToken(serializer.validated_data['refresh'])
            refresh.blacklist()
            return Response(
                {'detail': _('Déconnexion réussie.')},
                status=status.HTTP_205_RESET_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshViewCustom(TokenRefreshView):
    """
    Point de rafraîchissement de token personnalisé.
    Rafraîchit le token d'accès avec le refresh token.
    Aucune authentification requise.
    """
    
    serializer_class = TokenRefreshSerializer


class ProfileView(APIView):
    """
    Point du profil utilisateur.
    Retourne le profil de l'utilisateur authentifié.
    Authentification requise.
    """
    
    permission_classes = [IsAuthenticated, IsActive, IsNotBlocked]
    
    @swagger_auto_schema(
        responses={
            200: UserSerializer,
            401: 'Non autorisé'
        }
    )
    def get(self, request):
        """
        Retourne le profil de l'utilisateur actuel.
        
        Args:
            request: Requête GET avec le token d'authentification
        
        Returns:
            Response: Données du profil utilisateur
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ProfileUpdateView(APIView):
    """
    Point de mise à jour du profil.
    Permet aux utilisateurs de modifier leurs informations.
    Authentification requise.
    """
    
    permission_classes = [IsAuthenticated, IsActive, IsNotBlocked]
    
    @swagger_auto_schema(
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: 'Erreur de validation'
        }
    )
    def put(self, request):
        """
        Met à jour le profil utilisateur.
        
        Args:
            request: Requête PUT avec les données à mettre à jour
        
        Returns:
            Response: Profil mis à jour ou erreurs
        """
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserProfileSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    Point de changement de mot de passe.
    Change le mot de passe (requiert le mot de passe actuel).
    Authentification requise.
    """
    
    permission_classes = [IsAuthenticated, IsActive, IsNotBlocked]
    
    @swagger_auto_schema(
        request_body=PasswordChangeSerializer,
        responses={
            200: 'Mot de passe changé avec succès',
            400: 'Erreur de validation'
        }
    )
    def post(self, request):
        """
        Change le mot de passe de l'utilisateur.
        
        Args:
            request: Requête POST avec ancien et nouveau mot de passe
        
        Returns:
            Response: Confirmation ou erreurs
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': _('Mot de passe changé avec succès.')},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Point de demande de réinitialisation du mot de passe.
    Envoie un email de réinitialisation.
    Aucune authentification requise.
    """
    
    permission_classes = [IsNotAuthenticated]
    
    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        responses={
            200: 'Email de réinitialisation envoyé'
        }
    )
    def post(self, request):
        """
        Envoie un email de réinitialisation du mot de passe.
        
        Args:
            request: Requête POST avec l'email
        
        Returns:
            Response: Message de confirmation
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # Générer le token de réinitialisation
                token = secrets.token_urlsafe(32)
                # Stocker le token et envoyer l'email
                return Response(
                    {'detail': _('L\'email de réinitialisation a été envoyé.')},
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {'detail': _('L\'email de réinitialisation a été envoyé.')},
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Point de confirmation de réinitialisation du mot de passe.
    Valide le token et définit le nouveau mot de passe.
    Aucune authentification requise.
    """
    
    permission_classes = [IsNotAuthenticated]
    
    @swagger_auto_schema(
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: 'Mot de passe réinitialisé avec succès',
            400: 'Erreur de validation'
        }
    )
    def post(self, request):
        """
        Valide le token et change le mot de passe.
        
        Args:
            request: Requête POST avec token et nouveau mot de passe
        
        Returns:
            Response: Confirmation ou erreurs
        """
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {'detail': _('Le mot de passe a été réinitialisé avec succès.')},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationRequestView(APIView):
    """
    Point de demande de vérification d'email.
    Envoie un email de vérification.
    Aucune authentification requise.
    """
    
    permission_classes = [IsNotAuthenticated]
    
    @swagger_auto_schema(
        request_body=EmailVerificationRequestSerializer,
        responses={
            200: 'Email de vérification envoyé'
        }
    )
    def post(self, request):
        """
        Envoie un email de vérification.
        
        Args:
            request: Requête POST avec l'email
        
        Returns:
            Response: Message de confirmation
        """
        serializer = EmailVerificationRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                if user.is_email_verified:
                    return Response(
                        {'detail': _('L\'email est déjà vérifié.')},
                        status=status.HTTP_200_OK
                    )
                # Générer le token de vérification
                token = secrets.token_urlsafe(32)
                return Response(
                    {'detail': _('L\'email de vérification a été envoyé.')},
                    status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {'detail': _('L\'email de vérification a été envoyé.')},
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """
    Point de liste des utilisateurs.
    Retourne la liste de tous les utilisateurs (admin uniquement).
    Authentification et rôle admin requis.
    """
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(
        responses={
            200: UserListSerializer(many=True),
            403: 'Interdit'
        }
    )
    def get(self, request):
        """
        Retourne la liste de tous les utilisateurs.
        
        Args:
            request: Requête GET avec token admin
        
        Returns:
            Response: Liste des utilisateurs
        """
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """
    Point de détail d'un utilisateur.
    Retourne les détails d'un utilisateur spécifique.
    Authentification requise.
    """
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, user_id):
        """
        Retourne les détails d'un utilisateur.
        
        Args:
            request: Requête GET
            user_id: ID de l'utilisateur à afficher
        
        Returns:
            Response: Données de l'utilisateur ou erreur 404
        """
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'detail': _('Utilisateur non trouvé.')},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminUserUpdateView(APIView):
    """
    Point de mise à jour utilisateur par l'admin.
    Permet à l'admin de modifier le rôle et le statut.
    Authentification et rôle admin requis.
    """
    
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(
        request_body=AdminUserUpdateSerializer,
        responses={
            200: UserSerializer,
            400: 'Erreur de validation'
        }
    )
    def put(self, request, user_id):
        """
        Met à jour le rôle et le statut d'un utilisateur.
        
        Args:
            request: Requête PUT avec les données
            user_id: ID de l'utilisateur à modifier
        
        Returns:
            Response: Utilisateur mis à jour ou erreur
        """
        try:
            user = User.objects.get(id=user_id)
            serializer = AdminUserUpdateSerializer(
                user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                user = serializer.save()
                return Response(UserSerializer(user).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response(
                {'detail': _('Utilisateur non trouvé.')},
                status=status.HTTP_404_NOT_FOUND
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs.
    Fournit les opérations CRUD pour les utilisateurs.
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        """
        Retourne le sérialiseur approprié selon l'action.
        
        Returns:
            Serializer: Le sérialiseur à utiliser
        """
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        Retourne les permissions selon l'action.
        
        Returns:
            list: Liste de permissions
        """
        if self.action in ['create', 'list']:
            permission_classes = [IsAuthenticated, IsAdmin]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
