# Guia de Skills Customizadas

## O que são Skills

Skills são arquivos Markdown em `.claude/skills/` que ensinam ao Claude Code
como executar tarefas específicas do projeto. Funcionam como "receitas" reutilizáveis.

## Estrutura de uma Skill

```markdown
---
name: nome-da-skill
description: O que essa skill faz
triggers:
  - "frase que ativa a skill"
---

# Nome da Skill

## Steps
1. Passo 1
   ```bash
   comando aqui
   ```
```

## Skills deste projeto

| Skill | Arquivo | Quando usar |
|-------|---------|-------------|
| `run-agent` | `.claude/skills/run-agent.md` | Executar ciclo manual |
| `add-source` | `.claude/skills/add-source.md` | Adicionar nova fonte |
| `debug-search` | `.claude/skills/debug-search.md` | Depurar busca vazia |

## Como Claude Code usa Skills

Quando você menciona um dos triggers numa conversa, Claude Code carrega
automaticamente a skill e segue os steps documentados.

## Criando uma nova Skill

1. Crie `.claude/skills/minha-skill.md`
2. Adicione frontmatter com `name`, `description`, `triggers`
3. Documente os passos com comandos exatos
4. Teste mencionando o trigger numa conversa com Claude Code
