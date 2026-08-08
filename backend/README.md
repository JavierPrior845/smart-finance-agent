# Smart Finance Agent - Backend

Este directorio contiene el motor principal del proyecto Gestor de Finanzas, desarrollado en Python 3.12 con FastAPI y PostgreSQL (vía SQLAlchemy 2.0).

## 💻 Desarrollo Local

Si deseas trabajar en el código de forma local sin usar el contenedor de Docker para el backend, puedes hacerlo siguiendo estos pasos:

1. **Asegúrate de que la base de datos esté corriendo:**
   Si tienes configurado el `docker-compose` en la raíz del proyecto, asegúrate de levantar el servicio de DB:
   ```bash
   docker-compose up -d db
   ```

2. **Entorno Virtual y Dependencias:**
   ```bash
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
