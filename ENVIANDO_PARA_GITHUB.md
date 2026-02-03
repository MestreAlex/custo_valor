# 📤 Instruções para Enviar para GitHub

## Pré-requisitos

- [ ] Conta no GitHub
- [ ] Git instalado (`git --version`)
- [ ] Autenticação SSH ou HTTPS configurada

## Passo 1: Criar Novo Repositório no GitHub

1. Acesse https://github.com/new
2. **Nome do repositório:** `custo_valor` (ou seu nome preferido)
3. **Descrição:** Sistema de análise de futebol com validação de entradas qualificadas
4. **Visibilidade:** Public ou Private (sua escolha)
5. ⚠️ **Importante:** NÃO inicialize com README, .gitignore ou LICENSE
6. Clique "Create repository"

## Passo 2: Conectar Repositório Local ao GitHub

Após criar o repositório vazio no GitHub, você receberá a URL. Copie e execute:

### Opção A: HTTPS (Mais fácil)
```bash
cd c:\Users\Alex Menezes\projetos\custo_valor

git remote add origin https://github.com/SEU-USUARIO/custo_valor.git
git branch -M main
git push -u origin main
```

### Opção B: SSH (Mais seguro)
```bash
cd c:\Users\Alex Menezes\projetos\custo_valor

git remote add origin git@github.com:SEU-USUARIO/custo_valor.git
git branch -M main
git push -u origin main
```

**Substitua `SEU-USUARIO` pelo seu username do GitHub.**

## Passo 3: Verificar se Enviou com Sucesso

```bash
git remote -v
```

Deve mostrar:
```
origin  https://github.com/SEU-USUARIO/custo_valor.git (fetch)
origin  https://github.com/SEU-USUARIO/custo_valor.git (push)
```

## ✅ Pronto!

Seu repositório está no GitHub em: `https://github.com/SEU-USUARIO/custo_valor`

## 📝 Próximos Commits (Futuro)

Após fazer alterações, execute:

```bash
# Ver mudanças
git status

# Adicionar todas as mudanças
git add .

# Fazer commit
git commit -m "Descrição das mudanças"

# Enviar para GitHub
git push
```

## 🔗 Compartilhar o Repositório

Copie o link: `https://github.com/SEU-USUARIO/custo_valor`

Você pode compartilhar com:
- Colegas (para colaboração)
- Na documentação
- Em portfolio/currículo

## 📊 Struktur do Repositório GitHub

Seu repositório conterá:

```
📦 custo_valor
 ┣ 🔧 Scripts de inicialização
 ┣ 🌐 Servidores
 ┣ 📊 Geradores HTML
 ┣ 📈 Scripts de análise
 ┣ 📁 Dados (exceto CSVs grandes - no .gitignore)
 ┣ 📖 Documentação completa
 ┣ ✅ requirements.txt
 ┣ ✅ .gitignore
 ┗ ✅ README.md
```

## 🆘 Troubleshooting

### Erro: "fatal: remote origin already exists"
```bash
git remote remove origin
# Depois execute o Passo 2 novamente
```

### Erro de Autenticação HTTPS
```bash
# Windows: Use Git Credential Manager
git config --global credential.helper wincred

# Depois execute git push novamente
```

### Erro de Autenticação SSH
```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu-email@example.com"

# Adicionar em: https://github.com/settings/ssh/new
# Copie o conteúdo de: C:\Users\seu-usuario\.ssh\id_ed25519.pub
```

## 📚 Recursos Úteis

- [GitHub Help: Create a repo](https://docs.github.com/en/get-started/quickstart/create-a-repo)
- [GitHub Help: Authentication](https://docs.github.com/en/authentication)
- [Git Cheat Sheet](https://github.github.com/training-kit/downloads/github-git-cheat-sheet.pdf)

---

**Versão:** 1.0  
**Data:** 3 de fevereiro de 2026  
**Status:** Pronto para enviar ✅
