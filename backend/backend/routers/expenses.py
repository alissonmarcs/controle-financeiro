from fastapi import APIRouter, HTTPException, status, Depends, Query
from backend.schemas import (
    Expense,
    ExpenseDBItem,
    ExpenseDB,
    Message,
    Pagination,
)

from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.database import get_session

from backend import models

from typing import Annotated

DBSession = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter()


@router.post(
    '/expenses/', response_model=ExpenseDBItem, status_code=HTTPStatus.CREATED
)
async def create_expense(body: Expense, db_session: DBSession):

    query_result = await db_session.scalar(
        select(models.Expense).where((models.Expense.title == body.title))
    )

    if query_result:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Title already exists'
        )

    new_expense = models.Expense(
        title=body.title, description=body.description, value=body.value
    )
    db_session.add(new_expense)
    await db_session.commit()
    await db_session.refresh(new_expense)

    return new_expense


@router.get('/expenses/', response_model=ExpenseDB)
async def list_expenses(
    db_session: DBSession, paginator: Annotated[Pagination, Query()]
):
    query_result = await db_session.scalars(
        select(models.Expense).offset(paginator.offset).limit(paginator.limit)
    )
    expenses = query_result.all()
    return {'expenses': expenses}


@router.put('/expenses/{expense_id}', response_model=ExpenseDBItem)
async def update_expense(
    expense_id: int, body: Expense, db_session: DBSession
):
    expense = await db_session.scalar(
        select(models.Expense).where(models.Expense.id == expense_id)
    )
    if not expense:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
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
async def delete_expense(expense_id: int, db_session: DBSession):

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
