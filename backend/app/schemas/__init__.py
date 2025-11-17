"""
Schemas Package - EduAutismo IA

Exports all Pydantic schemas for API validation.
"""

# Activity schemas
from app.schemas.activity import (
    ActivityCreate,
    ActivityFilterParams,
    ActivityGenerate,
    ActivityListResponse,
    ActivityResponse,
    ActivityUpdate,
)

# Assessment schemas
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentListResponse,
    AssessmentResponse,
    AssessmentUpdate,
    ProgressAnalysisRequest,
    ProgressAnalysisResponse,
)

# Common schemas
from app.schemas.common import (
    BaseResponseSchema,
    BaseSchema,
    BulkDeleteRequest,
    BulkDeleteResponse,
    ComponentHealth,
    CountResponse,
    DateRangeFilter,
    DetailedHealthCheckResponse,
    ErrorDetail,
    ErrorResponse,
    FileUploadResponse,
    HealthCheckResponse,
    MessageResponse,
    PaginatedResponse,
    PaginationParams,
    SearchFilter,
    StatsResponse,
    SuccessResponse,
    TimestampSchema,
    Token,
    TokenRefresh,
    TokenResponse,
    UUIDSchema,
    ValidationErrorResponse,
)

# Student schemas
from app.schemas.student import StudentCreate, StudentListResponse, StudentResponse, StudentUpdate

# User schemas
from app.schemas.user import (
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    UserAdminUpdate,
    UserDetailResponse,
    UserListResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    UserUpdate,
)

# Professional schemas
from app.schemas.professional import (
    ProfessionalCreate,
    ProfessionalFilter,
    ProfessionalListResponse,
    ProfessionalResponse,
    ProfessionalStatistics,
    ProfessionalSummary,
    ProfessionalUpdate,
)

# Observation schemas
from app.schemas.observation import (
    ObservationFilter,
    ObservationSummary,
    ObservationTimeline,
    ProfessionalObservationCreate,
    ProfessionalObservationListResponse,
    ProfessionalObservationResponse,
    ProfessionalObservationUpdate,
    ProfessionalObservationWithDetails,
)

# Intervention Plan schemas
from app.schemas.intervention_plan import (
    InterventionPlanCreate,
    InterventionPlanEffectiveness,
    InterventionPlanFilter,
    InterventionPlanListResponse,
    InterventionPlanResponse,
    InterventionPlanStatistics,
    InterventionPlanSummary,
    InterventionPlanUpdate,
    InterventionPlanWithDetails,
    ProgressNoteCreate,
)

# Social Emotional Indicator schemas
from app.schemas.socioemotional_indicator import (
    BulkIndicatorCreate,
    BulkIndicatorResponse,
    IndicatorComparison,
    IndicatorCorrelation,
    IndicatorFilter,
    IndicatorTrend,
    SocialEmotionalIndicatorCreate,
    SocialEmotionalIndicatorListResponse,
    SocialEmotionalIndicatorResponse,
    SocialEmotionalIndicatorUpdate,
    SocialEmotionalIndicatorWithDetails,
    SocialEmotionalProfile,
)

__all__ = [
    # Common
    "BaseSchema",
    "BaseResponseSchema",
    "TimestampSchema",
    "UUIDSchema",
    "PaginationParams",
    "PaginatedResponse",
    "MessageResponse",
    "SuccessResponse",
    "ErrorDetail",
    "ErrorResponse",
    "ValidationErrorResponse",
    "ComponentHealth",
    "HealthCheckResponse",
    "DetailedHealthCheckResponse",
    "Token",
    "TokenRefresh",
    "TokenResponse",
    "FileUploadResponse",
    "DateRangeFilter",
    "SearchFilter",
    "BulkDeleteRequest",
    "BulkDeleteResponse",
    "CountResponse",
    "StatsResponse",
    # User
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "PasswordReset",
    "PasswordResetConfirm",
    "PasswordChange",
    "UserResponse",
    "UserDetailResponse",
    "UserListResponse",
    "UserAdminUpdate",
    # Student
    "StudentCreate",
    "StudentUpdate",
    "StudentResponse",
    "StudentListResponse",
    # Activity
    "ActivityGenerate",
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityResponse",
    "ActivityListResponse",
    "ActivityFilterParams",
    # Assessment
    "AssessmentCreate",
    "AssessmentUpdate",
    "AssessmentResponse",
    "AssessmentListResponse",
    "AssessmentFilterParams",
    "ProgressAnalysisRequest",
    "ProgressAnalysisResponse",
    # Professional
    "ProfessionalCreate",
    "ProfessionalUpdate",
    "ProfessionalResponse",
    "ProfessionalListResponse",
    "ProfessionalSummary",
    "ProfessionalFilter",
    "ProfessionalStatistics",
    # Observation
    "ProfessionalObservationCreate",
    "ProfessionalObservationUpdate",
    "ProfessionalObservationResponse",
    "ProfessionalObservationWithDetails",
    "ProfessionalObservationListResponse",
    "ObservationFilter",
    "ObservationSummary",
    "ObservationTimeline",
    # Intervention Plan
    "InterventionPlanCreate",
    "InterventionPlanUpdate",
    "InterventionPlanResponse",
    "InterventionPlanWithDetails",
    "InterventionPlanListResponse",
    "InterventionPlanSummary",
    "InterventionPlanFilter",
    "InterventionPlanStatistics",
    "InterventionPlanEffectiveness",
    "ProgressNoteCreate",
    # Social Emotional Indicator
    "SocialEmotionalIndicatorCreate",
    "SocialEmotionalIndicatorUpdate",
    "SocialEmotionalIndicatorResponse",
    "SocialEmotionalIndicatorWithDetails",
    "SocialEmotionalIndicatorListResponse",
    "IndicatorFilter",
    "IndicatorTrend",
    "SocialEmotionalProfile",
    "IndicatorComparison",
    "IndicatorCorrelation",
    "BulkIndicatorCreate",
    "BulkIndicatorResponse",
]
