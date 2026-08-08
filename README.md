# 🏦 Smart Finance Agent

> **Production-Grade Personal Finance Manager featuring Multi-Channel Ingestion (Voice / OCR / Text), Hexagonal Architecture, and Hybrid AI Categorization.**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B%20%7C%20pgvector-336791.svg)](https://www.postgresql.org/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot%20API-2CA5E0.svg)](https://core.telegram.org/bots)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Project Overview

**Smart Finance Agent** is a production-ready personal finance backend built on core software engineering principles: **zero quantitative hallucinations**, **low-friction multi-channel ingestion**, and **complete decoupling between the financial domain and AI providers**.

Unlike naïve LLM-wrapper applications, all accounting calculations, budget tracking, data aggregation, and anomaly detections are computed **deterministically** via Python and PostgreSQL. Large Language Models (LLMs) and Vision/Speech models are leveraged strictly for natural language understanding (Speech-to-Text), receipt OCR parsing, structured data extraction, and synthesizing actionable financial insights.

---

## ✨ Key Features

- 🎙️ **Low-Friction Multi-Channel Ingestion:** Register expenses in under 3 seconds via Telegram voice notes (Whisper STT), receipt photographs (Vision OCR), free-form text messages, or web UI.
- ⚡ **3-Tiered Hybrid Categorization:**
  1. *Tier 1:* Regex / Deterministic Dictionary matching ($<1\text{ms}$ latency, $\$0$ cost).
  2. *Tier 2:* Vector Similarity Search via `pgvector` ($\sim10\text{ms}$ latency, $\$0$ cost).
  3. *Tier 3:* LLM Structured Output (`Claude-3.5-Haiku` / `GPT-4o-mini` with Pydantic schemas) ($\sim600\text{ms}$ latency).
- 🧮 **Deterministic Quantitative Engine:** Financial metrics, budget progress, and anomaly detection (Robust Z-Score / IQR) computed entirely via SQL & Python DataFrames.
- 🤝 **Human-in-the-Loop Confirmation:** Interactive Telegram inline keyboards to review, modify, or confirm expenses before database insertion.
- 💻 **Web Application & Dashboard UI:** A containerized web interface for visual budget visualization, expense management, and manual entry alongside Telegram.
- 🏛️ **Hexagonal Architecture (Ports & Adapters):** Core domain fully isolated from external frameworks, Telegram APIs, and AI models for maximum testability.

---

## 🏗️ System Architecture

```
                       +------------------------------------+
                       |           DATA SOURCES             |
                       +------------------------------------+
                       | Telegram (Audio / Photo / Text)    |
                       | Web UI Dashboard / Manual Entry    |
                       | Bank CSV / PDF Statement Importer  |
                       +-----------------+------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                            INBOUND ADAPTERS LAYER                                 |
|  - TelegramBotAdapter (aiogram)                                                   |
|  - BankStatementParserAdapter (polars, pdfplumber)                                |
|  - RestApiAdapter (FastAPI Routing)                                               |
+-----------------------------------------+-----------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        APPLICATION & DOMAIN CORE LAYER                            |
|  - ProcessTransactionUseCase                                                      |
|  - CategorizeTransactionUseCase (3-Tier Cascade)                                  |
|  - FinancialCalculator & BudgetAnomalyDetector                                    |
+-----------------------------------------+-----------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           OUTBOUND ADAPTERS (PORTS)                               |
|  - TransactionRepository (PostgreSQL + pgvector via Async SQLAlchemy 2.0)         |
|  - SpeechToTextAdapter (Whisper API / Groq)                                       |
|  - LLMStructuredOutputAdapter (Instructor / OpenAI / Anthropic)                   |
|  - AsyncWorkerQueue (Redis + ARQ)                                                 |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ Tech Stack

| Component | Technology | Rationale |
| --- | --- | --- |
| **Language & Framework** | Python 3.12 + FastAPI | Async event loop (`uvloop`), Pydantic v2 schemas, and automatic OpenAPI generation. |
| **Database** | PostgreSQL 16 + `pgvector` | ACID transactions, relational integrity, and native vector embeddings search without external vector DB complexity. |
| **Async Task Queue** | Redis + ARQ | Asynchronous background processing for heavy audio/OCR tasks without blocking HTTP/Telegram webhooks. |
| **Speech-to-Text** | OpenAI Whisper (via Groq API) | Sub-second latency for Spanish/multilingual voice notes. |
| **LLM Engine** | Claude-3.5-Haiku / GPT-4o-mini | Sub-second structured JSON output with Pydantic schemas. |
| **Containerization** | Docker & Docker Compose | Multi-container environment orchestration (FastAPI, Postgres, Redis, Worker, Telegram Bot, Web UI). |

---

## 🚀 Quickstart Guide

### Prerequisites
- Docker & Docker Compose installed.
- Telegram Bot Token (from [@BotFather](https://t.me/botfather)).
- OpenAI API Key or Groq API Key.

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/smart-finance-agent.git
   cd smart-finance-agent
   ```

2. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, etc.)
   ```

3. **Launch Infrastructure with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

4. **Run Database Migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

---

## 💻 Desarrollo Local (Backend)

Si deseas trabajar en el código de forma local sin usar el contenedor de Docker para el backend, puedes hacerlo siguiendo estos pasos:

1. **Asegúrate de que la base de datos esté corriendo:**
   ```bash
   docker-compose up -d db
   ```

2. **Entorno Virtual y Dependencias:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Ejecutar el Servidor FastAPI (con Hot-Reload):**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/smart_finance"
   uvicorn src.main:app --reload
   ```
   La API estará disponible en `http://localhost:8000` y la documentación interactiva (Swagger) en `http://localhost:8000/docs`.

4. **Ejecutar los Tests:**
   La suite de pruebas (Unitarias y de Integración) está construida con `pytest`. Para correrla:
   ```bash
   export PYTHONPATH=. 
   pytest tests/ -v
   ```

---

## 🛡️ License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
