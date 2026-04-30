# Professional Work Scheduling System

A production-ready Django + React application for employee shift scheduling with calendar UI, smart algorithms, and Excel export.

## Tech Stack

- **Backend**: Django 6.0 + Django REST Framework
- **Frontend**: React 18 + Vite + FullCalendar + Tailwind CSS
- **Database**: PostgreSQL (production) / SQLite (development)
- **Optimization**: Google OR-Tools CP-SAT solver
- **Export**: Pandas + OpenPyXL

## Features

### Calendar Interface
- Monthly/weekly calendar views
- Color-coded shift types
- Click to edit shifts
- Drag-and-drop scheduling
- Employee filtering

### Smart Scheduling Engine
- Constraint satisfaction optimization
- Fair workload distribution
- Configurable rules (max consecutive days, rest periods, night shift limits)
- Minimizes variance in work hours

### Admin Panel
- Manage employees and shift types
- Override schedules manually
- Configure scheduling rules

### API Endpoints
- `GET /api/schedules/` - List schedules
- `POST /api/schedules/` - Create schedule
- `PUT /api/schedules/<id>/` - Update schedule
- `DELETE /api/schedules/<id>/` - Delete schedule
- `GET /api/employees/` - List employees
- `GET /api/shift-types/` - List shift types
- `POST /api/schedules/generate/` - Generate optimized schedule
- `GET /api/schedules/calendar_data/` - Calendar events
- `POST /api/update-shift/` - Update single shift
- `GET /api/export/` - Export to Excel

## Installation & Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL (for production)

### Backend Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repo>
   cd projetos-em-Python
   pip install -r requirements.txt
   ```

2. **Database setup:**
   - For development (SQLite):
     ```bash
     python manage.py migrate
     ```
   - For production (PostgreSQL):
     ```bash
     # Set DATABASE_URL environment variable
     export DATABASE_URL="postgresql://user:password@localhost:5432/scheduling_db"
     python manage.py migrate
     ```

3. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

4. **Populate sample data:**
   ```bash
   python populate.py
   ```

5. **Run Django server:**
   ```bash
   python manage.py runserver
   ```
   Server runs on http://localhost:8000

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run React development server:**
   ```bash
   npm run dev
   ```
   Frontend runs on http://localhost:5173

## Usage

1. **Access the application:**
   - Frontend: http://localhost:5173
   - Admin: http://localhost:8000/admin/
   - API: http://localhost:8000/api/

2. **Generate schedule:**
   - Select employees in frontend
   - Click "Generate Schedule"
   - View optimized schedule in calendar

3. **Edit shifts:**
   - Click on calendar events to edit
   - Drag events to change dates

4. **Export:**
   - Click "Export to Excel" for formatted spreadsheet

## Architecture

The application follows clean architecture principles with clear separation of concerns:

### Layers

- **Views Layer** (`views.py`): HTTP request/response handling, input validation via serializers
- **Services Layer** (`services.py`): Business logic, optimization algorithms, data processing
- **Serializers Layer** (`serializers.py`): Data validation, transformation, API contracts
- **Models Layer** (`models.py`): Data persistence, relationships
- **Exceptions Layer** (`exceptions.py`): Custom error handling

### Key Principles

- **Single Responsibility**: Each layer has a specific purpose
- **Dependency Inversion**: Services depend on abstractions (serializers, exceptions)
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Validation**: Input validation at API boundaries
- **Logging**: Comprehensive logging for debugging and monitoring

### Service Classes

- `SchedulingService`: OR-Tools optimization for schedule generation
- `ScheduleService`: Data access and business operations for schedules

### API Design

- RESTful endpoints with proper HTTP methods
- Request/Response serializers for validation
- Consistent error responses
- Pagination and filtering support

## Deployment

### Production Setup

1. **Environment variables:**
   ```bash
   export DATABASE_URL="postgresql://..."
   export DJANGO_SETTINGS_MODULE=scheduling_system.settings
   export SECRET_KEY="your-secret-key"
   ```

2. **Build frontend:**
   ```bash
   cd frontend
   npm run build
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Use production server:**
   - Gunicorn for Django
   - Nginx for static files
   - PostgreSQL database

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "scheduling_system.wsgi"]
```

## API Documentation

All endpoints return JSON. Use tools like Postman or curl for testing.

Example: Generate schedule
```bash
curl -X POST http://localhost:8000/api/schedules/generate/ \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2026-05-01", "end_date": "2026-05-31", "employee_ids": [1,2,3]}'
```

## Contributing

1. Backend changes: Test with `python manage.py test`
2. Frontend changes: Test with `npm run build`
3. Follow PEP 8 and ESLint rules

## License

MIT License

## Frontend

Uses FullCalendar with:
- Monthly view
- Color-coded events
- Click to edit shifts
- Drag-and-drop date changes
- Real-time updates via AJAX
- Filters by employee

## Export

Excel export with:
- Colored cells matching shift types
- Auto-adjusted column widths
- Sorted by date and employee