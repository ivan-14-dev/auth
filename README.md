# Module d'Authentification Django

Un module d'authentification complet et réutilisable pour les projets Django avec support JWT, contrôle d'accès par rôles et fonctionnalités de sécurité avancées.

## 🚀 Fonctionnalités

### Fonctionnalités d'Authentification
- **Inscription Utilisateur** - Créer de nouveaux comptes avec validation email
- **Connexion Utilisateur** - Authentification avec email et mot de passe
- **Authentification JWT** - Authentification sécurisée par tokens
- **Rafraîchissement de Token** - Renouveler les tokens sans nouvelle connexion
- **Déconnexion** - Invalider les tokens pour une déconnexion sécurisée
- **Changement de Mot de Passe** - Changer avec vérification du mot de passe actuel
- **Réinitialisation de Mot de Passe** - Demander via email
- **Vérification d'Email** - Vérifier les adresses email des utilisateurs

### Gestion des Utilisateurs
- **Modèle Utilisateur Personnalisé** - Champs étendus (profil, contact)
- **Contrôle d'Accès par Rôles** - Admin, Modérateur, Utilisateur
- **Profils Utilisateurs** - Modifier les informations de profil
- **Liste des Utilisateurs** - Admin uniquement
- **Gestion des Statuts** - Activer, désactiver, bloquer les utilisateurs

### Fonctionnalités de Sécurité
- **Validation de Mot de Passe** - Exigences de mot de passe fort
- **Limitation de Débit** - Prévenir les attaques par force brute
- **Configuration CORS** - Requêtes cross-origin sécurisées
- **Liste Noire de Tokens** - Invalider les tokens à la déconnexion
- **Gestion de Sessions** - Suivre les connexions, sessions actives

## 📦 Prérequis

- Python 3.8+
- Django 4.0+
- Django REST Framework
- Django REST Framework SimpleJWT
- PostgreSQL (recommandé) ou SQLite

## 🛠️ Installation

1. **Copier ou cloner le module** dans votre projet Django :
   ```bash
   cp -r auth/ votre_projet/
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer les variables d'environnement** dans `.env` :
   ```env
   SECRET_KEY=votre-cle-secrete
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Base de données
   DB_NAME=votre_db
   DB_USER=votre_utilisateur
   DB_PASSWORD=votre_mot_de_passe
   DB_HOST=localhost
   DB_PORT=5432
   
   # Email
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=votre_email@gmail.com
   EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
   ```

4. **Exécuter les migrations** :
   ```bash
   cd auth
   python manage.py makemigrations accounts
   python manage.py migrate
   ```

5. **Créer un superutilisateur** (accès admin) :
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancer le serveur de développement** :
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuration

### Modèle Utilisateur Personnalisé
Le module utilise un modèle utilisateur avec email comme identifiant :
```python
AUTH_USER_MODEL = 'accounts.User'
```

### Paramètres JWT
Configurez JWT dans `settings.py` :
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Paramètres CORS
Autoriser les requêtes cross-origin :
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

## 📡 Points de Terminaison API

### Authentification
| Point de terminaison | Méthode | Description | Auth Requis |
|---------------------|---------|-------------|-------------|
| `/api/v1/auth/register/` | POST | Inscription | Non |
| `/api/v1/auth/login/` | POST | Connexion | Non |
| `/api/v1/auth/logout/` | POST | Déconnexion | Oui |
| `/api/v1/auth/token/refresh/` | POST | Rafraîchir token | Non |

### Gestion du Mot de Passe
| Point de terminaison | Méthode | Description | Auth Requis |
|---------------------|---------|-------------|-------------|
| `/api/v1/auth/password/change/` | POST | Changer mot de passe | Oui |
| `/api/v1/auth/password/reset/` | POST | Demander reset | Non |
| `/api/v1/auth/password/reset/confirm/` | POST | Confirmer reset | Non |

### Vérification Email
| Point de terminaison | Méthode | Description | Auth Requis |
|---------------------|---------|-------------|-------------|
| `/api/v1/auth/email/verify/` | POST | Demander vérification | Non |

### Profil
| Point de terminaison | Méthode | Description | Auth Requis |
|---------------------|---------|-------------|-------------|
| `/api/v1/profile/` | GET | Obtenir profil | Oui |
| `/api/v1/profile/update/` | PUT | Mettre à jour profil | Oui |

### Administration
| Point de terminaison | Méthode | Description | Auth Requis |
|---------------------|---------|-------------|-------------|
| `/api/v1/admin/users/` | GET | Lister utilisateurs | Admin |
| `/api/v1/admin/users/<id>/` | GET | Détails utilisateur | Admin |
| `/api/v1/admin/users/<id>/update/` | PUT | Modifier utilisateur | Admin |

### Système
| Point de terminaison | Méthode | Description | Auth Requis |
|---------------------|---------|-------------|-------------|
| `/api/v1/health/` | GET | Vérification santé | Non |
| `/api/docs/` | GET | Docs API Swagger | Non |

## 📝 Exemples de Requêtes/Réponses

### Inscription
```json
POST /api/v1/auth/register/
{
    "username": "jean",
    "email": "jean@example.com",
    "password": "MotDePasse123!",
    "password_confirm": "MotDePasse123!",
    "phone_number": "+33123456789",
    "country": "France"
}

Réponse (201):
{
    "id": 1,
    "username": "jean",
    "email": "jean@example.com",
    "role": "user",
    "is_email_verified": false,
    ...
}
```

### Connexion
```json
POST /api/v1/auth/login/
{
    "email": "jean@example.com",
    "password": "MotDePasse123!"
}

Réponse (200):
{
    "user": {
        "id": 1,
        "email": "jean@example.com",
        "username": "jean",
        "role": "user"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

### Utiliser le Token
Inclure le token d'accès dans l'en-tête Authorization :
```
Authorization: Bearer <access_token>
```

## 🔐 Rôles Utilisateur

| Rôle | Description | Permissions |
|------|-------------|-------------|
| `admin` | Administrateur | Accès complet |
| `moderator` | Modérateur | Gérer utilisateurs, voir rapports |
| `user` | Utilisateur | Accéder à son profil, utiliser l'app |

## 🏗️ Architecture

### Structure du Projet
```
auth/
├── auth/                    # Paramètres Django
│   ├── settings.py         # Configuration complète
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Application WSGI
├── app/
│   └── accounts/          # Module d'authentification
│       ├── models.py      # Modèle User personnalisé
│       ├── serializers.py # Sérialiseurs DRF
│       ├── views.py      # Vues API
│       ├── urls.py       # URLs API
│       ├── permissions.py # Permissions personnalisées
│       └── admin.py      # Configuration admin
├── templates/accounts/email/ # Templates email HTML
├── requirements.txt      # Dépendances
└── README.md            # Cette documentation
```

### Flux de Données
1. Utilisateur s'inscrit → Compte créé (inactif)
2. Utilisateur se connecte → Tokens JWT émis
3. Utilisateur accède aux endpoints protégés → Token validé
4. Utilisateur se déconnecte → Refresh token en liste noire
5. Admin gère les utilisateurs → Contrôle d'accès par rôle

## 🔄 Intégration dans un Projet Existant

### 1. Ajouter aux Applications Installées
```python
INSTALLED_APPS = [
    # ... autres apps
    'app.accounts',
]
```

### 2. Configurer AUTH_USER_MODEL
```python
AUTH_USER_MODEL = 'accounts.User'
```

### 3. Inclure les URLs
```python
urlpatterns = [
    # ... autres patterns
    path('api/v1/', include('app.accounts.urls')),
]
```

### 4. Exécuter les Migrations
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

## 🧪 Tests

### Exécuter les tests :
```bash
python manage.py test accounts
```

### Créer un utilisateur de test :
```bash
python manage.py shell -c "
from accounts.models import User
User.objects.create_superuser(
    email='admin@example.com',
    password='AdminMotDePasse123!'
)
"
```

## 🚀 Déploiement

### Liste de Vérification Production
1. Définir `DEBUG=False`
2. Utiliser la base de données PostgreSQL
3. Configurer SSL/TLS
4. Définir une `SECRET_KEY` forte
5. Configurer les paramètres d'email
6. Configurer la limitation de débit
7. Configurer CORS pour les domaines de production
8. Mettre en place la journalisation
9. Utiliser des variables d'environnement

### Exemple Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "auth.wsgi:application"]
```

## 📚 Documentation API

La documentation API interactive est disponible sur :
- **Swagger UI** : `/api/docs/`
- **ReDoc** : `/api/redoc/`

## 🤝 Contribution

1. Forker le dépôt
2. Créer une branche de fonctionnalité (`git checkout -b feature/ma-fonctionnalite`)
3. Valider les modifications (`git commit -m 'Ajouter ma-fonctionnalite'`)
4. Pousser vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 🆘 Support

Pour les problèmes et questions :
- Ouvrir un ticket GitHub
- Email : support@example.com

---

Construit avec ❤️ utilisant Django et Django REST Framework
