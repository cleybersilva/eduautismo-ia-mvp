#!/usr/bin/env python3

"""
Script para validar links na documentação do EduAutismo IA.
Verifica links internos e externos em arquivos markdown.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple
import requests
import markdown
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

class DocLinkValidator:
    def __init__(self, docs_root: str):
        self.docs_root = Path(docs_root)
        self.md_files: Set[Path] = set()
        self.broken_links: List[Tuple[str, str, str]] = []
        self.checked_external: Set[str] = set()

    def find_md_files(self) -> None:
        """Encontra todos os arquivos markdown no diretório docs."""
        for path in self.docs_root.rglob("*.md"):
            self.md_files.add(path)

    def extract_links(self, content: str) -> List[str]:
        """Extrai links de um arquivo markdown."""
        # Links inline
        inline_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        # Links de referência
        ref_links = re.findall(r'\[([^\]]+)\]:\s*(\S+)', content)
        return [link for _, link in inline_links + ref_links]

    def check_internal_link(self, link: str, file_path: Path) -> bool:
        """Verifica se um link interno é válido."""
        if link.startswith("#"):
            # TODO: Implementar verificação de âncoras
            return True

        target_path = (file_path.parent / link).resolve()
        return target_path.exists()

    def check_external_link(self, url: str) -> bool:
        """Verifica se um link externo está acessível."""
        if url in self.checked_external:
            return True

        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 405:  # Method not allowed
                response = requests.get(url, timeout=10)
            valid = response.status_code < 400
            if valid:
                self.checked_external.add(url)
            return valid
        except:
            return False

    def validate_file(self, file_path: Path) -> None:
        """Valida todos os links em um arquivo markdown."""
        try:
            content = file_path.read_text(encoding='utf-8')
            links = self.extract_links(content)

            for link in links:
                # Ignorar capturas óbvias não-links (texto entre aspas ou com espaços)
                if not link or link.startswith(("'", '"')) or ' ' in link:
                    continue
                if link.startswith(('http://', 'https://')):
                    if not self.check_external_link(link):
                        self.broken_links.append((str(file_path), link, "Link externo inacessível"))
                else:
                    if not self.check_internal_link(link, file_path):
                        self.broken_links.append((str(file_path), link, "Link interno inválido"))
        except Exception as e:
            self.broken_links.append((str(file_path), "", f"Erro ao processar arquivo: {str(e)}"))

    def validate_all(self) -> None:
        """Valida todos os arquivos markdown encontrados."""
        self.find_md_files()
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.validate_file, self.md_files)

    def print_report(self) -> None:
        """Imprime relatório de validação."""
        print("\n=== Relatório de Validação de Links ===")
        print(f"\nArquivos verificados: {len(self.md_files)}")
        print(f"Links quebrados encontrados: {len(self.broken_links)}\n")

        if self.broken_links:
            print("Detalhes dos links quebrados:")
            for file_path, link, error in self.broken_links:
                print(f"\nArquivo: {file_path}")
                print(f"Link: {link}")
                print(f"Erro: {error}")
        else:
            print("Todos os links estão válidos! 🎉")

def main():
    if len(sys.argv) != 2:
        print("Uso: python validate_docs.py <pasta_docs>")
        sys.exit(1)

    docs_path = sys.argv[1]
    validator = DocLinkValidator(docs_path)
    validator.validate_all()
    validator.print_report()

    # Retorna código de erro se encontrar links quebrados
    sys.exit(1 if validator.broken_links else 0)

if __name__ == "__main__":
    main()