from pydantic import BaseModel, Field

class Expense(BaseModel):
    title: str 
    description: str = Field(min_length=1, max_length=120)
    value: int

class ExpenseDBItem(Expense):
    id: int = Field(ge=1)

class ExpenseDB(BaseModel):
    expenses: list[ExpenseDBItem]