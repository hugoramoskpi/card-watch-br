# Guia de Hooks

## O que são Hooks

Hooks são scripts executados automaticamente em eventos do Claude Code:
antes/depois de usar ferramentas (`PreToolUse`, `PostToolUse`), antes de parar, etc.

Configurados em `.claude/settings.json` na chave `"hooks"`.

## Hooks deste projeto

### pre-search (`hooks/pre-search.py`)
- **Quando:** antes de rodar o scheduler
- **O que faz:** valida que todas as API keys estão no `.env`
- **Por que:** evita ciclos que falham silenciosamente por falta de credenciais
- **Resultado:** exit code 0 = OK (continua), exit code 1 = bloqueia execução

### post-alert (`hooks/post-alert.py`)
- **Quando:** após rodar o scheduler
- **O que faz:** registra timestamp em `logs/alerts.log`
- **Por que:** auditoria de quando ciclos foram executados

## Estrutura no settings.json

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(python src/scheduler*)",
        "hooks": [{"type": "command", "command": "python hooks/pre-search.py"}]
      }
    ]
  }
}
```

## Criando um novo Hook

1. Crie o script em `hooks/meu-hook.py`
2. Adicione a entrada em `.claude/settings.json`
3. Teste manualmente: `python hooks/meu-hook.py`
4. exit code 0 = sucesso (não bloqueia), exit code 1 = bloqueia a ação
