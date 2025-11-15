"""
Unit tests for AWS Service.

Tests S3 file operations, validation, and error handling.
"""

import io
from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError

from app.core.exceptions import AWSError, ValidationError
from app.services.aws_service import AWSService, get_aws_service


class TestAWSServiceInit:
    """Test AWS Service initialization."""

    def test_aws_service_init(self):
        """Test service initialization with default config."""
        service = AWSService()

        assert service.bucket_name is not None
        assert service.session is not None
        assert service.MAX_FILE_SIZE == 50 * 1024 * 1024
        assert service.MAX_IMAGE_SIZE == 10 * 1024 * 1024

    def test_get_aws_service_singleton(self):
        """Test get_aws_service returns singleton instance."""
        service1 = get_aws_service()
        service2 = get_aws_service()

        assert service1 is service2


class TestFileUpload:
    """Test file upload functionality."""

    @pytest.fixture
    def aws_service(self):
        """Create AWS service instance."""
        return AWSService()

    @pytest.fixture
    def sample_file(self):
        """Create sample file for upload."""
        content = b"Sample file content"
        file_obj = io.BytesIO(content)
        return file_obj

    @pytest.mark.asyncio
    async def test_upload_file_success(self, aws_service, sample_file):
        """Test successful file upload."""
        # Mock S3 client
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.put_object = AsyncMock()

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            s3_key, url = await aws_service.upload_file(
                file_obj=sample_file, filename="test.jpg", prefix="test-prefix", content_type="image/jpeg"
            )

        # Verify results
        assert s3_key.startswith("test-prefix/")
        assert s3_key.endswith(".jpg")
        assert "https://" in url
        assert aws_service.bucket_name in url

        # Verify S3 client called
        mock_s3_client.put_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_with_metadata(self, aws_service, sample_file):
        """Test file upload with custom metadata."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.put_object = AsyncMock()

        custom_metadata = {"student_id": str(uuid4()), "uploaded_by": "teacher123"}

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            s3_key, url = await aws_service.upload_file(
                file_obj=sample_file,
                filename="test.jpg",
                prefix="students/images",
                content_type="image/jpeg",
                metadata=custom_metadata,
            )

        # Verify metadata passed to S3
        call_kwargs = mock_s3_client.put_object.call_args[1]
        assert "Metadata" in call_kwargs
        assert "student_id" in call_kwargs["Metadata"]

    @pytest.mark.asyncio
    async def test_upload_file_with_encryption(self, aws_service, sample_file):
        """Test file upload with KMS encryption."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.put_object = AsyncMock()

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            await aws_service.upload_file(file_obj=sample_file, filename="test.pdf", prefix="documents", encrypt=True)

        # Verify encryption enabled
        call_kwargs = mock_s3_client.put_object.call_args[1]
        assert call_kwargs.get("ServerSideEncryption") == "aws:kms"

    @pytest.mark.asyncio
    async def test_upload_file_no_encryption(self, aws_service, sample_file):
        """Test file upload without encryption."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.put_object = AsyncMock()

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            await aws_service.upload_file(file_obj=sample_file, filename="test.pdf", prefix="documents", encrypt=False)

        # Verify encryption not in kwargs
        call_kwargs = mock_s3_client.put_object.call_args[1]
        assert "ServerSideEncryption" not in call_kwargs


class TestFileValidation:
    """Test file validation."""

    @pytest.fixture
    def aws_service(self):
        """Create AWS service instance."""
        return AWSService()

    @pytest.mark.asyncio
    async def test_validate_file_type_images(self, aws_service):
        """Test image file type validation."""
        # Valid image types
        await aws_service._validate_file_type("image/jpeg", "students/images")
        await aws_service._validate_file_type("image/png", "students/images")

        # Invalid type for images
        with pytest.raises(ValidationError, match="Invalid file type"):
            await aws_service._validate_file_type("application/pdf", "students/images")

    @pytest.mark.asyncio
    async def test_validate_file_type_documents(self, aws_service):
        """Test document file type validation."""
        # Valid document types
        await aws_service._validate_file_type("application/pdf", "students/documents")

        # Invalid type for documents
        with pytest.raises(ValidationError, match="Invalid file type"):
            await aws_service._validate_file_type("image/jpeg", "students/documents")

    @pytest.mark.asyncio
    async def test_validate_file_size_within_limit(self, aws_service):
        """Test file size validation within limits."""
        # Image within limit (10MB)
        await aws_service._validate_file_size(5 * 1024 * 1024, "image/jpeg")

        # Document within limit (20MB)
        await aws_service._validate_file_size(15 * 1024 * 1024, "application/pdf")

    @pytest.mark.asyncio
    async def test_validate_file_size_exceeds_limit(self, aws_service):
        """Test file size validation exceeds limit."""
        # Image too large (> 10MB)
        with pytest.raises(ValidationError, match="File size exceeds"):
            await aws_service._validate_file_size(15 * 1024 * 1024, "image/jpeg")

        # Document too large (> 20MB)
        with pytest.raises(ValidationError, match="File size exceeds"):
            await aws_service._validate_file_size(25 * 1024 * 1024, "application/pdf")

    @pytest.mark.asyncio
    async def test_validate_empty_file(self, aws_service):
        """Test empty file validation."""
        with pytest.raises(ValidationError, match="File is empty"):
            await aws_service._validate_file_size(0, "image/jpeg")


class TestFileDownload:
    """Test file download functionality."""

    @pytest.fixture
    def aws_service(self):
        """Create AWS service instance."""
        return AWSService()

    @pytest.mark.asyncio
    async def test_download_file_success(self, aws_service):
        """Test successful file download."""
        # Mock S3 response
        mock_body = AsyncMock()
        mock_body.__aenter__.return_value = mock_body
        mock_body.__aexit__.return_value = None
        mock_body.read = AsyncMock(return_value=b"File content")

        mock_response = {"Body": mock_body, "Metadata": {"original_filename": "test.jpg"}}

        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.get_object = AsyncMock(return_value=mock_response)

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            content, metadata = await aws_service.download_file("test-key")

        assert content == b"File content"
        assert metadata.get("original_filename") == "test.jpg"

    @pytest.mark.asyncio
    async def test_download_file_not_found(self, aws_service):
        """Test download non-existent file."""
        # Mock S3 client error
        error_response = {"Error": {"Code": "NoSuchKey", "Message": "Not found"}}
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.get_object = AsyncMock(side_effect=ClientError(error_response, "GetObject"))

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            # Should raise custom FileNotFoundError (imported from exceptions)
            with pytest.raises(Exception):  # Will be CustomFileNotFoundError
                await aws_service.download_file("non-existent-key")


class TestFileDelete:
    """Test file deletion functionality."""

    @pytest.fixture
    def aws_service(self):
        """Create AWS service instance."""
        return AWSService()

    @pytest.mark.asyncio
    async def test_delete_file_success(self, aws_service):
        """Test successful file deletion."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.delete_object = AsyncMock()

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            result = await aws_service.delete_file("test-key")

        assert result is True
        mock_s3_client.delete_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_file_error(self, aws_service):
        """Test file deletion with error."""
        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.delete_object = AsyncMock(side_effect=ClientError(error_response, "DeleteObject"))

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            with pytest.raises(AWSError, match="Failed to delete file"):
                await aws_service.delete_file("test-key")


class TestPresignedURL:
    """Test presigned URL generation."""

    @pytest.fixture
    def aws_service(self):
        """Create AWS service instance."""
        return AWSService()

    @pytest.mark.asyncio
    async def test_generate_presigned_url_success(self, aws_service):
        """Test presigned URL generation."""
        mock_url = "https://bucket.s3.amazonaws.com/file?signed=token"
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.generate_presigned_url = AsyncMock(return_value=mock_url)

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            url = await aws_service.generate_presigned_url("test-key", expiration=3600)

        assert url == mock_url
        mock_s3_client.generate_presigned_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_presigned_url_with_download(self, aws_service):
        """Test presigned URL with forced download."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.generate_presigned_url = AsyncMock(return_value="https://test.url")

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            await aws_service.generate_presigned_url("test-key", download=True)

        # Verify ResponseContentDisposition in params
        call_args = mock_s3_client.generate_presigned_url.call_args
        assert "Params" in call_args[1]
        assert "ResponseContentDisposition" in call_args[1]["Params"]


class TestListFiles:
    """Test file listing functionality."""

    @pytest.fixture
    def aws_service(self):
        """Create AWS service instance."""
        return AWSService()

    @pytest.mark.asyncio
    async def test_list_files_success(self, aws_service):
        """Test successful file listing."""
        mock_response = {
            "Contents": [
                {"Key": "prefix/file1.jpg", "Size": 1024, "LastModified": datetime.now(), "ETag": "etag1"},
                {"Key": "prefix/file2.jpg", "Size": 2048, "LastModified": datetime.now(), "ETag": "etag2"},
            ]
        }

        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.list_objects_v2 = AsyncMock(return_value=mock_response)

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            files = await aws_service.list_files("prefix", max_keys=10)

        assert len(files) == 2
        assert files[0]["key"] == "prefix/file1.jpg"
        assert files[0]["size"] == 1024
        assert files[1]["key"] == "prefix/file2.jpg"

    @pytest.mark.asyncio
    async def test_list_files_empty(self, aws_service):
        """Test listing with no files."""
        mock_response = {"Contents": []}

        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.list_objects_v2 = AsyncMock(return_value=mock_response)

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            files = await aws_service.list_files("empty-prefix")

        assert len(files) == 0


class TestConvenienceMethods:
    """Test convenience upload methods."""

    @pytest.fixture
    def aws_service(self):
        """Create AWS service instance."""
        return AWSService()

    @pytest.fixture
    def sample_file(self):
        """Create sample file."""
        return io.BytesIO(b"Sample content")

    @pytest.mark.asyncio
    async def test_upload_student_document(self, aws_service, sample_file):
        """Test upload_student_document convenience method."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.put_object = AsyncMock()

        student_id = str(uuid4())

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            s3_key, url = await aws_service.upload_student_document(sample_file, "document.pdf", student_id)

        # Verify correct prefix used
        assert f"students/documents/{student_id}" in s3_key

    @pytest.mark.asyncio
    async def test_upload_student_image(self, aws_service, sample_file):
        """Test upload_student_image convenience method."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.put_object = AsyncMock()

        student_id = str(uuid4())

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            s3_key, url = await aws_service.upload_student_image(sample_file, "photo.jpg", student_id)

        # Verify correct prefix used
        assert f"students/images/{student_id}" in s3_key

    @pytest.mark.asyncio
    async def test_upload_activity_material(self, aws_service, sample_file):
        """Test upload_activity_material convenience method."""
        mock_s3_client = AsyncMock()
        mock_s3_client.__aenter__.return_value = mock_s3_client
        mock_s3_client.__aexit__.return_value = None
        mock_s3_client.put_object = AsyncMock()

        activity_id = str(uuid4())

        with patch.object(aws_service.session, "client", return_value=mock_s3_client):
            s3_key, url = await aws_service.upload_activity_material(sample_file, "material.pdf", activity_id)

        # Verify correct prefix used
        assert f"activities/materials/{activity_id}" in s3_key
