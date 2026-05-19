````markdown
# Sistema Profissional de Escala de Trabalho

Uma aplicação completa em **Django + React** para gerenciamento de escalas de funcionários, com interface de calendário, algoritmos inteligentes e exportação para Excel.

---

# Stack Tecnológica

- **Backend**: Django 6.0 + Django REST Framework
- **Frontend**: React 18 + Vite + FullCalendar + Tailwind CSS
- **Banco de Dados**: PostgreSQL (produção) / SQLite (desenvolvimento)
- **Otimização**: Google OR-Tools CP-SAT Solver
- **Exportação**: Pandas + OpenPyXL

---

# Funcionalidades

## Interface de Calendário

- Visualização mensal e semanal
- Tipos de turnos com cores diferentes
- Clique para editar turnos
- Arrastar e soltar escalas
- Filtro por funcionário

## Motor Inteligente de Escalonamento

- Otimização baseada em satisfação de restrições
- Distribuição justa da carga horária
- Regras configuráveis:
  - Máximo de dias consecutivos
  - Períodos de descanso
  - Limites de turnos noturnos
- Minimização da diferença de horas trabalhadas

## Painel Administrativo

- Gerenciamento de funcionários e tipos de turno
- Sobrescrita manual de escalas
- Configuração de regras de agendamento

## Endpoints da API

- `GET /api/schedules/` — Listar escalas
- `POST /api/schedules/` — Criar escala
- `PUT /api/schedules/<id>/` — Atualizar escala
- `DELETE /api/schedules/<id>/` — Remover escala
- `GET /api/employees/` — Listar funcionários
- `GET /api/shift-types/` — Listar tipos de turno
- `POST /api/schedules/generate/` — Gerar escala otimizada
- `GET /api/schedules/calendar_data/` — Eventos do calendário
- `POST /api/update-shift/` — Atualizar turno individual
- `GET /api/export/` — Exportar para Excel

---

# Instalação e Configuração

## Pré-requisitos

- Python 3.12+
- Node.js 18+
- PostgreSQL (produção)

---

# Configuração do Backend

## 1. Clonar o repositório e instalar dependências

```bash
git clone <repo>
cd projetos-em-Python
pip install -r requirements.txt
```

## 2. Configuração do banco de dados

### Desenvolvimento (SQLite)

```bash
python manage.py migrate
```

### Produção (PostgreSQL)

```bash
# Defina a variável DATABASE_URL
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/scheduling_db"

python manage.py migrate
```

## 3. Criar superusuário

```bash
python manage.py createsuperuser
```

## 4. Popular dados de exemplo

```bash
python populate.py
```

## 5. Executar servidor Django

```bash
python manage.py runserver
```

Servidor disponível em:

```text
http://localhost:8000
```

---

# Configuração do Frontend

## 1. Instalar dependências

```bash
cd frontend
npm install
```

## 2. Executar servidor React

```bash
npm run dev
```

Frontend disponível em:

```text
http://localhost:5173
```

---

# Como Usar

## 1. Acesse a aplicação

- Frontend: `http://localhost:5173`
- Admin: `http://localhost:8000/admin/`
- API: `http://localhost:8000/api/`

## 2. Gerar escala

- Selecione os funcionários no frontend
- Clique em **"Gerar Escala"**
- Visualize a escala otimizada no calendário

## 3. Editar turnos

- Clique nos eventos do calendário para editar
- Arraste eventos para alterar datas

## 4. Exportar

- Clique em **"Exportar para Excel"** para gerar a planilha formatada

---

# Arquitetura

A aplicação segue princípios de **Clean Architecture**, com clara separação de responsabilidades.

## Camadas

- **Views Layer (`views.py`)**
  - Manipulação de requisições/respostas HTTP
  - Validação de entrada via serializers

- **Services Layer (`services.py`)**
  - Regras de negócio
  - Algoritmos de otimização
  - Processamento de dados

- **Serializers Layer (`serializers.py`)**
  - Validação de dados
  - Transformação de dados
  - Contratos da API

- **Models Layer (`models.py`)**
  - Persistência de dados
  - Relacionamentos

- **Exceptions Layer (`exceptions.py`)**
  - Tratamento personalizado de erros

---

# Princípios-Chave

- **Responsabilidade Única**
  - Cada camada possui um propósito específico

- **Inversão de Dependência**
  - Serviços dependem de abstrações

- **Tratamento de Erros**
  - Exceções customizadas com status HTTP apropriados

- **Validação**
  - Validação de entrada nos limites da API

- **Logs**
  - Logging completo para monitoramento e depuração

---

# Classes de Serviço

- `SchedulingService`
  - Otimização de escalas usando OR-Tools

- `ScheduleService`
  - Operações de negócio e acesso a dados de escalas

---

# Design da API

- Endpoints RESTful
- Uso correto de métodos HTTP
- Serializers para validação
- Respostas de erro consistentes
- Suporte a paginação e filtros

---

# Deploy

## Configuração de Produção

### 1. Variáveis de ambiente

```bash
export DATABASE_URL="postgresql://..."
export DJANGO_SETTINGS_MODULE=scheduling_system.settings
export SECRET_KEY="sua-chave-secreta"
```

## 2. Build do frontend

```bash
cd frontend
npm run build
```

## 3. Coletar arquivos estáticos

```bash
python manage.py collectstatic
```

## 4. Servidor de produção

Recomendado:

- Gunicorn para Django
- Nginx para arquivos estáticos
- PostgreSQL como banco de dados

---

# Deploy com Docker

```dockerfile
# Exemplo de Dockerfile
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "scheduling_system.wsgi"]
```

---

# Documentação da API

Todos os endpoints retornam JSON.

Ferramentas recomendadas para testes:

- Postman
- curl

## Exemplo: gerar escala

```bash
curl -X POST http://localhost:8000/api/schedules/generate/ \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2026-05-01", "end_date": "2026-05-31", "employee_ids": [1,2,3]}'
```

---

# Contribuição

1. Alterações no backend:
   ```bash
   python manage.py test
   ```

2. Alterações no frontend:
   ```bash
   npm run build
   ```

3. Siga:
   - PEP 8
   - Regras ESLint

---

# Licença

Licença MIT

---

# Frontend

O sistema utiliza FullCalendar com:

- Visualização mensal
- Eventos coloridos
- Clique para editar turnos
- Alteração de datas via drag-and-drop
- Atualizações em tempo real via AJAX
- Filtros por funcionário

---

# Exportação

Exportação Excel com:

- Células coloridas conforme o tipo de turno
- Largura automática de colunas
- Ordenação por data e funcionário
````
