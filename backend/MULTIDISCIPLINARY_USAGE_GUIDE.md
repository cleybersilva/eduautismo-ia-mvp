# 📚 Guia de Uso - MVP 3.0 Multidisciplinar

> **Versão**: 3.0.0
> **Data**: 2025-12-01
> **Autor**: Cleyber Silva
> **Projeto**: EduAutismo IA - Plataforma Multidisciplinar

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Quick Start](#quick-start)
3. [Enums e Constantes](#enums-e-constantes)
4. [Endpoints da API](#endpoints-da-api)
5. [Exemplos por Disciplina](#exemplos-por-disciplina)
6. [Integração BNCC](#integração-bncc)
7. [Guia de Frontend](#guia-de-frontend)
8. [Casos de Uso Comuns](#casos-de-uso-comuns)
9. [Referência Rápida](#referência-rápida)

---

## Visão Geral

O **MVP 3.0** transforma a plataforma EduAutismo IA de uma solução especializada em TEA para uma **plataforma multidisciplinar completa** que suporta:

- ✅ **25 disciplinas** do currículo brasileiro
- ✅ **18 níveis escolares** (Infantil → EJA)
- ✅ **10 tipos pedagógicos** de atividades
- ✅ **Integração com BNCC** (Base Nacional Comum Curricular)
- ✅ **100% compatível** com sistema v1.0 (TEA-only)

### Características Principais

| Recurso | Descrição |
|---------|-----------|
| **Subject** | 25 disciplinas (Matemática, Português, Ciências, etc.) |
| **GradeLevel** | 18 níveis (Infantil Maternal → EJA Médio 3) |
| **PedagogicalType** | 10 formatos (Exercício, Jogo, Projeto, etc.) |
| **BNCC** | Códigos de competências (ex: "EF03MA01") |
| **AI Context** | Prompts específicos por disciplina |

---

## Quick Start

### 1. Geração Básica (Compatível com v1.0)

```bash
# Geração tradicional (ainda funciona!)
curl -X POST "http://localhost:8000/api/v1/activities/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Atividade de Cores",
    "description": "Reconhecer cores primárias",
    "activity_type": "cognitive",
    "difficulty": "easy",
    "duration_minutes": 30,
    "objectives": ["Identificar cores"],
    "materials": ["Cartões coloridos"],
    "instructions": ["Mostrar cartão", "Perguntar cor"]
  }'
```

### 2. Geração Multidisciplinar (v3.0)

```bash
# Nova geração com contexto multidisciplinar
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 45,
    "subject": "matematica",
    "grade_level": "fundamental_1_3ano",
    "pedagogical_type": "exercicio",
    "theme": "adição de números até 100",
    "bncc_competencies": ["EF03MA06", "EF03MA07"]
  }'
```

### 3. Buscar Disciplinas Disponíveis

```bash
# Listar todas as 25 disciplinas
curl -X GET "http://localhost:8000/api/v1/activities/meta/subjects" \
  -H "Authorization: Bearer $TOKEN"

# Resposta:
{
  "matematica": "Matemática",
  "portugues": "Português",
  "ciencias": "Ciências",
  ...
}
```

### 4. Buscar por BNCC

```bash
# Encontrar atividades com competência específica
curl -X GET "http://localhost:8000/api/v1/activities/search/bncc/EF03MA06" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Enums e Constantes

### Subject (25 Disciplinas)

#### Núcleo Comum (8)
```python
Subject.MATEMATICA          # "matematica"       → "Matemática"
Subject.PORTUGUES           # "portugues"        → "Português"
Subject.LITERATURA          # "literatura"       → "Literatura"
Subject.REDACAO             # "redacao"          → "Redação"
Subject.CIENCIAS            # "ciencias"         → "Ciências"
Subject.HISTORIA            # "historia"         → "História"
Subject.GEOGRAFIA           # "geografia"        → "Geografia"
Subject.INGLES              # "ingles"           → "Inglês"
```

#### Artes e Educação Física (6)
```python
Subject.ARTE                # "arte"             → "Arte"
Subject.EDUCACAO_FISICA     # "educacao_fisica"  → "Educação Física"
Subject.MUSICA              # "musica"           → "Música"
Subject.ARTES_VISUAIS       # "artes_visuais"    → "Artes Visuais"
Subject.TEATRO              # "teatro"           → "Teatro"
Subject.DANCA               # "danca"            → "Dança"
```

#### Ensino Médio (5)
```python
Subject.BIOLOGIA            # "biologia"         → "Biologia"
Subject.FISICA              # "fisica"           → "Física"
Subject.QUIMICA             # "quimica"          → "Química"
Subject.FILOSOFIA           # "filosofia"        → "Filosofia"
Subject.SOCIOLOGIA          # "sociologia"       → "Sociologia"
```

#### Tecnologia e Transversais (6)
```python
Subject.INFORMATICA              # "informatica"              → "Informática"
Subject.ESPANHOL                 # "espanhol"                 → "Espanhol"
Subject.EDUCACAO_PROFISSIONAL    # "educacao_profissional"    → "Educação Profissional"
Subject.EMPREENDEDORISMO         # "empreendedorismo"         → "Empreendedorismo"
Subject.EDUCACAO_FINANCEIRA      # "educacao_financeira"      → "Educação Financeira"
Subject.EDUCACAO_AMBIENTAL       # "educacao_ambiental"       → "Educação Ambiental"
```

### GradeLevel (18 Níveis)

#### Educação Infantil (3 níveis)
```python
GradeLevel.INFANTIL_MATERNAL    # "infantil_maternal"    → "Infantil - Maternal"
GradeLevel.INFANTIL_1           # "infantil_1"           → "Infantil I"
GradeLevel.INFANTIL_2           # "infantil_2"           → "Infantil II"
```

#### Fundamental I (5 níveis)
```python
GradeLevel.FUNDAMENTAL_1_1ANO   # "fundamental_1_1ano"   → "1º Ano - Fundamental I"
GradeLevel.FUNDAMENTAL_1_2ANO   # "fundamental_1_2ano"   → "2º Ano - Fundamental I"
GradeLevel.FUNDAMENTAL_1_3ANO   # "fundamental_1_3ano"   → "3º Ano - Fundamental I"
GradeLevel.FUNDAMENTAL_1_4ANO   # "fundamental_1_4ano"   → "4º Ano - Fundamental I"
GradeLevel.FUNDAMENTAL_1_5ANO   # "fundamental_1_5ano"   → "5º Ano - Fundamental I"
```

#### Fundamental II (4 níveis)
```python
GradeLevel.FUNDAMENTAL_2_6ANO   # "fundamental_2_6ano"   → "6º Ano - Fundamental II"
GradeLevel.FUNDAMENTAL_2_7ANO   # "fundamental_2_7ano"   → "7º Ano - Fundamental II"
GradeLevel.FUNDAMENTAL_2_8ANO   # "fundamental_2_8ano"   → "8º Ano - Fundamental II"
GradeLevel.FUNDAMENTAL_2_9ANO   # "fundamental_2_9ano"   → "9º Ano - Fundamental II"
```

#### Ensino Médio (3 níveis)
```python
GradeLevel.MEDIO_1ANO           # "medio_1ano"           → "1ª Série - Ensino Médio"
GradeLevel.MEDIO_2ANO           # "medio_2ano"           → "2ª Série - Ensino Médio"
GradeLevel.MEDIO_3ANO           # "medio_3ano"           → "3ª Série - Ensino Médio"
```

#### EJA (3 níveis)
```python
GradeLevel.EJA_FUNDAMENTAL      # "eja_fundamental"      → "EJA - Ensino Fundamental"
GradeLevel.EJA_MEDIO_1          # "eja_medio_1"          → "EJA - Ensino Médio I"
GradeLevel.EJA_MEDIO_3          # "eja_medio_3"          → "EJA - Ensino Médio III"
```

### PedagogicalActivityType (10 Tipos)

```python
PedagogicalActivityType.EXERCICIO       # "exercicio"       → "Exercício"
PedagogicalActivityType.JOGO_EDUCATIVO  # "jogo_educativo"  → "Jogo Educativo"
PedagogicalActivityType.PROJETO         # "projeto"         → "Projeto"
PedagogicalActivityType.LEITURA         # "leitura"         → "Leitura"
PedagogicalActivityType.ARTE_MANUAL     # "arte_manual"     → "Arte Manual"
PedagogicalActivityType.EXPERIMENTO     # "experimento"     → "Experimento"
PedagogicalActivityType.DEBATE          # "debate"          → "Debate"
PedagogicalActivityType.PESQUISA        # "pesquisa"        → "Pesquisa"
PedagogicalActivityType.APRESENTACAO    # "apresentacao"    → "Apresentação"
PedagogicalActivityType.AVALIACAO       # "avaliacao"       → "Avaliação"
```

### Helper Functions

```python
from app.utils.constants import (
    get_subjects,
    get_grade_levels,
    get_pedagogical_activity_types,
    get_subject_display_name,
    get_grade_level_display_name,
    get_subjects_by_grade_level,
)

# Listar todas as disciplinas
subjects = get_subjects()
# ['matematica', 'portugues', 'ciencias', ...]

# Obter nome de exibição
display = get_subject_display_name(Subject.MATEMATICA)
# "Matemática"

# Obter disciplinas apropriadas para um nível
subjects_3ano = get_subjects_by_grade_level(GradeLevel.FUNDAMENTAL_1_3ANO)
# [Subject.MATEMATICA, Subject.PORTUGUES, Subject.CIENCIAS, ...]
```

---

## Endpoints da API

### 1. POST /activities/generate-multidisciplinary

**Descrição**: Gera atividade multidisciplinar personalizada usando IA com contexto específico da disciplina.

**Request Body**:
```json
{
  "student_id": "uuid",
  "activity_type": "cognitive" | "social" | "motor" | "communication" | "sensory",
  "difficulty": "easy" | "medium" | "hard",
  "duration_minutes": 10-240,
  "subject": "matematica",
  "grade_level": "fundamental_1_3ano",
  "pedagogical_type": "exercicio",
  "theme": "opcional - tema específico",
  "bncc_competencies": ["EF03MA06", "EF03MA07"]
}
```

**Response (201 Created)**:
```json
{
  "id": "activity-uuid",
  "student_id": "student-uuid",
  "title": "Adição até 100: Aventura dos Números",
  "description": "Exercício de adição adaptado para TEA...",
  "activity_type": "cognitive",
  "difficulty": "medium",
  "duration_minutes": 45,
  "objectives": [
    "Compreender adição com reagrupamento",
    "Resolver problemas até 100"
  ],
  "materials": [
    "Material dourado",
    "Fichas numéricas",
    "Cartões visuais"
  ],
  "instructions": [
    "1. Apresentar material dourado",
    "2. Demonstrar reagrupamento visual",
    "3. Praticar com exemplos concretos"
  ],
  "adaptations": [
    "Usar apoios visuais coloridos",
    "Permitir uso de manipuláveis",
    "Reduzir quantidade de problemas se necessário"
  ],
  "subject": "matematica",
  "grade_level": "fundamental_1_3ano",
  "pedagogical_type": "exercicio",
  "bncc_competencies": ["EF03MA06", "EF03MA07"],
  "generated_by_ai": true,
  "created_at": "2025-12-01T10:00:00Z"
}
```

**Exemplo cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 45,
    "subject": "matematica",
    "grade_level": "fundamental_1_3ano",
    "pedagogical_type": "exercicio",
    "theme": "adição com reagrupamento",
    "bncc_competencies": ["EF03MA06"]
  }'
```

---

### 2. GET /activities/search/bncc/{bncc_code}

**Descrição**: Busca atividades por código BNCC específico.

**Path Parameters**:
- `bncc_code`: Código BNCC (ex: "EF03MA06")

**Query Parameters**:
- `skip`: Offset para paginação (padrão: 0)
- `limit`: Limite de resultados (padrão: 100)

**Response (200 OK)**:
```json
[
  {
    "id": "activity-uuid-1",
    "title": "Adição até 100",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 45,
    "subject": "matematica",
    "grade_level": "fundamental_1_3ano",
    "pedagogical_type": "exercicio",
    "generated_by_ai": true,
    "student_id": "student-uuid"
  }
]
```

**Exemplo cURL**:
```bash
# Buscar todas atividades com EF03MA06
curl -X GET "http://localhost:8000/api/v1/activities/search/bncc/EF03MA06" \
  -H "Authorization: Bearer $TOKEN"

# Com paginação
curl -X GET "http://localhost:8000/api/v1/activities/search/bncc/EF03MA06?skip=0&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3. GET /activities/meta/subjects

**Descrição**: Lista todas as 25 disciplinas disponíveis.

**Response (200 OK)**:
```json
{
  "matematica": "Matemática",
  "portugues": "Português",
  "literatura": "Literatura",
  "redacao": "Redação",
  "ciencias": "Ciências",
  "historia": "História",
  "geografia": "Geografia",
  "arte": "Arte",
  "educacao_fisica": "Educação Física",
  "musica": "Música",
  "ingles": "Inglês",
  "espanhol": "Espanhol",
  "biologia": "Biologia",
  "fisica": "Física",
  "quimica": "Química",
  "filosofia": "Filosofia",
  "sociologia": "Sociologia",
  "informatica": "Informática",
  "artes_visuais": "Artes Visuais",
  "teatro": "Teatro",
  "danca": "Dança",
  "educacao_profissional": "Educação Profissional",
  "empreendedorismo": "Empreendedorismo",
  "educacao_financeira": "Educação Financeira",
  "educacao_ambiental": "Educação Ambiental"
}
```

**Exemplo cURL**:
```bash
curl -X GET "http://localhost:8000/api/v1/activities/meta/subjects" \
  -H "Authorization: Bearer $TOKEN"
```

**Uso no Frontend**:
```javascript
// Preencher dropdown de disciplinas
const response = await fetch('/api/v1/activities/meta/subjects', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const subjects = await response.json();

// subjects = { "matematica": "Matemática", ... }
Object.entries(subjects).forEach(([code, name]) => {
  console.log(`${code} → ${name}`);
});
```

---

### 4. GET /activities/meta/grade-levels

**Descrição**: Lista todos os 18 níveis escolares disponíveis.

**Response (200 OK)**:
```json
{
  "infantil_maternal": "Infantil - Maternal",
  "infantil_1": "Infantil I",
  "infantil_2": "Infantil II",
  "fundamental_1_1ano": "1º Ano - Fundamental I",
  "fundamental_1_2ano": "2º Ano - Fundamental I",
  "fundamental_1_3ano": "3º Ano - Fundamental I",
  "fundamental_1_4ano": "4º Ano - Fundamental I",
  "fundamental_1_5ano": "5º Ano - Fundamental I",
  "fundamental_2_6ano": "6º Ano - Fundamental II",
  "fundamental_2_7ano": "7º Ano - Fundamental II",
  "fundamental_2_8ano": "8º Ano - Fundamental II",
  "fundamental_2_9ano": "9º Ano - Fundamental II",
  "medio_1ano": "1ª Série - Ensino Médio",
  "medio_2ano": "2ª Série - Ensino Médio",
  "medio_3ano": "3ª Série - Ensino Médio",
  "eja_fundamental": "EJA - Ensino Fundamental",
  "eja_medio_1": "EJA - Ensino Médio I",
  "eja_medio_3": "EJA - Ensino Médio III"
}
```

**Exemplo cURL**:
```bash
curl -X GET "http://localhost:8000/api/v1/activities/meta/grade-levels" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5. GET /activities/search (Enhanced)

**Descrição**: Busca avançada com múltiplos filtros multidisciplinares.

**Query Parameters**:
```
# Filtros v1.0 (compatíveis)
?activity_type=cognitive
?difficulty=medium
?theme=cores
?generated_by_ai=true
?student_id=uuid

# Filtros v3.0 (novos)
?subject=matematica
?grade_level=fundamental_1_3ano
?pedagogical_type=exercicio
?has_bncc=true
?bncc_code=EF03MA06

# Paginação
?skip=0
?limit=20
```

**Exemplo 1: Buscar Matemática do 3º Ano**:
```bash
curl -X GET "http://localhost:8000/api/v1/activities/search?subject=matematica&grade_level=fundamental_1_3ano" \
  -H "Authorization: Bearer $TOKEN"
```

**Exemplo 2: Buscar Exercícios com BNCC**:
```bash
curl -X GET "http://localhost:8000/api/v1/activities/search?pedagogical_type=exercicio&has_bncc=true" \
  -H "Authorization: Bearer $TOKEN"
```

**Exemplo 3: Filtros Combinados**:
```bash
curl -X GET "http://localhost:8000/api/v1/activities/search?subject=ciencias&grade_level=fundamental_2_6ano&pedagogical_type=experimento&difficulty=medium" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK)**:
```json
[
  {
    "id": "uuid",
    "title": "Título da Atividade",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 45,
    "theme": "tema opcional",
    "generated_by_ai": true,
    "student_id": "student-uuid",
    "subject": "matematica",
    "grade_level": "fundamental_1_3ano",
    "pedagogical_type": "exercicio"
  }
]
```

---

## Exemplos por Disciplina

### Matemática (3º Ano)

```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 45,
    "subject": "matematica",
    "grade_level": "fundamental_1_3ano",
    "pedagogical_type": "exercicio",
    "theme": "multiplicação visual",
    "bncc_competencies": ["EF03MA07"]
  }'
```

**Contexto IA Aplicado**:
- Usa estratégias visuais e concretas (material dourado, blocos)
- Divide problemas complexos em passos menores
- Linguagem literal e precisa
- Rotinas previsíveis

---

### Português (Literatura - 5º Ano)

```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 60,
    "subject": "literatura",
    "grade_level": "fundamental_1_5ano",
    "pedagogical_type": "leitura",
    "theme": "fábulas e interpretação",
    "bncc_competencies": ["EF05LP15"]
  }'
```

**Contexto IA Aplicado**:
- Suporte visual para compreensão (ilustrações, organizadores gráficos)
- Vocabulário acessível com explicações claras
- Estrutura previsível (início, meio, fim bem definidos)
- Perguntas objetivas para interpretação

---

### Ciências (Experimento - 6º Ano)

```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 90,
    "subject": "ciencias",
    "grade_level": "fundamental_2_6ano",
    "pedagogical_type": "experimento",
    "theme": "fotossíntese e plantas",
    "bncc_competencies": ["EF06CI05"]
  }'
```

**Contexto IA Aplicado**:
- Protocolo experimental passo a passo com imagens
- Instruções claras e sequenciais
- Considerações sensoriais (sons, texturas, cheiros)
- Permite observação estruturada

---

### História (Projeto - 7º Ano)

```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "hard",
    "duration_minutes": 120,
    "subject": "historia",
    "grade_level": "fundamental_2_7ano",
    "pedagogical_type": "projeto",
    "theme": "Brasil Colonial - Ciclo do Açúcar",
    "bncc_competencies": ["EF07HI10"]
  }'
```

**Contexto IA Aplicado**:
- Linha do tempo visual clara
- Conexão com interesses específicos do aluno
- Fontes primárias adaptadas (textos simplificados)
- Estrutura de projeto com etapas bem definidas

---

### Geografia (Pesquisa - 8º Ano)

```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "medium",
    "duration_minutes": 90,
    "subject": "geografia",
    "grade_level": "fundamental_2_8ano",
    "pedagogical_type": "pesquisa",
    "theme": "urbanização brasileira",
    "bncc_competencies": ["EF08GE05"]
  }'
```

**Contexto IA Aplicado**:
- Mapas e recursos visuais claros
- Roteiro de pesquisa estruturado
- Fontes de dados organizadas
- Permite focos de interesse específicos

---

### Física (Experimento - Ensino Médio)

```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "cognitive",
    "difficulty": "hard",
    "duration_minutes": 120,
    "subject": "fisica",
    "grade_level": "medio_1ano",
    "pedagogical_type": "experimento",
    "theme": "leis de Newton - movimento",
    "bncc_competencies": ["EM13CNT301"]
  }'
```

**Contexto IA Aplicado**:
- Protocolo experimental detalhado
- Cálculos com suporte visual
- Relação entre teoria e prática clara
- Segurança e previsibilidade no experimento

---

### Arte (Arte Manual - Infantil)

```bash
curl -X POST "http://localhost:8000/api/v1/activities/generate-multidisciplinary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "activity_type": "sensory",
    "difficulty": "easy",
    "duration_minutes": 30,
    "subject": "arte",
    "grade_level": "infantil_2",
    "pedagogical_type": "arte_manual",
    "theme": "cores e texturas"
  }'
```

**Contexto IA Aplicado**:
- Atividades sensoriais graduais
- Materiais adaptados (sem texturas aversivas)
- Instruções visuais passo a passo
- Permite expressão não-verbal

---

## Integração BNCC

### O que é BNCC?

A **Base Nacional Comum Curricular (BNCC)** define competências e habilidades essenciais para cada etapa da educação brasileira.

**Formato dos Códigos**:
- `EF` = Ensino Fundamental
- `03` = 3º ano
- `MA` = Matemática
- `06` = Habilidade específica

Exemplo: `EF03MA06` = "Resolver e elaborar problemas de adição e subtração com significados de juntar, acrescentar, separar e retirar, com números de até três algarismos."

### Buscar Atividades por BNCC

```bash
# Buscar atividades com competência EF03MA06
curl -X GET "http://localhost:8000/api/v1/activities/search/bncc/EF03MA06" \
  -H "Authorization: Bearer $TOKEN"

# Buscar atividades com QUALQUER código BNCC
curl -X GET "http://localhost:8000/api/v1/activities/search?has_bncc=true" \
  -H "Authorization: Bearer $TOKEN"

# Buscar BNCC de Ciências do 6º ano
curl -X GET "http://localhost:8000/api/v1/activities/search?subject=ciencias&grade_level=fundamental_2_6ano&has_bncc=true" \
  -H "Authorization: Bearer $TOKEN"
```

### Gerar Atividade com BNCC

```json
{
  "student_id": "uuid",
  "subject": "matematica",
  "grade_level": "fundamental_1_3ano",
  "pedagogical_type": "exercicio",
  "bncc_competencies": [
    "EF03MA06",  // Adição e subtração
    "EF03MA07"   // Multiplicação
  ]
}
```

**A IA irá**:
1. Incorporar objetivos da BNCC na atividade
2. Alinhar instruções com competências específicas
3. Sugerir avaliação baseada em habilidades BNCC

### Competências BNCC Comuns

#### Matemática - 3º Ano
```
EF03MA06: Adição e subtração até 999
EF03MA07: Multiplicação (tabuadas)
EF03MA08: Divisão (metade, terça, quarta parte)
```

#### Português - 5º Ano
```
EF05LP15: Interpretação de textos literários
EF05LP26: Produção de narrativas
EF05LP27: Utilizar recursos de coesão
```

#### Ciências - 6º Ano
```
EF06CI05: Explicar fotossíntese
EF06CI06: Concluir sobre funcionamento do sistema respiratório
```

---

## Guia de Frontend

### Setup Inicial

```javascript
// api/activities.js
const API_BASE = 'http://localhost:8000/api/v1';

export const activityAPI = {
  // Gerar atividade multidisciplinar
  generateMultidisciplinary: async (data, token) => {
    const response = await fetch(`${API_BASE}/activities/generate-multidisciplinary`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erro ao gerar atividade');
    }

    return response.json();
  },

  // Buscar disciplinas
  getSubjects: async (token) => {
    const response = await fetch(`${API_BASE}/activities/meta/subjects`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  // Buscar níveis escolares
  getGradeLevels: async (token) => {
    const response = await fetch(`${API_BASE}/activities/meta/grade-levels`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  // Buscar por BNCC
  searchByBNCC: async (bnccCode, token) => {
    const response = await fetch(`${API_BASE}/activities/search/bncc/${bnccCode}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },

  // Busca avançada
  search: async (filters, token) => {
    const params = new URLSearchParams(filters).toString();
    const response = await fetch(`${API_BASE}/activities/search?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    return response.json();
  },
};
```

### Componente React - Formulário de Geração

```jsx
// components/ActivityGeneratorForm.jsx
import React, { useState, useEffect } from 'react';
import { activityAPI } from '../api/activities';

export default function ActivityGeneratorForm({ studentId, token }) {
  const [subjects, setSubjects] = useState({});
  const [gradeLevels, setGradeLevels] = useState({});
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    student_id: studentId,
    activity_type: 'cognitive',
    difficulty: 'medium',
    duration_minutes: 45,
    subject: '',
    grade_level: '',
    pedagogical_type: 'exercicio',
    theme: '',
    bncc_competencies: [],
  });

  // Carregar metadados
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const [subjectsData, gradeLevelsData] = await Promise.all([
          activityAPI.getSubjects(token),
          activityAPI.getGradeLevels(token),
        ]);
        setSubjects(subjectsData);
        setGradeLevels(gradeLevelsData);
      } catch (error) {
        console.error('Erro ao carregar metadados:', error);
      }
    };
    loadMetadata();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const activity = await activityAPI.generateMultidisciplinary(formData, token);
      console.log('Atividade gerada:', activity);
      // Redirecionar ou mostrar atividade
    } catch (error) {
      console.error('Erro ao gerar atividade:', error);
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Gerar Atividade Multidisciplinar</h2>

      {/* Disciplina */}
      <label>
        Disciplina:
        <select
          value={formData.subject}
          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
          required
        >
          <option value="">Selecione uma disciplina</option>
          {Object.entries(subjects).map(([code, name]) => (
            <option key={code} value={code}>{name}</option>
          ))}
        </select>
      </label>

      {/* Nível Escolar */}
      <label>
        Nível Escolar:
        <select
          value={formData.grade_level}
          onChange={(e) => setFormData({ ...formData, grade_level: e.target.value })}
          required
        >
          <option value="">Selecione um nível</option>
          {Object.entries(gradeLevels).map(([code, name]) => (
            <option key={code} value={code}>{name}</option>
          ))}
        </select>
      </label>

      {/* Tipo Pedagógico */}
      <label>
        Tipo de Atividade:
        <select
          value={formData.pedagogical_type}
          onChange={(e) => setFormData({ ...formData, pedagogical_type: e.target.value })}
        >
          <option value="exercicio">Exercício</option>
          <option value="jogo_educativo">Jogo Educativo</option>
          <option value="projeto">Projeto</option>
          <option value="leitura">Leitura</option>
          <option value="experimento">Experimento</option>
          <option value="debate">Debate</option>
          <option value="pesquisa">Pesquisa</option>
          <option value="apresentacao">Apresentação</option>
          <option value="avaliacao">Avaliação</option>
        </select>
      </label>

      {/* Dificuldade */}
      <label>
        Dificuldade:
        <select
          value={formData.difficulty}
          onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
        >
          <option value="easy">Fácil</option>
          <option value="medium">Médio</option>
          <option value="hard">Difícil</option>
        </select>
      </label>

      {/* Duração */}
      <label>
        Duração (minutos):
        <input
          type="number"
          min="10"
          max="240"
          value={formData.duration_minutes}
          onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
        />
      </label>

      {/* Tema (opcional) */}
      <label>
        Tema (opcional):
        <input
          type="text"
          value={formData.theme}
          onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
          placeholder="Ex: adição com reagrupamento"
        />
      </label>

      {/* BNCC (opcional) */}
      <label>
        Códigos BNCC (opcional):
        <input
          type="text"
          placeholder="EF03MA06, EF03MA07"
          onChange={(e) => {
            const codes = e.target.value.split(',').map(c => c.trim()).filter(Boolean);
            setFormData({ ...formData, bncc_competencies: codes });
          }}
        />
      </label>

      <button type="submit" disabled={loading}>
        {loading ? 'Gerando...' : 'Gerar Atividade'}
      </button>
    </form>
  );
}
```

### Componente React - Busca por BNCC

```jsx
// components/BNCCSearch.jsx
import React, { useState } from 'react';
import { activityAPI } from '../api/activities';

export default function BNCCSearch({ token }) {
  const [bnccCode, setBnccCode] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!bnccCode.trim()) return;

    setLoading(true);
    try {
      const activities = await activityAPI.searchByBNCC(bnccCode, token);
      setResults(activities);
    } catch (error) {
      console.error('Erro na busca:', error);
      alert('Erro ao buscar atividades');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Buscar por Código BNCC</h2>

      <input
        type="text"
        value={bnccCode}
        onChange={(e) => setBnccCode(e.target.value)}
        placeholder="Ex: EF03MA06"
      />

      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Buscando...' : 'Buscar'}
      </button>

      {results.length > 0 && (
        <div>
          <h3>{results.length} atividades encontradas</h3>
          <ul>
            {results.map((activity) => (
              <li key={activity.id}>
                <strong>{activity.title}</strong>
                <br />
                {activity.subject} - {activity.grade_level}
                <br />
                Duração: {activity.duration_minutes} min
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

### Componente React - Busca Avançada

```jsx
// components/AdvancedSearch.jsx
import React, { useState } from 'react';
import { activityAPI } from '../api/activities';

export default function AdvancedSearch({ token }) {
  const [filters, setFilters] = useState({
    subject: '',
    grade_level: '',
    pedagogical_type: '',
    has_bncc: '',
  });
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    // Remover filtros vazios
    const activeFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, value]) => value !== '')
    );

    const activities = await activityAPI.search(activeFilters, token);
    setResults(activities);
  };

  return (
    <div>
      <h2>Busca Avançada</h2>

      <select
        value={filters.subject}
        onChange={(e) => setFilters({ ...filters, subject: e.target.value })}
      >
        <option value="">Todas as disciplinas</option>
        <option value="matematica">Matemática</option>
        <option value="portugues">Português</option>
        {/* ... outras opções */}
      </select>

      <select
        value={filters.has_bncc}
        onChange={(e) => setFilters({ ...filters, has_bncc: e.target.value })}
      >
        <option value="">Com ou sem BNCC</option>
        <option value="true">Apenas com BNCC</option>
        <option value="false">Apenas sem BNCC</option>
      </select>

      <button onClick={handleSearch}>Buscar</button>

      {/* Exibir resultados */}
      <ul>
        {results.map((activity) => (
          <li key={activity.id}>{activity.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Casos de Uso Comuns

### Caso 1: Professor criando atividade de Matemática

**Cenário**: Professora Ana quer criar exercícios de multiplicação para seu aluno João (3º ano, TEA leve).

**Passo a Passo**:

1. **Carregar metadados**:
```javascript
const subjects = await activityAPI.getSubjects(token);
const gradeLevels = await activityAPI.getGradeLevels(token);
```

2. **Selecionar opções no form**:
- Disciplina: `matematica`
- Nível: `fundamental_1_3ano`
- Tipo: `exercicio`
- Dificuldade: `medium`
- Tema: "tabuada do 2 e 3"
- BNCC: `["EF03MA07"]`

3. **Gerar atividade**:
```javascript
const activity = await activityAPI.generateMultidisciplinary({
  student_id: joaoId,
  subject: 'matematica',
  grade_level: 'fundamental_1_3ano',
  pedagogical_type: 'exercicio',
  activity_type: 'cognitive',
  difficulty: 'medium',
  duration_minutes: 45,
  theme: 'tabuada do 2 e 3',
  bncc_competencies: ['EF03MA07'],
}, token);
```

4. **Receber atividade personalizada**:
- Título: "Aventura da Multiplicação: Tabuada Visual"
- Instruções adaptadas para TEA (visuais, passo a passo)
- Materiais concretos sugeridos (blocos, fichas)
- Alinhada com BNCC EF03MA07

---

### Caso 2: Coordenadora buscando atividades por BNCC

**Cenário**: Coordenadora Maria precisa validar que todas as competências BNCC de Ciências do 6º ano estão sendo trabalhadas.

**Passo a Passo**:

1. **Buscar todas atividades de Ciências 6º ano com BNCC**:
```bash
curl -X GET "http://localhost:8000/api/v1/activities/search?subject=ciencias&grade_level=fundamental_2_6ano&has_bncc=true" \
  -H "Authorization: Bearer $TOKEN"
```

2. **Buscar competência específica**:
```bash
curl -X GET "http://localhost:8000/api/v1/activities/search/bncc/EF06CI05" \
  -H "Authorization: Bearer $TOKEN"
```

3. **Analisar resultados**:
- Ver quantas atividades existem para cada código BNCC
- Identificar lacunas (competências não cobertas)
- Gerar atividades para competências faltantes

---

### Caso 3: Geração em lote para múltiplos alunos

**Cenário**: Professor Carlos quer gerar atividades de História para 5 alunos diferentes, todos do 7º ano.

**Passo a Passo**:

```javascript
// Lista de alunos
const students = [
  { id: 'uuid1', name: 'Pedro', difficulty: 'easy' },
  { id: 'uuid2', name: 'Maria', difficulty: 'medium' },
  { id: 'uuid3', name: 'João', difficulty: 'medium' },
  { id: 'uuid4', name: 'Ana', difficulty: 'hard' },
  { id: 'uuid5', name: 'Lucas', difficulty: 'easy' },
];

// Template da atividade
const baseActivity = {
  subject: 'historia',
  grade_level: 'fundamental_2_7ano',
  pedagogical_type: 'projeto',
  activity_type: 'cognitive',
  duration_minutes: 120,
  theme: 'Brasil Colonial - Ciclo do Açúcar',
  bncc_competencies: ['EF07HI10'],
};

// Gerar para cada aluno
const activities = await Promise.all(
  students.map(student =>
    activityAPI.generateMultidisciplinary({
      ...baseActivity,
      student_id: student.id,
      difficulty: student.difficulty,
    }, token)
  )
);

console.log(`${activities.length} atividades geradas!`);
```

---

### Caso 4: Filtrar atividades existentes

**Cenário**: Professora Júlia quer reutilizar atividades de Português (Literatura) do 5º ano que já foram criadas.

**Passo a Passo**:

```javascript
// Buscar todas atividades de Literatura 5º ano
const activities = await activityAPI.search({
  subject: 'literatura',
  grade_level: 'fundamental_1_5ano',
  skip: 0,
  limit: 50,
}, token);

// Filtrar por tipo pedagógico no frontend
const leituras = activities.filter(a => a.pedagogical_type === 'leitura');
const projetos = activities.filter(a => a.pedagogical_type === 'projeto');

console.log(`${leituras.length} atividades de leitura encontradas`);
console.log(`${projetos.length} projetos encontrados`);
```

---

## Referência Rápida

### Endpoints Resumidos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/activities/generate-multidisciplinary` | Gerar atividade v3.0 |
| `GET` | `/activities/search/bncc/{code}` | Buscar por BNCC |
| `GET` | `/activities/meta/subjects` | Listar 25 disciplinas |
| `GET` | `/activities/meta/grade-levels` | Listar 18 níveis |
| `GET` | `/activities/search` | Busca avançada |

### Enums Resumidos

| Enum | Valores | Total |
|------|---------|-------|
| `Subject` | matematica, portugues, ciencias, ... | 25 |
| `GradeLevel` | infantil_1, fundamental_1_3ano, medio_1ano, ... | 18 |
| `PedagogicalActivityType` | exercicio, jogo_educativo, projeto, ... | 10 |

### Códigos BNCC Comuns

| Disciplina | Código | Descrição |
|------------|--------|-----------|
| Matemática 3º | `EF03MA06` | Adição e subtração |
| Matemática 3º | `EF03MA07` | Multiplicação |
| Português 5º | `EF05LP15` | Interpretação literária |
| Ciências 6º | `EF06CI05` | Fotossíntese |
| História 7º | `EF07HI10` | Brasil Colonial |
| Geografia 8º | `EF08GE05` | Urbanização |

### Response Codes

| Code | Significado |
|------|-------------|
| `200` | OK - Busca bem-sucedida |
| `201` | Created - Atividade gerada |
| `400` | Bad Request - Dados inválidos |
| `401` | Unauthorized - Token inválido |
| `404` | Not Found - Aluno não existe |
| `500` | Internal Error - Erro no servidor |

### Compatibilidade

| Feature | v1.0 (TEA) | v3.0 (Multi) |
|---------|------------|--------------|
| Campos básicos | ✅ | ✅ |
| activity_type | ✅ | ✅ |
| difficulty | ✅ | ✅ |
| subject | ❌ | ✅ |
| grade_level | ❌ | ✅ |
| pedagogical_type | ❌ | ✅ |
| bncc_competencies | ❌ | ✅ |

**Migração**: Atividades v1.0 continuam funcionando sem alterações. Campos v3.0 são opcionais.

---

## 🎉 Conclusão

O **MVP 3.0** expande significativamente as capacidades da plataforma EduAutismo IA, transformando-a em uma solução multidisciplinar completa enquanto mantém o foco em adaptações para TEA.

### Próximos Passos

1. **Explorar novos endpoints** com diferentes combinações de disciplinas
2. **Integrar frontend** com os componentes React fornecidos
3. **Testar geração de atividades** para diferentes perfis de alunos
4. **Mapear competências BNCC** para o currículo da sua instituição
5. **Feedback e iteração** para melhorar contextos disciplinares da IA

### Suporte

- **Documentação Técnica**: `CLAUDE.md`
- **Plano de Migração**: `MVP_3.0_MIGRATION_PLAN.md`
- **Testes**: `backend/tests/integration/test_multidisciplinary_api.py`
- **Issues**: GitHub Issues

---

**Versão**: 3.0.0
**Data de Lançamento**: 2025-12-01
**Autor**: Cleyber Silva
**Licença**: Projeto Acadêmico - TCC MBA IA & Big Data USP
