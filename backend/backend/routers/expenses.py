from fastapi import APIRouter, HTTPException, status
from backend.schemas import Expense, ExpenseDBItem, ExpenseDB

router = APIRouter()

expenses_fake_db: list[ExpenseDBItem] = []

@router.post('/expenses/', response_model=ExpenseDBItem, status_code=status.HTTP_201_CREATED)
def create_expense(body: Expense):
    new_expense_id = len(expenses_fake_db) + 1
    new_expense = ExpenseDBItem(id=new_expense_id, **body.model_dump())
    expenses_fake_db.append(new_expense)
    return new_expense

@router.get('/expenses/', response_model=ExpenseDB)
def list_expenses():
    return {'expenses': expenses_fake_db}


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