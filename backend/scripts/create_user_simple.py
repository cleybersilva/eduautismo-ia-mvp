#!/usr/bin/env python3
"""
Script simplificado para criar usuário admin usando SQLite.
Não requer Docker ou PostgreSQL rodando.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Configurar SQLite antes de importar qualquer coisa
import os
os.environ['DATABASE_URL'] = 'sqlite:///./eduautismo_dev.db'

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import get_password_hash
from app.db.base import Base
from app.models.user import User
from app.utils.constants import UserRole


def create_user(
    email: str,
    password: str,
    full_name: str,
    role: UserRole = UserRole.ADMIN,
):
    """
    Cria um usuário no banco de dados SQLite local.

    Args:
        email: Email do usuário
        password: Senha em texto plano
        full_name: Nome completo
        role: Role do usuário (default: ADMIN)
    """
    # Criar engine SQLite
    db_path = backend_dir / "eduautismo_dev.db"
    engine = create_engine(f'sqlite:///{db_path}', echo=False)

    # Criar todas as tabelas
    print("📦 Criando tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")
    print()

    # Criar sessão
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db: Session = SessionLocal()

    try:
        # Verificar se o usuário já existe
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            print(f"❌ Usuário com email '{email}' já existe!")
            print(f"   ID: {existing_user.id}")
            print(f"   Nome: {existing_user.full_name}")
            print(f"   Role: {existing_user.role}")
            print()

            # Atualizar senha
            print("🔄 Atualizando senha...")
            existing_user.hashed_password = get_password_hash(password)
            db.commit()
            print(f"✅ Senha atualizada com sucesso!")

            return existing_user

        # Criar novo usuário
        print(f"👤 Criando usuário: {full_name}")
        hashed_password = get_password_hash(password)

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print()
        print("✅ Usuário criado com sucesso!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.full_name}")
        print(f"   Role: {user.role.value}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Verificado: {user.is_verified}")

        return user

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar usuário: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def main():
    """Função principal."""
    print("=" * 70)
    print("🔐 CRIAÇÃO DE USUÁRIO ADMIN - EduAutismo IA")
    print("=" * 70)
    print()
    print("📝 Usando banco SQLite local (não requer Docker)")
    print()

    # Criar usuário Cleyber Silva
    create_user(
        email="cleyber.silva@usp.com",
        password="$Cleyber2025EUA",
        full_name="Cleyber Silva",
        role=UserRole.ADMIN,
    )

    print()
    print("=" * 70)
    print("✅ PROCESSO FINALIZADO!")
    print("=" * 70)
    print()
    print("🔑 Credenciais de acesso:")
    print(f"   📧 Email: cleyber.silva@usp.com")
    print(f"   🔒 Senha: $Cleyber2025EUA")
    print()
    print("🌐 Acesse o sistema:")
    print(f"   Frontend: http://localhost:5173")
    print(f"   Backend API: http://localhost:8000")
    print(f"   API Docs: http://localhost:8000/docs")
    print()
    print("💡 IMPORTANTE:")
    print("   - O banco de dados SQLite foi criado em: backend/eduautismo_dev.db")
    print("   - Para usar PostgreSQL, inicie o Docker: docker-compose up -d")
    print("   - Configure DATABASE_URL no .env para usar PostgreSQL")
    print()


if __name__ == "__main__":
    main()
