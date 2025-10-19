from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from config import settings
from db.session import database
from entrypoints.api.routers import blacklist_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await database.close()


app = FastAPI(
    title="Blacklist API - Gestión de Lista Negra de Emails",
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "ng.caicedo@uniandes.edu.co",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "blacklists",
            "description": "Operaciones de gestión de lista negra de emails",
        },
        {
            "name": "health",
            "description": "Health check y monitoreo",
        },
    ],
)

app.include_router(blacklist_router)


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="Verifica que el servicio esté funcionando correctamente. No requiere autenticación.",
    response_description="Estado del servicio",
    responses={
        200: {
            "description": "Servicio funcionando correctamente",
            "content": {
                "application/json": {
                    "example": {"status": "healthy"}
                }
            }
        }
    }
)
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )

