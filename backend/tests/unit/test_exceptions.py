"""
Unit tests for custom exceptions.

Tests all custom exception classes and the handle_exception helper.
"""

from fastapi import HTTPException, status

# Import custom exceptions:
# Base exception; Authentication & Authorization; Resource Not Found; Validation;
# Business Logic; External Services; File Upload; Rate Limiting; Data Integrity; Configuration; Helper function
from app.core.exceptions import (
    ActivityNotFoundError,
    AssessmentNotFoundError,
    AuthenticationError,
    AWSError,
    CacheError,
    ConfigurationError,
    DatabaseError,
    DataIntegrityError,
    DuplicateResourceError,
    EduAutismoException,
    EmailAlreadyExistsError,
    EmailServiceError,
    ExpiredTokenError,
    ExternalServiceError,
    FileNotFoundError,
    FileTooLargeError,
    FileUploadError,
    ForeignKeyViolationError,
    InactiveUserError,
    InvalidAgeError,
    InvalidCredentialsError,
    InvalidDurationError,
    InvalidEmailError,
    InvalidFileTypeError,
    InvalidTokenError,
    MissingConfigurationError,
    OpenAIError,
    PermissionDeniedError,
    RateLimitExceededError,
    ResourceLimitExceededError,
    ResourceNotFoundError,
    StudentNotFoundError,
    UserNotFoundError,
    ValidationError,
    WeakPasswordError,
    handle_exception,
)


class TestBaseException:
    """Tests for EduAutismoException base class."""

    def test_base_exception_default_initialization(self):
        """Test base exception with default values."""
        exc = EduAutismoException("Test error")

        assert exc.message == "Test error"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.details == {}
        assert str(exc) == "Test error"

    def test_base_exception_with_custom_status_code(self):
        """Test base exception with custom status code."""
        exc = EduAutismoException("Custom error", status_code=status.HTTP_400_BAD_REQUEST)

        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_base_exception_with_details(self):
        """Test base exception with details."""
        details = {"field": "email", "value": "test@example.com"}
        exc = EduAutismoException("Error with details", details=details)

        assert exc.details == details

    def test_to_http_exception(self):
        """Test conversion to HTTPException."""
        exc = EduAutismoException(
            "Test error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"extra": "info"},
        )

        http_exc = exc.to_http_exception()

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert http_exc.detail == {
            "message": "Test error",
            "details": {"extra": "info"},
        }


class TestAuthenticationExceptions:
    """Tests for authentication and authorization exceptions."""

    def test_authentication_error_default(self):
        """Test AuthenticationError with default message."""
        exc = AuthenticationError()

        assert exc.message == "Authentication failed"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        exc = AuthenticationError("Custom auth error")

        assert exc.message == "Custom auth error"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_credentials_error(self):
        """Test InvalidCredentialsError."""
        exc = InvalidCredentialsError()

        assert exc.message == "Email ou senha incorretos"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.details["error_code"] == "INVALID_CREDENTIALS"

    def test_invalid_token_error_default(self):
        """Test InvalidTokenError with default message."""
        exc = InvalidTokenError()

        assert exc.message == "Token inválido ou expirado"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.details["error_code"] == "INVALID_TOKEN"

    def test_invalid_token_error_custom_message(self):
        """Test InvalidTokenError with custom message."""
        exc = InvalidTokenError("Token malformado")

        assert exc.message == "Token malformado"
        assert exc.details["error_code"] == "INVALID_TOKEN"

    def test_expired_token_error(self):
        """Test ExpiredTokenError."""
        exc = ExpiredTokenError()

        assert exc.message == "Token expirado. Por favor, faça login novamente"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.details["error_code"] == "EXPIRED_TOKEN"

    def test_inactive_user_error(self):
        """Test InactiveUserError."""
        exc = InactiveUserError()

        assert exc.message == "Conta de usuário inativa. Entre em contato com o administrador"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.details["error_code"] == "USER_INACTIVE"

    def test_permission_denied_error_default(self):
        """Test PermissionDeniedError with default message."""
        exc = PermissionDeniedError()

        assert exc.message == "Permissão negada"
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.details["error_code"] == "PERMISSION_DENIED"
        assert "resource" not in exc.details

    def test_permission_denied_error_with_resource(self):
        """Test PermissionDeniedError with resource specified."""
        exc = PermissionDeniedError(message="Você não pode acessar este recurso", resource="student")

        assert exc.message == "Você não pode acessar este recurso"
        assert exc.details["resource"] == "student"


class TestResourceNotFoundExceptions:
    """Tests for resource not found exceptions."""

    def test_resource_not_found_without_id(self):
        """Test ResourceNotFoundError without ID."""
        exc = ResourceNotFoundError("Aluno")

        assert exc.message == "Aluno não encontrado"
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.details["resource_type"] == "Aluno"
        assert exc.details["resource_id"] is None

    def test_resource_not_found_with_id(self):
        """Test ResourceNotFoundError with ID."""
        exc = ResourceNotFoundError("Aluno", "123")

        assert exc.message == "Aluno não encontrado: 123"
        assert exc.details["resource_type"] == "Aluno"
        assert exc.details["resource_id"] == "123"

    def test_user_not_found_error(self):
        """Test UserNotFoundError."""
        exc = UserNotFoundError("user-123")

        assert "Usuário não encontrado: user-123" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_student_not_found_error(self):
        """Test StudentNotFoundError."""
        exc = StudentNotFoundError("student-456")

        assert "Aluno não encontrado: student-456" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_activity_not_found_error(self):
        """Test ActivityNotFoundError."""
        exc = ActivityNotFoundError("activity-789")

        assert "Atividade não encontrado: activity-789" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_assessment_not_found_error(self):
        """Test AssessmentNotFoundError."""
        exc = AssessmentNotFoundError()

        assert "Avaliação não encontrado" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND

    def test_file_not_found_error(self):
        """Test FileNotFoundError."""
        exc = FileNotFoundError("/path/to/file.pdf")

        assert "Arquivo não encontrado: /path/to/file.pdf" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND


class TestValidationExceptions:
    """Tests for validation exceptions."""

    def test_validation_error_minimal(self):
        """Test ValidationError with minimal arguments."""
        exc = ValidationError("Campo inválido")

        assert exc.message == "Campo inválido"
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.details["error_code"] == "VALIDATION_ERROR"
        assert "field" not in exc.details
        assert "value" not in exc.details

    def test_validation_error_with_field(self):
        """Test ValidationError with field."""
        exc = ValidationError("Email inválido", field="email")

        assert exc.details["field"] == "email"

    def test_validation_error_with_value(self):
        """Test ValidationError with value."""
        exc = ValidationError("Valor inválido", field="age", value=150)

        assert exc.details["field"] == "age"
        assert exc.details["value"] == "150"

    def test_invalid_email_error(self):
        """Test InvalidEmailError."""
        exc = InvalidEmailError("not-an-email")

        assert exc.message == "Formato de email inválido"
        assert exc.details["field"] == "email"
        assert exc.details["value"] == "not-an-email"

    def test_weak_password_error(self):
        """Test WeakPasswordError."""
        requirements = ["letra maiúscula", "caractere especial"]
        exc = WeakPasswordError(requirements)

        assert "letra maiúscula" in exc.message
        assert "caractere especial" in exc.message
        assert exc.details["field"] == "password"

    def test_invalid_age_error(self):
        """Test InvalidAgeError."""
        exc = InvalidAgeError(age=200, min_age=6, max_age=18)

        assert "6 e 18 anos" in exc.message
        assert exc.details["field"] == "age"
        assert exc.details["value"] == "200"

    def test_invalid_duration_error(self):
        """Test InvalidDurationError."""
        exc = InvalidDurationError(duration=500, min_duration=10, max_duration=120)

        assert "10 e 120 minutos" in exc.message
        assert exc.details["field"] == "duration_minutes"
        assert exc.details["value"] == "500"


class TestBusinessLogicExceptions:
    """Tests for business logic exceptions."""

    def test_email_already_exists_error(self):
        """Test EmailAlreadyExistsError."""
        exc = EmailAlreadyExistsError("test@example.com")

        assert exc.message == "Este email já está cadastrado"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["error_code"] == "EMAIL_ALREADY_EXISTS"
        assert exc.details["email"] == "test@example.com"

    def test_duplicate_resource_error(self):
        """Test DuplicateResourceError."""
        exc = DuplicateResourceError("Aluno", "ALU-001")

        assert "Aluno já existe: ALU-001" in exc.message
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.details["error_code"] == "DUPLICATE_RESOURCE"
        assert exc.details["resource_type"] == "Aluno"
        assert exc.details["identifier"] == "ALU-001"

    def test_resource_limit_exceeded_error(self):
        """Test ResourceLimitExceededError."""
        exc = ResourceLimitExceededError("alunos", 100)

        assert "Limite de alunos excedido: máximo 100" in exc.message
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["error_code"] == "RESOURCE_LIMIT_EXCEEDED"
        assert exc.details["resource_type"] == "alunos"
        assert exc.details["limit"] == 100


class TestExternalServiceExceptions:
    """Tests for external service exceptions."""

    def test_external_service_error_without_original(self):
        """Test ExternalServiceError without original exception."""
        exc = ExternalServiceError("OpenAI", "Rate limit exceeded")

        assert "Erro no serviço OpenAI: Rate limit exceeded" in exc.message
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.details["error_code"] == "EXTERNAL_SERVICE_ERROR"
        assert exc.details["service"] == "OpenAI"
        assert "original_error" not in exc.details

    def test_external_service_error_with_original(self):
        """Test ExternalServiceError with original exception."""
        original = ValueError("Connection timeout")
        exc = ExternalServiceError("Database", "Connection failed", original)

        assert "Erro no serviço Database: Connection failed" in exc.message
        assert exc.details["service"] == "Database"
        assert exc.details["original_error"] == "Connection timeout"

    def test_openai_error(self):
        """Test OpenAIError."""
        exc = OpenAIError("Rate limit exceeded")

        assert "Erro no serviço OpenAI" in exc.message
        assert exc.details["service"] == "OpenAI"

    def test_database_error(self):
        """Test DatabaseError."""
        original = Exception("Connection lost")
        exc = DatabaseError("Query failed", original)

        assert "Erro no serviço Database" in exc.message
        assert exc.details["service"] == "Database"
        assert exc.details["original_error"] == "Connection lost"

    def test_cache_error(self):
        """Test CacheError."""
        exc = CacheError("Redis unavailable")

        assert "Erro no serviço Cache (Redis)" in exc.message
        assert exc.details["service"] == "Cache (Redis)"

    def test_email_service_error(self):
        """Test EmailServiceError."""
        exc = EmailServiceError("SMTP connection failed")

        assert "Erro no serviço Email" in exc.message
        assert exc.details["service"] == "Email"

    def test_aws_error(self):
        """Test AWSError."""
        exc = AWSError("S3 bucket not found")

        assert "Erro no serviço AWS" in exc.message
        assert exc.details["service"] == "AWS"


class TestFileUploadExceptions:
    """Tests for file upload exceptions."""

    def test_file_upload_error_without_filename(self):
        """Test FileUploadError without filename."""
        exc = FileUploadError("Upload failed")

        assert exc.message == "Upload failed"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["error_code"] == "FILE_UPLOAD_ERROR"
        assert "filename" not in exc.details

    def test_file_upload_error_with_filename(self):
        """Test FileUploadError with filename."""
        exc = FileUploadError("Upload failed", filename="document.pdf")

        assert exc.details["filename"] == "document.pdf"

    def test_file_too_large_error(self):
        """Test FileTooLargeError."""
        exc = FileTooLargeError(filename="bigfile.pdf", size_mb=25.5, max_size_mb=10)

        assert "25.50MB" in exc.message
        assert "máximo: 10MB" in exc.message
        assert exc.details["filename"] == "bigfile.pdf"

    def test_invalid_file_type_error(self):
        """Test InvalidFileTypeError."""
        exc = InvalidFileTypeError("document.exe", ["pdf", "docx", "txt"])

        assert "Tipo de arquivo inválido" in exc.message
        assert "pdf, docx, txt" in exc.message
        assert exc.details["filename"] == "document.exe"


class TestRateLimitExceptions:
    """Tests for rate limiting exceptions."""

    def test_rate_limit_exceeded_error(self):
        """Test RateLimitExceededError."""
        exc = RateLimitExceededError(limit=100, window="minuto")

        assert "100 requisições por minuto" in exc.message
        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert exc.details["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert exc.details["limit"] == 100
        assert exc.details["window"] == "minuto"


class TestDataIntegrityExceptions:
    """Tests for data integrity exceptions."""

    def test_data_integrity_error_without_constraint(self):
        """Test DataIntegrityError without constraint."""
        exc = DataIntegrityError("Integrity violation")

        assert exc.message == "Integrity violation"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["error_code"] == "DATA_INTEGRITY_ERROR"
        assert "constraint" not in exc.details

    def test_data_integrity_error_with_constraint(self):
        """Test DataIntegrityError with constraint."""
        exc = DataIntegrityError("Unique constraint violated", constraint="unique_email")

        assert exc.details["constraint"] == "unique_email"

    def test_foreign_key_violation_error(self):
        """Test ForeignKeyViolationError."""
        exc = ForeignKeyViolationError(parent_resource="professor", child_resource="alunos")

        assert "Não é possível deletar professor" in exc.message
        assert "existem alunos associados" in exc.message
        assert exc.details["constraint"] == "foreign_key"


class TestConfigurationExceptions:
    """Tests for configuration exceptions."""

    def test_configuration_error_without_key(self):
        """Test ConfigurationError without config key."""
        exc = ConfigurationError("Configuration invalid")

        assert exc.message == "Configuration invalid"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.details["error_code"] == "CONFIGURATION_ERROR"
        assert "config_key" not in exc.details

    def test_configuration_error_with_key(self):
        """Test ConfigurationError with config key."""
        exc = ConfigurationError("Invalid value", config_key="DATABASE_URL")

        assert exc.details["config_key"] == "DATABASE_URL"

    def test_missing_configuration_error(self):
        """Test MissingConfigurationError."""
        exc = MissingConfigurationError("OPENAI_API_KEY")

        assert "Configuração obrigatória ausente: OPENAI_API_KEY" in exc.message
        assert exc.details["config_key"] == "OPENAI_API_KEY"


class TestHandleExceptionHelper:
    """Tests for handle_exception helper function."""

    def test_handle_eduautismo_exception(self):
        """Test handling of EduAutismoException."""
        exc = StudentNotFoundError("student-123")
        http_exc = handle_exception(exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert "Aluno não encontrado" in http_exc.detail["message"]

    def test_handle_value_error(self):
        """Test handling of ValueError."""
        exc = ValueError("Invalid value provided")
        http_exc = handle_exception(exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid value provided" in http_exc.detail["message"]

    def test_handle_key_error(self):
        """Test handling of KeyError."""
        exc = KeyError("missing_field")
        http_exc = handle_exception(exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert "Key not found" in http_exc.detail["message"]

    def test_handle_generic_exception(self):
        """Test handling of generic exception."""
        exc = RuntimeError("Something went wrong")
        http_exc = handle_exception(exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert http_exc.detail["message"] == "Internal server error"
        assert http_exc.detail["error_type"] == "RuntimeError"
