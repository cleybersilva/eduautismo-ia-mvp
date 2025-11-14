#!/usr/bin/env python3
"""
Script para criar usuário admin no banco de dados.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.utils.constants import UserRole


def create_admin_user(
    email: str,
    password: str,
    full_name: str,
    role: UserRole = UserRole.ADMIN,
):
    """
    Cria um usuário admin no banco de dados.

    Args:
        email: Email do usuário
        password: Senha em texto plano
        full_name: Nome completo
        role: Role do usuário (default: ADMIN)
    """
    db: Session = SessionLocal()

    try:
        # Verificar se o usuário já existe
        existing_user = db.query(User).filter(User.email == email).first()

        if existing_user:
            print(f"❌ Usuário com email '{email}' já existe!")
            print(f"   ID: {existing_user.id}")
            print(f"   Nome: {existing_user.full_name}")
            print(f"   Role: {existing_user.role}")

            # Perguntar se deseja atualizar a senha
            response = input("\n🔄 Deseja atualizar a senha? (s/n): ")
            if response.lower() == 's':
                existing_user.hashed_password = get_password_hash(password)
                db.commit()
                print(f"✅ Senha atualizada com sucesso para '{email}'!")
            else:
                print("⏭️  Operação cancelada.")

            return existing_user

        # Criar novo usuário
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

        print(f"✅ Usuário criado com sucesso!")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Nome: {user.full_name}")
        print(f"   Role: {user.role}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Verificado: {user.is_verified}")

        return user

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar usuário: {str(e)}")
        raise
    finally:
        db.close()


def main():
    """Função principal."""
    print("=" * 60)
    print("🔐 CRIAÇÃO DE USUÁRIO ADMIN - EduAutismo IA")
    print("=" * 60)
    print()

    # Criar usuário Cleyber Silva
    print("📝 Criando usuário: Cleyber Silva")
    print()

    create_admin_user(
        email="cleyber.silva@usp.com",
        password="$Cleyber2025EUA",
        full_name="Cleyber Silva",
        role=UserRole.ADMIN,
    )

    print()
    print("=" * 60)
    print("✅ PROCESSO FINALIZADO!")
    print("=" * 60)
    print()
    print("🔑 Credenciais de acesso:")
    print(f"   Email: cleyber.silva@usp.com")
    print(f"   Senha: $Cleyber2025EUA")
    print()
    print("🌐 Acesse o sistema em: http://localhost:5173")
    print()


if __name__ == "__main__":
    main()
