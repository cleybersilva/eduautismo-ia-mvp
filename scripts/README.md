# Scripts Directory

This directory contains utility scripts for the EduAutismo IA project.

## Structure Validation Scripts

### check_structure.py

**Purpose:** Validate project structure and create missing files with templates.

**Features:**
- ✅ Validates directory structure
- ✅ Validates file existence
- ✅ Priority-based file creation (1=Critical, 2=Important, 3=Optional)
- ✅ Intelligent file templates (Models, Schemas, Services, Routes, Tests)
- ✅ Detailed reporting with color-coded output
- ✅ Automatic TODO insertion for customization

**Quick Start:**
```bash
# Validate only
python scripts/check_structure.py --report-only

# Create critical files
python scripts/check_structure.py --create-missing --priority 1

# Create critical + important files
python scripts/check_structure.py --create-missing --priority 2
```

**Full Documentation:** See [docs/structure-validation.md](../docs/structure-validation.md)

### validate_structure.sh

**Purpose:** Complete validation workflow with multiple checks.

**Features:**
- ✅ Python version check
- ✅ Structure validation
- ✅ Package structure verification
- ✅ Critical files check
- ✅ Python syntax validation
- ✅ Git status report

**Quick Start:**
```bash
# Validate everything
./scripts/validate_structure.sh

# Auto-fix with Priority 1 files
./scripts/validate_structure.sh --fix

# Auto-fix with Priority 1 & 2 files
./scripts/validate_structure.sh --fix --priority 2
```

## Directory Organization

```
scripts/
├── README.md                    # This file
├── check_structure.py           # Main validation script
├── validate_structure.sh        # Complete workflow script
│
├── setup/                       # Setup and installation scripts
│   ├── check-requirements.sh
│   ├── install.sh
│   ├── quick-start.sh
│   └── test-all.sh
│
├── deployment/                  # Deployment scripts
│   ├── deploy-dev.sh
│   └── stop-dev.sh
│
├── backup/                      # Backup utilities
│
├── database/                    # Database management scripts
│
└── ml/                          # ML model training and management

```

## Other Scripts

### Setup Scripts (setup/)

**check-requirements.sh**
- Checks if all required tools are installed
- Validates Python, Node.js, Docker versions

**install.sh**
- Complete installation script
- Sets up backend and frontend environments

**quick-start.sh**
- Quick project startup
- Runs database migrations and starts services

**test-all.sh**
- Runs all test suites
- Backend and frontend tests

### Deployment Scripts (deployment/)

**deploy-dev.sh**
- Deploys to development environment
- Handles Docker containers and services

**stop-dev.sh**
- Stops development services
- Cleans up containers

## Usage Examples

### Complete New Project Setup

```bash
# 1. Create project structure
python scripts/check_structure.py --create-missing --priority 2

# 2. Validate everything
./scripts/validate_structure.sh

# 3. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 4. Run tests
pytest backend/tests/
```

### Daily Development Workflow

```bash
# Before starting work
./scripts/validate_structure.sh

# Before committing
python scripts/check_structure.py --report-only
git status
git add .
git commit -m "Your message"
```

### CI/CD Integration

```yaml
# .github/workflows/validate.yml
- name: Validate Structure
  run: python scripts/check_structure.py --report-only
```

## Script Permissions

Make scripts executable:

```bash
chmod +x scripts/*.sh
chmod +x scripts/**/*.sh
```

## Adding New Scripts

When adding new scripts:

1. Choose the appropriate subdirectory
2. Follow naming conventions (lowercase, hyphens)
3. Add shebang line (`#!/bin/bash` or `#!/usr/bin/env python3`)
4. Document in this README
5. Make executable with `chmod +x`
6. Add error handling (`set -e` for bash scripts)

### Template for Bash Scripts

```bash
#!/bin/bash
#
# Script Name - Brief Description
#
# Usage:
#   ./script-name.sh [options]
#
# Options:
#   --help    Show this help message

set -e  # Exit on error

# Script content here
```

### Template for Python Scripts

```python
#!/usr/bin/env python3
"""
Script Name - Brief Description

Usage:
    python script_name.py [options]
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Description')
    # Add arguments
    args = parser.parse_args()

    # Script logic here


if __name__ == '__main__':
    main()
```

## Troubleshooting

### Permission Issues

```bash
# Fix all scripts at once
find scripts/ -type f -name "*.sh" -exec chmod +x {} \;
find scripts/ -type f -name "*.py" -exec chmod +x {} \;
```

### Python Import Issues

```bash
# Set PYTHONPATH to project root
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Or run from project root
cd /path/to/eduautismo-ia-mvp
python scripts/check_structure.py
```

### Script Not Found

```bash
# Always run from project root
pwd  # Should be: /path/to/eduautismo-ia-mvp

# Use full path or ./
python scripts/check_structure.py  # ✅
python check_structure.py          # ❌
```

## Dependencies

Most scripts require:
- **Python 3.11+** for Python scripts
- **Bash 4.0+** for shell scripts
- **Git** for version control operations
- **Docker** (optional, for deployment scripts)

## Exit Codes

Scripts use standard exit codes:
- `0` - Success
- `1` - Warning or minor issues
- `2` - Error or major issues

Use in CI/CD:
```bash
./scripts/validate_structure.sh
if [ $? -ne 0 ]; then
    echo "Validation failed"
    exit 1
fi
```

## Best Practices

1. **Always run from project root**
2. **Check exit codes in automation**
3. **Review script output before acting on suggestions**
4. **Use `--help` flag when available**
5. **Test scripts in development before using in production**
6. **Keep scripts focused and single-purpose**
7. **Document all options and usage**

## Contributing

When contributing new scripts:
1. Follow existing patterns and conventions
2. Add comprehensive documentation
3. Include usage examples
4. Add error handling
5. Test thoroughly
6. Update this README

## Support

For issues with scripts:
1. Check script output for error messages
2. Review this documentation
3. Check [docs/structure-validation.md](../docs/structure-validation.md) for validation scripts
4. Review [docs/troubleshooting.md](../docs/troubleshooting.md) if available
5. Open an issue on GitHub

## Future Scripts

Planned additions:
- [ ] Database seeding script
- [ ] ML model training automation
- [ ] Performance benchmarking
- [ ] Security scanning
- [ ] Automated testing with coverage
- [ ] Production deployment scripts
- [ ] Backup and restore utilities

## License

All scripts are part of the EduAutismo IA project and follow the same MIT License.
