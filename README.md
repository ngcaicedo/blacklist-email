# Blacklist API

API REST para gestión de lista negra global de emails utilizando arquitectura hexagonal.

## Características

- **POST /blacklists**: Agregar un email a la lista negra global
- **GET /blacklists/{email}**: Consultar si un email está en la lista negra
- Autenticación mediante Bearer Token estático
- Base de datos PostgreSQL
- Arquitectura Hexagonal (Ports & Adapters)

## Requisitos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- Poetry (para gestión de dependencias)

## Configuración

### Variables de Entorno

- `DATABASE_URL`: URL de conexión a PostgreSQL (default: postgresql+asyncpg://blacklist_user:blacklist_pass@localhost:5432/blacklist_db)
- `AUTH_TOKEN`: Token de autenticación estático (default: bearer-token-static-2024)
- `APP_NAME`: Nombre de la aplicación (default: Blacklist API)
- `DB_ECHO`: Habilitar logs SQL (default: False)

## Ejecución con Docker Compose

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:9000`

## Despliegue en AWS Elastic Beanstalk

El proyecto está configurado para despliegue en AWS Elastic Beanstalk con:

- ✅ Health check configurado en `/health`
- ✅ Auto scaling configurado
- ✅ Variables de entorno predefinidas
- ✅ Configuración de nginx optimizada

### Quick Start

```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar (ya configurado)
eb init

# Crear environment
eb create blacklist-api-production

# Configurar base de datos
eb setenv DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/dbname"

# Desplegar
eb deploy
```

## Ejecución Local

1. Instalar dependencias:

```bash
poetry install
```

2. Ejecutar PostgreSQL:

```bash
docker-compose up postgres -d
```

3. Configurar variables de entorno:

```bash
export DATABASE_URL="postgresql+asyncpg://blacklist_user:blacklist_pass@localhost:5432/blacklist_db"
export AUTH_TOKEN="bearer-token-static-2024"
```

4. Ejecutar la aplicación:

```bash
poetry run uvicorn entrypoints.api.main:app --host 0.0.0.0 --port 9000 --reload
```

## Endpoints

### Health Check

```bash
GET /health
```

### Agregar Email a Lista Negra

```bash
POST /blacklists
Authorization: Bearer bearer-token-static-2024
Content-Type: application/json

{
  "email": "test@example.com",
  "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "blocked_reason": "Spam detected"
}
```

Respuesta exitosa (201):
```json
{
  "message": "Email added to blacklist successfully",
  "email": "test@example.com",
  "blocked_at": "2024-10-19T12:00:00"
}
```

### Consultar Email en Lista Negra

```bash
GET /blacklists/{email}
Authorization: Bearer bearer-token-static-2024
```

Respuesta (200):
```json
{
  "email": "test@example.com",
  "is_blocked": true,
  "blocked_reason": "Spam detected",
  "blocked_at": "2024-10-19T12:00:00"
}
```

## 📖 Documentación de la API

### Documentación Interactiva

Una vez que la API esté ejecutándose, accede a:

- **Swagger UI**: http://localhost:9000/docs
- **ReDoc**: http://localhost:9000/redoc

### Pruebas con Postman

La colección completa de Postman incluye:
- ✅ 3 endpoints documentados (Health, POST, GET)
- ✅ Tests automatizados
- ✅ Múltiples ejemplos de respuesta
- ✅ Variables de entorno configuradas

**Archivos incluidos:**
- `Blacklist_API.postman_collection.json` - Colección completa
- `Blacklist_API.postman_environment.json` - Variables de entorno

**Guía completa:** Ver `POSTMAN_DOCUMENTATION_GUIDE.md`

#### Importar en Postman

1. Abrir Postman
2. Importar `Blacklist_API.postman_collection.json`
3. Importar `Blacklist_API.postman_environment.json`
4. Seleccionar el environment "Blacklist API - Development"
5. Ejecutar los requests de prueba

#### Publicar Documentación

**Quick Start**: Ver `QUICK_START_POSTMAN.md` (5 minutos)

**Guía Completa**: Ver `POSTMAN_DOCUMENTATION_GUIDE.md` para:
- Publicar la documentación en Postman
- Crear workspace de equipo
- Compartir la URL con el equipo
- Escenarios de prueba detallados

## Arquitectura

El proyecto sigue la arquitectura hexagonal (Ports & Adapters):

```
src/
├── domain/           # Lógica de negocio
│   ├── schemas/     # DTOs
│   ├── ports/       # Interfaces
│   └── use_cases/   # Casos de uso
├── adapters/        # Implementaciones
│   ├── models/      # Modelos SQLModel
│   └── repositories/
├── entrypoints/     # Puntos de entrada
│   └── api/        # FastAPI
├── db/             # Configuración BD
├── assembly.py     # Dependency Injection
└── config.py       # Configuración
```

## Base de Datos

La aplicación crea automáticamente la tabla `blacklists` al iniciar con los siguientes campos:

- `id`: Identificador único (autoincremental)
- `email`: Email en la lista negra (único)
- `app_uuid`: UUID de la aplicación cliente
- `blocked_reason`: Motivo del bloqueo (opcional, máx 255 chars)
- `ip_address`: Dirección IP desde donde se hizo la solicitud
- `created_at`: Fecha y hora de creación

## Tecnologías

- FastAPI
- SQLModel
- PostgreSQL
- asyncpg
- Docker
- Poetry

