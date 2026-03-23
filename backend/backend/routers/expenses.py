from fastapi import APIRouter, status
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
def list_expense():
    return {'expenses': expenses_fake_db}