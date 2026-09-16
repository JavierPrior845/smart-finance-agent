from fastapi import APIRouter, Depends, HTTPException, status
from src.infrastructure.adapters.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from src.infrastructure.adapters.db.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.adapters.db.models.user import UserORM
from src.infrastructure.api.dependencies import get_user_repo, get_current_user
from src.infrastructure.api.v1.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
    SetupStatusResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/setup-status", response_model=SetupStatusResponse)
async def get_setup_status(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    """Indica si el sistema ya tiene usuarios creados o está en primer arranque."""
    count = await user_repo.count_users()
    return SetupStatusResponse(is_configured=count > 0, user_count=count)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    """Registra el primer administrador o un nuevo usuario y emite un token de 1 hora."""
    existing_user = await user_repo.get_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este correo electrónico.",
        )

    # Si es el primer usuario en la base de datos, asigna rol 'admin'
    user_count = await user_repo.count_users()
    role = "admin" if user_count == 0 else "user"

    hashed_pw = hash_password(payload.password)
    user = await user_repo.create_user(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_pw,
        role=role,
    )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    await user_repo.update_token(user.id, access_token)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLoginRequest,
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    """Inicia sesión con email y contraseña, devolviendo un Bearer Token válido por 1 hora."""
    user = await user_repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta de usuario está desactivada.",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role}
    )
    await user_repo.update_token(user.id, access_token)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserORM = Depends(get_current_user),
):
    """Retorna la información del usuario autenticado actual."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: UserORM = Depends(get_current_user),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repo),
):
    """Cierra la sesión invalidando el current_token en base de datos."""
    await user_repo.update_token(current_user.id, None)
    return {"message": "Sesión cerrada correctamente"}
