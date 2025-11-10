<div align="center">

# 🧩 EduAutismo IA

### Plataforma Inteligente de Apoio Pedagógico para Alunos com TEA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/AWS-Cloud-orange.svg)](https://aws.amazon.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](tests/)

[Funcionalidades](#-funcionalidades) •
[Arquitetura](#-arquitetura) •
[Instalação](#-instalação) •
[Documentação](#-documentação) •
[Contribuir](#-como-contribuir) •
[Licença](#-licença)

---

</div>

## 📖 Sobre o Projeto

**EduAutismo IA** é uma plataforma web desenvolvida como Trabalho de Conclusão de Curso (TCC) do MBA em Inteligência Artificial e Big Data pela Universidade de São Paulo (USP), que utiliza **Inteligência Artificial** e **Machine Learning** para auxiliar professores da rede pública na criação de atividades pedagógicas personalizadas para alunos com Transtorno do Espectro Autista (TEA).

### 🎯 Problema

Professores da rede pública enfrentam desafios significativos:
- Falta de tempo para criar atividades individualizadas
- Carência de recursos especializados em TEA
- Dificuldade em adaptar conteúdos para diferentes perfis cognitivos e sensoriais
- Necessidade de acompanhamento contínuo do desenvolvimento dos alunos

### 💡 Solução

Uma plataforma que:
- ✨ Gera atividades pedagógicas personalizadas usando **GPT-5**
- 📊 Realiza avaliações comportamentais baseadas em instrumentos validados (CARS, AQ, etc.)
- 🤖 Classifica perfis comportamentais com **Machine Learning**
- 📈 Acompanha evolução do aluno com dashboards e relatórios
- 🎓 Oferece recomendações baseadas em **análise preditiva**

---

## ✨ Funcionalidades

### 👨‍🏫 Para Professores

| Funcionalidade | Descrição |
|----------------|-----------|
| **Gestão de Alunos** | Cadastro e gerenciamento de perfis com informações cognitivas e sensoriais |
| **Avaliações Comportamentais** | Aplicação de instrumentos validados (CARS, AQ, SPM) com análise automática |
| **Geração de Atividades** | Criação automática de atividades personalizadas por IA |
| **Acompanhamento** | Dashboards com evolução, métricas e insights |
| **Relatórios** | Geração de relatórios pedagógicos em PDF |

### 🤖 Recursos de IA/ML

- **NLP (GPT-4)**: Geração de atividades contextualizadas e adequadas ao perfil
- **Classificação ML**: Predição de perfil comportamental (scikit-learn)
- **Sistema de Recomendação**: Sugestões baseadas em similaridade e performance
- **Análise Comportamental**: Identificação de padrões e tendências

### 🔒 Segurança e Compliance

- ✅ **LGPD Compliant**: Anonimização, consentimento, direito ao esquecimento
- 🔐 **Criptografia**: At rest (AES-256) e in transit (TLS 1.2+)
- 🛡️ **Autenticação**: JWT tokens com refresh
- 📝 **Auditoria**: Logging completo de todas as operações sensíveis

---

## 🏗️ Arquitetura

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                         USERS                               │
│                    (Professores)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌──────────────┐          ┌──────────────┐                │
│  │  Web UI      │          │  Mobile      │                │
│  │  (Streamlit) │          │  (Future)    │                │
│  └──────────────┘          └──────────────┘                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/TLS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         AWS ALB                             │
│                  (Load Balancer)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI REST API                        │  │
│  │              (ECS Fargate)                           │  │
│  │                                                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │  │
│  │  │   Student   │  │  Activity   │  │ Assessment │  │  │
│  │  │   Service   │  │  Service    │  │  Service   │  │  │
│  │  └─────────────┘  └─────────────┘  └────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │  DocumentDB  │  │     S3       │
│  (RDS)       │  │  (MongoDB)   │  │  (Storage)   │
│              │  │              │  │              │
│  Structured  │  │  Logs &      │  │  Files &     │
│  Data        │  │  Analytics   │  │  ML Models   │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Tech Stack

#### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic V2
- **Authentication**: JWT (python-jose)

#### Database
- **Relational**: PostgreSQL 15.4 (AWS RDS)
- **Document**: MongoDB 5.0 (AWS DocumentDB)
- **Cache**: Redis 7.2 (optional)

#### AI/ML
- **NLP**: OpenAI GPT-4
- **ML Framework**: scikit-learn 1.3+
- **Data Processing**: pandas, numpy
- **Embeddings**: sentence-transformers

#### Infrastructure
- **Cloud Provider**: AWS
- **Container**: Docker, ECS Fargate
- **IaC**: Terraform 1.5+
- **CI/CD**: GitHub Actions
- **Monitoring**: Datadog (APM, Logs, Metrics)

#### Storage & CDN
- **Object Storage**: AWS S3
- **CDN**: CloudFront (optional)

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- Docker e Docker Compose
- AWS CLI (para deploy em produção)
- Git

### Instalação Local (Desenvolvimento)

#### 1. Clone o repositório
```bash
git clone https://github.com/your-org/eduautismo-ia.git
cd eduautismo-ia
```

#### 2. Crie e ative ambiente virtual
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

#### 3. Instale dependências
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento
```

#### 4. Configure variáveis de ambiente
```bash
cp .env.example .env
nano .env  # Edite com suas credenciais
```

Variáveis essenciais:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/eduautismo_dev
MONGO_URL=mongodb://user:pass@localhost:27017
OPENAI_API_KEY=sk-your-api-key-here
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

#### 5. Inicie banco de dados com Docker
```bash
docker-compose up -d postgres mongodb redis
```

#### 6. Execute migrations
```bash
alembic upgrade head
```

#### 7. (Opcional) Seed database
```bash
python scripts/seed_database.py
```

#### 8. Inicie aplicação
```bash
# API
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Web Interface (outro terminal)
streamlit run src/web/app.py
```

#### 9. Acesse aplicação

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Web UI**: http://localhost:8501

### Instalação com Docker (Recomendado)
```bash
# Build e start todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

Serviços disponíveis:
- **API**: http://localhost:8000
- **Web**: http://localhost:8501
- **PostgreSQL**: localhost:5432
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

---

## 📚 Documentação

### Documentação da API

A documentação interativa da API está disponível em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Exemplos de Uso

#### Criar um Aluno
```python
import requests

API_URL = "http://localhost:8000"

# 1. Login
response = requests.post(
    f"{API_URL}/api/v1/auth/login",
    json={
        "username": "professor@example.com",
        "password": "senha123"
    }
)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Criar aluno
response = requests.post(
    f"{API_URL}/api/v1/students/",
    json={
        "age": 10,
        "grade_level": "fundamental_1_3ano",
        "diagnosis": "autismo_leve",
        "cognitive_profile": {
            "memory": 7,
            "attention": 6,
            "processing_speed": 7,
            "executive_function": 6,
            "language": 8,
            "visual_spatial": 7
        },
        "sensory_profile": {
            "visual": 2,
            "auditory": 2,
            "tactile": 1,
            "vestibular": 2,
            "proprioceptive": 1
        }
    },
    headers=headers
)

student = response.json()
print(f"Aluno criado: {student['id']}")
```

#### Gerar Atividade Personalizada
```python
response = requests.post(
    f"{API_URL}/api/v1/activities/generate",
    json={
        "student_id": student['id'],
        "subject": "matematica",
        "topic": "adicao",
        "difficulty": 3,
        "duration_minutes": 30
    },
    headers=headers
)

activity = response.json()
print(f"Atividade gerada: {activity['title']}")
print(f"Conteúdo: {activity['content']}")
```

### Guias Adicionais

- [📘 Guia de Instalação Completo](docs/installation.md)
- [🏗️ Guia de Arquitetura](docs/architecture.md)
- [🔒 Guia de Segurança e LGPD](docs/security.md)
- [🤖 Guia de ML/IA](docs/ml-guide.md)
- [🚀 Guia de Deploy AWS](docs/aws-deployment.md)
- [💰 Guia de FinOps](docs/finops.md)
- [🐛 Troubleshooting](docs/troubleshooting.md)

---

## 🧪 Testes

### Executar todos os testes
```bash
pytest
```

### Testes com coverage
```bash
pytest --cov=src --cov-report=html
```

### Testes específicos
```bash
# Testes unitários
pytest tests/unit/

# Testes de integração
pytest tests/integration/

# Teste específico
pytest tests/unit/test_student_service.py
```

### Linting e formatação
```bash
# Black (formatter)
black src/ tests/

# Flake8 (linter)
flake8 src/ tests/

# MyPy (type checker)
mypy src/

# isort (import sorter)
isort src/ tests/
```

---

## 📊 Estrutura do Projeto
```
eduautismo-ia/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
├── docs/                   # Documentação detalhada
├── ml_models/              # Modelos ML treinados
│   ├── behavioral_classifier/
│   └── recommender/
├── scripts/                # Scripts de automação
│   ├── train_models.py
│   ├── deploy.sh
│   ├── backup.sh
│   └── seed_database.py
├── src/
│   ├── api/                # FastAPI application
│   │   ├── routes/         # Endpoints
│   │   ├── dependencies/   # Dependencies
│   │   └── main.py
│   ├── core/               # Core functionality
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/             # ML models
│   │   ├── behavioral_classifier.py
│   │   └── activity_recommender.py
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   │   ├── student_service.py
│   │   ├── activity_service.py
│   │   └── assessment_service.py
│   ├── utils/              # Utilities
│   └── web/                # Streamlit web interface
├── terraform/              # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── .env.example            # Environment variables template
├── .gitignore
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.web
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini             # Database migrations
├── pytest.ini
└── README.md
```

---

## 🚀 Deploy

### Deploy em Produção (AWS)

#### Pré-requisitos
- Conta AWS configurada
- Terraform instalado
- Docker instalado
- AWS CLI configurado

#### 1. Provisionar infraestrutura
```bash
cd terraform/

# Inicializar Terraform
terraform init

# Criar workspace de produção
terraform workspace new production
terraform workspace select production

# Planejar
terraform plan -out=tfplan

# Aplicar
terraform apply tfplan
```

#### 2. Build e push de imagens
```bash
# Build
docker build -t eduautismo-api:latest -f Dockerfile.api .

# Login ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag e push
docker tag eduautismo-api:latest \
    123456789012.dkr.ecr.us-east-1.amazonaws.com/eduautismo-api:latest

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/eduautismo-api:latest
```

#### 3. Deploy aplicação
```bash
./scripts/deploy.sh production latest
```

### Deploy Automatizado (CI/CD)

O projeto inclui GitHub Actions para deploy automatizado:
```yaml
# .github/workflows/deploy.yml
# Push para main branch → Deploy automático
```

---

## 💰 Custos Estimados

| Componente | Custo Mensal (USD) | % Total |
|------------|-------------------|---------|
| Datadog | $235 | 30% |
| ECS Fargate | $175 | 22% |
| DocumentDB | $117 | 15% |
| OpenAI API | $90 | 11% |
| NAT Gateway | $67 | 8% |
| RDS PostgreSQL | $54 | 7% |
| Outros | $57 | 7% |
| **Total** | **~$795/mês** | **100%** |

**Otimizações disponíveis**: Reserved Instances (-30-40%), S3 Lifecycle (-50%), Right-sizing (-15-20%)

Ver [Guia de FinOps](docs/finops.md) para detalhes e estratégias de otimização.

---

## 🤝 Como Contribuir

Contribuições são bem-vindas! 🎉

### Processo

1. **Fork** o repositório
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Diretrizes

- Siga o style guide (Black, PEP 8)
- Adicione testes para novas features
- Mantenha coverage >80%
- Documente código com docstrings
- Use Conventional Commits

### Código de Conduta

Este projeto segue o [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

---

## 📝 Roadmap

### ✅ Versão 1.0 (Atual)
- [x] Gestão de alunos
- [x] Avaliações comportamentais
- [x] Geração de atividades com IA
- [x] Sistema de recomendação
- [x] Dashboards e relatórios
- [x] LGPD compliance

### 🚧 Versão 1.1 (Q2 2025)
- [ ] Aplicativo mobile (React Native)
- [ ] Gamificação de atividades
- [ ] Integração com LMS (Moodle, Canvas)
- [ ] Suporte a múltiplos idiomas
- [ ] API pública com rate limiting

### 🔮 Versão 2.0 (Q4 2025)
- [ ] Análise de sentimentos em texto livre
- [ ] Reconhecimento de padrões em desenhos
- [ ] Assistente virtual com voz
- [ ] Rede social para professores
- [ ] Marketplace de atividades

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.
```
MIT License

Copyright (c) 2025 EduAutismo IA Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 📞 Contato/WhatsApp

(81) 98484-5021
(83) 98832-9018

### Autor

**Cleyber Ferreira**
- 🎓 MBA em Inteligência Artificial e Big Data - USP
- 📧 Email: cleyber.silva@usp.com.br
- 💼 LinkedIn: [linkedin.com/in/cleybersilva](https://linkedin.com/in/cleybersilva)
- 🐙 GitHub: [@cleybersilva](https://github.com/cleybersilva)

### Projeto

- 🌐 Website: [eduautismo-ia.com.br](https://eduautismo-ia.com.br)
- 📖 Documentação: [docs.eduautismo-ia.com.br](https://docs.eduautismo-ia.com.br)
- 🐛 Issues: [github.com/cleybersilva/eduautismo-ia/issues](https://github.com/cleybersilva/eduautismo-ia/issues)
- 💬 Discussões: [github.com/cleybersilva/eduautismo-ia/discussions](https://github.com/cleybersilva/eduautismo-ia/discussions)

### Instituição

**UNIVERSIDADE DE SÃO PAULO (USP)**
- MBA em Inteligência Artificial e Big Data
- São Paulo, Brasil

---

## 🙏 Agradecimentos

- **USP** - Pela excelente formação em IA e Big Data
- **Prof. Dr. [Nome]** - Orientação acadêmica
- **OpenAI** - API GPT-4 para geração de conteúdo
- **AWS** - Infraestrutura cloud robusta
- **Comunidade Open Source** - Pelas incríveis ferramentas
- **Professores da Rede Pública** - Feedback valioso durante desenvolvimento
- **Famílias de alunos com TEA** - Inspiração e motivação

### Tecnologias Open Source Utilizadas

Agradecimentos especiais aos mantenedores de:
- [FastAPI](https://fastapi.tiangolo.com/) - Sebastián Ramírez
- [PostgreSQL](https://www.postgresql.org/) - PostgreSQL Global Development Group
- [scikit-learn](https://scikit-learn.org/) - scikit-learn developers
- [Docker](https://www.docker.com/) - Docker Inc.
- [Terraform](https://www.terraform.io/) - HashiCorp
- E centenas de outras bibliotecas Python

---

## 📊 Status do Projeto

![GitHub last commit](https://img.shields.io/github/last-commit/your-org/eduautismo-ia)
![GitHub issues](https://img.shields.io/github/issues/your-org/eduautismo-ia)
![GitHub pull requests](https://img.shields.io/github/issues-pr/your-org/eduautismo-ia)
![GitHub stars](https://img.shields.io/github/stars/your-org/eduautismo-ia?style=social)

### Métricas de Desenvolvimento

- **Cobertura de Testes**: 85%
- **Issues Abertas**: 5
- **Pull Requests**: 2
- **Contribuidores**: 3
- **Commits**: 250+
- **Linhas de Código**: ~15,000

---

## 🎓 Citação

Se você usar este projeto em sua pesquisa ou trabalho acadêmico, por favor cite:
```bibtex
@mastersthesis{silva2025eduautismo,
  title={EduAutismo IA: Plataforma Inteligente de Apoio Pedagógico para Alunos com TEA},
  author={Silva, Cleyber},
  year={2025},
  school={Universidade de São Paulo},
  type={Trabalho de Conclusão de Curso (MBA)},
  address={São Paulo, Brasil}
}
```

---

<div align="center">

### ⭐ Se este projeto foi útil, considere dar uma estrela!

**Feito com ❤️ para inclusão educacional**

[⬆ Voltar ao topo](#-eduautismo-ia)

</div>