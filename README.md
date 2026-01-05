# Barbearia Management System

Sistema de gerenciamento para barbearias, desenvolvido em Django. Inclui agendamento online, dashboard administrativo, integração de pagamentos via Pix (AbacatePay) e lembretes automáticos via WhatsApp (Evolution API).

## 🚀 Funcionalidades

-   **Agendamento Online:** Interface para clientes agendarem horários, escolhendo barbeiro, serviço, data e hora.
-   **Dashboard Administrativo:** Painel para gerenciar agendamentos, visualizar histórico financeiro e métricas.
-   **Pagamentos Pix:** Geração de QR Code Pix via integração com AbacatePay.
-   **Lembretes WhatsApp:** Envio automático de lembretes de agendamento via Evolution API.
-   **Gestão de Usuários:** Controle de acesso e perfis de usuário.

## 🛠 Tecnologias Utilizadas

-   **Backend:** Python 3, Django 5
-   **Banco de Dados:** SQLite (padrão), extensível para PostgreSQL
-   **Containerização:** Docker, Docker Compose
-   **Servidor Web:** Nginx, uWSGI
-   **Integrações:**
    -   [Evolution API](https://github.com/EvolutionAPI/evolution-api) (WhatsApp)
    -   [AbacatePay](https://abacatepay.com/) (Pagamentos Pix)

## 📋 Pré-requisitos

-   [Docker](https://www.docker.com/)
-   [Docker Compose](https://docs.docker.com/compose/)

## 🔧 Instalação e Execução

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/seu-usuario/barbearia.git
    cd barbearia
    ```

2.  **Configure as variáveis de ambiente:**

    Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

    ```env
    SECRET_KEY=sua_chave_secreta_django
    DEBUG=True
    
    # Configurações de Token de Autoatendimento
    SELF_SERVICE_TOKEN_KEY=seu_token_secreto
    REQUIRE_SELF_SERVICE_TOKEN=False
    
    # Integração Evolution API (WhatsApp)
    EVOLUTION_API_URL=http://evolution_api:8080
    EVOLUTION_API_KEY=sua_chave_evolution_api
    AUTHENTICATION_API_KEY=sua_chave_autenticacao
    
    # Integração AbacatePay
    ABACATEPAY_KEY=sua_chave_api_abacatepay
    ```

3.  **Execute com Docker Compose:**

    ```bash
    docker-compose up --build
    ```

    O sistema iniciará os seguintes serviços:
    -   `app`: Aplicação Django (porta 8000)
    -   `nginx`: Servidor web (porta 80)
    -   `evolution-api`: API de WhatsApp (porta 8082)
    -   `reminder-worker`: Worker para envio de lembretes

4.  **Acesse a aplicação:**

    -   **Web:** http://localhost
    -   **Admin Django:** http://localhost/admin

## 🗂 Estrutura do Projeto

-   `core/`: Configurações principais do projeto.
-   `scheduling/`: App de agendamento e gerenciamento de horários.
-   `dashboard/`: Painel administrativo personalizado.
-   `payments/`: Integração com gateway de pagamento.
-   `users/`: Gestão de usuários e autenticação.
-   `docker-compose.yml`: Orquestração dos containers.

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## 📄 Licença

[MIT](LICENSE)
