# 🏦 Smart Finance Agent

> **Production-Grade Personal Finance Manager featuring Multi-Channel Ingestion (Voice / OCR / Text), Hexagonal Architecture, Redis Task Queue, and Local Zero-Cost AI Extraction.**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B%20%7C%20pgvector-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7%2B-DC382D.svg)](https://redis.io/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot%20API-2CA5E0.svg)](https://core.telegram.org/bots)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Project Overview

**Smart Finance Agent** is a production-ready personal finance backend built on core software engineering principles: **zero quantitative hallucinations**, **low-friction multi-channel ingestion**, and **complete decoupling between the financial domain and AI providers**.

Unlike naïve LLM-wrapper applications, all accounting calculations, budget tracking, data aggregation, and anomaly detections are computed **deterministically** via Python and PostgreSQL. Large Language Models (LLMs) and Speech models (Whisper) run **100% locally at zero cost** to handle natural language understanding, speech-to-text, and structured JSON data extraction.

---

## ✨ Key Features

- 🎙️ **Low-Friction Multi-Channel Ingestion:** Register expenses in under 3 seconds via Telegram voice notes (Whisper STT), free-form text messages, or the web dashboard.
- ⚡ **Asynchronous Event-Driven Architecture:** Heavy audio transcription and LLM extraction are offloaded to an asynchronous **Redis + ARQ worker queue** to keep Telegram & HTTP handlers non-blocking.
- 🤖 **100% Local & Free AI Stack:**
  - **Speech-to-Text:** `faster-whisper` running locally on CPU.
  - **Structured NLU:** `Ollama` (`llama3.2:3b` / `qwen2.5-coder:1.5b`) using `instructor` for schema validation.
- 🤝 **Human-in-the-Loop Confirmation:** Interactive Telegram inline keyboards (`[ ✅ Confirmar ]` / `[ ❌ Cancelar ]`) to review extracted drafts before database insertion.
- 🏦 **Smart Default Resolution:** Automatically matches extracted accounts and categories with existing PostgreSQL records or falls back to your main account.
- 🏛️ **Hexagonal Architecture (Ports & Adapters):** Core domain fully isolated from external frameworks, Telegram APIs, and AI models for maximum testability.

---

## 🏗️ System Architecture

```
                       +------------------------------------+
                       |           DATA SOURCES             |
                       +------------------------------------+
                       | Telegram (Audio / Photo / Text)    |
                       | Web UI Dashboard / Manual Entry    |
                       +-----------------+------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            INBOUND ADAPTERS LAYER                                 |
|  - TelegramBotAdapter (aiogram 3.x)                                               |
|  - RestApiAdapter (FastAPI Routing)                                               |
+-----------------------------------------+-----------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        APPLICATION & DOMAIN CORE LAYER                            |
|  - CreateTransactionUseCase                                                       |
|  - ManageAccountUseCase & ManageCategoryUseCase                                   |
|  - ManageBudgetUseCase                                                            |
+-----------------------------------------+-----------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           OUTBOUND ADAPTERS (PORTS)                               |
|  - TransactionRepository (PostgreSQL + pgvector via Async SQLAlchemy 2.0)         |
|  - SpeechToTextAdapter (Faster-Whisper Local CPU)                                 |
|  - LLMStructuredOutputAdapter (Ollama + Instructor)                               |
|  - AsyncWorkerQueue (Redis 7 + ARQ Worker)                                        |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ Tech Stack

| Component | Technology | Rationale |
| --- | --- | --- |
| **Language & Framework** | Python 3.12 + FastAPI | Async event loop (`uvloop`), Pydantic v2 schemas, and automatic OpenAPI generation. |
| **Database** | PostgreSQL 16 + `pgvector` | ACID transactions, relational integrity, and native vector embeddings search. |
| **Task Queue & Cache** | Redis 7 + ARQ | Event-driven background worker queue for audio transcription and Redis draft state storage. |
| **Speech-to-Text** | `faster-whisper` (Local CPU) | Sub-second offline transcription for Spanish/multilingual voice notes. |
| **Local LLM Engine** | Ollama (`llama3.2:3b` / `qwen2.5-coder:1.5b`) | Zero-cost, 100% private structured JSON data extraction. |
| **Containerization** | Docker & Docker Compose | Multi-container orchestration (FastAPI, Postgres, Redis, ARQ Worker, Web UI). |

---

## 📱 Telegram Bot Configuration Guide

### 1. Create your Telegram Bot
1. Open Telegram and search for [@BotFather](https://t.me/botfather).
2. Send `/newbot` and follow the prompts to choose a name and username for your bot.
3. Copy the HTTP API token generated (e.g. `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

### 2. Get your Telegram User ID
For security, the bot only responds to whitelisted user IDs:
1. Search for [@userinfobot](https://t.me/userinfobot) or [@raw_data_bot](https://t.me/raw_data_bot) on Telegram.
2. Send a message to get your numerical User ID (e.g. `12345678`).

---

## 🚀 Environment Setup & Deployment

### Prerequisites
- Docker & Docker Compose installed.
- Ollama installed locally (`ollama pull llama3.2` or `ollama pull qwen2.5-coder:1.5b`).

### 1. Configure Environment Variables
Copy `.env.example` to `.env` in the root and backend directories:
```bash
cp backend/.env.example backend/.env
```
Fill in your credentials in `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/smart_finance
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
TELEGRAM_ALLOWED_USER_IDS=[12345678]
OLLAMA_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2
```

### 2. Launch Services with Docker Compose
Start PostgreSQL and Redis in the background:
```bash
docker-compose up -d db redis
```

### 3. Run Database Migrations & Seed Data
```bash
cd backend
source venv/bin/activate
alembic upgrade head
python seed_db.py
```

### 4. Start the Application & Workers
In separate terminal windows:

- **Start Backend API:**
  ```bash
  uvicorn src.main:app --reload
  ```
- **Start ARQ Background Worker (Telegram Ingestion):**
  ```bash
  export PYTHONPATH=.
  arq src.infrastructure.adapters.tasks.worker.WorkerSettings
  ```
- **Start Frontend Web Dashboard:**
  ```bash
  cd frontend
  npm run dev
  ```

---

## 🛡️ License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
