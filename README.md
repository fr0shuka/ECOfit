# EcoFit - Plataforma de Análise de Atividades e Hábitos Saudáveis

Aplicação SaaS desenvolvida como projeto prático de validação para o referencial de **Nível 5 RVCC em Ciência de Dados e Sistemas de Informação**.

A arquitetura do sistema segue rigorosamente o padrão **MVC (Model-View-Controller)**, garantindo o isolamento de responsabilidades, a modularidade do código e a integridade relacional dos dados.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.14+
* **Interface Web (Frontend):** Streamlit
* **Base de Dados & Autenticação (Backend):** Supabase (PostgreSQL em Arquitetura Relacional 3NF)
* **Serviços & Integrações:** APIs Meteorológicas em tempo real, gestão de eventos desportivos e processamento de ficheiros (GPX, FIT, CSV, etc.)

---

## 🏗️ Estrutura do Projeto (MVC)

O código encontra-se organizado modularmente de acordo com a seguinte árvore de diretórios:

```text
ecofit/
├── .streamlit/
│   └── secrets.toml            # Configuração segura e credenciais locais
├── config/
│   ├── __init__.py
│   └── database.py             # Inicialização e ligação ao cliente Supabase
├── controllers/
│   ├── __init__.py
│   ├── admin_controller.py     # Lógica de gestão administrativa e validações
│   ├── auth_controller.py      # Controlo de sessões e autenticação de utilizadores
│   ├── file_controller.py      # Processamento e importação de ficheiros de atividade
│   └── user_controller.py      # Gestão de dados globais e rankings de utilizadores
├── models/
│   ├── __init__.py
│   ├── activity_model.py       # Interações de dados para treinos e hábitos
│   └── user_model.py           # Operações de dados para perfis e utilizadores
├── services/
│   ├── __init__.py
│   ├── news_service.py         # Integração de notícias e eventos desportivos
│   └── weather_service.py      # Integração de meteorologia por geolocalização
├── views/
│   ├── __init__.py
│   ├── admin_analytics_view.py # Painel estatístico avançado para administradores
│   ├── admin_view.py           # Gestão de pedidos pendentes e perfis (Atleta, Atleta Pro, Admin)
│   ├── components.py           # Elementos reutilizáveis de interface (ex: meteorologia na sidebar)
│   ├── dashboard_view.py       # Registo de atividades físicas e hábitos saudáveis
│   ├── login_view.py           # Interface de autenticação e novos registos
│   ├── my_trainings_view.py    # Histórico, listagem detalhada, edição e eliminação de registos
│   ├── upload_view.py          # Zona de sincronização de ficheiros de treino
│   └── users_view.py           # Classificação geral e líderes da comunidade
├── .gitignore                  # Ficheiros e pastas ignoradas pelo controlo de versões
├── app.py                      # Orquestrador principal da aplicação (Routing e Sessão)
├── README.md                   # Documentação do projeto
└── requirements.txt            # Dependências do ecossistema Python