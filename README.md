# SmartSchedule Pro: Gestão Inteligente de Escalas

Este projeto consiste em uma solução Full Stack de nível empresarial projetada para mitigar a complexidade logística na gestão de recursos humanos. O sistema automatiza a criação de escalas de trabalho utilizando Programação por Restrições (CP), garantindo conformidade regulatória e equilíbrio operacional.

---

## Diferenciais Técnicos

* **Motor de Otimização Combinatória**: Integração com o Google OR-Tools CP-SAT Solver para a resolução de problemas de satisfação de restrições (CSP).
* **Arquitetura de Software**: Implementação baseada em Clean Architecture, garantindo o desacoplamento entre a lógica de negócio (Services), persistência de dados (Models) e interface de consumo (API).
* **Interface Reativa**: SPA (Single Page Application) desenvolvida com React 18 e FullCalendar, focada em performance e usabilidade para o usuário final.
* **Engenharia de Dados**: Sistema de exportação de relatórios com formatação condicional dinâmica utilizando as bibliotecas Pandas e OpenPyXL.

---

## Lógica de Escalonamento e Otimização

O núcleo do sistema reside na camada de serviço `SchedulingService`. O algoritmo transforma regras de negócio em restrições matemáticas, buscando a minimização da variância na carga horária entre colaboradores.

A função objetivo do motor de otimização é definida para respeitar o seguinte limite:

$$\sum_{day=1}^{n} Shift_{employee} \le MaxHours$$

### Regras de Negócio Implementadas

1. **Conformidade Trabalhista**: Garantia de intervalos de descanso obrigatórios entre jornadas (Interjornada).
2. **Equidade Operacional**: Algoritmo de distribuição justa para evitar a concentração de carga horária em grupos específicos de funcionários.
3. **Gestão de Turnos Críticos**: Limitação paramétrica de sequências de turnos noturnos e monitoramento de dias consecutivos de trabalho.

---

## Stack Tecnológica

### Backend
* **Linguagem**: Python 3.12
* **Framework**: Django 6.0
* **Interface**: Django REST Framework (DRF)
* **Solver**: Google OR-Tools
* **Banco de Dados**: PostgreSQL

### Frontend
* **Core**: React 18 (Vite)
* **Gestão de Estado**: Context API e Hooks customizados
* **Estilização**: Tailwind CSS
* **Agendamento**: FullCalendar v6

---

## Estrutura do Ecossistema

```text
├── backend/
│   ├── api/                # Endpoints e Serializers (Camada de Interface)
│   ├── services/           # Lógica de Negócio e Solver (Camada de Domínio)
│   ├── scheduling_system/  # Configurações de Ambiente e Middleware
│   └── tests/              # Testes unitários e de integração
├── frontend/
│   ├── src/
│   │   ├── components/     # Unidades de UI atômicas
│   │   ├── hooks/          # Lógica de abstração de consumo de API
│   │   └── pages/          # Views e roteamento
└── docker-compose.yml
