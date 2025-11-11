"""
Schemas Package - EduAutismo IA

Exports all Pydantic schemas for API validation.
"""

# Activity schemas
from app.schemas.activity import (ActivityCreate, ActivityFilterParams,
                                  ActivityGenerate, ActivityListResponse,
                                  ActivityResponse, ActivityUpdate)
# Assessment schemas
from app.schemas.assessment import (AssessmentCreate, AssessmentFilterParams,
                                    AssessmentListResponse, AssessmentResponse,
                                    AssessmentUpdate, ProgressAnalysisRequest,
                                    ProgressAnalysisResponse)
# Common schemas
from app.schemas.common import (BaseResponseSchema, BaseSchema,
                                BulkDeleteRequest, BulkDeleteResponse,
                                ComponentHealth, CountResponse,
                                DateRangeFilter, DetailedHealthCheckResponse,
                                ErrorDetail, ErrorResponse, FileUploadResponse,
                                HealthCheckResponse, MessageResponse,
                                PaginatedResponse, PaginationParams,
                                SearchFilter, StatsResponse, SuccessResponse,
                                TimestampSchema, Token, TokenRefresh,
                                TokenResponse, UUIDSchema,
                                ValidationErrorResponse)
# Student schemas
from app.schemas.student import (StudentCreate, StudentListResponse,
                                 StudentResponse, StudentUpdate)
# User schemas
from app.schemas.user import (PasswordChange, PasswordReset,
                              PasswordResetConfirm, UserAdminUpdate,
                              UserDetailResponse, UserListResponse, UserLogin,
                              UserRegister, UserResponse, UserUpdate)

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
