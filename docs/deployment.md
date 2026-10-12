# 🚀 Guía de Despliegue y Actualizaciones en Producción

Esta guía describe el protocolo oficial y seguro para desplegar actualizaciones de **Smart Finance Agent** en entornos de producción con **Docker**, asegurando la **cero pérdida de datos**, compatibilidad de esquemas con **Alembic**, y mínimo o nulo tiempo de inactividad (*Zero Downtime*).

---

## 🛡️ Reglas de Oro en Producción

> [!CAUTION]
> **1. NUNCA ejecutes `docker compose down -v`:** La bandera `-v` elimina los volúmenes persistentes (`postgres_data`), destruyendo la base de datos de producción irreversiblemente.
>
> **2. NUNCA ejecutes `./manage.sh consolidate-migrations` en producción:** Dicho comando está reservado exclusivamente para la inicialización o reestructuración de desarrollo; borra el historial de revisiones y la tabla `alembic_version`.
>
> **3. SIEMPRE realiza un backup previo:** Antes de tocar ramas, reconstruir imágenes o correr migraciones, exporta una copia con `pg_dump`.

---

## 📋 Protocolo de Despliegue Seguro (Paso a Paso)

### Paso 1: Backup Preventivo de la Base de Datos

Exporta un volcado SQL completo de la base de datos `smart_finance` a una carpeta de backups segura fuera del repositorio o en una ruta controlada:

```bash
# Crear directorio de backups si no existe
mkdir -p ../backups

# Generar volcado con timestamp
docker compose exec -T db pg_dump -U postgres -d smart_finance > ../backups/backup_smart_finance_$(date +%Y%m%d_%H%M%S).sql
```

Verifica que el archivo se haya creado correctamente y su tamaño sea consistente:
```bash
ls -lh ../backups/backup_smart_finance_*.sql
```

---

### Paso 2: Integrar y Actualizar el Código en `main`

Producción se despliega siempre desde la rama `main`:

```bash
# Cambiar a la rama principal y descargar los últimos cambios
git checkout main
git pull origin main
```

Si tus cambios procedían de ramas de funcionalidad o de `develop`, asegúrate de que los Pull Requests o merges estén completados y probados.

---

### Paso 3: Verificación de Migraciones de Base de Datos

Antes de aplicar migraciones a ciegas, verifica si los cambios realmente requieren alterar el esquema de PostgreSQL:

#### ¿Cuándo HACE FALTA una migración?
* Se añade, renombra o elimina una columna en un modelo ORM de `backend/src/infrastructure/adapters/db/models/`.
* Se crea una nueva tabla o relación foránea.
* Se modifica el tipo de datos físico en PostgreSQL (por ejemplo, de `VARCHAR` a `INTEGER`).

#### ¿Cuándo NO hace falta una migración?
* **Nuevos tipos en Pydantic / Enums de Python:** Si el modelo de BD ya almacena la columna como `String(30)` o `VARCHAR`, cualquier nuevo valor aceptado por las reglas de negocio de Python se guarda de forma nativa sin tocar la estructura de la tabla.
* Correcciones en endpoints, vistas de React, lógica de casos de uso o consultas analíticas.

#### ⚠️ Advertencia sobre `pgvector` y `alembic revision --autogenerate`:
El generador automático de Alembic no siempre detecta índices HNSW de `pgvector` (`idx_transactions_embedding`). Si ejecutas `autogenerate` sin cambios reales de esquema, Alembic generará erróneamente un comando `op.drop_index(...)`. 

* Si el archivo generado solo contiene `drop_index` sobre `idx_transactions_embedding`, **no es una migración válida** y debes eliminar el archivo con `rm backend/alembic/versions/*_<nombre>.py`.
* Si hay un cambio legítimo de esquema, asegúrate de revisar el archivo en `backend/alembic/versions/` antes de aplicarlo.

---

### Paso 4: Recompilar Imágenes de Aplicación

El Frontend (`frontend`) utiliza un contenedor Nginx con los estáticos generados durante el `docker build` (`npm run build`). Por su parte, la API (`api`) y el Worker (`worker`) instalan sus dependencias durante el build.

Reconstruye **únicamente** los servicios de aplicación, sin tocar los contenedores de datos (`db` y `redis`):

```bash
docker compose build api worker frontend
```

---

### Paso 5: Aplicar Migraciones Pendientes (Si Aplica)

Si el nuevo código incluye un archivo de migración legítimo en `backend/alembic/versions/`, aplícalo ahora:

```bash
docker compose exec api alembic upgrade head
```

Comprueba que la base de datos se encuentra sincronizada en el *head* actual:
```bash
docker compose exec api alembic current
```

---

### Paso 6: Recrear y Reiniciar Contenedores (Zero Downtime)

Aplica las nuevas imágenes levantando los servicios de aplicación con el flag `--no-deps`:

```bash
docker compose up -d --no-deps api worker frontend
```

> [!TIP]
> Al usar `--no-deps api worker frontend`, Docker Compose actualiza y sustituye los contenedores del backend y frontend de forma suave (*rolling restart*), mientras que `db` (PostgreSQL) y `redis` permanecen activos sin reiniciar ni cerrar sus conexiones de red.

---

### Paso 7: Comprobaciones Post-Despliegue

1. **Verificar el estado de todos los contenedores:**
   ```bash
   docker compose ps
   ```
   *Todos los servicios (`api`, `worker`, `frontend`, `db`, `redis`) deben aparecer en estado `Up` o `healthy`.*

2. **Validar el Healthcheck de la API:**
   ```bash
   curl -i http://localhost:8000/health
   ```
   *Debe responder HTTP `200 OK` con `{"status": "healthy"}`.*

3. **Inspeccionar los logs en busca de excepciones:**
   ```bash
   docker compose logs --tail=40 -f api
   ```

4. **Comprobar la interfaz Web:**
   Abre en el navegador `http://localhost` (o el puerto configurado en `FRONTEND_PORT`) y valida que:
   * La sesión siga activa.
   * Las nuevas pantallas o componentes aparezcan correctamente.
   * No existan errores en la consola del navegador (`F12`).

---

## 🛟 Plan de Contingencia y Rollback

Si tras el despliegue se detecta un error crítico inesperado:

### 1. Revertir el Código de la Aplicación
```bash
# Cambiar al commit o tag previo estable
git checkout <commit_anterior_o_tag>

# Recompilar y levantar de nuevo
docker compose build api worker frontend
docker compose up -d --no-deps api worker frontend
```

### 2. Restaurar la Base de Datos (Si se ejecutó una migración incompatible)
```bash
# Terminar conexiones activas a la base de datos
docker compose exec -T db psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'smart_finance' AND pid <> pg_backend_pid();"

# Recrear la base de datos vacía
docker compose exec -T db psql -U postgres -d postgres -c "DROP DATABASE smart_finance;"
docker compose exec -T db psql -U postgres -d postgres -c "CREATE DATABASE smart_finance;"

# Restaurar el volcado previo
cat ../backups/backup_smart_finance_<TIMESTAMP>.sql | docker compose exec -T db psql -U postgres -d smart_finance

# Verificar que los datos han sido restaurados
docker compose exec -T db psql -U postgres -d smart_finance -c "SELECT count(*) FROM transactions;"
```

---

## 🗂️ Resumen Rápido de Comandos

| Acción | Comando |
| :--- | :--- |
| **Backup Inmediato** | `docker compose exec -T db pg_dump -U postgres -d smart_finance > ../backups/backup_$(date +%Y%m%d_%H%M%S).sql` |
| **Recompilar App** | `docker compose build api worker frontend` |
| **Aplicar Migración** | `docker compose exec api alembic upgrade head` |
| **Actualizar Contenedores** | `docker compose up -d --no-deps api worker frontend` |
| **Ver Estado y Salud** | `docker compose ps && curl -i http://localhost:8000/health` |
| **Ver Logs en Directo** | `docker compose logs -f api` |
