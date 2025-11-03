# ============================================================
# 🏗️ ARQUITETURA - RESTAURANT ANALYTICS
# ============================================================
# Documento que descreve as decisões técnicas, estrutura lógica
# e diagramas arquiteturais do projeto Restaurant Analytics.
# Este formato segue padrão de documentação técnica nível pleno.
# ============================================================


## 📖 Visão Geral

O **Restaurant Analytics** é uma plataforma web desenvolvida para **donos de restaurantes explorarem dados operacionais e de vendas** de forma intuitiva, sem precisar escrever código.  
Inspirado em ferramentas como **Power BI** e **Metabase**, o sistema é focado no setor de **food service**, fornecendo métricas, comparações e dashboards personalizados.


## ⚙️ Objetivos Arquiteturais

| Objetivo | Descrição |
|-----------|------------|
| **Escalabilidade** | Suportar alto volume de dados (500k+ registros) com consultas rápidas. |
| **Modularidade** | Separar camadas de negócio, API e apresentação. |
| **Usabilidade** | Interface simples e dashboards configuráveis. |
| **Portabilidade** | Execução completa via Docker Compose. |
| **Manutenibilidade** | Código legível, testável e documentado. |


## 🧩 Arquitetura Lógica (Visão de Alto Nível)

A solução foi estruturada com **três camadas principais**:  
**Frontend (UI)**, **Backend (API)** e **Banco de Dados (Persistência)**.



### 📊 Diagrama UML Simplificado (Visão Geral)

```mermaid
%% ============================================================
%% 🌐 DIAGRAMA UML SIMPLIFICADO DE COMPONENTES
%% ============================================================
%% Representa a interação entre as principais camadas do sistema.
%% Pode ser renderizado diretamente no GitHub ou VS Code (Mermaid).
%% ============================================================

graph TD
    subgraph Frontend [🎨 Frontend - HTML / CSS / JS]
        A1[Interface Web] --> A2[Gráficos e Dashboards]
        A2 -->|AJAX / Fetch| B1
    end

    subgraph Backend [🧠 Backend - FastAPI]
        B1[API REST] --> B2[Serviço de Métricas]
        B2 --> B3[Serviço de Dashboards]
        B2 --> C1
    end

    subgraph Database [🗄️ Banco de Dados - PostgreSQL]
        C1[(Tabelas: orders, products, stores, channels)]
        C2[(Materialized Views)]
        C1 --> C2
    end

    A1 -.->|HTTP:80| Backend
    Backend -.->|TCP:5432| Database

🧱 Camadas e Responsabilidades

Camada	                   Tecnologia                     	        Responsabilidade

Frontend	             HTML5, CSS3, JavaScript	                Interface visual, dashboards, filtros e gráficos dinâmicos.
Backend (API)	         Python 3.11, FastAPI, SQLAlchemy	        Processamento de métricas, agregações e exposição da API REST.
Banco de Dados	         PostgreSQL	Armazenamento                   persistente, agregações analíticas e índices.

%% ============================================================
%% 🧠 DIAGRAMA DE COMPONENTES DO BACKEND (FastAPI)
%% ============================================================
%% Demonstra a separação entre camadas dentro do backend.
%% ============================================================

graph LR
    subgraph Backend
        R1[📡 routes/metrics.py] --> S1[services/analytics_service.py]
        R2[🧭 routes/dashboard.py] --> S2[services/dashboard_service.py]
        S1 --> D1[database/models.py]
        S2 --> D1
        D1 --> DB[(PostgreSQL)]
    end

🗂️ Estrutura de Pastas

restaurant-analytics/
├── backend/
│   ├── src/
│   │   ├── main.py                # Ponto de entrada da API FastAPI
│   │   ├── routes/                # Endpoints REST (organizados por domínio)
│   │   ├── services/              # Regras de negócio e cálculos de métricas
│   │   ├── database/              # Modelos ORM e sessão SQLAlchemy
│   │   └── utils/                 # Funções auxiliares
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                      # Interface visual
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
│
├── data/
│   ├── schema_postgres.sql        # Estrutura das tabelas
│   └── generate_sales.py          # Script para gerar dados simulados
│
├── infra/
│   ├── docker-compose.yml         # Orquestração de serviços
│   ├── nginx.conf                 # Configuração do proxy reverso
│   └── .env                       # Variáveis de ambiente
│
└── docs/
    ├── architecture.md            # Documento atual
    └── banner.png


📈 Estratégias de Performance    

| Estratégia                                  | Benefício                                                   |
| ------------------------------------------- | ----------------------------------------------------------- |
| **Índices compostos** (`store_id, sold_at`) | Aceleram consultas de faturamento por loja e período.       |
| **Materialized Views**                      | Reduzem tempo de resposta em consultas agregadas.           |
| **Particionamento Temporal**                | Melhora performance para datasets acima de 1M de registros. |
| **Cache In-Memory (futuro)**                | Reduz latência para endpoints mais acessados.               |


🔐 Segurança e Boas Práticas 

| Medida               | Descrição                                    |
| -------------------- | -------------------------------------------- |
| `.env`               | Armazena variáveis sensíveis fora do código. |
| `CORS`               | Restrito a domínios confiáveis.              |
| `Pydantic`           | Validação de entrada de dados.               |
| `Logs estruturados`  | Monitoramento e rastreabilidade.             |
| `TLS / JWT (futuro)` | Planejado para autenticação e multiusuário.  |


🧭 Decisões Arquiteturais-Chave

| Decisão                | Justificativa                                        | Trade-off                         |
| ---------------------- | ---------------------------------------------------- | --------------------------------- |
| **FastAPI**            | Alta performance e documentação automática (OpenAPI) | Exige tipagem e async             |
| **PostgreSQL**         | SQL avançado, confiável e com extensões analíticas   | Mais pesado em dev                |
| **Docker Compose**     | Padroniza ambiente e isolamento                      | Build inicial mais lento          |
| **Frontend estático**  | Simplicidade e baixo acoplamento                     | Menos dinâmico que frameworks SPA |
| **Materialized Views** | Otimização de queries analíticas                     | Necessita atualização periódica   |
