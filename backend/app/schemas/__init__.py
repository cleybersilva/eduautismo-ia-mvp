"""
Schemas Package - EduAutismo IA

Exports all Pydantic schemas for API validation.
"""

# Common schemas
from backend.app.schemas.common import (
    BaseSchema,
    BaseResponseSchema,
    TimestampSchema,
    UUIDSchema,
    PaginationParams,
    PaginatedResponse,
    MessageResponse,
    SuccessResponse,
    ErrorDetail,
    ErrorResponse,
    ValidationErrorResponse,
    ComponentHealth,
    HealthCheckResponse,
    DetailedHealthCheckResponse,
    Token,
    TokenRefresh,
    TokenResponse,
    FileUploadResponse,
    DateRangeFilter,
    SearchFilter,
    BulkDeleteRequest,
    BulkDeleteResponse,
    CountResponse,
    StatsResponse,
)

# User schemas
from backend.app.schemas.user import (
    UserRegister,
    UserLogin,
    UserUpdate,
    PasswordReset,
    PasswordResetConfirm,
    PasswordChange,
    UserResponse,
    UserDetailResponse,
    UserListResponse,
    UserAdminUpdate,
)

# Student schemas
from backend.app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
)

# Activity schemas
from backend.app.schemas.activity import (
    ActivityGenerate,
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
    ActivityFilterParams,
)

# Assessment schemas
from backend.app.schemas.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AssessmentResponse,
    AssessmentListResponse,
    AssessmentFilterParams,
    ProgressAnalysisRequest,
    ProgressAnalysisResponse,
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
]
