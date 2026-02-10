"""
Paramètres Django pour le projet d'authentification.
Configuration complète du module d'authentification.
"""

# Importer les modules nécessaires
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Construire les chemins du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Répertoire des templates
TEMPLATES_DIR = BASE_DIR / 'templates'

# ==================== Paramètres de sécurité ====================
# Clé secrète pour le chiffrement (charger depuis les variables d'environnement)
SECRET_KEY = os.getenv('SECRET_KEY', 'votre-cle-secrete-ici')
# Mode débogage (True en développement, False en production)
DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
# Hôtes autorisés (séparés par des virgules)
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# ==================== Applications installées ====================
INSTALLED_APPS = [
    # Applications intégrées à Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Applications tierces
    'rest_framework',                           # Framework REST pour Django
    'rest_framework_simplejwt',                 # Authentification JWT
    'rest_framework_simplejwt.token_blacklist',  # Liste noire des tokens
    'corsheaders',                              # Gestion CORS
    'drf_yasg',                                 # Documentation API Swagger
    'django_filters',                           # Filtrage des requêtes
    
    # Applications locales
    'app.accounts',                              # Module d'authentification
]

# ==================== Middleware ====================
# Logiciel intermédiaire pour le traitement des requêtes
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==================== Configuration des URLs ====================
# Point d'entrée des URLs
ROOT_URLCONF = 'auth.urls'

# ==================== Configuration des templates ====================
TEMPLATES = [
    {
        # Moteur de templates
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Répertoires de templates
        'DIRS': [TEMPLATES_DIR],
        # Chercher les templates dans les applications
        'APP_DIRS': True,
        # Options de configuration
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==================== Application WSGI ====================
WSGI_APPLICATION = 'auth.wsgi.application'

# ==================== Base de données ====================
# Configuration flexible - utilise SQLite par défaut, PostgreSQL en production
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')

if 'postgresql' in DB_ENGINE:
    # Configuration PostgreSQL (pour la production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'auth_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    # Configuration SQLite (pour le développement)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
        }
    }

# Alternative: SQLite pour le développement
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# ==================== Modèle utilisateur personnalisé ====================
# Utiliser notre modèle User personnalisé au lieu de celui par défaut de Django
AUTH_USER_MODEL = 'accounts.User'

# ==================== Validateurs de mot de passe ====================
AUTH_PASSWORD_VALIDATORS = [
    # Vérifier la similarité avec les attributs de l'utilisateur
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # Longueur minimale du mot de passe
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    # Vérifier les mots de passe courants
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # Vérifier que le mot de passe n'est pas entièrement numérique
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==================== Internationalisation ====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==================== Fichiers statiques et médias ====================
STATIC_URL = 'static/'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==================== Type de clé primaire par défaut ====================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== Configuration Django REST Framework ====================
REST_FRAMEWORK = {
    # Classes d'authentification par défaut
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    
    # Classes de permissions par défaut
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Classes de rendu par défaut
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    
    # Classes d'analyse par défaut
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    
    # Classes de filtrage par défaut
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Classe de pagination par défaut
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # Nombre d'éléments par page
    'PAGE_SIZE': 20,
    
    # Gestionnaire d'exceptions personnalisé
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    
    # Classes de limitation de débit
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    
    # Taux de limitation de débit
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',    # 100 requêtes par heure pour les anonymes
        'user': '1000/hour',   # 1000 requêtes par heure pour les utilisateurs
    },
    
    # Clé pour les erreurs non liées aux champs
    'NON_FIELD_ERRORS_KEY': 'detail',
}

# ==================== Configuration JWT ====================
SIMPLE_JWT = {
    # Durée de vie du token d'accès (60 minutes)
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    
    # Durée de vie du token de rafraîchissement (7 jours)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    
    # Rotation des tokens de rafraîchissement
    'ROTATE_REFRESH_TOKENS': True,
    
    # Mettre les anciens tokens en liste noire après rotation
    'BLACKLIST_AFTER_ROTATION': True,
    
    # Mettre à jour la date de dernière connexion
    'UPDATE_LAST_LOGIN': True,
    
    # Algorithme de signature
    'ALGORITHM': 'HS256',
    
    # Clé de signature (doit être sécurisée en production)
    'SIGNING_KEY': SECRET_KEY,
    
    # Clé de vérification (None utilise SIGNING_KEY)
    'VERIFYING_KEY': None,
    
    # Audience du token
    'AUDIENCE': None,
    
    # Émetteur du token
    'ISSUER': None,
    
    # Type d'en-tête d'authentification
    'AUTH_HEADER_TYPES': ('Bearer',),
    
    # Nom de l'en-tête d'authentification
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    
    # Champ utilisateur dans le token
    'USER_ID_FIELD': 'id',
    
    # Claim utilisateur dans le token
    'USER_ID_CLAIM': 'user_id',
    
    # Classes de tokens autorisées
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    
    # Claim du type de token
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    # Claim du JTI (jeton d'identification unique)
    'JTI_CLAIM': 'jti',
    
    # Configuration des tokens glissants (optionnel)
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ==================== Configuration de l'email ====================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@votredomaine.com')

# URL du frontend pour les liens dans les emails
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# ==================== Configuration CORS ====================
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [origin for origin in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]
CORS_ALLOW_CREDENTIALS = True

# ==================== Limitation de débit ====================
RATE_LIMIT_ENABLED = not DEBUG
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 3600))

# ==================== Paramètres de sécurité pour la production ====================
if not DEBUG:
    # Rediriger vers HTTPS
    SECURE_SSL_REDIRECT = True
    # Cookies sécurisés
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Protection XSS
    SECURE_BROWSER_XSS_FILTER = True
    # Empêcher le clickjacking
    X_FRAME_OPTIONS = 'DENY'
    # HTTP Strict Transport Security (1 an)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ==================== Configuration de la journalisation (logging) ====================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        # Format détaillé pour le débogage
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        # Format simple pour la production
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        # Afficher les logs dans la console
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    # Configuration du logger racine
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    # Configuration des loggers spécifiques
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
