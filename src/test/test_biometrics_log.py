"""Tests for biometrics log endpoints."""

from datetime import date

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth import create_access_token, hash_password
from src.models.biometrics_log import BiometricsLog
from src.models.user import User


class TestBiometricsLogEndpoints:
    """Tests for biometrics log CRUD and per-user isolation."""

    def test_create_biometrics_log_success(
        self,
        client: TestClient,
        test_user: User,
        user_token: str,
    ):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            "/api/v0/biometrics-logs/",
            json={
                "User_ID": 99999,
                "Log_Date": "2026-03-30",
                "Weight": 79.5,
                "Sleep_Hours": 7.5,
                "Heart_Rate": 62,
            },
            headers=headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        payload = response.json()
        assert payload["User_ID"] == test_user.User_ID
        assert payload["Weight"] == 79.5

    def test_create_biometrics_log_unauthorized(self, client: TestClient):
        response = client.post(
            "/api/v0/biometrics-logs/",
            json={
                "User_ID": 1,
                "Log_Date": "2026-03-30",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_biometrics_logs_returns_only_current_user_data(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        other_user = User(
            User_mail="bio-other@example.com",
            User_password=hash_password("otherpassword123"),
            isAdmin=False,
        )
        db.add(other_user)
        db.commit()

        own_log = BiometricsLog(
            User_ID=test_user.User_ID,
            Log_Date=date(2026, 3, 1),
            Weight=80.0,
        )
        other_log = BiometricsLog(
            User_ID=other_user.User_ID,
            Log_Date=date(2026, 3, 2),
            Weight=95.0,
        )
        db.add_all([own_log, other_log])
        db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/biometrics-logs/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        returned_ids = [item["Log_ID"] for item in response.json()]
        assert own_log.Log_ID in returned_ids
        assert other_log.Log_ID not in returned_ids

    def test_get_biometrics_log_not_found_for_other_user(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        other_user = User(
            User_mail="bio-owner@example.com",
            User_password=hash_password("ownerpassword123"),
            isAdmin=False,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        other_log = BiometricsLog(
            User_ID=other_user.User_ID,
            Log_Date=date(2026, 3, 3),
            Weight=91.0,
        )
        db.add(other_log)
        db.commit()
        db.refresh(other_log)

        token = create_access_token(data={"sub": str(test_user.User_ID)})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/api/v0/biometrics-logs/{other_log.Log_ID}", headers=headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Biometrics log not found" in response.json()["detail"]

    def test_update_and_delete_biometrics_log(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        log = BiometricsLog(
            User_ID=test_user.User_ID,
            Log_Date=date(2026, 3, 10),
            Weight=82.0,
            Sleep_Hours=6.0,
            Heart_Rate=70,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        headers = {"Authorization": f"Bearer {user_token}"}

        update_response = client.put(
            f"/api/v0/biometrics-logs/{log.Log_ID}",
            json={
                "User_ID": test_user.User_ID,
                "Log_Date": "2026-03-11",
                "Weight": 81.2,
                "Sleep_Hours": 7.2,
                "Heart_Rate": 66,
            },
            headers=headers,
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["Weight"] == 81.2

        delete_response = client.delete(
            f"/api/v0/biometrics-logs/{log.Log_ID}",
            headers=headers,
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(
            f"/api/v0/biometrics-logs/{log.Log_ID}",
            headers=headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
