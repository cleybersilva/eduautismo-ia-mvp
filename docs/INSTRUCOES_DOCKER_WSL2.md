# 🐳 Instruções: Configurar Docker Desktop com WSL2

## Problema Atual
```
The command 'docker-compose' could not be found in this WSL 2 distro.
We recommend to activate the WSL integration in Docker Desktop settings.
```

## ✅ Solução (5 minutos)

### Passo 1: Abrir Docker Desktop
1. Abra o **Docker Desktop** no Windows
2. Se não estiver instalado, baixe em: https://www.docker.com/products/docker-desktop

### Passo 2: Configurar WSL Integration
1. No Docker Desktop, clique no ícone de **Settings** (⚙️) no canto superior direito
2. No menu lateral, clique em **Resources**
3. Clique em **WSL Integration**

### Passo 3: Ativar Integração
4. Ative a opção: **"Enable integration with my default WSL distro"**
5. Na lista de distros disponíveis, marque a checkbox da sua distro Ubuntu
   - Exemplo: `Ubuntu` ou `Ubuntu-22.04`
6. Clique em **"Apply & Restart"**

### Passo 4: Aguardar Reinício
7. Docker Desktop irá reiniciar (aguarde ~30 segundos)
8. Verifique se o status mostra: **"Docker Desktop is running"**

### Passo 5: Validar no WSL
Volte ao terminal WSL e execute:

```bash
# Verificar se docker está disponível
docker --version
# Deve mostrar: Docker version 24.x.x

# Verificar se docker-compose está disponível
docker-compose --version
# Deve mostrar: Docker Compose version v2.x.x

# Verificar se Docker está rodando
docker ps
# Deve mostrar lista de containers (pode estar vazia)
```

## ✅ Confirmação de Sucesso

Se todos os comandos acima funcionarem sem erros, o Docker WSL2 está configurado corretamente!

## ❌ Troubleshooting

### Problema: "Cannot connect to the Docker daemon"
**Solução**:
1. Certifique-se que Docker Desktop está rodando no Windows
2. No Docker Desktop Settings, verifique se "Use the WSL 2 based engine" está marcado
3. Reinicie o WSL: `wsl --shutdown` e abra novamente

### Problema: Docker Desktop não inicia
**Solução**:
1. Certifique-se que WSL2 está instalado no Windows
2. Execute no PowerShell (como Admin):
   ```powershell
   wsl --set-default-version 2
   wsl --update
   ```
3. Reinicie o computador

### Problema: Distro não aparece na lista
**Solução**:
1. Verifique se sua distro está usando WSL2:
   ```powershell
   # No PowerShell:
   wsl -l -v
   ```
2. Se aparecer VERSION 1, converta para WSL2:
   ```powershell
   wsl --set-version Ubuntu 2
   ```

## 🎯 Próximo Passo

Após configurar o Docker WSL2, volte ao terminal e execute:

```bash
# Marcar tarefa como concluída
echo "✅ Docker WSL2 configurado com sucesso!"

# Continuar com próximos passos
cd /mnt/d/ENGINEER/VS_Code/eduautismo-ia-mvp
```

---

**⏰ Tempo estimado**: 5-10 minutos
**Dificuldade**: ⭐⭐☆☆☆ (Fácil)
