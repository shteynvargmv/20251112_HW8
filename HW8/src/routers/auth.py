"""Endpoint авторизации."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from auth import config, security
from fastapi import APIRouter, HTTPException, Response
from schemas.custom import CustomLoginSchema
from services.fly_service import FlyService

router = APIRouter(prefix='', tags=['Аутентификация'])

@router.post('/login', summary='Аутентификация пользователя')
def login(credentials: CustomLoginSchema, response: Response):
    """Аутентификация."""
    scustoms = FlyService().get_scustom(('phone','password'), (credentials.phone, credentials.password))
    if len(scustoms) > 0:
        token = security.create_access_token(uid=scustoms[0].phone)
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {'access_token': token}
    
    raise HTTPException(status_code=401, detail='Неверный логин или пароль')