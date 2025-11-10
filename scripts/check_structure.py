#!/usr/bin/env python3
"""
Project Structure Validator for EduAutismo IA MVP

This script validates the project structure against the expected layout
defined in the project documentation.

Usage:
    python scripts/check_structure.py [--verbose] [--fix]

Options:
    --verbose    Show detailed information about all checks
    --fix        Create missing directories (use with caution)
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@dataclass
class ValidationResult:
    """Results of structure validation"""
    missing_dirs: List[str]
    missing_files: List[str]
    present_dirs: List[str]
    present_files: List[str]
    unexpected_items: List[str]


class ProjectStructureValidator:
    """Validates the EduAutismo IA project structure"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # Expected directories (relative to project root)
        self.expected_dirs = {
            # Root level directories
            '.github',
            '.github/workflows',
            '.vscode',
            'docs',
            'scripts',
            'scripts/setup',
            'scripts/deployment',
            'scripts/backup',
            'scripts/database',
            'scripts/ml',
            'logs',

            # Backend structure
            'backend',
            'backend/app',
            'backend/app/api',
            'backend/app/api/routes',
            'backend/app/api/dependencies',
            'backend/app/core',
            'backend/app/models',
            'backend/app/services',
            'backend/app/utils',
            'backend/app/schemas',
            'backend/migrations',
            'backend/tests',
            'backend/tests/unit',
            'backend/tests/integration',
            'backend/tests/fixtures',

            # Frontend structure
            'frontend',
            'frontend/src',
            'frontend/src/components',
            'frontend/src/pages',
            'frontend/src/services',
            'frontend/src/styles',
            'frontend/src/utils',
            'frontend/public',

            # ML and Infrastructure
            'ml_models',
            'ml_models/behavioral_classifier',
            'ml_models/recommender',
            'terraform',
        }

        # Expected files (critical files only)
        self.expected_files = {
            # Root configuration files
            '.gitignore',
            'README.md',

            # Backend files
            'backend/app/__init__.py',
            'backend/app/main.py',
            'backend/app/config.py',
            'backend/app/core/__init__.py',
            'backend/requirements.txt',
            'backend/requirements-dev.txt',

            # Frontend files
            'frontend/package.json',
            'frontend/vite.config.js',
            'frontend/tailwind.config.js',
            'frontend/src/App.jsx',
            'frontend/src/main.jsx',
            'frontend/index.html',

            # Environment and configuration
            'backend/.env.example',

            # Scripts
            'check_install.sh',
        }

        # Optional but recommended files
        self.optional_files = {
            'backend/alembic.ini',
            'backend/pytest.ini',
            'backend/Dockerfile',
            'frontend/Dockerfile',
            'docker-compose.yml',
            '.env',
            'backend/.env',
            'terraform/main.tf',
            'terraform/variables.tf',
            'terraform/outputs.tf',
        }

    def validate(self, verbose: bool = False) -> ValidationResult:
        """
        Validate the project structure

        Args:
            verbose: If True, print detailed information

        Returns:
            ValidationResult object with validation details
        """
        missing_dirs = []
        missing_files = []
        present_dirs = []
        present_files = []

        # Check directories
        for dir_path in sorted(self.expected_dirs):
            full_path = self.project_root / dir_path
            if full_path.exists() and full_path.is_dir():
                present_dirs.append(dir_path)
                if verbose:
                    print(f"{Colors.OKGREEN}✓{Colors.ENDC} Directory: {dir_path}")
            else:
                missing_dirs.append(dir_path)
                if verbose:
                    print(f"{Colors.FAIL}✗{Colors.ENDC} Missing directory: {dir_path}")

        # Check files
        for file_path in sorted(self.expected_files):
            full_path = self.project_root / file_path
            if full_path.exists() and full_path.is_file():
                present_files.append(file_path)
                if verbose:
                    print(f"{Colors.OKGREEN}✓{Colors.ENDC} File: {file_path}")
            else:
                missing_files.append(file_path)
                if verbose:
                    print(f"{Colors.FAIL}✗{Colors.ENDC} Missing file: {file_path}")

        # Check optional files (informational only)
        if verbose:
            print(f"\n{Colors.BOLD}Optional Files:{Colors.ENDC}")
            for file_path in sorted(self.optional_files):
                full_path = self.project_root / file_path
                if full_path.exists():
                    print(f"{Colors.OKCYAN}✓{Colors.ENDC} Optional: {file_path}")
                else:
                    print(f"{Colors.WARNING}○{Colors.ENDC} Optional (missing): {file_path}")

        return ValidationResult(
            missing_dirs=missing_dirs,
            missing_files=missing_files,
            present_dirs=present_dirs,
            present_files=present_files,
            unexpected_items=[]
        )

    def create_missing_directories(self, missing_dirs: List[str]) -> None:
        """
        Create missing directories

        Args:
            missing_dirs: List of directory paths to create
        """
        for dir_path in missing_dirs:
            full_path = self.project_root / dir_path
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"{Colors.OKGREEN}✓{Colors.ENDC} Created: {dir_path}")
            except Exception as e:
                print(f"{Colors.FAIL}✗{Colors.ENDC} Failed to create {dir_path}: {e}")

    def print_summary(self, result: ValidationResult) -> None:
        """
        Print a summary of the validation results

        Args:
            result: ValidationResult object
        """
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}Project Structure Validation Summary{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

        total_dirs = len(self.expected_dirs)
        total_files = len(self.expected_files)

        # Directories summary
        dirs_ok = len(result.present_dirs)
        dirs_missing = len(result.missing_dirs)
        dirs_percentage = (dirs_ok / total_dirs * 100) if total_dirs > 0 else 0

        print(f"{Colors.BOLD}Directories:{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}Present:{Colors.ENDC} {dirs_ok}/{total_dirs} ({dirs_percentage:.1f}%)")
        if dirs_missing > 0:
            print(f"  {Colors.FAIL}Missing:{Colors.ENDC} {dirs_missing}/{total_dirs}")

        # Files summary
        files_ok = len(result.present_files)
        files_missing = len(result.missing_files)
        files_percentage = (files_ok / total_files * 100) if total_files > 0 else 0

        print(f"\n{Colors.BOLD}Files:{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}Present:{Colors.ENDC} {files_ok}/{total_files} ({files_percentage:.1f}%)")
        if files_missing > 0:
            print(f"  {Colors.FAIL}Missing:{Colors.ENDC} {files_missing}/{total_files}")

        # Overall status
        overall_percentage = ((dirs_ok + files_ok) / (total_dirs + total_files) * 100)
        print(f"\n{Colors.BOLD}Overall Completion:{Colors.ENDC} {overall_percentage:.1f}%")

        # Detailed missing items
        if result.missing_dirs:
            print(f"\n{Colors.BOLD}{Colors.WARNING}Missing Directories:{Colors.ENDC}")
            for dir_path in sorted(result.missing_dirs):
                print(f"  {Colors.WARNING}•{Colors.ENDC} {dir_path}")

        if result.missing_files:
            print(f"\n{Colors.BOLD}{Colors.FAIL}Missing Critical Files:{Colors.ENDC}")
            for file_path in sorted(result.missing_files):
                print(f"  {Colors.FAIL}•{Colors.ENDC} {file_path}")

        # Status indicator
        print(f"\n{Colors.BOLD}Status:{Colors.ENDC} ", end="")
        if overall_percentage >= 90:
            print(f"{Colors.OKGREEN}✓ Excellent - Project structure is well-formed{Colors.ENDC}")
        elif overall_percentage >= 70:
            print(f"{Colors.WARNING}⚠ Good - Some components are missing{Colors.ENDC}")
        elif overall_percentage >= 50:
            print(f"{Colors.WARNING}⚠ Fair - Several components need attention{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ Poor - Major structural issues detected{Colors.ENDC}")

        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate EduAutismo IA project structure'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information about all checks'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Create missing directories (WARNING: use with caution)'
    )
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Path to project root (default: current directory)'
    )

    args = parser.parse_args()

    # Get project root
    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"{Colors.FAIL}Error: Project root does not exist: {project_root}{Colors.ENDC}")
        sys.exit(1)

    print(f"{Colors.BOLD}Validating project structure...{Colors.ENDC}")
    print(f"Project root: {project_root}\n")

    # Create validator and run validation
    validator = ProjectStructureValidator(project_root)
    result = validator.validate(verbose=args.verbose)

    # Print summary
    validator.print_summary(result)

    # Fix if requested
    if args.fix and result.missing_dirs:
        print(f"{Colors.WARNING}Creating missing directories...{Colors.ENDC}\n")
        validator.create_missing_directories(result.missing_dirs)
        print(f"\n{Colors.OKGREEN}Done! Re-run the script to verify.{Colors.ENDC}\n")
    elif result.missing_dirs and not args.fix:
        print(f"{Colors.OKCYAN}Tip: Run with --fix to automatically create missing directories{Colors.ENDC}\n")

    # Exit code based on results
    # 0 = success (>= 90%)
    # 1 = warning (>= 70%)
    # 2 = error (< 70%)
    total = len(validator.expected_dirs) + len(validator.expected_files)
    present = len(result.present_dirs) + len(result.present_files)
    percentage = (present / total * 100) if total > 0 else 0

    if percentage >= 90:
        sys.exit(0)
    elif percentage >= 70:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
