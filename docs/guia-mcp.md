# Guia de Integração MCP

## O que é MCP?

Model Context Protocol (MCP) é um protocolo aberto que permite ao Claude Code
usar ferramentas externas (servidores MCP) diretamente nas conversas.

## MCP Configurado: Brave Search

O servidor `brave-search` permite que Claude Code faça buscas na web diretamente.

### Pré-requisito

Node.js 18+ instalado:
```bash
node --version
```

### Configuração no Claude Code

Adicione ao `.claude/settings.json` (já incluído no projeto):
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {"BRAVE_API_KEY": "${BRAVE_SEARCH_API_KEY}"}
    }
  }
}
```

### Verificar se está funcionando

No terminal do Claude Code, digite `/mcp` para listar servidores disponíveis.

### Adicionando outros servidores MCP

Consulte `github.com/modelcontextprotocol/servers` para servidores disponíveis.
Adicione novas entradas em `mcpServers` no `.claude/settings.json`.
