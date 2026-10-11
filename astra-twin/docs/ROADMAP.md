# Roteiro de evolução

## MVP — implementado nesta branch
- Integração com Responses API.
- Memória local SQLite por sessão.
- Configuração validada e limites de entrada/histórico.
- Interface CLI e testes unitários offline.

## Fase seguinte — fiabilidade
- [ ] Executar testes numa máquina de desenvolvimento com Python 3.11+.
- [ ] Adicionar testes com cliente API simulado e falhas de rede.
- [ ] Registar latência, tokens e custo quando os dados de utilização estiverem disponíveis.
- [ ] Criar avaliação de qualidade com casos de teste versionados.
- [ ] Adicionar timeouts/retries limitados e política de backoff.
- [ ] Criar migrações de esquema da memória e política de retenção.

## Fase de ferramentas controladas
- [ ] Especificar contratos JSON para cada ferramenta.
- [ ] Criar allowlist de ferramentas e validação determinística de argumentos.
- [ ] Executar ferramentas em processo/container isolado com permissões mínimas.
- [ ] Pedir aprovação humana para ações externas, destrutivas ou irreversíveis.
- [ ] Criar testes de prompt injection, conteúdo externo malicioso e abuso de ferramentas.

## Fase de produção
- [ ] Autenticação e autorização por utilizador.
- [ ] Armazenamento seguro de segredos.
- [ ] Métricas, logs estruturados e alertas.
- [ ] Políticas de privacidade, exportação e eliminação de dados.
- [ ] Avaliação de fallback para modelo alternativo.
- [ ] CI para lint, testes e análise de dependências.

## Critérios mínimos de lançamento
- Todos os testes automáticos passam.
- Nenhum segredo no repositório.
- Custos por tarefa medidos num conjunto representativo.
- Falhas de API e entradas excessivas tratadas sem perda de estado.
- Ferramentas externas desativadas por predefinição.
