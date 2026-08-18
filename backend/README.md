# ⚙️ Smart Finance Agent - Backend API & Ingestion Worker

Este directorio contiene el motor principal del proyecto **Gestor de Finanzas Personal**, desarrollado en Python 3.12 con **FastAPI**, **PostgreSQL** (vía SQLAlchemy 2.0 Async), **Redis + ARQ** para procesamiento de tareas asíncronas y **AI Local** (Faster-Whisper + Ollama).

---

## 🏗️ Estructura del Proyecto (Arquitectura Hexagonal)

```
backend/src/
├── domain/                    # Entidades y reglas de negocio puras
│   ├── models/                # Account, Transaction, Category, Budget
│   └── services/              # Lógica financiera determinista
├── application/               # Casos de Uso e Interfaces (Ports)
│   ├── use_cases/             # CreateTransaction, ManageAccount, etc.
│   └── ports/                 # TransactionRepository, AccountRepository
├── infrastructure/            # Adaptadores e Infraestructura externa
│   ├── adapters/
│   │   ├── ai/                # local_stt.py (Whisper) y data_extractor.py (Ollama)
│   │   ├── db/                # Modelos ORM, Migraciones Alembic y Repositorios
│   │   ├── redis/             # Pool de conexiones Redis
│   │   ├── tasks/             # Worker ARQ (process_voice_task, process_text_task)
│   │   └── telegram/          # Bot Aiogram 3.x, Handlers y Middlewares
│   └── api/                   # Router FastAPI, Dependencias y DTOs
└── config.py                  # Configuración Pydantic Settings (.env)
```

---

## 💻 Desarrollo Local

### 1. Prerrequisitos
- Python 3.12 instalado.
- Redis y PostgreSQL corriendo (puedes levantarlos con `docker-compose up -d db redis` desde la raíz).
- Servidor local de **Ollama** activo (`http://localhost:11434`) con el modelo descargado (`ollama pull llama3.2`).

### 2. Entorno Virtual e Instalación de Dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuración del `.env`
Crea o edita tu archivo `.env` en la raíz de `backend/`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/smart_finance
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_ALLOWED_USER_IDS=[12345678]
OLLAMA_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
```

### 4. Ejecutar Migraciones de Base de Datos y Poblado Inicial
```bash
alembic upgrade head
python seed_db.py
```

### 5. Ejecutar la API Web (FastAPI)
```bash
uvicorn src.main:app --reload
```
- Swagger UI interactivo: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`

### 6. Ejecutar el ARQ Worker (Bot de Telegram e Ingesta Asíncrona)
En una terminal secundaria:
```bash
source venv/bin/activate
export PYTHONPATH=.
arq src.infrastructure.adapters.tasks.worker.WorkerSettings
```

---

## 🧪 Pruebas Unitarias e Integración
```bash
export PYTHONPATH=.
pytest tests/ -v
```
