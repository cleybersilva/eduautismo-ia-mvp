"""
Activity API routes.

This module defines the FastAPI routes for activity operations.
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.database import get_db
from app.models.activity import Activity
from app.models.student import Student
from app.schemas.activity import (
    ActivityCreate,
    ActivityFilterParams,
    ActivityGenerate,
    ActivityListResponse,
    ActivityResponse,
    ActivityUpdate,
)
from app.services.activity_service import ActivityService
from app.services.nlp_service import get_nlp_service
from app.utils.constants import (
    GradeLevel,
    PedagogicalActivityType,
    Subject,
    get_grade_levels,
    get_subjects,
)
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
        description=(
            f"Atividade {type_name.lower()} personalizada para {student.name}, "
            f"com nível de dificuldade {difficulty_name.lower()}. "
            f"Esta atividade foi criada considerando o perfil de aprendizagem do aluno: {student.diagnosis}."
        ),
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


@router.get("/search/bncc/{bncc_code}", response_model=List[ActivityListResponse])
def search_by_bncc(
    bncc_code: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ActivityListResponse]:
    """
    Search activities by BNCC competency code (MVP 3.0).

    Searches for activities that include the specified BNCC code in their
    bncc_competencies array.

    **Example:** `/search/bncc/EF03MA01`

    **Parameters:**
    - bncc_code: BNCC competency code (e.g., "EF03MA01")
    - skip: Pagination offset
    - limit: Maximum results (1-100)

    **Returns:** List of activities with the specified BNCC code
    """
    teacher_id = UUID(current_user["user_id"])

    logger.info(f"Searching activities by BNCC code: {bncc_code}")

    # Query activities with BNCC code
    query = db.query(Activity).join(Student).filter(Student.teacher_id == teacher_id)

    # Filter by BNCC code (works for both PostgreSQL and SQLite)
    if db.bind.dialect.name == "postgresql":
        # PostgreSQL: uses native ARRAY contains operator
        query = query.filter(Activity.bncc_competencies.contains([bncc_code]))
        activities = query.offset(skip).limit(limit).all()
    else:
        # SQLite: Filter in Python since StringArray deserializes JSON to list
        # We retrieve all activities for the teacher, then filter by BNCC code in memory
        all_activities = query.offset(skip).limit(100).all()  # Get more to ensure we have enough
        activities = [
            act
            for act in all_activities
            if act.bncc_competencies and bncc_code in act.bncc_competencies
        ]
        # Apply limit after filtering
        activities = activities[:limit]

    logger.info(f"Found {len(activities)} activities with BNCC code {bncc_code}")

    return activities
@router.get("/meta/subjects", response_model=Dict[str, str])
def list_subjects() -> Dict[str, str]:
    """
    List all available subjects/disciplines (MVP 3.0).

    Returns a dictionary mapping subject codes to display names.

    **Example Response:**
    ```json
    {
      "matematica": "Matemática",
      "portugues": "Português",
      "ciencias": "Ciências",
      ...
    }
    ```

    **Use case:** Populate subject dropdown in frontend
    """
    from app.utils.constants import get_subject_display_name

    subjects = {}
    for subject_code in get_subjects():
        try:
            subject_enum = Subject(subject_code)
            subjects[subject_code] = get_subject_display_name(subject_enum)
        except ValueError:
            subjects[subject_code] = subject_code

    return subjects
@router.get("/meta/grade-levels", response_model=Dict[str, str])
def list_grade_levels() -> Dict[str, str]:
    """
    List all available grade levels (MVP 3.0).

    Returns a dictionary mapping grade level codes to display names.

    **Example Response:**
    ```json
    {
      "infantil_maternal": "Infantil - Maternal",
      "fundamental_1_1ano": "1º Ano - Fundamental I",
      "medio_1ano": "1ª Série - Ensino Médio",
      ...
    }
    ```

    **Use case:** Populate grade level dropdown in frontend
    """
    from app.utils.constants import get_grade_level_display_name

    grade_levels = {}
    for grade_code in get_grade_levels():
        try:
            grade_enum = GradeLevel(grade_code)
            grade_levels[grade_code] = get_grade_level_display_name(grade_enum)
        except ValueError:
            grade_levels[grade_code] = grade_code

    return grade_levels
@router.get("/search", response_model=List[ActivityListResponse])
def search_activities(
    subject: Optional[Subject] = Query(None, description="Filter by subject"),
    grade_level: Optional[GradeLevel] = Query(None, description="Filter by grade level"),
    pedagogical_type: Optional[PedagogicalActivityType] = Query(None, description="Filter by pedagogical type"),
    has_bncc: Optional[bool] = Query(None, description="Filter activities with/without BNCC codes"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    student_id: Optional[UUID] = Query(None, description="Filter by student"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[ActivityListResponse]:
    """
    Advanced search with multidisciplinary filters (MVP 3.0).

    **New Filters:**
    - subject: Filter by educational subject
    - grade_level: Filter by grade level
    - pedagogical_type: Filter by activity format
    - has_bncc: true/false to filter activities with/without BNCC codes

    **Example:**
    ```
    GET /search?subject=matematica&grade_level=fundamental_1_3ano&has_bncc=true
    ```

    **Returns:** Paginated list of activities matching all filters
    """
    teacher_id = UUID(current_user["user_id"])

    # Start with base query
    query = db.query(Activity).join(Student).filter(Student.teacher_id == teacher_id)

    # Apply v3.0 filters
    if subject:
        query = query.filter(Activity.subject == subject)

    if grade_level:
        query = query.filter(Activity.grade_level == grade_level)

    if pedagogical_type:
        query = query.filter(Activity.pedagogical_type == pedagogical_type)

    if has_bncc is not None:
        if has_bncc:
            # Has BNCC codes (array is not null and not empty)
            query = query.filter(Activity.bncc_competencies.isnot(None))
        else:
            # Does not have BNCC codes
            query = query.filter(
                or_(Activity.bncc_competencies.is_(None), Activity.bncc_competencies == [])
            )

    if difficulty:
        query = query.filter(Activity.difficulty == difficulty)

    if student_id:
        query = query.filter(Activity.student_id == student_id)

    # Execute query with pagination
    activities = query.order_by(Activity.created_at.desc()).offset(skip).limit(limit).all()

    logger.info(
        f"Advanced search: subject={subject}, grade={grade_level}, "
        f"pedagogical_type={pedagogical_type}, found={len(activities)}"
    )

    return activities

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


# ============================================================================
# MVP 3.0 - Multidisciplinary Endpoints
# ============================================================================


@router.post("/generate-multidisciplinary", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def generate_multidisciplinary_activity(
    activity_data: ActivityGenerate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityResponse:
    """
    Generate multidisciplinary activity using AI with subject-specific context (MVP 3.0).

    This endpoint generates activities tailored to specific subjects, grade levels,
    and pedagogical formats, with optional BNCC alignment.

    **New Parameters (v3.0):**
    - subject: Educational subject/discipline (e.g., "matematica", "portugues")
    - grade_level: Brazilian education level (e.g., "fundamental_1_3ano")
    - pedagogical_type: Activity format (e.g., "exercicio", "jogo_educativo")
    - bncc_competencies: Array of BNCC codes (e.g., ["EF03MA01"])

    **Example Request:**
    ```json
    {
      "student_id": "uuid-here",
      "activity_type": "cognitive",
      "difficulty": "medium",
      "duration_minutes": 30,
      "subject": "matematica",
      "grade_level": "fundamental_1_3ano",
      "pedagogical_type": "exercicio",
      "bncc_competencies": ["EF03MA06"],
      "theme": "adição com reagrupamento"
    }
    ```

    **Returns:** Generated activity with subject-specific content

    **Raises:**
    - 400: Missing required fields (subject and grade_level)
    - 404: Student not found
    - 403: Permission denied
    - 500: AI generation failed
    """
    teacher_id = UUID(current_user["user_id"])

    # Validate required fields for multidisciplinary generation
    if not activity_data.subject or not activity_data.grade_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="subject e grade_level são obrigatórios para geração multidisciplinar",
        )

    # Get student
    student = db.query(Student).filter(Student.id == activity_data.student_id).first()

    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    # Check permission
    if student.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para criar atividades para este aluno",
        )

    logger.info(
        f"Generating multidisciplinary activity: student={student.id}, "
        f"subject={activity_data.subject}, grade={activity_data.grade_level}"
    )

    try:
        # Use NLP Service if subject and grade_level are provided
        if activity_data.subject and activity_data.grade_level:
            nlp_service = get_nlp_service()

            # Build student profile
            student_profile = {
                "name": student.name,
                "age": student.age,
                "diagnosis": student.diagnosis,
                "interests": student.interests or [],
                "strengths": [],  # TODO: Add to student model
                "challenges": [],  # TODO: Add to student model
            }

            # Generate with NLP Service
            generated = await nlp_service.generate_multidisciplinary_activity(
                student_profile=student_profile,
                subject=activity_data.subject,
                grade_level=activity_data.grade_level,
                activity_type=activity_data.activity_type,
                pedagogical_type=activity_data.pedagogical_type,
                difficulty=activity_data.difficulty,
                duration_minutes=activity_data.duration_minutes,
                theme=activity_data.theme,
                bncc_competencies=activity_data.bncc_competencies,
            )

            # Create activity from generated content
            activity = Activity(
                student_id=activity_data.student_id,
                title=generated.title,
                description=generated.description,
                activity_type=activity_data.activity_type,
                difficulty=activity_data.difficulty,
                duration_minutes=generated.duration_minutes,
                objectives=generated.objectives,
                materials=generated.materials,
                instructions=generated.instructions,
                adaptations=generated.adaptations,
                visual_supports=generated.visual_supports,
                success_criteria=generated.success_criteria,
                theme=activity_data.theme,
                tags=[activity_data.subject.value, activity_data.grade_level.value]
                if activity_data.subject and activity_data.grade_level
                else None,
                # MVP 3.0 fields
                subject=activity_data.subject,
                grade_level=activity_data.grade_level,
                pedagogical_type=activity_data.pedagogical_type,
                bncc_competencies=activity_data.bncc_competencies,
                # Metadata
                generated_by_ai=True,
                generation_metadata={
                    "model": "gpt-4o",
                    "subject": activity_data.subject.value if activity_data.subject else None,
                    "grade_level": activity_data.grade_level.value if activity_data.grade_level else None,
                    "bncc_codes": activity_data.bncc_competencies,
                },
                is_published=True,
                is_template=False,
                created_by_id=teacher_id,
            )

            db.add(activity)
            db.commit()
            db.refresh(activity)

            logger.info(f"Multidisciplinary activity generated: {activity.id}")

            return activity

        else:
            # Fallback to simple generation if subject/grade not provided
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="subject e grade_level são obrigatórios para geração multidisciplinar",
            )

    except Exception as e:
        logger.error(f"Error generating multidisciplinary activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar atividade: {str(e)}",
        )








