"""Tests for meal log endpoints."""

from datetime import date

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth import create_access_token, hash_password
from src.models.meal_log import MealLog
from src.models.product import Product
from src.models.user import User


class TestMealLogEndpoints:
    """Tests for meal log CRUD and data isolation."""

    def test_create_meal_log_success(
        self,
        client: TestClient,
        test_user: User,
        test_product: Product,
        user_token: str,
    ):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            "/api/v0/meal-logs/",
            json={
                "User_ID": 99999,
                "Product_ID": test_product.Product_ID,
                "Log_Date": "2026-03-30",
            },
            headers=headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        payload = response.json()
        assert payload["User_ID"] == test_user.User_ID
        assert payload["Product_ID"] == test_product.Product_ID

    def test_create_meal_log_unauthorized(self, client: TestClient, test_product: Product):
        response = client.post(
            "/api/v0/meal-logs/",
            json={
                "User_ID": 1,
                "Product_ID": test_product.Product_ID,
                "Log_Date": "2026-03-30",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_meal_logs_returns_only_current_user_data(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        other_user = User(
            User_mail="meal-other@example.com",
            User_password=hash_password("otherpassword123"),
            isAdmin=False,
        )
        product = Product(product_name="Rice")

        db.add_all([other_user, product])
        db.commit()
        db.refresh(product)

        own_log = MealLog(
            User_ID=test_user.User_ID,
            Product_ID=product.Product_ID,
            Log_Date=date(2026, 3, 20),
        )
        other_log = MealLog(
            User_ID=other_user.User_ID,
            Product_ID=product.Product_ID,
            Log_Date=date(2026, 3, 21),
        )

        db.add_all([own_log, other_log])
        db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/meal-logs/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        returned_ids = [item["Log_ID"] for item in response.json()]
        assert own_log.Log_ID in returned_ids
        assert other_log.Log_ID not in returned_ids

    def test_get_meal_log_not_found_for_other_user(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        test_product: Product,
        user_token: str,
    ):
        other_user = User(
            User_mail="meal-owner@example.com",
            User_password=hash_password("ownerpassword123"),
            isAdmin=False,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        other_log = MealLog(
            User_ID=other_user.User_ID,
            Product_ID=test_product.Product_ID,
            Log_Date=date(2026, 3, 10),
        )
        db.add(other_log)
        db.commit()
        db.refresh(other_log)

        token = create_access_token(data={"sub": str(test_user.User_ID)})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/api/v0/meal-logs/{other_log.Log_ID}", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Meal log not found" in response.json()["detail"]

    def test_update_and_delete_meal_log(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        test_product: Product,
        user_token: str,
    ):
        log = MealLog(
            User_ID=test_user.User_ID,
            Product_ID=test_product.Product_ID,
            Log_Date=date(2026, 3, 10),
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        headers = {"Authorization": f"Bearer {user_token}"}

        update_response = client.put(
            f"/api/v0/meal-logs/{log.Log_ID}",
            json={
                "User_ID": test_user.User_ID,
                "Product_ID": test_product.Product_ID,
                "Log_Date": "2026-03-11",
            },
            headers=headers,
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["Log_Date"] == "2026-03-11"

        delete_response = client.delete(
            f"/api/v0/meal-logs/{log.Log_ID}",
            headers=headers,
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(f"/api/v0/meal-logs/{log.Log_ID}", headers=headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
