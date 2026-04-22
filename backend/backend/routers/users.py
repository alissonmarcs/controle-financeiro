from fastapi import APIRouter, HTTPException, status, Depends, Query

from sqlalchemy import select

from backend import schemas
from backend import models

# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_session
from backend.security import get_current_user

from http import HTTPStatus

from sqlalchemy.exc import IntegrityError

from backend.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)

from fastapi.security import OAuth2PasswordRequestForm

from typing import Annotated

DBSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[models.User, Depends(get_current_user)]

router = APIRouter()


@router.post(
    '/users/',
    response_model=schemas.CreatedUser,
    status_code=HTTPStatus.CREATED,
)
async def create_user(body: schemas.User, db_session: DBSession):
    hashed_password = get_password_hash(body.password)
    new_user = models.User(
        username=body.username, email=body.email, password=hashed_password
    )

    try:
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )

    return new_user


@router.get(
    '/users/{user_id}',
    response_model=schemas.CreatedUser,
    status_code=HTTPStatus.OK,
)
async def get_user(user_id: int, db_session: DBSession):
    query_result = await db_session.scalar(
        select(models.User).where(models.User.id == user_id)
    )
    if not query_result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    return query_result


@router.get('/users/', response_model=schemas.Users, status_code=HTTPStatus.OK)
async def get_users(
    db_session: DBSession, paginator: Annotated[schemas.Pagination, Query()]
):
    query = await db_session.scalars(
        select(models.User).offset(paginator.offset).limit(paginator.limit)
    )

    users = query.all()
    return {'users': users}


@router.put(
    '/users/{user_id}',
    response_model=schemas.CreatedUser,
    status_code=HTTPStatus.OK,
)
async def update_user(
    user_id: int,
    body: schemas.User,
    db_session: DBSession,
    current_user: CurrentUser,
):

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = body.username
        current_user.email = body.email
        current_user.password = get_password_hash(body.password)
        await db_session.commit()
        await db_session.refresh(current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )
    return current_user


@router.delete('/users/{user_id}', response_model=schemas.Message)
async def delete_user(
    user_id: int,
    db_session: DBSession,
    current_user: CurrentUser,
):

    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    await db_session.delete(current_user)
    await db_session.commit()
    return {'message': 'User deleted'}


@router.post('/token', response_model=schemas.Token)
async def get_access_token(
    db_session: DBSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await db_session.scalar(
        select(models.User).where(models.User.email == form_data.username)
    )
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )
    token = create_access_token({'sub': user.email})
    return {'access_token': token, 'token_type': 'bearer'}


@router.get('/refresh_token', response_model=schemas.Token)
async def refresh_token(
    current_user: CurrentUser,
):
    token = create_access_token({'sub': current_user.email})
    return {'access_token': token, 'token_type': 'bearer'}
