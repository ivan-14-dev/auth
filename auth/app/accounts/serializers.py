from rest_framework import serializers
from  django.contrib.auth import get_user_model
from .models import SendEmailVerification, SendPasswordResetEmail, PasswordResetToken

User = get_user_model()                                 # Recuperer le model de user personnalisé

# 
class UserSerializer(serializers.ModelSerializer):
   
    class Meta: 
        model  = User
        fields = ['id', 'username', 'email', 'email_recuperation', 'phone_number', 'address', 'country', 'role', 'created_at', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True) # Champ de mot de passe en écriture seule pour éviter de le renvoyer dans les réponses

    class Meta :
        model = User
        fields = ['username', 'email', 'password', 'email_recuperation', 'phone_number', 'address', 'country', 'role']
    
    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)        # Champ de courriel requis pour la connexion
    password = serializers.CharField(write_only=True)    # Champ de mot de passe en écriture seule pour éviter de le renvoyer dans les réponses

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)    # Récupérer l'utilisateur par son adresse e-mail
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")  # Lever une erreur si l'utilisateur n'existe pas

            if not user.check_password(password):       # Vérifier le mot de passe
                raise serializers.ValidationError("Invalid email or password.")  # Lever une erreur si le mot de passe est incorrect
        else:
            raise serializers.ValidationError("Both email and password are required.")  # Lever une erreur


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email_recuperation', 'phone_number', 'address', 'country', 'role', 'image']
        read_only_fields = ['email']  # Rendre le champ email en lecture seule pour éviter de le modifier lors de la mise à jour du profil

class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)  # Champ de mot de passe en écriture seule pour éviter de le renvoyer dans les réponses
    password_confirmation = serializers.CharField(write_only=True)  # Champ de confirmation de mot de passe en écriture seule

    def validate_password(self, value):
        user = self.context['request'].user  # Récupérer l'utilisateur à partir du contexte de la requête
        if not user.check_password(value):     # Vérifier le mot de passe
            raise serializers.ValidationError("Incorrect password.")  # Lever une erreur si le mot de passe est incorrect
        return value
    

class SendPasswordResetEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendPasswordResetEmail
        fields = ['email']

class PasswordResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetToken
        fields = ['user', 'token']

class SendEmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendEmailVerification
        fields = ['email']