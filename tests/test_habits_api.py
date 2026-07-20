from datetime import time

import pytest

from habits.models import Habit

pytestmark = pytest.mark.django_db


def test_authenticated_user_can_create_habit(
    authenticated_client,
    user,
    habit_payload,
):
    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 201
    habit = Habit.objects.get(pk=response.data["id"])
    assert habit.owner == user
    assert habit.action == habit_payload["action"]


def test_user_sees_only_own_habits(authenticated_client, user, another_user):
    own_habit = Habit.objects.create(
        owner=user,
        place="Дома",
        time=time(9, 0),
        action="Сделать зарядку",
        execution_time=60,
    )
    Habit.objects.create(
        owner=another_user,
        place="Офис",
        time=time(10, 0),
        action="Выпить воду",
        execution_time=30,
    )

    response = authenticated_client.get("/api/habits/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == own_habit.id


def test_user_cannot_retrieve_or_modify_another_users_habit(
    authenticated_client,
    another_user,
):
    foreign_habit = Habit.objects.create(
        owner=another_user,
        place="Зал",
        time=time(8, 0),
        action="Сделать растяжку",
        execution_time=100,
    )

    retrieve = authenticated_client.get(f"/api/habits/{foreign_habit.id}/")
    update = authenticated_client.patch(
        f"/api/habits/{foreign_habit.id}/",
        {"action": "Изменить чужую привычку"},
        format="json",
    )
    delete = authenticated_client.delete(f"/api/habits/{foreign_habit.id}/")

    assert retrieve.status_code == 404
    assert update.status_code == 404
    assert delete.status_code == 404
    assert Habit.objects.filter(pk=foreign_habit.id).exists()


def test_owner_can_update_and_delete_habit(authenticated_client, user):
    habit = Habit.objects.create(
        owner=user,
        place="Дома",
        time=time(7, 0),
        action="Сделать зарядку",
        execution_time=90,
    )

    update = authenticated_client.patch(
        f"/api/habits/{habit.id}/",
        {"action": "Сделать лёгкую зарядку"},
        format="json",
    )
    delete = authenticated_client.delete(f"/api/habits/{habit.id}/")

    assert update.status_code == 200
    assert update.data["action"] == "Сделать лёгкую зарядку"
    assert delete.status_code == 204
    assert not Habit.objects.filter(pk=habit.id).exists()


def test_public_habits_are_visible_read_only_without_authentication(api_client, user):
    public_habit = Habit.objects.create(
        owner=user,
        place="Парк",
        time=time(18, 0),
        action="Гулять вокруг квартала",
        execution_time=120,
        is_public=True,
    )
    Habit.objects.create(
        owner=user,
        place="Дома",
        time=time(20, 0),
        action="Записать планы",
        execution_time=60,
        is_public=False,
    )

    response = api_client.get("/api/habits/public/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    item = response.data["results"][0]
    assert item["id"] == public_habit.id
    assert "owner" not in item
    assert "related_habit" not in item


def test_limit_offset_pagination_returns_required_shape(authenticated_client, user):
    for index in range(7):
        Habit.objects.create(
            owner=user,
            place="Дома",
            time=time(6 + index, 0),
            action=f"Привычка {index}",
            execution_time=60,
        )

    first_page = authenticated_client.get("/api/habits/?limit=5&offset=0")
    second_page = authenticated_client.get("/api/habits/?limit=5&offset=5")

    assert first_page.status_code == 200
    assert first_page.data["count"] == 7
    assert len(first_page.data["results"]) == 5
    assert first_page.data["next"] is not None
    assert second_page.data["count"] == 7
    assert len(second_page.data["results"]) == 2
    assert second_page.data["previous"] is not None
