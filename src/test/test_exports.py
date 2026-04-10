"""Tests for CSV export endpoints."""

import csv
from datetime import date
from io import StringIO

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.workout_session import WorkoutSession
from src.models.workout_type import WorkoutType


def _read_csv_rows(response_text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(response_text))
    return list(reader)


class TestCsvExports:
    def test_export_requires_auth(self, client: TestClient):
        response = client.get("/api/v0/exports/products.csv")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_forbidden_non_admin(self, client: TestClient, user_token: str):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/exports/products.csv", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only admins can export data" in response.json()["detail"]

    def test_export_products_csv_admin(self, client: TestClient, admin_token: str, test_product):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/exports/products.csv", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert "text/csv" in response.headers.get("content-type", "")
        assert "products.csv" in response.headers.get("content-disposition", "")

        rows = _read_csv_rows(response.text)
        assert len(rows) >= 1
        assert "product_name" in rows[0]
        assert any(row["product_name"] == test_product.product_name for row in rows)

    def test_export_users_csv_admin_excludes_password(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/exports/users.csv", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        rows = _read_csv_rows(response.text)
        assert len(rows) >= 1
        assert "User_password" not in rows[0]
        assert "User_mail" in rows[0]

    def test_export_meal_logs_csv_empty_has_header_only(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/exports/meal-logs.csv", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        lines = [line for line in response.text.splitlines() if line.strip()]
        assert len(lines) == 1
        assert lines[0].startswith("Log_ID,User_ID,Product_ID,Log_Date")

    def test_export_workout_sessions_csv_includes_workout_type_fields(
        self,
        client: TestClient,
        db: Session,
        test_user,
        admin_token: str,
    ):
        workout_type = WorkoutType(WorkoutType_Name="running")
        db.add(workout_type)
        db.commit()
        db.refresh(workout_type)

        workout_session = WorkoutSession(
            User_ID=test_user.User_ID,
            Session_Date=date(2026, 4, 1),
            Session_Duration=35,
            WorkoutType_ID=workout_type.WorkoutType_ID,
        )
        db.add(workout_session)
        db.commit()

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/exports/workout-sessions.csv", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        rows = _read_csv_rows(response.text)
        assert len(rows) >= 1
        assert "WorkoutType_ID" in rows[0]
        assert "WorkoutType_Name" in rows[0]
        assert any(
            row["WorkoutType_Name"] == workout_type.WorkoutType_Name
            for row in rows
        )
