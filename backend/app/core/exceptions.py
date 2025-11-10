"""
Custom Exceptions - EduAutismo IA

Centralized exception definitions for the application.
All custom exceptions provide consistent error handling and messaging.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


# ============================================================================
# Base Custom Exception
# ============================================================================

class EduAutismoException(Exception):
    """Base exception for all custom exceptions in the application."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_http_exception(self) -> HTTPException:
        """Convert to FastAPI HTTPException."""
        return HTTPException(
            status_code=self.status_code,
            detail={
                "message": self.message,
                "details": self.details,
            },
        )


# ============================================================================
# Authentication & Authorization Exceptions
# ============================================================================

class AuthenticationError(EduAutismoException):
    """Base authentication error."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid email or password."""

    def __init__(self):
        super().__init__(
            message="Email ou senha incorretos",
            details={"error_code": "INVALID_CREDENTIALS"},
        )


class InvalidTokenError(AuthenticationError):
    """Invalid or expired token."""

    def __init__(self, message: str = "Token inválido ou expirado"):
        super().__init__(
            message=message,
            details={"error_code": "INVALID_TOKEN"},
        )


class ExpiredTokenError(AuthenticationError):
    """Token has expired."""

    def __init__(self):
        super().__init__(
            message="Token expirado. Por favor, faça login novamente",
            details={"error_code": "EXPIRED_TOKEN"},
        )


class InactiveUserError(AuthenticationError):
    """User account is inactive."""

    def __init__(self):
        super().__init__(
            message="Conta de usuário inativa. Entre em contato com o administrador",
            details={"error_code": "USER_INACTIVE"},
        )


class PermissionDeniedError(EduAutismoException):
    """User doesn't have permission for this action."""

    def __init__(self, message: str = "Permissão negada", resource: Optional[str] = None):
        details = {"error_code": "PERMISSION_DENIED"}
        if resource:
            details["resource"] = resource

        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


# ============================================================================
# Resource Not Found Exceptions
# ============================================================================

class ResourceNotFoundError(EduAutismoException):
    """Base exception for resource not found errors."""

    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        message = f"{resource_type} não encontrado"
        if resource_id:
            message += f": {resource_id}"

        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={
                "error_code": "RESOURCE_NOT_FOUND",
                "resource_type": resource_type,
                "resource_id": resource_id,
            },
        )


class UserNotFoundError(ResourceNotFoundError):
    """User not found."""

    def __init__(self, user_id: Optional[str] = None):
        super().__init__(resource_type="Usuário", resource_id=user_id)


class StudentNotFoundError(ResourceNotFoundError):
    """Student not found."""

    def __init__(self, student_id: Optional[str] = None):
        super().__init__(resource_type="Aluno", resource_id=student_id)


class ActivityNotFoundError(ResourceNotFoundError):
    """Activity not found."""

    def __init__(self, activity_id: Optional[str] = None):
        super().__init__(resource_type="Atividade", resource_id=activity_id)


class AssessmentNotFoundError(ResourceNotFoundError):
    """Assessment not found."""

    def __init__(self, assessment_id: Optional[str] = None):
        super().__init__(resource_type="Avaliação", resource_id=assessment_id)


# ============================================================================
# Validation Exceptions
# ============================================================================

class ValidationError(EduAutismoException):
    """Base validation error."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        details = {"error_code": "VALIDATION_ERROR"}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class InvalidEmailError(ValidationError):
    """Invalid email format."""

    def __init__(self, email: str):
        super().__init__(
            message="Formato de email inválido",
            field="email",
            value=email,
        )


class WeakPasswordError(ValidationError):
    """Password doesn't meet security requirements."""

    def __init__(self, requirements: list[str]):
        super().__init__(
            message=f"Senha não atende aos requisitos: {', '.join(requirements)}",
            field="password",
        )


class InvalidAgeError(ValidationError):
    """Invalid age value."""

    def __init__(self, age: int, min_age: int, max_age: int):
        super().__init__(
            message=f"Idade deve estar entre {min_age} e {max_age} anos",
            field="age",
            value=age,
        )


class InvalidDurationError(ValidationError):
    """Invalid activity duration."""

    def __init__(self, duration: int, min_duration: int, max_duration: int):
        super().__init__(
            message=f"Duração deve estar entre {min_duration} e {max_duration} minutos",
            field="duration_minutes",
            value=duration,
        )


# ============================================================================
# Business Logic Exceptions
# ============================================================================

class EmailAlreadyExistsError(EduAutismoException):
    """Email is already registered."""

    def __init__(self, email: str):
        super().__init__(
            message="Este email já está cadastrado",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "error_code": "EMAIL_ALREADY_EXISTS",
                "email": email,
            },
        )


class DuplicateResourceError(EduAutismoException):
    """Resource already exists."""

    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} já existe: {identifier}",
            status_code=status.HTTP_409_CONFLICT,
            details={
                "error_code": "DUPLICATE_RESOURCE",
                "resource_type": resource_type,
                "identifier": identifier,
            },
        )


class ResourceLimitExceededError(EduAutismoException):
    """Resource limit exceeded."""

    def __init__(self, resource_type: str, limit: int):
        super().__init__(
            message=f"Limite de {resource_type} excedido: máximo {limit}",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "error_code": "RESOURCE_LIMIT_EXCEEDED",
                "resource_type": resource_type,
                "limit": limit,
            },
        )


# ============================================================================
# External Service Exceptions
# ============================================================================

class ExternalServiceError(EduAutismoException):
    """Base exception for external service errors."""

    def __init__(
        self,
        service_name: str,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        details = {
            "error_code": "EXTERNAL_SERVICE_ERROR",
            "service": service_name,
        }
        if original_error:
            details["original_error"] = str(original_error)

        super().__init__(
            message=f"Erro no serviço {service_name}: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class OpenAIError(ExternalServiceError):
    """OpenAI API error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            service_name="OpenAI",
            message=message,
            original_error=original_error,
        )


class DatabaseError(ExternalServiceError):
    """Database error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            service_name="Database",
            message=message,
            original_error=original_error,
        )


class CacheError(ExternalServiceError):
    """Cache service error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            service_name="Cache (Redis)",
            message=message,
            original_error=original_error,
        )


class EmailServiceError(ExternalServiceError):
    """Email service error."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            service_name="Email",
            message=message,
            original_error=original_error,
        )


# ============================================================================
# File Upload Exceptions
# ============================================================================

class FileUploadError(EduAutismoException):
    """Base file upload error."""

    def __init__(self, message: str, filename: Optional[str] = None):
        details = {"error_code": "FILE_UPLOAD_ERROR"}
        if filename:
            details["filename"] = filename

        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class FileTooLargeError(FileUploadError):
    """Uploaded file is too large."""

    def __init__(self, filename: str, size_mb: float, max_size_mb: int):
        super().__init__(
            message=f"Arquivo muito grande: {size_mb:.2f}MB (máximo: {max_size_mb}MB)",
            filename=filename,
        )


class InvalidFileTypeError(FileUploadError):
    """Invalid file type/extension."""

    def __init__(self, filename: str, allowed_types: list[str]):
        super().__init__(
            message=f"Tipo de arquivo inválido. Tipos permitidos: {', '.join(allowed_types)}",
            filename=filename,
        )


# ============================================================================
# Rate Limiting Exceptions
# ============================================================================

class RateLimitExceededError(EduAutismoException):
    """Rate limit exceeded."""

    def __init__(self, limit: int, window: str):
        super().__init__(
            message=f"Limite de requisições excedido: {limit} requisições por {window}",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "limit": limit,
                "window": window,
            },
        )


# ============================================================================
# Data Integrity Exceptions
# ============================================================================

class DataIntegrityError(EduAutismoException):
    """Data integrity violation."""

    def __init__(self, message: str, constraint: Optional[str] = None):
        details = {"error_code": "DATA_INTEGRITY_ERROR"}
        if constraint:
            details["constraint"] = constraint

        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ForeignKeyViolationError(DataIntegrityError):
    """Foreign key constraint violation."""

    def __init__(self, parent_resource: str, child_resource: str):
        super().__init__(
            message=f"Não é possível deletar {parent_resource} pois existem {child_resource} associados",
            constraint="foreign_key",
        )


# ============================================================================
# Configuration Exceptions
# ============================================================================

class ConfigurationError(EduAutismoException):
    """Configuration error."""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"error_code": "CONFIGURATION_ERROR"}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class MissingConfigurationError(ConfigurationError):
    """Required configuration is missing."""

    def __init__(self, config_key: str):
        super().__init__(
            message=f"Configuração obrigatória ausente: {config_key}",
            config_key=config_key,
        )


# ============================================================================
# Helper Functions
# ============================================================================

def handle_exception(exception: Exception) -> HTTPException:
    """
    Convert any exception to HTTPException.

    Args:
        exception: Exception to handle

    Returns:
        HTTPException with appropriate status code and message
    """
    if isinstance(exception, EduAutismoException):
        return exception.to_http_exception()

    # Handle standard Python exceptions
    if isinstance(exception, ValueError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(exception)},
        )

    if isinstance(exception, KeyError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": f"Key not found: {exception}"},
        )

    # Generic server error
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": "Internal server error",
            "error_type": type(exception).__name__,
        },
    )
