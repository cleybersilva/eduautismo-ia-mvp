"""
Application Constants - EduAutismo IA

Centralized constants used throughout the application.
"""

from enum import Enum
from typing import List

# ============================================================================
# User Roles
# ============================================================================


class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    TEACHER = "teacher"
    PARENT = "parent"  # Future implementation
    THERAPIST = "therapist"  # Future implementation


# ============================================================================
# Activity Types
# ============================================================================


class ActivityType(str, Enum):
    """Types of educational activities."""

    COGNITIVE = "cognitive"
    SOCIAL = "social"
    MOTOR = "motor"
    SENSORY = "sensory"
    COMMUNICATION = "communication"
    DAILY_LIVING = "daily_living"
    ACADEMIC = "academic"


# ============================================================================
# Difficulty Levels
# ============================================================================


class DifficultyLevel(str, Enum):
    """Difficulty levels for activities."""

    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


# ============================================================================
# Assessment Ratings
# ============================================================================


class EngagementLevel(str, Enum):
    """Student engagement level during activity."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CompletionStatus(str, Enum):
    """Activity completion status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    NEEDS_ASSISTANCE = "needs_assistance"


class DifficultyRating(str, Enum):
    """How appropriate was the activity difficulty."""

    TOO_EASY = "too_easy"
    SLIGHTLY_EASY = "slightly_easy"
    APPROPRIATE = "appropriate"
    SLIGHTLY_HARD = "slightly_hard"
    TOO_HARD = "too_hard"


# ============================================================================
# TEA (Autism Spectrum Disorder) Levels
# ============================================================================


class TEALevel(str, Enum):
    """TEA support levels based on DSM-5."""

    LEVEL_1 = "level_1"  # Requiring support
    LEVEL_2 = "level_2"  # Requiring substantial support
    LEVEL_3 = "level_3"  # Requiring very substantial support


# ============================================================================
# Learning Domains
# ============================================================================


class LearningDomain(str, Enum):
    """Learning domains for skill assessment."""

    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    VERBAL = "verbal"
    LOGICAL = "logical"
    SOCIAL = "social"
    EMOTIONAL = "emotional"


# ============================================================================
# OpenAI Configuration
# ============================================================================


class OpenAIModel(str, Enum):
    """Available OpenAI models."""

    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"


# Default model for activity generation
DEFAULT_OPENAI_MODEL = OpenAIModel.GPT_4O_MINI

# Token limits
MAX_TOKENS_ACTIVITY_GENERATION = 2000
MAX_TOKENS_PROGRESS_ANALYSIS = 1500
MAX_TOKENS_RECOMMENDATION = 1000

# Temperature settings
TEMPERATURE_CREATIVE = 0.9  # For creative content generation
TEMPERATURE_BALANCED = 0.7  # For general responses
TEMPERATURE_PRECISE = 0.3  # For factual/analytical content


# ============================================================================
# Pagination
# ============================================================================

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1


# ============================================================================
# Validation Constraints
# ============================================================================

# User
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True

# Student
MIN_STUDENT_AGE = 2
MAX_STUDENT_AGE = 21
MAX_INTERESTS_COUNT = 20

# Activity
MIN_ACTIVITY_DURATION = 5  # minutes
MAX_ACTIVITY_DURATION = 180  # minutes
DEFAULT_ACTIVITY_DURATION = 30  # minutes

# Assessment
MAX_NOTES_LENGTH = 2000
MAX_RECOMMENDATIONS_LENGTH = 5000


# ============================================================================
# JWT Token Configuration
# ============================================================================

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1


# ============================================================================
# File Upload
# ============================================================================

MAX_UPLOAD_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]
ALLOWED_DOCUMENT_EXTENSIONS = ["pdf", "doc", "docx", "txt"]


# ============================================================================
# Cache TTL (Time To Live) in seconds
# ============================================================================

CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour
CACHE_TTL_VERY_LONG = 86400  # 24 hours


# ============================================================================
# Rate Limiting
# ============================================================================

RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000
RATE_LIMIT_OPENAI_PER_MINUTE = 10  # Prevent API abuse


# ============================================================================
# Database
# ============================================================================

DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30  # seconds
DB_POOL_RECYCLE = 3600  # 1 hour


# ============================================================================
# Error Messages
# ============================================================================

ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Email ou senha incorretos",
    "USER_NOT_FOUND": "Usuário não encontrado",
    "USER_INACTIVE": "Usuário inativo",
    "EMAIL_ALREADY_EXISTS": "Email já cadastrado",
    "STUDENT_NOT_FOUND": "Aluno não encontrado",
    "ACTIVITY_NOT_FOUND": "Atividade não encontrada",
    "ASSESSMENT_NOT_FOUND": "Avaliação não encontrada",
    "INVALID_TOKEN": "Token inválido ou expirado",
    "PERMISSION_DENIED": "Permissão negada",
    "OPENAI_ERROR": "Erro ao gerar conteúdo com IA",
    "DATABASE_ERROR": "Erro ao acessar banco de dados",
    "VALIDATION_ERROR": "Erro de validação de dados",
}


# ============================================================================
# Success Messages
# ============================================================================

SUCCESS_MESSAGES = {
    "USER_CREATED": "Usuário criado com sucesso",
    "USER_UPDATED": "Usuário atualizado com sucesso",
    "USER_DELETED": "Usuário removido com sucesso",
    "STUDENT_CREATED": "Aluno cadastrado com sucesso",
    "STUDENT_UPDATED": "Perfil do aluno atualizado com sucesso",
    "STUDENT_DELETED": "Aluno removido com sucesso",
    "ACTIVITY_GENERATED": "Atividade gerada com sucesso",
    "ACTIVITY_UPDATED": "Atividade atualizada com sucesso",
    "ASSESSMENT_CREATED": "Avaliação registrada com sucesso",
    "PASSWORD_RESET_SENT": "Email de recuperação de senha enviado",
    "PASSWORD_RESET_SUCCESS": "Senha alterada com sucesso",
}


# ============================================================================
# System Prompts for OpenAI
# ============================================================================

SYSTEM_PROMPT_ACTIVITY_GENERATION = """
Você é um especialista em educação especial e Transtorno do Espectro Autista (TEA).
Sua função é criar atividades pedagógicas personalizadas, estruturadas e adaptadas
para crianças com TEA, considerando suas características individuais, interesses
e nível de desenvolvimento.

As atividades devem ser:
- Claras e estruturadas
- Adequadas ao nível de desenvolvimento
- Incorporar interesses especiais quando possível
- Incluir instruções visuais
- Ter objetivos educacionais bem definidos
- Ser motivadoras e engajadoras
- Incluir estratégias de apoio e adaptações
"""

SYSTEM_PROMPT_PROGRESS_ANALYSIS = """
Você é um especialista em avaliação educacional e desenvolvimento infantil,
especializado em TEA. Analise o progresso do aluno com base nas avaliações
fornecidas e identifique:

- Padrões de desempenho
- Áreas de progresso
- Áreas que necessitam mais suporte
- Recomendações personalizadas
- Ajustes sugeridos nas estratégias de ensino

Seja objetivo, construtivo e focado no desenvolvimento positivo.
"""

SYSTEM_PROMPT_RECOMMENDATIONS = """
Você é um consultor educacional especializado em TEA. Com base no perfil
e histórico do aluno, forneça recomendações práticas e acionáveis para:

- Próximas atividades
- Estratégias de ensino
- Áreas a serem trabalhadas
- Recursos educacionais
- Envolvimento familiar

Suas recomendações devem ser específicas, práticas e baseadas em evidências.
"""


# ============================================================================
# API Response Formats
# ============================================================================


class ResponseStatus(str, Enum):
    """Standard API response statuses."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


# ============================================================================
# Default Values
# ============================================================================

DEFAULT_USER_AVATAR = "/static/images/default-avatar.png"
DEFAULT_STUDENT_AVATAR = "/static/images/default-student.png"
DEFAULT_ACTIVITY_IMAGE = "/static/images/default-activity.png"


# ============================================================================
# Feature Flags
# ============================================================================

FEATURE_FLAGS = {
    "ENABLE_EMAIL_NOTIFICATIONS": False,  # TODO: Implement email service
    "ENABLE_PARENT_PORTAL": False,  # TODO: Future feature
    "ENABLE_REPORT_GENERATION": False,  # TODO: Implement PDF reports
    "ENABLE_ACTIVITY_SHARING": False,  # TODO: Teacher collaboration
    "ENABLE_GAMIFICATION": False,  # TODO: Badges and achievements
    "ENABLE_VIDEO_ACTIVITIES": False,  # TODO: Video content support
}


# ============================================================================
# Logging
# ============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ============================================================================
# Date/Time Formats
# ============================================================================

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATETIME_FORMAT_ISO = "%Y-%m-%dT%H:%M:%S.%fZ"


# ============================================================================
# Timezone
# ============================================================================

DEFAULT_TIMEZONE = "America/Sao_Paulo"


# ============================================================================
# Helper Functions
# ============================================================================


def get_activity_types() -> List[str]:
    """Get list of all activity types."""
    return [activity_type.value for activity_type in ActivityType]


def get_difficulty_levels() -> List[str]:
    """Get list of all difficulty levels."""
    return [level.value for level in DifficultyLevel]


def get_user_roles() -> List[str]:
    """Get list of all user roles."""
    return [role.value for role in UserRole]


def get_engagement_levels() -> List[str]:
    """Get list of all engagement levels."""
    return [level.value for level in EngagementLevel]


def get_completion_statuses() -> List[str]:
    """Get list of all completion statuses."""
    return [status.value for status in CompletionStatus]
