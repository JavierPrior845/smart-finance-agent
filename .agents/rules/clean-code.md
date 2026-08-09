# Rule: Clean Code & Hexagonal Architecture Standards

1. **Single Responsibility Principle (SRP)**:
   - Las funciones y métodos deben ser pequeños (idealmente < 25 líneas) y tener una única razón para cambiar.
   - Extraer lógica compleja o bucles secundarios en funciones auxiliares puras.

2. **Tipado Estricto (Type Hints)**:
   - Todo el código en Python debe incluir anotaciones de tipos completas en argumentos y retornos (`mypy` compliant).

3. **Arquitectura Hexagonal Estricta**:
   - `domain/`: Código Python puro. CERO importaciones de `infrastructure/`, `fastapi`, `sqlalchemy` o proveedores externos.
   - `application/`: Define casos de uso y puertos (interfaces abstractas). No depende de detalles de infraestructura.
   - `infrastructure/`: Implementa los adaptadores concretos (PostgreSQL, Telegram, Ollama, Groq, etc.).

4. **Manejo Explicito de Excepciones**:
   - Prohibido usar `except Exception: pass` o retornos silenciosos `None`.
   - Capturar excepciones específicas e impulsarlas como `DomainException` personalizadas cuando crucen capas.

5. **Documentación Concisa**:
   - Mantener docstrings concisos estilo Google en clases y funciones públicas.
