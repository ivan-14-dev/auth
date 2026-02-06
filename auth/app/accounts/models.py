from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model extending AbstractUser."""
    username = models.CharField(max_length=150, unique=True , required=True)        # Ensure username is unique
    email = models.EmailField(unique=True,required=True)                            # Ensure email is unique for each user
    email_recuperation = models.EmailField(blank=True, null=True)                   # Optional recovery email field
    phone_number = models.CharField(max_length=15, blank=True, null=True)           # Optional phone number field
    address = models.TextField(blank=True, null=True)                               # Optional address field    
    country = models.CharField(max_length=50, blank=True, null=True,verbose_name="Country of Residence") # Optional country field with verbose name
    created_at = models.DateTimeField(auto_now_add=True)                            # Timestamp for when the user was created
    updated_at = models.DateTimeField(auto_now=True)                                # Timestamp for when the user

    def __str__(self):
        return self.username  # Return the username as the string representation of the user
    
    class Meta:               # Meta information for the User model : permet de customiser le comportement du modele
        verbose_name = 'User'                           # Singular name for the model
        verbose_name_plural = 'Users'                   # Plural name for the model
        ordering = ['username', '-updated_at']  # Default ordering by username and updated_at in descending order