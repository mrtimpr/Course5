from datetime import time

import pytest

from habits.models import Habit

pytestmark = pytest.mark.django_db


def test_reward_and_related_habit_are_mutually_exclusive(
    authenticated_client,
    user,
    habit_payload,
):
    pleasant = Habit.objects.create(
        owner=user,
        place="Дома",
        time=time(21, 0),
        action="Принять ванну",
        is_pleasant=True,
        execution_time=120,
    )
    habit_payload.update({"related_habit": pleasant.id, "reward": "Десерт"})

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 400
    assert "non_field_errors" in response.data


def test_execution_time_cannot_exceed_two_minutes(
    authenticated_client,
    habit_payload,
):
    habit_payload["execution_time"] = 121

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 400
    assert "execution_time" in response.data


@pytest.mark.parametrize("periodicity", [0, 8])
def test_periodicity_must_be_between_one_and_seven(
    authenticated_client,
    habit_payload,
    periodicity,
):
    habit_payload["periodicity"] = periodicity

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 400
    assert "periodicity" in response.data


def test_related_habit_must_be_pleasant(
    authenticated_client,
    user,
    habit_payload,
):
    useful = Habit.objects.create(
        owner=user,
        place="Дома",
        time=time(11, 0),
        action="Выпить стакан воды",
        execution_time=10,
    )
    habit_payload["related_habit"] = useful.id
    habit_payload["reward"] = ""

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 400
    assert "related_habit" in response.data


def test_pleasant_habit_cannot_have_reward(
    authenticated_client,
    habit_payload,
):
    habit_payload.update({"is_pleasant": True, "reward": "Шоколад"})

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 400
    assert "reward" in response.data


def test_pleasant_habit_cannot_have_related_habit(
    authenticated_client,
    user,
    habit_payload,
):
    pleasant = Habit.objects.create(
        owner=user,
        place="Дома",
        time=time(12, 0),
        action="Слушать музыку",
        is_pleasant=True,
        execution_time=120,
    )
    habit_payload.update(
        {"is_pleasant": True, "related_habit": pleasant.id, "reward": ""}
    )

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 400
    assert "related_habit" in response.data


def test_related_habit_must_belong_to_current_user(
    authenticated_client,
    another_user,
    habit_payload,
):
    foreign_pleasant = Habit.objects.create(
        owner=another_user,
        place="Дома",
        time=time(13, 0),
        action="Посмотреть серию сериала",
        is_pleasant=True,
        execution_time=120,
    )
    habit_payload.update({"related_habit": foreign_pleasant.id, "reward": ""})

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 400
    assert "related_habit" in response.data


def test_valid_useful_habit_can_reference_own_pleasant_habit(
    authenticated_client,
    user,
    habit_payload,
):
    pleasant = Habit.objects.create(
        owner=user,
        place="Дома",
        time=time(22, 0),
        action="Принять ванну с пеной",
        is_pleasant=True,
        execution_time=120,
    )
    habit_payload.update({"related_habit": pleasant.id, "reward": ""})

    response = authenticated_client.post("/api/habits/", habit_payload, format="json")

    assert response.status_code == 201
    assert response.data["related_habit"] == pleasant.id
