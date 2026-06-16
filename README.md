# SmartSchedule Pro — Gestão Inteligente de Escalas

Aplicação web para automatizar a criação de escalas de trabalho usando **Programação por Restrições (CP-SAT)**, garantindo conformidade com regras de descanso e equilíbrio de carga entre os colaboradores.

### 🔗 Acesso à aplicação

**https://sistema-de-escala-eight.vercel.app**

> Calendário de turnos, geração automática de escala, edição por arrasto e exportação para Excel. Painel administrativo em `/admin/`.

---

## Diferenciais Técnicos

* **Motor de Otimização Combinatória**: Google OR-Tools CP-SAT Solver resolvendo o problema de alocação de turnos como um CSP.
* **Arquitetura em camadas**: lógica de negócio isolada em *Services* (`shifts/services.py`), persistência em *Models*, e interface de consumo via *Django REST Framework*.
* **Interface no servidor**: página única renderizada pelo Django com **Bootstrap 5** e **FullCalendar 6**, sem necessidade de build de frontend.
* **Exportação de relatórios**: geração de planilhas `.xlsx` com **Pandas** + **OpenPyXL**.

---

## Lógica de Escalonamento e Otimização

O núcleo do sistema reside na classe `SchedulingService`. O algoritmo transforma regras de negócio em restrições matemáticas e busca **minimizar a variância da carga de trabalho** entre os colaboradores (`Minimize(max_work - min_work)`).

### Regras de Negócio Implementadas

1. **Um turno por colaborador por dia** (restrição de exclusividade).
2. **Máximo de dias consecutivos de trabalho** (janela deslizante).
3. **Descanso obrigatório** após atingir o máximo de dias consecutivos.
4. **Mínimo de colaboradores por dia**.
5. **Turnos noturnos**: evita dois turnos noturnos seguidos para o mesmo colaborador.

Todos os parâmetros são configuráveis por *Regra de Escalonamento* (`SchedulingRule`) no admin, incluindo o tempo-limite do solver.

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.12+ |
| Framework | Django 6.0 |
| API | Django REST Framework |
| Solver | Google OR-Tools (CP-SAT) |
| Interface | Django Templates + Bootstrap 5 + FullCalendar 6 |
| Relatórios | Pandas + OpenPyXL |
| Banco (produção) | PostgreSQL (Neon) |
| Banco (local) | SQLite |
| Estáticos | WhiteNoise |
| Hospedagem | Vercel (serverless) |

---

## Estrutura do Projeto

```text
├── api/
│   └── index.py            # Entrypoint WSGI para a Vercel (serverless)
├── scheduling_system/      # Configurações do projeto (settings, urls, wsgi)
├── shifts/
│   ├── models.py           # Employee, ShiftType, Schedule, SchedulingRule
│   ├── serializers.py      # Validação e serialização (DRF)
│   ├── services.py         # Lógica de negócio + solver OR-Tools
│   ├── views.py            # ViewSets e endpoints da API
│   ├── urls.py             # Rotas da API e da página
│   ├── admin.py            # Painel administrativo
│   ├── templates/shifts/   # calendar.html (interface)
│   └── tests.py            # 39 testes (modelos, services, API, export)
├── manage.py
├── main.py                 # Execução local como app desktop (Waitress)
├── populate.py             # Popula dados de exemplo
├── requirements.txt
└── vercel.json             # Configuração de deploy serverless
```

---

## Endpoints principais da API

| Método | Rota | Descrição |
|---|---|---|
| `GET/POST` | `/api/employees/` | CRUD de funcionários |
| `GET/POST` | `/api/shift-types/` | CRUD de tipos de turno |
| `GET/POST` | `/api/schedules/` | CRUD de escalas |
| `GET/POST` | `/api/scheduling-rules/` | CRUD de regras |
| `POST` | `/api/schedules/generate/` | Gera a escala otimizada |
| `GET` | `/api/schedules/calendar_data/` | Eventos para o calendário |
| `POST` | `/api/update-shift/` | Cria/atualiza um turno |
| `GET` | `/api/export/` | Exporta a escala em Excel |

---

## Execução local

```bash
# 1. Ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 2. Dependências
pip install -r requirements.txt

# 3. Banco e dados de exemplo
python manage.py migrate
python populate.py

# 4. Servidor de desenvolvimento
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

### Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste:

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta do Django (obrigatória em produção) |
| `DEBUG` | `True` em dev, `False` em produção |
| `DATABASE_URL` | URI PostgreSQL (se ausente, usa SQLite) |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `CSRF_TRUSTED_ORIGINS` | Origens confiáveis para CSRF |

---

## Testes

```bash
python manage.py test
```

---

## Deploy (Vercel)

O deploy é automático a cada `push` na branch `main` via integração com o GitHub. A aplicação roda como função serverless Python (`api/index.py`), com PostgreSQL no Neon (`DATABASE_URL`) e arquivos estáticos servidos pelo WhiteNoise. Detalhes do empacotamento como executável Windows estão em [README_BUILD.md](README_BUILD.md).
