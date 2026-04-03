from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy import select

from backend import schemas
from backend import models

from sqlalchemy.orm import Session
from backend.database import get_session

from http import HTTPStatus

from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post('/users/', response_model=schemas.CreatedUser, status_code=HTTPStatus.CREATED)
def create_user(
        body: schemas.User,
        db_session: Session = Depends(get_session)
):
    new_user = models.User(username=body.username, email=body.email, password=body.password)

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

