"""Tests for equipment endpoints."""

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth import create_access_token, hash_password
from src.models.equipment import Equipment
from src.models.user import User


class TestEquipmentEndpoints:
    """Tests for equipment CRUD and access control."""

    def test_create_equipment_success(self, client: TestClient, user_token: str):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            "/api/v0/equipment/",
            json={
                "Equipment_Name": "Dumbbell",
                "Equipment_Category": "Strength",
                "Equipment_Location": "Home",
            },
            headers=headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        payload = response.json()
        assert payload["Equipment_Name"] == "Dumbbell"
        assert "Equipment_ID" in payload

    def test_create_equipment_unauthorized(self, client: TestClient):
        response = client.post(
            "/api/v0/equipment/",
            json={
                "Equipment_Name": "Kettlebell",
                "Equipment_Category": "Strength",
                "Equipment_Location": "Gym",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_equipment_returns_only_current_user_items(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        other_user = User(
            User_mail="equipment-other@example.com",
            User_password=hash_password("otherpassword123"),
            isAdmin=False,
        )
        own_equipment = Equipment(Equipment_Name="Rowing Machine")
        other_equipment = Equipment(Equipment_Name="Treadmill")

        db.add_all([other_user, own_equipment, other_equipment])
        db.commit()

        test_user.equipment.append(own_equipment)
        other_user.equipment.append(other_equipment)
        db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/equipment/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        names = [item["Equipment_Name"] for item in response.json()]
        assert "Rowing Machine" in names
        assert "Treadmill" not in names

    def test_get_equipment_by_id_forbidden_for_non_owner(
        self,
        client: TestClient,
        db: Session,
        admin_user: User,
    ):
        owner = User(
            User_mail="equipment-owner@example.com",
            User_password=hash_password("ownerpassword123"),
            isAdmin=False,
        )
        equipment = Equipment(Equipment_Name="Spin Bike")

        db.add_all([owner, equipment])
        db.commit()

        owner.equipment.append(equipment)
        db.commit()
        db.refresh(equipment)

        token = create_access_token(data={"sub": str(admin_user.User_ID)})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"/api/v0/equipment/{equipment.Equipment_ID}", headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in response.json()["detail"]

    def test_delete_equipment_removes_association(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        equipment = Equipment(Equipment_Name="Jump Rope")
        db.add(equipment)
        db.commit()

        test_user.equipment.append(equipment)
        db.commit()
        db.refresh(equipment)

        headers = {"Authorization": f"Bearer {user_token}"}
        delete_response = client.delete(
            f"/api/v0/equipment/{equipment.Equipment_ID}",
            headers=headers,
        )

        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        list_response = client.get("/api/v0/equipment/", headers=headers)
        assert list_response.status_code == status.HTTP_200_OK
        assert all(
            item["Equipment_ID"] != equipment.Equipment_ID
            for item in list_response.json()
        )
