from src.app import activities


class TestGetRoot:
    def test_redirects_to_index(self, client):
        # Arrange
        url = "/"

        # Act
        response = client.get(url, follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange
        expected_activities = set(activities.keys())

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert set(response.json().keys()) == expected_activities

    def test_activity_has_expected_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        for name, details in response.json().items():
            assert required_fields.issubset(details.keys()), f"{name} missing fields"


class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        assert email in activities[activity]["participants"]

    def test_signup_nonexistent_activity(self, client):
        # Arrange
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # already in participants

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"


class TestUnregister:
    def test_unregister_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # existing participant

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity}"
        assert email not in activities[activity]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        # Arrange
        activity = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_not_signed_up(self, client):
        # Arrange
        activity = "Chess Club"
        email = "nobody@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"
