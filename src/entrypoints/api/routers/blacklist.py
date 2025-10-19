from fastapi import APIRouter, Depends, HTTPException, Request, status

from assembly import get_add_email_use_case, get_check_email_use_case
from domain.schemas import (
    BlacklistCheckResponse,
    BlacklistCreateRequest,
    BlacklistCreateResponse,
)
from domain.use_cases import AddEmailToBlacklistUseCase, CheckEmailInBlacklistUseCase
from entrypoints.api.dependencies import get_client_ip, verify_token
from errors import DuplicateEmailError

router = APIRouter(prefix="/blacklists", tags=["blacklists"])


@router.post(
    "",
    response_model=BlacklistCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar email a lista negra",
    description="""
    Agrega un email a la lista negra global de la organización.
    
    El sistema registra automáticamente:
    - Dirección IP del cliente (de headers X-Forwarded-For, X-Real-IP o conexión directa)
    - Fecha y hora exacta de la solicitud (UTC)
    
    Parámetros requeridos:
    - **email**: Dirección de email válida
    - **app_uuid**: UUID de la aplicación cliente que hace la solicitud
    - **blocked_reason**: (Opcional) Motivo del bloqueo, máximo 255 caracteres
    
    Notas importantes:
    - El email no puede estar duplicado en la lista negra
    - El UUID debe tener formato válido
    - Requiere autenticación mediante Bearer Token
    """,
    response_description="Email agregado exitosamente a la lista negra",
    responses={
        201: {
            "description": "Email agregado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Email added to blacklist successfully",
                        "email": "spam@example.com",
                        "blocked_at": "2024-10-19T14:30:00.123456"
                    }
                }
            }
        },
        401: {
            "description": "Token de autenticación inválido o faltante",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid authentication token"}
                }
            }
        },
        409: {
            "description": "El email ya existe en la lista negra",
            "content": {
                "application/json": {
                    "example": {"detail": "Email spam@example.com already exists in blacklist"}
                }
            }
        },
        422: {
            "description": "Error de validación en los datos de entrada",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def add_email_to_blacklist(
    request: Request,
    data: BlacklistCreateRequest,
    add_email_use_case: AddEmailToBlacklistUseCase = Depends(get_add_email_use_case),
    token: str = Depends(verify_token),
) -> BlacklistCreateResponse:
    try:
        ip_address = get_client_ip(request)
        result = await add_email_use_case.execute(data, ip_address)
        return result
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "/{email}",
    response_model=BlacklistCheckResponse,
    summary="Consultar email en lista negra",
    description="""
    Consulta si un email específico está en la lista negra global de la organización.
    
    Retorna información completa sobre el estado del email:
    - Si está bloqueado o no
    - Motivo del bloqueo (si aplica)
    - Fecha y hora del bloqueo (si aplica)
    
    Parámetro de ruta:
    - **email**: Dirección de email a consultar
    
    Casos de uso:
    - Validar si un usuario puede registrarse
    - Verificar acceso antes de permitir operaciones
    - Auditoría y consultas de historial
    - Integración con múltiples sistemas
    
    Notas:
    - Retorna estado 200 tanto si el email está bloqueado como si no
    - Requiere autenticación mediante Bearer Token
    """,
    response_description="Estado del email en la lista negra",
    responses={
        200: {
            "description": "Consulta exitosa - Email bloqueado",
            "content": {
                "application/json": {
                    "examples": {
                        "blocked": {
                            "summary": "Email bloqueado",
                            "value": {
                                "email": "spam@example.com",
                                "is_blocked": True,
                                "blocked_reason": "Usuario reportado por spam",
                                "blocked_at": "2024-10-19T14:30:00.123456"
                            }
                        },
                        "not_blocked": {
                            "summary": "Email no bloqueado",
                            "value": {
                                "email": "clean@example.com",
                                "is_blocked": False,
                                "blocked_reason": None,
                                "blocked_at": None
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Token de autenticación inválido o faltante",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid authentication token"}
                }
            }
        }
    }
)
async def check_email_in_blacklist(
    email: str,
    check_email_use_case: CheckEmailInBlacklistUseCase = Depends(get_check_email_use_case),
    token: str = Depends(verify_token),
) -> BlacklistCheckResponse:
    result = await check_email_use_case.execute(email)
    return result

