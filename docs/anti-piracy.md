# Uso Aceitável e Proteção de Secrets

## Licença

Este projeto é licenciado sob MIT. Você pode usar, modificar e distribuir livremente,
desde que mantenha a atribuição de copyright no arquivo LICENSE.

## Proteção de API Keys e Secrets

NUNCA cometa arquivos com dados sensíveis:
- `.env` está no `.gitignore` — jamais remova essa linha
- API keys devem estar SEMPRE em variáveis de ambiente, nunca hardcoded
- O CI (security-scan.yml) roda Gitleaks em todo PR para detectar secrets acidentais
- Se uma key for exposta acidentalmente: revogue-a IMEDIATAMENTE no portal do provedor

## Uso Responsável das APIs

- **Reddit PRAW:** respeite rate limits (60 req/min no plano free)
- **Brave Search:** plano free = 2.000 req/mês. Ciclos de 2h = ~360 req/mês
- **Playwright:** use apenas headless. Respeite robots.txt dos sites

## O que NÃO fazer

- Não use este projeto para spam ou scraping agressivo
- Não revenda dados coletados sem atribuição
- Não remova avisos de copyright do código
- Não compartilhe seu .env com outras pessoas
