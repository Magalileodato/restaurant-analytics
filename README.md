# 🍽️ Restaurant Analytics MVP

Python FastAPI PostgreSQL Docker HTML CSS JavaScript

<!-- 👇 Slogan visual do projeto (imagem localizada em frontend/img/) -->

<p align="center">
  <img src="frontend/img/slogan-data-feeds-intelligence-food.png" alt="Slogan: Data Feeds Intelligence for Food Service" width="720" />
</p>

## 🚀 Descrição do Projeto

O Restaurant Analytics MVP é uma plataforma inteligente para donos de restaurantes explorarem métricas operacionais e de vendas de forma simples, intuitiva e visual — como um Power BI feito sob medida para o setor de food service.

A solução permite:

📊 Visualizar faturamento, ticket médio e produtos mais vendidos
📅 Comparar períodos e detectar tendências
⚙️ Criar dashboards personalizados sem código
🧠 Extrair insights automáticos com IA (futuro roadmap)

💡 Ideal para gestores que desejam tomar decisões baseadas em dados, sem precisar entender SQL ou BI corporativo.



## 🎥 Vídeo de Explicação (YouTube)

> **Novo!** Seção para o link do vídeo de apresentação do projeto.
>
> Substitua `VIDEO_ID` abaixo pelo ID do seu vídeo no YouTube.

[🔗 Assistir no YouTube](https://www.youtube.com/watch?v=VIDEO_ID)

[![Assista à apresentação no YouTube](https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)

## 🗂 Estrutura do Projeto

```
restaurant-analytics/
├── backend/                                   # 🧠 Backend principal (FastAPI)
│   ├── __init__.py                            # 📦 Marca o pacote 'backend' e facilita imports relativos
│   ├── src/                                   # Código-fonte organizado por domínio
│   │   ├── __init__.py                        # 📦 Exposição/organização do namespace de 'src'
│   │   ├── main.py                            # 🚀 Entry point da API FastAPI
│   │   ├── init_db.py                         # 🗄️ Inicialização e setup do banco
│   │   ├── routes/                            # 🌐 Rotas / Endpoints
│   │   │   ├── __init__.py                    # 📦 Registra/agrupa blueprints/routers do módulo de rotas
│   │   │   ├── metrics.py                     # 📈 Endpoints de métricas
│   │   │   └── dashboard.py                   # 🧭 Endpoints de dashboards
│   │   ├── services/                          # ⚙️ Lógica de negócio e regras
│   │   │   ├── __init__.py                    # 📦 Superfície pública de serviços (injeção de dependências)
│   │   │   └── analytics_service.py           # 🧮 Processamento e agregações
│   │   ├── database/                          # 🗃️ Configuração e modelos do banco
│   │   │   ├── __init__.py                    # 📦 Inicializa camada de persistência (ex.: exporta Base/engine)
│   │   │   ├── models.py                      # 🧱 ORM (SQLAlchemy)
│   │   │   └── session.py                     # 🔌 Conexão com PostgreSQL
│   │   ├── utils/                             # 🧰 Funções utilitárias
│   │   │   ├── __init__.py                    # 📦 Reexporta helpers utilitários para import simplificado
│   │   │   └── helpers.py                     # 🪛 Funções de apoio gerais
│   ├── requirements.txt                       # 📦 Dependências Python (FastAPI, SQLAlchemy etc.)
│   └── Dockerfile                             # 🐳 Container do backend
│
├── frontend/                                  # 🎨 Frontend estático (HTML, CSS e JS)
│   ├── index.html                             # 🖥️ Página principal do dashboard
│   ├── nginx.conf                             # 🌐 Configuração do servidor Nginx
│   ├── css/                                   # 💅 Estilos visuais
│   │   └── style.css                          # 🎨 Arquivo de estilos principais
│   ├── img/                                   # 🖼️ Imagens e elementos gráficos
│   │   └── slogan-data-feeds-intelligence-food.png  # 🍽️ Banner/logotipo temático (dados + alimentação)
│   ├── js/                                    # ⚡ Scripts e interatividade
│   │   └── app.js                             # 🧠 Lógica e gráficos dinâmicos do dashboard
│   └── Dockerfile                             # 🐳 Container do frontend
│
├── infra/                                     # ⚙️ Infraestrutura e DevOps
│   ├── docker-compose.yml                     # 🔧 Orquestração (Backend + DB + Nginx)
│   └── .env                                   # 🌍 Variáveis de ambiente (API keys, DB configs, etc.)
│
├── data/                                      # 📊 Scripts e schema do banco
│   ├── schema_postgres.sql                    # 🧱 Estrutura SQL das tabelas (DDL)
│   └── generate_sales.py                      # 🧮 Script para gerar dados simulados de vendas
│
├── docs/                                      # 📚 Documentação e materiais visuais
│   ├── banner.png                             # 🖼️ Banner de apresentação do projeto
│   ├── architecture.md                        # 🏗️ Decisões e diagramas arquiteturais
│   ├── diagrama.png                           # 🧩 Diagrama geral da arquitetura do sistema
│   ├── doc_banco_dados.md                     # 🗄️ Documentação técnica do banco de dados
│   ├── doc_teste_conexao.md                   # 🔌 Guia de teste de conexão com o banco/API
│   ├── doc_local_cold.md                      # 🧊 Guia de execução local em ambiente "cold start" (primeira inicialização)
│   ├── doc_teste_frontend.md                  # 🧭 Guia de teste e validação do frontend
│   ├── dataBase_setup_guide.md                # 🧰 Passo a passo de configuração do banco de dados
│   ├── uml_classes.png                        # 🧮 Diagrama de classes UML do backend
│   ├── uml_use_case_completo.png              # 🎯 Diagrama de casos de uso completo do sistema
│   └── uml_use_case_front.png                 # 🖥️ Diagrama de casos de uso focado no frontend
│
├── .gitignore                                 # 🙈 Arquivos/pastas ignorados pelo Git
├── LICENSE                                    # 📜 Licença MIT do projeto
└── README.md                                  # 🏁 README principal (resumo e instruções iniciais)
```

## ⚙️ Tecnologias Utilizadas

|-------------------------------------------------------------------------------------------------------
|  🧩 Camada           |             🛠️ Tecnologia            |              💡 Função
|-------------------------------------------------------------------------------------------------------
|
|    Backend          |        🖥️ Python 3.11 + FastAPI      |     API REST modular e performática
|-------------------------------------------------------------------------------------------------------
|
|   Banco de Dados    |        🗄️ PostgreSQL                  |  Armazenamento e agregações analíticas
|-------------------------------------------------------------------------------------------------------
|   Frontend          |    🌐  HTML5, CSS3, JavaScript        |    Dashboard interativo e responsivo
|-------------------------------------------------------------------------------------------------------
|
|   Deploy            |     🐳Docker & Docker Compose         |   Execução containerizada
|-------------------------------------------------------------------------------------------------------
|
|  Configuração       |     🔧  python-dotenv                 |   Gerenciamento de variáveis seguras
|-------------------------------------------------------------------------------------------------------

## 📦 Instalação e Execução

1️⃣ Clone o repositório

```
git clone https://github.com/magali-leodato/restaurant-analytics.git
cd restaurant-analytics
```

2️⃣ Configure variáveis de ambiente

```
cp infra/.env.example .env
```

3️⃣ Execute com Docker

```
docker-compose up --build
```

Acesse: 👉 [http://localhost:8000](http://localhost:8000)

4️⃣ (Opcional) Usando venv sem Docker

```
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.src.main:app --reload
```

## 📋 Exemplo de requirements.txt

```
fastapi==0.103.2
uvicorn[standard]==0.23.2
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
python-dotenv==1.0.1
pandas==2.2.3
jinja2==3.1.4
```

## 📈 Funcionalidades

✅ Dashboard com métricas essenciais

✅ Filtros por canal (iFood, Rappi, presencial, app próprio)

✅ Comparação de períodos

🚧 IA para geração de insights automáticos

🚧 Exportação de relatórios (PDF / Excel)

🚧 Gestão multi-lojas

## 🔮 Próximos Passos

🧠 Integração de IA para insights automáticos

🔒 Autenticação e controle de acesso por usuário

🎨 UI/UX aprimorado com gráficos interativos

☁️ Deploy em nuvem (Render / Railway / Fly.io)

💬 Tradução multilíngue (PT/EN)

## 👩‍💻 Desenvolvedora

Magali Leodato
🔗 LinkedIn

💻 GitHub

## 📜 Licença

Este projeto está sob a licença MIT.
Consulte o arquivo LICENSE para mais detalhes.
