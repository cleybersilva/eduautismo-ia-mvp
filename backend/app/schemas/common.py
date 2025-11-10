"""
Common Schemas - EduAutismo IA

Reusable schema definitions for API requests and responses.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Base Schemas
# ============================================================================

class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode (was orm_mode in V1)
        populate_by_name=True,  # Allow populating by field name
        use_enum_values=True,  # Use enum values instead of enum objects
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UUIDSchema(BaseSchema):
    """Schema with UUID identifier."""

    id: UUID = Field(..., description="Unique identifier")


class BaseResponseSchema(UUIDSchema, TimestampSchema):
    """Base response schema with ID and timestamps."""

    pass


# ============================================================================
# Pagination
# ============================================================================

class PaginationParams(BaseSchema):
    """Query parameters for pagination."""

    skip: int = Field(
        default=0,
        ge=0,
        description="Number of records to skip",
        examples=[0, 20, 40],
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return",
        examples=[10, 20, 50],
    )


T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    skip: int = Field(..., ge=0, description="Number of items skipped")
    limit: int = Field(..., ge=1, description="Maximum items per page")
    has_more: bool = Field(..., description="Whether there are more items")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int = 0,
        limit: int = 20,
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response.

        Args:
            items: List of items
            total: Total count
            skip: Offset
            limit: Limit

        Returns:
            PaginatedResponse instance
        """
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total,
        )


# ============================================================================
# API Responses
# ============================================================================

class MessageResponse(BaseSchema):
    """Simple message response."""

    message: str = Field(..., description="Response message")


class SuccessResponse(MessageResponse):
    """Success response with optional data."""

    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional data",
    )


class ErrorDetail(BaseSchema):
    """Error detail information."""

    field: Optional[str] = Field(default=None, description="Field with error")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class ErrorResponse(BaseSchema):
    """Error response."""

    message: str = Field(..., description="Error message")
    details: Optional[List[ErrorDetail]] = Field(
        default=None,
        description="Detailed error information",
    )
    error_code: Optional[str] = Field(
        default=None,
        description="Error code for client handling",
    )


class ValidationErrorResponse(ErrorResponse):
    """Validation error response (422)."""

    message: str = Field(default="Validation error")
    details: List[ErrorDetail] = Field(..., description="Validation errors")


# ============================================================================
# Health Check
# ============================================================================

class ComponentHealth(BaseSchema):
    """Health status of a component."""

    status: str = Field(
        ...,
        description="Component status",
        examples=["up", "down", "degraded"],
    )
    latency_ms: Optional[float] = Field(
        default=None,
        description="Response latency in milliseconds",
        ge=0,
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if component is down",
    )


class HealthCheckResponse(BaseSchema):
    """Health check response."""

    status: str = Field(
        ...,
        description="Overall status",
        examples=["healthy", "degraded", "unhealthy"],
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Check timestamp",
    )
    version: Optional[str] = Field(
        default=None,
        description="API version",
    )
    environment: Optional[str] = Field(
        default=None,
        description="Environment name",
    )


class DetailedHealthCheckResponse(HealthCheckResponse):
    """Detailed health check with component statuses."""

    components: Dict[str, ComponentHealth] = Field(
        ...,
        description="Status of individual components",
    )


# ============================================================================
# Authentication
# ============================================================================

class Token(BaseSchema):
    """JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(
        default="bearer",
        description="Token type",
    )


class TokenRefresh(BaseSchema):
    """Token refresh request."""

    refresh_token: str = Field(
        ...,
        description="Refresh token to exchange for new access token",
        min_length=10,
    )


class TokenResponse(BaseSchema):
    """Token response after refresh."""

    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


# ============================================================================
# File Upload
# ============================================================================

class FileUploadResponse(BaseSchema):
    """File upload response."""

    filename: str = Field(..., description="Uploaded filename")
    url: str = Field(..., description="File URL")
    size_bytes: int = Field(..., ge=0, description="File size in bytes")
    content_type: str = Field(..., description="MIME type")


# ============================================================================
# Filters
# ============================================================================

class DateRangeFilter(BaseSchema):
    """Date range filter."""

    start_date: Optional[datetime] = Field(
        default=None,
        description="Start date (inclusive)",
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="End date (inclusive)",
    )


class SearchFilter(BaseSchema):
    """Generic search filter."""

    query: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Search query",
    )


# ============================================================================
# Bulk Operations
# ============================================================================

class BulkDeleteRequest(BaseSchema):
    """Bulk delete request."""

    ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of IDs to delete",
    )


class BulkDeleteResponse(BaseSchema):
    """Bulk delete response."""

    deleted_count: int = Field(
        ...,
        ge=0,
        description="Number of items deleted",
    )
    failed_ids: Optional[List[UUID]] = Field(
        default=None,
        description="IDs that failed to delete",
    )


# ============================================================================
# Statistics
# ============================================================================

class CountResponse(BaseSchema):
    """Simple count response."""

    count: int = Field(..., ge=0, description="Count")


class StatsResponse(BaseSchema):
    """Generic statistics response."""

    total: int = Field(..., ge=0, description="Total count")
    stats: Dict[str, Any] = Field(
        ...,
        description="Statistical data",
    )
