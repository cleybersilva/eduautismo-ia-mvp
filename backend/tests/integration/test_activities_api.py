"""
Integration tests for activities API.
"""


class TestActivitiesAPI:
    """Test class for activities API endpoints."""

    def test_generate_activity_success(self, client, auth_headers, test_student):
        """Test successful activity generation."""
        response = client.post(
            "/api/v1/activities/generate",
            headers=auth_headers,
            json={
                "student_id": test_student["id"],
                "activity_type": "cognitive",
                "difficulty": "easy",
                "duration_minutes": 30,
                "theme": "números e cores",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == test_student["id"]
        assert data["activity_type"] == "cognitive"
        assert data["difficulty"] == "easy"
        assert data["duration_minutes"] == 30
        assert data["theme"] == "números e cores"
        assert data["generated_by_ai"] is True
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "objectives" in data
        assert "materials" in data
        assert "instructions" in data

    def test_generate_activity_without_auth(self, client, test_student):
        """Test generating activity without authentication fails."""
        response = client.post(
            "/api/v1/activities/generate",
            json={
                "student_id": test_student["id"],
                "activity_type": "academic",
                "difficulty": "medium",
                "duration_minutes": 45,
            },
        )

        assert response.status_code == 403

    def test_generate_activity_nonexistent_student(self, client, auth_headers):
        """Test generating activity for non-existent student."""
        import uuid

        fake_id = str(uuid.uuid4())

        response = client.post(
            "/api/v1/activities/generate",
            headers=auth_headers,
            json={"student_id": fake_id, "activity_type": "social", "difficulty": "easy", "duration_minutes": 30},
        )

        assert response.status_code == 404

    def test_generate_activity_invalid_duration(self, client, auth_headers, test_student):
        """Test generating activity with invalid duration."""
        response = client.post(
            "/api/v1/activities/generate",
            headers=auth_headers,
            json={
                "student_id": test_student["id"],
                "activity_type": "motor",
                "difficulty": "medium",
                "duration_minutes": 200,  # Over maximum
            },
        )

        assert response.status_code == 422

    def test_generate_multiple_activity_types(self, client, auth_headers, test_student):
        """Test generating activities of different types."""
        activity_types = ["cognitive", "social", "motor", "academic"]

        for activity_type in activity_types:
            response = client.post(
                "/api/v1/activities/generate",
                headers=auth_headers,
                json={
                    "student_id": test_student["id"],
                    "activity_type": activity_type,
                    "difficulty": "easy",
                    "duration_minutes": 30,
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert data["activity_type"] == activity_type
            assert data["generated_by_ai"] is True
