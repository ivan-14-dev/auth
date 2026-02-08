from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UpdateProfileSerializer, DeleteAccountSerializer
from .permissions import IsAdmin, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()                                 # Recuperer le model de user personnalisé

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]  # Seuls les utilisateurs authentifiés et ayant le rôle d'administrateur peuvent accéder à cette vue
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    

class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Seuls les utilisateurs authentifiés peuvent accéder à cette vue
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = []  # Permet à tous les utilisateurs d'accéder à cette vue, même ceux qui ne sont pas authentifiés
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)  # Authentifier l'utilisateur en utilisant l'adresse e-mail et le mot de passe
            if user is not None:
                refresh = RefreshToken.for_user(user) # Générer un token de rafraîchissement pour l'utilisateur authentifié
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]  # Seuls les utilisateurs authentifiés peuvent accéder à cette vue
    def put(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)  # Permet une mise à jour partielle du profil de l'utilisateur
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]  # Seuls les utilisateurs authentifiés et ayant le rôle d'administrateur peuvent accéder à cette vue
    
    def delete(self, request):
        serializer = DeleteAccountSerializer(data=request.data, context={'request': request})  # Utiliser le contexte de la requête pour valider le mot de passe
        if request.user.is_authenticated and request.user.role == 'Admin':  # Vérifier si l'utilisateur est authentifié et a le rôle d'administrateur
             return Response({"detail": "Admin accounts cannot be deleted."}, status=status.HTTP_403_FORBIDDEN)  # Empêcher la suppression des comptes administrateurs
        
        if serializer.is_valid():
            user = request.user
            user.delete()  # Supprimer le compte de l'utilisateur
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)