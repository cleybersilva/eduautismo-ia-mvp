"""
Professional Pydantic schemas - DTOs para profissionais.

Schemas de validação e serialização para profissionais do sistema multiprofissional.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.professional import ProfessionalRole


# ============================================================================
# CREATE SCHEMAS
# ============================================================================


class ProfessionalCreate(BaseModel):
    """Schema para criação de profissional."""

    name: str = Field(..., min_length=3, max_length=255, description="Nome completo do profissional")
    email: EmailStr = Field(..., description="Email profissional")
    role: ProfessionalRole = Field(..., description="Função/especialidade profissional")
    specialization: Optional[str] = Field(
        None, max_length=255, description="Especialização adicional"
    )
    license_number: Optional[str] = Field(None, max_length=100, description="Número de registro profissional")
    organization: str = Field(..., min_length=3, max_length=255, description="Instituição/organização")
    phone: Optional[str] = Field(None, max_length=20, description="Telefone de contato")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dra. Maria Silva",
                "email": "maria.silva@escola.edu.br",
                "role": "teacher",
                "specialization": "Educação Especial",
                "license_number": None,
                "organization": "Escola Municipal João Paulo II",
                "phone": "(11) 98765-4321",
            }
        }


class ProfessionalUpdate(BaseModel):
    """Schema para atualização de profissional."""

    name: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[ProfessionalRole] = None
    specialization: Optional[str] = Field(None, max_length=255)
    license_number: Optional[str] = Field(None, max_length=100)
    organization: Optional[str] = Field(None, min_length=3, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class ProfessionalResponse(BaseModel):
    """Schema de resposta para profissional."""

    id: UUID
    name: str
    email: str
    role: ProfessionalRole
    role_display: str
    specialization: Optional[str]
    license_number: Optional[str]
    organization: str
    phone: Optional[str]
    is_active: bool
    is_education_professional: bool
    is_health_professional: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProfessionalListResponse(BaseModel):
    """Schema para lista paginada de profissionais."""

    professionals: list[ProfessionalResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProfessionalSummary(BaseModel):
    """Schema resumido de profissional (para listas e relacionamentos)."""

    id: UUID
    name: str
    role: ProfessionalRole
    role_display: str
    organization: str

    class Config:
        from_attributes = True


# ============================================================================
# FILTER/QUERY SCHEMAS
# ============================================================================


class ProfessionalFilter(BaseModel):
    """Schema para filtros de busca de profissionais."""

    role: Optional[ProfessionalRole] = None
    organization: Optional[str] = None
    is_active: Optional[bool] = True
    search: Optional[str] = Field(None, description="Busca por nome ou email")
    is_education: Optional[bool] = Field(None, description="Filtrar apenas profissionais de educação")
    is_health: Optional[bool] = Field(None, description="Filtrar apenas profissionais de saúde")


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================


class ProfessionalStatistics(BaseModel):
    """Estatísticas de profissionais no sistema."""

    total_professionals: int
    total_active: int
    total_inactive: int
    by_role: dict[str, int]
    education_professionals: int
    health_professionals: int
    organizations_count: int
