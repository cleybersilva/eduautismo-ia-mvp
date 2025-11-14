#!/usr/bin/env python3
"""
Script para atualizar email do usuário no banco de dados.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Configurar SQLite
import os
os.environ['DATABASE_URL'] = 'sqlite:///./eduautismo_dev.db'

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.user import User


def update_user_email(old_email: str, new_email: str):
    """
    Atualiza o email de um usuário.

    Args:
        old_email: Email atual
        new_email: Novo email
    """
    # Criar engine SQLite
    db_path = backend_dir / "eduautismo_dev.db"
    engine = create_engine(f'sqlite:///{db_path}', echo=False)

    # Criar sessão
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db: Session = SessionLocal()

    try:
        # Buscar usuário pelo email antigo
        user = db.query(User).filter(User.email == old_email).first()

        if not user:
            print(f"❌ Usuário com email '{old_email}' não encontrado!")
            return

        print(f"✅ Usuário encontrado:")
        print(f"   ID: {user.id}")
        print(f"   Nome: {user.full_name}")
        print(f"   Email atual: {user.email}")
        print(f"   Role: {user.role.value}")
        print()

        # Atualizar email
        print(f"🔄 Atualizando email para: {new_email}")
        user.email = new_email
        db.commit()

        print()
        print(f"✅ Email atualizado com sucesso!")
        print(f"   ID: {user.id}")
        print(f"   Nome: {user.full_name}")
        print(f"   Novo email: {user.email}")
        print(f"   Role: {user.role.value}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao atualizar email: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def main():
    """Função principal."""
    print("=" * 70)
    print("📧 ATUALIZAÇÃO DE EMAIL - EduAutismo IA")
    print("=" * 70)
    print()

    # Atualizar email
    update_user_email(
        old_email="cleyber.silva@usp.com",
        new_email="cleyber.silva@usp.br"
    )

    print()
    print("=" * 70)
    print("✅ PROCESSO FINALIZADO!")
    print("=" * 70)
    print()
    print("🔑 Novas credenciais de acesso:")
    print(f"   📧 Email: cleyber.silva@usp.br")
    print(f"   🔒 Senha: $Cleyber2025EUA")
    print()
    print("🌐 Acesse o sistema em: http://localhost:5173")
    print()


if __name__ == "__main__":
    main()
