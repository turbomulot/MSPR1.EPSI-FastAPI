# Documentation Pytest

## Objectif
Ce document centralise toute la documentation de test du backend FastAPI.

## Prerequis
Installez les dependances de dev:

```bash
pip install -e ".[dev]"
```

Alternative minimale:

```bash
pip install pytest pytest-cov httpx pytest-asyncio
```

## Commandes utiles

### Lancer toute la suite
```bash
pytest src/test/ -v
```

### Lancer avec couverture
```bash
pytest src/test/ -v --cov=src --cov-report=term-missing --cov-report=html
```

Resultats:
- Rapport terminal avec lignes manquantes
- Rapport HTML dans `htmlcov/index.html`

### Lancer un fichier
```bash
pytest src/test/test_user.py -v
pytest src/test/test_product.py -v
pytest src/test/test_analytics.py -v
```

### Lancer un test unique
```bash
pytest src/test/test_user.py::TestUserCreate::test_create_user_success -v
```

### Sortie concise
```bash
pytest src/test/ -q
```

## Organisation des tests

```text
src/test/
├── __init__.py
├── conftest.py
├── test_app.py
├── test_user.py
├── test_product.py
└── test_analytics.py
```

## Couverture fonctionnelle actuelle

### test_app.py
- Demarrage de l'application
- Prefixe d'API (`/api/v0`)
- Routes invalides

### test_user.py
- Creation d'utilisateur
- Connexion JWT
- Autorisations (admin vs non-admin)
- Consultation profil courant et profil par id

### test_product.py
- CRUD produits
- Verifications d'authentification
- Pagination (`skip`, `limit`)

### test_analytics.py
- Endpoint analytics protege par JWT
- Isolation des donnees par utilisateur
- Cas sans donnees

## Fixtures principales (conftest.py)
- `db`: base SQLite de test
- `client`: client HTTP FastAPI
- `test_user`: utilisateur standard
- `admin_user`: utilisateur administrateur
- `user_token` / `admin_token`: JWT de test
- `test_product`: produit de test

## Bonnes pratiques
- Garder les tests deterministes
- Isoler les donnees entre tests
- Verifier les codes HTTP et la structure JSON
- Tester les cas d'erreur (401, 403, 404, 422)
