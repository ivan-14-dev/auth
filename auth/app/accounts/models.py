from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    username = models.CharField(max_length=150, unique=True , required=True)        # Ensure username is unique
    email = models.EmailField(unique=True,required=True)                            # Ensure email is unique for each user
    email_recuperation = models.EmailField(blank=True, null=True)                   # Optional recovery email field
    phone_number = models.CharField(max_length=15, blank=True, null=True)           # Optional phone number field
    address = models.TextField(blank=True, null=True)                               # Optional address field    
    country = models.CharField(max_length=50, blank=True, null=True,verbose_name="Country of Residence") # Optional country field with verbose name
    created_at = models.DateTimeField(auto_now_add=True)                            # Timestamp for when the user was created
    updated_at = models.DateTimeField(auto_now=True)                                # Timestamp for when the user
    role = models.CharField(max_length = 20, choices = ROLE_CHOICES, default='user')  # Role field with choices and default value
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)     # Optional profile image field

    def __str__(self):
        return self.email  # Return the email as the string representation of the user
    
    class Meta:               # Meta information for the User model : permet de customiser le comportement du modele
        verbose_name = 'User'                           # Singular name for the model
        verbose_name_plural = 'Users'                   # Plural name for the model
        ordering = ['username', '-updated_at']          # Default ordering by username and updated_at in descending order


class SendPasswordResetEmail(models.Model):
    email = models.EmailField(unique=True)  # Ensure email is unique for password reset requests
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the password reset request was created

    def __str__(self):
        return self.email  # Return the email as the string representation of the password reset request
    
    class Meta:
        verbose_name = 'Send Password Reset Email'  # Singular name for the model
        verbose_name_plural = 'Send Password Reset Emails'  # Plural name for the model
        ordering = ['-created_at']  # Default ordering by created_at in descending order

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link the token to a specific user
    token = models.CharField(max_length=255, unique=True)  # Unique token for password reset
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the token was created

    def __str__(self):
        return f"Password reset token for {self.user.email}"  # String representation of the password reset token
    
    class Meta:
        verbose_name = 'Password Reset Token'  # Singular name for the model
        verbose_name_plural = 'Password Reset Tokens'  # Plural name for the model
        ordering = ['-created_at']  # Default ordering by created_at in descending order

class SendEmailVerification(models.Model):
    email = models.EmailField(unique=True)  # Ensure email is unique for email verification requests
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the email verification request was created

    def __str__(self):
        return self.email  # Return the email as the string representation of the email verification request
    
    class Meta:
        verbose_name = 'Send Email Verification'  # Singular name for the model
        verbose_name_plural = 'Send Email Verifications'  # Plural name for the model
        ordering = ['-created_at']  # Default ordering by created_at in descending order