"""Tests for workout type endpoints."""

from fastapi import status
from fastapi.testclient import TestClient


class TestWorkoutTypeEndpoints:
    def test_get_workout_types_requires_auth(self, client: TestClient):
        response = client.get("/api/v0/workout-types/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_workout_type_admin_only(self, client: TestClient, user_token: str):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            "/api/v0/workout-types/",
            json={"WorkoutType_Name": "squats"},
            headers=headers,
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only admins can manage workout types" in response.json()["detail"]

    def test_create_and_list_workout_types_admin(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}

        create_response = client.post(
            "/api/v0/workout-types/",
            json={"WorkoutType_Name": "running"},
            headers=headers,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        created = create_response.json()
        assert created["WorkoutType_Name"] == "running"

        list_response = client.get("/api/v0/workout-types/", headers=headers)
        assert list_response.status_code == status.HTTP_200_OK
        names = [item["WorkoutType_Name"] for item in list_response.json()]
        assert "running" in names
