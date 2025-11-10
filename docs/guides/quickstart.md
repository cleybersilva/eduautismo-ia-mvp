# 🚀 Guia de Início Rápido

Este guia fornece instruções passo a passo para começar a trabalhar com o projeto EduAutismo IA.

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Node.js 18+
- AWS CLI configurado (para recursos em nuvem)

## Instalação Rápida

1. Clone o repositório:
```bash
git clone https://github.com/cleybersilva/eduautismo-ia-mvp.git
cd eduautismo-ia-mvp
```

2. Execute o script de instalação rápida:
```bash
./scripts/setup/quick-start.sh
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Inicie os serviços:
```bash
docker-compose up -d
```

## Verificação da Instalação

Execute o script de verificação para garantir que tudo está funcionando corretamente:
```bash
./scripts/setup/check-requirements.sh
```

## Próximos Passos

1. [Configuração do Ambiente de Desenvolvimento](./development-setup.md)
2. [Guia de Contribuição](./contributing.md)
3. [Documentação da API](./api-docs.md)

## Problemas Comuns

Consulte nossa [página de troubleshooting](./troubleshooting.md) para soluções de problemas comuns.

## Links Úteis

- [Documentação Completa](./INDEX.md)
- [Guia de Desenvolvimento](./development-guide.md)
- [FAQ](./faq.md)