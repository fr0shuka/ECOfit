# EcoFit - Plataforma de análise de atividades

Este projeto é a construção de uma aplicação SaaS para monitorização de hábitos e atividade física. Desenvolvido como projeto prático de validação para o referencial de **Nível 5 RVCC em Ciência de Dados e Sistemas de Informação**.

A aplicação utiliza uma arquitetura puramente assente no padrão **MVC (Model-View-Controller)** para garantir o isolamento de responsabilidades, segurança dos dados e escalabilidade do código.

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.14+
*   **Interface Web (Frontend):** Streamlit
*   **Base de Dados & Autenticação (Backend):** Supabase (PostgreSQL via HTTPS)
*   **Gestor de Dependências:** `uv` / `pip`

---

## 🏗️ Estrutura do Projeto (MVC)

O código encontra-se organizado de forma modular seguindo as boas práticas:

```text
ecofit/
├── .streamlit/
│   └── secrets.toml          # Credenciais locais protegidas (ignoradas no Git)
├── config/
│   └── database.py           # Inicialização segura do cliente Supabase
├── controllers/
│   ├── auth_controller.py    # Controlo de sessão e logins
│   └── admin_controller.py   # Validação sintática (Regex) e lógica de registos
├── models/
│   └── user_model.py         # Queries SQL / API Directas à tabela bd_utilizadores
├── views/
│   ├── login_view.py         # Interfaces das abas de login e novos pedidos
│   ├── admin_view.py         # Painel restrito de aprovação para perfis Admin
│   └── dashboard_view.py     # Área de trabalho provisória do Atleta
├── app.py                    # Orquestrador principal da aplicação (Routing)
└── requirements.txt          # Dependências do ecossistema para Deploy Cloud