"""
Activity API routes.

This module defines the FastAPI routes for activity operations.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.activity import Activity
from app.models.student import Student
from app.schemas.activity import ActivityCreate, ActivityGenerate, ActivityResponse, ActivityUpdate
from app.services.activity_service import ActivityService
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/activities", tags=["activities"])


@router.post("/generate", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def generate_activity(
    activity_data: ActivityGenerate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> ActivityResponse:
    """
    Generate personalized activity using AI.

    Args:
        activity_data: Generation parameters
        current_user: Current authenticated user
        db: Database session

    Returns:
        Generated activity object

    Raises:
        HTTPException: If student not found or permission denied
    """
    teacher_id = UUID(current_user["user_id"])

    # Get student
    student = db.query(Student).filter(Student.id == activity_data.student_id).first()

    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    # Check permission
    if student.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para criar atividades para este aluno"
        )

    # Generate activity content (simplified version without OpenAI)
    logger.info(f"Generating activity for student {student.id} by teacher {teacher_id}")

    # Build activity based on student profile and parameters
    activity_type_names = {
        "cognitive": "Cognitiva",
        "social": "Social",
        "motor": "Motora",
        "sensory": "Sensorial",
        "communication": "Comunicação",
        "daily_living": "Vida Diária",
        "academic": "Acadêmica",
    }

    difficulty_names = {
        "very_easy": "Muito Fácil",
        "easy": "Fácil",
        "medium": "Médio",
        "hard": "Difícil",
        "very_hard": "Muito Difícil",
    }

    type_name = activity_type_names.get(activity_data.activity_type, activity_data.activity_type)
    difficulty_name = difficulty_names.get(activity_data.difficulty, activity_data.difficulty)
    theme_text = f" - {activity_data.theme}" if activity_data.theme else ""

    # Create activity
    activity = Activity(
        student_id=activity_data.student_id,
        title=f"Atividade {type_name}{theme_text}",
        description=f"Atividade {type_name.lower()} personalizada para {student.name}, com nível de dificuldade {difficulty_name.lower()}. "
        f"Esta atividade foi criada considerando o perfil de aprendizagem do aluno: {student.diagnosis}.",
        activity_type=activity_data.activity_type,
        difficulty=activity_data.difficulty,
        duration_minutes=activity_data.duration_minutes,
        objectives=[
            f"Desenvolver habilidades de {type_name.lower()} adequadas ao nível do aluno",
            "Promover engajamento através de atividades adaptadas",
            "Respeitar o perfil sensorial e ritmo de aprendizagem",
        ],
        materials=["Material visual de apoio", "Recursos adaptados para TEA", "Ambiente estruturado e previsível"],
        instructions=[
            "1. Prepare o ambiente garantindo que esteja calmo e organizado",
            "2. Apresente a atividade de forma clara e visual",
            "3. Divida a tarefa em pequenos passos",
            "4. Ofereça suporte quando necessário",
            "5. Reforce positivamente cada conquista",
            "6. Permita pausas sensoriais se o aluno demonstrar necessidade",
        ],
        adaptations=[
            "Use apoios visuais (imagens, pictogramas)",
            "Mantenha instruções curtas e diretas",
            "Permita tempo extra para processamento",
            "Reduza estímulos sensoriais desnecessários",
        ],
        visual_supports=[
            "Sequência visual dos passos",
            "Timer visual para duração",
            "Imagens de apoio relacionadas ao tema",
        ],
        success_criteria=[
            "Aluno consegue iniciar a atividade com suporte mínimo",
            "Demonstra compreensão das instruções",
            "Completa pelo menos 70% da atividade proposta",
            "Mantém engajamento durante a maior parte do tempo",
        ],
        theme=activity_data.theme,
        tags=[activity_data.activity_type, activity_data.difficulty],
        generated_by_ai=True,
        generation_metadata={
            "student_profile": {
                "name": student.name,
                "age": student.age,
                "diagnosis": student.diagnosis,
                "tea_level": student.tea_level,
                "interests": student.interests,
            },
            "generation_params": {
                "activity_type": activity_data.activity_type,
                "difficulty": activity_data.difficulty,
                "duration_minutes": activity_data.duration_minutes,
                "theme": activity_data.theme,
            },
            "model": "template-based",
            "note": "Generated using simplified template (OpenAI integration pending)",
        },
        is_published=True,
        is_template=False,
        created_by_id=teacher_id,
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    logger.info(f"Activity generated successfully: {activity.id}")

    return activity


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_data: ActivityCreate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
) -> ActivityResponse:
    """
    Create a new activity manually.

    Args:
        activity_data: Activity creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created activity object
    """
    teacher_id = UUID(current_user["user_id"])

    # Verify student exists and belongs to teacher
    student = db.query(Student).filter(Student.id == activity_data.student_id).first()

    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    if student.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para criar atividades para este aluno"
        )

    # Create activity
    activity = Activity(
        **activity_data.model_dump(),
        generated_by_ai=False,
        is_published=True,
        is_template=False,
        created_by_id=teacher_id,
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int, db: Session = Depends(get_db)) -> ActivityResponse:
    """
    Get a activity by ID.

    Args:
        activity_id: Activity ID
        db: Database session

    Returns:
        Activity object

    Raises:
        HTTPException: If activity not found
    """
    activity = ActivityService.get(db, activity_id)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return activity


@router.get("/", response_model=List[ActivityResponse])
def list_activitys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[ActivityResponse]:
    """
    List activitys with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List of activity objects
    """
    return ActivityService.get_multi(db, skip=skip, limit=limit)


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(activity_id: int, activity_data: ActivityUpdate, db: Session = Depends(get_db)) -> ActivityResponse:
    """
    Update a activity.

    Args:
        activity_id: Activity ID
        activity_data: Update data
        db: Database session

    Returns:
        Updated activity object

    Raises:
        HTTPException: If activity not found
    """
    activity = ActivityService.update(db, activity_id, activity_data)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(activity_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete a activity.

    Args:
        activity_id: Activity ID
        db: Database session

    Raises:
        HTTPException: If activity not found
    """
    success = ActivityService.delete(db, activity_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
