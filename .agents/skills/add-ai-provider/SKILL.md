---
name: add-ai-provider
description: Pasos deterministas para añadir o integrar un nuevo proveedor/modelo de IA (Local o Cloud) en el sistema.
---

# Skill: Añadir Proveedor o Modelo de IA (LLM / STT / OCR)

**Contexto**: Esta skill guía la integración determinista de un nuevo proveedor (ej. Ollama, Groq, OpenAI, Gemini, Local PyTorch) en la arquitectura del proyecto.

**Instrucciones de checklist a seguir:**

1. **Variables de Entorno y Configuración**:
   - Registrar la clave de API o URL del servicio en `.env.example` y en `backend/src/config.py` con Pydantic Settings.

2. **Puerto de Aplicación (Interface)**:
   - Verificar si existe la interfaz abstracta en `src/application/ports/` (ej. `llm_port.py`, `stt_port.py`). Si no, crearla.

3. **Adaptador de Infraestructura**:
   - Crear la implementación concreta en `src/infrastructure/adapters/llm/` o `stt/` herada del puerto.
   - Asegurar manejo de fallbacks y reintentos ante timeouts.

4. **Inyección de Dependencias / Factory**:
   - Actualizar el selector de proveedores para instanciar el nuevo adaptador según la variable de entorno activa.

5. **Prueba de Integración**:
   - Añadir un test en `backend/tests/unit/` verificando la respuesta estructurada del nuevo proveedor.
