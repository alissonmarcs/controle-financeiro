from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from http import HTTPStatus
from jwt import encode, decode, DecodeError, ExpiredSignatureError
from pwdlib import PasswordHash

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

from backend.database import get_session
from backend import models 

from sqlalchemy import select 
from sqlalchemy.orm import Session 

from backend.settings import Settings

from sqlalchemy.ext.asyncio import AsyncSession

password_hasher = PasswordHash.recommended()

settings = Settings()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES 
    )
    to_encode.update({'exp': expire})
    encoded_jwt = encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str):
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hasher.verify(plain_password, hashed_password)

token_extractor = OAuth2PasswordBearer(tokenUrl='token')

async def get_current_user(
    db_session: AsyncSession = Depends(get_session),
    token: str = Depends(token_extractor)
):
    credentials_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject_email = payload.get('sub')

        if not subject_email:
            raise credentials_exception

    except DecodeError:
        raise credentials_exception

    except ExpiredSignatureError:
        raise credentials_exception

    user = await db_session.scalar(select(models.User).where(models.User.email == subject_email))
    if not user:
        raise credentials_exception

    return user