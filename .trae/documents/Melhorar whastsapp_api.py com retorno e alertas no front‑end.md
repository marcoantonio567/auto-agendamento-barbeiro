## Objetivo
- Tornar `send_mensage` robusta e útil: retornar sucesso/erro estruturado e permitir que as views informem o front‑end (via mensagens Django ou JSON) quando a requisição falhar.

## Diagnóstico Atual
- `send_mensage` apenas imprime e retorna `None`; não valida nem propaga erros.
- Em `dashboard/views.py` (`admin_shift_hour`), a chamada é envolvida em `try/except ... pass`, então falhas são silenciosas e o usuário sempre vê sucesso.

## Alterações na Função `send_mensage`
1. Validação de entrada
   - Normalizar telefone (somente dígitos), aceitar/validar tamanho e prefixar código do país (`55`) apenas se não presente.
2. Configuração
   - Ler `EVOLUTION_API_URL` e `EVOLUTION_API_KEY` via `decouple.config` (como já faz) e validar chave ausente com retorno de erro.
3. Requisição HTTP
   - Usar `requests.post` com `timeout` (ex.: 10s) e `response.raise_for_status()` para mapear HTTP 4xx/5xx.
4. Tratamento de exceções
   - Capturar `requests.exceptions.Timeout`, `ConnectionError`, `HTTPError` e retornar estrutura de erro com códigos/mensagens amigáveis.
5. Estrutura de retorno
   - Retornar `dict` com formato:
     - Sucesso: `{ "ok": true, "status_code": <int>, "data": <obj opcional> }`
     - Erro: `{ "ok": false, "status_code": <int|None>, "error": <string>, "details": <string opcional> }`
6. Logging
   - Substituir `print` por `logging` (níveis `info`/`warning`/`error`).

## Integração com Views (Django)
1. Atualizar `dashboard/views.py:admin_shift_hour`
   - Remover `except ... pass`.
   - Consumir o retorno de `send_mensage`:
     - Se `ok` for `true`: `messages.success` com confirmação de envio.
     - Se `ok` for `false`: `messages.error` com motivo (ex.: chave ausente, timeout, número inválido, HTTP 401/403/5xx).
2. Propagar status HTTP adequado (opcional)
   - Para rotas API, retornar `JsonResponse` com `status=400/401/500` e o payload de erro.

## Endpoint Opcional para AJAX
- Criar endpoint `POST /api/whatsapp/send` que recebe `{ number, text }` e responde com JSON seguindo a estrutura de retorno.
- Front‑end pode exibir toast/modal de erro sem necessidade de redirect.

## Tratamento de Erros Cobertos
- Chave ausente (`EVOLUTION_API_KEY` vazio).
- URL inválida/serviço fora (`ConnectionError`).
- Timeout.
- Respostas HTTP não‑2xx (inclui 401/403/404/5xx).
- Número inválido (tamanho/formato).

## Testes e Validação
- Testes manuais com cenários:
  - Sucesso (API key válida e número correto).
  - Falha por API key vazia.
  - Timeout simulando indisponibilidade.
  - HTTP 401/403 com chave inválida.
- Verificação visual
  - Em fluxo de página: checar `messages.error/success` após ação.
  - Em AJAX: checar JSON e exibir toast.

## Impacto e Compatibilidade
- Não altera a assinatura pública (continua sendo chamada a mesma função), mas agora retorna estrutura útil.
- Mudança na view para usar o retorno é necessária para o usuário ver o erro.
- Sem dependências novas além de `logging` (padrão da biblioteca).