from fastapi import APIRouter, HTTPException, status, Depends


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
