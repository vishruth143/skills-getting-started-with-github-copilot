import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

original_activities = copy.deepcopy(app_module.activities)
client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = copy.deepcopy(original_activities)
    yield
    app_module.activities = copy.deepcopy(original_activities)


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"], dict)
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_succeeds():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}

    activity_data = client.get("/activities").json()[activity]
    assert email in activity_data["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_for_activity_succeeds():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}

    activity_data = client.get("/activities").json()[activity]
    assert email not in activity_data["participants"]


def test_unregister_not_signed_up_returns_400():
    # Arrange
    email = "missing@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Email not signed up for this activity"


def test_signup_invalid_activity_returns_404():
    # Arrange
    activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_invalid_activity_returns_404():
    # Arrange
    activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity)}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
