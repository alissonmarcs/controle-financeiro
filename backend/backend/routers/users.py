from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy import select

from backend import schemas
from backend import models

from sqlalchemy.orm import Session
from backend.database import get_session

from http import HTTPStatus

from sqlalchemy.exc import IntegrityError

from backend.security import get_password_hash, verify_password, create_access_token

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post('/users/', response_model=schemas.CreatedUser, status_code=HTTPStatus.CREATED)
def create_user(
        body: schemas.User,
        db_session: Session = Depends(get_session)
):
    hashed_password = get_password_hash(body.password)
    new_user = models.User(username=body.username, email=body.email, password=hashed_password)

    try:
        db_session.add(new_user)
        db_session.commit()
        db_session.refresh(new_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists'
        )

    return new_user

@router.get('/users/{user_id}', response_model=schemas.CreatedUser, status_code=HTTPStatus.OK)
def get_user(
        user_id: int,
        db_session: Session = Depends(get_session),
):
    query_result = db_session.scalar(select(models.User).where(models.User.id == user_id))
    if not query_result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )
    return query_result

@router.get('/users/', response_model=schemas.Users , status_code=HTTPStatus.OK)
def get_users(
        db_session: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    query_result = db_session.scalars(select(models.User).offset(skip).limit(limit)).all()

    return {'users': query_result}

@router.put('/users/{user_id}', response_model=schemas.CreatedUser, status_code=HTTPStatus.OK)
def update_user(
    user_id: int,
    body: schemas.User,
    db_session: Session = Depends(get_session)
):
    query_result = db_session.scalar(select(models.User).where(models.User.id == user_id))
    if not query_result:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not exists'
        )

    try:
        query_result.username = body.username
        query_result.email = body.email
        query_result.password = get_password_hash(body.password)
        db_session.commit()
        db_session.refresh(query_result)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists'
        )
    return query_result

@router.delete('/users/{user_id}', response_model=schemas.Message)
def delete_user(
    user_id: int,
    db_session: Session = Depends(get_session)
):
    user = db_session.scalar(select(models.User).where(models.User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )
    db_session.delete(user)
    db_session.commit()
    return {'message': 'User deleted'}

@router.post('/token', response_model=schemas.Token)
def get_access_token(
   form_data: OAuth2PasswordRequestForm = Depends(),
   db_session: Session = Depends(get_session)
):
    user = db_session.scalar(select(models.User).where(models.User.email == form_data.username))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password'
        )
    token = create_access_token({'sub': user.email})
    return {'access_token': token, 'token_type': 'bearer'}
