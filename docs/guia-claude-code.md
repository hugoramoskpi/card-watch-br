# Guia de Claude Code — Boas Práticas

## O que é Claude Code

Claude Code é uma CLI interativa da Anthropic que auxilia no desenvolvimento de software.
Ele lê seu projeto, entende o contexto via CLAUDE.md e executa tarefas complexas autonomamente.

## Configuração Inicial no Projeto

1. Instale: `npm install -g @anthropic-ai/claude-code`
2. Na raiz do projeto: `claude` (abre a interface)
3. O CLAUDE.md na raiz é carregado automaticamente como contexto do projeto

## Boas Práticas

### CLAUDE.md
- Documente comandos essenciais, arquitetura e variáveis de ambiente
- Mantenha atualizado sempre que a stack mudar
- Seja conciso: Claude lê o arquivo a cada sessão

### Permissões (.claude/settings.json)
- Use `permissions.allow` para liberar comandos seguros (pytest, git, uvicorn)
- Nunca libere comandos destrutivos globalmente (rm -rf, drop table, etc.)

### Commits frequentes
- Faça commit após cada feature funcional testada
- Mensagens no formato: `feat:`, `fix:`, `docs:`, `chore:`, `ci:`

### Segurança
- `.env` nunca no git
- Use `.env.example` como template público
- CI escaneia secrets automaticamente

## Skills e Hooks

Ver `docs/guia-skills.md` e `docs/guia-hooks.md` para detalhes.
