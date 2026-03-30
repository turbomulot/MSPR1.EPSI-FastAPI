# Guide de demarrage rapide API

## 1) Demarrer l'application

Depuis la racine du projet:

```bash
alembic upgrade head
fastapi dev src/app.py
```

L'API est disponible avec le prefixe:
- `/api/v0`

## 2) Creer un utilisateur

Endpoint:
- `POST /api/v0/users/`

Exemple de payload:

```json
{
  "User_mail": "alice@example.com",
  "User_password": "Secret123!",
  "isAdmin": false
}
```

## 3) Se connecter pour obtenir un JWT

Endpoint:
- `POST /api/v0/users/login`

Exemple de payload:

```json
{
  "User_mail": "alice@example.com",
  "User_password": "Secret123!"
}
```

Reponse:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

## 4) Appeler un endpoint protege

Ajouter l'en-tete:

```text
Authorization: Bearer <jwt>
```

Exemple:
- `GET /api/v0/products/`

## 5) Consulter la documentation complete

- Documentation des endpoints (entree/sortie): `docs/endpoints.md`
- Documentation des tests Pytest (fichier unique): `docs/pytest.md`
