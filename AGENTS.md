# AGENTS.md - Pair Programming & Project Guidelines

Welcome to **Smart Finance Agent**! This repository is configured for Pair Programming with AI Agents using Google Antigravity.

## 📐 Architecture & Standards
- **Hexagonal Architecture**: Keep `domain/` pure Python without external framework imports.
- **Clean Code Rules**: Enforce small functions (<25 lines), strict type hints, explicit domain exceptions. See [`.agents/rules/clean-code.md`](.agents/rules/clean-code.md).
- **Cost Strategy**: 100% Free / Zero-Cost AI stack (Ollama local / Groq API Free Tier, Tesseract / Gemini Free Tier OCR).

## 🛠️ Key Project Commands
- **Run Backend Tests**: `pytest backend/tests`
- **Start Local Stack**: `docker-compose up -d --build`
- **Run DB Migrations**: `docker-compose exec backend alembic upgrade head`

## 🧰 Custom Skills Available
- `clean-refactor`: Refactor complex functions into single-responsibility helpers.
- `add-ai-provider`: Step-by-step checklist to register new local or cloud AI models.
- `auto-document`: Generate Google-style docstrings and update architecture diagrams.
- `commit-message`: Generate Conventional Commit messages.
