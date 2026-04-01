from fastapi import APIRouter, HTTPException, status, Depends
from backend.schemas import Expense, ExpenseDBItem, ExpenseDB

from http import HTTPStatus

from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database import get_session

from backend import models

router = APIRouter()

expenses_fake_db: list[ExpenseDBItem] = []

@router.post('/expenses/', response_model=ExpenseDBItem, status_code=HTTPStatus.CREATED)
def create_expense(body: Expense, db_session: Session = Depends(get_session)):

    query_result = db_session.scalar(
        select(models.Expense).where(
            (models.Expense.title == body.title)
        )
    ) 

    if query_result:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Title already exists'
        )

    new_expense = models.Expense(title=body.title, description=body.description, value=body.value)
    db_session.add(new_expense)
    db_session.commit()
    db_session.refresh(new_expense)

    return new_expense

@router.get('/expenses/', response_model=ExpenseDB)
def list_expenses(
        db_session: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100
):
    expenses = db_session.scalars(select(models.Expense).offset(skip).limit(limit)).all()
    return {'expenses': expenses}


@router.put('/expenses/{expense_id}', response_model=ExpenseDBItem)
def update_expense(expense_id: int, body: Expense):
    for index, expense in enumerate(expenses_fake_db):
        if expense.id == expense_id:
            updated_expense = ExpenseDBItem(id=expense_id, **body.model_dump())
            expenses_fake_db[index] = updated_expense
            return updated_expense

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Expense not found',
    )

@router.delete('/expenses/{expense_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int):
    for index, expense in enumerate(expenses_fake_db):
        if expense.id == expense_id:
            del expenses_fake_db[index]
            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Expense not found',
    )