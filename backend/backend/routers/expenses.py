from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend import models
from backend.database import get_session
from backend.schemas import (
    Expense,
    ExpenseDB,
    ExpenseDBItem,
    Message,
)
from backend.security import get_current_user

DBSession = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[models.User, Depends(get_current_user)]

router = APIRouter()


@router.post(
    '/expenses/', response_model=ExpenseDBItem, status_code=HTTPStatus.CREATED
)
async def create_expense(
    body: Expense, db_session: DBSession, user: CurrentUser
):

    query_result = await db_session.scalar(
        select(models.Expense).where((models.Expense.title == body.title))
    )

    if query_result:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Title already exists'
        )

    new_expense = models.Expense(
        user_id=user.id,
        title=body.title,
        description=body.description,
        value=body.value,
    )
    db_session.add(new_expense)
    await db_session.commit()
    await db_session.refresh(new_expense)

    return new_expense


@router.get('/expenses/', response_model=ExpenseDB)
async def list_expenses(db_session: DBSession, user: CurrentUser):
    return {'expenses': user.expenses}


@router.put('/expenses/{expense_id}', response_model=ExpenseDBItem)
async def update_expense(
    expense_id: int,
    body: Expense,
    db_session: DBSession,
    user: CurrentUser,
):
    expense = await db_session.scalar(
        select(models.Expense).where(models.Expense.id == expense_id)
    )
    if not expense:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    if user.id != expense.user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='User not own expense'
        )

    try:
        expense.value = body.value
        expense.title = body.title
        expense.description = body.description
        await db_session.commit()
        await db_session.refresh(expense)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Title already exists'
        )

    return expense


@router.delete('/expenses/{expense_id}', response_model=Message)
async def delete_expense(
    expense_id: int, db_session: DBSession, user: CurrentUser
):

    # print(user)

    expense = await db_session.scalar(
        select(models.Expense).where(models.Expense.id == expense_id)
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Expense not found',
        )
    await db_session.delete(expense)
    await db_session.commit()
    return {'message': 'Expense deleted'}
