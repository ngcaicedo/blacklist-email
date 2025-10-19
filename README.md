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

#### Variables de Base de Datos (RDS)
- `RDS_HOSTNAME`: Host de la base de datos PostgreSQL
- `RDS_USERNAME`: Usuario de PostgreSQL
- `RDS_PASSWORD`: Contraseña de PostgreSQL
- `RDS_DB_NAME`: Nombre de la base de datos
- `RDS_PORT`: Puerto de PostgreSQL (default: 5432)

#### Variables de Aplicación
- `AUTH_TOKEN`: Token de autenticación estático (default: bearer-token-static-2024)
- `APP_NAME`: Nombre de la aplicación (default: Blacklist API)
- `DB_ECHO`: Habilitar logs SQL (default: False)

> **Nota**: El proyecto usa variables de entorno compatibles con AWS RDS, lo que facilita la integración con Elastic Beanstalk.

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
- ✅ Integración nativa con AWS RDS

### Quick Start

```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar (ya configurado)
eb init

# Crear environment
eb create blacklist-api-production

# Configurar base de datos RDS (opción 1: usando RDS de AWS)
# Si conectas una instancia RDS desde la consola de EB, las variables se configuran automáticamente

# Configurar base de datos manualmente (opción 2)
eb setenv \
  RDS_HOSTNAME="your-rds-endpoint.rds.amazonaws.com" \
  RDS_USERNAME="your_user" \
  RDS_PASSWORD="your_password" \
  RDS_DB_NAME="blacklist_db" \
  RDS_PORT="5432"

# Desplegar
eb deploy
```

### Configuración de RDS en Elastic Beanstalk

Elastic Beanstalk puede configurar automáticamente las variables de entorno RDS cuando vinculas una instancia de base de datos al environment. Esto hace que la aplicación se integre sin configuración adicional.

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
export RDS_HOSTNAME="localhost"
export RDS_USERNAME="blacklist_user"
export RDS_PASSWORD="blacklist_pass"
export RDS_DB_NAME="blacklist_db"
export RDS_PORT="5433"
export AUTH_TOKEN="bearer-token-static-2024"
```

> **Nota**: El puerto 5433 se usa porque docker-compose mapea PostgreSQL al puerto 5433 del host para evitar conflictos con instalaciones locales de PostgreSQL.

4. Ejecutar la aplicación:

```bash
poetry run uvicorn entrypoints.api.main:app --host 0.0.0.0 --port 9000 --reload
```

**Alternativa**: Ejecutar todo con Docker Compose:

```bash
docker-compose up --build
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

