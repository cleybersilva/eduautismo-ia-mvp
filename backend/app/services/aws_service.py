"""
AWS Service - EduAutismo IA

Serviço para integração com AWS S3 e KMS.
Gerencia upload, download, deleção de arquivos e criptografia.
"""

import mimetypes
from datetime import datetime, timedelta
from typing import BinaryIO, Dict, List, Optional, Tuple
from uuid import uuid4

import aioboto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import settings
from app.core.exceptions import AWSError
from app.core.exceptions import FileNotFoundError as CustomFileNotFoundError
from app.core.exceptions import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AWSService:
    """Serviço para operações com AWS S3 e KMS."""

    # Tamanhos máximos permitidos (em bytes)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20MB

    # Tipos de arquivo permitidos
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg"}

    # Prefixos de diretórios no S3
    STUDENT_DOCS_PREFIX = "students/documents"
    STUDENT_IMAGES_PREFIX = "students/images"
    ACTIVITY_MATERIALS_PREFIX = "activities/materials"
    ASSESSMENT_FILES_PREFIX = "assessments/files"

    def __init__(self):
        """Inicializa o serviço AWS."""
        self.session = aioboto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_S3_BUCKET

    async def upload_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        prefix: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        encrypt: bool = True,
    ) -> Tuple[str, str]:
        """
        Faz upload de arquivo para S3.

        Args:
            file_obj: Objeto arquivo (file-like object)
            filename: Nome do arquivo
            prefix: Prefixo do caminho (diretório)
            content_type: Tipo MIME do arquivo
            metadata: Metadados customizados
            encrypt: Se deve criptografar com KMS

        Returns:
            Tupla (s3_key, url) - Chave S3 e URL do arquivo

        Raises:
            ValidationError: Se arquivo inválido
            AWSError: Se erro ao fazer upload
        """
        try:
            # Gerar nome único para o arquivo
            file_extension = filename.split(".")[-1] if "." in filename else ""
            unique_filename = f"{uuid4()}.{file_extension}" if file_extension else str(uuid4())
            s3_key = f"{prefix}/{unique_filename}"

            # Detectar content type se não fornecido
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = "application/octet-stream"

            # Validar tipo de arquivo
            await self._validate_file_type(content_type, prefix)

            # Ler conteúdo do arquivo
            file_content = file_obj.read()

            # Validar tamanho
            file_size = len(file_content)
            await self._validate_file_size(file_size, content_type)

            # Preparar metadados
            upload_metadata = {
                "original_filename": filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "content_type": content_type,
                "file_size": str(file_size),
            }
            if metadata:
                upload_metadata.update(metadata)

            # Configurar criptografia
            extra_args = {
                "ContentType": content_type,
                "Metadata": upload_metadata,
            }

            if encrypt:
                extra_args["ServerSideEncryption"] = "aws:kms"
                # Se tiver KMS key ID configurado, adicionar
                # extra_args["SSEKMSKeyId"] = settings.AWS_KMS_KEY_ID

            # Upload para S3
            async with self.session.client("s3") as s3_client:
                await s3_client.put_object(Bucket=self.bucket_name, Key=s3_key, Body=file_content, **extra_args)

            logger.info(
                f"File uploaded successfully: {s3_key}",
                extra={
                    "s3_key": s3_key,
                    "file_name": filename,
                    "size": file_size,
                    "content_type": content_type,
                },
            )

            # Construir URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

            return s3_key, url

        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS error uploading file: {e}")
            raise AWSError(f"Failed to upload file: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {e}")
            raise AWSError(f"Unexpected error uploading file: {str(e)}") from e

    async def download_file(self, s3_key: str) -> Tuple[bytes, Dict[str, str]]:
        """
        Baixa arquivo do S3.

        Args:
            s3_key: Chave do arquivo no S3

        Returns:
            Tupla (file_content, metadata) - Conteúdo e metadados

        Raises:
            CustomFileNotFoundError: Se arquivo não encontrado
            AWSError: Se erro ao baixar
        """
        try:
            async with self.session.client("s3") as s3_client:
                response = await s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)

                # Ler conteúdo do arquivo
                async with response["Body"] as stream:
                    file_content = await stream.read()

                # Extrair metadados
                metadata = response.get("Metadata", {})

                logger.info(
                    f"File downloaded successfully: {s3_key}",
                    extra={"s3_key": s3_key, "size": len(file_content)},
                )

                return file_content, metadata

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.warning(f"File not found: {s3_key}")
                raise CustomFileNotFoundError(f"File not found: {s3_key}") from e
            logger.error(f"AWS error downloading file: {e}")
            raise AWSError(f"Failed to download file: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error downloading file: {e}")
            raise AWSError(f"Unexpected error downloading file: {str(e)}") from e

    async def delete_file(self, s3_key: str) -> bool:
        """
        Deleta arquivo do S3.

        Args:
            s3_key: Chave do arquivo no S3

        Returns:
            True se deletado com sucesso

        Raises:
            AWSError: Se erro ao deletar
        """
        try:
            async with self.session.client("s3") as s3_client:
                await s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)

            logger.info(f"File deleted successfully: {s3_key}", extra={"s3_key": s3_key})
            return True

        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS error deleting file: {e}")
            raise AWSError(f"Failed to delete file: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {e}")
            raise AWSError(f"Unexpected error deleting file: {str(e)}") from e

    async def generate_presigned_url(self, s3_key: str, expiration: int = 3600, download: bool = False) -> str:
        """
        Gera URL presignada para acesso temporário ao arquivo.

        Args:
            s3_key: Chave do arquivo no S3
            expiration: Tempo de expiração em segundos (padrão: 1 hora)
            download: Se deve forçar download (attachment)

        Returns:
            URL presignada

        Raises:
            AWSError: Se erro ao gerar URL
        """
        try:
            params = {"Bucket": self.bucket_name, "Key": s3_key}

            # Forçar download se solicitado
            if download:
                params["ResponseContentDisposition"] = "attachment"

            async with self.session.client("s3") as s3_client:
                url = await s3_client.generate_presigned_url("get_object", Params=params, ExpiresIn=expiration)

            logger.info(
                f"Presigned URL generated: {s3_key}",
                extra={"s3_key": s3_key, "expiration": expiration},
            )

            return url

        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS error generating presigned URL: {e}")
            raise AWSError(f"Failed to generate presigned URL: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {e}")
            raise AWSError(f"Unexpected error generating presigned URL: {str(e)}") from e

    async def list_files(self, prefix: str, max_keys: int = 100) -> List[Dict[str, any]]:
        """
        Lista arquivos em um prefixo (diretório).

        Args:
            prefix: Prefixo para filtrar arquivos
            max_keys: Máximo de arquivos a retornar

        Returns:
            Lista de dicionários com informações dos arquivos

        Raises:
            AWSError: Se erro ao listar
        """
        try:
            async with self.session.client("s3") as s3_client:
                response = await s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix, MaxKeys=max_keys)

            files = []
            for obj in response.get("Contents", []):
                files.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                        "etag": obj["ETag"],
                    }
                )

            logger.info(f"Listed {len(files)} files in prefix: {prefix}")
            return files

        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS error listing files: {e}")
            raise AWSError(f"Failed to list files: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            raise AWSError(f"Unexpected error listing files: {str(e)}") from e

    async def copy_file(self, source_key: str, destination_key: str) -> bool:
        """
        Copia arquivo dentro do S3.

        Args:
            source_key: Chave do arquivo de origem
            destination_key: Chave do arquivo de destino

        Returns:
            True se copiado com sucesso

        Raises:
            AWSError: Se erro ao copiar
        """
        try:
            copy_source = {"Bucket": self.bucket_name, "Key": source_key}

            async with self.session.client("s3") as s3_client:
                await s3_client.copy_object(CopySource=copy_source, Bucket=self.bucket_name, Key=destination_key)

            logger.info(
                f"File copied: {source_key} -> {destination_key}",
                extra={"source": source_key, "destination": destination_key},
            )
            return True

        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS error copying file: {e}")
            raise AWSError(f"Failed to copy file: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error copying file: {e}")
            raise AWSError(f"Unexpected error copying file: {str(e)}") from e

    async def get_file_metadata(self, s3_key: str) -> Dict[str, any]:
        """
        Obtém metadados de um arquivo.

        Args:
            s3_key: Chave do arquivo no S3

        Returns:
            Dicionário com metadados do arquivo

        Raises:
            CustomFileNotFoundError: Se arquivo não encontrado
            AWSError: Se erro ao obter metadados
        """
        try:
            async with self.session.client("s3") as s3_client:
                response = await s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)

            metadata = {
                "content_type": response.get("ContentType"),
                "content_length": response.get("ContentLength"),
                "last_modified": response.get("LastModified"),
                "etag": response.get("ETag"),
                "metadata": response.get("Metadata", {}),
                "encryption": response.get("ServerSideEncryption"),
            }

            return metadata

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise CustomFileNotFoundError(f"File not found: {s3_key}") from e
            logger.error(f"AWS error getting file metadata: {e}")
            raise AWSError(f"Failed to get file metadata: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error getting file metadata: {e}")
            raise AWSError(f"Unexpected error getting file metadata: {str(e)}") from e

    # ========== Métodos de Validação ==========

    async def _validate_file_type(self, content_type: str, prefix: str) -> None:
        """Valida tipo de arquivo baseado no prefixo."""
        allowed_types = set()

        if "images" in prefix:
            allowed_types = self.ALLOWED_IMAGE_TYPES
        elif "documents" in prefix:
            allowed_types = self.ALLOWED_DOCUMENT_TYPES
        elif "materials" in prefix:
            # Materiais podem ser imagens ou documentos
            allowed_types = self.ALLOWED_IMAGE_TYPES | self.ALLOWED_DOCUMENT_TYPES
        elif "audio" in prefix:
            allowed_types = self.ALLOWED_AUDIO_TYPES

        if allowed_types and content_type not in allowed_types:
            raise ValidationError(f"Invalid file type: {content_type}. " f"Allowed types: {', '.join(allowed_types)}")

    async def _validate_file_size(self, file_size: int, content_type: str) -> None:
        """Valida tamanho do arquivo."""
        max_size = self.MAX_FILE_SIZE

        if content_type in self.ALLOWED_IMAGE_TYPES:
            max_size = self.MAX_IMAGE_SIZE
        elif content_type in self.ALLOWED_DOCUMENT_TYPES:
            max_size = self.MAX_DOCUMENT_SIZE

        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise ValidationError(f"File size exceeds maximum allowed: {max_size_mb}MB")

        if file_size == 0:
            raise ValidationError("File is empty")

    # ========== Métodos de Conveniência ==========

    async def upload_student_document(
        self, file_obj: BinaryIO, filename: str, student_id: str, metadata: Optional[Dict] = None
    ) -> Tuple[str, str]:
        """Upload documento de aluno."""
        prefix = f"{self.STUDENT_DOCS_PREFIX}/{student_id}"
        if metadata is None:
            metadata = {}
        metadata["student_id"] = student_id
        return await self.upload_file(file_obj, filename, prefix, metadata=metadata)

    async def upload_student_image(
        self, file_obj: BinaryIO, filename: str, student_id: str, metadata: Optional[Dict] = None
    ) -> Tuple[str, str]:
        """Upload imagem de aluno."""
        prefix = f"{self.STUDENT_IMAGES_PREFIX}/{student_id}"
        if metadata is None:
            metadata = {}
        metadata["student_id"] = student_id
        return await self.upload_file(file_obj, filename, prefix, metadata=metadata)

    async def upload_activity_material(
        self, file_obj: BinaryIO, filename: str, activity_id: str, metadata: Optional[Dict] = None
    ) -> Tuple[str, str]:
        """Upload material de atividade."""
        prefix = f"{self.ACTIVITY_MATERIALS_PREFIX}/{activity_id}"
        if metadata is None:
            metadata = {}
        metadata["activity_id"] = activity_id
        return await self.upload_file(file_obj, filename, prefix, metadata=metadata)

    async def upload_assessment_file(
        self, file_obj: BinaryIO, filename: str, assessment_id: str, metadata: Optional[Dict] = None
    ) -> Tuple[str, str]:
        """Upload arquivo de avaliação."""
        prefix = f"{self.ASSESSMENT_FILES_PREFIX}/{assessment_id}"
        if metadata is None:
            metadata = {}
        metadata["assessment_id"] = assessment_id
        return await self.upload_file(file_obj, filename, prefix, metadata=metadata)


# Singleton instance
_aws_service = None


def get_aws_service() -> AWSService:
    """
    Retorna instância singleton do AWSService.

    Returns:
        Instância de AWSService
    """
    global _aws_service
    if _aws_service is None:
        _aws_service = AWSService()
    return _aws_service
