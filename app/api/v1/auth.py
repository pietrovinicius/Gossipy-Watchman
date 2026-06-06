import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from app.core.settings import settings
from app.services.auth_service import create_access_token, verify_password

logger = logging.getLogger(__name__)

router = APIRouter()

_DEV_FALLBACK_PASS = "watchman"


@router.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends()) -> dict:
    if form.username != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    if settings.ADMIN_PASSWORD_HASH:
        valid = verify_password(form.password, settings.ADMIN_PASSWORD_HASH)
    else:
        logger.warning("ADMIN_PASSWORD_HASH não configurado, usando fallback de desenvolvimento")
        valid = form.password == _DEV_FALLBACK_PASS

    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    token = create_access_token({"sub": form.username})
    return {"access_token": token, "token_type": "bearer"}
