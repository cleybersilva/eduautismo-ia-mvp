"""
Integration tests for assessments API.
"""


class TestAssessmentsAPI:
    """Test class for assessments API endpoints."""

    def test_create_assessment_success(self, client, auth_headers, test_activity):
        """Test successful assessment creation."""
        response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "completed",
                "engagement_level": "high",
                "difficulty_rating": "appropriate",
                "actual_duration_minutes": 35,
                "notes": "Aluno demonstrou excelente engajamento",
                "strengths_observed": "Boa concentração e persistência",
                "challenges_observed": "Precisa de apoio em algumas etapas",
                "recommendations": "Continuar com atividades similares",
                "independence_level": "Independente com supervisão",
                "assistance_needed": "Apoio verbal ocasional",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["activity_id"] == test_activity["id"]
        assert data["student_id"] == test_activity["student_id"]
        assert data["completion_status"] == "completed"
        assert data["engagement_level"] == "high"
        assert data["difficulty_rating"] == "appropriate"
        assert data["actual_duration_minutes"] == 35
        assert "id" in data
        assert "created_at" in data

    def test_create_assessment_without_auth(self, client, test_activity):
        """Test creating assessment without authentication fails."""
        response = client.post(
            "/api/v1/assessments/",
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "completed",
                "engagement_level": "high",
                "difficulty_rating": "appropriate",
            },
        )

        # FastAPI's HTTPBearer returns 403 when no auth header is provided
        assert response.status_code == 403

    def test_create_assessment_invalid_activity(self, client, auth_headers, test_activity):
        """Test creating assessment with invalid activity ID."""
        import uuid

        fake_id = str(uuid.uuid4())

        response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": fake_id,
                "student_id": test_activity["student_id"],
                "completion_status": "completed",
                "engagement_level": "high",
                "difficulty_rating": "appropriate",
            },
        )

        assert response.status_code in [404, 400]

    def test_create_assessment_minimal_data(self, client, auth_headers, test_activity):
        """Test creating assessment with minimal required data."""
        response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "completed",
                "engagement_level": "medium",
                "difficulty_rating": "appropriate",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["activity_id"] == test_activity["id"]
        assert data["completion_status"] == "completed"

    def test_get_assessment_by_id(self, client, auth_headers, test_activity):
        """Test getting assessment by ID."""
        # First create an assessment
        create_response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "completed",
                "engagement_level": "high",
                "difficulty_rating": "appropriate",
            },
        )
        assessment_id = create_response.json()["id"]

        # Now get it
        response = client.get(f"/api/v1/assessments/{assessment_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == assessment_id
        assert data["activity_id"] == test_activity["id"]

    def test_get_assessment_not_found(self, client, auth_headers):
        """Test getting non-existent assessment."""
        import uuid

        fake_id = str(uuid.uuid4())

        response = client.get(f"/api/v1/assessments/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_list_assessments_by_student(self, client, auth_headers, test_activity):
        """Test listing assessments for a student."""
        # Create multiple assessments
        for i in range(3):
            client.post(
                "/api/v1/assessments/",
                headers=auth_headers,
                json={
                    "activity_id": test_activity["id"],
                    "student_id": test_activity["student_id"],
                    "completion_status": "completed",
                    "engagement_level": "high",
                    "difficulty_rating": "appropriate",
                    "notes": f"Assessment {i+1}",
                },
            )

        # List assessments
        response = client.get(f"/api/v1/assessments/student/{test_activity["student_id"]}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_update_assessment(self, client, auth_headers, test_activity):
        """Test updating an assessment."""
        # Create assessment
        create_response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "in_progress",
                "engagement_level": "medium",
                "difficulty_rating": "appropriate",
            },
        )
        assessment_id = create_response.json()["id"]

        # Update assessment
        response = client.put(
            f"/api/v1/assessments/{assessment_id}",
            headers=auth_headers,
            json={
                "completion_status": "completed",
                "engagement_level": "high",
                "notes": "Atualização: Atividade concluída com sucesso",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["completion_status"] == "completed"
        assert data["engagement_level"] == "high"
        assert "Atualização" in data["notes"]

    def test_create_assessment_with_skills_data(self, client, auth_headers, test_activity):
        """Test creating assessment with skills and behavioral data."""
        response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "completed",
                "engagement_level": "very_high",
                "difficulty_rating": "appropriate",
                "skills_demonstrated": {"fine_motor": True, "problem_solving": True, "communication": False},
                "behavioral_notes": {
                    "self_regulation": "good",
                    "social_interaction": "needs_improvement",
                    "attention_span": "excellent",
                },
                "objectives_met": {"objective_1": True, "objective_2": True, "objective_3": False},
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["skills_demonstrated"] is not None
        assert data["behavioral_notes"] is not None
        assert data["objectives_met"] is not None

    def test_create_assessment_invalid_completion_status(self, client, auth_headers, test_activity):
        """Test creating assessment with invalid completion status."""
        response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "invalid_status",
                "engagement_level": "high",
                "difficulty_rating": "appropriate",
            },
        )

        assert response.status_code == 422

    def test_create_assessment_negative_duration(self, client, auth_headers, test_activity):
        """Test creating assessment with negative duration."""
        response = client.post(
            "/api/v1/assessments/",
            headers=auth_headers,
            json={
                "activity_id": test_activity["id"],
                "student_id": test_activity["student_id"],
                "completion_status": "completed",
                "engagement_level": "high",
                "difficulty_rating": "appropriate",
                "actual_duration_minutes": -10,
            },
        )

        assert response.status_code == 422
