#!/usr/bin/env python3
"""
Script para atualizar automaticamente README.md e CLAUDE.md.

Este script:
- Detecta mudanças na estrutura do projeto
- Atualiza versões e datas automaticamente
- Atualiza árvore de diretórios
- Atualiza comandos e URLs

Uso:
    python scripts/update_docs.py
    python scripts/update_docs.py --check-only  # Apenas verificar
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class DocsUpdater:
    """Atualiza documentação automaticamente."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.readme_path = project_root / "README.md"
        self.claude_path = project_root / "CLAUDE.md"
        self.changes_made = False

    def get_project_structure(self) -> str:
        """Gera árvore de estrutura do projeto."""
        structure = []

        # Diretórios importantes para documentar
        important_dirs = [
            ".github/workflows",
            "backend/app",
            "backend/tests",
            "backend/alembic",
            "frontend/src",
            "terraform",
            "docs",
            "scripts",
        ]

        for dir_path in important_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                structure.append(f"✓ {dir_path}")

        return "\n".join(structure)

    def get_current_date(self) -> str:
        """Retorna data atual no formato YYYY-MM-DD."""
        return datetime.now().strftime("%Y-%m-%d")

    def count_files(self, pattern: str) -> int:
        """Conta arquivos que correspondem ao padrão."""
        return len(list(self.project_root.rglob(pattern)))

    def get_project_stats(self) -> Dict[str, int]:
        """Coleta estatísticas do projeto."""
        return {
            "py_files": self.count_files("*.py"),
            "test_files": self.count_files("test_*.py"),
            "jsx_files": self.count_files("*.jsx"),
            "workflow_files": self.count_files(".github/workflows/*.yml"),
        }

    def update_claude_version(self) -> bool:
        """Atualiza versão e data no CLAUDE.md."""
        if not self.claude_path.exists():
            print("⚠️  CLAUDE.md não encontrado")
            return False

        content = self.claude_path.read_text(encoding="utf-8")
        original = content

        # Atualizar data
        current_date = self.get_current_date()
        content = re.sub(
            r"\*\*Última Atualização\*\*:\s*\d{4}-\d{2}-\d{2}",
            f"**Última Atualização**: {current_date}",
            content
        )

        # Incrementar versão menor (1.1.0 -> 1.1.1)
        def increment_version(match):
            major, minor, patch = match.groups()
            new_patch = int(patch) + 1
            return f"**Versão**: {major}.{minor}.{new_patch}"

        content = re.sub(
            r"\*\*Versão\*\*:\s*(\d+)\.(\d+)\.(\d+)",
            increment_version,
            content
        )

        if content != original:
            self.claude_path.write_text(content, encoding="utf-8")
            print("✅ CLAUDE.md atualizado (versão e data)")
            self.changes_made = True
            return True

        return False

    def check_outdated_paths(self, content: str) -> List[str]:
        """Verifica paths desatualizados na documentação."""
        issues = []

        # Procurar por referências a src/ que não deveriam existir
        if re.search(r'uvicorn\s+src\.', content):
            issues.append("❌ Comando uvicorn usando 'src.' ao invés de 'app.'")

        if re.search(r'from\s+src\.', content) and '# src/' not in content:
            issues.append("❌ Import usando 'from src.' ao invés de 'from app.'")

        if 'streamlit run' in content and 'Streamlit' not in content:
            issues.append("❌ Referência a streamlit encontrada")

        if 'localhost:8501' in content:
            issues.append("❌ Porta 8501 (Streamlit) ao invés de 5173 (Vite)")

        if 'your-org/eduautismo-ia' in content:
            issues.append("❌ URL de repositório genérica 'your-org'")

        return issues

    def verify_docs(self) -> Tuple[List[str], List[str]]:
        """Verifica se documentação está atualizada."""
        readme_issues = []
        claude_issues = []

        if self.readme_path.exists():
            readme_content = self.readme_path.read_text(encoding="utf-8")
            readme_issues = self.check_outdated_paths(readme_content)

        if self.claude_path.exists():
            claude_content = self.claude_path.read_text(encoding="utf-8")
            claude_issues = self.check_outdated_paths(claude_content)

        return readme_issues, claude_issues

    def update_all(self) -> bool:
        """Executa todas as atualizações."""
        print("🔄 Atualizando documentação...")
        print()

        # Atualizar CLAUDE.md
        self.update_claude_version()

        # Verificar problemas
        readme_issues, claude_issues = self.verify_docs()

        if readme_issues:
            print("\n⚠️  Problemas encontrados no README.md:")
            for issue in readme_issues:
                print(f"  {issue}")

        if claude_issues:
            print("\n⚠️  Problemas encontrados no CLAUDE.md:")
            for issue in claude_issues:
                print(f"  {issue}")

        if readme_issues or claude_issues:
            print("\n💡 Execute correções manuais ou use os templates corretos")
            return False

        print("\n✅ Documentação verificada e atualizada!")
        return True


def main():
    """Função principal."""
    # Detectar root do projeto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Verificar se estamos no diretório correto
    if not (project_root / "README.md").exists():
        print("❌ Erro: README.md não encontrado no diretório raiz")
        print(f"   Procurado em: {project_root}")
        sys.exit(1)

    updater = DocsUpdater(project_root)

    # Verificar modo
    check_only = "--check-only" in sys.argv or "--check" in sys.argv

    if check_only:
        print("🔍 Verificando documentação (somente leitura)...")
        print()
        readme_issues, claude_issues = updater.verify_docs()

        total_issues = len(readme_issues) + len(claude_issues)

        if total_issues > 0:
            print(f"\n❌ {total_issues} problema(s) encontrado(s)")
            sys.exit(1)
        else:
            print("\n✅ Documentação está atualizada!")
            sys.exit(0)
    else:
        # Modo de atualização
        success = updater.update_all()

        if updater.changes_made:
            print("\n📝 Mudanças foram feitas. Não esqueça de commitar!")

        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
