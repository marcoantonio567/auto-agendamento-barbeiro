# Sistema de Gerenciamento para Barbearia

<p align="center">
  <a href="README.md">
    <img src="https://img.shields.io/badge/English-0A66C2?style=for-the-badge&logo=readme&logoColor=white" alt="English README">
  </a>
  <a href="README.pt-BR.md">
    <img src="https://img.shields.io/badge/Portugues-2E7D32?style=for-the-badge&logo=readme&logoColor=white" alt="README em Portugues">
  </a>
</p>

Sistema de gerenciamento para barbearias, desenvolvido em Django. Inclui agendamento online, painel administrativo, integracao de pagamentos via Pix (AbacatePay) e lembretes automaticos via WhatsApp (Evolution API).

## Capturas de tela

### Agendamento online

![Selecao de servico](docs/images/agendamento-servico.png)

![Selecao de barbeiro](docs/images/agendamento-barbeiro.png)

![Horarios disponiveis](docs/images/agendamento-horarios.png)

### Painel administrativo

![Historico de agendamentos](docs/images/painel-historico.png)

![Painel financeiro](docs/images/painel-financeiro.png)

## Funcionalidades

- **Agendamento online:** Interface para clientes agendarem horarios, escolhendo barbeiro, servico, data e horario.
- **Painel administrativo:** Painel para gerenciar agendamentos, visualizar historico financeiro e metricas.
- **Pagamentos via Pix:** Geracao de QR Code Pix por meio da integracao com a AbacatePay.
- **Lembretes via WhatsApp:** Envio automatico de lembretes de agendamento pela Evolution API.
- **Gerenciamento de usuarios:** Controle de acesso e perfis de usuario.

## Tecnologias utilizadas

- **Backend:** Python 3, Django 5
- **Banco de dados:** SQLite (padrao), extensivel para PostgreSQL
- **Conteinerizacao:** Docker, Docker Compose
- **Servidor web:** Nginx, uWSGI
- **Integracoes:**
  - [Evolution API](https://github.com/EvolutionAPI/evolution-api) (WhatsApp)
  - [AbacatePay](https://abacatepay.com/) (Pagamentos Pix)

## Pre-requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Instalacao e execucao

1. **Clone o repositorio:**

```bash
git clone https://github.com/your-username/barbershop.git
cd barbershop
```

2. **Configure as variaveis de ambiente:**

Crie um arquivo `.env` na raiz do projeto com as seguintes variaveis:

```env
SECRET_KEY=your_secret_django_key
DEBUG=True

# Configuracoes do token de autoatendimento
SELF_SERVICE_TOKEN_KEY=your_secret_token
REQUIRE_SELF_SERVICE_TOKEN=False

# Integracao com Evolution API (WhatsApp)
EVOLUTION_API_URL=http://evolution_api:8080
EVOLUTION_API_KEY=your_evolution_api_key
AUTHENTICATION_API_KEY=your_authentication_key

# Integracao com AbacatePay
ABACATEPAY_KEY=your_abacatepay_api_key
```

3. **Execute com Docker Compose:**

```bash
docker-compose up --build
```

O sistema iniciara os seguintes servicos:

- `app`: Aplicacao Django (porta 8000)
- `nginx`: Servidor web (porta 80)
- `evolution-api`: API do WhatsApp (porta 8082)
- `reminder-worker`: Worker para envio de lembretes

4. **Acesse a aplicacao:**

- **Web:** http://localhost
- **Django Admin:** http://localhost/admin

## Estrutura do projeto

- `core/`: Configuracoes principais do projeto.
- `scheduling/`: App de agendamento e gerenciamento de horarios.
- `dashboard/`: Painel administrativo personalizado.
- `payments/`: Integracao com gateway de pagamento.
- `users/`: Gerenciamento e autenticacao de usuarios.
- `docker-compose.yml`: Orquestracao dos containers.

## Contribuicao

Contribuicoes sao bem-vindas! Fique a vontade para abrir issues ou enviar pull requests.

## Licenca

[MIT](LICENSE)
